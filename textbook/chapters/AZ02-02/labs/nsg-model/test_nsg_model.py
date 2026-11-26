import copy
import json
import unittest
from pathlib import Path

from nsg_model import ModelError, NsgModel, StatefulFlowTable


SCENARIO = Path(__file__).parent / "scenarios" / "banking-payment.json"


def load_document():
    return json.loads(SCENARIO.read_text(encoding="utf-8"))


class NsgModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model = NsgModel.from_file(SCENARIO)

    def test_effective_policy_includes_subnet_and_nic_nsgs(self):
        self.assertEqual(self.model.attached_nsgs("pay-api-01"), ("nsg-payments-subnet", "nsg-pay-api-nic"))

    def test_subnet_allow_does_not_override_nic_deny(self):
        flow = self.model.make_flow(self.model.flows[0])
        verdict, results = self.model.evaluate(flow)
        self.assertEqual(results[0][1:], ("ALLOW", "Allow-Edge-To-Api"))
        self.assertEqual(results[1][1:], ("DENY", "Deny-Maintenance-Api-Port"))
        self.assertEqual(verdict, "DENY")

    def test_lower_numeric_priority_matches_before_higher_priority(self):
        nsg = "nsg-pay-api-nic"
        flow = self.model.make_flow(self.model.flows[0])
        result = self.model.evaluate_nsg(nsg, flow)
        self.assertEqual(result, ("DENY", "Deny-Maintenance-Api-Port"))

    def test_first_match_stops_before_later_allow(self):
        rules = self.model.nsgs["nsg-pay-api-nic"]
        flow = self.model.make_flow(self.model.flows[0])
        matched = next(rule for rule in rules if rule.matches(flow))
        self.assertEqual((matched.priority, matched.action), (100, "Deny"))

    def test_asg_member_matches_role_rule(self):
        flow = self.model.make_flow(self.model.flows[0])
        result = self.model.evaluate_nsg("nsg-payments-subnet", flow)
        self.assertEqual(result, ("ALLOW", "Allow-Edge-To-Api"))

    def test_nonmember_is_denied_by_explicit_fallback_rule(self):
        row = copy.deepcopy(self.model.flows[0])
        row["remote"] = {"nic_id": "legacy-client-01", "ip": "10.40.1.99", "port": 53145}
        flow = self.model.make_flow(row)
        result = self.model.evaluate_nsg("nsg-payments-subnet", flow)
        self.assertEqual(result, ("DENY", "Deny-Other-To-Api"))

    def test_port_range_and_protocol_are_part_of_match(self):
        document = load_document()
        rule = document["nsgs"]["nsg-payments-subnet"]["rules"][0]
        rule["destination_port"] = "8400-8450"
        model = NsgModel(document)
        flow = model.make_flow(document["flows"][0])
        result = model.evaluate_nsg("nsg-payments-subnet", flow)
        self.assertEqual(result, ("ALLOW", "Allow-Edge-To-Api"))
        rule["protocol"] = "UDP"
        model = NsgModel(document)
        flow = model.make_flow(document["flows"][0])
        result = model.evaluate_nsg("nsg-payments-subnet", flow)
        self.assertEqual(result, ("DENY", "Deny-Other-To-Api"))
        self.assertEqual(flow.protocol, "TCP")

    def test_allowed_outbound_flow_creates_reverse_state(self):
        state = StatefulFlowTable()
        outflow = self.model.make_flow(self.model.flows[1])
        self.assertEqual(self.model.evaluate(outflow, state)[0], "ALLOW")
        reply = self.model.make_flow(self.model.flows[2])
        self.assertEqual(self.model.evaluate(reply, state)[0], "ALLOW_ESTABLISHED_FLOW")

    def test_established_reply_survives_policy_change_but_new_tuple_does_not(self):
        model = NsgModel.from_file(SCENARIO)
        state = StatefulFlowTable()
        outflow = model.make_flow(model.flows[1])
        self.assertEqual(model.evaluate(outflow, state)[0], "ALLOW")
        for nsg_id in ("nsg-payments-subnet", "nsg-pay-api-nic"):
            model.nsgs[nsg_id] = [rule for rule in model.nsgs[nsg_id] if rule.name != "Allow-Api-To-Ledger"]
        reply = model.make_flow(model.flows[2])
        self.assertEqual(model.evaluate(reply, state)[0], "ALLOW_ESTABLISHED_FLOW")
        new_row = copy.deepcopy(model.flows[1])
        new_row["local_port"] = 51001
        new_flow = model.make_flow(new_row)
        self.assertEqual(model.evaluate(new_flow, state)[0], "DENY")

    def test_unknown_rule_match_is_not_assumed_to_follow_azure_defaults(self):
        document = load_document()
        document["nsgs"]["nsg-pay-api-nic"]["rules"] = []
        model = NsgModel(document)
        flow = model.make_flow(document["flows"][0])
        self.assertEqual(model.evaluate_nsg("nsg-pay-api-nic", flow), ("NO_CUSTOM_MATCH", None))

    def test_rejects_duplicate_priorities_in_one_nsg_and_direction(self):
        document = load_document()
        rule = copy.deepcopy(document["nsgs"]["nsg-pay-api-nic"]["rules"][0])
        rule["name"] = "duplicate-priority"
        document["nsgs"]["nsg-pay-api-nic"]["rules"].append(rule)
        with self.assertRaises(ModelError):
            NsgModel(document)

    def test_custom_priority_range_is_validated(self):
        document = load_document()
        document["nsgs"]["nsg-pay-api-nic"]["rules"][0]["priority"] = 99
        with self.assertRaises(ModelError):
            NsgModel(document)

    def test_ip_flow_verify_model_rejects_icmp_probe(self):
        document = load_document()
        document["flows"][0]["protocol"] = "ICMP"
        with self.assertRaises(ModelError):
            NsgModel.from_file(SCENARIO).make_flow(document["flows"][0])


if __name__ == "__main__":
    unittest.main()
