from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Sequence
from unittest.mock import patch

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from textbook.incidents.live_ir11.watchdog import (
    RESOURCE_GROUP,
    PROJECT_TAG,
    AzureCleanup,
    WatchdogConfig,
    WatchdogError,
    _resolve_command,
    wait_for_completion_or_timeout,
    watch_for_primary_or_cleanup,
)


SUBSCRIPTION = "11111111-1111-4111-8111-111111111111"
TENANT = "22222222-2222-4222-8222-222222222222"
RUN_ID = "a" * 32


def config(**overrides: object) -> WatchdogConfig:
    values: dict[str, object] = {
        "subscription_id": SUBSCRIPTION,
        "tenant_id": TENANT,
        "resource_group": RESOURCE_GROUP,
        "run_id": RUN_ID,
        "wait_seconds": 2100,
        "max_runtime_seconds": 2700,
        "cleanup_timeout_seconds": 600,
    }
    values.update(overrides)
    return WatchdogConfig(**values)  # type: ignore[arg-type]


class FakeAzure:
    def __init__(self, *, exists: bool, tags: dict[str, str] | None = None, resources: list[str] | None = None) -> None:
        self.exists = exists
        self.tags = tags or {}
        self.resources = resources or []
        self.commands: list[list[str]] = []

    def __call__(self, command: Sequence[str], timeout: float) -> subprocess.CompletedProcess[str]:
        args = list(command)
        self.commands.append(args)
        if args[1:3] == ["account", "show"]:
            payload = {"id": SUBSCRIPTION, "tenantId": TENANT, "state": "Enabled"}
            return subprocess.CompletedProcess(args, 0, json.dumps(payload), "")
        if args[1:3] == ["group", "exists"]:
            return subprocess.CompletedProcess(args, 0, str(self.exists).lower(), "")
        if args[1:3] == ["group", "show"]:
            return subprocess.CompletedProcess(args, 0, json.dumps(self.tags), "")
        if args[1:3] == ["group", "delete"]:
            self.exists = False
            return subprocess.CompletedProcess(args, 0, "", "")
        if args[1:3] == ["resource", "list"]:
            return subprocess.CompletedProcess(args, 0, json.dumps(self.resources), "")
        raise AssertionError(f"unexpected Azure CLI command: {args[1:3]}")


