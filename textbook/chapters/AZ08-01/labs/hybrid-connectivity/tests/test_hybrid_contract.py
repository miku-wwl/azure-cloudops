import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))
from hybrid_contract import evaluate, longest_route, longest_suffix_rule


FIXTURE = Path(__file__).parents[1] / "topology.json"


def fixture():
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def failed_codes(topology):
    return {code for status, code, _ in evaluate(topology) if status == "FAIL"}


class RouteContracts(unittest.TestCase):
    def test_fixture_has_two_directional_routes_and_paired_transit(self):
        self.assertEqual(failed_codes(fixture()), set())

    def test_hub_gateway_transit_flag_is_required(self):
        data = fixture()
        data["network"]["gateway_transit"]["hub_allow_gateway_transit"] = False
        self.assertIn("NET-01", failed_codes(data))

    def test_spoke_remote_gateway_flag_is_required(self):
        data = fixture()
        data["network"]["gateway_transit"]["spoke_use_remote_gateway"] = False
        self.assertIn("NET-01", failed_codes(data))

    def test_remote_gateway_cannot_be_combined_with_spokes_own_gateway(self):
        data = fixture()
        data["network"]["gateway_transit"]["spoke_gateway_present"] = True
        self.assertIn("NET-01", failed_codes(data))

    def test_forwarded_traffic_is_checked_separately(self):
        data = fixture()
        data["network"]["gateway_transit"]["spoke_allow_forwarded_traffic"] = False
        self.assertIn("NET-02", failed_codes(data))

    def test_bgp_session_down_fails_even_if_static_fixture_routes_remain(self):
        data = fixture()
        data["network"]["routes"]["bgp_session_up"] = False
        self.assertIn("NET-03", failed_codes(data))
        self.assertIn("NET-05", failed_codes(data))
        self.assertIn("NET-06", failed_codes(data))

    def test_route_propagation_is_an_independent_gate(self):
        data = fixture()
        data["network"]["routes"]["spoke_route_propagation_enabled"] = False
        self.assertIn("NET-04", failed_codes(data))
        self.assertIn("NET-05", failed_codes(data))
        self.assertNotIn("NET-06", failed_codes(data))

    def test_spoke_without_a_route_fails_only_that_direction(self):
        data = fixture()
        data["network"]["routes"]["spoke_route_table"] = []
        self.assertIn("NET-05", failed_codes(data))
        self.assertNotIn("NET-06", failed_codes(data))

    def test_return_route_missing_exposes_one_way_reachability(self):
        data = fixture()
        data["network"]["routes"]["onprem_route_table"] = []
        self.assertIn("NET-06", failed_codes(data))
        self.assertNotIn("NET-05", failed_codes(data))

    def test_more_specific_route_wins(self):
        routes = [
            {"prefix": "172.22.0.0/16", "next_hop": "vpn", "source": "BGP"},
            {"prefix": "172.22.10.0/24", "next_hop": "er", "source": "BGP"},
        ]
        self.assertEqual(longest_route("172.22.10.27", routes)["next_hop"], "er")

    def test_equal_length_conflicting_routes_are_not_guessed(self):
        routes = [
            {"prefix": "172.22.10.0/24", "next_hop": "vpn"},
            {"prefix": "172.22.10.0/24", "next_hop": "er"},
        ]
        with self.assertRaisesRegex(ValueError, "ambiguous"):
            longest_route("172.22.10.27", routes)


class DnsContracts(unittest.TestCase):
    def test_inbound_forwarding_requires_both_dns_transports(self):
        data = fixture()
        data["dns"]["onprem_query"]["tcp53_allowed"] = False
        self.assertIn("DNS-02", failed_codes(data))

    def test_private_zone_must_be_linked_to_inbound_vnet(self):
        data = fixture()
        data["dns"]["resolver"]["private_zone_linked_to_inbound_vnet"] = False
        self.assertIn("DNS-03", failed_codes(data))

    def test_ruleset_link_is_required_for_azure_outbound_forwarding(self):
        data = fixture()
        data["dns"]["azure_query"]["ruleset_linked_vnets"] = []
        self.assertIn("DNS-04", failed_codes(data))

    def test_outbound_endpoint_must_be_associated_with_ruleset(self):
        data = fixture()
        data["dns"]["azure_query"]["outbound_endpoint_associated"] = False
        self.assertIn("DNS-04", failed_codes(data))

    def test_longest_dns_suffix_selects_the_most_specific_forwarder(self):
        data = fixture()
        rule = longest_suffix_rule(data["dns"]["onprem_query"]["name"],
                                   data["dns"]["onprem_query"]["conditional_forwarders"])
        self.assertEqual(rule["suffix"], "privatelink.database.windows.net")

    def test_dns_suffix_boundary_does_not_match_lookalike_name(self):
        rules = [{"suffix": "corp.example", "target": "10.1.0.53"}]
        self.assertIsNone(longest_suffix_rule("ledger.notcorp.example", rules))

    def test_equal_length_conflicting_dns_rules_are_not_guessed(self):
        rules = [
            {"suffix": "corp.example", "target_type": "onprem-dns", "target": "10.1.0.53"},
            {"suffix": "corp.example", "target_type": "onprem-dns", "target": "10.1.0.54"},
        ]
        with self.assertRaisesRegex(ValueError, "ambiguous"):
            longest_suffix_rule("ledger.corp.example", rules)

    def test_ruleset_to_own_inbound_endpoint_is_flagged(self):
        data = fixture()
        data["dns"]["azure_query"]["ruleset_linked_vnets"].append("hub")
        data["dns"]["azure_query"]["rules"].append({
            "suffix": "privatelink.database.windows.net", "target": "10.40.5.4",
            "target_type": "resolver-inbound", "reachable": True,
            "udp53_allowed": True, "tcp53_allowed": True,
        })
        self.assertIn("DNS-05", failed_codes(data))

    def test_unlinked_hub_loop_rule_is_not_claimed_as_a_loop_for_this_model(self):
        data = fixture()
        data["dns"]["azure_query"]["rules"] = [{
            "suffix": "privatelink.database.windows.net", "target": "10.40.5.4",
            "target_type": "resolver-inbound", "reachable": True,
            "udp53_allowed": True, "tcp53_allowed": True,
        }]
        self.assertNotIn("DNS-05", failed_codes(data))

    def test_unreachable_or_blocked_onprem_dns_target_fails(self):
        data = fixture()
        data["dns"]["azure_query"]["rules"][-1]["tcp53_allowed"] = False
        self.assertIn("DNS-07", failed_codes(data))

    def test_dns_failure_does_not_change_ip_route_contracts(self):
        data = fixture()
        data["dns"]["azure_query"]["ruleset_linked_vnets"] = []
        codes = failed_codes(data)
        self.assertTrue({"NET-05", "NET-06"}.isdisjoint(codes))


if __name__ == "__main__":
    unittest.main()
