#!/usr/bin/env python3
"""Delete one synthetic source object and verify checksum-based restore elsewhere."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(evidence_path: Path) -> dict[str, Any]:
    evidence: dict[str, Any] = {"incident_id": "IR-12", "status": "FAILED",
                                "started_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                                "mechanism": "All records are deterministic synthetic JSON. A pre-fault SHA-256 manifest validates a separate backup; the missing source object is restored into a new path without overwriting source data.",
                                "scope": {"business_data_used": False, "restore_overwrites_source": False}}
    with tempfile.TemporaryDirectory(prefix="azure-cloudops-ir12-") as temporary:
        root = Path(temporary)
        source, backup, restore = root / "source", root / "backup", root / "restore"
        source.mkdir()
        backup.mkdir()
        records = {
            "record-001.json": {"id": "synthetic-001", "amount": 125, "currency": "NZD"},
            "record-002.json": {"id": "synthetic-002", "amount": 340, "currency": "NZD"},
            "record-003.json": {"id": "synthetic-003", "amount": 75, "currency": "NZD"},
        }
        for name, value in records.items():
            (source / name).write_text(json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
        manifest = {"objects": [{"name": name, "bytes": (source / name).stat().st_size, "sha256": sha(source / name)} for name in sorted(records)]}
        manifest_path = backup / "manifest.json"
        manifest_path.write_text(json.dumps(manifest, sort_keys=True, indent=2) + "\n", encoding="utf-8")
        for item in manifest["objects"]:
            shutil.copy2(source / item["name"], backup / item["name"])
        backup_before = {name: sha(backup / name) for name in sorted(records)}
        baseline_reads = {name: json.loads((source / name).read_text(encoding="utf-8")) for name in sorted(records)}
        baseline_manifest_valid = len(manifest["objects"]) == len(records) and all(item["sha256"] == sha(source / item["name"]) for item in manifest["objects"])
        missing_name = "record-002.json"
        (source / missing_name).unlink()
        source_missing = not (source / missing_name).exists()
        source_read_error: str | None = None
        try:
            (source / missing_name).read_bytes()
        except FileNotFoundError as exc:
            source_read_error = type(exc).__name__
        expected = next(item for item in manifest["objects"] if item["name"] == missing_name)
        backup_hash_before = sha(backup / missing_name)
        restore.mkdir()
        destination = restore / missing_name
        recovery_start = time.monotonic()
        shutil.copy2(backup / missing_name, destination)
        restored_hash = sha(destination)
        recovery_seconds = round(time.monotonic() - recovery_start, 6)
        restored_records = {path.name: json.loads(path.read_text(encoding="utf-8")) for path in sorted(restore.glob("*.json"))}
        # Apply fixture-level validation to unaffected source objects plus the new restored object.
        complete_set = {name: json.loads((source / name).read_text(encoding="utf-8")) for name in sorted(records) if (source / name).exists()}
        complete_set[missing_name] = json.loads(destination.read_text(encoding="utf-8"))
        backup_after = {name: sha(backup / name) for name in sorted(records)}
        checks = {
            "baseline_manifest_covers_all_synthetic_objects": baseline_manifest_valid,
            "source_loss_is_observed_before_restore": source_missing and source_read_error == "FileNotFoundError" and missing_name not in {path.name for path in source.iterdir()},
            "backup_bytes_match_pre_loss_manifest": backup_hash_before == expected["sha256"] and backup_before[missing_name] == expected["sha256"],
            "restore_target_was_new_and_separate": destination.parent == restore and restore != source and restore != backup,
            "restored_object_matches_expected_hash_and_record": restored_hash == expected["sha256"] and restored_records.get(missing_name) == baseline_reads[missing_name],
            "complete_restored_fixture_matches_manifest": len(complete_set) == len(records) and all(sha((source if (source / item["name"]).exists() else restore) / item["name"]) == item["sha256"] for item in manifest["objects"]),
            "backup_unchanged": backup_before == backup_after,
            "recovery_time_measured": recovery_seconds >= 0,
        }
        evidence.update({"manifest": manifest, "manifest_sha256": sha(manifest_path), "baseline_application_reads": baseline_reads,
                         "source_loss": {"missing_object": missing_name, "source_missing": source_missing, "read_error": source_read_error},
                         "backup_hash_after_source_loss": backup_hash_before, "restored_object_sha256": restored_hash,
                         "restored_record": restored_records[missing_name], "recovery_seconds": recovery_seconds,
                         "checks": checks, "ok": all(checks.values()), "status": "LOCAL_VERIFIED" if all(checks.values()) else "FAILED"})
    evidence["cleanup"] = {"source_backup_restore_temp_paths_removed": True}
    evidence["completed_at_utc"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    evidence_path.parent.mkdir(parents=True, exist_ok=True)
    evidence_path.write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return evidence


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence", type=Path, default=Path(__file__).resolve().parents[1] / "evidence" / "IR-12_local-restore.json")
    args = parser.parse_args()
    result = run(args.evidence)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("ok") and result.get("cleanup", {}).get("source_backup_restore_temp_paths_removed") else 2


if __name__ == "__main__":
    raise SystemExit(main())
