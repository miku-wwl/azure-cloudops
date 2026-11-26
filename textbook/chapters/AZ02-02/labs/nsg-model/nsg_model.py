#!/usr/bin/env python3
"""Narrow stateful NSG rule teaching model; no Azure APIs."""

from __future__ import annotations

import argparse
import ipaddress
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


class ModelError(ValueError):
    """Invalid fixture or unsupported filtering input."""


@dataclass(frozen=True)
class Endpoint:
    name: str
    ip: ipaddress.IPv4Address
    port: int
    asgs: frozenset[str]


@dataclass(frozen=True)
class Flow:
    id: str
    local_nic: str
    direction: str
    protocol: str
    local: Endpoint
    remote: Endpoint

    def key(self) -> tuple[Any, ...]:
        endpoints = tuple(sorted(((str(self.local.ip), self.local.port), (str(self.remote.ip), self.remote.port))))
        return self.protocol, endpoints


@dataclass(frozen=True)
class Matcher:
    kind: str
    value: str | None = None

    def matches(self, endpoint: Endpoint) -> bool:
        if self.kind == "Any":
            return True
        if self.kind == "ASG":
            return self.value in endpoint.asgs
        if self.kind == "CIDR":
            try:
                return endpoint.ip in ipaddress.ip_network(self.value, strict=False)
            except ValueError as exc:
                raise ModelError(f"invalid CIDR matcher {self.value!r}") from exc
        if self.kind == "IP":
            return endpoint.ip == ipaddress.ip_address(self.value)
        raise ModelError(f"unsupported matcher kind {self.kind!r}")


@dataclass(frozen=True)
class Rule:
    name: str
    priority: int
    direction: str
    protocol: str
    source: Matcher
    source_port: str
    destination: Matcher
    destination_port: str
    action: str

    @classmethod
    def from_dict(cls, row: dict[str, Any]) -> "Rule":
        try:
            priority = int(row["priority"])
            direction = row["direction"]
            protocol = row["protocol"]
            action = row["action"]
            source = Matcher(row["source"]["kind"], row["source"].get("value"))
            destination = Matcher(row["destination"]["kind"], row["destination"].get("value"))
        except (KeyError, TypeError, ValueError) as exc:
            raise ModelError(f"incomplete rule {row.get('name', '<unnamed>')!r}") from exc
        if not 100 <= priority <= 4096:
            raise ModelError(f"custom NSG priority {priority} must be between 100 and 4096")
        if direction not in {"Inbound", "Outbound"}:
            raise ModelError(f"unsupported rule direction {direction!r}")
        if protocol not in {"TCP", "UDP", "Any"}:
            raise ModelError(f"model supports TCP, UDP and Any rules, not {protocol!r}")
        if action not in {"Allow", "Deny"}:
            raise ModelError(f"unsupported rule action {action!r}")
        if source.kind not in {"Any", "ASG", "CIDR", "IP"} or destination.kind not in {"Any", "ASG", "CIDR", "IP"}:
            raise ModelError("matcher kind must be Any, ASG, CIDR or IP")
        for matcher in (source, destination):
            if matcher.kind != "Any" and not matcher.value:
                raise ModelError(f"matcher {matcher.kind} requires a value")
        source_port = str(row.get("source_port", "*"))
        destination_port = str(row.get("destination_port", "*"))
        _validate_port_spec(source_port)
        _validate_port_spec(destination_port)
        return cls(
            str(row.get("name", "unnamed")), priority, direction, protocol, source,
            source_port, destination, destination_port, action
        )

    def matches(self, flow: Flow) -> bool:
        if self.direction != flow.direction or (self.protocol != "Any" and self.protocol != flow.protocol):
            return False
        if flow.direction == "Inbound":
            packet_source, source_port = flow.remote, flow.remote.port
            packet_destination, destination_port = flow.local, flow.local.port
        else:
            packet_source, source_port = flow.local, flow.local.port
            packet_destination, destination_port = flow.remote, flow.remote.port
        return (
            self.source.matches(packet_source)
            and _port_matches(self.source_port, source_port)
            and self.destination.matches(packet_destination)
            and _port_matches(self.destination_port, destination_port)
        )


def _validate_port_spec(spec: str) -> None:
    if spec == "*":
        return
    for part in spec.split(","):
        values = part.split("-", 1)
        try:
            start = int(values[0])
            end = int(values[-1])
        except ValueError as exc:
            raise ModelError(f"invalid port specification {spec!r}") from exc
        if not 0 <= start <= end <= 65535:
            raise ModelError(f"port range out of bounds: {spec!r}")


def _port_matches(spec: str, port: int) -> bool:
    if spec == "*":
        return True
    for part in spec.split(","):
        if "-" in part:
            start, end = (int(value) for value in part.split("-", 1))
            if start <= port <= end:
                return True
        elif int(part) == port:
            return True
    return False


class StatefulFlowTable:
    """Remember allowed 5-tuples so reverse traffic models NSG statefulness."""

    def __init__(self):
        self._allowed: set[tuple[Any, ...]] = set()

    def contains(self, flow: Flow) -> bool:
        return flow.key() in self._allowed

    def record(self, flow: Flow) -> None:
        self._allowed.add(flow.key())


