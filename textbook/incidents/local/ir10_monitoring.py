#!/usr/bin/env python3
"""Measure real loopback HTTP responses and evaluate an alert from those records."""
from __future__ import annotations

import argparse
import http.client
import json
import tempfile
import threading
import uuid
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any


class HealthServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True

    def __init__(self, address: tuple[str, int], telemetry: Path):
        super().__init__(address, ProbeHandler)
        self.health_status = 200
        self.telemetry_path = telemetry
        self.telemetry: list[dict[str, Any]] = []
        self.telemetry_lock = threading.Lock()


class ProbeHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        status = self.server.health_status  # type: ignore[attr-defined]
        event = {"event_id": uuid.uuid4().hex, "observed_at_utc": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
                 "method": self.command, "path": self.path, "http_status": status}
        body = b"healthy\n" if status == 200 else b"synthetic dependency failure\n"
        with self.server.telemetry_lock:  # type: ignore[attr-defined]
            self.server.telemetry.append(event)  # type: ignore[attr-defined]
            with self.server.telemetry_path.open("a", encoding="utf-8") as stream:  # type: ignore[attr-defined]
                stream.write(json.dumps(event, separators=(",", ":")) + "\n")
        self.send_response(status)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("X-Observation-ID", event["event_id"])
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, _format: str, *_args: Any) -> None:
        return


def real_probe(port: int) -> dict[str, Any]:
    connection = http.client.HTTPConnection("127.0.0.1", port, timeout=2)
    try:
        connection.request("GET", "/health")
        response = connection.getresponse()
        body = response.read(256).decode("utf-8", "replace")
        return {"status": response.status, "body": body, "observation_id": response.getheader("X-Observation-ID"),
                "method": "GET", "path": "/health"}
    finally:
        connection.close()


def evaluate(rows: list[dict[str, Any]], threshold: int) -> dict[str, Any]:
    failures = [row for row in rows if row["http_status"] >= 500]
    return {"threshold": threshold, "failure_count": len(failures), "fired": len(failures) >= threshold,
            "source_event_ids": [row["event_id"] for row in rows]}


def run(evidence_path: Path) -> dict[str, Any]:
    evidence: dict[str, Any] = {"incident_id": "IR-10", "status": "FAILED",
                                "started_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                                "mechanism": "All alert inputs are measured HTTP response rows written by a local server during actual GET /health requests; the rule evaluator only references captured event IDs.",
                                "azure_monitor_used": False}
    with tempfile.TemporaryDirectory(prefix="azure-cloudops-ir10-") as temporary:
        telemetry_path = Path(temporary) / "telemetry.jsonl"
        server = HealthServer(("127.0.0.1", 0), telemetry_path)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        evidence["scope"] = {"bind": "127.0.0.1", "port": server.server_address[1], "telemetry_store": "run-owned temporary JSONL"}
        try:
            healthy = [real_probe(server.server_address[1]) for _ in range(2)]
            rows = list(server.telemetry)
            initial_eval = evaluate(rows[-2:], threshold=2)
            alert_state = "Fired" if initial_eval["fired"] else "Resolved"
            server.health_status = 503
            failing = [real_probe(server.server_address[1]) for _ in range(2)]
            rows_after_fault = list(server.telemetry)
            fault_ids = [probe["observation_id"] for probe in failing]
            fault_rows = [row for row in rows_after_fault if row["event_id"] in fault_ids]
            bad_rule = evaluate(fault_rows, threshold=99)
            transitions: list[dict[str, Any]] = []
            if bad_rule["fired"] != (alert_state == "Fired"):
                prior = alert_state
                alert_state = "Fired" if bad_rule["fired"] else "Resolved"
                transitions.append({"from": prior, "to": alert_state, "source_event_ids": bad_rule["source_event_ids"], "reason": "misconfigured threshold"})
            repaired_rule = evaluate(fault_rows, threshold=2)
            if repaired_rule["fired"] != (alert_state == "Fired"):
                prior = alert_state
                alert_state = "Fired" if repaired_rule["fired"] else "Resolved"
                transitions.append({"from": prior, "to": alert_state, "source_event_ids": repaired_rule["source_event_ids"], "reason": "threshold corrected to 2 failures"})
            server.health_status = 200
            healthy_after = [real_probe(server.server_address[1]) for _ in range(2)]
            rows_after_recovery = list(server.telemetry)
            recovery_ids = [probe["observation_id"] for probe in healthy_after]
            recovery_rows = [row for row in rows_after_recovery if row["event_id"] in recovery_ids]
            recovered_rule = evaluate(recovery_rows, threshold=2)
            if recovered_rule["fired"] != (alert_state == "Fired"):
                prior = alert_state
                alert_state = "Fired" if recovered_rule["fired"] else "Resolved"
                transitions.append({"from": prior, "to": alert_state, "source_event_ids": recovered_rule["source_event_ids"], "reason": "successful recovery probes"})
            file_rows = [json.loads(line) for line in telemetry_path.read_text(encoding="utf-8").splitlines()]
            evidence.update({"baseline_probes": healthy, "initial_evaluation": initial_eval, "failure_probes": failing,
                             "misconfigured_rule_evaluation": bad_rule, "repaired_rule_evaluation_same_ids": repaired_rule,
                             "recovery_probes": healthy_after, "recovery_rule_evaluation": recovered_rule,
                             "alert_transitions": transitions, "telemetry": file_rows, "final_alert_state": alert_state})
            checks = {
                "baseline_real_http_probes_healthy": all(p["status"] == 200 and p["observation_id"] for p in healthy),
                "failure_measurements_are_real_503_responses": all(p["status"] == 503 and p["observation_id"] for p in failing),
                "telemetry_rows_match_real_requests": len(file_rows) == 6 and all(row["path"] == "/health" for row in file_rows),
                "broken_threshold_misses_same_failures": not bad_rule["fired"] and bad_rule["failure_count"] == 2 and bad_rule["source_event_ids"] == repaired_rule["source_event_ids"],
                "corrected_threshold_fires_from_same_measurements": repaired_rule["fired"] and repaired_rule["failure_count"] == 2,
                "recovery_same_probe_resolves_alert": all(p["status"] == 200 for p in healthy_after) and not recovered_rule["fired"] and alert_state == "Resolved",
                "state_transitions_reference_measured_event_ids": all(transition["source_event_ids"] for transition in transitions),
            }
            evidence["checks"] = checks
            evidence["ok"] = all(checks.values())
            evidence["status"] = "LOCAL_VERIFIED" if evidence["ok"] else "FAILED"
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=3)
            evidence["cleanup"] = {"listener_closed": True, "worker_stopped": not thread.is_alive(),
                                    "temporary_telemetry_deleted_after_capture": True}
    evidence["completed_at_utc"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    evidence_path.parent.mkdir(parents=True, exist_ok=True)
    evidence_path.write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return evidence


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence", type=Path, default=Path(__file__).resolve().parents[1] / "evidence" / "IR-10_local-alert.json")
    args = parser.parse_args()
    result = run(args.evidence)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("ok") and result.get("cleanup", {}).get("worker_stopped") else 2


if __name__ == "__main__":
    raise SystemExit(main())
