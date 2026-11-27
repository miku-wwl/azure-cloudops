#!/usr/bin/env python3
"""Run all eight mandatory E8 incidents serially in fresh, owned scopes."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


NODE_IMAGE = "kindest/node@sha256:099e049362a1526b2db71494e1947aae99bd16290d7c895f2b7ea312e3cbfaed"
MANDATORY = ("IR-01", "IR-02", "IR-05", "IR-07", "IR-08", "IR-10", "IR-11", "IR-12")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def invoke(command: list[str], cwd: Path, timeout: int, env: dict[str, str] | None = None) -> dict[str, Any]:
    try:
        result = subprocess.run(command, cwd=cwd, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                timeout=timeout, check=False, encoding="utf-8", errors="replace")
        return {"command": command, "returncode": result.returncode, "output": result.stdout}
    except subprocess.TimeoutExpired as exc:
        return {"command": command, "returncode": 124, "output": (exc.stdout or "").decode("utf-8", "replace") if isinstance(exc.stdout, bytes) else (exc.stdout or ""), "timeout_seconds": timeout}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--label", required=True, help="evidence directory name, e.g. cycle-2")
    parser.add_argument("--evidence-root", type=Path, default=Path(__file__).resolve().parents[1] / "evidence")
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[3]
    incident_root = Path(__file__).resolve().parents[1]
    evidence_dir = args.evidence_root.resolve() / args.label
    if evidence_dir.exists():
        parser.error(f"evidence directory already exists: {evidence_dir}")
    evidence_dir.mkdir(parents=True)
    work = repo / "work"
    work.mkdir(exist_ok=True)
    summary: dict[str, Any] = {"label": args.label, "status": "FAILED", "started_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                               "scope": "fresh process per scenario; unique Docker namespaces, kind cluster, Terraform temporary checkout, loopback ports and data paths",
                               "cloud_calls": "NONE", "incidents": {}}
    # Hash pre-existing Terraform source/state artifacts to prove this replay only used a fresh temp copy.
    terraform_lab = repo / "textbook" / "chapters" / "AZ07-02" / "labs" / "terraform-state"
    guarded = [terraform_lab / "main.tf", terraform_lab / "terraform.tfstate", terraform_lab / "terraform.tfstate.backup"]
    before_hashes = {str(path.relative_to(repo)): sha(path) for path in guarded if path.is_file()}
    started = time.monotonic()
    try:
        with tempfile.TemporaryDirectory(prefix=f"{args.label}-", dir=work) as binary_dir:
            binary_root = Path(binary_dir)
            go_env = os.environ.copy()
            go_env.update({"GOOS": "linux", "GOARCH": "amd64", "CGO_ENABLED": "0"})
            health_binary = binary_root / "health_server_linux_amd64"
            registry_binary = binary_root / "registry_404_linux_amd64"
            builds = {
                "health_server": invoke(["go", "build", "-o", str(health_binary), str(incident_root / "local" / "health_server.go")], repo, 60, go_env),
                "registry_fixture": invoke(["go", "build", "-o", str(registry_binary), str(incident_root / "local" / "registry_404.go")], repo, 60, go_env),
            }
            summary["builds"] = builds
            if any(value["returncode"] != 0 for value in builds.values()):
                raise RuntimeError("a local Linux fixture binary did not build")
            commands: dict[str, list[str]] = {
                "IR-01": [sys.executable, str(incident_root / "local" / "ir01_dns.py"), "--evidence", str(evidence_dir / "IR-01.json")],
                "IR-02": [sys.executable, str(incident_root / "local" / "ir02_filter.py"), "--image", NODE_IMAGE, "--binary", str(health_binary), "--evidence", str(evidence_dir / "IR-02.json")],
                "IR-05": [sys.executable, str(incident_root / "local" / "ir05_permissions.py"), "--image", NODE_IMAGE, "--evidence", str(evidence_dir / "IR-05.json")],
                "IR-07": [sys.executable, str(incident_root / "local" / "ir07_kind.py"), "--node-image", NODE_IMAGE, "--health-binary", str(health_binary), "--registry-binary", str(registry_binary), "--repo", str(repo), "--evidence", str(evidence_dir / "IR-07.json")],
                "IR-10": [sys.executable, str(incident_root / "local" / "ir10_monitoring.py"), "--evidence", str(evidence_dir / "IR-10.json")],
                "IR-11": [sys.executable, str(incident_root / "local" / "ir11_rollback.py"), "--evidence", str(evidence_dir / "IR-11.json")],
                "IR-12": [sys.executable, str(incident_root / "local" / "ir12_restore.py"), "--evidence", str(evidence_dir / "IR-12.json")],
            }
            for incident_id in ("IR-01", "IR-02", "IR-05", "IR-07", "IR-10", "IR-11", "IR-12"):
                result = invoke(commands[incident_id], repo, 300)
                summary["incidents"][incident_id] = {"exit_code": result["returncode"], "command": result["command"]}
                if result["returncode"] != 0:
                    raise RuntimeError(f"{incident_id} returned {result['returncode']}: {result['output'][-2400:]}")
                artifact = json.loads((evidence_dir / f"{incident_id}.json").read_text(encoding="utf-8"))
                summary["incidents"][incident_id]["status"] = artifact.get("status")
                summary["incidents"][incident_id]["checks_passed"] = bool(artifact.get("ok"))
                cleanup = artifact.get("cleanup", {})
                if incident_id in {"IR-02", "IR-05"} and not cleanup.get("container_absent"):
                    raise RuntimeError(f"{incident_id} left its run-owned container behind")
                if incident_id == "IR-07" and not (cleanup.get("cluster_absent") and cleanup.get("app_image_absent") and cleanup.get("shared_cluster_still_present") and cleanup.get("temporary_kubeconfig_and_build_context_removed")):
                    raise RuntimeError("IR-07 did not meet all resource-cleanup checks")
                if incident_id in {"IR-10", "IR-11"} and not cleanup.get("worker_stopped"):
                    raise RuntimeError(f"{incident_id} left a local server worker running")
                if artifact.get("status") != "LOCAL_VERIFIED" or not artifact.get("ok"):
                    raise RuntimeError(f"{incident_id} evidence did not pass its scenario checks")

            terraform_output = invoke([sys.executable, str(terraform_lab / "scripts" / "verify_lab.py")], repo, 600)
            terraform_log = evidence_dir / "IR-08_local-terraform.txt"
            terraform_log.write_text(terraform_output["output"], encoding="utf-8")
            terraform_pass = (terraform_output["returncode"] == 0 and "actual_local_lock_contention=PASS" in terraform_output["output"]
                              and "provider_read_drift_and_reconcile=PASS" in terraform_output["output"]
                              and "azure_calls=NONE" in terraform_output["output"]
                              and "ISOLATED_TEMPORARY_LAB_CLEANED" in terraform_output["output"])
            summary["incidents"]["IR-08"] = {"exit_code": terraform_output["returncode"], "status": "LOCAL_VERIFIED" if terraform_pass else "FAILED",
                                              "checks_passed": terraform_pass, "evidence": str(terraform_log.relative_to(args.evidence_root.resolve()))}
            if not terraform_pass:
                raise RuntimeError(f"IR-08 Terraform verification failed: {terraform_output['output'][-3000:]}")

        after_hashes = {str(path.relative_to(repo)): sha(path) for path in guarded if path.is_file()}
        summary["terraform_checkout_unchanged"] = before_hashes == after_hashes
        if not summary["terraform_checkout_unchanged"]:
            raise RuntimeError("the repository Terraform lab or State changed during the isolated replay")
        summary["all_mandatory_passed"] = set(summary["incidents"]) == set(MANDATORY) and all(item.get("status") == "LOCAL_VERIFIED" and item.get("checks_passed") for item in summary["incidents"].values())
        summary["status"] = "LOCAL_VERIFIED" if summary["all_mandatory_passed"] else "FAILED"
    except Exception as exc:
        summary["error"] = str(exc)
        summary["status"] = "FAILED"
    summary["elapsed_seconds"] = round(time.monotonic() - started, 3)
    summary["completed_at_utc"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    (evidence_dir / "cycle-summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{args.label}: {summary['status']} ({len(summary['incidents'])}/8 incidents recorded; {summary['elapsed_seconds']} s)")
    if summary.get("error"):
        print(summary["error"])
    return 0 if summary["status"] == "LOCAL_VERIFIED" else 2


if __name__ == "__main__":
    raise SystemExit(main())
