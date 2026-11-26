"""Tests for the synthetic offline recovery acceptance model."""

from __future__ import annotations

import unittest
from copy import deepcopy

from recovery_model import elapsed_minutes, evaluate_case, load_cases


class RecoveryModelTests(unittest.TestCase):
    def setUp(self):
        self.cases = {case["id"]: case for case in load_cases()}

    def test_elapsed_minutes_respects_timezone_offsets(self):
        self.assertEqual(60, elapsed_minutes("2026-11-27T10:00:00+13:00", "2026-11-27T11:00:00+13:00"))

    def test_naive_timestamp_is_rejected(self):
        with self.assertRaises(ValueError):
            elapsed_minutes("2026-11-27T10:00:00", "2026-11-27T11:00:00")

    def test_negative_elapsed_time_is_rejected(self):
        with self.assertRaises(ValueError):
            elapsed_minutes("2026-11-27T11:00:00+13:00", "2026-11-27T10:00:00+13:00")

    def test_backup_restore_passes_only_after_all_local_gates(self):
        result = evaluate_case(self.cases["backup-restore-with-valid-ledger"])
        self.assertEqual(8, result["rpo_minutes"])
        self.assertEqual(43, result["rto_minutes"])
        self.assertEqual(5, result["recovery_delay_minutes"])
        self.assertTrue(result["passed"])

    def test_rto_includes_detection_and_recovery_start_delay(self):
        case = deepcopy(self.cases["backup-restore-with-valid-ledger"])
        case["recovery_started_at"] = "2026-11-27T10:15:00+13:00"
        result = evaluate_case(case)
        self.assertEqual(15, result["recovery_delay_minutes"])
        self.assertEqual(28, result["restore_duration_minutes"])
        self.assertEqual(43, result["rto_minutes"])

    def test_crash_consistency_label_does_not_auto_fail_or_auto_pass(self):
        case = deepcopy(self.cases["crash-consistent-point-needs-repair"])
        case["actual_rows"] = case["expected_rows"]
        case["actual_sha256"] = case["expected_sha256"]
        case["application_probe_passed"] = True
        self.assertTrue(evaluate_case(case)["passed"])

    def test_restore_failure_detects_integrity_and_application_checks(self):
        result = evaluate_case(self.cases["crash-consistent-point-needs-repair"])
        self.assertIn("record_count_matches", result["failed_checks"])
        self.assertIn("digest_matches", result["failed_checks"])
        self.assertIn("application_probe_passed", result["failed_checks"])

    def test_latest_processed_asr_case_meets_synthetic_objectives(self):
        result = evaluate_case(self.cases["asr-latest-processed-fast-start"])
        self.assertEqual(9, result["rpo_minutes"])
        self.assertEqual(25, result["rto_minutes"])
        self.assertTrue(result["passed"])

    def test_latest_point_has_lower_rpo_but_can_miss_rto(self):
        result = evaluate_case(self.cases["asr-latest-better-rpo-misses-rto"])
        self.assertEqual(2, result["rpo_minutes"])
        self.assertEqual(52, result["rto_minutes"])
        self.assertIn("rto_within_target", result["failed_checks"])

    def test_asr_drill_requires_isolated_network(self):
        result = evaluate_case(self.cases["asr-test-network-not-isolated"])
        self.assertIn("target_isolated", result["failed_checks"])

    def test_asr_drill_requires_cleanup_to_close(self):
        result = evaluate_case(self.cases["asr-test-network-not-isolated"])
        self.assertIn("test_cleanup_complete", result["failed_checks"])

    def test_backup_restore_does_not_require_asr_cleanup_field(self):
        case = deepcopy(self.cases["backup-restore-with-valid-ledger"])
        case.pop("cleanup_complete")
        self.assertTrue(evaluate_case(case)["passed"])

    def test_unknown_mode_is_rejected(self):
        case = deepcopy(self.cases["backup-restore-with-valid-ledger"])
        case["mode"] = "production_failover"
        with self.assertRaises(ValueError):
            evaluate_case(case)

    def test_unknown_consistency_is_rejected(self):
        case = deepcopy(self.cases["backup-restore-with-valid-ledger"])
        case["consistency"] = "maybe-consistent"
        with self.assertRaises(ValueError):
            evaluate_case(case)

    def test_negative_row_count_is_rejected(self):
        case = deepcopy(self.cases["backup-restore-with-valid-ledger"])
        case["actual_rows"] = -1
        with self.assertRaises(ValueError):
            evaluate_case(case)

    def test_negative_target_is_rejected(self):
        case = deepcopy(self.cases["backup-restore-with-valid-ledger"])
        case["rpo_target_minutes"] = -1
        with self.assertRaises(ValueError):
            evaluate_case(case)


if __name__ == "__main__":
    unittest.main()
