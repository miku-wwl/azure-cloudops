import unittest
from pathlib import Path

from reliability_model import (
    ModelError,
    ReliabilityModel,
    error_budget_minutes,
    parallel_availability,
    series_availability,
)


SCENARIO = Path(__file__).parent / "scenarios" / "settlement.json"


class ReliabilityModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model = ReliabilityModel.from_file(SCENARIO)

    def test_availability_set_survives_one_vm_fault_domain(self):
        self.assertTrue(self.model.evaluate("availability_set", "vm-fd1-failure"))

    def test_availability_set_does_not_claim_datacenter_resilience(self):
        self.assertFalse(self.model.evaluate("availability_set", "shared-datacenter"))

    def test_availability_set_zone_behavior_is_not_inferred(self):
        self.assertIsNone(self.model.evaluate("availability_set", "zone-1-outage"))

    def test_more_api_zones_do_not_repair_single_zone_ledger(self):
        self.assertFalse(
            self.model.evaluate("multi_zone_api_single_zone_ledger", "zone-1-outage")
        )

    def test_zone_redundant_critical_path_survives_one_zone(self):
        self.assertTrue(self.model.evaluate("zone_redundant_path", "zone-1-outage"))

    def test_shared_identity_dependency_can_break_zone_redundant_path(self):
        self.assertFalse(
            self.model.evaluate("zone_redundant_path", "identity-provider-outage")
        )

    def test_single_region_design_does_not_survive_region_outage(self):
        self.assertFalse(self.model.evaluate("zone_redundant_path", "region-outage"))

    def test_serial_availability_multiplies_independent_components(self):
        result = series_availability((0.9999, 0.9995, 0.9995, 0.9999))
        self.assertAlmostEqual(result, 0.99880046, places=8)

    def test_parallel_availability_uses_independence_assumption(self):
        self.assertAlmostEqual(parallel_availability((0.999, 0.999)), 0.999999)

    def test_time_based_error_budget_for_30_days(self):
        self.assertAlmostEqual(error_budget_minutes(0.9995, 30 * 24 * 60), 21.6)

    def test_fixture_expected_matrix_is_consistent(self):
        for fault in self.model.faults:
            for topology_id, expected in fault.expected.items():
                with self.subTest(fault=fault.id, topology=topology_id):
                    self.assertEqual(self.model.evaluate(topology_id, fault.id), expected)

    def test_rejects_invalid_probability_and_window(self):
        with self.assertRaises(ModelError):
            series_availability((1.01,))
        with self.assertRaises(ModelError):
            parallel_availability(())
        with self.assertRaises(ModelError):
            error_budget_minutes(1.1, 100)
        with self.assertRaises(ModelError):
            error_budget_minutes(0.99, 0)


if __name__ == "__main__":
    unittest.main()
