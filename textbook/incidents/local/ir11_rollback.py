#!/usr/bin/env python3
"""Observe an actual local HTTP regression and roll back by an atomic release pointer."""
from __future__ import annotations

import argparse
import hashlib
import http.client
import json
import os
import tempfile
import threading
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any


class ReleaseServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True

    def __init__(self, address: tuple[str, int], root: Path, pointer: Path):
        super().__init__(address, ReleaseHandler)
        self.root = root
        self.pointer = pointer
        self.observations: list[dict[str, Any]] = []


class ReleaseHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        release_id = self.server.pointer.read_text(encoding="ascii").strip()  # type: ignore[attr-defined]
        release_path = self.server.root / release_id / "release.json"  # type: ignore[attr-defined]
        document = json.loads(release_path.read_text(encoding="utf-8"))
        body = (json.dumps(document["response"], sort_keys=True, separators=(",", ":")) + "\n").encode()
        observation = {"at_utc": datetime.now(timezone.utc).isoformat(timespec="milliseconds"), "method": self.command,
                       "path": self.path, "release": release_id, "status": document["status"], "body_sha256": hashlib.sha256(body).hexdigest()}
        self.server.observations.append(observation)  # type: ignore[attr-defined]
        self.send_response(document["status"])
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("X-Release", release_id)
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, _format: str, *_args: Any) -> None:
        return


def atomic_point(pointer: Path, release_id: str) -> None:
    candidate = pointer.with_suffix(".next")
    candidate.write_text(release_id + "\n", encoding="ascii")
    os.replace(candidate, pointer)


def probe(port: int) -> dict[str, Any]:
    connection = http.client.HTTPConnection("127.0.0.1", port, timeout=2)
    try:
        connection.request("GET", "/api/orders/42")
        response = connection.getresponse()
        body = response.read(2048).decode("utf-8", "replace")
        return {"status": response.status, "body": body, "release": response.getheader("X-Release"), "method": "GET", "path": "/api/orders/42"}
    finally:
        connection.close()


def run(evidence_path: Path) -> dict[str, Any]:
    evidence: dict[str, Any] = {"incident_id": "IR-11", "status": "FAILED",
                                "started_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                                "mechanism": "One loopback HTTP service reads an atomic active-release pointer for every request; v1/v2 artifacts are immutable synthetic JSON fixtures.",
                                "scope": {"stable_url_path": "/api/orders/42", "bind": "127.0.0.1", "cloud_deployment": False}}
    with tempfile.TemporaryDirectory(prefix="azure-cloudops-ir11-") as temporary:
        root = Path(temporary)
        releases = root / "releases"
        releases.mkdir()
        documents = {
            "v1": {"release_id": "v1", "status": 200, "response": {"order_id": "synthetic-42", "state": "ready"}},
            "v2": {"release_id": "v2", "status": 500, "response": {"order_id": "synthetic-42", "state": "regressed"}},
        }
        digests: dict[str, str] = {}
        for release_id, document in documents.items():
            directory = releases / release_id
            directory.mkdir()
            artifact = directory / "release.json"
            artifact.write_text(json.dumps(document, sort_keys=True, indent=2) + "\n", encoding="utf-8")
            digests[release_id] = hashlib.sha256(artifact.read_bytes()).hexdigest()
        pointer = root / "active-release.txt"
        pointer.write_text("v1\n", encoding="ascii")
        server = ReleaseServer(("127.0.0.1", 0), releases, pointer)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        evidence["scope"]["port"] = server.server_address[1]
        try:
            baseline = probe(server.server_address[1])
            baseline_pointer = pointer.read_text(encoding="ascii").strip()
            atomic_point(pointer, "v2")
            fault = probe(server.server_address[1])
            fault_pointer = pointer.read_text(encoding="ascii").strip()
            atomic_point(pointer, "v1")
            recovery = probe(server.server_address[1])
            recovered_pointer = pointer.read_text(encoding="ascii").strip()
            observations = list(server.observations)
            checks = {
                "baseline_contract_passed": baseline["status"] == 200 and json.loads(baseline["body"])["state"] == "ready" and baseline["release"] == "v1",
                "fault_is_actual_functional_http_regression": fault["status"] == 500 and json.loads(fault["body"])["state"] == "regressed" and fault["release"] == "v2",
                "active_bad_artifact_matches_immutable_digest": fault_pointer == "v2" and hashlib.sha256((releases / "v2" / "release.json").read_bytes()).hexdigest() == digests["v2"],
                "same_url_recovers_on_prior_release": recovery["status"] == 200 and json.loads(recovery["body"])["state"] == "ready" and recovery["release"] == "v1",
                "prior_artifact_digest_unchanged": hashlib.sha256((releases / "v1" / "release.json").read_bytes()).hexdigest() == digests["v1"],
                "only_atomic_pointer_changed": baseline_pointer == "v1" and recovered_pointer == "v1" and len(observations) == 3 and all(row["path"] == "/api/orders/42" for row in observations),
            }
            evidence.update({"release_sha256": digests, "baseline_probe": baseline, "fault_probe": fault, "recovery_probe": recovery,
                             "observations": observations, "active_pointer_after_each_phase": [baseline_pointer, fault_pointer, recovered_pointer],
                             "checks": checks, "ok": all(checks.values()), "status": "LOCAL_VERIFIED" if all(checks.values()) else "FAILED"})
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=3)
            evidence["cleanup"] = {"listener_closed": True, "worker_stopped": not thread.is_alive(), "release_artifacts_deleted_after_capture": True}
    evidence["completed_at_utc"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    evidence_path.parent.mkdir(parents=True, exist_ok=True)
    evidence_path.write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return evidence


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence", type=Path, default=Path(__file__).resolve().parents[1] / "evidence" / "IR-11_local-rollback.json")
    args = parser.parse_args()
    result = run(args.evidence)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("ok") and result.get("cleanup", {}).get("worker_stopped") else 2


if __name__ == "__main__":
    raise SystemExit(main())
