"""Offline model for synthetic Log Analytics and Application Insights telemetry."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any


TABLES = {"AppRequests", "AppDependencies", "AppExceptions"}


def load_fixture() -> dict[str, Any]:
    path = Path(__file__).parent / "fixtures" / "telemetry-cases.json"
    return json.loads(path.read_text(encoding="utf-8"))


def validate_event(event: dict[str, Any]) -> None:
    if event.get("table") not in TABLES:
        raise ValueError(f"unsupported table: {event.get('table')!r}")
    for field in ("time_minute", "id", "operation_id", "role", "item_count"):
        if field not in event:
            raise ValueError(f"missing required field: {field}")
    if int(event["item_count"]) < 1:
        raise ValueError("item_count must be positive")


def filter_time(events: list[dict[str, Any]], start_minute: int, end_minute: int) -> list[dict[str, Any]]:
    if start_minute > end_minute:
        raise ValueError("start_minute must be <= end_minute")
    for event in events:
        validate_event(event)
    return [
        event for event in events
        if start_minute <= int(event["time_minute"]) <= end_minute
    ]


def summarize_requests(
    events: list[dict[str, Any]], start_minute: int, end_minute: int, bin_minutes: int
) -> list[dict[str, Any]]:
    if bin_minutes < 1:
        raise ValueError("bin_minutes must be at least 1")
    selected = [
        event for event in filter_time(events, start_minute, end_minute)
        if event["table"] == "AppRequests"
    ]
    groups: dict[tuple[int, str], list[dict[str, Any]]] = defaultdict(list)
    for event in selected:
        bucket = (int(event["time_minute"]) // bin_minutes) * bin_minutes
        groups[(bucket, str(event["role"]))].append(event)

    results = []
    for (bucket, role), records in sorted(groups.items()):
        results.append({
            "bin_start": bucket,
            "role": role,
            "row_count": len(records),
            "request_count": sum(int(record["item_count"]) for record in records),
            "failed_count": sum(
                int(record["item_count"])
                for record in records
                if record.get("success") is False
            ),
        })
    return results


def transaction_timeline(events: list[dict[str, Any]], operation_id: str) -> dict[str, Any]:
    records = [event for event in events if event.get("operation_id") == operation_id]
    records.sort(key=lambda event: (int(event["time_minute"]), str(event["table"]), str(event["id"])))
    visible_ids = {str(event["id"]) for event in records}
    links: list[list[str]] = []
    unmatched_parent_ids: set[str] = set()
    for event in records:
        parent_id = event.get("parent_id")
        if not parent_id:
            continue
        if str(parent_id) in visible_ids:
            links.append([str(parent_id), str(event["id"])])
        elif event["table"] != "AppRequests":
            unmatched_parent_ids.add(str(parent_id))

    status = "NO_MATCHING_ROWS" if not records else (
        "PARTIAL_PARENT_LINKS" if unmatched_parent_ids else "OBSERVED_LINKS"
    )
    return {
        "status": status,
        "records": [str(event["id"]) for event in records],
        "links": sorted(links),
        "unmatched_parent_ids": sorted(unmatched_parent_ids),
    }


def run_cases() -> int:
    fixture = load_fixture()
    failures = 0
    for case in fixture["cases"]:
        if case["mode"] == "request_summary":
            result = summarize_requests(
                fixture["events"], case["start_minute"], case["end_minute"], case["bin_minutes"]
            )
        elif case["mode"] == "transaction":
            result = transaction_timeline(fixture["events"], case["operation_id"])
        else:
            raise ValueError(f"unsupported case mode: {case['mode']!r}")
        passed = result == case["expected"]
        print(f"{case['id']}: {'PASS' if passed else 'FAIL'}")
        if not passed:
            print(f"  expected={case['expected']}")
            print(f"  actual={result}")
            failures += 1
    print(f"Fixture cases: {len(fixture['cases'])}; failed: {failures}")
    return int(failures > 0)


if __name__ == "__main__":
    raise SystemExit(run_cases())
