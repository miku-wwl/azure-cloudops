#!/usr/bin/env python3
"""Real loopback DNS protocol failure/recovery without changing host DNS."""
from __future__ import annotations

import argparse
import http.client
import json
import socket
import socketserver
import struct
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


FQDN = "billing.ir01.lab.test"
UNRELATED = "unrelated.ir01.lab.test"
HTTP_BODY = b"IR01_APPLICATION_OK\n"


def _question(name: str) -> bytes:
    labels = name.rstrip(".").split(".")
    return b"".join(bytes([len(label)]) + label.encode("ascii") for label in labels) + b"\0" + struct.pack("!HH", 1, 1)


def _parse_question(packet: bytes) -> tuple[str, bytes]:
    if len(packet) < 17 or struct.unpack("!H", packet[4:6])[0] != 1:
        raise ValueError("unsupported DNS request")
    offset = 12
    labels: list[str] = []
    while offset < len(packet):
        size = packet[offset]
        offset += 1
        if size == 0:
            break
        if size & 0xC0 or offset + size > len(packet):
            raise ValueError("compressed or invalid DNS question")
        labels.append(packet[offset:offset + size].decode("ascii"))
        offset += size
    if offset + 4 > len(packet):
        raise ValueError("incomplete DNS question")
    return ".".join(labels).casefold(), packet[12:offset + 4]


def _response(packet: bytes, faulted: bool, address: str) -> tuple[bytes, str, int]:
    name, question = _parse_question(packet)
    exists = name == FQDN and not faulted
    rcode = 0 if exists else 3
    ident = packet[:2]
    flags = 0x8180 | rcode
    header = struct.pack("!HHHHHH", int.from_bytes(ident, "big"), flags, 1, int(exists), 0, 0)
    answer = b""
    if exists:
        answer = b"\xc0\x0c" + struct.pack("!HHIH", 1, 1, 0, 4) + socket.inet_aton(address)
    return header + question + answer, name, rcode


def _query(resolver: tuple[str, int], name: str) -> dict[str, Any]:
    ident = 0xA701
    request = struct.pack("!HHHHHH", ident, 0x0100, 1, 0, 0, 0) + _question(name)
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client:
        client.settimeout(1.0)
        client.sendto(request, resolver)
        reply, _peer = client.recvfrom(512)
    rid, flags, qd, answers, _authority, _additional = struct.unpack("!HHHHHH", reply[:12])
    if rid != ident or qd != 1:
        raise ValueError("DNS response did not match the request")
    rcode = flags & 0xF
    parsed: dict[str, Any] = {"qname": name, "rcode": rcode, "answer_count": answers, "address": None}
    if answers:
        offset = 12 + len(_question(name))
        if reply[offset:offset + 2] != b"\xc0\x0c":
            raise ValueError("unexpected DNS answer name")
        _kind, _class, _ttl, length = struct.unpack("!HHIH", reply[offset + 2:offset + 12])
        parsed["address"] = socket.inet_ntoa(reply[offset + 12:offset + 12 + length])
    return parsed


class _DnsServer(socketserver.ThreadingUDPServer):
    allow_reuse_address = True
    daemon_threads = True

    def __init__(self, address: tuple[str, int]):
        super().__init__(address, _DnsHandler)
        self.faulted = False
        self.observations: list[dict[str, Any]] = []


class _DnsHandler(socketserver.BaseRequestHandler):
    def handle(self) -> None:
        packet, sock = self.request
        response, name, rcode = _response(packet, self.server.faulted, "127.0.0.1")  # type: ignore[attr-defined]
        self.server.observations.append({"qname": name, "rcode": rcode, "faulted": self.server.faulted})  # type: ignore[attr-defined]
        sock.sendto(response, self.client_address)


class _HealthHandler(socketserver.BaseRequestHandler):
    def handle(self) -> None:
        request = self.request.recv(2048)
        status = 200 if request.startswith(b"GET /health ") else 404
        body = HTTP_BODY if status == 200 else b"not found\n"
        response = f"HTTP/1.1 {status} {'OK' if status == 200 else 'Not Found'}\r\nContent-Length: {len(body)}\r\nConnection: close\r\n\r\n".encode("ascii") + body
        self.request.sendall(response)


