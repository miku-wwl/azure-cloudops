#!/usr/bin/env python3
"""A deliberately small, allow-only model of inherited role assignments."""

from __future__ import annotations

import argparse
import fnmatch
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


class ScopeError(ValueError):
    """The fixture contains an unknown scope, parent, or cycle."""


@dataclass(frozen=True)
class Scope:
    id: str
    arm_scope: str
    parent: str | None


@dataclass(frozen=True)
class Assignment:
    principal: str
    scope: str
    role: str
    actions: tuple[str, ...]
    data_actions: tuple[str, ...]


class ScopeModel:
    """Evaluate only direct and ancestor allow grants from one JSON fixture."""

    def __init__(self, document: dict[str, Any]):
        self.scopes = {
            row["id"]: Scope(row["id"], row["arm_scope"], row.get("parent"))
            for row in document["scopes"]
        }
        if len(self.scopes) != len(document["scopes"]):
            raise ScopeError("scope ids must be unique")
        for scope in self.scopes.values():
            if scope.parent is not None and scope.parent not in self.scopes:
                raise ScopeError(f"unknown parent {scope.parent!r} for {scope.id!r}")
            self.scope_chain(scope.id)
        self.assignments = tuple(
            Assignment(
                principal=row["principal"],
                scope=row["scope"],
                role=row["role"],
                actions=tuple(row.get("actions", ())),
                data_actions=tuple(row.get("data_actions", ())),
            )
            for row in document["assignments"]
        )
        for assignment in self.assignments:
            if assignment.scope not in self.scopes:
                raise ScopeError(f"unknown assignment scope {assignment.scope!r}")

    @classmethod
    def from_file(cls, path: Path) -> "ScopeModel":
        return cls(json.loads(path.read_text(encoding="utf-8")))

    def scope_chain(self, target: str) -> tuple[str, ...]:
        """Return target and all parents, nearest first."""
        if target not in self.scopes:
            raise ScopeError(f"unknown scope {target!r}")
        chain: list[str] = []
        seen: set[str] = set()
        current: str | None = target
        while current is not None:
            if current in seen:
                raise ScopeError(f"scope parent cycle at {current!r}")
            seen.add(current)
            chain.append(current)
            current = self.scopes[current].parent
        return tuple(chain)

    def inherited_assignments(self, principal: str, target: str) -> tuple[Assignment, ...]:
        chain = self.scope_chain(target)
        rank = {scope_id: index for index, scope_id in enumerate(reversed(chain))}
        matches = [
            assignment
            for assignment in self.assignments
            if assignment.principal == principal and assignment.scope in chain
        ]
        return tuple(sorted(matches, key=lambda item: rank[item.scope]))

    def matching_grants(
        self, principal: str, target: str, operation: str, plane: str
    ) -> tuple[Assignment, ...]:
        if plane not in ("control", "data"):
            raise ValueError("plane must be 'control' or 'data'")
        field = "actions" if plane == "control" else "data_actions"
        requested = operation.casefold()
        return tuple(
            assignment
            for assignment in self.inherited_assignments(principal, target)
            if any(fnmatch.fnmatchcase(requested, rule.casefold()) for rule in getattr(assignment, field))
        )

    def allows(self, principal: str, target: str, operation: str, plane: str) -> bool:
        return bool(self.matching_grants(principal, target, operation, plane))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--scenario",
        type=Path,
        default=Path(__file__).parent / "scenarios" / "banking-lz.json",
    )
    args = parser.parse_args()
    document = json.loads(args.scenario.read_text(encoding="utf-8"))
    model = ScopeModel(document)

    print("Scope inheritance fixture (illustrative; no Azure API call)")
    for probe in document["probes"]:
        grants = model.matching_grants(
            probe["principal"], probe["target"], probe["operation"], probe["plane"]
        )
        outcome = "ALLOW" if grants else "NO MATCH"
        origin = ", ".join(f"{grant.role}@{grant.scope}" for grant in grants) or "none"
        print(
            f"{probe['principal']} -> {probe['target']} "
            f"[{probe['plane']}] {probe['operation']}: {outcome}; grants={origin}"
        )


if __name__ == "__main__":
    main()
