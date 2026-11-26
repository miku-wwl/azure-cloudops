"""Offline evaluator for synthetic Azure Monitor metric-alert examples."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any


def aggregate_values(values: list[float], aggregation: str) -> float:
    if not values:
        raise ValueError("cannot aggregate an empty metric window")
    normalized = aggregation.lower()
    if normalized in {"sum", "total"}:
        return float(sum(values))
    if normalized == "count":
        return float(len(values))
    if normalized in {"average", "avg"}:
        return float(sum(values) / len(values))
    if normalized in {"min", "minimum"}:
        return float(min(values))
    if normalized in {"max", "maximum"}:
        return float(max(values))
    raise ValueError(f"unsupported aggregation: {aggregation!r}")


def violates(value: float, operator: str, threshold: float) -> bool:
    if operator == "GreaterThan":
        return value > threshold
    if operator == "GreaterThanOrEqual":
        return value >= threshold
    if operator == "LessThan":
        return value < threshold
    if operator == "LessThanOrEqual":
        return value <= threshold
    raise ValueError(f"unsupported operator: {operator!r}")


def series_groups(case: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    split_by = case.get("split_by", [])
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for point in case["points"]:
        if not split_by:
            name = "All"
        else:
            dimensions = point.get("dimensions", {})
            name = "|".join(f"{field}={dimensions.get(field, '<missing>')}" for field in split_by)
        groups[name].append(point)
    return dict(sorted(groups.items()))


def evaluate_metric_rule(case: dict[str, Any]) -> dict[str, Any]:
    """Evaluate user-supplied buckets, not Azure's provider-side metric pipeline."""
    lookback = int(case["lookback_minutes"])
    if lookback < 1:
        raise ValueError("lookback_minutes must be at least 1")
    stateful = bool(case.get("stateful", True))
    resolved_checks = int(case.get("resolve_after_checks", 3))
    if resolved_checks < 1:
        raise ValueError("resolve_after_checks must be at least 1")

    evaluations: dict[str, list[dict[str, Any]]] = {}
    events: list[dict[str, Any]] = []
    last_values: dict[str, float | None] = {}
    groups = series_groups(case)
    for series, points in groups.items():
        monitor_state = "NoAlert"
        good_checks = 0
        evaluations[series] = []
        for end_minute in case["evaluation_minutes"]:
            window = [
                point
                for point in points
                if end_minute - lookback < int(point["minute"]) <= end_minute
            ]
            if not window:
                evaluations[series].append(
                    {"minute": end_minute, "value": None, "breach": None, "monitor_state": monitor_state}
                )
                continue

            value = aggregate_values([float(point["value"]) for point in window], case["aggregation"])
            breach = violates(value, case["operator"], float(case["threshold"]))
            event_type: str | None = None
            if stateful:
                if breach:
                    good_checks = 0
                    if monitor_state != "Fired":
                        monitor_state = "Fired"
                        event_type = "Fired"
                elif monitor_state == "Fired":
                    good_checks += 1
                    if good_checks >= resolved_checks:
                        monitor_state = "Resolved"
                        event_type = "Resolved"
            elif breach:
                monitor_state = "Fired"
                event_type = "Fired"
            else:
                monitor_state = "NoAlert"

            evaluations[series].append(
                {"minute": end_minute, "value": value, "breach": breach, "monitor_state": monitor_state}
            )
            last_values[series] = value
            if event_type:
                events.append(
                    {
                        "series": series,
                        "minute": end_minute,
                        "type": event_type,
                        "notification_sent": not bool(case.get("suppress_notifications", False)),
                    }
                )

    return {
        "series": list(groups),
        "last_values": last_values,
        "evaluations": evaluations,
        "events": events,
    }


def dynamic_history_status(days: int, samples: int) -> str:
    if days < 3 or samples < 30:
        return "DYNAMIC_HISTORY_INSUFFICIENT"
    if days < 21:
        return "DYNAMIC_BASELINE_READY_WEEKLY_PATTERN_PENDING"
    return "DYNAMIC_WEEKLY_HISTORY_AVAILABLE"


def evaluate_case(case: dict[str, Any]) -> dict[str, Any]:
    mode = case.get("mode")
    if mode == "metric_rule":
        return evaluate_metric_rule(case)
    if mode == "dynamic_history":
        return {"status": dynamic_history_status(int(case["days"]), int(case["samples"]))}
    raise ValueError(f"unsupported mode: {mode!r}")


def case_matches(case: dict[str, Any], result: dict[str, Any]) -> bool:
    expected = case["expected"]
    if case["mode"] == "dynamic_history":
        return result["status"] == expected["status"]
    if result["series"] != expected["series"] or result["events"] != expected["events"]:
        return False
    for series, expected_value in expected["last_values"].items():
        actual = result["last_values"].get(series)
        if actual is None or abs(actual - float(expected_value)) > 1e-9:
            return False
    return True


def run_fixtures() -> int:
    path = Path(__file__).parent / "fixtures" / "metric-alert-cases.json"
    cases = json.loads(path.read_text(encoding="utf-8"))
    failures = 0
    for case in cases:
        result = evaluate_case(case)
        passed = case_matches(case, result)
        if "status" in result:
            detail = result["status"]
        else:
            detail = f"series={len(result['series'])} events={len(result['events'])}"
        print(f"{case['id']}: {'PASS' if passed else 'FAIL'} {detail}")
        if not passed:
            failures += 1
            print(f"  expected={case['expected']}")
            print(f"  actual={result}")
    print(f"Fixture cases: {len(cases)}; failed: {failures}")
    return int(failures > 0)


if __name__ == "__main__":
    raise SystemExit(run_fixtures())
