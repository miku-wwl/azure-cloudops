"""Offline inventory scope and pagination model for synthetic resources only."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable


HERE = Path(__file__).resolve().parent
FIXTURE = HERE / "fixtures" / "resources.json"


def select_visible_resources(resources: Iterable[dict], requested_subscriptions: Iterable[str]) -> list[dict]:
    """Model one principal's readable rows inside an explicit subscription allowlist."""
    requested = set(requested_subscriptions)
    return sorted(
        (dict(row) for row in resources
         if row["subscription_id"] in requested and row["readable"]),
        key=lambda row: row["id"].casefold(),
    )


def page_by_offset(resources: Iterable[dict], offset: int, page_size: int) -> list[dict]:
    """Model a sorted, offset-based page; it is not an Azure token implementation."""
    if not isinstance(offset, int) or isinstance(offset, bool) or offset < 0:
        raise ValueError("offset must be a non-negative integer")
    if not isinstance(page_size, int) or isinstance(page_size, bool) or page_size < 1:
        raise ValueError("page_size must be a positive integer")
    ordered = sorted((dict(row) for row in resources), key=lambda row: row["id"].casefold())
    return ordered[offset:offset + page_size]


def paginate_stable(resources: Iterable[dict], page_size: int) -> list[list[dict]]:
    """Split a static synthetic set after sorting by its unique resource ID."""
    if not isinstance(page_size, int) or isinstance(page_size, bool) or page_size < 1:
        raise ValueError("page_size must be a positive integer")
    ordered = sorted((dict(row) for row in resources), key=lambda row: row["id"].casefold())
    return [ordered[start:start + page_size] for start in range(0, len(ordered), page_size)]


def audit_pages(pages: Iterable[Iterable[dict]], expected_ids: Iterable[str]) -> dict:
    """Compare flattened page IDs with a synthetic, independently known fixture set."""
    ids = [row["id"] for page in pages for row in page]
    expected = set(expected_ids)
    observed = set(ids)
    repeated = sorted({resource_id for resource_id in ids if ids.count(resource_id) > 1})
    return {
        "row_count": len(ids),
        "unique_count": len(observed),
        "duplicate_ids": repeated,
        "missing_ids": sorted(expected - observed),
        "unexpected_ids": sorted(observed - expected),
    }


def load_fixture() -> dict:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def main() -> None:
    data = load_fixture()
    rows = select_visible_resources(data["resources"], data["requested_subscriptions"])
    pages = paginate_stable(rows, data["page_size"])
    expected = [row["id"] for row in rows]
    print(f"requested subscriptions: {', '.join(data['requested_subscriptions'])}")
    print(f"visible synthetic rows: {len(rows)}; pages: {len(pages)}; page size: {data['page_size']}")
    for page_number, page in enumerate(pages, start=1):
        print(f"page {page_number}: " + ", ".join(row["name"] for row in page))
    print("page audit: " + json.dumps(audit_pages(pages, expected), ensure_ascii=False, sort_keys=True))
    print("scope note: unreadable fixture objects are omitted; live RBAC and ARG are not queried")


if __name__ == "__main__":
    main()
