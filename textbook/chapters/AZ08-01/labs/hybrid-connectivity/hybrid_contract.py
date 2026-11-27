#!/usr/bin/env python3
"""Check a deliberately narrow, fictional hybrid routing/DNS contract.

This validates input relationships only. It is not an Azure configuration parser,
control-plane client, router, DNS server, or emulator.
"""
from __future__ import annotations

import argparse
import ipaddress
import json
from pathlib import Path
from typing import Any


def matching_suffix(name: str, suffix: str) -> bool:
    name, suffix = name.rstrip(".").lower(), suffix.strip(".").lower()
    return name == suffix or name.endswith("." + suffix)


def longest_suffix_rule(name: str, rules: list[dict[str, Any]]) -> dict[str, Any] | None:
    matches = [rule for rule in rules if matching_suffix(name, rule["suffix"])]
    if not matches:
        return None
    longest = max(len(rule["suffix"].strip(".")) for rule in matches)
    winners = [rule for rule in matches if len(rule["suffix"].strip(".")) == longest]
    targets = {(rule.get("target_type"), rule.get("target")) for rule in winners}
    if len(targets) != 1:
        raise ValueError(f"ambiguous equal-length DNS suffix rules for {name}")
    return winners[0]


def longest_route(destination: str, routes: list[dict[str, Any]]) -> dict[str, Any] | None:
    address = ipaddress.ip_address(destination)
    matches = [
        route for route in routes
        if address.version == ipaddress.ip_network(route["prefix"], strict=False).version
        and address in ipaddress.ip_network(route["prefix"], strict=False)
    ]
    if not matches:
        return None
    width = max(ipaddress.ip_network(route["prefix"], strict=False).prefixlen for route in matches)
    winners = [
        route for route in matches
        if ipaddress.ip_network(route["prefix"], strict=False).prefixlen == width
    ]
    next_hops = {route["next_hop"] for route in winners}
    if len(next_hops) != 1:
        raise ValueError(f"ambiguous equal-length routes to {destination}")
    return winners[0]


