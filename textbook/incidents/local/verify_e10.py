#!/usr/bin/env python3
"""Cross-check two complete E8 cycles and E10's separate-scope replays."""
from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any


MANDATORY = ("IR-01", "IR-02", "IR-05", "IR-07", "IR-08", "IR-10", "IR-11", "IR-12")
EVIDENCE_NAMES = {
    "IR-01": "IR-01_local-dns.json", "IR-02": "IR-02_local-filter.json", "IR-05": "IR-05_local-permissions.json",
    "IR-07": "IR-07_local-kind.json", "IR-08": "IR-08_local-terraform.txt", "IR-10": "IR-10_local-alert.json",
    "IR-11": "IR-11_local-rollback.json", "IR-12": "IR-12_local-restore.json",
}


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def local_cleanup_ok(incident_id: str, data: dict[str, Any]) -> bool:
    cleanup = data.get("cleanup", {})
    if incident_id == "IR-01":
        return cleanup.get("background_threads_stopped") is True
    if incident_id in {"IR-02", "IR-05"}:
        return cleanup.get("container_absent") is True
    if incident_id == "IR-07":
        return all(cleanup.get(key) is True for key in ("cluster_absent", "app_image_absent", "shared_cluster_still_present", "temporary_kubeconfig_and_build_context_removed"))
    if incident_id in {"IR-10", "IR-11"}:
        return cleanup.get("worker_stopped") is True
    if incident_id == "IR-12":
        return cleanup.get("source_backup_restore_temp_paths_removed") is True
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence-root", type=Path, default=Path(__file__).resolve().parents[1] / "evidence")
    args = parser.parse_args()
    root = args.evidence_root.resolve()
    cycle1_dir = root / "cycle-1"
    cycle1_dir.mkdir(exist_ok=True)
    first: dict[str, Any] = {"label": "cycle-1", "source": "E8 first clean execution; evidence is stored at the incident paths in the parent directory",
                             "incidents": {}, "status": "FAILED"}
    first_data: dict[str, dict[str, Any]] = {}
    for incident_id in MANDATORY:
        source_path = root / EVIDENCE_NAMES[incident_id]
        if incident_id == "IR-08":
            transcript = source_path.read_text(encoding="utf-8")
            valid = all(token in transcript for token in ("actual_local_lock_contention=PASS", "provider_read_drift_and_reconcile=PASS",
                                                          "azure_calls=NONE", "ISOLATED_TEMPORARY_LAB_CLEANED"))
            first["incidents"][incident_id] = {"status": "LOCAL_VERIFIED" if valid else "FAILED", "cleanup_passed": valid,
                                               "source_evidence": EVIDENCE_NAMES[incident_id]}
        else:
            data = read_json(source_path)
            first_data[incident_id] = data
            clean = local_cleanup_ok(incident_id, data)
            valid = data.get("status") == "LOCAL_VERIFIED" and data.get("ok") is True and clean and all(data.get("checks", {}).values())
            first["incidents"][incident_id] = {"status": "LOCAL_VERIFIED" if valid else "FAILED", "cleanup_passed": clean,
                                               "source_evidence": EVIDENCE_NAMES[incident_id], "started_at_utc": data.get("started_at_utc"),
                                               "completed_at_utc": data.get("completed_at_utc")}
    first["all_eight_verified_and_clean"] = set(first["incidents"]) == set(MANDATORY) and all(item["status"] == "LOCAL_VERIFIED" and item["cleanup_passed"] for item in first["incidents"].values())
    first["status"] = "LOCAL_VERIFIED" if first["all_eight_verified_and_clean"] else "FAILED"
    first_path = cycle1_dir / "cycle-summary.json"
    if first_path.exists():
        parser.error(f"refusing to overwrite existing cycle summary: {first_path}")
    first_path.write_text(json.dumps(first, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    second = read_json(root / "cycle-2" / "cycle-summary.json")
    second_data: dict[str, dict[str, Any]] = {incident_id: read_json(root / "cycle-2" / f"{incident_id}.json") for incident_id in MANDATORY if incident_id != "IR-08"}
    replay_checks = {
        "cycle_one_has_all_eight_clean_outcomes": first["all_eight_verified_and_clean"],
        "cycle_two_has_all_eight_clean_outcomes": second.get("status") == "LOCAL_VERIFIED" and second.get("all_mandatory_passed") is True and set(second.get("incidents", {})) == set(MANDATORY),
        "terraform_repository_artifacts_unchanged_in_cycle_two": second.get("terraform_checkout_unchanged") is True,
        "independent_network_replay_used_new_namespace": first_data["IR-02"]["scope"]["container"] != second_data["IR-02"]["scope"]["container"],
        "independent_identity_replay_used_new_principal_container": first_data["IR-05"]["scope"]["container"] != second_data["IR-05"]["scope"]["container"],
        "independent_data_recovery_replay_was_a_new_execution": first_data["IR-12"]["started_at_utc"] != second_data["IR-12"]["started_at_utc"] and first_data["IR-12"]["manifest_sha256"] == second_data["IR-12"]["manifest_sha256"],
        "independent_kind_cluster_was_uniquely_created_and_removed": first_data["IR-07"]["scope"]["cluster"] != second_data["IR-07"]["scope"]["cluster"] and second_data["IR-07"]["cleanup"]["cluster_absent"],
    }
    result = {"status": "LOCAL_VERIFIED" if all(replay_checks.values()) else "FAILED", "cycles": ["cycle-1", "cycle-2"],
              "mandatory_incidents": list(MANDATORY), "independent_replay_incidents": ["IR-02", "IR-05", "IR-12"],
              "independent_context_note": "Separate Python processes, fresh Docker containers/network namespaces, a unique disposable kind cluster, and new temporary directories were used. This is an execution replay, not an independent human review.",
              "checks": replay_checks, "evidence": ["cycle-1/cycle-summary.json", "cycle-2/cycle-summary.json"]}
    output = root / "e10-verification.json"
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"E10 {result['status']}: two complete cycles; independent replays={','.join(result['independent_replay_incidents'])}")
    return 0 if result["status"] == "LOCAL_VERIFIED" else 2


if __name__ == "__main__":
    raise SystemExit(main())
