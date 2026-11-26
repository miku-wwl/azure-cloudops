#!/usr/bin/env python3
"""Evaluate a tiny, synthetic token-boundary and Azure RBAC fixture.

This is a teaching model, not a JWT validator or an Azure authorization engine.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


class FixtureError(ValueError):
    """The local teaching fixture is malformed or internally inconsistent."""


@dataclass(frozen=True)
class Scope:
    id: str
    parent: str | None


@dataclass(frozen=True)
class Role:
    id: str
    name: str
    actions: tuple[str, ...]
    not_actions: tuple[str, ...]
    data_actions: tuple[str, ...]
    not_data_actions: tuple[str, ...]


@dataclass(frozen=True)
class Assignment:
    id: str
    tenant_id: str
    principal_id: str
    role_id: str
    scope: str


@dataclass(frozen=True)
class Decision:
    decision: str
    stage: str
    reason: str
    assignments: tuple[str, ...] = ()


class AuthorizationModel:
    """Check asserted token context, then union matching inherited RBAC grants."""

    def __init__(self, document: dict[str, Any]):
        self.scopes = {
            row["id"]: Scope(row["id"], row.get("parent"))
            for row in document["scopes"]
        }
        if len(self.scopes) != len(document["scopes"]):
            raise FixtureError("scope ids must be unique")
        for scope in self.scopes.values():
            if scope.parent is not None and scope.parent not in self.scopes:
                raise FixtureError(f"unknown parent {scope.parent!r} for {scope.id!r}")
            self.scope_chain(scope.id)

        self.roles = {
            row["id"]: Role(
                id=row["id"],
                name=row["name"],
                actions=tuple(row.get("actions", ())),
                not_actions=tuple(row.get("not_actions", ())),
                data_actions=tuple(row.get("data_actions", ())),
                not_data_actions=tuple(row.get("not_data_actions", ())),
            )
            for row in document["roles"]
        }
        if len(self.roles) != len(document["roles"]):
            raise FixtureError("role ids must be unique")

        self.assignments = tuple(
            Assignment(
                id=row["id"],
                tenant_id=row["tenant_id"],
                principal_id=row["principal_id"],
                role_id=row["role_id"],
                scope=row["scope"],
            )
            for row in document["assignments"]
        )
        for assignment in self.assignments:
            if assignment.scope not in self.scopes:
                raise FixtureError(f"unknown scope {assignment.scope!r}")
            if assignment.role_id not in self.roles:
                raise FixtureError(f"unknown role {assignment.role_id!r}")

    @classmethod
    def from_file(cls, path: Path) -> "AuthorizationModel":
        return cls(json.loads(path.read_text(encoding="utf-8")))

    def scope_chain(self, target: str) -> tuple[str, ...]:
        """Return the target and its ancestors, nearest scope first."""
        if target not in self.scopes:
            raise FixtureError(f"unknown target scope {target!r}")
        chain: list[str] = []
        seen: set[str] = set()
        current: str | None = target
        while current is not None:
            if current in seen:
                raise FixtureError(f"scope parent cycle at {current!r}")
            seen.add(current)
            chain.append(current)
            current = self.scopes[current].parent
        return tuple(chain)

    @staticmethod
    def _matches(operation: str, patterns: tuple[str, ...]) -> bool:
        candidate = operation.casefold()
        return any(fnmatch.fnmatchcase(candidate, pattern.casefold()) for pattern in patterns)

    def _check_token(self, request: dict[str, Any]) -> Decision | None:
        token = request["token"]
        now = request["now"]

        # This fixture boolean represents an upstream trust result; no JWT signature
        # is parsed or verified here.
        if not request.get("signature_trusted", False):
            return Decision("DENY", "TOKEN", "fixture trust assertion is false")
        if token.get("iss") != request["expected_issuer"]:
            return Decision("DENY", "TOKEN", "issuer does not match configured issuer")
        if token.get("tid") != request["expected_tenant"]:
            return Decision("DENY", "TOKEN", "tenant does not match this API boundary")
        if token.get("aud") != request["expected_audience"]:
            return Decision("DENY", "TOKEN", "audience is not this API")
        if not isinstance(token.get("exp"), int) or token["exp"] <= now:
            return Decision("DENY", "TOKEN", "token is expired or has no integer exp")
        if not isinstance(token.get("nbf", 0), int) or token.get("nbf", 0) > now:
            return Decision("DENY", "TOKEN", "token is not yet valid")
        if not isinstance(token.get("oid"), str) or not token["oid"]:
            return Decision("DENY", "TOKEN", "tenant-local principal object id is missing")
        return None

    def evaluate(self, request: dict[str, Any]) -> Decision:
        """Evaluate one synthetic API request and return its first decision boundary."""
        token_rejection = self._check_token(request)
        if token_rejection:
            return token_rejection

        target = request["target"]
        operation = request["operation"]
        plane = request["plane"]
        if plane not in ("control", "data"):
            raise FixtureError("plane must be 'control' or 'data'")
        chain = self.scope_chain(target)
        token = request["token"]
        applicable = tuple(
            assignment
            for assignment in self.assignments
            if assignment.tenant_id == token["tid"]
            and assignment.principal_id == token["oid"]
            and assignment.scope in chain
        )
        if not applicable:
            return Decision("DENY", "RBAC", "no matching principal assignment at target or ancestor")

        grants: list[str] = []
        excluded: list[str] = []
        for assignment in applicable:
            role = self.roles[assignment.role_id]
            if plane == "control":
                allows = role.actions
                excludes = role.not_actions
            else:
                allows = role.data_actions
                excludes = role.not_data_actions
            if self._matches(operation, allows):
                if self._matches(operation, excludes):
                    excluded.append(assignment.id)
                else:
                    grants.append(assignment.id)

        if grants:
            return Decision("ALLOW", "RBAC", "at least one applicable role grants this operation", tuple(grants))
        if excluded:
            return Decision(
                "DENY",
                "RBAC",
                "matching role permission is removed by its own NotActions/NotDataActions",
                tuple(excluded),
            )
        if applicable:
            return Decision("DENY", "RBAC", "assignments matched, but none grants this operation on this plane", ())
        return Decision("DENY", "RBAC", "no applicable role grants this operation on this plane", ())


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--scenario",
        type=Path,
        default=Path(__file__).parent / "scenarios" / "authorization-cases.json",
    )
    args = parser.parse_args()
    document = json.loads(args.scenario.read_text(encoding="utf-8"))
    model = AuthorizationModel(document)
    print("Synthetic token boundary + role-assignment fixture (no Azure or JWT call)")
    for case in document["requests"]:
        result = model.evaluate(case)
        token = case["token"]
        print(
            f"{case['id']}: {result.decision} at {result.stage}; {result.reason}; "
            f"aud={token.get('aud')} {case['plane']}:{case['operation']} "
            f"target={case['target']} granting_assignments={','.join(result.assignments) or 'none'}"
        )


if __name__ == "__main__":
    main()
