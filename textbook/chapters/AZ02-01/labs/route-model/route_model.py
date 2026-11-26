#!/usr/bin/env python3
"""Narrow, deterministic Azure route-selection teaching model; no Azure APIs."""

from __future__ import annotations

import argparse
import ipaddress
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


class ModelError(ValueError):
    """Invalid fixture or routing input."""


class UnsupportedRoutingSemantics(ModelError):
    """The input uses Azure routing behavior intentionally outside this model."""


SOURCE_RANK = {"system": 0, "bgp": 1, "udr": 2}
SPECIAL_KINDS = {"virtual_network", "virtual_network_peering", "service_endpoint"}


@dataclass(frozen=True)
class Route:
    name: str
    prefix: ipaddress.IPv4Network
    source: str
    next_hop_type: str
    next_hop_ip: str | None = None
    kind: str = "ordinary"

    @classmethod
    def from_dict(cls, row: dict[str, Any]) -> "Route":
        try:
            prefix = ipaddress.ip_network(row["prefix"], strict=True)
        except (KeyError, ValueError, TypeError) as exc:
            raise ModelError(f"invalid route prefix: {row.get('prefix')!r}") from exc
        if not isinstance(prefix, ipaddress.IPv4Network):
            raise ModelError("this teaching model supports IPv4 routes only")
        source = row.get("source")
        if source not in SOURCE_RANK:
            raise ModelError(f"unsupported route source: {source!r}")
        next_hop_type = row.get("next_hop_type")
        if not isinstance(next_hop_type, str) or not next_hop_type:
            raise ModelError("route next_hop_type is required")
        next_hop_ip = row.get("next_hop_ip")
        if next_hop_type == "VirtualAppliance":
            try:
                address = ipaddress.ip_address(next_hop_ip)
            except (ValueError, TypeError) as exc:
                raise ModelError("VirtualAppliance routes require a valid next_hop_ip") from exc
            if not isinstance(address, ipaddress.IPv4Address):
                raise ModelError("this teaching model supports IPv4 appliance addresses only")
            next_hop_ip = str(address)
        kind = row.get("kind", "ordinary")
        if kind not in {"ordinary", *SPECIAL_KINDS}:
            raise ModelError(f"unsupported route kind: {kind!r}")
        return cls(str(row.get("name", row["prefix"])), prefix, source, next_hop_type, next_hop_ip, kind)

    def display(self) -> str:
        hop = self.next_hop_type
        if self.next_hop_ip:
            hop += f"({self.next_hop_ip})"
        return f"{self.prefix} [{self.source}] -> {hop}"


@dataclass(frozen=True)
class Selection:
    subnet_id: str
    destination: ipaddress.IPv4Address
    route: Route


