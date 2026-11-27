#!/usr/bin/env python3
"""Check curriculum, editable sources, local Markdown references and E9 catalogue."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
EXCLUDED = {"build", ".terraform", ".pytest_cache", "__pycache__", "dist"}
FIELD_LABELS = {
    "Lab ID",
    "Associated lecture",
    "Associated incident IDs",
    "Deployment architecture",
    "Required permissions",
    "Region and SKU",
    "Terraform root module",
    "Resource list",
    "Estimated cost",
    "Maximum lifetime",
    "Baseline probes",
    "Fault injection",
    "Diagnostics",
    "Recovery",
    "Teardown",
    "Residual-resource checks",
    "Delayed billing checks",
    "Classification",
}
EXPECTED_LABS = {"LAB-L0-01", *(f"LAB-IR-{n:02}" for n in range(1, 13))}
ALLOWED_CLASSIFICATIONS = {
    "Zero-cost read-only",
    "Potentially zero-cost live mutation",
    "Low-cost short-lived experiment",
    "Budget-deferred",
    "Permission-deferred",
    "Enterprise design-only",
}
MD_LINK = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
CURRICULUM_ID = re.compile(r"^\|\s*\d+\s*\|\s*([A-Z]{2,4}\d{2}-\d{2}|FIN-01)\s+—", re.MULTILINE)


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def markdown_target(raw: str) -> str:
    value = raw.strip()
    if value.startswith("<") and ">" in value:
        value = value[1 : value.index(">")]
    else:
        value = value.split(maxsplit=1)[0] if value else ""
    return unquote(value)


def check_curriculum_and_sources() -> int:
    curriculum = (ROOT / "CURRICULUM.md").read_text(encoding="utf-8")
    ids = CURRICULUM_ID.findall(curriculum)
    if len(ids) != 23 or len(set(ids)) != 23:
        fail(f"curriculum must declare 23 unique lecture IDs; found {len(ids)}")

    source_ids = {
        path.name
        for path in (ROOT / "chapters").iterdir()
        if path.is_dir() and (path / "chapter.md").is_file() and (path / "ACCEPTANCE.md").is_file()
    }
    if source_ids != set(ids):
        fail(f"curriculum/source mismatch: missing sources={sorted(set(ids) - source_ids)}, extra={sorted(source_ids - set(ids))}")

    source_map = (ROOT / "SOURCE_MAP.md").read_text(encoding="utf-8")
    missing_map = [lecture for lecture in ids if not re.search(rf"(?<![A-Z0-9]){re.escape(lecture)}(?![A-Z0-9])", source_map)]
    if missing_map:
        fail("source map is missing lecture IDs: " + ", ".join(missing_map))

    pdfs = list((ROOT / "dist" / "pdf").glob("*.pdf"))
    if len(pdfs) != 23:
        fail(f"publication must contain 23 PDFs; found {len(pdfs)}")
    for lecture in ids:
        if len([pdf for pdf in pdfs if pdf.name.startswith(lecture + "_")]) != 1:
            fail(f"expected exactly one PDF beginning with {lecture}_")
    print("PASS: 23 curriculum entries, chapter sources, source-map entries and PDFs")
    return len(ids)


def check_internal_markdown_links() -> int:
    checked = 0
    missing: list[str] = []
    for markdown in ROOT.rglob("*.md"):
        relative = markdown.relative_to(ROOT)
        if set(relative.parts) & EXCLUDED:
            continue
        try:
            content = markdown.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            missing.append(f"{relative}: not UTF-8")
            continue
        for match in MD_LINK.finditer(content):
            target = markdown_target(match.group(1))
            if not target or target.startswith(("#", "//")):
                continue
            parsed = urlsplit(target)
            if parsed.scheme or parsed.netloc or target.startswith("mailto:"):
                continue
            local = parsed.path
            if not local:
                continue
            if local.startswith("/"):
                resolved = (REPO / local.lstrip("/")).resolve()
            else:
                resolved = (markdown.parent / local).resolve()
            checked += 1
            if not resolved.exists():
                missing.append(f"{relative}: {target}")
    if missing:
        fail("broken local Markdown references:\n  " + "\n  ".join(missing[:40]))
    print(f"PASS: {checked} local Markdown file references")
    return checked


def check_e9_catalogue() -> int:
    path = ROOT / "LIVE_LAB_CATALOGUE.md"
    source = path.read_text(encoding="utf-8")
    sections = re.split(r"(?m)^## (LAB-[A-Z0-9-]+)\s+—", source)
    found: dict[str, set[str]] = {}
    for index in range(1, len(sections), 2):
        lab_id = sections[index]
        body = sections[index + 1]
        labels = set(re.findall(r"(?m)^\| ([^|]+) \|", body))
        found[lab_id] = labels
    if set(found) != EXPECTED_LABS:
        fail(f"E9 catalogue ID mismatch: missing={sorted(EXPECTED_LABS - set(found))}, extra={sorted(set(found) - EXPECTED_LABS)}")
    for lab_id, labels in found.items():
        absent = FIELD_LABELS - labels
        if absent:
            fail(f"{lab_id} is missing required fields: {', '.join(sorted(absent))}")
    classes = re.findall(r"(?m)^\| Classification \| \*\*(.*?)\*\* \|$", source)
    if len(classes) != len(EXPECTED_LABS) or set(classes) - ALLOWED_CLASSIFICATIONS:
        fail(f"E9 classification values are incomplete or unsupported: {classes}")
    print(f"PASS: E9 catalogue covers {len(found)} labs with all 18 required fields")
    return len(found)


def main() -> int:
    check_curriculum_and_sources()
    check_internal_markdown_links()
    check_e9_catalogue()
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(main())
