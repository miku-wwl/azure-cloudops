import unittest

from governance_evidence_model import classify_activity, evaluate_defender, evaluate_policy, run_fixture


class PolicyEffectTests(unittest.TestCase):
    def test_audit_allows_request_but_reports_noncompliance(self):
        result = evaluate_policy("audit", True, "create")
        self.assertEqual(result["request"], "NOT_BLOCKED_BY_THIS_EFFECT")
        self.assertEqual(result["compliance"], "NON_COMPLIANT")

    def test_deny_blocks_matching_create_or_update(self):
        for phase in ("create", "update"):
            with self.subTest(phase=phase):
                self.assertEqual(evaluate_policy("deny", True, phase)["request"], "BLOCKED_BY_THIS_EFFECT")

    def test_deny_does_not_repair_existing_resource(self):
        result = evaluate_policy("deny", True, "existing")
        self.assertEqual(result["request"], "NON_COMPLIANT_EXISTING_RESOURCE")
        self.assertEqual(result["follow_up"], "REPAIR_EXISTING_RESOURCE")

    def test_dine_requires_post_success_or_existing_task_path(self):
        request = evaluate_policy("deployIfNotExists", True, "create")
        existing = evaluate_policy("deployIfNotExists", True, "existing")
        self.assertEqual(request["follow_up"], "POST_SUCCESS_DELAY_AND_IDENTITY_DEPLOYMENT")
        self.assertEqual(existing["follow_up"], "REMEDIATION_TASK_REQUIRED")

    def test_nonmatching_condition_is_compliant(self):
        self.assertEqual(evaluate_policy("deny", False, "update")["compliance"], "COMPLIANT")

    def test_invalid_effect_or_phase_is_rejected(self):
        with self.assertRaises(ValueError):
            evaluate_policy("modify", True, "create")
        with self.assertRaises(ValueError):
            evaluate_policy("audit", True, "delete")


class ActivityEvidenceTests(unittest.TestCase):
    def test_started_management_operations_have_activity_log_evidence(self):
        for kind in ("started_management_write", "started_management_action_failure"):
            with self.subTest(kind=kind):
                self.assertEqual(classify_activity(kind)["evidence"], "ACTIVITY_LOG_EXPECTED")

    def test_read_is_not_typically_captured(self):
        self.assertEqual(classify_activity("management_read")["evidence"], "ACTIVITY_LOG_READ_NOT_TYPICALLY_CAPTURED")

    def test_data_plane_read_requires_diagnostics(self):
        self.assertEqual(classify_activity("data_plane_read")["evidence"], "RESOURCE_LOGS_REQUIRE_DIAGNOSTIC_SETTING")
        self.assertEqual(classify_activity("data_plane_read", True)["evidence"], "RESOURCE_LOGS_MAY_BE_AVAILABLE")

    def test_preoperation_denial_has_no_activity_log_entry(self):
        self.assertEqual(classify_activity("pre_operation_authn_authz_rejection")["evidence"], "NO_ACTIVITY_LOG_ENTRY")

    def test_unknown_event_is_rejected(self):
        with self.assertRaises(ValueError):
            classify_activity("imaginary_event")


class DefenderBoundaryTests(unittest.TestCase):
    def test_recommendation_without_effect_does_not_enforce(self):
        result = evaluate_defender(True)
        self.assertEqual(result["posture"], "RECOMMENDATION_PRESENT")
        self.assertEqual(result["enforcement"], "NO_POLICY_ENFORCEMENT_CONFIGURED")

    def test_selected_deny_and_enforce_map_to_policy_paths(self):
        self.assertEqual(evaluate_defender(True, "deny")["enforcement"], "REQUEST_ENFORCEMENT_VIA_AZURE_POLICY_DENY")
        self.assertEqual(evaluate_defender(True, "enforce")["enforcement"], "REMEDIATION_PATH_VIA_AZURE_POLICY_DINE")

    def test_workload_plan_cost_is_separate(self):
        result = evaluate_defender(True, "none", workload_plan_enabled=True)
        self.assertEqual(result["enforcement"], "NO_POLICY_ENFORCEMENT_CONFIGURED")
        self.assertEqual(result["workload_plan"], "PLAN_COST_REQUIRES_CURRENT_PRICE_REVIEW")

    def test_unknown_action_is_rejected(self):
        with self.assertRaises(ValueError):
            evaluate_defender(True, "block-everything")


class FixtureTests(unittest.TestCase):
    def test_fixture_has_all_three_evidence_domains(self):
        results = run_fixture()
        names = {result["name"] for result in results}
        self.assertIn("audit-allows-matching-create", names)
        self.assertIn("pre-operation-authz-rejection", names)
        self.assertIn("defender-recommendation-only", names)
        self.assertEqual(len(results), 14)


if __name__ == "__main__":
    unittest.main()
