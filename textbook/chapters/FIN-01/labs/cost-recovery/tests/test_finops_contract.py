import copy
import json
import sys
import unittest
from decimal import Decimal
from pathlib import Path

LAB = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LAB))

import finops_contract as fc


FIXTURE = LAB / "synthetic-ledger.json"


def load_fixture():
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


class FinOpsContractTests(unittest.TestCase):
    def test_actual_gross_credits_and_net_are_separate(self):
        report = fc.summarize(load_fixture())
        self.assertEqual(report["gross_charges"], Decimal("180.50"))
        self.assertEqual(report["credits"], Decimal("12.00"))
        self.assertEqual(report["net_cost"], Decimal("168.50"))

    def test_amortized_view_splits_commitment_used_and_unused(self):
        report = fc.summarize(load_fixture(), "amortized")
        self.assertEqual(report["gross_charges"], Decimal("180.50"))
        self.assertEqual(report["view"], "amortized")

    def test_views_are_never_summed_together(self):
        data = load_fixture()
        actual = fc.summarize(data, "actual")
        amortized = fc.summarize(data, "amortized")
        self.assertEqual(actual["gross_charges"], Decimal("180.50"))
        self.assertEqual(amortized["gross_charges"], Decimal("180.50"))
        self.assertNotEqual(actual["gross_charges"] + amortized["gross_charges"], actual["gross_charges"])

    def test_direct_tag_takes_precedence(self):
        data = load_fixture()
        row = next(r for r in data["cost_records"] if r["id"] == "vm-dev" and r["view"] == "actual")
        row["tags"]["costCenter"] = "Payments"
        report = fc.summarize(data)
        self.assertEqual(report["by_cost_center"]["Payments"], Decimal("149.00"))
        self.assertNotIn("Engineering", report["by_cost_center"])

    def test_explicit_tag_inheritance_can_resolve_owner(self):
        report = fc.summarize(load_fixture())
        self.assertEqual(report["by_cost_center"]["Engineering"], Decimal("48.00"))

    def test_disabled_inheritance_leaves_record_unallocated(self):
        data = load_fixture()
        row = next(r for r in data["cost_records"] if r["id"] == "vm-dev" and r["view"] == "actual")
        row["tag_inheritance_enabled"] = False
        report = fc.summarize(data)
        self.assertEqual(report["unallocated_gross"], Decimal("57.50"))

    def test_unknown_meter_is_not_dropped(self):
        report = fc.summarize(load_fixture())
        self.assertEqual(report["unallocated_gross"], Decimal("9.50"))

    def test_unallocated_commitment_remains_visible(self):
        report = fc.summarize(load_fixture(), "amortized")
        self.assertEqual(report["unallocated_gross"], Decimal("10.90"))

    def test_allocation_reconciles_to_gross(self):
        report = fc.summarize(load_fixture())
        self.assertEqual(report["allocated_gross"] + report["unallocated_gross"], report["gross_charges"])

    def test_shared_pool_is_split_by_explicit_weights(self):
        report = fc.summarize(load_fixture())
        self.assertEqual(report["shared_by_cost_center"]["Payments"], Decimal("21.00"))
        self.assertEqual(report["shared_by_cost_center"]["Analytics"], Decimal("9.00"))

    def test_shared_weights_must_total_one_hundred(self):
        data = load_fixture()
        row = next(r for r in data["cost_records"] if r["id"] == "network-shared" and r["view"] == "actual")
        row["shared_weights"]["Analytics"] = "25.00"
        with self.assertRaisesRegex(fc.ContractError, "total 100"):
            fc.summarize(data)

    def test_negative_shared_weight_is_rejected(self):
        data = load_fixture()
        row = next(r for r in data["cost_records"] if r["id"] == "network-shared" and r["view"] == "actual")
        row["shared_weights"]["Payments"] = "120.00"
        row["shared_weights"]["Analytics"] = "-20.00"
        with self.assertRaisesRegex(fc.ContractError, "nonnegative"):
            fc.summarize(data)

    def test_budget_threshold_marks_actual_and_forecast(self):
        result = fc.budget_status(load_fixture())
        self.assertTrue(result["threshold_crossed_by_actual"])
        self.assertTrue(result["threshold_crossed_by_forecast"])

    def test_budget_is_alert_only_and_never_stops_usage(self):
        result = fc.budget_status(load_fixture())
        self.assertEqual(result["control"], "alert_only")
        self.assertFalse(result["consumption_stopped"])

    def test_forecast_can_cross_before_actual(self):
        data = load_fixture()
        data["budget"]["actual_cost"] = "100.00"
        result = fc.budget_status(data)
        self.assertFalse(result["threshold_crossed_by_actual"])
        self.assertTrue(result["threshold_crossed_by_forecast"])

    def test_commitment_utilization_is_per_hour(self):
        result = fc.commitment_utilization(load_fixture())[0]
        self.assertEqual(result["committed"], Decimal("4.00"))
        self.assertEqual(result["covered"], Decimal("2.60"))
        self.assertEqual(result["unused_expired"], Decimal("1.40"))
        self.assertEqual(result["utilization_percent"], Decimal("65.00"))

    def test_unused_commitment_does_not_roll_over(self):
        result = fc.commitment_utilization(load_fixture())[0]
        self.assertFalse(result["unused_rolls_over"])

    def test_stopped_vm_may_still_bill_compute(self):
        result = fc.recovery_decisions(load_fixture())
        stopped = next(r for r in result if r["id"] == "vm-dev")
        self.assertTrue(stopped["compute_billed"])
        self.assertEqual(stopped["decision"], "review_owner_before_deallocate")

    def test_deallocated_vm_has_no_compute_charge_but_keeps_residuals(self):
        result = fc.recovery_decisions(load_fixture())
        stopped = next(r for r in result if r["id"] == "vm-stage")
        self.assertFalse(stopped["compute_billed"])
        self.assertEqual(stopped["decision"], "inspect_persistent_resources")
        self.assertIn("os-disk-stage", stopped["residual_resources"])

    def test_retention_required_item_is_preserved(self):
        result = fc.recovery_decisions(load_fixture())
        deleted = next(r for r in result if r["id"] == "vm-deleted")
        self.assertEqual(deleted["decision"], "retain_required_resources")

    def test_unapproved_detached_resource_requires_owner_review(self):
        data = load_fixture()
        item = next(r for r in data["resource_candidates"] if r["id"] == "disk-expired")
        item["owner_approved"] = False
        decision = next(r for r in fc.recovery_decisions(data) if r["id"] == "disk-expired")
        self.assertEqual(decision["decision"], "owner_review_required")

    def test_owner_approval_only_makes_cleanup_eligible(self):
        decision = next(r for r in fc.recovery_decisions(load_fixture()) if r["id"] == "disk-expired")
        self.assertEqual(decision["decision"], "eligible_for_approved_cleanup")
        self.assertFalse(decision["execution_performed"])

    def test_unknown_power_state_fails_to_investigation(self):
        data = load_fixture()
        data["resource_candidates"][0]["power_state"] = "Unknown"
        decision = fc.recovery_decisions(data)[0]
        self.assertEqual(decision["decision"], "investigate_unknown_state")
        self.assertIsNone(decision["compute_billed"])

    def test_selected_view_must_be_valid(self):
        data = load_fixture()
        data["selected_view"] = "both"
        with self.assertRaisesRegex(fc.ContractError, "selected_view"):
            fc.validate(data)

    def test_negative_noncredit_amount_is_rejected(self):
        data = load_fixture()
        row = next(r for r in data["cost_records"] if r["id"] == "vm-prod" and r["view"] == "actual")
        row["amount"] = "-1.00"
        with self.assertRaisesRegex(fc.ContractError, "negative charge"):
            fc.summarize(data)

    def test_duplicate_id_in_same_view_is_rejected(self):
        data = load_fixture()
        duplicate = copy.deepcopy(next(r for r in data["cost_records"] if r["id"] == "vm-prod" and r["view"] == "actual"))
        data["cost_records"].append(duplicate)
        with self.assertRaisesRegex(fc.ContractError, "duplicate"):
            fc.validate(data)

    def test_mixed_currency_fixture_is_rejected(self):
        data = load_fixture()
        data["cost_records"][0]["currency"] = "NZD"
        with self.assertRaisesRegex(fc.ContractError, "one explicit currency"):
            fc.validate(data)


if __name__ == "__main__":
    unittest.main()
