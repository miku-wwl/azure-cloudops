"""Independent, fail-closed cleanup watchdog for the disposable IR-11 group.

The watchdog waits for a completion marker. If the main run has not verified
cleanup by the deadline, it checks the exact Azure CLI tenant/subscription,
requires the run-specific ownership tags, deletes only the approved resource
group, and verifies that the group and its resources are gone. It never logs
resource IDs or raw Azure CLI output.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Sequence


RESOURCE_GROUP = "rg-azure-cloudops-ir11-aue"
PLAN_NAME = "asp-azure-cloudops-ir11-aue"
SITE_NAME = "azcoir11aue261126"
PROJECT_TAG = "azure-cloudops-ir11"
CONFIRMED_MARKER = "CLEANED_UP_NO_PENDING_GROUP_CREATE"
RUN_ID_RE = re.compile(r"^[0-9a-f]{32}$")


class WatchdogError(RuntimeError):
    """A safe cleanup could not be proven; raw Azure output is suppressed."""


@dataclass(frozen=True)
class WatchdogConfig:
    subscription_id: str
    tenant_id: str
    resource_group: str
    run_id: str
    wait_seconds: int
    max_runtime_seconds: int
    cleanup_timeout_seconds: int

    @classmethod
    def from_json(cls, path: Path) -> "WatchdogConfig":
        try:
            raw = json.loads(path.read_text(encoding="utf-8-sig"))
        except (OSError, json.JSONDecodeError) as exc:
            raise WatchdogError("watchdog config is missing or invalid") from exc
        if not isinstance(raw, dict):
            raise WatchdogError("watchdog config must be an object")
        try:
            config = cls(
                subscription_id=str(uuid.UUID(raw["subscription_id"])),
                tenant_id=str(uuid.UUID(raw["tenant_id"])),
                resource_group=raw["resource_group"],
                run_id=raw["run_id"],
                wait_seconds=raw["wait_seconds"],
                max_runtime_seconds=raw["max_runtime_seconds"],
                cleanup_timeout_seconds=raw["cleanup_timeout_seconds"],
            )
        except (KeyError, ValueError, TypeError, AttributeError) as exc:
            raise WatchdogError("watchdog config fields are invalid") from exc
        if config.resource_group != RESOURCE_GROUP:
            raise WatchdogError("watchdog refuses an unapproved resource group")
        if not isinstance(config.run_id, str) or not RUN_ID_RE.fullmatch(config.run_id):
            raise WatchdogError("watchdog run id is invalid")
        if isinstance(config.wait_seconds, bool) or not isinstance(config.wait_seconds, int) or not 1 <= config.wait_seconds <= 40 * 60:
            raise WatchdogError("watchdog wait must be between 1 and 40 minutes")
        if isinstance(config.max_runtime_seconds, bool) or not isinstance(config.max_runtime_seconds, int) or not config.wait_seconds < config.max_runtime_seconds <= 45 * 60:
            raise WatchdogError("watchdog maximum runtime must be after its trigger and no more than 45 minutes")
        if isinstance(config.cleanup_timeout_seconds, bool) or not isinstance(config.cleanup_timeout_seconds, int) or not 30 <= config.cleanup_timeout_seconds <= 10 * 60:
            raise WatchdogError("watchdog cleanup timeout must be between 30 and 600 seconds")
        return config


Runner = Callable[[Sequence[str], float], subprocess.CompletedProcess[str]]


def _resolve_command(command: Sequence[str], *, is_windows: bool | None = None) -> list[str]:
    resolved = list(command)
    windows = os.name == "nt" if is_windows is None else is_windows
    if windows and resolved and resolved[0] == "az":
        wrapper = shutil.which("az")
        if wrapper is None:
            raise WatchdogError("Azure CLI command is unavailable")
        launch_path = Path(wrapper)
        if launch_path.suffix.casefold() in {".cmd", ".bat"}:
            # Use the installed CLI's interpreter so the timeout owns the
            # Azure CLI process itself, and no batch shell reparses arguments.
            cli_python = launch_path.parent.parent / "python.exe"
            if not cli_python.is_file():
                raise WatchdogError("Azure CLI's bundled interpreter is unavailable")
            resolved = [str(cli_python), "-IBm", "azure.cli", *resolved[1:]]
        else:
            resolved[0] = wrapper
    return resolved


def _default_runner(command: Sequence[str], timeout: float) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        _resolve_command(command),
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
    )


class AzureCleanup:
    def __init__(
        self,
        config: WatchdogConfig,
        *,
        runner: Runner = _default_runner,
        sleep: Callable[[float], None] = time.sleep,
        monotonic: Callable[[], float] = time.monotonic,
    ) -> None:
        self.config = config
        self.runner = runner
        self.sleep = sleep
        self.monotonic = monotonic

    def _az(
        self,
        *args: str,
        timeout: float | None = None,
        deadline: float | None = None,
    ) -> str:
        command = ["az", *args, "--only-show-errors"]
        budget = timeout or self.config.cleanup_timeout_seconds
        if deadline is not None:
            remaining = deadline - self.monotonic()
            if remaining <= 0:
                raise WatchdogError("watchdog runtime deadline reached before Azure verification")
            budget = min(budget, remaining)
        try:
            result = self.runner(command, budget)
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise WatchdogError("Azure CLI command could not be completed") from exc
        if result.returncode != 0:
            raise WatchdogError("Azure CLI command failed")
        return result.stdout

    def _context_matches(self, *, deadline: float | None = None) -> None:
        raw = self._az(
            "account", "show", "--subscription", self.config.subscription_id,
            "--output", "json",
            deadline=deadline,
        )
        try:
            account = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise WatchdogError("Azure CLI returned an invalid account context") from exc
        if (
            not isinstance(account, dict)
            or str(account.get("id", "")).casefold() != self.config.subscription_id.casefold()
            or str(account.get("tenantId", "")).casefold() != self.config.tenant_id.casefold()
            or account.get("state") != "Enabled"
        ):
            raise WatchdogError("Azure CLI context no longer matches the approved tenant and subscription")

    def _group_exists(self, *, deadline: float | None = None) -> bool:
        raw = self._az(
            "group", "exists", "--name", self.config.resource_group,
            "--subscription", self.config.subscription_id, "--output", "tsv",
            deadline=deadline,
        ).strip().casefold()
        if raw not in {"true", "false"}:
            raise WatchdogError("Azure CLI returned an invalid resource-group state")
        return raw == "true"

    def _is_owned(self, *, deadline: float | None = None) -> bool:
        raw = self._az(
            "group", "show", "--name", self.config.resource_group,
            "--subscription", self.config.subscription_id,
            "--query", "tags", "--output", "json",
            deadline=deadline,
        )
        try:
            tags = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise WatchdogError("Azure CLI returned invalid ownership tags") from exc
        return (
            isinstance(tags, dict)
            and tags.get("project") == PROJECT_TAG
            and tags.get("run-id") == self.config.run_id
        )

    def _resource_ids(self, *, deadline: float | None = None) -> list[str]:
        raw = self._az(
            "resource", "list",
            "--subscription", self.config.subscription_id,
            "--query", f"[?resourceGroup=='{self.config.resource_group}'].id", "--output", "json",
            deadline=deadline,
        )
        try:
            resources = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise WatchdogError("Azure CLI returned invalid residual-resource data") from exc
        if not isinstance(resources, list) or any(not isinstance(item, str) for item in resources):
            raise WatchdogError("Azure CLI returned an incomplete residual-resource inventory")
        return resources

    def cleanup_if_present(self, *, deadline: float | None = None) -> bool:
        """Delete only an owned group; return whether it existed and was removed."""
        self._context_matches(deadline=deadline)
        if not self._group_exists(deadline=deadline):
            if self._resource_ids(deadline=deadline):
                raise WatchdogError("residual resources remain after the group disappeared")
            return False
        if not self._is_owned(deadline=deadline):
            raise WatchdogError("resource-group ownership marker does not match; refusing deletion")
        owned_prefix = f"/subscriptions/{self.config.subscription_id}/resourceGroups/{RESOURCE_GROUP}/providers/Microsoft.Web"
        allowed = {
            f"{owned_prefix}/serverfarms/{PLAN_NAME}".casefold(),
            f"{owned_prefix}/sites/{SITE_NAME}".casefold(),
        }
        if any(resource.casefold() not in allowed for resource in self._resource_ids(deadline=deadline)):
            raise WatchdogError("resource group contains a resource outside the approved deletion scope")
        try:
            self._az(
                "group", "delete", "--name", self.config.resource_group,
                "--subscription", self.config.subscription_id, "--yes",
                timeout=self.config.cleanup_timeout_seconds,
                deadline=deadline,
            )
        except WatchdogError:
            # A concurrent primary-process delete is acceptable only if the
            # subsequent existence and residual checks prove full removal.
            if self._group_exists(deadline=deadline):
                raise

        cleanup_deadline = self.monotonic() + self.config.cleanup_timeout_seconds
        if deadline is not None:
            cleanup_deadline = min(cleanup_deadline, deadline)
        while self._group_exists(deadline=deadline) and self.monotonic() < cleanup_deadline:
            self.sleep(min(2.0, max(0.0, cleanup_deadline - self.monotonic())))
        if self._group_exists(deadline=deadline):
            raise WatchdogError("resource group remained after bounded cleanup wait")
        if self._resource_ids(deadline=deadline):
            raise WatchdogError("residual resources remain or inventory is not empty")
        return True

    def cleanup(self, *, deadline: float | None = None) -> str:
        self.cleanup_if_present(deadline=deadline)
        if self._group_exists(deadline=deadline):
            raise WatchdogError("resource group remained after cleanup")
        if self._resource_ids(deadline=deadline):
            raise WatchdogError("residual resources remain or inventory is not empty")
        return "CLEANED_UP"


def wait_for_completion_or_timeout(
    done_file: Path,
    wait_seconds: int,
    *,
    monotonic: Callable[[], float] = time.monotonic,
    sleep: Callable[[float], None] = time.sleep,
) -> bool:
    """Return True if the primary process wrote its verified-cleanup marker."""
    deadline = monotonic() + wait_seconds
    while True:
        if done_file.is_file():
            return True
        remaining = deadline - monotonic()
        if remaining <= 0:
            return done_file.is_file()
        sleep(min(5.0, remaining))


def watch_for_primary_or_cleanup(
    config: WatchdogConfig,
    done_file: Path,
    *,
    cleanup: AzureCleanup,
    monotonic: Callable[[], float] = time.monotonic,
    sleep: Callable[[float], None] = time.sleep,
    poll_seconds: float = 30.0,
) -> str:
    """Watch through the full lifetime so late ARM completion is still cleaned."""
    started = monotonic()
    cleanup_trigger = started + config.wait_seconds
    hard_deadline = started + config.max_runtime_seconds
    final_check_start = hard_deadline - min(5 * 60, config.cleanup_timeout_seconds)
    while monotonic() < final_check_start:
        now = monotonic()
        if done_file.is_file() or now >= cleanup_trigger:
            try:
                confirmed = done_file.is_file() and done_file.read_text(encoding="ascii").strip() == CONFIRMED_MARKER
            except (OSError, UnicodeError):
                confirmed = False
            try:
                if confirmed:
                    # The synchronous group create completed before the parent
                    # proved deletion. Independently verify before exiting.
                    return cleanup.cleanup(deadline=hard_deadline)
                # An ambiguous create can still finish after primary cleanup.
                cleanup.cleanup_if_present(deadline=hard_deadline)
            except WatchdogError:
                # A transient read or delete error must not end the watchdog
                # while there is time for another ownership-checked attempt.
                pass
        remaining = final_check_start - monotonic()
        sleep(min(poll_seconds, max(0.0, remaining)))
    # Reserve the final window for a bounded cleanup and residual inventory
    # check. If Azure cannot prove removal inside the 45-minute cap, fail
    # visibly instead of reporting success or extending the run indefinitely.
    return cleanup.cleanup(deadline=hard_deadline)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Independent fail-closed LAB-IR-11 cleanup watchdog.")
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--done-file", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        config = WatchdogConfig.from_json(args.config)
        cleaner = AzureCleanup(config)
        result = watch_for_primary_or_cleanup(config, args.done_file, cleanup=cleaner)
    except WatchdogError as exc:
        print(json.dumps({"watchdog": "CLEANUP_UNVERIFIED", "reason": str(exc)}, sort_keys=True), file=sys.stderr)
        return 1
    print(json.dumps({"watchdog": result}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
