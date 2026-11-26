"""Synthetic incident timeline, hypothesis and bounded-repair model."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path


HERE = Path(__file__).resolve().parent
FIXTURE = HERE / "fixtures" / "bank-incident.json"
REQUIRED_SCOPE = "synthetic://bank/payments/blobServices/default/containers/rates"
REQUIRED_PRINCIPAL = "payments-mi-v2"
REQUIRED_ROLE = "Storage Blob Data Reader"
REQUIRED_CAUSAL_FACTS = {
    "known_good_same_probe",
    "release_changed_principal",
    "rates_dependency_403",
    "token_audience_storage",
    "trace_principal_is_v2",
    "v2_missing_rates_reader",
}


def parse_time(value: str) -> datetime:
    """Parse an ISO-8601 timestamp that includes an offset or Z."""
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("timestamps must include a timezone offset")
    return parsed


def elapsed_minutes(start: str, end: str) -> float:
    """Measure elapsed minutes from event timestamps, not ingestion time."""
    minutes = (parse_time(end) - parse_time(start)).total_seconds() / 60
    if minutes < 0:
        raise ValueError("timestamps must be in chronological order")
    return round(minutes, 2)


def evidence_facts(case: dict) -> tuple[set[str], dict[str, dict]]:
    evidence = case.get("evidence")
    if not isinstance(evidence, list):
        raise ValueError("evidence must be a list")
    ids: set[str] = set()
    rows: dict[str, dict] = {}
    facts: set[str] = set()
    for row in evidence:
        for field in ("id", "fact", "event_time", "observed_at", "source"):
            if field not in row or not row[field]:
                raise ValueError(f"evidence entry is missing {field}")
        if row["id"] in ids:
            raise ValueError(f"duplicate evidence id: {row['id']}")
        ids.add(row["id"])
        parse_time(row["event_time"])
        parse_time(row["observed_at"])
        rows[row["fact"]] = row
        facts.add(row["fact"])
    return facts, rows


def classify_hypotheses(facts: set[str]) -> dict[str, str]:
    """Return evidence states without treating absence as disproof."""
    return {
        "identity_authorization": (
            "SUPPORTED_BY_SYNTHETIC_EVIDENCE"
            if REQUIRED_CAUSAL_FACTS <= facts else "INSUFFICIENT_EVIDENCE"
        ),
        "private_dns": (
            "DISFAVORED_FOR_TESTED_PATH"
            if {"dns_answer_expected", "tcp_connection_succeeded"} <= facts
            else "UNKNOWN"
        ),
        "network_filter_or_route": (
            "DISFAVORED_FOR_TESTED_PATH"
            if {"tcp_connection_succeeded", "rates_dependency_403"} <= facts
            else "UNKNOWN"
        ),
        "database_or_ledger": (
            "DISFAVORED_FOR_TESTED_PATH"
            if {"sql_dependency_succeeded", "ledger_invariants_before_repair"} <= facts
            else "UNKNOWN"
        ),
        "azure_platform_event": (
            "NOT_OBSERVED_NOT_EXCLUDED"
            if "no_matching_service_health_event_observed" in facts
            else "UNKNOWN"
        ),
        "deployment": (
            "TRIGGER_CORRELATED_NOT_FAILURE_MECHANISM"
            if "release_changed_principal" in facts else "UNKNOWN"
        ),
        "token_audience": (
            "DISFAVORED_FOR_TESTED_REQUEST"
            if "token_audience_storage" in facts else "UNKNOWN"
        ),
    }


def evaluate_case(case: dict) -> dict:
    """Evaluate the synthetic RCA contract and its recovery gates."""
    facts, rows = evidence_facts(case)
    episode = case["episode"]
    repair = case["repair"]
    recovery = case["recovery"]

    baseline_at = rows.get("known_good_same_probe", {}).get("event_time")
    release_at = rows.get("release_changed_principal", {}).get("event_time")
    failure_at = episode["first_failed_at"]
    verified_at = episode["verified_at"]
    parse_time(failure_at)
    parse_time(verified_at)
    rto = elapsed_minutes(failure_at, verified_at)
    detection_delay = elapsed_minutes(failure_at, episode["alerted_at"])

    ordered = False
    if baseline_at and release_at:
        ordered = (
            parse_time(baseline_at) < parse_time(release_at)
            <= parse_time(failure_at) <= parse_time(verified_at)
        )

    causal_evidence_complete = REQUIRED_CAUSAL_FACTS <= facts and ordered
    repair_is_bounded = all([
        bool(repair.get("approved")),
        bool(repair.get("approval_id")),
        repair.get("principal") == REQUIRED_PRINCIPAL,
        repair.get("role") == REQUIRED_ROLE,
        repair.get("scope") == REQUIRED_SCOPE,
        not repair.get("other_changes"),
    ])
    same_probe_recovered = all([
        bool(recovery.get("same_probe")),
        recovery.get("probe_id") == case.get("baseline_probe_id"),
        recovery.get("api_status") == 200,
        recovery.get("storage_dependency_status") == 200,
        "same_probe_recovered" in facts,
    ])
    integrity_and_idempotency = all([
        bool(recovery.get("ledger_digest_matches")),
        recovery.get("ledger_record_delta") == 1,
        bool(recovery.get("idempotency_check_passed")),
    ])
    negative_scope_control = all([
        bool(recovery.get("unrelated_scope_access_denied")),
        "unrelated_scope_still_denied" in facts,
    ])
    stable_and_drained = all([
        recovery.get("stable_window_minutes", 0) >= 5,
        bool(recovery.get("queue_drained")),
    ])
    rto_target = episode.get("rto_target_minutes", -1)
    if not isinstance(rto_target, (int, float)) or rto_target < 0:
        raise ValueError("RTO target must be a non-negative number of minutes")

    checks = {
        "event_timeline_ordered": ordered,
        "causal_evidence_complete": causal_evidence_complete,
        "repair_approved_and_bounded": repair_is_bounded,
        "same_business_probe_recovered": same_probe_recovered,
        "ledger_integrity_and_idempotency": integrity_and_idempotency,
        "unrelated_scope_remains_denied": negative_scope_control,
        "stable_window_and_queue_recovered": stable_and_drained,
        "operational_rto_within_target": rto <= rto_target,
    }
    root_cause_supported = all([
        causal_evidence_complete,
        repair_is_bounded,
        same_probe_recovered,
    ])
    return {
        "case_id": case.get("case_id", "unknown"),
        "root_cause": (
            "new workload identity lacks the required rates data read role"
            if root_cause_supported else "UNRESOLVED"
        ),
        "root_cause_supported": root_cause_supported,
        "hypotheses": classify_hypotheses(facts),
        "rto_minutes": rto,
        "detection_delay_minutes": detection_delay,
        "checks": checks,
        "passed": all(checks.values()),
        "failed_checks": [name for name, passed in checks.items() if not passed],
    }


def load_case() -> dict:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def main() -> None:
    result = evaluate_case(load_case())
    state = "PASS" if result["passed"] else "FAIL"
    print(f"{state} {result['case_id']}: RTO={result['rto_minutes']}m; "
          f"detection={result['detection_delay_minutes']}m")
    print(f"  root cause: {result['root_cause']}")
    print("  hypotheses: " + json.dumps(result["hypotheses"], sort_keys=True))
    if result["failed_checks"]:
        print("  failed: " + ", ".join(result["failed_checks"]))
    print("Synthetic fixture only; no Azure, KQL, identity, role or ledger was queried.")


if __name__ == "__main__":
    main()