class NsgModel:
    """Evaluate custom rules attached to one VM NIC and its subnet."""

    def __init__(self, document: dict[str, Any]):
        self.nics = document.get("nics", {})
        self.subnets = document.get("subnets", {})
        self.nsgs: dict[str, list[Rule]] = {}
        raw_nsgs = document.get("nsgs", {})
        if not self.nics or not raw_nsgs:
            raise ModelError("fixture requires NICs and NSGs")
        for nsg_id, row in raw_nsgs.items():
            rules = [Rule.from_dict(rule) for rule in row.get("rules", [])]
            priorities = [(rule.direction, rule.priority) for rule in rules]
            if len(priorities) != len(set(priorities)):
                raise ModelError(f"NSG {nsg_id!r} repeats a priority in the same direction")
            self.nsgs[nsg_id] = sorted(rules, key=lambda rule: rule.priority)
        for nic_id, nic in self.nics.items():
            subnet_id = nic.get("subnet_id")
            if subnet_id not in self.subnets:
                raise ModelError(f"NIC {nic_id!r} references unknown subnet {subnet_id!r}")
            for nsg_id in (nic.get("nsg_id"), self.subnets[subnet_id].get("nsg_id")):
                if nsg_id is not None and nsg_id not in self.nsgs:
                    raise ModelError(f"NIC/subnet references unknown NSG {nsg_id!r}")
        self.flows = document.get("flows", [])

    @classmethod
    def from_file(cls, path: Path) -> "NsgModel":
        try:
            document = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ModelError(f"cannot read scenario: {exc}") from exc
        return cls(document)

    def make_flow(self, row: dict[str, Any]) -> Flow:
        try:
            nic_id = row["local_nic"]
            nic = self.nics[nic_id]
            local_ip = ipaddress.ip_address(row.get("local_ip", nic["ip"]))
            remote_row = row["remote"]
            remote_ip = ipaddress.ip_address(remote_row["ip"])
            local_port = int(row["local_port"])
            remote_port = int(remote_row["port"])
        except (KeyError, TypeError, ValueError) as exc:
            raise ModelError(f"invalid flow {row.get('id', '<unnamed>')!r}") from exc
        if not isinstance(local_ip, ipaddress.IPv4Address) or not isinstance(remote_ip, ipaddress.IPv4Address):
            raise ModelError("this teaching model supports IPv4 flows only")
        if not (0 <= local_port <= 65535 and 0 <= remote_port <= 65535):
            raise ModelError("flow ports must be between 0 and 65535")
        direction, protocol = row.get("direction"), row.get("protocol")
        if direction not in {"Inbound", "Outbound"}:
            raise ModelError(f"unsupported flow direction {direction!r}")
        if protocol not in {"TCP", "UDP"}:
            raise ModelError("the IP Flow Verify teaching scenarios support TCP and UDP only")
        remote_name = remote_row.get("nic_id")
        remote_asgs = frozenset(self.nics.get(remote_name, {}).get("asgs", []))
        return Flow(
            str(row.get("id", "flow")), nic_id, direction, protocol,
            Endpoint(nic_id, local_ip, local_port, frozenset(nic.get("asgs", []))),
            Endpoint(str(remote_name or remote_row.get("name", "remote")), remote_ip, remote_port, remote_asgs),
        )

    def attached_nsgs(self, nic_id: str) -> tuple[str, ...]:
        if nic_id not in self.nics:
            raise ModelError(f"unknown NIC {nic_id!r}")
        nic = self.nics[nic_id]
        subnet_nsg = self.subnets[nic["subnet_id"]].get("nsg_id")
        nic_nsg = nic.get("nsg_id")
        return tuple(nsg_id for nsg_id in (subnet_nsg, nic_nsg) if nsg_id is not None)

    def evaluate_nsg(self, nsg_id: str, flow: Flow) -> tuple[str, str | None]:
        for rule in self.nsgs[nsg_id]:
            if rule.matches(flow):
                return rule.action.upper(), rule.name
        return "NO_CUSTOM_MATCH", None

    def evaluate(self, flow: Flow, state: StatefulFlowTable | None = None) -> tuple[str, list[tuple[str, str, str | None]]]:
        if state is not None and state.contains(flow):
            return "ALLOW_ESTABLISHED_FLOW", []
        results = []
        for nsg_id in self.attached_nsgs(flow.local_nic):
            action, rule_name = self.evaluate_nsg(nsg_id, flow)
            results.append((nsg_id, action, rule_name))
        if any(action == "DENY" for _, action, _ in results):
            verdict = "DENY"
        elif results and all(action == "ALLOW" for _, action, _ in results):
            verdict = "ALLOW"
            if state is not None:
                state.record(flow)
        else:
            verdict = "NOT_MODELED_DEFAULT_RULES"
        return verdict, results

    def report(self) -> str:
        lines = ["Custom NSG rule teaching model (synthetic IPv4 fixture; no Azure API call)"]
        state = StatefulFlowTable()
        for row in self.flows:
            flow = self.make_flow(row)
            verdict, layers = self.evaluate(flow, state)
            lines.append(f"\n{flow.id}: {flow.direction} {flow.protocol} local={flow.local.ip}:{flow.local.port} remote={flow.remote.ip}:{flow.remote.port}")
            if layers:
                lines.append("  associated-filter results (scope listing, not a packet-order trace):")
                for nsg_id, action, rule in layers:
                    lines.append(f"    {nsg_id}: {action}" + (f" by {rule}" if rule else ""))
            else:
                lines.append("  established flow record matched; current rules were not re-evaluated")
            lines.append(f"  verdict: {verdict}")
        lines.append("\nNo result establishes Azure effective rules, platform admin rules, or end-to-end reachability.")
        return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--scenario",
        type=Path,
        default=Path(__file__).parent / "scenarios" / "banking-payment.json",
    )
    args = parser.parse_args()
    print(NsgModel.from_file(args.scenario).report())


if __name__ == "__main__":
    main()
