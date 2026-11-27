#!/usr/bin/env python3
"""Exercise Linux file authorization as UID/GID 65534 in a disposable container."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def invoke(args: list[str], timeout: int = 15, input_bytes: bytes | None = None) -> dict[str, Any]:
    result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=timeout, check=False, input=input_bytes)
    return {"command": args, "returncode": result.returncode,
            "output": result.stdout.decode("utf-8", "replace").strip()}


def run(image: str, evidence_path: Path) -> dict[str, Any]:
    container = f"azure-cloudops-ir05-{uuid.uuid4().hex[:10]}"
    root = f"/tmp/{container}"
    object_path = f"{root}/in-scope.txt"
    negative_path = f"{root}/neighbor.txt"
    payload = b"synthetic-fixture=IR-05\n"
    digest = hashlib.sha256(payload).hexdigest()
    evidence: dict[str, Any] = {
        "incident_id": "IR-05", "status": "FAILED", "started_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "scope": {"container": container, "uid": 65534, "gid": 65534, "network": "none", "objects": [object_path, negative_path]},
        "mechanism": "Root creates synthetic files inside one disposable networkless container; every authorization probe runs through docker exec as UID/GID 65534. No host account, Azure token, or cloud role is touched.",
        "expected_sha256": digest, "commands": {},
    }
    created = False
    try:
        created_result = invoke(["docker", "run", "--detach", "--name", container, "--network", "none", "--entrypoint", "/bin/bash",
                                "--cap-drop", "ALL", "--cap-add", "CHOWN", "--security-opt", "no-new-privileges", image, "-lc", "sleep 600"])
        evidence["commands"]["create_isolated_container"] = created_result
        if created_result["returncode"] != 0:
            raise RuntimeError(created_result["output"])
        created = True
        evidence["container_id"] = created_result["output"]

        def root_call(key: str, *parts: str, input_bytes: bytes | None = None) -> dict[str, Any]:
            result = invoke(["docker", "exec", "-i", container, *parts], input_bytes=input_bytes)
            evidence["commands"][key] = result
            if result["returncode"] != 0:
                raise RuntimeError(f"{key}: {result['output']}")
            return result

        root_call("create_fixture_directory", "mkdir", "-m", "0711", root)
        root_call("write_synthetic_object", "sh", "-c", f"cat > {object_path}", input_bytes=payload)
        root_call("write_neighbor_control", "sh", "-c", f"printf 'out-of-scope=IR-05\\n' > {negative_path}")
        root_call("assign_grants", "chown", "root:65534", object_path)
        root_call("set_granted_read_only_mode", "chmod", "0640", object_path)
        root_call("set_neighbor_owner_and_mode", "sh", "-c", f"chown root:root {negative_path} && chmod 0400 {negative_path}")
        identity = invoke(["docker", "exec", "--user", "65534:65534", container, "id"])
        evidence["commands"]["effective_principal"] = identity
        if identity["returncode"] != 0 or "uid=65534" not in identity["output"] or "gid=65534" not in identity["output"]:
            raise RuntimeError("could not establish the contracted unprivileged principal")

        def user_probe(key: str, *parts: str, input_bytes: bytes | None = None) -> dict[str, Any]:
            result = invoke(["docker", "exec", "-i", "--user", "65534:65534", container, *parts], input_bytes=input_bytes)
            evidence["commands"][key] = result
            return result

        baseline = user_probe("baseline_read", "cat", object_path)
        write_attempt = user_probe("write_negative_control", "sh", "-c", f"printf x >> {object_path}")
        neighbor = user_probe("neighbor_read_negative_control", "cat", negative_path)
        enumeration = user_probe("enumerate_parent_negative_control", "ls", root)
        root_call("remove_read_grant_fault", "chmod", "0000", object_path)
        fault = user_probe("fault_same_read", "cat", object_path)
        exists = root_call("root_confirm_object_exists", "stat", "-c", "%F mode=%a uid=%u gid=%g", object_path)
        root_call("grant_minimal_group_read_repair", "chmod", "0040", object_path)
        recovery = user_probe("recovery_same_read", "cat", object_path)
        recovered_digest = hashlib.sha256(recovery["output"].encode("utf-8") + (b"\n" if recovery["output"] else b"")).hexdigest()
        # docker exec text capture removes the trailing newline, so compare the payload digest directly as well.
        raw_recovery = invoke(["docker", "exec", "--user", "65534:65534", container, "sha256sum", object_path])
        evidence["commands"]["recovered_digest_as_same_principal"] = raw_recovery
        write_after = user_probe("write_negative_control_after_repair", "sh", "-c", f"printf x >> {object_path}")
        neighbor_after = user_probe("neighbor_negative_control_after_repair", "cat", negative_path)
        checks = {
            "principal_is_the_selected_uid_gid": "uid=65534" in identity["output"] and "gid=65534" in identity["output"],
            "baseline_same_object_readable": baseline["returncode"] == 0 and baseline["output"] == payload.decode().rstrip("\n"),
            "write_denied_before_fault": write_attempt["returncode"] != 0 and "Permission denied" in write_attempt["output"],
            "neighbor_denied_before_fault": neighbor["returncode"] != 0 and "Permission denied" in neighbor["output"],
            "directory_not_enumerable": enumeration["returncode"] != 0 and "Permission denied" in enumeration["output"],
            "fault_is_eacces_on_existing_object": fault["returncode"] != 0 and "Permission denied" in fault["output"] and "No such file" not in fault["output"] and exists["returncode"] == 0,
            "same_read_recovered_and_hash_matches": recovery["returncode"] == 0 and recovery["output"] == payload.decode().rstrip("\n") and raw_recovery["returncode"] == 0 and digest in raw_recovery["output"],
            "write_and_neighbor_still_denied": write_after["returncode"] != 0 and neighbor_after["returncode"] != 0,
        }
        evidence["recovery_digest_from_captured_text"] = recovered_digest
        evidence["checks"] = checks
        evidence["ok"] = all(checks.values())
        evidence["status"] = "LOCAL_VERIFIED" if evidence["ok"] else "FAILED"
    finally:
        if created:
            cleanup = invoke(["docker", "rm", "--force", container], timeout=30)
            evidence["cleanup"] = {"remove_container": cleanup, "container_absent": invoke(["docker", "inspect", container])["returncode"] != 0,
                                   "host_accounts_modified": False}
            if not evidence["cleanup"]["container_absent"]:
                evidence["status"] = "FAILED_CLEANUP"
        evidence["completed_at_utc"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
        evidence_path.parent.mkdir(parents=True, exist_ok=True)
        evidence_path.write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return evidence


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image", required=True, help="pre-existing local Linux image by immutable digest")
    parser.add_argument("--evidence", type=Path, default=Path(__file__).resolve().parents[1] / "evidence" / "IR-05_local-permissions.json")
    args = parser.parse_args()
    result = run(args.image, args.evidence)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("ok") and result.get("cleanup", {}).get("container_absent") else 2


if __name__ == "__main__":
    raise SystemExit(main())
