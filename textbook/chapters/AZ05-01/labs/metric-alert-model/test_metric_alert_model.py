"""Unit tests for metric aggregation, dimensional series, and alert state."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from metric_alert_model import (
    aggregate_values,
    case_matches,
    dynamic_history_status,
    evaluate_metric_rule,
    violates,
)


class AggregationTests(unittest.TestCase):
    def test_average_aggregation(self) -> None:
        self.assertEqual(aggregate_values([40, 96], "Average"), 68)

    def test_total_is_sum(self) -> None:
        self.assertEqual(aggregate_values([2, 3, 4], "Total"), 9)

    def test_count_counts_records_not_sample_values(self) -> None:
        self.assertEqual(aggregate_values([0, 0, 0], "Count"), 3)

    def test_minimum_aggregation(self) -> None:
        self.assertEqual(aggregate_values([70, 95, 88], "Minimum"), 70)

    def test_maximum_aggregation(self) -> None:
        self.assertEqual(aggregate_values([70, 95, 88], "Maximum"), 95)

    def test_empty_window_has_no_aggregate(self) -> None:
        with self.assertRaises(ValueError):
            aggregate_values([], "Average")

    def test_unknown_aggregation_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            aggregate_values([1], "Percentile")

    def test_greater_and_less_operators(self) -> None:
        self.assertTrue(violates(91, "GreaterThan", 90))
        self.assertFalse(violates(90, "GreaterThan", 90))
        self.assertTrue(violates(9, "LessThan", 10))


class DimensionAndWindowTests(unittest.TestCase):
    def setUp(self) -> None:
        self.points = [
            {"minute": 1, "value": 40, "dimensions": {"region": "west", "server": "a"}},
            {"minute": 1, "value": 96, "dimensions": {"region": "east", "server": "b"}},
        ]

    def test_rollup_without_dimensions_can_hide_one_hot_series(self) -> None:
        case = {
            "points": self.points,
            "split_by": [],
            "aggregation": "Average",
            "lookback_minutes": 5,
            "evaluation_minutes": [1],
            "operator": "GreaterThan",
            "threshold": 90,
        }
        result = evaluate_metric_rule(case)
        self.assertEqual(result["series"], ["All"])
        self.assertEqual(result["events"], [])

    def test_split_by_dimension_creates_independent_series(self) -> None:
        case = {
            "points": self.points,
            "split_by": ["region"],
            "aggregation": "Average",
            "lookback_minutes": 5,
            "evaluation_minutes": [1],
            "operator": "GreaterThan",
            "threshold": 90,
        }
        result = evaluate_metric_rule(case)
        self.assertEqual(result["series"], ["region=east", "region=west"])
        self.assertEqual([event["series"] for event in result["events"]], ["region=east"])

    def test_multiple_dimensions_form_a_combination_key(self) -> None:
        case = {
            "points": self.points,
            "split_by": ["region", "server"],
            "aggregation": "Maximum",
            "lookback_minutes": 5,
            "evaluation_minutes": [1],
            "operator": "GreaterThan",
            "threshold": 90,
        }
        result = evaluate_metric_rule(case)
        self.assertIn("region=east|server=b", result["series"])

    def test_missing_dimension_is_explicit_in_series_key(self) -> None:
        case = {
            "points": [{"minute": 1, "value": 5, "dimensions": {}}],
            "split_by": ["region"],
            "aggregation": "Average",
            "lookback_minutes": 1,
            "evaluation_minutes": [1],
            "operator": "GreaterThan",
            "threshold": 4,
        }
        self.assertEqual(evaluate_metric_rule(case)["series"], ["region=<missing>"])

    def test_window_is_open_at_start_and_closed_at_end(self) -> None:
        case = {
            "points": [{"minute": 0, "value": 100}, {"minute": 1, "value": 50}],
            "split_by": [],
            "aggregation": "Maximum",
            "lookback_minutes": 1,
            "evaluation_minutes": [1],
            "operator": "GreaterThan",
            "threshold": 90,
        }
        self.assertEqual(evaluate_metric_rule(case)["last_values"]["All"], 50)

    def test_new_evaluations_recompute_overlapping_lookback_windows(self) -> None:
        case = {
            "points": [{"minute": 1, "value": 95}, {"minute": 2, "value": 70}],
            "split_by": [],
            "aggregation": "Maximum",
            "lookback_minutes": 3,
            "evaluation_minutes": [1, 2],
            "operator": "GreaterThan",
            "threshold": 90,
        }
        result = evaluate_metric_rule(case)
        self.assertEqual([row["value"] for row in result["evaluations"]["All"]], [95, 95])


class AlertStateTests(unittest.TestCase):
    def test_stateful_alert_fires_once_during_continuous_breach(self) -> None:
        case = {
            "points": [{"minute": 1, "value": 95}, {"minute": 2, "value": 96}],
            "split_by": [],
            "aggregation": "Maximum",
            "lookback_minutes": 1,
            "evaluation_minutes": [1, 2],
            "operator": "GreaterThan",
            "threshold": 90,
            "stateful": True,
        }
        result = evaluate_metric_rule(case)
        self.assertEqual([event["type"] for event in result["events"]], ["Fired"])

    def test_stateful_alert_resolves_after_three_good_checks(self) -> None:
        case = {
            "points": [
                {"minute": 1, "value": 95},
                {"minute": 2, "value": 70},
                {"minute": 3, "value": 70},
                {"minute": 4, "value": 70},
            ],
            "split_by": [],
            "aggregation": "Maximum",
            "lookback_minutes": 1,
            "evaluation_minutes": [1, 2, 3, 4],
            "operator": "GreaterThan",
            "threshold": 90,
            "stateful": True,
            "resolve_after_checks": 3,
        }
        result = evaluate_metric_rule(case)
        self.assertEqual([event["type"] for event in result["events"]], ["Fired", "Resolved"])
        self.assertEqual(result["events"][-1]["minute"], 4)

    def test_a_new_breach_after_resolution_fires_again(self) -> None:
        case = {
            "points": [
                {"minute": 1, "value": 95},
                {"minute": 2, "value": 70},
                {"minute": 3, "value": 70},
                {"minute": 4, "value": 70},
                {"minute": 5, "value": 95},
            ],
            "split_by": [],
            "aggregation": "Maximum",
            "lookback_minutes": 1,
            "evaluation_minutes": [1, 2, 3, 4, 5],
            "operator": "GreaterThan",
            "threshold": 90,
            "stateful": True,
        }
        result = evaluate_metric_rule(case)
        self.assertEqual([event["type"] for event in result["events"]], ["Fired", "Resolved", "Fired"])

    def test_stateless_alert_repeats_for_each_violating_check_without_resolve(self) -> None:
        case = {
            "points": [{"minute": 1, "value": 95}, {"minute": 2, "value": 96}, {"minute": 3, "value": 70}],
            "split_by": [],
            "aggregation": "Maximum",
            "lookback_minutes": 1,
            "evaluation_minutes": [1, 2, 3],
            "operator": "GreaterThan",
            "threshold": 90,
            "stateful": False,
        }
        result = evaluate_metric_rule(case)
        self.assertEqual([event["minute"] for event in result["events"]], [1, 2])
        self.assertNotIn("Resolved", [event["type"] for event in result["events"]])

    def test_suppression_changes_notification_not_alert_event(self) -> None:
        case = {
            "points": [{"minute": 1, "value": 95}],
            "split_by": [],
            "aggregation": "Maximum",
            "lookback_minutes": 1,
            "evaluation_minutes": [1],
            "operator": "GreaterThan",
            "threshold": 90,
            "suppress_notifications": True,
        }
        result = evaluate_metric_rule(case)
        self.assertEqual(result["events"][0]["type"], "Fired")
        self.assertFalse(result["events"][0]["notification_sent"])

    def test_bad_lookback_and_resolve_count_are_rejected(self) -> None:
        base = {
            "points": [], "split_by": [], "aggregation": "Average", "lookback_minutes": 0,
            "evaluation_minutes": [], "operator": "GreaterThan", "threshold": 1,
        }
        with self.assertRaises(ValueError):
            evaluate_metric_rule(base)
        base["lookback_minutes"] = 1
        base["resolve_after_checks"] = 0
        with self.assertRaises(ValueError):
            evaluate_metric_rule(base)


class DynamicHistoryTests(unittest.TestCase):
    def test_dynamic_history_requires_three_days_and_thirty_samples(self) -> None:
        self.assertEqual(dynamic_history_status(2, 40), "DYNAMIC_HISTORY_INSUFFICIENT")
        self.assertEqual(dynamic_history_status(3, 29), "DYNAMIC_HISTORY_INSUFFICIENT")

    def test_three_weeks_are_needed_for_weekly_seasonality(self) -> None:
        self.assertEqual(dynamic_history_status(10, 50), "DYNAMIC_BASELINE_READY_WEEKLY_PATTERN_PENDING")
        self.assertEqual(dynamic_history_status(21, 150), "DYNAMIC_WEEKLY_HISTORY_AVAILABLE")

    def test_all_fixtures_match_expected_results(self) -> None:
        cases = json.loads((Path(__file__).parent / "fixtures" / "metric-alert-cases.json").read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(cases), 10)
        for case in cases:
            with self.subTest(case=case["id"]):
                result = (
                    {"status": dynamic_history_status(case["days"], case["samples"])}
                    if case["mode"] == "dynamic_history"
                    else evaluate_metric_rule(case)
                )
                self.assertTrue(case_matches(case, result))


if __name__ == "__main__":
    unittest.main()
