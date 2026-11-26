"""Small deterministic teaching model; not an implementation of Terraform or Azure."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


class ModelError(ValueError):
    """Raised when the synthetic contract is invalid."""


def topological_order(nodes: set[str], edges: set[tuple[str, str]]) -> list[str]:
    """Return a deterministic dependency-first order for (prerequisite, dependent) edges."""
    unknown = {name for edge in edges for name in edge if name not in nodes}
    if unknown:
        raise ModelError(f"unknown graph node(s): {', '.join(sorted(unknown))}")

    remaining = {node: set() for node in nodes}
    for prerequisite, dependent in edges:
        remaining[dependent].add(prerequisite)

    order: list[str] = []
    while remaining:
        ready = sorted(node for node, deps in remaining.items() if not deps)
        if not ready:
            raise ModelError("dependency cycle")
        order.extend(ready)
        for node in ready:
            remaining.pop(node)
        for deps in remaining.values():
            deps.difference_update(ready)
    return order


@dataclass(frozen=True)
class ResourceBinding:
    address: str
    provider: str
    remote_id: str


def validate_bindings(bindings: list[ResourceBinding]) -> None:
    addresses = [item.address for item in bindings]
    remote_ids = [item.remote_id for item in bindings]
    if len(addresses) != len(set(addresses)):
        raise ModelError("a resource address may appear only once")
    if len(remote_ids) != len(set(remote_ids)):
        raise ModelError("a remote object may be bound to only one address")
    if any(not item.address or not item.provider or not item.remote_id for item in bindings):
        raise ModelError("address, provider, and remote_id are required")


def choose_provider(resource_type: str, explicit: str | None = None) -> str:
    if explicit:
        if explicit not in {"azurerm", "azapi"}:
            raise ModelError("provider must be azurerm or azapi")
        return explicit
    if resource_type.startswith("azurerm_"):
        return "azurerm"
    if resource_type == "azapi_resource":
        return "azapi"
    raise ModelError("provider cannot be inferred from this synthetic resource type")


@dataclass(frozen=True)
class PlannedChange:
    action: str
    changed_fields: tuple[str, ...] = ()


def classify_change(
    before: dict[str, Any] | None,
    after: dict[str, Any] | None,
    *,
    force_new: set[str] | None = None,
    ignore_changes: set[str] | None = None,
    prevent_destroy: bool = False,
    create_before_destroy: bool = False,
) -> PlannedChange:
    force_new = force_new or set()
    ignored = ignore_changes or set()
    if before is None and after is None:
        return PlannedChange("no-op")
    if before is None:
        return PlannedChange("create")
    if after is None:
        if prevent_destroy:
            raise ModelError("prevent_destroy blocks this synthetic destroy")
        return PlannedChange("destroy")

    changed = tuple(sorted(
        key for key in before.keys() | after.keys()
        if key not in ignored and before.get(key) != after.get(key)
    ))
    if not changed:
        return PlannedChange("no-op")
    if set(changed) & force_new:
        return PlannedChange("replace-cbd" if create_before_destroy else "replace", changed)
    return PlannedChange("update", changed)


def import_existing(
    *,
    remote_id: str,
    destination: str,
    remote_catalog: set[str],
    bindings: list[ResourceBinding],
    provider: str,
) -> PlannedChange:
    """Model an import proposal. It never creates a remote object."""
    validate_bindings(bindings)
    if not remote_id or not destination or not provider:
        raise ModelError("remote_id, destination, and provider are required")
    if remote_id not in remote_catalog:
        raise ModelError("cannot import an object absent from the synthetic catalog")
    by_address = {item.address: item for item in bindings}
    if destination in by_address:
        if by_address[destination].remote_id == remote_id:
            return PlannedChange("already-bound")
        raise ModelError("destination address is bound to a different object")
    if any(item.remote_id == remote_id for item in bindings):
        raise ModelError("remote object is already bound at another address")
    return PlannedChange("import")
