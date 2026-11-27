from __future__ import annotations

import re
import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TERRAFORM_ROOT = ROOT / "terraform" / "azure-enterprise-reference"
RUNNER = ROOT / "tools" / "verify_terraform.py"


class AzureTerraformSafetyTests(unittest.TestCase):
    def test_provider_registration_is_disabled_for_both_providers(self) -> None:
        providers = (TERRAFORM_ROOT / "versions.tf").read_text(encoding="utf-8")
        self.assertRegex(providers, r'resource_provider_registrations\s*=\s*"none"')
        self.assertRegex(providers, r'skip_provider_registration\s*=\s*true')
        self.assertNotRegex(providers, r'resource_providers_to_register\s*=')

    def test_provider_configuration_disables_interactive_cli_identity_paths(self) -> None:
        providers = (TERRAFORM_ROOT / "versions.tf").read_text(encoding="utf-8")
        for setting in ("use_cli", "use_msi", "use_aks_workload_identity"):
            self.assertRegex(providers, rf"{setting}\s*=\s*false")
        self.assertRegex(providers, r"use_oidc\s*=\s*var\.use_workload_identity")
        variables = (TERRAFORM_ROOT / "variables.tf").read_text(encoding="utf-8")
        self.assertRegex(variables, r'variable\s+"use_workload_identity"\s*\{[^}]*default\s*=\s*false')

    def test_reference_root_remote_backend_requires_oidc_and_disables_credential_fallback(self) -> None:
        source = (TERRAFORM_ROOT / "versions.tf").read_text(encoding="utf-8")
        self.assertRegex(source, r'backend\s+"azurerm"\s*\{')
        self.assertRegex(source, r"use_azuread_auth\s*=\s*true")
        self.assertRegex(source, r"use_oidc\s*=\s*true")
        self.assertRegex(source, r"use_cli\s*=\s*false")
        self.assertRegex(source, r"use_msi\s*=\s*false")

    def test_provider_versions_are_locked_to_verified_selections(self) -> None:
        requirements = (TERRAFORM_ROOT / "versions.tf").read_text(encoding="utf-8")
        lockfile = (TERRAFORM_ROOT / ".terraform.lock.hcl").read_text(encoding="utf-8")
        self.assertRegex(requirements, r'version\s*=\s*"= 5\.15\.0"')
        self.assertRegex(requirements, r'version\s*=\s*"= 2\.14\.0"')
        self.assertRegex(lockfile, r'provider "registry\.terraform\.io/hashicorp/azurerm" \{\s*version\s*=\s*"5\.15\.0"')
        self.assertRegex(lockfile, r'provider "registry\.terraform\.io/azure/azapi" \{\s*version\s*=\s*"2\.14\.0"')

    def test_azure_features_are_disabled_by_default(self) -> None:
        variables = (TERRAFORM_ROOT / "variables.tf").read_text(encoding="utf-8")
        feature_defaults = re.findall(
            r'variable\s+"enable_[^"]+"\s*\{.*?default\s*=\s*(true|false)',
            variables,
            flags=re.DOTALL,
        )
        self.assertGreaterEqual(len(feature_defaults), 9)
        self.assertTrue(all(value == "false" for value in feature_defaults))

    def test_no_resource_provider_registration_resource_exists(self) -> None:
        for tf_file in (ROOT / "terraform").rglob("*.tf"):
            source = tf_file.read_text(encoding="utf-8")
            self.assertNotRegex(source, r'resource\s+"azurerm_resource_provider_registration"')

    def test_sensitive_and_public_network_defaults_are_explicit(self) -> None:
        storage = (ROOT / "terraform" / "modules" / "storage" / "main.tf").read_text(encoding="utf-8")
        vault = (ROOT / "terraform" / "modules" / "key_vault" / "main.tf").read_text(encoding="utf-8")
        vm = (ROOT / "terraform" / "modules" / "linux_vm" / "main.tf").read_text(encoding="utf-8")
        registry = (ROOT / "terraform" / "modules" / "container_registry" / "main.tf").read_text(encoding="utf-8")
        cluster = (ROOT / "terraform" / "modules" / "aks" / "main.tf").read_text(encoding="utf-8")
        self.assertRegex(storage, r'public_network_access\s*=\s*"Disabled"')
        self.assertRegex(storage, r"shared_access_key_enabled\s*=\s*false")
        self.assertRegex(vault, r"rbac_authorization_enabled\s*=\s*true")
        self.assertRegex(vault, r"purge_protection_enabled\s*=\s*true")
        self.assertRegex(vault, r"public_network_access_enabled\s*=\s*false")
        self.assertRegex(vm, r"disable_password_authentication\s*=\s*true")
        self.assertRegex(vm, r"secure_boot_enabled\s*=\s*true")
        self.assertNotIn('resource "azurerm_public_ip"', vm)
        self.assertRegex(registry, r"admin_enabled\s*=\s*false")
        self.assertRegex(registry, r"public_network_access_enabled\s*=\s*false")
        self.assertRegex(cluster, r"private_cluster_enabled\s*=\s*true")

    def test_root_uses_an_existing_resource_group_and_audit_only_policy(self) -> None:
        root_main = (TERRAFORM_ROOT / "main.tf").read_text(encoding="utf-8")
        self.assertNotRegex(root_main, r'resource\s+"azurerm_resource_group"')
        self.assertRegex(root_main, r'enforcementMode\s*=\s*"DoNotEnforce"')

    def test_every_terraform_test_run_is_plan_only(self) -> None:
        test_files = [
            path
            for path in ROOT.rglob("*.tftest.hcl")
            if not {".terraform", "build", "dist", "__pycache__"} & set(path.relative_to(ROOT).parts)
        ]
        self.assertTrue(test_files)
        for test_file in test_files:
            source = test_file.read_text(encoding="utf-8")
            runs = re.split(r'(?=^run\s+"[^\"]+"\s*\{)', source, flags=re.MULTILINE)
            run_blocks = [block for block in runs if re.match(r'^run\s+"[^\"]+"\s*\{', block)]
            self.assertTrue(run_blocks, test_file)
            for block in run_blocks:
                self.assertRegex(block, r"(?m)^\s*command\s*=\s*plan\s*$", test_file)
                self.assertNotRegex(block, r"(?m)^\s*command\s*=\s*(apply|destroy)\s*$", test_file)

    def test_cost_guard_has_project_ceiling_planning_line_and_contingency(self) -> None:
        root_main = (TERRAFORM_ROOT / "main.tf").read_text(encoding="utf-8")
        self.assertIn("<= 0.70", root_main)
        self.assertIn("+ 0.30 <= 1.00", root_main)
        self.assertIn("terraform_data.live_scope_guard", root_main)

    def test_runner_strips_azure_and_tf_override_variables(self) -> None:
        runner = RUNNER.read_text(encoding="utf-8")
        self.assertIn('upper.startswith(("ARM_", "AZURE_", "TF_"))', runner)
        self.assertIn('"ARM_USE_CLI": "false"', runner)
        self.assertIn('"ARM_USE_OIDC": "false"', runner)
        self.assertIn('"ARM_USE_MSI": "false"', runner)

    def test_runner_environment_function_removes_sensitive_overrides(self) -> None:
        spec = importlib.util.spec_from_file_location("verify_terraform", RUNNER)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        cleaned = module.sanitized_environment(
            {
                "ARM_CLIENT_SECRET": "fixture-secret",
                "AZURE_CONFIG_DIR": "fixture-config",
                "TF_VAR_target_subscription_id": "fixture-subscription",
                "TF_CLI_ARGS_apply": "-auto-approve",
                "PATH": "preserved-path",
                "SAFE_VALUE": "preserved-value",
            }
        )
        self.assertNotIn("ARM_CLIENT_SECRET", cleaned)
        self.assertNotIn("AZURE_CONFIG_DIR", cleaned)
        self.assertNotIn("TF_VAR_target_subscription_id", cleaned)
        self.assertNotIn("TF_CLI_ARGS_apply", cleaned)
        self.assertEqual(cleaned["PATH"], "preserved-path")
        self.assertEqual(cleaned["SAFE_VALUE"], "preserved-value")
        self.assertEqual(cleaned["ARM_USE_CLI"], "false")
        self.assertEqual(cleaned["ARM_USE_OIDC"], "false")
        self.assertEqual(cleaned["ARM_USE_MSI"], "false")
