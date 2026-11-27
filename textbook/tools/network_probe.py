#!/usr/bin/env python3
"""Direct, read-only DNS/TCP/TLS and HTTP HEAD probes with bounded timeouts."""
from __future__ import annotations

import argparse
import errno
import hashlib
import http.client
import json
import queue
import selectors
import socket
import ssl
import sys
import threading
import time
import urllib.parse
from datetime import datetime, timezone
from typing import Any, Sequence


EXIT_OK = 0
EXIT_UNHEALTHY = 2
EXIT_USAGE = 3


class ProbeError(ValueError):
    pass


def _fingerprint(value: str) -> str:
    return "sha256:" + hashlib.sha256(value.encode("utf-8")).hexdigest()[:20]


def resolve(host: str, port: int, timeout: float) -> list[tuple[int, tuple[Any, ...]]]:
    """Bound the caller's wait for the OS resolver, which Python cannot cancel."""
    result: queue.Queue[tuple[bool, Any]] = queue.Queue(maxsize=1)

    def lookup() -> None:
        try:
            result.put((True, socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)))
        except OSError as exc:
            result.put((False, exc))

    threading.Thread(target=lookup, name="azure-cloudops-dns", daemon=True).start()
    try:
        succeeded, value = result.get(timeout=timeout)
    except queue.Empty as exc:
        # A timed-out resolver call can finish in the background, but cannot hold up this CLI.
        raise ProbeError("DNS_TIMEOUT") from exc
    if not succeeded:
        raise ProbeError("DNS_FAILURE") from value
    items = value
    unique: dict[tuple[int, tuple[Any, ...]], None] = {}
    for family, socktype, proto, _canonname, sockaddr in items:
        unique[(family, sockaddr)] = None
    return list(unique)


def _connect_any(addresses: list[tuple[int, tuple[Any, ...]]], deadline: float) -> tuple[socket.socket | None, list[str]]:
    """Race resolved addresses within one deadline, then close losing sockets."""
    pending_codes = {
        errno.EINPROGRESS, errno.EWOULDBLOCK, errno.EALREADY, errno.EINTR,
        getattr(errno, "WSAEWOULDBLOCK", 10035),
        getattr(errno, "WSAEINPROGRESS", 10036),
        getattr(errno, "WSAEALREADY", 10037),
    }
    errors: list[str] = []
    sockets: list[socket.socket] = []
    winner: socket.socket | None = None
    selector = selectors.DefaultSelector()
    try:
        for family, sockaddr in addresses[:16]:
            candidate = socket.socket(family, socket.SOCK_STREAM)
            candidate.setblocking(False)
            sockets.append(candidate)
            try:
                code = candidate.connect_ex(sockaddr)
            except OSError as exc:
                errors.append(type(exc).__name__)
                candidate.close()
                continue
            if code == 0:
                winner = candidate
                candidate.setblocking(True)
                return candidate, errors
            if code in pending_codes:
                selector.register(candidate, selectors.EVENT_WRITE)
            else:
                errors.append("OSError")
                candidate.close()
        while selector.get_map():
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                errors.append("TimeoutError")
                break
            ready = selector.select(remaining)
            if not ready:
                errors.append("TimeoutError")
                break
            for key, _mask in ready:
                candidate = key.fileobj
                selector.unregister(candidate)
                if candidate.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR) == 0:
                    winner = candidate
                    candidate.setblocking(True)
                    return candidate, errors
                errors.append("OSError")
                candidate.close()
        return None, errors
    finally:
        selector.close()
        for candidate in sockets:
            if candidate is not winner:
                candidate.close()


def probe_tcp_tls(host: str, port: int, timeout: float, tls: bool, server_name: str | None = None, show_addresses: bool = False) -> dict[str, Any]:
    started = time.monotonic()
    deadline = started + timeout
    addresses = resolve(host, port, timeout)
    output: dict[str, Any] = {
        "probe": "tcp-tls",
        "host": host,
        "port": port,
        "resolved_address_count": len(addresses),
        "addresses": [sockaddr[0] if show_addresses else _fingerprint(str(sockaddr[0])) for _family, sockaddr in addresses],
        "address_redaction": "disabled-by-explicit-option" if show_addresses else "sha256-prefix",
        "tcp_connected": False,
        "tls_requested": tls,
        "tls_verified": None,
    }
    if not addresses:
        raise ProbeError("DNS_FAILURE")
    raw, errors = _connect_any(addresses, deadline)
    if raw is not None:
        try:
            output["tcp_connected"] = True
            if tls:
                context = ssl.create_default_context()
                name = server_name or host
                raw.settimeout(max(0.001, deadline - time.monotonic()))
                with context.wrap_socket(raw, server_hostname=name) as secured:
                    raw = None
                    certificate = secured.getpeercert(binary_form=True)
                    details = secured.getpeercert()
                    not_after = details.get("notAfter")
                    output.update({
                        "tls_verified": True,
                        "tls_version": secured.version(),
                        "cipher": secured.cipher()[0] if secured.cipher() else None,
                        "certificate_sha256": hashlib.sha256(certificate).hexdigest(),
                        "certificate_not_after_utc": _certificate_time(not_after) if not_after else None,
                    })
            output["elapsed_ms"] = round((time.monotonic() - started) * 1000, 2)
            return output
        except (OSError, ssl.SSLError, TimeoutError) as exc:
            errors.append(type(exc).__name__)
        finally:
            if raw is not None:
                raw.close()
    output["error"] = "TLS_VERIFICATION_FAILED" if tls and output["tcp_connected"] else "TCP_CONNECT_FAILED"
    output["failure_types"] = sorted(set(errors))
    return output