class IR11WatchdogTests(unittest.TestCase):
    def test_config_rejects_any_group_other_than_the_approved_name(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "watchdog.json"
            path.write_text(json.dumps({
                "subscription_id": SUBSCRIPTION,
                "tenant_id": TENANT,
                "resource_group": "unrelated-rg",
                "run_id": RUN_ID,
                "wait_seconds": 2100,
                "max_runtime_seconds": 2700,
                "cleanup_timeout_seconds": 600,
            }), encoding="utf-8")
            with self.assertRaises(WatchdogError):
                WatchdogConfig.from_json(path)

    def test_windows_runner_resolves_the_azure_cmd_wrapper(self) -> None:
        with patch("textbook.incidents.live_ir11.watchdog.shutil.which", return_value=r"C:\Azure CLI\az.cmd"):
            self.assertEqual(
                [r"C:\Azure CLI\az.cmd", "account", "show"],
                _resolve_command(["az", "account", "show"], is_windows=True),
            )

    def test_windows_runner_fails_closed_if_azure_cli_wrapper_is_missing(self) -> None:
        with patch("textbook.incidents.live_ir11.watchdog.shutil.which", return_value=None):
            with self.assertRaisesRegex(WatchdogError, "Azure CLI command is unavailable"):
                _resolve_command(["az", "account", "show"], is_windows=True)

    def test_missing_group_is_success_only_when_residual_inventory_is_empty(self) -> None:
        fake = FakeAzure(exists=False)
        result = AzureCleanup(config(), runner=fake).cleanup()
        self.assertEqual("CLEANED_UP", result)
        self.assertFalse(any(command[1:3] == ["group", "delete"] for command in fake.commands))

        fake_with_residue = FakeAzure(exists=False, resources=["redacted-resource-id"])
        with self.assertRaisesRegex(WatchdogError, "residual resources"):
            AzureCleanup(config(), runner=fake_with_residue).cleanup()

    def test_unowned_group_is_never_deleted(self) -> None:
        fake = FakeAzure(exists=True, tags={"project": "other-project", "run-id": RUN_ID})
        with self.assertRaisesRegex(WatchdogError, "ownership marker"):
            AzureCleanup(config(), runner=fake).cleanup()
        self.assertFalse(any(command[1:3] == ["group", "delete"] for command in fake.commands))

    def test_context_mismatch_stops_before_any_group_command(self) -> None:
        fake = FakeAzure(exists=True)

        def wrong_context(command: Sequence[str], timeout: float) -> subprocess.CompletedProcess[str]:
            if list(command)[1:3] == ["account", "show"]:
                args = list(command)
                fake.commands.append(args)
                return subprocess.CompletedProcess(args, 0, json.dumps({
                    "id": SUBSCRIPTION,
                    "tenantId": "33333333-3333-4333-8333-333333333333",
                    "state": "Enabled",
                }), "")
            return fake(command, timeout)

        with self.assertRaisesRegex(WatchdogError, "context no longer matches"):
            AzureCleanup(config(), runner=wrong_context).cleanup()
        self.assertEqual(1, len(fake.commands))

    def test_owned_group_is_deleted_and_residual_inventory_verified(self) -> None:
        tags = {"project": PROJECT_TAG, "run-id": RUN_ID}
        fake = FakeAzure(exists=True, tags=tags)
        self.assertEqual("CLEANED_UP", AzureCleanup(config(), runner=fake).cleanup())
        self.assertTrue(any(command[1:3] == ["group", "delete"] for command in fake.commands))
        self.assertEqual([], fake.resources)

    def test_failed_delete_is_accepted_only_if_a_concurrent_delete_completed(self) -> None:
        class ConcurrentDelete(FakeAzure):
            def __call__(self, command: Sequence[str], timeout: float) -> subprocess.CompletedProcess[str]:
                args = list(command)
                if args[1:3] == ["group", "delete"]:
                    self.commands.append(args)
                    self.exists = False
                    return subprocess.CompletedProcess(args, 1, "", "conflict")
                return super().__call__(args, timeout)

        tags = {"project": PROJECT_TAG, "run-id": RUN_ID}
        fake = ConcurrentDelete(exists=True, tags=tags)
        self.assertEqual("CLEANED_UP", AzureCleanup(config(), runner=fake).cleanup())

    def test_wait_helper_detects_primary_cleanup_marker(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            marker = Path(temp) / "verified.done"
            marker.write_text("CLEANED_UP\n", encoding="utf-8")
            self.assertTrue(wait_for_completion_or_timeout(marker, 2100))

    def test_watchdog_timeout_is_bounded_and_reports_no_primary_marker(self) -> None:
        now = [0.0]

        def advance(seconds: float) -> None:
            now[0] += seconds

        with tempfile.TemporaryDirectory() as temp:
            marker = Path(temp) / "missing.done"
            completed = wait_for_completion_or_timeout(
                marker,
                11,
                monotonic=lambda: now[0],
                sleep=advance,
            )
        self.assertFalse(completed)
        self.assertGreaterEqual(now[0], 11)
        self.assertLessEqual(now[0], 11.1)

    def test_watchdog_keeps_monitoring_for_late_resource_group_creation(self) -> None:
        now = [0.0]
        tags = {"project": PROJECT_TAG, "run-id": RUN_ID}
        fake = FakeAzure(exists=False, tags=tags)

        def advance(seconds: float) -> None:
            now[0] += seconds
            if now[0] >= 2130:
                fake.exists = True

        with tempfile.TemporaryDirectory() as temp:
            marker = Path(temp) / "missing.done"
            result = watch_for_primary_or_cleanup(
                config(),
                marker,
                cleanup=AzureCleanup(config(), runner=fake, sleep=advance, monotonic=lambda: now[0]),
                monotonic=lambda: now[0],
                sleep=advance,
                poll_seconds=30,
            )
        self.assertEqual("CLEANED_UP", result)
        self.assertTrue(any(command[1:3] == ["group", "delete"] for command in fake.commands))
        self.assertFalse(fake.exists)

    def test_watchdog_keeps_monitoring_after_primary_cleanup_marker(self) -> None:
        now = [0.0]
        tags = {"project": PROJECT_TAG, "run-id": RUN_ID}
        fake = FakeAzure(exists=False, tags=tags)

        def advance(seconds: float) -> None:
            now[0] += seconds
            if now[0] >= 20:
                fake.exists = True

        with tempfile.TemporaryDirectory() as temp:
            marker = Path(temp) / "verified.done"
            marker.write_text("CLEANED_UP\n", encoding="utf-8")
            short_config = config(wait_seconds=5, max_runtime_seconds=90, cleanup_timeout_seconds=30)
            result = watch_for_primary_or_cleanup(
                short_config,
                marker,
                cleanup=AzureCleanup(short_config, runner=fake, sleep=advance, monotonic=lambda: now[0]),
                monotonic=lambda: now[0],
                sleep=advance,
                poll_seconds=10,
            )
        self.assertEqual("CLEANED_UP", result)
        self.assertTrue(any(command[1:3] == ["group", "delete"] for command in fake.commands))
        self.assertFalse(fake.exists)

    def test_azure_calls_are_bounded_by_the_watchdog_hard_deadline(self) -> None:
        timeouts: list[float] = []

        def runner(command: Sequence[str], timeout: float) -> subprocess.CompletedProcess[str]:
            timeouts.append(timeout)
            args = list(command)
            return subprocess.CompletedProcess(args, 0, json.dumps({
                "id": SUBSCRIPTION,
                "tenantId": TENANT,
                "state": "Enabled",
            }), "")

        cleaner = AzureCleanup(config(), runner=runner, monotonic=lambda: 2699.5)
        cleaner._context_matches(deadline=2700.0)
        self.assertEqual([0.5], timeouts)


if __name__ == "__main__":
    unittest.main()
