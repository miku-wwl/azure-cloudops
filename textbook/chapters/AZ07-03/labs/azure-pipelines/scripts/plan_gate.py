#!/usr/bin/env python3
"""Fail-closed integrity checks for the AZ07-03 synthetic plan-contract lab.

This script checks artifact bytes and metadata. It does not authenticate an
approver, call Azure DevOps, parse a Terraform plan, or authorize Azure access.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


class ContractError(ValueError):
    """Raised when any expected plan or approval field fails closed."""


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractError(f"cannot read JSON contract: {path.name}") from exc
    if not isinstance(value, dict):
        raise ContractError(f"contract root must be an object: {path.name}")
    return value


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    try:
        with path.open("rb") as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(block)
    except OSError as exc:
        raise ContractError(f"cannot read required file: {path.name}") from exc
    return digest.hexdigest()


def _utc(value: Any, field: str) -> datetime:
    if not isinstance(value, str):
        raise ContractError(f"{field} must be an ISO-8601 timestamp")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ContractError(f"{field} must be an ISO-8601 timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ContractError(f"{field} must include a timezone")
    return parsed.astimezone(timezone.utc)


def verify_contract(
    *,
    plan_path: Path,
    manifest_path: Path,
    approval_path: Path,
    lock_path: Path,
    expected_commit: str,
    expected_target: str,
    now: datetime | None = None,
) -> None:
    manifest = _read_json(manifest_path)
    approval = _read_json(approval_path)
    now = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)

    required_manifest = {
        "schema_version",
        "run_id",
        "source_commit",
        "target_scope",
        "provider_lock_sha256",
        "plan_sha256",
        "created_utc",
        "expires_utc",
        "created_by",
    }
    required_approval = {
        "schema_version",
        "run_id",
        "source_commit",
        "target_scope",
        "provider_lock_sha256",
        "plan_sha256",
        "approved_by",
        "approved_utc",
        "expires_utc",
    }
    if not required_manifest.issubset(manifest):
        raise ContractError("plan manifest is incomplete")
    if not required_approval.issubset(approval):
        raise ContractError("approval record is incomplete")
    if manifest["schema_version"] != 1 or approval["schema_version"] != 1:
        raise ContractError("unsupported contract schema")

    commit = manifest["source_commit"]
    if not isinstance(commit, str) or not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise ContractError("manifest source_commit must be a 40-character Git SHA")
    if commit != expected_commit or approval["source_commit"] != expected_commit:
        raise ContractError("source commit does not match the approved run")
    if manifest["target_scope"] != expected_target or approval["target_scope"] != expected_target:
        raise ContractError("target scope does not match the approved run")
    if not isinstance(manifest["run_id"], str) or not manifest["run_id"]:
        raise ContractError("run_id is required")
    if approval["run_id"] != manifest["run_id"]:
        raise ContractError("approval belongs to a different pipeline run")

    plan_digest = _sha256(plan_path)
    lock_digest = _sha256(lock_path)
    if manifest["plan_sha256"] != plan_digest or approval["plan_sha256"] != plan_digest:
        raise ContractError("plan bytes do not match the reviewed digest")
    if manifest["provider_lock_sha256"] != lock_digest or approval["provider_lock_sha256"] != lock_digest:
        raise ContractError("provider lock file does not match the reviewed digest")

    creator = manifest["created_by"]
    approver = approval["approved_by"]
    if not isinstance(creator, str) or not creator or not isinstance(approver, str) or not approver:
        raise ContractError("creator and approver identifiers are required")
    if creator.casefold() == approver.casefold():
        raise ContractError("plan creator cannot approve the same plan")

    created = _utc(manifest["created_utc"], "created_utc")
    expires = _utc(manifest["expires_utc"], "expires_utc")
    approved = _utc(approval["approved_utc"], "approved_utc")
    approval_expires = _utc(approval["expires_utc"], "approval.expires_utc")
    if expires != approval_expires:
        raise ContractError("approval expiry differs from the plan expiry")
    if expires <= created or expires - created > timedelta(hours=4):
        raise ContractError("plan validity window must be positive and no longer than four hours")
    if created > now or approved < created or approved > now or now >= expires:
        raise ContractError("plan approval is premature, future-dated, or expired")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--approval", type=Path, required=True)
    parser.add_argument("--lock-file", type=Path, required=True)
    parser.add_argument("--expected-commit", required=True)
    parser.add_argument("--expected-target", required=True)
    args = parser.parse_args()
    try:
        verify_contract(
            plan_path=args.plan,
            manifest_path=args.manifest,
            approval_path=args.approval,
            lock_path=args.lock_file,
            expected_commit=args.expected_commit,
            expected_target=args.expected_target,
        )
    except ContractError as exc:
        print(f"DENY: {exc}", file=sys.stderr)
        return 1
    print("PASS: plan bytes, lock digest, source, scope, run, approver and expiry agree")
    print("LIMIT: this local verifier does not authenticate the approval record")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
