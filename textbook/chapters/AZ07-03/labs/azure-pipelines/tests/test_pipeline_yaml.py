from __future__ import annotations

import re
import unittest
from pathlib import Path

import yaml


LAB = Path(__file__).resolve().parents[1]


class PipelineYamlTests(unittest.TestCase):
    def setUp(self):
        self.pipeline_path = LAB / "azure-pipelines.yml"
        self.pipeline = yaml.safe_load(self.pipeline_path.read_text(encoding="utf-8"))

    def test_pipeline_and_reusable_template_parse_as_yaml(self):
        template_path = LAB / "templates" / "offline-checks.yml"
        template = yaml.safe_load(template_path.read_text(encoding="utf-8"))
        self.assertEqual(self.pipeline["stages"][0]["stage"], "Validate")
        self.assertEqual(len(template["steps"]), 2)

    def test_pipeline_is_manual_and_has_no_yaml_pr_trigger(self):
        self.assertEqual(self.pipeline["trigger"], "none")
        self.assertNotIn("pr", self.pipeline)

    def test_agent_and_checkout_use_minimum_pipeline_access(self):
        self.assertEqual(self.pipeline["pool"]["name"], "CloudOps-Offline")
        job = self.pipeline["stages"][0]["jobs"][0]
        checkout = job["steps"][0]["checkout"]
        self.assertEqual(checkout, "self")
        self.assertFalse(job["steps"][0]["persistCredentials"])

    def test_current_yaml_does_not_authenticate_or_mutate_azure(self):
        source = self.pipeline_path.read_text(encoding="utf-8").lower()
        for forbidden in ("azurecli@2", "terraform apply", "terraform destroy", "az login", "addspntoenvironment"):
            self.assertNotIn(forbidden, source)

    def test_reusable_template_is_referenced_and_exists(self):
        job = self.pipeline["stages"][0]["jobs"][0]
        template_steps = [step["template"] for step in job["steps"] if "template" in step]
        self.assertEqual(template_steps, ["templates/offline-checks.yml"])
        self.assertTrue((LAB / template_steps[0]).is_file())

    def test_enterprise_cloud_stages_are_disabled_by_default_and_compile_time_gated(self):
        path = LAB / "enterprise-pipeline.yml"
        enterprise = yaml.safe_load(path.read_text(encoding="utf-8"))
        parameters = {entry["name"]: entry for entry in enterprise["parameters"]}
        self.assertIs(parameters["enableCloudDelivery"]["default"], False)
        self.assertEqual(enterprise["trigger"], "none")
        conditional = [stage for stage in enterprise["stages"] if isinstance(stage, dict) and any("${{ if" in str(key) for key in stage)]
        self.assertEqual(len(conditional), 1)
        self.assertEqual(conditional[0]["${{ if eq(parameters.enableCloudDelivery, true) }}"][0]["template"], "templates/enterprise-delivery.yml")

    def test_enterprise_flow_has_plan_review_apply_order_and_protected_resources(self):
        path = LAB / "templates" / "enterprise-delivery.yml"
        delivery = yaml.safe_load(path.read_text(encoding="utf-8"))
        stages = delivery["stages"]
        self.assertEqual([stage["stage"] for stage in stages], ["Plan", "PlanReview", "Apply"])
        self.assertEqual(stages[0]["dependsOn"], "Validate")
        self.assertEqual(stages[1]["dependsOn"], "Plan")
        self.assertEqual(stages[2]["dependsOn"], "PlanReview")
        self.assertEqual(stages[2]["lockBehavior"], "sequential")
        self.assertEqual(stages[1]["jobs"][0]["deployment"], "ReviewPlan")
        self.assertEqual(stages[2]["jobs"][0]["deployment"], "ControlledApply")
        self.assertEqual(stages[1]["jobs"][0]["pool"]["name"], "${{ parameters.reviewAgentPool }}")
        self.assertIn("${{ parameters.planEnvironment }}", str(stages[1]["jobs"][0]["environment"]))
        self.assertIn("${{ parameters.applyEnvironment }}", str(stages[2]["jobs"][0]["environment"]))
        self.assertIn("${{ parameters.planVariableGroup }}", str(stages[0]["variables"]))
        self.assertIn("${{ parameters.applyVariableGroup }}", str(stages[2]["variables"]))

    def test_enterprise_flow_binds_service_connections_and_current_run_artifact(self):
        text = (LAB / "templates" / "enterprise-delivery.yml").read_text(encoding="utf-8")
        self.assertIn("azureSubscription: ${{ parameters.planServiceConnection }}", text)
        self.assertIn("azureSubscription: ${{ parameters.applyServiceConnection }}", text)
        self.assertIn("addSpnToEnvironment: true", text)
        self.assertIn("SYSTEM_OIDCREQUESTURI: $(System.OidcRequestUri)", text)
        self.assertIn("ARM_OIDC_AZURE_SERVICE_CONNECTION_ID", text)
        self.assertIn("PublishPipelineArtifact@1", text)
        self.assertGreaterEqual(text.count("download: current\n                  artifact: terraform-plan"), 2)
        self.assertIn("--backend-config", text)
        self.assertIn("plan_bundle.py\" create", text)
        self.assertIn("plan_bundle.py\" verify", text)
        self.assertIn("cloudops-approval-broker fetch", text)
        self.assertIn("controlled_apply.py", text)
        self.assertIn("TRUST_STORE_SHA256", text)
        self.assertIn("CONTROL_ROOT", text)
        self.assertIn("TARGET_SUBSCRIPTION_ID", text)
        self.assertIn("TARGET_RESOURCE_GROUP", text)
        self.assertGreaterEqual(text.count('v != "1.15.5"'), 3)
        self.assertIn("init -backend=false", text)
        self.assertIsNone(re.search(r"(?:^|\s)terraform\s+(?:apply|destroy)(?:\s|$)", text, re.IGNORECASE | re.MULTILINE))

        apply_template = yaml.safe_load((LAB / "templates" / "enterprise-delivery.yml").read_text(encoding="utf-8"))
        apply = next(stage for stage in apply_template["stages"] if stage["stage"] == "Apply")
        steps = apply["jobs"][0]["strategy"]["runOnce"]["deploy"]["steps"]
        preflight_index = next(i for i, step in enumerate(steps) if step.get("displayName") == "Verify the artifact and scope before requesting an Azure identity")
        identity_index = next(i for i, step in enumerate(steps) if step.get("task") == "AzureCLI@2")
        self.assertLess(preflight_index, identity_index)
        self.assertEqual(steps[0]["download"], "none")

    def test_enterprise_yaml_is_not_mistaken_for_an_azure_devops_server_run(self):
        path = LAB / "enterprise-pipeline.yml"
        text = path.read_text(encoding="utf-8")
        parsed = yaml.safe_load(text)
        self.assertIn("stages", parsed)
        self.assertNotIn("pr", parsed)
        self.assertIn("not been uploaded, compiled or run", text)
        offline_source = self.pipeline_path.read_text(encoding="utf-8").lower()
        self.assertNotIn("azurecli@2", offline_source)
        self.assertNotIn("enterprise-delivery.yml", offline_source)


if __name__ == "__main__":
    unittest.main()
