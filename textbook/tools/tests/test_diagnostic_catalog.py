from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


CATALOG = Path(__file__).parents[1] / "diagnostic_catalog.json"
REQUIRED = {
    "dns", "routes", "tcp_tls", "nsg", "private_endpoint", "identity",
    "token_audience", "rbac", "key_vault", "azure_policy",
    "kubernetes_image_pull", "application_health", "monitoring",
}
MUTATION_VERBS = re.compile(r"(?:^|\s)(create|delete|update|assign|apply|destroy|enable|disable|set)(?:\s|$)", re.IGNORECASE)


class DiagnosticCatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
        cls.rows = {item["id"]: item for item in cls.catalog["diagnostics"]}

    def test_all_required_categories_have_purpose_inputs_and_interpretation(self) -> None:
        self.assertEqual(set(self.rows), REQUIRED)
        for item in self.rows.values():
            with self.subTest(diagnostic=item["id"]):
                self.assertTrue(item["purpose"])
                self.assertTrue(item["required_inputs"])
                self.assertTrue(item["commands"])
                self.assertTrue(item["interpretation"])
                self.assertTrue(item["verification"])

    def test_catalog_marks_all_service_observations_unrun(self) -> None:
        self.assertEqual(self.catalog["status"], "DOCUMENTED_NOT_RUN")
        self.assertIn("default subscription", self.catalog["scope_contract"])
        self.assertIn("Do not change the default subscription", self.catalog["scope_contract"])

    def test_command_examples_contain_no_mutation_verbs(self) -> None:
        for item in self.rows.values():
            for command in item["commands"]:
                with self.subTest(diagnostic=item["id"], command=command):
                    self.assertIsNone(MUTATION_VERBS.search(command))

    def test_network_and_token_tools_are_referenced_for_their_categories(self) -> None:
        self.assertIn("network_probe.py", " ".join(self.rows["tcp_tls"]["commands"]))
        self.assertIn("network_probe.py", " ".join(self.rows["application_health"]["commands"]))
        self.assertIn("token_audience.py", " ".join(self.rows["token_audience"]["commands"]))

    def test_metric_query_uses_the_documented_metric_list_parameter(self) -> None:
        command = " ".join(self.rows["monitoring"]["commands"])
        self.assertIn("--metrics <metric_name>", command)
        self.assertNotIn(" --metric ", command)


if __name__ == "__main__":
    unittest.main()
