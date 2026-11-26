"""A small, synthetic decision model for Private Endpoint name resolution.

It is not an Azure DNS emulator and makes no Azure API calls.
"""
from __future__ import annotations

from dataclasses import dataclass
from ipaddress import IPv4Address
import json
from pathlib import Path
import sys

VALID_STATUSES = {"Approved", "Pending", "Rejected", "Disconnected"}


class ModelInputError(ValueError):
    """Raised when a fixture describes an unsupported or invalid case."""


@dataclass(frozen=True)
class Endpoint:
    service_fqdn: str
    private_fqdn: str
    private_ip: str
    public_ip: str
    connection_status: str

    def __post_init__(self) -> None:
        prefix = self.service_fqdn.removesuffix(".blob.core.windows.net")
        if not prefix or prefix == self.service_fqdn:
            raise ModelInputError("only a Storage Blob service FQDN is in scope")
        expected_private = f"{prefix}.privatelink.blob.core.windows.net"
        if self.private_fqdn != expected_private:
            raise ModelInputError("private FQDN must match the service account name")
        for value, label in ((self.private_ip, "private_ip"), (self.public_ip, "public_ip")):
            try:
                IPv4Address(value)
            except ValueError as exc:
                raise ModelInputError(f"{label} must be a valid IPv4 address") from exc
        if not IPv4Address(self.private_ip).is_private:
            raise ModelInputError("private_ip must be RFC1918/private address space")
        if self.connection_status not in VALID_STATUSES:
            raise ModelInputError(f"unsupported private endpoint status: {self.connection_status}")


@dataclass(frozen=True)
class DNSContext:
    """Describe whether this resolver can see the linked private zone."""

    vnet_linked: bool
    custom_dns: bool
    forwards_from_linked_vnet: bool
    private_a_record_present: bool
    fallback_to_internet: bool


@dataclass(frozen=True)
class Resolution:
    kind: str
    address: str | None
    service_hostname: str
    reason: str


def resolve(endpoint: Endpoint, context: DNSContext) -> Resolution:
    """Select a fixture answer; no real CNAME walk, cache, TTL, or DNS packet exists."""
    zone_visible = context.vnet_linked and (
        not context.custom_dns or context.forwards_from_linked_vnet
    )
    if not zone_visible:
        return Resolution(
            "PUBLIC_ENDPOINT", endpoint.public_ip, endpoint.service_fqdn,
            "private zone is not visible to this resolver; use the fixture public answer",
        )
    if context.private_a_record_present:
        return Resolution(
            "PRIVATE_ENDPOINT", endpoint.private_ip, endpoint.service_fqdn,
            "linked private zone contains the endpoint A record",
        )
    if context.fallback_to_internet:
        return Resolution(
            "PUBLIC_ENDPOINT", endpoint.public_ip, endpoint.service_fqdn,
            "linked private zone has no A record; fallback-to-Internet selects the fixture public answer",
        )
    return Resolution(
        "NXDOMAIN", None, endpoint.service_fqdn,
        "linked private zone has no matching A record and fallback is disabled",
    )


def evaluate(
    endpoint: Endpoint,
    context: DNSContext,
    *,
    public_network_enabled: bool,
    data_authorized: bool,
) -> tuple[Resolution, str]:
    """Evaluate only DNS choice, endpoint approval, public access, and auth gates."""
    answer = resolve(endpoint, context)
    if answer.kind == "NXDOMAIN":
        return answer, "DNS_NXDOMAIN"
    if answer.kind == "PRIVATE_ENDPOINT":
        if endpoint.connection_status != "Approved":
            return answer, "ENDPOINT_NOT_APPROVED"
        if not data_authorized:
            return answer, "DATA_PLANE_AUTH_DENIED"
        return answer, "PRIVATE_ACCESS_ALLOWED"
    if not public_network_enabled:
        return answer, "PUBLIC_NETWORK_ACCESS_DISABLED"
    if not data_authorized:
        return answer, "DATA_PLANE_AUTH_DENIED"
    return answer, "PUBLIC_ACCESS_ALLOWED"


def load_document(path: Path) -> tuple[Endpoint, list[dict]]:
    document = json.loads(path.read_text(encoding="utf-8"))
    raw = document["endpoint"]
    endpoint = Endpoint(**raw)
    return endpoint, document["cases"]


def run_document(path: Path) -> list[tuple[str, Resolution, str]]:
    endpoint, cases = load_document(path)
    results = []
    for case in cases:
        context = DNSContext(**case["dns"])
        case_endpoint = Endpoint(**(endpoint.__dict__ | {
            "connection_status": case.get("connection_status", endpoint.connection_status)
        }))
        resolution, outcome = evaluate(
            case_endpoint,
            context,
            public_network_enabled=case["public_network_enabled"],
            data_authorized=case["data_authorized"],
        )
        results.append((case["name"], resolution, outcome))
    return results


def main() -> int:
    default = Path(__file__).with_name("scenarios") / "storage-private-endpoint.json"
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else default
    try:
        for name, answer, outcome in run_document(path):
            target = answer.address or "NO_ADDRESS"
            print(f"{name}: DNS={answer.kind} {target}; data-path={outcome}")
            print(f"  client hostname remains {answer.service_hostname}")
    except (OSError, KeyError, TypeError, json.JSONDecodeError, ModelInputError) as exc:
        print(f"fixture error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
