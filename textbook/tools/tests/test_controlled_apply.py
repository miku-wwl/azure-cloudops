from __future__ import annotations

import base64
import importlib.util
import json
import tempfile
import sys
import threading
import unittest
import uuid
from unittest.mock import patch
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey


REPOSITORY = Path(__file__).resolve().parents[3]
TEXTBOOK = REPOSITORY / "textbook"
TOOLS = TEXTBOOK / "tools"
TERRAFORM_ROOT = TEXTBOOK / "terraform" / "azure-enterprise-reference"
BACKEND_ROOT = TEXTBOOK / "terraform" / "azure-remote-state-backend"
SPEC = importlib.util.spec_from_file_location("controlled_apply", TOOLS / "controlled_apply.py")
assert SPEC and SPEC.loader
controlled_apply = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = controlled_apply
SPEC.loader.exec_module(controlled_apply)


class ControlledApplyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="azure-cloudops-approval-")
        self.external = Path(self.temp.name)
        self.artifacts = self.external / "artifacts"
        self.artifacts.mkdir()
        self.plan_path = self.artifacts / "approved.tfplan"
        self.plan_path.write_bytes(b"synthetic sensitive binary plan\x00\x01")
        self.approval_path = self.artifacts / "approval-envelope.json"
        self.trust_path = self.artifacts / "trusted-approvers.json"
        self.control_root = self.external / "control"
        work_dir = REPOSITORY / "work"
        work_dir.mkdir(exist_ok=True)
        self.lock_temp = tempfile.TemporaryDirectory(
            prefix="controlled-apply-lock-", dir=work_dir
        )
        self.terraform_root = Path(self.lock_temp.name)
        self.lock_file = self.terraform_root / ".terraform.lock.hcl"
        self.lock_file.write_text('provider "example" { version = "1.0.0" }\n', encoding="utf-8")
        self.key = Ed25519PrivateKey.generate()
        public = self.key.public_key().public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )
        self.trust = {
            "schema_version": 1,
            "signers": [
                {
                    "key_id": "test-approver-2026",
                    "public_key_b64": base64.b64encode(public).decode("ascii"),
                    "identities": ["platform.approver@example.test"],
                    "environments": ["test"],
                    "subscription_ids": ["11111111-1111-4111-8111-111111111111"],
                    "resource_groups": ["rg-cloudops-test"],
                    "operations": [
                        controlled_apply.SAFE_OPERATION,
                        controlled_apply.DESTRUCTIVE_OPERATION,
                    ],
                }
            ],
        }
        self.write_trust()
        self.scope = controlled_apply.Scope(
            source_git_sha="a" * 40,
            target_environment="test",
            subscription_id="11111111-1111-4111-8111-111111111111",
            resource_group="rg-cloudops-test",
            provider_lock_sha256=controlled_apply.sha256_file(self.lock_file),
            run_id="ado-run-8451",
        )
        self.plan_json = {
            "format_version": "1.2",
            "applyable": True,
            "complete": True,
            "errored": False,
            "variables": {
                "target_subscription_id": {"value": self.scope.subscription_id},
                "target_resource_group_name": {"value": self.scope.resource_group},
            },
            "resource_changes": [
                {"address": "azurerm_example.sample", "change": {"actions": ["create"]}}
            ]
        }
        self.payload = self.new_payload()
        self.write_approval()

    def tearDown(self) -> None:
        self.lock_temp.cleanup()
        self.temp.cleanup()

    def write_trust(self) -> None:
        self.trust_path.write_text(
            json.dumps(self.trust, sort_keys=True, separators=(",", ":")),
            encoding="utf-8",
        )

    def new_payload(self) -> dict[str, object]:
        now = datetime.now(timezone.utc)
        return {
            "schema_version": 1,
            "approval_id": str(uuid.uuid4()),
            "nonce": str(uuid.uuid4()),
            "key_id": "test-approver-2026",
            "approver_identity": "platform.approver@example.test",
            "approved_at": (now - timedelta(minutes=1)).isoformat().replace("+00:00", "Z"),
            "expires_at": (now + timedelta(minutes=12)).isoformat().replace("+00:00", "Z"),
            "source_git_sha": self.scope.source_git_sha,
            "target_environment": self.scope.target_environment,
            "subscription_id": self.scope.subscription_id,
            "resource_group": self.scope.resource_group,
            "provider_lock_sha256": self.scope.provider_lock_sha256,
            "plan_sha256": controlled_apply.sha256_file(self.plan_path),
            "operation": controlled_apply.SAFE_OPERATION,
            "run_id": self.scope.run_id,
        }

    def write_approval(self) -> None:
        signature = self.key.sign(controlled_apply.canonical_json(self.payload))
        envelope = {
            "payload": self.payload,
            "signature_b64": base64.b64encode(signature).decode("ascii"),
        }
        self.approval_path.write_text(
            json.dumps(envelope, sort_keys=True, separators=(",", ":")),
            encoding="utf-8",
        )

    def run_gate(self, apply=None):
        return controlled_apply.execute_controlled_apply(
            repository=REPOSITORY,
            terraform_root=self.terraform_root,
            plan_path=self.plan_path,
            approval_path=self.approval_path,
            trust_store_path=self.trust_path,
            trust_store_sha256=controlled_apply.sha256_file(self.trust_path),
            lock_file=self.lock_file,
            control_root=self.control_root,
            scope=self.scope,
            plan_loader=lambda sealed: self.plan_json,
            apply_executor=apply or (lambda _plan: 0),
        )

    def assert_rejected(self, pattern: str, *, apply=None) -> None:
        called = False

        def record(plan: Path) -> int:
            nonlocal called
            called = True
            return apply(plan) if apply else 0

        with self.assertRaisesRegex(controlled_apply.ApprovalError, pattern):
            self.run_gate(record)
        self.assertFalse(called, "the apply callback must not run after a rejected authorization")

    def test_accepted_signed_approval_applies_only_the_sealed_exact_plan(self) -> None:
        seen: list[tuple[Path, bytes]] = []

        def apply(plan: Path) -> int:
            seen.append((plan, plan.read_bytes()))
            return 0

        authorization, result = self.run_gate(apply)
        self.assertEqual(result, 0)
        self.assertEqual(authorization.operation, controlled_apply.SAFE_OPERATION)
        self.assertEqual(authorization.plan_sha256, controlled_apply.sha256_file(self.plan_path))
        self.assertEqual(seen[0][1], self.plan_path.read_bytes())
        self.assertFalse(seen[0][0].exists(), "sealed sensitive plan should be removed after apply")
        self.assertFalse((self.control_root / "active-locks" / "unused").exists())

    def test_missing_approval_is_rejected(self) -> None:
        self.approval_path.unlink()
        self.assert_rejected("approval envelope")

    def test_missing_plan_is_rejected(self) -> None:
        self.plan_path.unlink()
        with self.assertRaises(controlled_apply.ApprovalError):
            self.run_gate()

    def test_missing_trusted_keys_are_rejected(self) -> None:
        self.trust_path.unlink()
        with self.assertRaises(controlled_apply.ApprovalError):
            self.run_gate()

    def test_missing_provider_lock_is_rejected(self) -> None:
        self.lock_file.unlink()
        self.assert_rejected("provider lock file")

    def test_expired_approval_is_rejected(self) -> None:
        now = datetime.now(timezone.utc)
        self.payload["approved_at"] = (now - timedelta(minutes=12)).isoformat().replace("+00:00", "Z")
        self.payload["expires_at"] = (now - timedelta(minutes=2)).isoformat().replace("+00:00", "Z")
        self.write_approval()
        self.assert_rejected("expired")

    def test_altered_plan_artifact_is_rejected(self) -> None:
        self.plan_path.write_bytes(self.plan_path.read_bytes() + b"tampered")
        self.assert_rejected("changed after approval")

    def test_changed_git_sha_is_rejected(self) -> None:
        self.payload["source_git_sha"] = "b" * 40
        self.write_approval()
        self.assert_rejected("Git SHA")

    def test_wrong_resource_group_is_rejected(self) -> None:
        self.payload["resource_group"] = "rg-other"
        self.write_approval()
        self.assert_rejected("resource group")

    def test_wrong_subscription_is_rejected(self) -> None:
        self.payload["subscription_id"] = "22222222-2222-4222-8222-222222222222"
        self.write_approval()
        self.assert_rejected("subscription")

    def test_plan_target_subscription_must_match_the_signed_scope(self) -> None:
        self.plan_json["variables"]["target_subscription_id"]["value"] = "22222222-2222-4222-8222-222222222222"
        self.assert_rejected("plan target_subscription_id")

    def test_plan_target_resource_group_must_match_the_signed_scope(self) -> None:
        self.plan_json["variables"]["target_resource_group_name"]["value"] = "rg-other"
        self.assert_rejected("plan target_resource_group_name")

    def test_unapplyable_or_errored_plan_is_rejected(self) -> None:
        self.plan_json["applyable"] = False
        self.assert_rejected("not applyable")

    def test_incomplete_plan_is_rejected(self) -> None:
        self.plan_json["complete"] = False
        self.assert_rejected("incomplete")

    def test_wrong_environment_is_rejected(self) -> None:
        self.payload["target_environment"] = "production"
        self.write_approval()
        self.assert_rejected("environment")

    def test_changed_provider_lock_is_rejected(self) -> None:
        self.lock_file.write_text('provider "example" { version = "2.0.0" }\n', encoding="utf-8")
        self.assert_rejected("lock file changed")

    def test_unauthorized_identity_is_rejected_after_signature_verification(self) -> None:
        self.payload["approver_identity"] = "unlisted@example.test"
        self.write_approval()
        self.assert_rejected("identity is not authorized")

    def test_tampered_approval_payload_is_rejected_by_signature(self) -> None:
        envelope = json.loads(self.approval_path.read_text(encoding="utf-8"))
        envelope["payload"]["target_environment"] = "production"
        self.approval_path.write_text(json.dumps(envelope), encoding="utf-8")
        self.assert_rejected("signature is invalid")

    def test_trust_store_digest_must_match_protected_pipeline_digest(self) -> None:
        with self.assertRaisesRegex(controlled_apply.ApprovalError, "protected digest"):
            controlled_apply.verify_approval(
                approval_path=self.approval_path,
                trust_store_path=self.trust_path,
                trust_store_sha256="0" * 64,
                plan_sha256=controlled_apply.sha256_file(self.plan_path),
                plan_json=self.plan_json,
                scope=self.scope,
            )

    def test_wrong_run_id_is_rejected_to_prevent_cross_run_replay(self) -> None:
        self.payload["run_id"] = "ado-run-other"
        self.write_approval()
        self.assert_rejected("run ID")

    def test_replayed_approval_nonce_is_rejected(self) -> None:
        calls = 0

        def apply(_plan: Path) -> int:
            nonlocal calls
            calls += 1
            return 0

        self.run_gate(apply)
        self.assert_rejected("already been consumed", apply=apply)
        self.assertEqual(calls, 1)

    def test_concurrent_execution_for_same_scope_is_rejected(self) -> None:
        entered = threading.Event()
        release = threading.Event()
        first_result: list[object] = []

        def blocking_apply(_plan: Path) -> int:
            entered.set()
            if not release.wait(timeout=10):
                raise AssertionError("test release event was not set")
            return 0

        def first_worker() -> None:
            try:
                first_result.append(self.run_gate(blocking_apply))
            except Exception as exc:  # collected for assertion in the parent thread
                first_result.append(exc)

        worker = threading.Thread(target=first_worker)
        worker.start()
        self.assertTrue(entered.wait(timeout=5), "first Terraform operation did not enter apply")
        try:
            self.assert_rejected("holds this target scope")
        finally:
            release.set()
            worker.join(timeout=10)
        self.assertFalse(worker.is_alive())
        self.assertEqual(len(first_result), 1)
        self.assertNotIsInstance(first_result[0], Exception)

    def test_apply_failure_still_consumes_the_approval_nonce(self) -> None:
        self.assertEqual(self.run_gate(lambda _plan: 1)[1], 1)
        self.assert_rejected("already been consumed")

    def test_unapproved_destructive_actions_are_rejected(self) -> None:
        self.plan_json["resource_changes"][0]["change"]["actions"] = ["delete", "create"]
        self.write_approval()
        self.assert_rejected("operation does not authorize")

    def test_explicitly_authorized_delete_requires_a_distinct_operation(self) -> None:
        self.plan_json["resource_changes"][0]["change"]["actions"] = ["delete"]
        self.payload["operation"] = controlled_apply.DESTRUCTIVE_OPERATION
        self.write_approval()
        authorization, result = self.run_gate()
        self.assertEqual(result, 0)
        self.assertTrue(authorization.destructive)
        self.assertEqual(authorization.operation, controlled_apply.DESTRUCTIVE_OPERATION)

    def test_unsupported_state_actions_are_rejected(self) -> None:
        self.plan_json["resource_changes"][0]["change"]["actions"] = ["forget"]
        self.assert_rejected("unsupported or unknown")

    def test_trusted_backend_is_conditional_oidc_and_does_not_initialize(self) -> None:
        source = (BACKEND_ROOT / "terraform.tf").read_text(encoding="utf-8")
        sample = (BACKEND_ROOT / "backend.example.hcl").read_text(encoding="utf-8")
        self.assertIn('backend "azurerm"', source)
        self.assertRegex(source, r"use_oidc\s*=\s*true")
        self.assertRegex(source, r"use_azuread_auth\s*=\s*true")
        self.assertRegex(source, r"use_cli\s*=\s*false")
        self.assertRegex(source, r"use_msi\s*=\s*false")
        self.assertIn("REPLACE_WITH_EXISTING_STATE_RESOURCE_GROUP", sample)
        self.assertIn("NOT_RUN", (BACKEND_ROOT / "README.md").read_text(encoding="utf-8"))

    def test_terraform_apply_rejects_long_lived_credentials_before_start(self) -> None:
        with patch.dict(
            controlled_apply.os.environ,
            {
                "ARM_CLIENT_SECRET": "test-only-secret",
                "ARM_CLIENT_ID": "test-client",
                "ARM_TENANT_ID": "test-tenant",
            },
            clear=True,
        ):
            with self.assertRaisesRegex(controlled_apply.ApprovalError, "long-lived Azure credentials"):
                controlled_apply.terraform_apply(
                    "terraform",
                    self.terraform_root,
                    self.plan_path,
                    10,
                )

    def test_terraform_apply_requires_the_ado_federated_service_connection(self) -> None:
        with patch.dict(
            controlled_apply.os.environ,
            {"ARM_CLIENT_ID": "test-client", "ARM_TENANT_ID": "test-tenant"},
            clear=True,
        ):
            with self.assertRaisesRegex(controlled_apply.ApprovalError, "Service Connection"):
                controlled_apply.terraform_apply(
                    "terraform",
                    self.terraform_root,
                    self.plan_path,
                    10,
                )


if __name__ == "__main__":
    unittest.main()
