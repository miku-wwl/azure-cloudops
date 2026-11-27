#!/usr/bin/env python3
"""Bounded, read-only Azure Resource Graph inventory using an existing az session.

The query and subscription scope are explicit on every page. The tool never logs
in, selects a default subscription, or asks for a token. By default, resource
names and IDs are replaced with stable SHA-256 references and dynamic properties
and tags are never requested or emitted.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable, Sequence


EXIT_OK = 0
EXIT_EMPTY = 2
EXIT_USAGE = 3
EXIT_AUTH = 4
EXIT_PERMISSION = 5
EXIT_TIMEOUT = 6
EXIT_INCOMPLETE = 7
EXIT_QUERY = 8
EXIT_DEPENDENCY = 9

_RESOURCE_GROUP = re.compile(r"^[A-Za-z0-9()._-]{1,90}$")
_AUTH_MARKERS = (
    "please run 'az login'", "run az login", "aadsts", "authenticationfailed",
    "authentication required", "not logged in", "login required",
)
_PERMISSION_MARKERS = (
    "authorizationfailed", "insufficient privileges", "forbidden", "http 403", "status code 403",
)
_RETRY_MARKERS = (
    "toomanyrequests", "rate limit", "throttl", "http 429", "status code 429",
    "serviceunavailable", "temporarily unavailable", "http 502", "http 503", "http 504",
)
_TRANSIENT_HTTP_STATUS = re.compile(r"\b(?:429|502|503|504)\b")


@dataclass(frozen=True)
class Page:
    rows: list[dict[str, Any]]
    skip_token: str | None
    total_records: int | None


class InventoryError(RuntimeError):
    def __init__(self, code: str, message: str, exit_code: int, attempts: int = 1) -> None:
        super().__init__(message)
        self.code = code
        self.exit_code = exit_code
        self.attempts = attempts


def _safe_error_class(stderr: str) -> tuple[str, str, int, bool]:
    lowered = stderr.casefold()
    if any(marker in lowered for marker in _AUTH_MARKERS):
        return "AUTH_REQUIRED", "Azure CLI has no usable authenticated session.", EXIT_AUTH, False
    if any(marker in lowered for marker in _PERMISSION_MARKERS):
        return "PERMISSION_DENIED", "The current identity cannot read the requested subscription scope.", EXIT_PERMISSION, False
    if any(marker in lowered for marker in _RETRY_MARKERS) or _TRANSIENT_HTTP_STATUS.search(lowered):
        return "TRANSIENT_SERVICE_ERROR", "Azure Resource Graph returned a retryable service or throttling error.", EXIT_QUERY, True
    return "QUERY_FAILED", "Azure Resource Graph query failed; raw CLI output was suppressed.", EXIT_QUERY, False


def _default_runner(command: Sequence[str], timeout: float) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(command),
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
    )


def _int_or_none(value: Any, label: str) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise InventoryError("INVALID_RESPONSE", f"Azure Resource Graph returned an invalid {label}.", EXIT_INCOMPLETE)
    return value


def parse_page(raw: str) -> Page:
    if len(raw.encode("utf-8", errors="replace")) > 20 * 1024 * 1024:
        raise InventoryError("RESPONSE_TOO_LARGE", "Azure Resource Graph page exceeded the 20 MiB safety limit.", EXIT_INCOMPLETE)
    try:
        value = json.loads(raw)
    except (json.JSONDecodeError, TypeError) as exc:
        raise InventoryError("INVALID_RESPONSE", "Azure CLI returned invalid JSON; raw output was suppressed.", EXIT_INCOMPLETE) from exc
    if not isinstance(value, dict) or not isinstance(value.get("data"), list):
        raise InventoryError("INVALID_RESPONSE", "Azure Resource Graph response omitted its data array.", EXIT_INCOMPLETE)
    rows = value["data"]
    count = _int_or_none(value.get("count"), "count")
    if count is None:
        raise InventoryError("INVALID_RESPONSE", "Azure Resource Graph response omitted its count.", EXIT_INCOMPLETE)
    if count != len(rows):
        raise InventoryError("INVALID_RESPONSE", "Azure Resource Graph count did not match the returned rows.", EXIT_INCOMPLETE)
    token = value.get("skip_token", value.get("skipToken", value.get("$skipToken")))
    if token is not None and (not isinstance(token, str) or not token):
        raise InventoryError("INVALID_RESPONSE", "Azure Resource Graph returned an invalid continuation token.", EXIT_INCOMPLETE)
    total = value.get("total_records", value.get("totalRecords"))
    return Page(rows=rows, skip_token=token, total_records=_int_or_none(total, "total-record count"))


def _resource_row(item: dict[str, Any], show_identifiers: bool) -> dict[str, Any]:
    resource_id = item.get("id")
    resource_type = item.get("type")
    if not isinstance(resource_id, str) or not resource_id or not isinstance(resource_type, str) or not resource_type:
        raise InventoryError("INVALID_RESPONSE", "A resource row omitted its resource ID or type.", EXIT_INCOMPLETE)
    location = item.get("location")
    if location is not None and not isinstance(location, str):
        raise InventoryError("INVALID_RESPONSE", "A resource row contained an invalid location.", EXIT_INCOMPLETE)
    result: dict[str, Any] = {"type": resource_type, "location": location}
    if show_identifiers:
        result["id"] = resource_id
        for field in ("name", "resourceGroup", "subscriptionId"):
            value = item.get(field)
            if value is not None and not isinstance(value, str):
                raise InventoryError("INVALID_RESPONSE", f"A resource row contained an invalid {field}.", EXIT_INCOMPLETE)
            result[field] = value
    else:
        result["resource_ref"] = hashlib.sha256(resource_id.casefold().encode("utf-8")).hexdigest()[:20]
    return result


class AzureInventory:
    def __init__(
        self,
        *,
        subscription_id: str,
        resource_group: str | None = None,
        page_size: int = 1000,
        max_pages: int = 100,
        timeout: float = 30.0,
        retries: int = 3,
        show_identifiers: bool = False,
        runner: Callable[[Sequence[str], float], subprocess.CompletedProcess[str]] = _default_runner,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        try:
            self.subscription_id = str(uuid.UUID(subscription_id))
        except (ValueError, TypeError, AttributeError) as exc:
            raise InventoryError("INVALID_SCOPE", "subscription-id must be a UUID.", EXIT_USAGE) from exc
        if resource_group is not None and not _RESOURCE_GROUP.fullmatch(resource_group):
            raise InventoryError("INVALID_SCOPE", "resource-group contains unsupported characters or length.", EXIT_USAGE)
        if isinstance(page_size, bool) or not 1 <= page_size <= 1000:
            raise InventoryError("INVALID_OPTION", "page-size must be between 1 and 1000.", EXIT_USAGE)
        if isinstance(max_pages, bool) or not 1 <= max_pages <= 100:
            raise InventoryError("INVALID_OPTION", "max-pages must be between 1 and 100.", EXIT_USAGE)
        if not 1 <= timeout <= 300:
            raise InventoryError("INVALID_OPTION", "timeout must be between 1 and 300 seconds per request.", EXIT_USAGE)
        if not 0 <= retries <= 5:
            raise InventoryError("INVALID_OPTION", "retries must be between 0 and 5.", EXIT_USAGE)
        self.resource_group = resource_group
        self.page_size = page_size
        self.max_pages = max_pages
        self.timeout = timeout
        self.retries = retries
        self.show_identifiers = show_identifiers
        self.runner = runner
        self.sleep = sleep

    def _require_resource_graph_extension(self) -> None:
        """Check the local CLI extension without allowing dynamic installation."""
        try:
            result = self.runner(["az", "extension", "show", "--name", "resource-graph", "--only-show-errors", "--output", "json"], self.timeout)
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise InventoryError("EXTENSION_CHECK_FAILED", "Could not verify the local Azure CLI Resource Graph extension.", EXIT_DEPENDENCY) from exc
        if result.returncode != 0:
            raise InventoryError("EXTENSION_REQUIRED", "Install the Azure CLI resource-graph extension explicitly before running inventory.", EXIT_DEPENDENCY)
        try:
            metadata = json.loads(result.stdout)
        except (json.JSONDecodeError, TypeError) as exc:
            raise InventoryError("EXTENSION_CHECK_FAILED", "Azure CLI returned invalid extension metadata.", EXIT_DEPENDENCY) from exc
        if not isinstance(metadata, dict) or metadata.get("name") != "resource-graph":
            raise InventoryError("EXTENSION_REQUIRED", "Install the Azure CLI resource-graph extension explicitly before running inventory.", EXIT_DEPENDENCY)

    def _query(self) -> str:
        query = (
            "Resources\n"
            f"| where subscriptionId =~ '{self.subscription_id}'\n"
        )
        if self.resource_group is not None:
            query += f"| where resourceGroup =~ '{self.resource_group}'\n"
        return query + "| project id, name, type, resourceGroup, subscriptionId, location\n| order by id asc"

    def _get_page(self, skip_token: str | None) -> tuple[Page, int]:
        command = [
            "az", "graph", "query", "--graph-query", self._query(),
            "--subscriptions", self.subscription_id,
            "--first", str(self.page_size), "--only-show-errors", "--output", "json",
        ]
        if skip_token is not None:
            command.extend(["--skip-token", skip_token])
        for attempt in range(self.retries + 1):
            try:
                result = self.runner(command, self.timeout)
            except subprocess.TimeoutExpired as exc:
                if attempt < self.retries:
                    self.sleep(min(0.5 * (2 ** attempt), 8.0))
                    continue
                raise InventoryError("REQUEST_TIMEOUT", "Azure Resource Graph request exceeded its timeout.", EXIT_TIMEOUT, attempt + 1) from exc
            if result.returncode == 0:
                try:
                    return parse_page(result.stdout), attempt + 1
                except InventoryError:
                    raise
            code, message, exit_code, retryable = _safe_error_class(result.stderr or "")
            if retryable and attempt < self.retries:
                self.sleep(min(0.5 * (2 ** attempt), 8.0))
                continue
            raise InventoryError(code, message, exit_code, attempt + 1)
        raise AssertionError("retry loop must return or raise")

    def collect(self) -> dict[str, Any]:
        self._require_resource_graph_extension()
        records: list[dict[str, Any]] = []
        seen_ids: set[str] = set()
        seen_tokens: set[str] = set()
        total_records: int | None = None
        total_changed = False
        warnings: list[str] = []
        pages = 0
        page_row_count = 0
        skip_token: str | None = None
        duplicate_count = 0

        while pages < self.max_pages:
            page, attempts = self._get_page(skip_token)
            pages += 1
            page_row_count += len(page.rows)
            if page.total_records is not None:
                if total_records is not None and page.total_records != total_records:
                    total_changed = True
                    warnings.append("total_records changed during pagination; inventory is not a point-in-time snapshot")
                total_records = page.total_records
            for item in page.rows:
                if not isinstance(item, dict):
                    raise InventoryError("INVALID_RESPONSE", "A resource row was not an object.", EXIT_INCOMPLETE, attempts)
                resource_id = item.get("id")
                if not isinstance(resource_id, str) or not resource_id:
                    raise InventoryError("INVALID_RESPONSE", "A resource row omitted its ID.", EXIT_INCOMPLETE, attempts)
                key = resource_id.casefold()
                if key in seen_ids:
                    duplicate_count += 1
                    continue
                seen_ids.add(key)
                records.append(_resource_row(item, self.show_identifiers))
            next_token = page.skip_token
            if next_token is None:
                break
            if next_token in seen_tokens:
                raise InventoryError("PAGINATION_LOOP", "Azure Resource Graph repeated a continuation token.", EXIT_INCOMPLETE)
            seen_tokens.add(next_token)
            skip_token = next_token
        else:
            return self._result(records, pages, total_records, page_row_count, duplicate_count, warnings, complete=False, error={
                "code": "PAGE_LIMIT_REACHED", "message": "max-pages was reached while Azure Resource Graph still returned a continuation token."
            })

        complete = True
        error = None
        if duplicate_count:
            warnings.append("duplicate resource IDs appeared across pages; concurrent inventory changes may have shifted results")
        if total_changed:
            complete = False
            error = {"code": "TOTAL_CHANGED", "message": "Azure Resource Graph total_records changed during pagination."}
        elif duplicate_count:
            complete = False
            error = {"code": "DUPLICATE_IDS", "message": "Duplicate resource IDs appeared across pages; completeness cannot be established."}
        elif total_records is not None and len(records) != total_records:
            complete = False
            error = {"code": "COUNT_MISMATCH", "message": "Unique resource count did not match Azure Resource Graph total_records."}
        elif total_records is None and page_row_count == pages * self.page_size:
            complete = False
            error = {"code": "TOTAL_UNKNOWN", "message": "A full final page had no continuation token or total_records; completeness cannot be established."}
        return self._result(records, pages, total_records, page_row_count, duplicate_count, warnings, complete, error)

    def _result(
        self,
        records: list[dict[str, Any]],
        pages: int,
        total_records: int | None,
        page_row_count: int,
        duplicate_count: int,
        warnings: list[str],
        complete: bool,
        error: dict[str, str] | None,
    ) -> dict[str, Any]:
        result: dict[str, Any] = {
            "schema_version": 1,
            "ok": complete,
            "status": "complete" if complete and records else "empty" if complete else "incomplete",
            "scope": {"subscription_id": self.subscription_id, "resource_group": self.resource_group},
            "query": "Azure Resource Graph Resources; projected inventory fields only",
            "pagination": {
                "page_size": self.page_size,
                "pages": pages,
                "rows_received": page_row_count,
                "unique_resources": len(records),
                "reported_total_records": total_records,
                "duplicate_ids": duplicate_count,
                "point_in_time_snapshot": False,
            },
            "identifier_redaction": "sha256-prefix" if not self.show_identifiers else "disabled-by-explicit-option",
            "warnings": warnings,
            "resources": records,
            "collected_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        }
        if error is not None:
            result["error"] = error
        return result


class _ArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        self.print_usage(sys.stderr)
        self.exit(EXIT_USAGE, f"{self.prog}: error: {message}\n")


def build_parser() -> argparse.ArgumentParser:
    parser = _ArgumentParser(description="Read-only, explicitly scoped Azure Resource Graph inventory.")
    parser.add_argument("--subscription-id", required=True, help="Required subscription UUID; the default Azure subscription is never used.")
    parser.add_argument("--resource-group", help="Optional resource-group name filter within the required subscription.")
    parser.add_argument("--page-size", type=int, default=1000, help="ARG page size (1–1000; default: 1000).")
    parser.add_argument("--max-pages", type=int, default=100, help="Maximum page count (1–100; default: 100).")
    parser.add_argument("--timeout", type=float, default=30.0, help="Timeout in seconds per page request (1–300; default: 30).")
    parser.add_argument("--retries", type=int, default=3, help="Retries for transient/timeout failures (0–5; default: 3).")
    parser.add_argument("--show-resource-identifiers", action="store_true", help="Include resource IDs/names; default output uses stable redacted references.")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        inventory = AzureInventory(
            subscription_id=args.subscription_id,
            resource_group=args.resource_group,
            page_size=args.page_size,
            max_pages=args.max_pages,
            timeout=args.timeout,
            retries=args.retries,
            show_identifiers=args.show_resource_identifiers,
        )
        result = inventory.collect()
    except InventoryError as exc:
        print(json.dumps({
            "schema_version": 1,
            "ok": False,
            "status": "error",
            "error": {"code": exc.code, "message": str(exc), "attempts": exc.attempts},
        }, ensure_ascii=False, sort_keys=True))
        return exc.exit_code
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    if not result["ok"]:
        return EXIT_INCOMPLETE
    return EXIT_EMPTY if result["status"] == "empty" else EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
