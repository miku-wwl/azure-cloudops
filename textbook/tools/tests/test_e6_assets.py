from __future__ import annotations

import unittest
from pathlib import Path
import sys

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))
from azure_inventory import AzureInventory  # noqa: E402


ROOT = Path(__file__).resolve().parents[2]
KQL_DIR = ROOT / "chapters" / "AZ05-02" / "labs" / "telemetry-triage" / "queries"
REQUIRED_KQL = {
    "failed-activity-operations.kql": {"AzureActivity", "TimeGenerated", "ActivityStatusValue", "CorrelationId"},
    "heartbeat-freshness.kql": {"Heartbeat", "TimeGenerated", "Computer", "_ResourceId", "OSType"},
    "request-failures-by-operation.kql": {"AppRequests", "Success", "ResultCode", "DurationMs", "ItemCount"},
    "dependency-failures.kql": {"AppDependencies", "DependencyType", "Target", "Success", "ItemCount"},
    "exceptions-by-operation.kql": {"AppExceptions", "ExceptionType", "ProblemId", "OperationId", "ItemCount"},
}


class E6AssetsTests(unittest.TestCase):
    def test_five_operational_kql_files_state_schema_and_not_run_status(self) -> None:
        for filename, schema_tokens in REQUIRED_KQL.items():
            with self.subTest(query=filename):
                source = (KQL_DIR / filename).read_text(encoding="utf-8")
                self.assertIn("Purpose:", source)
                self.assertIn("Schema assumptions:", source)
                self.assertIn("Verification:", source)
                self.assertIn("NOT_RUN", source)
                for token in schema_tokens:
                    self.assertIn(token, source)

    def test_inventory_query_is_explicit_and_projects_a_minimal_allowlist(self) -> None:
        inventory = AzureInventory(subscription_id="11111111-2222-3333-4444-555555555555")
        query = inventory._query()
        self.assertIn("subscriptionId =~ '11111111-2222-3333-4444-555555555555'", query)
        self.assertIn("| project id, name, type, resourceGroup, subscriptionId, location", query)
        self.assertNotIn("properties", query.casefold())
        self.assertNotIn("tags", query.casefold())
        self.assertIn("| order by id asc", query)


if __name__ == "__main__":
    unittest.main()
