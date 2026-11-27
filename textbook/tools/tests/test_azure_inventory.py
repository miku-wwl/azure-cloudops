from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path
from typing import Any, Sequence

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import azure_inventory  # noqa: E402


SUBSCRIPTION = "11111111-2222-3333-4444-555555555555"
RESOURCE_1 = "/subscriptions/11111111-2222-3333-4444-555555555555/resourceGroups/lab/providers/Microsoft.Compute/virtualMachines/vm-a"
RESOURCE_2 = "/subscriptions/11111111-2222-3333-4444-555555555555/resourceGroups/lab/providers/Microsoft.Network/networkInterfaces/nic-a"


def row(resource_id: str, name: str, resource_type: str, **extra: Any) -> dict[str, Any]:
    return {"id": resource_id, "name": name, "type": resource_type, "resourceGroup": "lab", "subscriptionId": SUBSCRIPTION, "location": "eastus", **extra}


def response(rows: list[dict[str, Any]], *, total: int, token: str | None = None) -> str:
    return json.dumps({"count": len(rows), "data": rows, "skip_token": token, "total_records": total})


class FakeRunner:
    def __init__(self, results: list[subprocess.CompletedProcess[str] | BaseException], extension: subprocess.CompletedProcess[str] | None = None):
        self.results = list(results)
        self.extension = extension or completed('{"name":"resource-graph","version":"1.0.0"}')
        self.calls: list[tuple[list[str], float]] = []

    def __call__(self, command: Sequence[str], timeout: float) -> subprocess.CompletedProcess[str]:
        self.calls.append((list(command), timeout))
        if list(command[:3]) == ["az", "extension", "show"]:
            return self.extension
        result = self.results.pop(0)
        if isinstance(result, BaseException):
            raise result
        return result


def completed(stdout: str = "", stderr: str = "", code: int = 0) -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess(args=["az"], returncode=code, stdout=stdout, stderr=stderr)


