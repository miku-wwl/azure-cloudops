#!/usr/bin/env python3
"""Evaluate a synthetic managed-identity, federation, and Key Vault flow.

This is a small teaching fixture. It does not acquire or validate real tokens,
call Azure, or return any secret value.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


KEY_VAULT_AUDIENCE = "https://vault.azure.net"


class FixtureError(ValueError):
    """The local teaching fixture is malformed or internally inconsistent."""


@dataclass(frozen=True)
class Decision:
    decision: str
    stage: str
    reason: str
    identity_id: str | None = None


class CredentialFlowModel:
    """Select a synthetic identity, check trust and gates, and report no values."""

    def __init__(self, document: dict[str, Any]):
        self.identities = {row["id"]: row for row in document["identities"]}
        if len(self.identities) != len(document["identities"]):
            raise FixtureError("identity ids must be unique")

        self.hosts = {row["id"]: row for row in document["hosts"]}
        if len(self.hosts) != len(document["hosts"]):
            raise FixtureError("host ids must be unique")
        for host in self.hosts.values():
            attached = ([host["system_identity"]] if host.get("system_identity") else [])
            attached.extend(host.get("user_assigned", []))
            missing = [identity for identity in attached if identity not in self.identities]
            if missing:
                raise FixtureError(f"host {host['id']!r} references unknown identity {missing[0]!r}")
            if len(attached) != len(set(attached)):
                raise FixtureError(f"host {host['id']!r} attaches an identity more than once")

        self.federated_credentials = {
            row["id"]: row for row in document["federated_credentials"]
        }
        if len(self.federated_credentials) != len(document["federated_credentials"]):
            raise FixtureError("federated credential ids must be unique")
        for credential in self.federated_credentials.values():
            if credential["identity_id"] not in self.identities:
                raise FixtureError(f"federated credential {credential['id']!r} references unknown identity")

        self.vaults = {row["id"]: row for row in document["vaults"]}
        if len(self.vaults) != len(document["vaults"]):
            raise FixtureError("vault ids must be unique")
        for vault in self.vaults.values():
            if vault["permission_model"] not in ("azure_rbac", "access_policy"):
                raise FixtureError(f"unknown permission model for {vault['id']!r}")

        self.requests = tuple(document["requests"])

    @classmethod
    def from_file(cls, path: Path) -> "CredentialFlowModel":
        return cls(json.loads(path.read_text(encoding="utf-8")))

    def _select_managed_identity(self, request: dict[str, Any]) -> str | Decision:
        host_id = request["host_id"]
        if host_id not in self.hosts:
            raise FixtureError(f"unknown host {host_id!r}")
        host = self.hosts[host_id]
        system_identity = host.get("system_identity")
        user_assigned = tuple(host.get("user_assigned", ()))
        selected = request.get("identity_selector")

        if selected is None:
            if system_identity:
                selected = system_identity
            elif len(user_assigned) == 1:
                selected = user_assigned[0]
            elif len(user_assigned) > 1:
                return Decision("DENY", "CREDENTIAL", "multiple user-assigned identities require an explicit selector")
            else:
                return Decision("DENY", "CREDENTIAL", "host has no managed identity")

        attached = set(user_assigned)
        if system_identity:
            attached.add(system_identity)
        if selected not in attached:
            return Decision("DENY", "CREDENTIAL", "selected identity is not attached to this host")
        return selected

    def _resolve_identity(self, request: dict[str, Any]) -> str | Decision:
        credential_type = request["credential_type"]
        if credential_type == "managed_identity":
            return self._select_managed_identity(request)
        if credential_type == "workload_federation":
            credential_id = request["federated_credential_id"]
            if credential_id not in self.federated_credentials:
                raise FixtureError(f"unknown federated credential {credential_id!r}")
            credential = self.federated_credentials[credential_id]
            external = request["external_token"]
            # These strings are compared exactly (including case), as Entra does
            # for federated credential issuer, subject, and audience matching.
            expected = (credential["issuer"], credential["subject"], credential["audience"])
            actual = (external.get("iss"), external.get("sub"), external.get("aud"))
            if actual != expected:
                return Decision("DENY", "FEDERATION", "external issuer, subject, or audience did not exactly match")
            return credential["identity_id"]
        raise FixtureError(f"unknown credential type {credential_type!r}")

    def evaluate(self, request: dict[str, Any]) -> Decision:
        """Return the first synthetic gate result without reading or printing values."""
        identity_id = self._resolve_identity(request)
        if isinstance(identity_id, Decision):
            return identity_id
        identity = self.identities[identity_id]

        vault_id = request["vault_id"]
        if vault_id not in self.vaults:
            raise FixtureError(f"unknown vault {vault_id!r}")
        vault = self.vaults[vault_id]
        token = request["entra_access_token"]

        # Claims are fictional input. No JWT is parsed, signed, or verified.
        if token.get("aud") != KEY_VAULT_AUDIENCE:
            return Decision("DENY", "TOKEN", "Entra access token audience is not Key Vault", identity_id)
        if token.get("tenant_id") != vault["tenant_id"]:
            return Decision("DENY", "TOKEN", "token tenant does not match the vault tenant", identity_id)
        if identity.get("tenant_id") != vault["tenant_id"]:
            return Decision("DENY", "TOKEN", "selected identity is not in the vault tenant", identity_id)
        if token.get("principal_id") != identity["principal_id"]:
            return Decision("DENY", "TOKEN", "token principal does not match the selected identity", identity_id)

        if not vault["network_allowed"]:
            return Decision("DENY", "NETWORK", "vault network path is blocked by the fixture", identity_id)

        operation = request["operation"]
        if operation not in ("secret:get", "secret:list", "secret:set", "secret:delete"):
            raise FixtureError(f"unknown secret operation {operation!r}")

        if vault["permission_model"] == "azure_rbac":
            grants = [
                row for row in vault.get("role_assignments", [])
                if row["principal_id"] == identity["principal_id"]
                and operation in _role_permissions(row["role"])
            ]
            if grants:
                return Decision("ALLOW", "COMPLETE", "all fixture gates passed", identity_id)
            return Decision("DENY", "AUTHZ", "no Key Vault data role grants this operation", identity_id)

        grants = [
            row for row in vault.get("access_policies", [])
            if row["principal_id"] == identity["principal_id"]
            and operation.removeprefix("secret:") in row.get("secret_permissions", [])
        ]
        if grants:
            return Decision("ALLOW", "COMPLETE", "all fixture gates passed", identity_id)
        return Decision("DENY", "AUTHZ", "no access policy grants this operation", identity_id)


def _role_permissions(role: str) -> frozenset[str]:
    """A deliberately tiny symbolic subset of Key Vault role behavior."""
    if role == "Key Vault Secrets User":
        return frozenset({"secret:get", "secret:list"})
    if role == "Key Vault Secrets Officer":
        return frozenset({"secret:get", "secret:list", "secret:set", "secret:delete"})
    if role == "Key Vault Administrator":
        return frozenset({"secret:get", "secret:list", "secret:set", "secret:delete"})
    if role == "Key Vault Contributor":
        return frozenset()
    raise FixtureError(f"unknown symbolic role {role!r}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--scenario",
        type=Path,
        default=Path(__file__).parent / "scenarios" / "credential-flow-cases.json",
    )
    args = parser.parse_args()
    document = json.loads(args.scenario.read_text(encoding="utf-8"))
    model = CredentialFlowModel(document)
    print("Synthetic credential flow fixture (no token, Azure, network, or secret value)")
    for request in model.requests:
        result = model.evaluate(request)
        print(f"{request['id']}: {result.decision} at {result.stage}; {result.reason}")


if __name__ == "__main__":
    main()
