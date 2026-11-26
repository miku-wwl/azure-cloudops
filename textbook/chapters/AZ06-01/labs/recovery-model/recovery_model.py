"""Offline recovery-point, RPO/RTO and integrity model for synthetic cases."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path


HERE = Path(__file__).resolve().parent
FIXTURE = HERE / "fixtures" / "recovery-cases.json"
VALID_MODES = {"backup_restore_test", "asr_test_failover"}
VALID_CONSISTENCY = {"application", "file-system", "crash"}


def elapsed_minutes(earlier: str, later: str) -> float:
    """Return elapsed minutes for timezone-aware ISO-8601 timestamps."""
    start = datetime.fromisoformat(earlier)
    end = datetime.fromisoformat(later)
    if start.tzinfo is None or end.tzinfo is None:
        raise ValueError("timestamps must include timezone offsets")
    minutes = (end - start).total_seconds() / 60
    if minutes < 0:
        raise ValueError("recovery timestamps must be in chronological order")
    return minutes


def evaluate_case(case: dict) -> dict:
    """Check a synthetic recovered service against time, data and isolation gates."""
    mode = case["mode"]
    if mode not in VALID_MODES:
        raise ValueError(f"unsupported mode: {mode}")
    if case["consistency"] not in VALID_CONSISTENCY:
        raise ValueError(f"unsupported consistency: {case['consistency']}")
    if case["expected_rows"] < 0 or case["actual_rows"] < 0:
        raise ValueError("row counts must be non-negative")
    if case["rpo_target_minutes"] < 0 or case["rto_target_minutes"] < 0:
        raise ValueError("RPO and RTO targets must be non-negative")

    rpo = elapsed_minutes(case["recovery_point_at"], case["failure_at"])
    recovery_delay = elapsed_minutes(case["failure_at"], case["recovery_started_at"])
    restore_duration = elapsed_minutes(case["recovery_started_at"], case["service_verified_at"])
    rto = recovery_delay + restore_duration
    checks = {
        "rpo_within_target": rpo <= case["rpo_target_minutes"],
        "rto_within_target": rto <= case["rto_target_minutes"],
        "record_count_matches": case["expected_rows"] == case["actual_rows"],
        "digest_matches": case["expected_sha256"] == case["actual_sha256"],
        "application_probe_passed": bool(case["application_probe_passed"]),
    }
    if mode == "asr_test_failover":
        checks["target_isolated"] = bool(case["target_isolated"])
        checks["test_cleanup_complete"] = bool(case["cleanup_complete"])

    return {
        "id": case["id"],
        "mode": mode,
        "consistency": case["consistency"],
        "rpo_minutes": round(rpo, 2),
        "recovery_delay_minutes": round(recovery_delay, 2),
        "restore_duration_minutes": round(restore_duration, 2),
        "rto_minutes": round(rto, 2),
        "checks": checks,
        "passed": all(checks.values()),
        "failed_checks": [name for name, passed in checks.items() if not passed],
    }


def load_cases() -> list[dict]:
    payload = json.loads(FIXTURE.read_text(encoding="utf-8"))
    return payload["cases"]


def main() -> None:
    for case in load_cases():
        result = evaluate_case(case)
        state = "PASS" if result["passed"] else "FAIL"
        print(f"{state} {result['id']}: RPO={result['rpo_minutes']}m RTO={result['rto_minutes']}m")
        if result["failed_checks"]:
            print("  failed: " + ", ".join(result["failed_checks"]))
    print("Synthetic cases only; no Azure Backup, Site Recovery, VM, database or cost was queried.")


if __name__ == "__main__":
    main()
