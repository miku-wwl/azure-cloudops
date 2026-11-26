from __future__ import annotations

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


if __name__ == "__main__":
    unittest.main()