def evaluate(topology: dict[str, Any]) -> list[tuple[str, str, str]]:
    """Return (status, code, explanation) entries; status is PASS or FAIL."""
    findings: list[tuple[str, str, str]] = []

    def check(condition: bool, code: str, ok: str, bad: str) -> None:
        findings.append(("PASS" if condition else "FAIL", code, ok if condition else bad))

    network = topology["network"]
    transit = network["gateway_transit"]
    transit_ok = (
        transit["hub_gateway_present"]
        and transit["hub_allow_gateway_transit"]
        and transit["spoke_use_remote_gateway"]
        and not transit["spoke_gateway_present"]
    )
    check(transit_ok, "NET-01",
          "gateway transit is paired hub-to-spoke and the spoke has no own gateway",
          "gateway transit is incomplete or the spoke also owns a gateway")
    check(transit["hub_allow_forwarded_traffic"] and transit["spoke_allow_forwarded_traffic"],
          "NET-02", "forwarded traffic is allowed on both modeled peering directions",
          "forwarded traffic is not allowed on both modeled peering directions")

    routes = network["routes"]
    check(routes["bgp_session_up"], "NET-03", "the modeled BGP session is established",
          "the modeled BGP session is down; learned routes cannot be assumed")
    check(routes["spoke_route_propagation_enabled"], "NET-04",
          "gateway route propagation is enabled for the spoke",
          "gateway route propagation is disabled for the spoke")

    probe = routes["probe"]
    spoke_candidates = routes["spoke_route_table"]
    onprem_candidates = routes["onprem_route_table"]
    if not routes["bgp_session_up"]:
        spoke_candidates = [route for route in spoke_candidates if route.get("source") != "BGP"]
        onprem_candidates = [route for route in onprem_candidates if route.get("source") != "BGP"]
    if not routes["spoke_route_propagation_enabled"]:
        spoke_candidates = [route for route in spoke_candidates if route.get("source") != "BGP"]
    for code, dst, candidates, expected, ok_side, fail_side in (
        ("NET-05", probe["onprem_ip"], spoke_candidates,
         routes["expected_spoke_next_hop"], "spoke-to-branch", "spoke-to-branch"),
        ("NET-06", probe["spoke_ip"], onprem_candidates,
         routes["expected_onprem_next_hop"], "branch-to-spoke", "branch-to-spoke"),
    ):
        try:
            selected = longest_route(dst, candidates)
            route_ok = selected is not None and selected["next_hop"] == expected
            detail = (f"{ok_side} selects {selected['prefix']} via {selected['next_hop']}"
                      if route_ok else
                      f"{fail_side} has no expected route to {dst} (selected {selected})")
        except (KeyError, ValueError) as exc:
            route_ok, detail = False, f"{fail_side} route table is invalid: {exc}"
        check(route_ok, code, detail, detail)

    dns = topology["dns"]
    resolver = dns["resolver"]
    onprem = dns["onprem_query"]
    try:
        inbound_rule = longest_suffix_rule(onprem["name"], onprem["conditional_forwarders"])
        inbound_rule_ok = inbound_rule is not None and inbound_rule["target_type"] == "resolver-inbound"
    except (KeyError, ValueError) as exc:
        inbound_rule, inbound_rule_ok = None, False
        inbound_error = str(exc)
    else:
        inbound_error = "no conditional forwarder targets the inbound endpoint"
    check(inbound_rule_ok, "DNS-01",
          f"on-prem query selects the longest conditional suffix {inbound_rule['suffix']} to the inbound endpoint"
          if inbound_rule_ok else inbound_error,
          inbound_error)
    inbound_path_ok = onprem["resolver_reachable"] and onprem["udp53_allowed"] and onprem["tcp53_allowed"]
    check(inbound_path_ok, "DNS-02", "on-premises can reach the inbound endpoint on UDP/TCP 53",
          "the inbound endpoint path or UDP/TCP 53 allowance is incomplete")
    check(resolver["private_zone_linked_to_inbound_vnet"], "DNS-03",
          "the private zone is linked to the inbound endpoint VNet",
          "the inbound endpoint VNet is not linked to the private zone")

    azure = dns["azure_query"]
    ruleset_linked = azure["source_vnet"] in azure["ruleset_linked_vnets"]
    ruleset_ready = (azure["dns_mode"] == "azure-provided"
                     and azure["outbound_endpoint_associated"] and ruleset_linked)
    check(ruleset_ready, "DNS-04",
          "Azure-provided DNS evaluates a ruleset with an associated outbound endpoint linked to the source VNet",
          "Azure-provided DNS, outbound endpoint association, or source VNet ruleset link is missing")
    resolver_vnet = resolver["inbound_vnet"]
    loop = (resolver_vnet in azure["ruleset_linked_vnets"] and any(
        rule.get("target_type") == "resolver-inbound" for rule in azure["rules"]
    ))
    check(not loop, "DNS-05", "no linked ruleset sends queries back to its own hub inbound endpoint",
          "ruleset links to the inbound endpoint VNet and forwards to that inbound endpoint; loop risk")
    try:
        outbound_rule = longest_suffix_rule(azure["name"], azure["rules"])
        outbound_rule_ok = outbound_rule is not None and outbound_rule.get("target_type") == "onprem-dns"
    except (KeyError, ValueError) as exc:
        outbound_rule, outbound_rule_ok = None, False
        outbound_error = str(exc)
    else:
        outbound_error = "no matching rule forwards this name to on-premises DNS"
    check(outbound_rule_ok, "DNS-06",
          f"Azure query selects the longest suffix {outbound_rule['suffix']} to on-premises DNS"
          if outbound_rule_ok else outbound_error,
          outbound_error)
    target_path_ok = (outbound_rule_ok and outbound_rule.get("reachable", False)
                      and outbound_rule.get("udp53_allowed", False)
                      and outbound_rule.get("tcp53_allowed", False))
    check(target_path_ok, "DNS-07", "the selected on-prem DNS target is reachable on UDP/TCP 53",
          "the selected on-prem DNS target path or UDP/TCP 53 allowance is incomplete")
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("topology", nargs="?", type=Path, default=Path(__file__).with_name("topology.json"))
    args = parser.parse_args()
    try:
        topology = json.loads(args.topology.read_text(encoding="utf-8"))
        findings = evaluate(topology)
    except (OSError, json.JSONDecodeError, KeyError, ValueError) as exc:
        print(f"INPUT_ERROR: {exc}")
        return 2
    print("SYNTHETIC CONTRACT CHECK - not an Azure query or emulator")
    print(f"Fixture: {topology.get('label', 'unlabelled')}")
    for status, code, message in findings:
        print(f"{status:4} {code}: {message}")
    failed = sum(status == "FAIL" for status, _, _ in findings)
    print(f"Summary: {len(findings) - failed} passed; {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
