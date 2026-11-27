from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from plan_bundle import BundleError, create_bundle, summarize_plan, verify_bundle


COMMIT = "a" * 40
RUN_ID = "local-run-203"
SUBSCRIPTION = "11111111-1111-1111-1111-111111111111"
RESOURCE_GROUP = "rg-azure-cloudops-test"
SENSITIVE_SENTINEL = "do-not-print-this-sensitive-output"


class PlanBundleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name)
        self.repository = self.base / "repo"
        self.terraform_root = self.repository / "textbook" / "terraform"
        self.terraform_root.mkdir(parents=True)
        self.lock = self.terraform_root / ".terraform.lock.hcl"
        self.lock.write_text('provider "hashicorp/azurerm" { version = "5.0.0" }\n', encoding="utf-8")
        self.backend = self.base / "protected" / "production.tfbackend"
        self.backend.parent.mkdir()
        self.backend.write_text('key = "production.tfstate"\n', encoding="utf-8")
        self.bundle = self.base / "workspace" / "terraform-plan"
        self.bundle.mkdir(parents=True)
        self.plan = self.bundle / "approved.tfplan"
        self.plan.write_bytes(b"SYNTHETIC PLAN BYTES - NOT A TERRAFORM PLAN")
        self.plan_json = {
            "format_version": "1.2",
            "applyable": True,
            "complete": True,
            "errored": False,
            "variables": {
                "target_subscription_id": {"value": SUBSCRIPTION},
                "target_resource_group_name": {"value": RESOURCE_GROUP},
            },
            "resource_changes": [
                {
                    "address": "azurerm_key_vault.example",
                    "type": "azurerm_key_vault",
                    "change": {"actions": ["create"], "after": {"secret": SENSITIVE_SENTINEL}},
                }
            ],
        }

    def tearDown(self):
        self.temp.cleanup()

    def create(self):
        return create_bundle(
            repository=self.repository,
            terraform_root=self.terraform_root,
            lock_file=self.lock,
            backend_config=self.backend,
            plan_path=self.plan,
            output_dir=self.bundle,
            source_git_sha=COMMIT,
            run_id=RUN_ID,
            target_environment="production",
            subscription_id=SUBSCRIPTION,
            resource_group=RESOURCE_GROUP,
            plan_json_loader=lambda _plan, _root: self.plan_json,
        )

    def verify(self, **overrides):
        args = {
            "repository": self.repository,
            "terraform_root": self.terraform_root,
            "lock_file": self.lock,
            "backend_config": self.backend,
            "bundle_dir": self.bundle,
            "expected_source_git_sha": COMMIT,
            "expected_run_id": RUN_ID,
            "expected_target_environment": "production",
            "expected_subscription_id": SUBSCRIPTION,
            "expected_resource_group": RESOURCE_GROUP,
            "plan_json_loader": lambda _plan, _root: self.plan_json,
        }
        args.update(overrides)
        return verify_bundle(**args)

    def test_creates_redacted_bundle_bound_to_source_scope_backend_lock_and_run(self):
        manifest = self.create()
        self.assertEqual(manifest["source_git_sha"], COMMIT)
        self.assertEqual(manifest["run_id"], RUN_ID)
        self.assertEqual(manifest["operation"], "terraform-apply")
        self.assertEqual(manifest["backend_config_sha256"], hashlib.sha256(self.backend.read_bytes()).hexdigest())
        self.assertEqual(self.verify(), manifest)
        summary = (self.bundle / "review-summary.json").read_text(encoding="utf-8")
        self.assertNotIn(SENSITIVE_SENTINEL, summary)
        self.assertNotIn(SENSITIVE_SENTINEL, (self.bundle / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual({path.name for path in self.bundle.iterdir()}, {"approved.tfplan", "manifest.json", "review-summary.json"})
        self.assertNotIn(self.bundle, self.repository.parents)

    def test_wrong_plan_scope_is_rejected_when_creating_or_verifying(self):
        self.plan_json["variables"]["target_resource_group_name"]["value"] = "rg-other"
        with self.assertRaisesRegex(BundleError, "resource group"):
            self.create()
        self.plan_json["variables"]["target_resource_group_name"]["value"] = RESOURCE_GROUP
        self.create()
        with self.assertRaisesRegex(BundleError, "resource_group"):
            self.verify(expected_resource_group="rg-other")

    def test_backend_lock_plan_and_run_changes_are_rejected(self):
        self.create()
        self.backend.write_text('key = "different.tfstate"\n', encoding="utf-8")
        with self.assertRaisesRegex(BundleError, "backend target"):
            self.verify()
        self.backend.write_text('key = "production.tfstate"\n', encoding="utf-8")
        self.lock.write_text("provider lock changed\n", encoding="utf-8")
        with self.assertRaisesRegex(BundleError, "provider lock"):
            self.verify()
        self.lock.write_text('provider "hashicorp/azurerm" { version = "5.0.0" }\n', encoding="utf-8")
        self.plan.write_bytes(b"modified")
        with self.assertRaisesRegex(BundleError, "saved plan changed"):
            self.verify()
        with self.assertRaisesRegex(BundleError, "run_id"):
            self.verify(expected_run_id="different-run")

    def test_unsupported_action_sequences_and_nonspecific_json_are_rejected(self):
        for action in (["create", "create"], ["forget"], ["update", "delete"], []):
            candidate = dict(self.plan_json)
            candidate["resource_changes"] = [
                {"address": "x", "type": "azurerm_test", "change": {"actions": action}}
            ]
            with self.subTest(action=action), self.assertRaises(BundleError):
                summarize_plan(candidate)

    def test_replacement_is_classified_as_destructive(self):
        self.plan_json["resource_changes"][0]["change"]["actions"] = ["delete", "create"]
        summary = summarize_plan(self.plan_json)
        self.assertTrue(summary["requires_destructive_approval"])
        self.assertEqual(summary["action_count"], 2)

    def test_output_changes_show_names_and_actions_without_values(self):
        self.plan_json["output_changes"] = {
            "connection_string": {"actions": ["update"], "after": SENSITIVE_SENTINEL}
        }
        summary = summarize_plan(self.plan_json)
        self.assertEqual(summary["output_change_count"], 1)
        self.assertEqual(summary["output_changes"], [{"name": "connection_string", "actions": ["update"]}])
        self.assertNotIn(SENSITIVE_SENTINEL, json.dumps(summary))
        self.plan_json["output_changes"]["connection_string"]["actions"] = ["update", {"x": 1}]
        with self.assertRaisesRegex(BundleError, "output action"):
            summarize_plan(self.plan_json)

    def test_bundle_and_backend_must_remain_outside_repository(self):
        inside_backend = self.terraform_root / "backend.tfbackend"
        inside_backend.write_text('key = "local.tfstate"\n', encoding="utf-8")
        with self.assertRaisesRegex(BundleError, "outside the repository"):
            create_bundle(
                repository=self.repository,
                terraform_root=self.terraform_root,
                lock_file=self.lock,
                backend_config=inside_backend,
                plan_path=self.plan,
                output_dir=self.bundle,
                source_git_sha=COMMIT,
                run_id=RUN_ID,
                target_environment="production",
                subscription_id=SUBSCRIPTION,
                resource_group=RESOURCE_GROUP,
                plan_json_loader=lambda _plan, _root: self.plan_json,
            )

    def test_duplicate_json_properties_are_rejected(self):
        manifest = self.base / "duplicate.json"
        manifest.write_text('{"x": 1, "x": 2}', encoding="utf-8")
        from plan_bundle import _read_json

        with self.assertRaisesRegex(BundleError, "duplicate"):
            _read_json(manifest, "fixture", 1024)


if __name__ == "__main__":
    unittest.main()
