#!/usr/bin/env python3
"""Deterministic critical-path and SLO-budget teaching model; no Azure APIs."""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any


class ModelError(ValueError):
    """Invalid probability, scenario, or topology fixture."""


def series_availability(parts: list[float] | tuple[float, ...]) -> float:
    """Multiply serial component availability estimates (independence assumed)."""
    if not parts:
        raise ModelError("at least one component probability is required")
    if any(not 0 <= value <= 1 for value in parts):
        raise ModelError("availability values must be between 0 and 1")
    return math.prod(parts)


def parallel_availability(parts: list[float] | tuple[float, ...]) -> float:
    """Probability that at least one independent parallel component is available."""
    if not parts:
        raise ModelError("at least one component probability is required")
    if any(not 0 <= value <= 1 for value in parts):
        raise ModelError("availability values must be between 0 and 1")
    return 1 - math.prod(1 - value for value in parts)


def error_budget_minutes(slo: float, window_minutes: int) -> float:
    """Translate a time-based availability SLO into a maximum bad-time budget."""
    if not 0 < slo <= 1:
        raise ModelError("SLO must be greater than 0 and at most 1")
    if window_minutes <= 0:
        raise ModelError("window_minutes must be positive")
    return window_minutes * (1 - slo)


@dataclass(frozen=True)
class Topology:
    name: str
    description: str
    required_groups: dict[str, tuple[str, ...]]
    supported_faults: frozenset[str]


@dataclass(frozen=True)
class Fault:
    id: str
    description: str
    down: frozenset[str]
    expected: dict[str, bool | None]


class ReliabilityModel:
    """Check an AND/OR critical path against explicit fixture failures."""

    def __init__(self, document: dict[str, Any]):
        self.slo = float(document["time_based_slo"])
        self.window_minutes = int(document["window_minutes"])
        error_budget_minutes(self.slo, self.window_minutes)
        self.topologies: dict[str, Topology] = {}
        for key, row in document["topologies"].items():
            groups = {name: tuple(items) for name, items in row["required_groups"].items()}
            if not groups or any(not items for items in groups.values()):
                raise ModelError(f"topology {key!r} contains an empty required group")
            self.topologies[key] = Topology(
                key,
                row["description"],
                groups,
                frozenset(row["supported_faults"]),
            )
        self.faults = tuple(
            Fault(
                row["id"],
                row["description"],
                frozenset(row["down"]),
                row["expected"],
            )
            for row in document["faults"]
        )
        if not self.topologies or not self.faults:
            raise ModelError("fixture requires topologies and faults")
        for fault in self.faults:
            unknown = set(fault.expected) - set(self.topologies)
            if unknown:
                raise ModelError(f"fault {fault.id!r} has unknown topologies: {sorted(unknown)}")

    @classmethod
    def from_file(cls, path: Path) -> "ReliabilityModel":
        return cls(json.loads(path.read_text(encoding="utf-8")))

    def evaluate(self, topology_id: str, fault_id: str) -> bool | None:
        """Return True/False, or None when the topology cannot represent this fault."""
        if topology_id not in self.topologies:
            raise ModelError(f"unknown topology {topology_id!r}")
        fault = next((item for item in self.faults if item.id == fault_id), None)
        if fault is None:
            raise ModelError(f"unknown fault {fault_id!r}")
        topology = self.topologies[topology_id]
        if fault_id not in topology.supported_faults:
            return None
        return all(
            any(component not in fault.down for component in alternatives)
            for alternatives in topology.required_groups.values()
        )

    def report(self) -> str:
        lines = ["Critical-flow fault matrix (illustrative JSON fixture; no Azure API call)"]
        for fault in self.faults:
            lines.append(f"\n{fault.id}: {fault.description}")
            for topology_id, topology in self.topologies.items():
                result = self.evaluate(topology_id, fault.id)
                status = "NOT_MODELED" if result is None else "AVAILABLE" if result else "UNAVAILABLE"
                lines.append(f"  {topology.name}: {status}")
        minutes = error_budget_minutes(self.slo, self.window_minutes)
        lines.append(
            f"\nTime-based SLO {self.slo:.5%} over {self.window_minutes} minutes "
            f"allows {minutes:.2f} minutes of bad time."
        )
        lines.append("This budget conversion does not apply directly to request-based SLI.")
        return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--scenario",
        type=Path,
        default=Path(__file__).parent / "scenarios" / "settlement.json",
    )
    args = parser.parse_args()
    model = ReliabilityModel.from_file(args.scenario)
    print(model.report())


if __name__ == "__main__":
    main()
