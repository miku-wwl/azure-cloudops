import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import app_release_model as model


class WarmupTests(unittest.TestCase):
    def test_default_accepts_any_http_status(self):
        self.assertTrue(model.warmup_accepted(503))
        self.assertTrue(model.warmup_accepted(302))

    def test_filter_can_reject_unwanted_status(self):
        self.assertFalse(model.warmup_accepted(503, [200, 202]))
        self.assertTrue(model.warmup_accepted(202, [200, 202]))

    def test_no_response_is_not_warm(self):
        self.assertFalse(model.warmup_accepted(None))


class SlotSwapTests(unittest.TestCase):
    def setUp(self):
        self.production = {"release": "release-a", "identity": "prod-slot"}
        self.staging = {"release": "release-b", "identity": "stage-slot"}

    def test_route_changes_but_identities_stay_with_slots(self):
        result = model.swap_slots(self.production, self.staging, 200)
        self.assertTrue(result["completed"])
        self.assertEqual(("release-b", "release-a"), (result["production"], result["staging"]))
        self.assertEqual(("prod-slot", "stage-slot"),
                         (result["production_identity"], result["staging_identity"]))

    def test_status_filter_blocks_swap(self):
        result = model.swap_slots(self.production, self.staging, 503, [200])
        self.assertFalse(result["completed"])
        self.assertEqual("release-a", result["production"])

    def test_restart_failure_blocks_swap(self):
        self.assertFalse(model.swap_slots(self.production, self.staging, 200, restart_ok=False)["completed"])


class ContainerAppScopeTests(unittest.TestCase):
    def test_template_changes_create_revision(self):
        for change in ("image", "container", "probe", "scale"):
            with self.subTest(change=change):
                impact = model.classify_changes([change])
                self.assertTrue(impact["revision_created"])
                self.assertFalse(impact["app_scope_changed"])

    def test_app_configuration_does_not_create_revision(self):
        for change in ("secret", "ingress", "traffic", "revision_mode", "identity", "registry", "dapr"):
            with self.subTest(change=change):
                impact = model.classify_changes([change])
                self.assertFalse(impact["revision_created"])
                self.assertTrue(impact["app_scope_changed"])

    def test_secret_scope_requires_restart_or_redeploy(self):
        impact = model.classify_changes(["secret"])
        self.assertTrue(impact["secret_restart_required"])

    def test_identity_change_does_not_request_automatic_restart(self):
        impact = model.classify_changes(["identity"])
        self.assertFalse(impact["revision_created"])
        self.assertFalse(impact["identity_restart_automatic"])

    def test_unknown_change_is_rejected(self):
        with self.assertRaises(ValueError):
            model.classify_changes(["unknown"])


class TrafficTests(unittest.TestCase):
    def test_single_mode_keeps_old_revision_until_candidate_ready(self):
        result = model.plan_cutover("single", "release-a", "release-b", False)
        self.assertEqual({"release-a": 100}, result["traffic"])
        ready = model.plan_cutover("single", "release-a", "release-b", True)
        self.assertEqual({"release-b": 100}, ready["traffic"])

    def test_multiple_mode_accepts_ready_candidate_weight(self):
        result = model.plan_cutover("multiple", "release-a", "release-b", True,
                                    {"release-a": 90, "release-b": 10})
        self.assertTrue(result["allowed"])
        self.assertEqual(100, sum(result["traffic"].values()))

    def test_local_release_gate_blocks_unready_candidate_weight(self):
        result = model.plan_cutover("multiple", "release-a", "release-b", False,
                                    {"release-a": 90, "release-b": 10})
        self.assertFalse(result["allowed"])
        self.assertEqual({"release-a": 90, "release-b": 10}, result["traffic"])

    def test_bad_multiple_weights_are_rejected(self):
        with self.assertRaises(ValueError):
            model.plan_cutover("multiple", "release-a", "release-b", True,
                               {"release-a": 80, "release-b": 10})

    def test_route_rollback_requires_active_previous_revision(self):
        result = model.rollback_route("release-a", "release-b", True)
        self.assertEqual({"release-a": 100, "release-b": 0}, result["traffic"])
        self.assertFalse(model.rollback_route("release-a", "release-b", False)["allowed"])


if __name__ == "__main__":
    unittest.main()