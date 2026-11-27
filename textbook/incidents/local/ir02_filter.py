#!/usr/bin/env python3
"""Exercise an exact firewall tuple in a disposable Docker network namespace."""
from __future__ import annotations

import argparse
import json
import subprocess
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def invoke(args: list[str], timeout: int = 15, input_text: str | None = None) -> dict[str, Any]:
    result = subprocess.run(args, text=True, encoding="utf-8", errors="replace", input=input_text,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=timeout, check=False)
    return {"command": args, "returncode": result.returncode, "output": result.stdout.strip()}


def require(evidence: dict[str, Any], key: str, args: list[str], timeout: int = 15) -> dict[str, Any]:
    result = invoke(args, timeout)
    evidence.setdefault("commands", {})[key] = result
    if result["returncode"] != 0:
        raise RuntimeError(f"{key} failed ({result['returncode']}): {result['output']}")
    return result


def probe(evidence: dict[str, Any], key: str, container: str, port: int) -> dict[str, Any]:
    result = invoke(["docker", "exec", container, "curl", "--silent", "--show-error", "--max-time", "2",
                     "--output", "/dev/null", "--write-out", "%{http_code}", f"http://127.0.0.1:{port}/health"])
    evidence.setdefault("probes", {})[key] = result
    return result


def run(image: str, binary: Path, evidence_path: Path) -> dict[str, Any]:
    container = f"azure-cloudops-ir02-{uuid.uuid4().hex[:10]}"
    evidence: dict[str, Any] = {
        "incident_id": "IR-02",
        "status": "FAILED",
        "started_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "scope": {"container": container, "network": "none", "firewall": "container network namespace INPUT chain only",
                  "tuple": {"interface": "lo", "source": "127.0.0.1", "destination": "127.0.0.1", "protocol": "tcp", "fault_port": 18080, "negative_control_port": 18081}},
        "mechanism": "A run-owned Docker container with --network none, a namespace-local veth pair, and one exact iptables REJECT rule. No host firewall command or external destination is used.",
    }
    created = False
    try:
        result = require(evidence, "create_isolated_namespace", [
            "docker", "run", "--detach", "--name", container, "--network", "none", "--entrypoint", "/bin/bash",
            "--cap-drop", "ALL", "--cap-add", "NET_ADMIN", "--security-opt", "no-new-privileges", image, "-lc", "sleep 600",
        ])
        created = True
        evidence["container_id"] = result["output"]
        require(evidence, "copy_health_server", ["docker", "cp", str(binary), f"{container}:/tmp/health_server"])
        require(evidence, "create_veth_pair", ["docker", "exec", container, "ip", "link", "add", "e8v0", "type", "veth", "peer", "name", "e8v1"])
        require(evidence, "enable_veth_pair", ["docker", "exec", container, "ip", "link", "set", "e8v0", "up"])
        require(evidence, "enable_veth_peer", ["docker", "exec", container, "ip", "link", "set", "e8v1", "up"])
        require(evidence, "inspect_links", ["docker", "exec", container, "ip", "-brief", "link"])
        require(evidence, "inspect_routes", ["docker", "exec", container, "ip", "route"])
        require(evidence, "start_listener_18080", ["docker", "exec", "--detach", container, "/tmp/health_server",
                                                     "--listen", "0.0.0.0:18080", "--release", "ir02-18080"])
        # Repeated functional requests gate readiness; this is not a delay-only check.
        ready: dict[str, Any] | None = None
        for attempt in range(20):
            ready = probe(evidence, f"listener_18080_readiness_{attempt + 1}", container, 18080)
            if ready["returncode"] == 0 and ready["output"] == "200":
                break
        if ready is None or ready["returncode"] != 0 or ready["output"] != "200":
            raise RuntimeError("IR-02 synthetic service did not pass a real HTTP readiness probe")
        evidence["probes"]["baseline_allowed_port"] = ready
        neg_baseline = probe(evidence, "baseline_negative_control_before_rule", container, 18081)
        if neg_baseline["returncode"] == 0:
            raise RuntimeError("negative-control port unexpectedly accepted a TCP/HTTP probe")
        allowed_again = probe(evidence, "allowed_control_during_incident", container, 18080)
        if allowed_again["returncode"] != 0 or allowed_again["output"] != "200":
            raise RuntimeError("allowed control stopped responding before fault injection")
        require(evidence, "inject_fault_rule", ["docker", "exec", container, "iptables", "-I", "INPUT", "1", "-i", "lo",
                "-s", "127.0.0.1", "-d", "127.0.0.1", "-p", "tcp", "--dport", "18080", "-j", "REJECT", "--reject-with", "tcp-reset"])
        failure = probe(evidence, "fault_same_probe", container, 18080)
        if failure["returncode"] == 0:
            raise RuntimeError("injected firewall rule did not cause an observed probe failure")
        require(evidence, "observe_firewall_counters", ["docker", "exec", container, "iptables", "-L", "INPUT", "-n", "-v", "-x", "--line-numbers"])
        require(evidence, "remove_only_fault_rule", ["docker", "exec", container, "iptables", "-D", "INPUT", "-i", "lo", "-s",
                "127.0.0.1", "-d", "127.0.0.1", "-p", "tcp", "--dport", "18080", "-j", "REJECT", "--reject-with", "tcp-reset"])
        recovery = probe(evidence, "recovery_same_probe", container, 18080)
        negative_after = probe(evidence, "negative_control_after_recovery", container, 18081)
        counters = evidence["commands"]["observe_firewall_counters"]["output"]
        checks = {
            "baseline_functional_probe_passed": ready["output"] == "200",
            "negative_control_remained_blocked": neg_baseline["returncode"] != 0 and negative_after["returncode"] != 0,
            "allowed_control_remained_healthy": allowed_again["output"] == "200",
            "fault_tuple_failed": failure["returncode"] != 0,
            "root_cause_rule_counter_incremented": any(len(line.split()) > 2 and line.split()[0].isdigit() and int(line.split()[1]) > 0 and "dpt:18080" in line for line in counters.splitlines()),
            "same_probe_recovered": recovery["returncode"] == 0 and recovery["output"] == "200",
            "fault_rule_removed": "--dport 18080" not in invoke(["docker", "exec", container, "iptables", "-S", "INPUT"])["output"],
        }
        evidence["checks"] = checks
        evidence["ok"] = all(checks.values())
        evidence["status"] = "LOCAL_VERIFIED" if evidence["ok"] else "FAILED"
        evidence["host_scope_assertion"] = "Windows host firewall and host routes were not addressed by any command; container network is none and veth endpoints exist only inside the disposable namespace."
    finally:
        if created:
            cleanup = invoke(["docker", "rm", "--force", container], timeout=30)
            evidence["cleanup"] = {"remove_container": cleanup, "container_absent": invoke(["docker", "inspect", container])["returncode"] != 0}
            if not evidence["cleanup"]["container_absent"]:
                evidence["status"] = "FAILED_CLEANUP"
        evidence["completed_at_utc"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
        evidence_path.parent.mkdir(parents=True, exist_ok=True)
        evidence_path.write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return evidence


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image", required=True, help="pre-existing local Linux image by immutable digest")
    parser.add_argument("--binary", type=Path, required=True, help="statically linked Linux health server")
    parser.add_argument("--evidence", type=Path, default=Path(__file__).resolve().parents[1] / "evidence" / "IR-02_local-filter.json")
    args = parser.parse_args()
    result = run(args.image, args.binary, args.evidence)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("ok") and result.get("cleanup", {}).get("container_absent") else 2


if __name__ == "__main__":
    raise SystemExit(main())
