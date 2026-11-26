"""Tests for the synthetic incident investigation and repair contract."""

from __future__ import annotations

import copy
import unittest

from incident_model import evaluate_case, load_case


class IncidentModelTests(unittest.TestCase):
    def setUp(self) -> None:
        self.case = load_case()

    def result(self, case: dict | None = None) -> dict:
        return evaluate_case(case if case is not None else self.case)

    def remove_fact(self, case: dict, fact: str) -> None:
        case["evidence"] = [row for row in case["evidence"] if row["fact"] != fact]

    def test_synthetic_bank_case_passes_every_gate(self) -> None:
        result = self.result()
        self.assertTrue(result["passed"], result["failed_checks"])
        self.assertTrue(result["root_cause_supported"])
        self.assertIn("rates data read role", result["root_cause"])

    def test_rto_runs_from_first_failed_request_to_verified_stability(self) -> None:
        result = self.result()
        self.assertEqual(result["rto_minutes"], 18)
        self.assertEqual(result["detection_delay_minutes"], 1)

    def test_collection_delay_does_not_change_event_time_rto(self) -> None:
        case = copy.deepcopy(self.case)
        next(row for row in case["evidence"] if row["fact"] == "rates_dependency_403")["observed_at"] = "2026-11-27T10:18:00Z"
        result = self.result(case)
        self.assertTrue(result["passed"])
        self.assertEqual(result["rto_minutes"], 18)

    def test_identity_hypothesis_requires_all_discriminating_facts(self) -> None:
        case = copy.deepcopy(self.case)
        self.remove_fact(case, "v2_missing_rates_reader")
        result = self.result(case)
        self.assertFalse(result["root_cause_supported"])
        self.assertEqual(result["root_cause"], "UNRESOLVED")

    def test_wrong_token_audience_does_not_support_missing_role_rca(self) -> None:
        case = copy.deepcopy(self.case)
        self.remove_fact(case, "token_audience_storage")
        result = self.result(case)
        self.assertFalse(result["root_cause_supported"])
        self.assertEqual(result["hypotheses"]["token_audience"], "UNKNOWN")

    def test_dns_and_network_hypotheses_are_only_disfavored_for_tested_path(self) -> None:
        result = self.result()
        self.assertEqual(result["hypotheses"]["private_dns"], "DISFAVORED_FOR_TESTED_PATH")
        self.assertEqual(result["hypotheses"]["network_filter_or_route"], "DISFAVORED_FOR_TESTED_PATH")

    def test_missing_dns_probe_leaves_dns_hypothesis_unknown(self) -> None:
        case = copy.deepcopy(self.case)
        self.remove_fact(case, "dns_answer_expected")
        result = self.result(case)
        self.assertEqual(result["hypotheses"]["private_dns"], "UNKNOWN")
        self.assertTrue(result["passed"])

    def test_unavailable_platform_evidence_is_not_treated_as_no_platform_fault(self) -> None:
        result = self.result()
        self.assertEqual(result["hypotheses"]["azure_platform_event"], "NOT_OBSERVED_NOT_EXCLUDED")

    def test_absence_of_health_snapshot_keeps_platform_hypothesis_unknown(self) -> None:
        case = copy.deepcopy(self.case)
        self.remove_fact(case, "no_matching_service_health_event_observed")
        result = self.result(case)
        self.assertEqual(result["hypotheses"]["azure_platform_event"], "UNKNOWN")
        self.assertTrue(result["passed"])

    def test_release_is_recorded_as_trigger_correlation_not_mechanism(self) -> None:
        result = self.result()
        self.assertEqual(result["hypotheses"]["deployment"], "TRIGGER_CORRELATED_NOT_FAILURE_MECHANISM")

    def test_release_after_first_failure_breaks_causal_timeline(self) -> None:
        case = copy.deepcopy(self.case)
        row = next(row for row in case["evidence"] if row["fact"] == "release_changed_principal")
        row["event_time"] = "2026-11-27T10:04:00Z"
        result = self.result(case)
        self.assertFalse(result["checks"]["event_timeline_ordered"])
        self.assertFalse(result["passed"])

    def test_timestamps_must_have_timezone(self) -> None:
        case = copy.deepcopy(self.case)
        case["evidence"][0]["event_time"] = "2026-11-27T09:57:00"
        with self.assertRaisesRegex(ValueError, "timezone"):
            self.result(case)

    def test_duplicate_evidence_ids_are_rejected(self) -> None:
        case = copy.deepcopy(self.case)
        case["evidence"][1]["id"] = case["evidence"][0]["id"]
        with self.assertRaisesRegex(ValueError, "duplicate evidence id"):
            self.result(case)

    def test_exact_container_scope_is_required(self) -> None:
        case = copy.deepcopy(self.case)
        case["repair"]["scope"] = "synthetic://bank/payments"
        self.assertFalse(self.result(case)["checks"]["repair_approved_and_bounded"])

    def test_storage_account_scope_is_too_broad(self) -> None:
        case = copy.deepcopy(self.case)
        case["repair"]["scope"] = "synthetic://bank/payments/storage-account"
        result = self.result(case)
        self.assertFalse(result["passed"])
        self.assertIn("repair_approved_and_bounded", result["failed_checks"])

    def test_owner_or_contributor_repair_is_rejected(self) -> None:
        for role in ("Owner", "Contributor", "Storage Blob Data Contributor"):
            with self.subTest(role=role):
                case = copy.deepcopy(self.case)
                case["repair"]["role"] = role
                self.assertFalse(self.result(case)["checks"]["repair_approved_and_bounded"])

    def test_repair_must_target_selected_workload_identity(self) -> None:
        case = copy.deepcopy(self.case)
        case["repair"]["principal"] = "payments-mi-v1"
        self.assertFalse(self.result(case)["checks"]["repair_approved_and_bounded"])

    def test_repair_requires_recorded_approval(self) -> None:
        case = copy.deepcopy(self.case)
        case["repair"]["approved"] = False
        self.assertFalse(self.result(case)["checks"]["repair_approved_and_bounded"])

    def test_hidden_compensating_changes_are_rejected(self) -> None:
        case = copy.deepcopy(self.case)
        case["repair"]["other_changes"] = ["disable_network_rules"]
        self.assertFalse(self.result(case)["checks"]["repair_approved_and_bounded"])

    def test_recovery_must_reuse_the_baseline_probe(self) -> None:
        case = copy.deepcopy(self.case)
        case["recovery"]["probe_id"] = "health-live"
        result = self.result(case)
        self.assertFalse(result["checks"]["same_business_probe_recovered"])

    def test_api_success_without_storage_success_fails(self) -> None:
        case = copy.deepcopy(self.case)
        case["recovery"]["storage_dependency_status"] = 403
        self.assertFalse(self.result(case)["checks"]["same_business_probe_recovered"])

    def test_non_success_api_response_fails(self) -> None:
        case = copy.deepcopy(self.case)
        case["recovery"]["api_status"] = 503
        self.assertFalse(self.result(case)["checks"]["same_business_probe_recovered"])

    def test_ledger_digest_failure_blocks_closure_without_erasing_cause_evidence(self) -> None:
        case = copy.deepcopy(self.case)
        case["recovery"]["ledger_digest_matches"] = False
        result = self.result(case)
        self.assertTrue(result["root_cause_supported"])
        self.assertFalse(result["checks"]["ledger_integrity_and_idempotency"])
        self.assertFalse(result["passed"])

    def test_duplicate_business_write_is_rejected(self) -> None:
        case = copy.deepcopy(self.case)
        case["recovery"]["ledger_record_delta"] = 2
        self.assertFalse(self.result(case)["checks"]["ledger_integrity_and_idempotency"])

    def test_idempotency_failure_blocks_closure(self) -> None:
        case = copy.deepcopy(self.case)
        case["recovery"]["idempotency_check_passed"] = False
        self.assertFalse(self.result(case)["checks"]["ledger_integrity_and_idempotency"])

    def test_negative_access_control_must_still_deny_unrelated_scope(self) -> None:
        case = copy.deepcopy(self.case)
        case["recovery"]["unrelated_scope_access_denied"] = False
        result = self.result(case)
        self.assertFalse(result["checks"]["unrelated_scope_remains_denied"])
        self.assertFalse(result["passed"])

    def test_unrelated_scope_evidence_must_match_the_recovery_probe(self) -> None:
        case = copy.deepcopy(self.case)
        self.remove_fact(case, "unrelated_scope_still_denied")
        self.assertFalse(self.result(case)["checks"]["unrelated_scope_remains_denied"])

    def test_stability_window_must_meet_minimum(self) -> None:
        case = copy.deepcopy(self.case)
        case["recovery"]["stable_window_minutes"] = 4.99
        self.assertFalse(self.result(case)["checks"]["stable_window_and_queue_recovered"])

    def test_queue_must_drain(self) -> None:
        case = copy.deepcopy(self.case)
        case["recovery"]["queue_drained"] = False
        self.assertFalse(self.result(case)["checks"]["stable_window_and_queue_recovered"])

    def test_rto_target_includes_detection_diagnosis_and_repair_delay(self) -> None:
        case = copy.deepcopy(self.case)
        case["episode"]["rto_target_minutes"] = 17
        self.assertFalse(self.result(case)["checks"]["operational_rto_within_target"])


if __name__ == "__main__":
    unittest.main()
