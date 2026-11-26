"""Unit tests for the deterministic Azure data-boundary fixtures."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from azure_data_boundary_model import (
    evaluate_blob_read,
    evaluate_case,
    evaluate_sql_connection,
    plan_blob_recovery,
    plan_sql_restore,
)


class FixtureTests(unittest.TestCase):
    def test_every_fixture_matches_its_expected_classification(self) -> None:
        cases = json.loads((Path(__file__).parent / "fixtures" / "boundary-cases.json").read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(cases), 20)
        for case in cases:
            with self.subTest(case=case["id"]):
                self.assertEqual(evaluate_case(case).code, case["expected"])

    def test_fixture_ids_are_unique(self) -> None:
        cases = json.loads((Path(__file__).parent / "fixtures" / "boundary-cases.json").read_text(encoding="utf-8"))
        ids = [case["id"] for case in cases]
        self.assertEqual(len(ids), len(set(ids)))

    def test_unknown_mode_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            evaluate_case({"mode": "unknown"})


class BlobReadTests(unittest.TestCase):
    def setUp(self) -> None:
        self.base = {
            "private_required": True,
            "resolved_endpoint": "private",
            "private_endpoint_approved": True,
            "private_subresources": ["blob"],
            "required_subresource": "blob",
            "private_path_allowed": True,
            "token_valid": True,
            "data_role": "Storage Blob Data Reader",
            "role_effective": True,
            "object_state": "present",
        }

    def test_private_endpoint_reader_path_is_ready(self) -> None:
        self.assertEqual(evaluate_blob_read(self.base).code, "STORAGE_BLOB_READ_READY")

    def test_public_dns_does_not_satisfy_private_only_requirement(self) -> None:
        case = {**self.base, "resolved_endpoint": "public", "public_network_enabled": False}
        self.assertEqual(evaluate_blob_read(case).code, "STORAGE_DNS_PATH_MISMATCH")

    def test_private_endpoint_must_be_approved(self) -> None:
        case = {**self.base, "private_endpoint_approved": False}
        self.assertEqual(evaluate_blob_read(case).code, "STORAGE_PRIVATE_ENDPOINT_NOT_APPROVED")

    def test_blob_endpoint_does_not_replace_required_dfs_endpoint(self) -> None:
        case = {**self.base, "required_subresource": "dfs"}
        self.assertEqual(evaluate_blob_read(case).code, "STORAGE_PRIVATE_SUBRESOURCE_MISSING")

    def test_public_firewall_denial_precedes_authorization(self) -> None:
        case = {
            "resolved_endpoint": "public",
            "public_network_enabled": True,
            "firewall_default": "Deny",
            "public_source_allowed": False,
            "token_valid": False,
        }
        self.assertEqual(evaluate_blob_read(case).code, "STORAGE_PUBLIC_FIREWALL_DENY")

    def test_private_network_policy_can_block_private_endpoint_path(self) -> None:
        case = {**self.base, "private_path_allowed": False}
        self.assertEqual(evaluate_blob_read(case).code, "STORAGE_PRIVATE_PATH_BLOCKED")

    def test_management_reader_does_not_grant_blob_data_read(self) -> None:
        case = {**self.base, "data_role": "Reader"}
        self.assertEqual(evaluate_blob_read(case).code, "STORAGE_DATA_ROLE_MISSING")

    def test_role_propagation_is_a_separate_gate(self) -> None:
        case = {**self.base, "role_effective": False}
        self.assertEqual(evaluate_blob_read(case).code, "STORAGE_ROLE_PROPAGATION_PENDING")

    def test_shared_key_policy_can_reject_key_mode(self) -> None:
        case = {**self.base, "auth_mode": "shared_key", "shared_key_allowed": False}
        self.assertEqual(evaluate_blob_read(case).code, "STORAGE_SHARED_KEY_DISABLED")

    def test_valid_sas_does_not_bypass_public_network_disable(self) -> None:
        case = {
            "resolved_endpoint": "public",
            "public_network_enabled": False,
            "auth_mode": "sas",
            "sas_valid": True,
        }
        self.assertEqual(evaluate_blob_read(case).code, "STORAGE_PUBLIC_ENDPOINT_DISABLED")

    def test_http_is_rejected_when_secure_transfer_is_required(self) -> None:
        case = {**self.base, "protocol": "http"}
        self.assertEqual(evaluate_blob_read(case).code, "STORAGE_HTTPS_REQUIRED")


class SqlConnectionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.base = {
            "private_required": True,
            "resolved_endpoint": "private",
            "private_endpoint_approved": True,
            "private_path_allowed": True,
            "port_1433_reachable": True,
            "connection_policy": "Proxy",
            "tls_hostname_valid": True,
            "auth_mode": "entra",
            "token_valid": True,
            "database_principal_exists": True,
            "database_permission": True,
            "database_exists": True,
        }

    def test_complete_sql_path_is_ready(self) -> None:
        self.assertEqual(evaluate_sql_connection(self.base).code, "SQL_QUERY_READY")

    def test_sql_private_dns_mismatch_precedes_other_gates(self) -> None:
        case = {**self.base, "resolved_endpoint": "public", "public_network_enabled": False}
        self.assertEqual(evaluate_sql_connection(case).code, "SQL_DNS_PATH_MISMATCH")

    def test_redirect_can_fail_after_1433_handshake(self) -> None:
        case = {**self.base, "connection_policy": "Redirect", "redirect_ports_reachable": False}
        self.assertEqual(evaluate_sql_connection(case).code, "SQL_REDIRECT_PORTS_BLOCKED")

    def test_proxy_path_uses_port_1433_gate(self) -> None:
        case = {**self.base, "port_1433_reachable": False}
        self.assertEqual(evaluate_sql_connection(case).code, "SQL_TCP_1433_BLOCKED")

    def test_token_does_not_create_sql_database_principal(self) -> None:
        case = {**self.base, "database_principal_exists": False}
        self.assertEqual(evaluate_sql_connection(case).code, "SQL_DATABASE_PRINCIPAL_MISSING")

    def test_existing_principal_still_needs_database_permission(self) -> None:
        case = {**self.base, "database_permission": False}
        self.assertEqual(evaluate_sql_connection(case).code, "SQL_DATABASE_PERMISSION_DENIED")

    def test_tls_hostname_validation_is_independent(self) -> None:
        case = {**self.base, "tls_hostname_valid": False}
        self.assertEqual(evaluate_sql_connection(case).code, "SQL_TLS_NAME_MISMATCH")


class RecoveryTests(unittest.TestCase):
    def test_blob_pitr_needs_all_three_features(self) -> None:
        case = {
            "resource_scope": "blob",
            "method": "blob_pitr",
            "hierarchical_namespace": False,
            "blob_type": "block",
            "blob_soft_delete_enabled": True,
            "change_feed_enabled": False,
            "versioning_enabled": True,
            "within_retention": True,
        }
        self.assertEqual(plan_blob_recovery(case).code, "STORAGE_PITR_PREREQUISITES_MISSING")

    def test_blob_pitr_does_not_restore_deleted_container(self) -> None:
        self.assertEqual(
            plan_blob_recovery({"resource_scope": "container", "method": "blob_pitr"}).code,
            "STORAGE_RECOVERY_SCOPE_MISMATCH",
        )

    def test_blob_pitr_is_not_supported_for_hierarchical_namespace(self) -> None:
        self.assertEqual(
            plan_blob_recovery({"resource_scope": "blob", "method": "blob_pitr", "hierarchical_namespace": True}).code,
            "STORAGE_PITR_UNSUPPORTED_HNS",
        )

    def test_blob_pitr_only_supports_block_blobs(self) -> None:
        case = {
            "resource_scope": "blob",
            "method": "blob_pitr",
            "hierarchical_namespace": False,
            "blob_type": "append",
            "blob_soft_delete_enabled": True,
            "change_feed_enabled": True,
            "versioning_enabled": True,
            "within_retention": True,
        }
        self.assertEqual(plan_blob_recovery(case).code, "STORAGE_PITR_BLOCK_BLOB_ONLY")

    def test_blob_pitr_requires_available_time_window(self) -> None:
        case = {
            "resource_scope": "blob",
            "method": "blob_pitr",
            "hierarchical_namespace": False,
            "blob_type": "block",
            "blob_soft_delete_enabled": True,
            "change_feed_enabled": True,
            "versioning_enabled": True,
            "within_retention": False,
        }
        self.assertEqual(plan_blob_recovery(case).code, "STORAGE_RECOVERY_POINT_OUTSIDE_RETENTION")

    def test_sql_geo_restore_requires_geo_redundant_backup(self) -> None:
        case = {
            "method": "geo_restore",
            "restore_permission": True,
            "backup_redundancy": "LRS",
            "geo_point_available": True,
        }
        self.assertEqual(plan_sql_restore(case).code, "SQL_GEO_RESTORE_POINT_UNAVAILABLE")

    def test_sql_pitr_restores_to_new_database(self) -> None:
        case = {
            "method": "pitr",
            "restore_permission": True,
            "pitr_point_available": True,
            "target_name_available": True,
        }
        self.assertEqual(plan_sql_restore(case).code, "SQL_PITR_NEW_DATABASE")

    def test_sql_restore_does_not_overwrite_existing_target(self) -> None:
        case = {
            "method": "pitr",
            "restore_permission": True,
            "pitr_point_available": True,
            "target_name_available": False,
        }
        self.assertEqual(plan_sql_restore(case).code, "SQL_RESTORE_TARGET_NAME_CONFLICT")

    def test_restore_requires_authorized_operator(self) -> None:
        case = {"method": "pitr", "restore_permission": False, "pitr_point_available": True}
        self.assertEqual(plan_sql_restore(case).code, "SQL_RESTORE_PERMISSION_MISSING")


if __name__ == "__main__":
    unittest.main()
