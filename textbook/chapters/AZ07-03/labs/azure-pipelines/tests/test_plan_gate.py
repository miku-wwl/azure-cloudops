from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from plan_gate import ContractError, verify_contract


NOW = datetime(2026, 11, 27, 0, 0, tzinfo=timezone.utc)
COMMIT = "a" * 40
TARGET = "fixture://tenant-lab/subscription-lab/rg-lab/state/prod.tfstate"


class PlanGateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.plan = self.root / "plan.tfplan"
        self.lock = self.root / ".terraform.lock.hcl"
        self.manifest_path = self.root / "manifest.json"
        self.approval_path = self.root / "approval.json"
        self.plan.write_bytes(b"SYNTHETIC PLAN BYTES - NOT A TERRAFORM PLAN")
        self.lock.write_text('provider "hashicorp/azurerm" { version = "5.0.0" }\n', encoding="utf-8")
        self.manifest = {
            "schema_version": 1,
            "run_id": "run-local-17",
            "source_commit": COMMIT,
            "target_scope": TARGET,
            "provider_lock_sha256": self.digest(self.lock),
            "plan_sha256": self.digest(self.plan),
            "created_utc": "2026-11-26T23:00:00Z",
            "expires_utc": "2026-11-27T03:00:00Z",
            "created_by": "planner-fixture",
        }
        self.approval = {
            "schema_version": 1,
            "run_id": "run-local-17",
            "source_commit": COMMIT,
            "target_scope": TARGET,
            "provider_lock_sha256": self.digest(self.lock),
            "plan_sha256": self.digest(self.plan),
            "approved_by": "reviewer-fixture",
            "approved_utc": "2026-11-26T23:30:00Z",
            "expires_utc": "2026-11-27T03:00:00Z",
        }
        self.write_contracts()

    def tearDown(self):
        self.temp.cleanup()

    @staticmethod
    def digest(path: Path) -> str:
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def write_contracts(self):
        self.manifest_path.write_text(json.dumps(self.manifest), encoding="utf-8")
        self.approval_path.write_text(json.dumps(self.approval), encoding="utf-8")

    def verify(self, *, commit=COMMIT, target=TARGET):
        verify_contract(
            plan_path=self.plan,
            manifest_path=self.manifest_path,
            approval_path=self.approval_path,
            lock_path=self.lock,
            expected_commit=commit,
            expected_target=target,
            now=NOW,
        )

    def test_approved_unchanged_contract_passes(self):
        self.verify()

    def test_plan_tampering_fails(self):
        self.plan.write_bytes(self.plan.read_bytes() + b"tampered")
        with self.assertRaisesRegex(ContractError, "plan bytes"):
            self.verify()

    def test_wrong_source_commit_fails(self):
        with self.assertRaisesRegex(ContractError, "source commit"):
            self.verify(commit="b" * 40)

    def test_manifest_wrong_scope_fails(self):
        self.manifest["target_scope"] = "fixture://other-target"
        self.write_contracts()
        with self.assertRaisesRegex(ContractError, "target scope"):
            self.verify()

    def test_wrong_provider_lock_fails(self):
        self.lock.write_text("provider lock changed\n", encoding="utf-8")
        with self.assertRaisesRegex(ContractError, "provider lock"):
            self.verify()

    def test_expired_plan_fails(self):
        self.manifest["created_utc"] = "2026-11-26T18:00:00Z"
        self.manifest["expires_utc"] = "2026-11-26T22:00:00Z"
        self.approval["approved_utc"] = "2026-11-26T19:00:00Z"
        self.approval["expires_utc"] = "2026-11-26T22:00:00Z"
        self.write_contracts()
        with self.assertRaisesRegex(ContractError, "expired"):
            self.verify()

    def test_approval_for_another_plan_fails(self):
        self.approval["plan_sha256"] = "0" * 64
        self.write_contracts()
        with self.assertRaisesRegex(ContractError, "plan bytes"):
            self.verify()

    def test_approval_for_another_run_fails(self):
        self.approval["run_id"] = "run-local-18"
        self.write_contracts()
        with self.assertRaisesRegex(ContractError, "different pipeline run"):
            self.verify()

    def test_plan_creator_cannot_approve(self):
        self.approval["approved_by"] = self.manifest["created_by"]
        self.write_contracts()
        with self.assertRaisesRegex(ContractError, "cannot approve"):
            self.verify()

    def test_timezone_is_required(self):
        self.manifest["created_utc"] = "2026-11-26T23:00:00"
        self.write_contracts()
        with self.assertRaisesRegex(ContractError, "include a timezone"):
            self.verify()

    def test_long_validity_window_fails(self):
        self.manifest["expires_utc"] = "2026-11-27T05:00:01Z"
        self.approval["expires_utc"] = self.manifest["expires_utc"]
        self.write_contracts()
        with self.assertRaisesRegex(ContractError, "no longer than four hours"):
            self.verify()

    def test_future_approval_fails(self):
        self.approval["approved_utc"] = "2026-11-27T00:01:00Z"
        self.write_contracts()
        with self.assertRaisesRegex(ContractError, "future-dated"):
            self.verify()


if __name__ == "__main__":
    unittest.main()