def probe(resolver: tuple[str, int], app_port: int) -> dict[str, Any]:
    dns = _query(resolver, FQDN)
    result: dict[str, Any] = {"fqdn": FQDN, "dns": dns, "http": None}
    if dns["rcode"] != 0 or not dns["address"]:
        result["failure_category"] = "DNS_NXDOMAIN" if dns["rcode"] == 3 else "DNS_NO_ADDRESS"
        return result
    connection = http.client.HTTPConnection(dns["address"], app_port, timeout=1.0)
    try:
        connection.request("GET", "/health", headers={"Host": FQDN})
        response = connection.getresponse()
        body = response.read(256)
        result["http"] = {"status": response.status, "body": body.decode("ascii", "replace")}
        result["failure_category"] = None if response.status == 200 else "APPLICATION_FAILURE"
    finally:
        connection.close()
    return result


def run(evidence_path: Path) -> dict[str, Any]:
    dns = _DnsServer(("127.0.0.1", 0))
    http = socketserver.ThreadingTCPServer(("127.0.0.1", 0), _HealthHandler)
    dns_thread = threading.Thread(target=dns.serve_forever, daemon=True)
    http_thread = threading.Thread(target=http.serve_forever, daemon=True)
    dns_thread.start()
    http_thread.start()
    resolver = ("127.0.0.1", dns.server_address[1])
    evidence: dict[str, Any] = {
        "incident_id": "IR-01",
        "status": "LOCAL_VERIFIED",
        "started_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "scope": {"dns_bind": "127.0.0.1", "resolver_port": resolver[1], "fqdn": FQDN, "app_bind": "127.0.0.1", "app_port": http.server_address[1]},
        "mechanism": "DNS wire-format A query to an explicit run-owned loopback UDP resolver; no machine resolver configuration is changed.",
    }
    try:
        baseline = probe(resolver, http.server_address[1])
        dns.faulted = True
        failure = probe(resolver, http.server_address[1])
        fault_evidence = list(dns.observations)
        dns.faulted = False
        recovery = probe(resolver, http.server_address[1])
        unrelated = _query(resolver, UNRELATED)
        evidence.update({"baseline": baseline, "fault": failure, "root_cause_observations": fault_evidence, "recovery": recovery, "negative_control": unrelated})
        checks = {
            "baseline_same_probe_passed": baseline["dns"]["address"] == "127.0.0.1" and baseline["http"]["status"] == 200 and baseline["http"]["body"] == HTTP_BODY.decode(),
            "fault_was_real_nxdomain": failure["dns"]["rcode"] == 3 and failure["http"] is None and failure["failure_category"] == "DNS_NXDOMAIN",
            "resolver_captured_fault": any(item["qname"] == FQDN and item["rcode"] == 3 and item["faulted"] for item in fault_evidence),
            "same_probe_recovered": recovery["dns"]["address"] == "127.0.0.1" and recovery["http"]["status"] == 200 and recovery["http"]["body"] == HTTP_BODY.decode(),
            "unrelated_name_did_not_fall_back": unrelated["rcode"] == 3 and unrelated["answer_count"] == 0,
        }
        evidence["checks"] = checks
        evidence["ok"] = all(checks.values())
        if not evidence["ok"]:
            evidence["status"] = "FAILED"
        return evidence
    finally:
        dns.shutdown()
        http.shutdown()
        dns.server_close()
        http.server_close()
        dns_thread.join(timeout=2)
        http_thread.join(timeout=2)
        evidence["cleanup"] = {"dns_listener_closed": True, "http_listener_closed": True, "background_threads_stopped": not dns_thread.is_alive() and not http_thread.is_alive()}
        evidence["completed_at_utc"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
        evidence_path.parent.mkdir(parents=True, exist_ok=True)
        evidence_path.write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence", type=Path, default=Path(__file__).resolve().parents[1] / "evidence" / "IR-01_local-dns.json")
    args = parser.parse_args()
    result = run(args.evidence)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("ok") else 2


if __name__ == "__main__":
    raise SystemExit(main())