def _certificate_time(value: str) -> str:
    parsed = datetime.strptime(value, "%b %d %H:%M:%S %Y %Z").replace(tzinfo=timezone.utc)
    return parsed.isoformat(timespec="seconds")


def probe_http_head(url: str, timeout: float) -> dict[str, Any]:
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname or parsed.username or parsed.password:
        raise ProbeError("URL_MUST_BE_HTTP_OR_HTTPS_WITHOUT_CREDENTIALS")
    if parsed.query or parsed.fragment:
        raise ProbeError("URL_QUERY_AND_FRAGMENT_ARE_NOT_ALLOWED")
    try:
        port = parsed.port or (443 if parsed.scheme == "https" else 80)
    except ValueError as exc:
        raise ProbeError("URL_PORT_INVALID") from exc
    if not 1 <= port <= 65535:
        raise ProbeError("URL_PORT_INVALID")
    host = parsed.hostname
    display_url = urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, parsed.path or "/", "", ""))
    target = urllib.parse.urlunsplit(("", "", parsed.path or "/", "", ""))
    started = time.monotonic()
    deadline = started + timeout
    try:
        addresses = resolve(host, port, timeout)
    except ProbeError as exc:
        return {"probe": "http-head", "url": display_url, "healthy": False, "error": str(exc), "redirects_followed": False, "body_read": False}
    raw, errors = _connect_any(addresses, deadline)
    connection: http.client.HTTPConnection | None = None
    try:
        if raw is None:
            raise TimeoutError("No address accepted a connection before the deadline.")
        remaining = max(0.001, deadline - time.monotonic())
        raw.settimeout(remaining)
        if parsed.scheme == "https":
            context = ssl.create_default_context()
            raw = context.wrap_socket(raw, server_hostname=host)
            raw.settimeout(max(0.001, deadline - time.monotonic()))
        connection = http.client.HTTPConnection(host, port, timeout=max(0.001, deadline - time.monotonic()))
        connection.sock = raw
        raw = None
        connection.request("HEAD", target, headers={"User-Agent": "azure-cloudops-read-only-probe/1.0"})
        response = connection.getresponse()
        status = response.status
        response.close()
        return {
            "probe": "http-head",
            "url": display_url,
            "method": "HEAD",
            "status_code": status,
            "healthy": 200 <= status < 300,
            "redirects_followed": False,
            "body_read": False,
            "tls_verified": parsed.scheme == "https",
            "elapsed_ms": round((time.monotonic() - started) * 1000, 2),
        }
    except (OSError, ssl.SSLError, TimeoutError, http.client.HTTPException) as exc:
        errors.append(type(exc).__name__)
    finally:
        if connection is not None:
            connection.close()
        if raw is not None:
            raw.close()
    return {
        "probe": "http-head", "url": display_url, "healthy": False,
        "error": "HTTP_REQUEST_FAILED", "failure_types": sorted(set(errors)),
        "redirects_followed": False, "body_read": False,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Read-only network probes; no credentials, writes, or response bodies.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    tcp = subparsers.add_parser("tcp-tls", help="Resolve DNS, connect TCP, and optionally verify a TLS handshake.")
    tcp.add_argument("--host", required=True)
    tcp.add_argument("--port", required=True, type=int)
    tcp.add_argument("--tls", action="store_true", help="Perform a certificate-verified TLS handshake.")
    tcp.add_argument("--server-name", help="Optional TLS SNI/verification hostname.")
    tcp.add_argument("--show-addresses", action="store_true", help="Reveal resolved IP addresses instead of hashes.")
    tcp.add_argument("--timeout", type=float, default=5.0)
    http = subparsers.add_parser("http-head", help="Issue one unauthenticated HTTP HEAD request; never follow redirects or read a body.")
    http.add_argument("--url", required=True)
    http.add_argument("--timeout", type=float, default=10.0)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not 1 <= args.timeout <= 30:
        print(json.dumps({"ok": False, "error": "INVALID_TIMEOUT", "message": "timeout must be between 1 and 30 seconds"}))
        return EXIT_USAGE
    try:
        if args.command == "tcp-tls":
            if not 1 <= args.port <= 65535:
                raise ProbeError("PORT_OUT_OF_RANGE")
            result = probe_tcp_tls(args.host, args.port, args.timeout, args.tls, args.server_name, args.show_addresses)
            ok = bool(result.get("tcp_connected")) and (not args.tls or result.get("tls_verified") is True)
        else:
            result = probe_http_head(args.url, args.timeout)
            ok = bool(result.get("healthy"))
    except ProbeError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        return EXIT_USAGE if "URL_" in str(exc) or str(exc) == "PORT_OUT_OF_RANGE" else EXIT_UNHEALTHY
    result["ok"] = ok
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    return EXIT_OK if ok else EXIT_UNHEALTHY


if __name__ == "__main__":
    raise SystemExit(main())