class AzureInventoryTests(unittest.TestCase):
    def inventory(self, runner: FakeRunner, **kwargs: Any) -> azure_inventory.AzureInventory:
        return azure_inventory.AzureInventory(subscription_id=SUBSCRIPTION, runner=runner, sleep=lambda _: None, **kwargs)

    def test_uses_explicit_subscription_and_never_reads_default_scope(self) -> None:
        runner = FakeRunner([completed(response([row(RESOURCE_1, "vm-a", "Microsoft.Compute/virtualMachines")], total=1))])
        result = self.inventory(runner).collect()
        command = runner.calls[1][0]
        self.assertIn("--subscriptions", command)
        self.assertIn(SUBSCRIPTION, command)
        self.assertNotIn("--subscription", command)
        self.assertIn(SUBSCRIPTION, command[command.index("--graph-query") + 1])
        self.assertEqual(result["status"], "complete")

    def test_follows_continuation_token_and_deduplicates_stable_ids(self) -> None:
        runner = FakeRunner([
            completed(response([row(RESOURCE_1, "vm-a", "Microsoft.Compute/virtualMachines"), row(RESOURCE_2, "nic-a", "Microsoft.Network/networkInterfaces")], total=4, token="opaque-next")),
            completed(response([row(RESOURCE_1 + "/extensions/agent", "agent", "Microsoft.Compute/virtualMachines/extensions"), row(RESOURCE_1 + "/extensions/guest", "guest", "Microsoft.Compute/virtualMachines/extensions")], total=4)),
        ])
        result = self.inventory(runner, page_size=2).collect()
        self.assertEqual(result["status"], "complete")
        self.assertEqual(result["pagination"]["pages"], 2)
        self.assertEqual(result["pagination"]["rows_received"], 4)
        self.assertEqual(result["pagination"]["unique_resources"], 4)
        self.assertEqual(result["pagination"]["duplicate_ids"], 0)
        self.assertIn("--skip-token", runner.calls[2][0])
        self.assertIn("opaque-next", runner.calls[2][0])

    def test_duplicate_ids_across_pages_make_result_incomplete(self) -> None:
        runner = FakeRunner([
            completed(response([row(RESOURCE_1, "vm-a", "Microsoft.Compute/virtualMachines"), row(RESOURCE_2, "nic-a", "Microsoft.Network/networkInterfaces")], total=3, token="next")),
            completed(response([row(RESOURCE_2, "nic-a", "Microsoft.Network/networkInterfaces"), row(RESOURCE_1 + "/extensions/agent", "agent", "Microsoft.Compute/virtualMachines/extensions")], total=3)),
        ])
        result = self.inventory(runner, page_size=2).collect()
        self.assertEqual(result["status"], "incomplete")
        self.assertEqual(result["error"]["code"], "DUPLICATE_IDS")
        self.assertEqual(result["pagination"]["unique_resources"], 3)

    def test_default_output_redacts_resource_identifiers_and_omits_dynamic_fields(self) -> None:
        sensitive_tags = {"owner": "alice", "secret": "should-not-be-returned"}
        runner = FakeRunner([completed(response([row(RESOURCE_1, "vm-secret-name", "Microsoft.Compute/virtualMachines", tags=sensitive_tags, properties={"adminPassword": "hidden"})], total=1))])
        result = self.inventory(runner).collect()
        resource = result["resources"][0]
        encoded = json.dumps(result)
        self.assertIn("resource_ref", resource)
        self.assertNotIn("id", resource)
        self.assertNotIn("name", resource)
        self.assertNotIn("vm-secret-name", encoded)
        self.assertNotIn("alice", encoded)
        self.assertNotIn("hidden", encoded)
        self.assertEqual(result["identifier_redaction"], "sha256-prefix")

    def test_explicit_identifier_option_returns_only_projected_identifiers(self) -> None:
        runner = FakeRunner([completed(response([row(RESOURCE_1, "vm-a", "Microsoft.Compute/virtualMachines", properties={"password": "not-projected"})], total=1))])
        result = self.inventory(runner, show_identifiers=True).collect()
        resource = result["resources"][0]
        self.assertEqual(resource["id"], RESOURCE_1)
        self.assertEqual(resource["name"], "vm-a")
        self.assertNotIn("properties", resource)
        self.assertNotIn("password", json.dumps(result))

    def test_empty_result_is_explicit(self) -> None:
        runner = FakeRunner([completed(response([], total=0))])
        result = self.inventory(runner).collect()
        self.assertEqual(result["status"], "empty")
        self.assertEqual(result["resources"], [])
        self.assertTrue(result["ok"])

    def test_permission_error_is_not_retried_or_echoed(self) -> None:
        runner = FakeRunner([completed(stderr=f"AuthorizationFailed for {RESOURCE_1}", code=1)])
        with self.assertRaises(azure_inventory.InventoryError) as raised:
            self.inventory(runner).collect()
        self.assertEqual(raised.exception.code, "PERMISSION_DENIED")
        self.assertEqual(raised.exception.exit_code, azure_inventory.EXIT_PERMISSION)
        self.assertEqual(len(runner.calls), 2)
        self.assertEqual(runner.calls[1][0][:3], ["az", "graph", "query"])
        self.assertNotIn(RESOURCE_1, str(raised.exception))

    def test_missing_login_is_reported_without_attempting_authentication(self) -> None:
        runner = FakeRunner([completed(stderr="Please run 'az login' to setup account", code=1)])
        with self.assertRaises(azure_inventory.InventoryError) as raised:
            self.inventory(runner).collect()
        self.assertEqual(raised.exception.code, "AUTH_REQUIRED")
        self.assertEqual(raised.exception.exit_code, azure_inventory.EXIT_AUTH)
        self.assertEqual(len(runner.calls), 2)
        self.assertEqual(runner.calls[1][0][:3], ["az", "graph", "query"])

    def test_missing_resource_graph_extension_fails_before_query(self) -> None:
        runner = FakeRunner([], extension=completed(stderr="extension not found", code=1))
        with self.assertRaises(azure_inventory.InventoryError) as raised:
            self.inventory(runner).collect()
        self.assertEqual(raised.exception.code, "EXTENSION_REQUIRED")
        self.assertEqual(raised.exception.exit_code, azure_inventory.EXIT_DEPENDENCY)
        self.assertEqual(len(runner.calls), 1)
        self.assertEqual(runner.calls[0][0][:3], ["az", "extension", "show"])

    def test_throttled_request_retries_with_bounded_backoff(self) -> None:
        runner = FakeRunner([
            completed(stderr="TooManyRequests: 429", code=1),
            completed(response([], total=0)),
        ])
        delays: list[float] = []
        inventory = azure_inventory.AzureInventory(subscription_id=SUBSCRIPTION, runner=runner, sleep=delays.append, retries=2)
        result = inventory.collect()
        self.assertEqual(result["status"], "empty")
        self.assertEqual(len(runner.calls), 3)
        self.assertEqual(delays, [0.5])

    def test_transient_failure_exhaustion_has_sanitized_error(self) -> None:
        runner = FakeRunner([completed(stderr="503 token=super-secret", code=1), completed(stderr="503 token=super-secret", code=1)])
        inventory = azure_inventory.AzureInventory(subscription_id=SUBSCRIPTION, runner=runner, sleep=lambda _: None, retries=1)
        with self.assertRaises(azure_inventory.InventoryError) as raised:
            inventory.collect()
        self.assertEqual(raised.exception.code, "TRANSIENT_SERVICE_ERROR")
        self.assertEqual(raised.exception.attempts, 2)
        self.assertNotIn("super-secret", str(raised.exception))

    def test_timeout_retries_then_returns_timeout_exit(self) -> None:
        runner = FakeRunner([subprocess.TimeoutExpired("az graph query", 1), subprocess.TimeoutExpired("az graph query", 1)])
        inventory = azure_inventory.AzureInventory(subscription_id=SUBSCRIPTION, runner=runner, sleep=lambda _: None, timeout=1, retries=1)
        with self.assertRaises(azure_inventory.InventoryError) as raised:
            inventory.collect()
        self.assertEqual(raised.exception.code, "REQUEST_TIMEOUT")
        self.assertEqual(raised.exception.exit_code, azure_inventory.EXIT_TIMEOUT)
        self.assertEqual(raised.exception.attempts, 2)

    def test_page_limit_and_count_mismatch_fail_closed(self) -> None:
        many = FakeRunner([completed(response([row(RESOURCE_1, "vm-a", "Microsoft.Compute/virtualMachines")], total=3, token="next"))])
        limited = self.inventory(many, page_size=1, max_pages=1).collect()
        self.assertEqual(limited["status"], "incomplete")
        self.assertEqual(limited["error"]["code"], "PAGE_LIMIT_REACHED")

        mismatch = FakeRunner([completed(response([row(RESOURCE_1, "vm-a", "Microsoft.Compute/virtualMachines")], total=2))])
        incomplete = self.inventory(mismatch).collect()
        self.assertEqual(incomplete["status"], "incomplete")
        self.assertEqual(incomplete["error"]["code"], "COUNT_MISMATCH")

    def test_repeated_continuation_token_fails_closed(self) -> None:
        runner = FakeRunner([
            completed(response([row(RESOURCE_1, "vm-a", "Microsoft.Compute/virtualMachines")], total=2, token="same")),
            completed(response([row(RESOURCE_2, "nic-a", "Microsoft.Network/networkInterfaces")], total=2, token="same")),
        ])
        with self.assertRaises(azure_inventory.InventoryError) as raised:
            self.inventory(runner, page_size=1).collect()
        self.assertEqual(raised.exception.code, "PAGINATION_LOOP")

    def test_scope_filter_and_resource_group_injection_are_rejected(self) -> None:
        with self.assertRaises(azure_inventory.InventoryError) as raised:
            azure_inventory.AzureInventory(subscription_id="not-a-uuid", runner=FakeRunner([]))
        self.assertEqual(raised.exception.exit_code, azure_inventory.EXIT_USAGE)
        with self.assertRaises(azure_inventory.InventoryError):
            azure_inventory.AzureInventory(subscription_id=SUBSCRIPTION, resource_group="lab' | Resources", runner=FakeRunner([]))

    def test_cli_help_documents_explicit_subscription_and_redaction_options(self) -> None:
        help_text = azure_inventory.build_parser().format_help()
        self.assertIn("--subscription-id", help_text)
        self.assertIn("--show-resource-identifiers", help_text)
        self.assertIn("default Azure", " ".join(help_text.split()))
        self.assertIn("never used", " ".join(help_text.split()))

    def test_missing_required_scope_uses_a_distinct_usage_exit_code(self) -> None:
        with self.assertRaises(SystemExit) as raised:
            azure_inventory.main([])
        self.assertEqual(raised.exception.code, azure_inventory.EXIT_USAGE)


if __name__ == "__main__":
    unittest.main()
