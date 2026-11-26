import copy
import json
import unittest
from pathlib import Path

from route_model import ModelError, RouteModel, UnsupportedRoutingSemantics


SCENARIO = Path(__file__).parent / "scenarios" / "banking-hub-spoke.json"


def load_document():
    return json.loads(SCENARIO.read_text(encoding="utf-8"))


class RouteModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model = RouteModel.from_file(SCENARIO)

    def test_longest_prefix_beats_broader_udr(self):
        route = self.model.select("payments", "172.20.40.15").route
        self.assertEqual((str(route.prefix), route.name), ("172.20.40.0/24", "partner-segment"))

    def test_equal_prefix_udr_beats_bgp_for_partner_route(self):
        document = load_document()
        document["subnets"]["payments"]["bgp_routes"].append(
            {"name": "partner-bgp", "prefix": "172.20.40.0/24", "source": "bgp", "next_hop_type": "VirtualNetworkGateway"}
        )
        route = RouteModel(document).select("payments", "172.20.40.15").route
        self.assertEqual((str(route.prefix), route.source, route.next_hop_ip), ("172.20.40.0/24", "udr", "10.20.0.4"))

    def test_equal_prefix_udr_beats_bgp(self):
        route = self.model.select("payments", "172.20.1.2").route
        self.assertEqual((route.source, route.next_hop_type), ("udr", "VirtualAppliance"))

    def test_default_udr_beats_equal_prefix_system_default(self):
        route = self.model.select("payments", "203.0.113.10").route
        self.assertEqual((str(route.prefix), route.source, route.next_hop_ip), ("0.0.0.0/0", "udr", "10.20.0.4"))

    def test_effective_routes_combine_system_bgp_and_associated_udr(self):
        rows = self.model.effective_routes("payments")
        self.assertEqual({route.source for route in rows}, {"system", "bgp", "udr"})

    def test_one_route_table_can_be_reused_by_multiple_subnets(self):
        for subnet in ("payments", "settlement"):
            self.assertEqual(self.model.select(subnet, "172.20.40.15").route.next_hop_ip, "10.20.0.4")

    def test_asymmetric_path_is_flagged_when_return_uses_another_firewall(self):
        forward, reverse, verdict = self.model.evaluate_flow(self.model.flows[0])
        self.assertEqual(forward.route.next_hop_ip, "10.20.0.4")
        self.assertEqual(reverse.route.next_hop_ip, "10.20.0.8")
        self.assertEqual(verdict, "ASYMMETRIC_AT_STATEFUL_INSPECTOR")

    def test_same_inspector_in_both_modeled_directions_is_symmetric(self):
        _, _, verdict = self.model.evaluate_flow(self.model.flows[1])
        self.assertEqual(verdict, "SYMMETRIC_THROUGH_INSPECTOR")

    def test_none_next_hop_models_a_blackhole(self):
        document = load_document()
        document["route_tables"]["rt-payments"]["routes"].append(
            {"name": "blocked-test-range", "prefix": "198.51.100.0/24", "source": "udr", "next_hop_type": "None"}
        )
        route = RouteModel(document).select("payments", "198.51.100.7").route
        self.assertEqual(route.next_hop_type, "None")

    def test_special_system_route_semantics_are_refused_not_guessed(self):
        document = load_document()
        document["subnets"]["payments"]["system_routes"].append(
            {"name": "service-endpoint", "prefix": "198.51.100.0/24", "source": "system", "next_hop_type": "VirtualNetworkServiceEndpoint", "kind": "service_endpoint"}
        )
        with self.assertRaises(UnsupportedRoutingSemantics):
            RouteModel(document).select("payments", "198.51.100.7")

    def test_virtual_appliance_route_requires_valid_ip(self):
        document = load_document()
        bad = copy.deepcopy(document["route_tables"]["rt-payments"]["routes"][0])
        bad["next_hop_ip"] = None
        document["route_tables"]["rt-payments"]["routes"].append(bad)
        with self.assertRaises(ModelError):
            RouteModel(document)

    def test_duplicate_prefixes_in_one_route_table_are_rejected(self):
        document = load_document()
        duplicate = copy.deepcopy(document["route_tables"]["rt-payments"]["routes"][0])
        duplicate["name"] = "duplicate"
        document["route_tables"]["rt-payments"]["routes"].append(duplicate)
        with self.assertRaises(ModelError):
            RouteModel(document)

    def test_unknown_route_table_association_is_rejected(self):
        document = load_document()
        document["subnets"]["payments"]["route_table_id"] = "missing"
        with self.assertRaises(ModelError):
            RouteModel(document)


if __name__ == "__main__":
    unittest.main()
