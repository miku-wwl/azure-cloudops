"""Unit tests for local telemetry grouping and operation correlation."""

from __future__ import annotations

import unittest

from telemetry_model import (
    filter_time,
    load_fixture,
    summarize_requests,
    transaction_timeline,
)


class TelemetryFixtureTests(unittest.TestCase):
    def setUp(self) -> None:
        self.events = load_fixture()["events"]

    def test_request_count_uses_item_count_not_stored_row_count(self) -> None:
        rows = summarize_requests(self.events, 100, 104, 5)
        checkout = next(row for row in rows if row["role"] == "checkout-api")
        self.assertEqual(checkout["row_count"], 2)
        self.assertEqual(checkout["request_count"], 5)
        self.assertEqual(checkout["failed_count"], 4)

    def test_roles_are_separate_aggregation_dimensions(self) -> None:
        rows = summarize_requests(self.events, 100, 104, 5)
        self.assertEqual([row["role"] for row in rows], ["catalog-api", "checkout-api"])

    def test_time_filter_excludes_old_event(self) -> None:
        result = filter_time(self.events, 100, 104)
        self.assertNotIn("req-old", [event["id"] for event in result])

    def test_time_filter_includes_both_explicit_boundaries(self) -> None:
        events = [
            {"table": "AppRequests", "time_minute": 10, "id": "a", "operation_id": "op", "role": "api", "item_count": 1},
            {"table": "AppRequests", "time_minute": 20, "id": "b", "operation_id": "op", "role": "api", "item_count": 1},
        ]
        self.assertEqual([item["id"] for item in filter_time(events, 10, 20)], ["a", "b"])

    def test_invalid_time_range_and_bin_width_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            filter_time(self.events, 20, 10)
        with self.assertRaises(ValueError):
            summarize_requests(self.events, 100, 104, 0)


class CorrelationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.events = load_fixture()["events"]

    def test_operation_id_groups_request_dependency_and_exception(self) -> None:
        result = transaction_timeline(self.events, "op-7")
        self.assertEqual(result["records"], ["req-17", "dep-31", "exc-9"])
        self.assertEqual(
            result["links"], [["req-17", "dep-31"], ["req-17", "exc-9"]]
        )
        self.assertEqual(result["status"], "OBSERVED_LINKS")

    def test_parent_id_checks_direct_relationship(self) -> None:
        result = transaction_timeline(self.events, "op-8")
        self.assertEqual(result["links"], [["req-18", "dep-32"]])

    def test_missing_parent_is_partial_evidence_not_no_event(self) -> None:
        result = transaction_timeline(self.events, "op-10")
        self.assertEqual(result["status"], "PARTIAL_PARENT_LINKS")
        self.assertEqual(result["records"], ["dep-orphan"])
        self.assertEqual(result["unmatched_parent_ids"], ["req-not-collected"])

    def test_no_rows_is_reported_without_assigning_a_root_cause(self) -> None:
        self.assertEqual(
            transaction_timeline(self.events, "op-absent"),
            {"status": "NO_MATCHING_ROWS", "records": [], "links": [], "unmatched_parent_ids": []},
        )

    def test_timeline_order_is_deterministic(self) -> None:
        result = transaction_timeline(list(reversed(self.events)), "op-7")
        self.assertEqual(result["records"], ["req-17", "dep-31", "exc-9"])


class FixtureAcceptanceTests(unittest.TestCase):
    def test_all_fixture_cases_match(self) -> None:
        data = load_fixture()
        for case in data["cases"]:
            with self.subTest(case=case["id"]):
                if case["mode"] == "request_summary":
                    actual = summarize_requests(
                        data["events"], case["start_minute"], case["end_minute"], case["bin_minutes"]
                    )
                else:
                    actual = transaction_timeline(data["events"], case["operation_id"])
                self.assertEqual(actual, case["expected"])


if __name__ == "__main__":
    unittest.main()
