"""Offline decision model for Azure Storage and Azure SQL data boundaries."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Decision:
    code: str
    next_evidence: str


READ_ROLES = {
    "Storage Blob Data Reader",
    "Storage Blob Data Contributor",
    "Storage Blob Data Owner",
}


def evaluate_blob_read(case: dict[str, Any]) -> Decision:
    """Check the Blob read path in order: name, network, transport, identity, data."""
    resolved = case.get("resolved_endpoint", "public")
    if case.get("private_required", False) and resolved != "private":
        return Decision(
            "STORAGE_DNS_PATH_MISMATCH",
            "Resolve the normal blob FQDN from the workload DNS path and inspect its CNAME/A chain.",
        )
    if resolved == "private":
        if not case.get("private_endpoint_approved", False):
            return Decision(
                "STORAGE_PRIVATE_ENDPOINT_NOT_APPROVED",
                "Inspect the private endpoint connection state and the requested storage subresource.",
            )
        subresources = set(case.get("private_subresources", []))
        if case.get("required_subresource", "blob") not in subresources:
            return Decision(
                "STORAGE_PRIVATE_SUBRESOURCE_MISSING",
                "Check whether the client needs blob, dfs, file, queue, table, or another endpoint subresource.",
            )
        if not case.get("private_path_allowed", True):
            return Decision(
                "STORAGE_PRIVATE_PATH_BLOCKED",
                "Inspect client routing, NSGs, private-endpoint network policies, and any NVA path.",
            )
    elif resolved == "public":
        if not case.get("public_network_enabled", True):
            return Decision(
                "STORAGE_PUBLIC_ENDPOINT_DISABLED",
                "Use the intended private endpoint and verify that the workload resolves the normal FQDN privately.",
            )
        if case.get("firewall_default", "Allow") == "Deny" and not case.get(
            "public_source_allowed", False
        ):
            return Decision(
                "STORAGE_PUBLIC_FIREWALL_DENY",
                "Check the source NAT address, selected subnet/resource rules, and the storage firewall default action.",
            )
    else:
        return Decision("STORAGE_DNS_LOOKUP_FAILED", "Inspect the workload resolver and authoritative DNS path.")

    if case.get("secure_transfer_required", True) and case.get("protocol", "https") != "https":
        return Decision("STORAGE_HTTPS_REQUIRED", "Use the normal HTTPS storage endpoint and inspect TLS policy.")

    mode = case.get("auth_mode", "entra")
    if mode == "entra":
        if not case.get("token_valid", False):
            return Decision("STORAGE_TOKEN_INVALID", "Identify the principal and token audience without exposing the token.")
        if case.get("data_role") not in READ_ROLES:
            return Decision(
                "STORAGE_DATA_ROLE_MISSING",
                "Check a Blob data role at the narrowest useful scope; a management-plane Reader role is not a data role.",
            )
        if not case.get("role_effective", False):
            return Decision("STORAGE_ROLE_PROPAGATION_PENDING", "Verify assignment scope and allow for role propagation.")
    elif mode == "sas":
        if not case.get("sas_valid", False):
            return Decision("STORAGE_SAS_INVALID", "Check SAS resource, permission, protocol, expiry, and signed scope.")
    elif mode == "shared_key":
        if not case.get("shared_key_allowed", False):
            return Decision("STORAGE_SHARED_KEY_DISABLED", "Use an approved authorization mode; do not re-enable Shared Key by default.")
        if not case.get("credential_valid", False):
            return Decision("STORAGE_SHARED_KEY_INVALID", "Verify key selection and rotation state without printing the key.")
    else:
        return Decision("STORAGE_AUTH_MODE_UNSUPPORTED", "Confirm which Storage authorization mode the client actually used.")

    object_state = case.get("object_state", "present")
    if object_state == "deleted":
        if case.get("blob_soft_delete_enabled", False):
            return Decision(
                "STORAGE_BLOB_DELETED_RECOVERABLE",
                "Confirm the deletion time, retention window, and blob/version state before choosing a recovery operation.",
            )
        return Decision("STORAGE_BLOB_NOT_FOUND", "Verify the object path and whether a usable recovery point exists.")
    if object_state != "present":
        return Decision("STORAGE_BLOB_NOT_FOUND", "Check the account, container, exact blob name, and current object state.")
    return Decision("STORAGE_BLOB_READ_READY", "Run an approved application-level read and validate the returned object.")


def evaluate_sql_connection(case: dict[str, Any]) -> Decision:
    """Separate SQL DNS, endpoint, transport, authentication, and database grants."""
    resolved = case.get("resolved_endpoint", "public")
    if case.get("private_required", False) and resolved != "private":
        return Decision(
            "SQL_DNS_PATH_MISMATCH",
            "Resolve the normal logical-server FQDN from the client and verify the private DNS zone/VNet link.",
        )
    if resolved == "private":
        if not case.get("private_endpoint_approved", False):
            return Decision("SQL_PRIVATE_ENDPOINT_NOT_APPROVED", "Inspect the SQL private endpoint connection approval state.")
        if not case.get("private_path_allowed", True):
            return Decision("SQL_PRIVATE_PATH_BLOCKED", "Inspect routing, NSGs, NVA state, and the private-endpoint path.")
    elif resolved == "public":
        if not case.get("public_network_enabled", True):
            return Decision("SQL_PUBLIC_ACCESS_DISABLED", "Use the intended approved private endpoint path.")
        if not case.get("public_source_allowed", False):
            return Decision("SQL_PUBLIC_FIREWALL_DENY", "Check the observed client egress address and server firewall rules.")
    else:
        return Decision("SQL_DNS_LOOKUP_FAILED", "Inspect the client resolver, DNS forwarding, and logical-server FQDN.")

    if not case.get("port_1433_reachable", False):
        return Decision("SQL_TCP_1433_BLOCKED", "Check the client-to-endpoint path and the required TCP 1433 rule.")
    if case.get("connection_policy", "Default") == "Redirect" and not case.get(
        "redirect_ports_reachable", False
    ):
        return Decision(
            "SQL_REDIRECT_PORTS_BLOCKED",
            "A 1433 handshake can succeed before Redirect times out; verify the active policy and required port range.",
        )
    if not case.get("tls_hostname_valid", True):
        return Decision("SQL_TLS_NAME_MISMATCH", "Use the server FQDN and validate TLS/SNI instead of connecting by private IP.")

    mode = case.get("auth_mode", "entra")
    if mode == "entra":
        if not case.get("token_valid", False):
            return Decision("SQL_ENTRA_TOKEN_INVALID", "Confirm the workload principal and SQL token acquisition path.")
    elif mode == "sql_auth":
        if not case.get("credential_valid", False):
            return Decision("SQL_AUTHENTICATION_FAILED", "Check the approved SQL login and rotation path without logging secrets.")
    else:
        return Decision("SQL_AUTH_MODE_UNSUPPORTED", "Confirm the configured SQL authentication method.")

    if not case.get("database_principal_exists", False):
        return Decision(
            "SQL_DATABASE_PRINCIPAL_MISSING",
            "Create or map the approved database principal; an Azure resource role alone is not a SQL database user.",
        )
    if not case.get("database_permission", False):
        return Decision("SQL_DATABASE_PERMISSION_DENIED", "Check the database user's grants and target database.")
    if not case.get("database_exists", True):
        return Decision("SQL_DATABASE_NOT_FOUND", "Check server, database name, restore target, and current DNS alias.")
    return Decision("SQL_QUERY_READY", "Run an approved minimal query and validate the application transaction path.")


def plan_blob_recovery(case: dict[str, Any]) -> Decision:
    """Check a synthetic recovery request against resource scope and prerequisites."""
    scope = case.get("resource_scope", "blob")
    method = case.get("method", "blob_pitr")

    if scope == "account":
        return Decision(
            "STORAGE_ACCOUNT_RECOVERY_SEPARATE_PLAN",
            "Blob PITR does not restore an account; check the separately designed account-level protection and recovery path.",
        )
    if scope == "container" and method != "container_soft_delete":
        return Decision(
            "STORAGE_RECOVERY_SCOPE_MISMATCH",
            "Blob PITR operates on block blobs, not deleted containers; verify container soft delete and its retention window.",
        )
    if method == "container_soft_delete":
        if scope != "container":
            return Decision("STORAGE_RECOVERY_SCOPE_MISMATCH", "Container soft delete is scoped to a container.")
        if not case.get("container_soft_delete_enabled", False):
            return Decision("STORAGE_CONTAINER_RECOVERY_UNAVAILABLE", "Check whether container soft delete was enabled before deletion.")
        if not case.get("within_retention", False):
            return Decision("STORAGE_RECOVERY_POINT_OUTSIDE_RETENTION", "Confirm the actual retention interval and deletion time.")
        return Decision("STORAGE_CONTAINER_RECOVERY_CANDIDATE", "Confirm container contents and perform an approved scoped recovery.")
    if method == "blob_pitr":
        if case.get("hierarchical_namespace", False):
            return Decision("STORAGE_PITR_UNSUPPORTED_HNS", "Blob versioning is not supported for hierarchical-namespace accounts.")
        if case.get("blob_type", "block") != "block":
            return Decision("STORAGE_PITR_BLOCK_BLOB_ONLY", "Blob point-in-time restore supports block-blob operations only.")
        required = ("blob_soft_delete_enabled", "change_feed_enabled", "versioning_enabled")
        if not all(case.get(flag, False) for flag in required):
            return Decision("STORAGE_PITR_PREREQUISITES_MISSING", "Verify soft delete, change feed, and blob versioning were enabled.")
        if not case.get("within_retention", False):
            return Decision("STORAGE_RECOVERY_POINT_OUTSIDE_RETENTION", "Check the configured PITR and supporting retention windows.")
        return Decision("STORAGE_BLOB_PITR_CANDIDATE", "Review the exact blob/container scope and overwrite impact before restore.")
    if method == "version_restore":
        if case.get("hierarchical_namespace", False):
            return Decision("STORAGE_VERSIONING_UNSUPPORTED_HNS", "Use a data-protection method supported by this account type.")
        if not case.get("version_exists", False):
            return Decision("STORAGE_VERSION_NOT_FOUND", "Check version inventory and lifecycle deletion history.")
        return Decision("STORAGE_VERSION_RESTORE_CANDIDATE", "Validate the chosen version and preserve the current blob before promotion.")
    return Decision("STORAGE_RECOVERY_METHOD_UNSUPPORTED", "Match the requested recovery method to the deleted resource type.")


def plan_sql_restore(case: dict[str, Any]) -> Decision:
    """Select a documented Azure SQL Database backup restore candidate."""
    if not case.get("restore_permission", False):
        return Decision("SQL_RESTORE_PERMISSION_MISSING", "Verify the approved Azure resource scope and restore operator role.")

    method = case.get("method", "pitr")
    candidates = {
        "pitr": ("SQL_PITR_NEW_DATABASE", case.get("pitr_point_available", False)),
        "geo_restore": (
            "SQL_GEO_RESTORE_NEW_DATABASE",
            case.get("backup_redundancy") in {"GRS", "GZRS"} and case.get("geo_point_available", False),
        ),
        "ltr": ("SQL_LTR_RESTORE_NEW_DATABASE", case.get("ltr_backup_verified", False)),
    }
    if method not in candidates:
        return Decision("SQL_RESTORE_METHOD_UNSUPPORTED", "Choose PITR, geo-restore, or a verified LTR backup for this scenario.")
    outcome, available = candidates[method]
    if not available:
        if method == "pitr":
            return Decision("SQL_PITR_POINT_UNAVAILABLE", "Inspect the database's actual PITR window and recovery-point inventory.")
        if method == "geo_restore":
            return Decision("SQL_GEO_RESTORE_POINT_UNAVAILABLE", "Verify geo/GZRS backup redundancy and the latest replicated recovery point.")
        return Decision("SQL_LTR_BACKUP_UNVERIFIED", "Verify that the required long-term full backup exists and is within retention.")
    if not case.get("target_name_available", True):
        return Decision("SQL_RESTORE_TARGET_NAME_CONFLICT", "Choose a new target database name; restore does not overwrite an existing database.")
    return Decision(outcome, "Restore to a new database, validate data and dependencies, then use an approved cutover plan.")


def evaluate_case(case: dict[str, Any]) -> Decision:
    evaluators = {
        "blob_read": evaluate_blob_read,
        "sql_connect": evaluate_sql_connection,
        "blob_recovery": plan_blob_recovery,
        "sql_restore": plan_sql_restore,
    }
    mode = case.get("mode")
    if mode not in evaluators:
        raise ValueError(f"unsupported mode: {mode!r}")
    return evaluators[mode](case)


def run_fixtures() -> int:
    path = Path(__file__).parent / "fixtures" / "boundary-cases.json"
    cases = json.loads(path.read_text(encoding="utf-8"))
    failures = 0
    for case in cases:
        decision = evaluate_case(case)
        expected = case["expected"]
        passed = decision.code == expected
        print(f"{case['id']}: {'PASS' if passed else 'FAIL'} expected={expected} actual={decision.code}")
        if not passed:
            failures += 1
    print(f"Fixture cases: {len(cases)}; failed: {failures}")
    return int(failures > 0)


if __name__ == "__main__":
    raise SystemExit(run_fixtures())
