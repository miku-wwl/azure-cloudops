import unittest

from vm_operations_model import (
    boot_diagnostics_evidence,
    disk_io_ceiling,
    evaluate_rollout,
    guest_evidence,
    interpret_vm_state,
    run_fixture,
)


class VmStateTests(unittest.TestCase):
    def test_stopped_allocated_is_compute_billed(self):
        self.assertTrue(interpret_vm_state("stopped_allocated", "succeeded")["compute_billed"])

    def test_stopped_deallocated_has_no_compute_charge_but_resources_may_remain(self):
        result = interpret_vm_state("stopped_deallocated", "succeeded")
        self.assertFalse(result["compute_billed"])
        self.assertEqual(result["attached_resource_cost"], "ATTACHED_DISK_NETWORK_COST_MAY_CONTINUE")

    def test_running_and_failed_provisioning_are_independent_signals(self):
        result = interpret_vm_state("running", "failed")
        self.assertTrue(result["compute_billed"])
        self.assertEqual(result["operation_interpretation"], "LAST_CONTROL_PLANE_OPERATION_FAILED")
        self.assertEqual(result["application_health"], "NOT_INFERRED_FROM_CONTROL_PLANE_STATE")

    def test_invalid_state_is_rejected(self):
        with self.assertRaises(ValueError):
            interpret_vm_state("healthy", "succeeded")

    def test_guest_collection_requires_agent_and_rule(self):
        self.assertFalse(guest_evidence(False, True)["guest_metrics_collected"])
        self.assertFalse(guest_evidence(True, False)["guest_metrics_collected"])
        self.assertTrue(guest_evidence(True, True, "healthy")["guest_metrics_collected"])


class VmssRolloutTests(unittest.TestCase):
    def test_manual_leaves_existing_instance_on_previous_model(self):
        result = evaluate_rollout("uniform", "manual", 5, 4, "none")
        self.assertEqual(result["result"], "EXISTING_INSTANCE_REMAINS_ON_OLD_MODEL")

    def test_manual_instance_already_at_model(self):
        self.assertEqual(evaluate_rollout("uniform", "manual", 5, 5, "none")["result"], "INSTANCE_ALREADY_AT_MODEL")

    def test_automatic_policy_has_no_order_guarantee(self):
        self.assertEqual(evaluate_rollout("uniform", "automatic", 5, 4, "none")["result"], "AUTOMATIC_ORDER_NOT_GUARANTEED")

    def test_uniform_rolling_requires_probe_or_extension(self):
        self.assertEqual(evaluate_rollout("uniform", "rolling", 5, 4, "none")["result"], "ROLLING_HEALTH_GATE_CONFIGURATION_REQUIRED")
        self.assertEqual(evaluate_rollout("uniform", "rolling", 5, 4, "load_balancer_probe")["result"], "ROLLING_BATCHES_USE_HEALTH_SIGNAL")

    def test_flexible_rolling_model_marks_mode_support_recheck(self):
        result = evaluate_rollout("flexible", "rolling", 5, 4, "application_health_extension")
        self.assertEqual(result["result"], "ROLLING_BATCHES_USE_HEALTH_SIGNAL")
        self.assertTrue(result["mode_support_recheck"])
        self.assertEqual(result["scope"], "CONCEPTUAL_FIXTURE_ONLY")


class DiskPerformanceTests(unittest.TestCase):
    def test_disk_cap_limits_iops(self):
        result = disk_io_ceiling(9000, 5000, 8000, 400, 600, 700)
        self.assertEqual(result["delivered_iops"], 5000)
        self.assertEqual(result["iops_limiter"], "DISK_CAP")

    def test_vm_cap_limits_throughput(self):
        result = disk_io_ceiling(7000, 12000, 9000, 600, 900, 500)
        self.assertEqual(result["delivered_iops"], 7000)
        self.assertEqual(result["delivered_mbps"], 500)
        self.assertEqual(result["throughput_limiter"], "VM_CAP")

    def test_disk_and_vm_equal_caps_report_tie(self):
        result = disk_io_ceiling(150, 100, 100, 20, 10, 10)
        self.assertEqual(result["iops_limiter"], "DISK_AND_VM_CAPS_TIE")
        self.assertEqual(result["throughput_limiter"], "DISK_AND_VM_CAPS_TIE")

    def test_cache_path_outside_fixture_is_rejected(self):
        with self.assertRaises(ValueError):
            disk_io_ceiling(100, 50, 80, 20, 10, 15, host_cache="read_only")

    def test_negative_input_is_rejected(self):
        with self.assertRaises(ValueError):
            disk_io_ceiling(-1, 100, 80, 20, 10, 15)


class BootEvidenceTests(unittest.TestCase):
    def test_boot_diagnostics_does_not_upgrade_unknown_app_state(self):
        result = boot_diagnostics_evidence(True, "unknown")
        self.assertTrue(result["boot_evidence_available"])
        self.assertEqual(result["application_health"], "unknown")
        self.assertEqual(result["conclusion"], "BOOT_EVIDENCE_DOES_NOT_PROVE_APP_HEALTH")

    def test_unknown_health_value_is_rejected(self):
        with self.assertRaises(ValueError):
            boot_diagnostics_evidence(False, "partial")


class FixtureTests(unittest.TestCase):
    def test_fixture_exercises_each_evidence_domain(self):
        rows = run_fixture()
        names = {row["name"] for row in rows}
        self.assertIn("running-last-operation-failed", names)
        self.assertIn("manual-instance-drift", names)
        self.assertIn("disk-cap-bottleneck", names)
        self.assertIn("boot-diagnostics-only", names)
        self.assertEqual(len(rows), 9)


if __name__ == "__main__":
    unittest.main()