class RouteModel:
    """Resolve a fixture's subnet-effective routes using documented ordinary-route rules."""

    def __init__(self, document: dict[str, Any]):
        self.subnets = document.get("subnets", {})
        self.route_tables = document.get("route_tables", {})
        self.flows = document.get("flows", [])
        if not self.subnets or not isinstance(self.subnets, dict):
            raise ModelError("fixture requires at least one subnet")
        if not isinstance(self.route_tables, dict):
            raise ModelError("route_tables must be an object")

        self._system: dict[str, tuple[Route, ...]] = {}
        self._bgp: dict[str, tuple[Route, ...]] = {}
        for subnet_id, subnet in self.subnets.items():
            table_id = subnet.get("route_table_id")
            if table_id is not None and table_id not in self.route_tables:
                raise ModelError(f"subnet {subnet_id!r} references unknown route table {table_id!r}")
            self._system[subnet_id] = self._read_routes(subnet.get("system_routes", []), "system")
            self._bgp[subnet_id] = self._read_routes(subnet.get("bgp_routes", []), "bgp")

        for table_id, table in self.route_tables.items():
            associated = table.get("associated_subnets", [])
            unknown_subnets = set(associated) - set(self.subnets)
            if unknown_subnets:
                raise ModelError(f"route table {table_id!r} has unknown subnets: {sorted(unknown_subnets)}")
            for subnet_id in associated:
                if self.subnets[subnet_id].get("route_table_id") != table_id:
                    raise ModelError(f"subnet {subnet_id!r} and table {table_id!r} disagree on association")
            ud_routes = self._read_routes(table.get("routes", []), "udr")
            prefixes = [route.prefix for route in ud_routes]
            if len(prefixes) != len(set(prefixes)):
                raise ModelError(f"route table {table_id!r} repeats a route prefix")
            self.route_tables[table_id] = {**table, "_routes": ud_routes}

    @staticmethod
    def _read_routes(rows: list[dict[str, Any]], expected_source: str) -> tuple[Route, ...]:
        if not isinstance(rows, list):
            raise ModelError(f"{expected_source} routes must be a list")
        routes = tuple(Route.from_dict(row) for row in rows)
        if any(route.source != expected_source for route in routes):
            raise ModelError(f"route source does not match its {expected_source} collection")
        return routes

    @classmethod
    def from_file(cls, path: Path) -> "RouteModel":
        try:
            document = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ModelError(f"cannot read scenario: {exc}") from exc
        return cls(document)

    def effective_routes(self, subnet_id: str) -> tuple[Route, ...]:
        if subnet_id not in self.subnets:
            raise ModelError(f"unknown subnet {subnet_id!r}")
        subnet = self.subnets[subnet_id]
        routes = list(self._system[subnet_id]) + list(self._bgp[subnet_id])
        table_id = subnet.get("route_table_id")
        if table_id is not None:
            table = self.route_tables[table_id]
            if subnet_id not in table.get("associated_subnets", []):
                raise ModelError(f"route table {table_id!r} does not declare subnet {subnet_id!r}")
            routes.extend(table["_routes"])
        return tuple(routes)

    def select(self, subnet_id: str, destination_ip: str) -> Selection:
        try:
            destination = ipaddress.ip_address(destination_ip)
        except ValueError as exc:
            raise ModelError(f"invalid destination IP {destination_ip!r}") from exc
        if not isinstance(destination, ipaddress.IPv4Address):
            raise ModelError("this teaching model supports IPv4 destinations only")
        routes = self.effective_routes(subnet_id)
        matching = [route for route in routes if destination in route.prefix]
        if not matching:
            raise ModelError(f"no matching route for {destination} from subnet {subnet_id!r}")
        if any(route.kind in SPECIAL_KINDS for route in matching):
            kinds = sorted({route.kind for route in matching if route.kind in SPECIAL_KINDS})
            raise UnsupportedRoutingSemantics(
                "special system-route preference/override rules are outside this model: "
                + ", ".join(kinds)
            )
        best_prefix = max(route.prefix.prefixlen for route in matching)
        longest = [route for route in matching if route.prefix.prefixlen == best_prefix]
        best_source_rank = max(SOURCE_RANK[route.source] for route in longest)
        winners = [route for route in longest if SOURCE_RANK[route.source] == best_source_rank]
        identities = {(r.next_hop_type, r.next_hop_ip, r.name) for r in winners}
        if len(identities) > 1:
            raise UnsupportedRoutingSemantics(
                f"multiple equal-best routes for {destination}; ECMP/route selection is outside this model"
            )
        return Selection(subnet_id, destination, winners[0])

    @staticmethod
    def uses_inspector(selection: Selection, inspector_ip: str) -> bool:
        try:
            expected = ipaddress.IPv4Address(inspector_ip)
        except ipaddress.AddressValueError as exc:
            raise ModelError(f"invalid inspector IP {inspector_ip!r}") from exc
        return (
            selection.route.next_hop_type == "VirtualAppliance"
            and selection.route.next_hop_ip == str(expected)
        )

    def evaluate_flow(self, flow: dict[str, Any]) -> tuple[Selection, Selection, str]:
        inspector_ip = flow.get("stateful_inspector_ip")
        if not inspector_ip:
            raise ModelError(f"flow {flow.get('id')!r} requires stateful_inspector_ip")
        forward = self.select(flow["forward_subnet"], flow["remote_ip"])
        reverse = self.select(flow["return_subnet"], flow["client_ip"])
        forward_seen = self.uses_inspector(forward, inspector_ip)
        reverse_seen = self.uses_inspector(reverse, inspector_ip)
        if forward_seen and reverse_seen:
            verdict = "SYMMETRIC_THROUGH_INSPECTOR"
        elif forward_seen != reverse_seen:
            verdict = "ASYMMETRIC_AT_STATEFUL_INSPECTOR"
        else:
            verdict = "BYPASSES_INSPECTOR_BOTH_DIRECTIONS"
        return forward, reverse, verdict

    def report(self) -> str:
        lines = ["Subnet route-selection teaching model (synthetic fixture; no Azure API call)"]
        for flow in self.flows:
            forward, reverse, verdict = self.evaluate_flow(flow)
            lines.extend(
                [
                    f"\n{flow['id']}: {flow.get('description', '')}",
                    f"  forward from {forward.subnet_id} to {forward.destination}: {forward.route.display()}",
                    f"  return from {reverse.subnet_id} to {reverse.destination}: {reverse.route.display()}",
                    f"  stateful-path result: {verdict}",
                ]
            )
        lines.append("\nNo result establishes NIC effective routes, end-to-end reachability, or Azure packet behavior.")
        return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--scenario",
        type=Path,
        default=Path(__file__).parent / "scenarios" / "banking-hub-spoke.json",
    )
    args = parser.parse_args()
    print(RouteModel.from_file(args.scenario).report())


if __name__ == "__main__":
    main()
