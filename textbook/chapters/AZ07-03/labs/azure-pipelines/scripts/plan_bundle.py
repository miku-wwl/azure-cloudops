#!/usr/bin/env python3
"""Create and verify an exact-plan review bundle outside a repository checkout.

The plan and Terraform show JSON may contain sensitive values. JSON is kept in
memory and is never printed or written; the bundle contains only the binary
plan, a scope/hash manifest, and a redacted resource/output-action summary.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable
import uuid


MAX_PLAN_BYTES = 256 * 1024 * 1024
MAX_PLAN_JSON_BYTES = 64 * 1024 * 1024
MAX_SUMMARY_BYTES = 4 * 1024 * 1024
MAX_CHANGE_ROWS = 10_000
ALLOWED_ACTIONS = {"no-op", "read", "create", "update", "delete"}
ALLOWED_ACTION_SEQUENCES = {
    ("no-op",), ("read",), ("create",), ("update",), ("delete",),
    ("delete", "create"), ("create", "delete"),
}
SHA256_HEX = re.compile(r"^[0-9a-f]{64}$")
GIT_SHA = re.compile(r"^[0-9a-f]{40}$")
PLAN_NAME = "approved.tfplan"
MANIFEST_NAME = "manifest.json"
SUMMARY_NAME = "review-summary.json"
ARTIFACT_FILES = {PLAN_NAME, MANIFEST_NAME, SUMMARY_NAME}
MANIFEST_FIELDS = {
    "schema_version",
    "run_id",
    "source_git_sha",
    "target_environment",
    "subscription_id",
    "resource_group",
    "backend_config_sha256",
    "provider_lock_sha256",
    "plan_sha256",
    "operation",
    "action_count",
    "review_summary_sha256",
    "created_at_utc",
}


class BundleError(ValueError):
    """Raised when the plan bundle is incomplete, altered, or out of scope."""


class _DuplicateJsonProperty(ValueError):
    """Internal signal used to reject ambiguous JSON objects."""


def _object_without_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, item in pairs:
        if key in result:
            raise _DuplicateJsonProperty(key)
        result[key] = item
    return result


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    try:
        with path.open("rb") as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(block)
    except OSError as exc:
        raise BundleError(f"cannot read required file: {path.name}") from exc
    return digest.hexdigest()


def _is_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def _require_outside(path: Path, repository: Path, label: str) -> None:
    if _is_within(path, repository):
        raise BundleError(f"{label} must be outside the repository checkout")


def _read_json(path: Path, label: str, limit: int) -> dict[str, Any]:
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise BundleError(f"cannot read {label}") from exc
    if not raw or len(raw) > limit:
        raise BundleError(f"{label} is empty or exceeds its size limit")
    try:
        value = json.loads(raw.decode("utf-8"), object_pairs_hook=_object_without_duplicates)
    except _DuplicateJsonProperty as exc:
        raise BundleError(f"{label} contains a duplicate JSON property") from exc
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise BundleError(f"{label} is not valid UTF-8 JSON") from exc
    if not isinstance(value, dict):
        raise BundleError(f"{label} root must be an object")
    return value


def load_terraform_plan_json(terraform: str, terraform_root: Path, plan_path: Path) -> dict[str, Any]:
    """Use `terraform show -json` without persisting or logging its sensitive output."""
    try:
        result = subprocess.run(
            [terraform, f"-chdir={terraform_root}", "show", "-json", str(plan_path)],
            check=False,
            capture_output=True,
            timeout=120,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise BundleError("Terraform could not inspect the saved plan") from exc
    if result.returncode != 0 or not result.stdout or len(result.stdout) > MAX_PLAN_JSON_BYTES:
        raise BundleError("Terraform returned an invalid or oversized plan inspection result")
    try:
        value = json.loads(result.stdout, object_pairs_hook=_object_without_duplicates)
    except _DuplicateJsonProperty as exc:
        raise BundleError("Terraform returned plan JSON with a duplicate property") from exc
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise BundleError("Terraform returned invalid plan JSON") from exc
    if not isinstance(value, dict):
        raise BundleError("Terraform plan JSON root must be an object")
    return value


def summarize_plan(plan_json: dict[str, Any]) -> dict[str, Any]:
    """Return only addresses, resource types, and actions; omit all values."""
    if not isinstance(plan_json.get("format_version"), str) or not re.fullmatch(
        r"1\.\d+", plan_json["format_version"]
    ):
        raise BundleError("Terraform returned an unsupported plan JSON format version")
    if (
        plan_json.get("applyable") is not True
        or plan_json.get("complete") is not True
        or plan_json.get("errored") is not False
    ):
        raise BundleError("Terraform plan is incomplete, not applyable, or reports an error")
    changes = plan_json.get("resource_changes")
    if not isinstance(changes, list) or len(changes) > MAX_CHANGE_ROWS:
        raise BundleError("Terraform plan has a missing or oversized resource_changes list")

    counts = {action: 0 for action in sorted(ALLOWED_ACTIONS)}
    rows: list[dict[str, Any]] = []
    action_count = 0
    destructive = False
    for resource in changes:
        if not isinstance(resource, dict):
            raise BundleError("Terraform plan contains an invalid resource change")
        change = resource.get("change")
        if not isinstance(change, dict):
            raise BundleError("Terraform plan contains an invalid resource change")
        actions = change.get("actions")
        if not isinstance(actions, list) or not actions or any(not isinstance(x, str) for x in actions):
            raise BundleError("Terraform plan contains an invalid action list")
        if tuple(actions) not in ALLOWED_ACTION_SEQUENCES:
            raise BundleError("Terraform plan contains an unsupported or unknown resource action")
        address = resource.get("address")
        resource_type = resource.get("type")
        if not isinstance(address, str) or not address or not isinstance(resource_type, str) or not resource_type:
            raise BundleError("Terraform plan change omits its address or resource type")
        for action in actions:
            counts[action] += 1
        action_count += len(actions)
        destructive = destructive or "delete" in actions
        deposed = resource.get("deposed")
        if deposed is not None and (not isinstance(deposed, str) or not deposed):
            raise BundleError("Terraform plan contains an invalid deposed resource key")
        row = {"address": address, "type": resource_type, "actions": actions}
        if deposed is not None:
            row["deposed"] = deposed
        rows.append(row)

    output_changes = plan_json.get("output_changes", {})
    if not isinstance(output_changes, dict) or len(output_changes) > MAX_CHANGE_ROWS:
        raise BundleError("Terraform plan has an invalid or oversized output_changes map")
    output_rows: list[dict[str, Any]] = []
    for name, output in sorted(output_changes.items()):
        if not isinstance(name, str) or not name or not isinstance(output, dict):
            raise BundleError("Terraform plan contains an invalid output change")
        actions = output.get("actions")
        if (
            not isinstance(actions, list)
            or not actions
            or any(not isinstance(action, str) for action in actions)
            or tuple(actions) not in ALLOWED_ACTION_SEQUENCES
        ):
            raise BundleError("Terraform plan contains an unsupported output action sequence")
        output_rows.append({"name": name, "actions": actions})

    return {
        "schema_version": 1,
        "format_version": plan_json["format_version"],
        "counts": counts,
        "action_count": action_count,
        "requires_destructive_approval": destructive,
        "changes": rows,
        "output_change_count": len(output_rows),
        "output_changes": output_rows,
    }


def _validate_context(
    *, source_git_sha: str, run_id: str, target_environment: str, subscription_id: str, resource_group: str
) -> None:
    if not isinstance(source_git_sha, str) or not GIT_SHA.fullmatch(source_git_sha):
        raise BundleError("source Git SHA must be a lowercase 40-character commit ID")
    for label, value in (
        ("run ID", run_id),
        ("target environment", target_environment),
        ("subscription ID", subscription_id),
        ("resource group", resource_group),
    ):
        if not isinstance(value, str) or not value.strip() or len(value) > 256:
            raise BundleError(f"{label} is missing or invalid")


def _validate_plan_scope(plan_json: dict[str, Any], *, subscription_id: str, resource_group: str) -> None:
    variables = plan_json.get("variables")
    if not isinstance(variables, dict):
        raise BundleError("Terraform plan omits its target scope variables")
    subscription = variables.get("target_subscription_id")
    group = variables.get("target_resource_group_name")
    subscription_value = subscription.get("value") if isinstance(subscription, dict) else None
    group_value = group.get("value") if isinstance(group, dict) else None
    try:
        subscription_matches = str(uuid.UUID(subscription_value)).casefold() == str(uuid.UUID(subscription_id)).casefold()
    except (ValueError, TypeError, AttributeError) as exc:
        raise BundleError("Terraform plan or expected target subscription is not a UUID") from exc
    if not subscription_matches:
        raise BundleError("Terraform plan subscription does not match the requested pipeline scope")
    if not isinstance(group_value, str) or group_value.casefold() != resource_group.casefold():
        raise BundleError("Terraform plan resource group does not match the requested pipeline scope")


def _resolve_repository(repository: Path) -> Path:
    try:
        result = repository.resolve(strict=True)
    except OSError as exc:
        raise BundleError("repository path does not exist") from exc
    if not result.is_dir():
        raise BundleError("repository path must be a directory")
    return result


def _resolve_inputs(
    *, repository: Path, terraform_root: Path, lock_file: Path, backend_config: Path, plan_path: Path, output_dir: Path
) -> tuple[Path, Path, Path, Path, Path, Path]:
    if any(path.is_symlink() for path in (terraform_root, lock_file, backend_config, plan_path, output_dir)):
        raise BundleError("plan bundle paths must not be symlinks")
    repo = _resolve_repository(repository)
    try:
        root = terraform_root.resolve(strict=True)
        lock = lock_file.resolve(strict=True)
        backend = backend_config.resolve(strict=True)
        plan = plan_path.resolve(strict=True)
        output = output_dir.resolve(strict=True)
    except OSError as exc:
        raise BundleError("one or more plan-bundle paths are missing") from exc
    if not root.is_dir() or not _is_within(root, repo):
        raise BundleError("Terraform root must be inside the repository checkout")
    if not lock.is_file() or not _is_within(lock, root) or lock.name != ".terraform.lock.hcl":
        raise BundleError("provider lock file must be the Terraform root's .terraform.lock.hcl")
    if not backend.is_file():
        raise BundleError("backend configuration must be a regular file")
    _require_outside(backend, repo, "backend configuration")
    if not plan.is_file() or plan.is_symlink() or plan.name != PLAN_NAME:
        raise BundleError(f"saved plan must be a regular file named {PLAN_NAME}")
    if not output.is_dir() or output.is_symlink():
        raise BundleError("plan bundle output must be a regular directory")
    if not _is_within(plan, output):
        raise BundleError("saved plan must be inside the plan bundle directory")
    _require_outside(plan, repo, "saved plan")
    _require_outside(output, repo, "plan bundle")
    return repo, root, lock, backend, plan, output


def _manifest_from(
    *,
    run_id: str,
    source_git_sha: str,
    target_environment: str,
    subscription_id: str,
    resource_group: str,
    backend_digest: str,
    lock_digest: str,
    plan_digest: str,
    summary_digest: str,
    summary: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "run_id": run_id,
        "source_git_sha": source_git_sha,
        "target_environment": target_environment,
        "subscription_id": subscription_id,
        "resource_group": resource_group,
        "backend_config_sha256": backend_digest,
        "provider_lock_sha256": lock_digest,
        "plan_sha256": plan_digest,
        "operation": "terraform-apply-with-delete" if summary["requires_destructive_approval"] else "terraform-apply",
        "action_count": summary["action_count"],
        "review_summary_sha256": summary_digest,
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }


def _write_json(path: Path, value: dict[str, Any]) -> bytes:
    raw = canonical_json(value) + b"\n"
    if len(raw) > MAX_SUMMARY_BYTES:
        raise BundleError(f"generated artifact exceeds its size limit: {path.name}")
    try:
        with path.open("xb") as stream:
            stream.write(raw)
            stream.flush()
    except OSError as exc:
        raise BundleError(f"cannot create bundle file: {path.name}") from exc
    return raw


def create_bundle(
    *,
    repository: Path,
    terraform_root: Path,
    lock_file: Path,
    backend_config: Path,
    plan_path: Path,
    output_dir: Path,
    source_git_sha: str,
    run_id: str,
    target_environment: str,
    subscription_id: str,
    resource_group: str,
    plan_json_loader: Callable[[Path, Path], dict[str, Any]] | None = None,
    terraform: str = "terraform",
) -> dict[str, Any]:
    _validate_context(
        source_git_sha=source_git_sha,
        run_id=run_id,
        target_environment=target_environment,
        subscription_id=subscription_id,
        resource_group=resource_group,
    )
    repo, root, lock, backend, plan, output = _resolve_inputs(
        repository=repository,
        terraform_root=terraform_root,
        lock_file=lock_file,
        backend_config=backend_config,
        plan_path=plan_path,
        output_dir=output_dir,
    )
    if plan.stat().st_size <= 0 or plan.stat().st_size > MAX_PLAN_BYTES:
        raise BundleError("saved plan is empty or exceeds its size limit")
    if {entry.name for entry in output.iterdir()} != {PLAN_NAME}:
        raise BundleError("plan bundle directory must contain only the saved plan before bundle creation")
    loader = plan_json_loader or (lambda plan_file, root_dir: load_terraform_plan_json(terraform, root_dir, plan_file))
    try:
        plan_json = loader(plan, root)
    except BundleError:
        raise
    except Exception as exc:
        raise BundleError("saved plan inspection failed") from exc
    if not isinstance(plan_json, dict):
        raise BundleError("saved plan inspection did not return a JSON object")
    _validate_plan_scope(plan_json, subscription_id=subscription_id, resource_group=resource_group)
    summary = summarize_plan(plan_json)
    summary_raw = _write_json(output / SUMMARY_NAME, summary)
    manifest = _manifest_from(
        run_id=run_id,
        source_git_sha=source_git_sha,
        target_environment=target_environment,
        subscription_id=subscription_id,
        resource_group=resource_group,
        backend_digest=sha256_file(backend),
        lock_digest=sha256_file(lock),
        plan_digest=sha256_file(plan),
        summary_digest=hashlib.sha256(summary_raw).hexdigest(),
        summary=summary,
    )
    _write_json(output / MANIFEST_NAME, manifest)
    return manifest


def verify_bundle(
    *,
    repository: Path,
    terraform_root: Path,
    lock_file: Path,
    backend_config: Path,
    bundle_dir: Path,
    expected_source_git_sha: str,
    expected_run_id: str,
    expected_target_environment: str,
    expected_subscription_id: str,
    expected_resource_group: str,
    plan_json_loader: Callable[[Path, Path], dict[str, Any]] | None = None,
    terraform: str = "terraform",
) -> dict[str, Any]:
    _validate_context(
        source_git_sha=expected_source_git_sha,
        run_id=expected_run_id,
        target_environment=expected_target_environment,
        subscription_id=expected_subscription_id,
        resource_group=expected_resource_group,
    )
    repo = _resolve_repository(repository)
    if any(path.is_symlink() for path in (terraform_root, lock_file, backend_config, bundle_dir)):
        raise BundleError("verification paths must not be symlinks")
    try:
        root = terraform_root.resolve(strict=True)
        lock = lock_file.resolve(strict=True)
        backend = backend_config.resolve(strict=True)
        bundle = bundle_dir.resolve(strict=True)
    except OSError as exc:
        raise BundleError("one or more verification paths are missing") from exc
    if not root.is_dir() or not _is_within(root, repo):
        raise BundleError("Terraform root must be inside the repository checkout")
    if not lock.is_file() or not _is_within(lock, root) or lock.name != ".terraform.lock.hcl":
        raise BundleError("provider lock file must be the Terraform root's .terraform.lock.hcl")
    if not backend.is_file():
        raise BundleError("backend configuration must be a regular file")
    _require_outside(backend, repo, "backend configuration")
    if not bundle.is_dir() or bundle.is_symlink():
        raise BundleError("plan bundle must be a regular directory")
    _require_outside(bundle, repo, "plan bundle")
    if any(entry.is_symlink() or not entry.is_file() for entry in bundle.iterdir()):
        raise BundleError("plan bundle contains a non-file or symlink")
    if {entry.name for entry in bundle.iterdir()} != ARTIFACT_FILES:
        raise BundleError("plan bundle is missing files or contains unexpected files")
    plan = bundle / PLAN_NAME
    if plan.stat().st_size <= 0 or plan.stat().st_size > MAX_PLAN_BYTES:
        raise BundleError("saved plan is empty or exceeds its size limit")
    manifest = _read_json(bundle / MANIFEST_NAME, "plan manifest", MAX_SUMMARY_BYTES)
    if set(manifest) != MANIFEST_FIELDS or type(manifest.get("schema_version")) is not int or manifest["schema_version"] != 1:
        raise BundleError("plan manifest has a missing, extra, or unsupported field")
    for field, expected in (
        ("run_id", expected_run_id),
        ("source_git_sha", expected_source_git_sha),
        ("target_environment", expected_target_environment),
        ("subscription_id", expected_subscription_id),
        ("resource_group", expected_resource_group),
    ):
        if manifest.get(field) != expected:
            raise BundleError(f"plan manifest {field} does not match the current pipeline scope")
    try:
        created = datetime.fromisoformat(str(manifest["created_at_utc"]).replace("Z", "+00:00"))
    except ValueError as exc:
        raise BundleError("plan manifest creation time is invalid") from exc
    if created.tzinfo is None or created.utcoffset() is None:
        raise BundleError("plan manifest creation time must include a timezone")
    lock_digest = sha256_file(lock)
    plan_digest = sha256_file(plan)
    if manifest.get("provider_lock_sha256") != lock_digest:
        raise BundleError("provider lock file changed after the plan was created")
    if manifest.get("backend_config_sha256") != sha256_file(backend):
        raise BundleError("backend target changed after the plan was created")
    if manifest.get("plan_sha256") != plan_digest:
        raise BundleError("saved plan changed after the plan was created")
    if not SHA256_HEX.fullmatch(str(manifest.get("review_summary_sha256", ""))):
        raise BundleError("review summary digest is invalid")
    summary_path = bundle / SUMMARY_NAME
    summary_raw = summary_path.read_bytes()
    if len(summary_raw) > MAX_SUMMARY_BYTES or hashlib.sha256(summary_raw).hexdigest() != manifest[
        "review_summary_sha256"
    ]:
        raise BundleError("review summary changed after the plan was created")
    summary = _read_json(summary_path, "plan review summary", MAX_SUMMARY_BYTES)
    loader = plan_json_loader or (lambda plan_file, root_dir: load_terraform_plan_json(terraform, root_dir, plan_file))
    try:
        plan_json = loader(plan, root)
    except BundleError:
        raise
    except Exception as exc:
        raise BundleError("saved plan inspection failed") from exc
    if not isinstance(plan_json, dict):
        raise BundleError("saved plan inspection did not return a JSON object")
    _validate_plan_scope(
        plan_json, subscription_id=expected_subscription_id, resource_group=expected_resource_group
    )
    expected_summary = summarize_plan(plan_json)
    if summary != expected_summary:
        raise BundleError("review summary does not match the saved plan")
    expected_operation = (
        "terraform-apply-with-delete" if expected_summary["requires_destructive_approval"] else "terraform-apply"
    )
    if manifest.get("operation") != expected_operation:
        raise BundleError("plan manifest operation does not match the saved plan actions")
    if type(manifest.get("action_count")) is not int or manifest["action_count"] != expected_summary["action_count"]:
        raise BundleError("plan manifest action count does not match the saved plan")
    return manifest


def _add_scope_arguments(parser: argparse.ArgumentParser, *, create: bool) -> None:
    parser.add_argument("--repository", type=Path, required=True)
    parser.add_argument("--terraform-root", type=Path, required=True)
    parser.add_argument("--lock-file", type=Path, required=True)
    parser.add_argument("--backend-config", type=Path, required=True)
    if create:
        parser.add_argument("--plan", type=Path, required=True)
        parser.add_argument("--output-dir", type=Path, required=True)
        parser.add_argument("--source-git-sha", required=True)
        parser.add_argument("--run-id", required=True)
        parser.add_argument("--target-environment", required=True)
        parser.add_argument("--subscription-id", required=True)
        parser.add_argument("--resource-group", required=True)
    else:
        parser.add_argument("--bundle-dir", type=Path, required=True)
        parser.add_argument("--expected-source-git-sha", required=True)
        parser.add_argument("--expected-run-id", required=True)
        parser.add_argument("--expected-target-environment", required=True)
        parser.add_argument("--expected-subscription-id", required=True)
        parser.add_argument("--expected-resource-group", required=True)
    parser.add_argument("--terraform", default="terraform")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    create = commands.add_parser("create", help="write a manifest and redacted review summary")
    _add_scope_arguments(create, create=True)
    verify = commands.add_parser("verify", help="verify the exact plan bundle before controlled apply")
    _add_scope_arguments(verify, create=False)
    args = parser.parse_args()
    try:
        if args.command == "create":
            manifest = create_bundle(
                repository=args.repository,
                terraform_root=args.terraform_root,
                lock_file=args.lock_file,
                backend_config=args.backend_config,
                plan_path=args.plan,
                output_dir=args.output_dir,
                source_git_sha=args.source_git_sha,
                run_id=args.run_id,
                target_environment=args.target_environment,
                subscription_id=args.subscription_id,
                resource_group=args.resource_group,
                terraform=args.terraform,
            )
        else:
            manifest = verify_bundle(
                repository=args.repository,
                terraform_root=args.terraform_root,
                lock_file=args.lock_file,
                backend_config=args.backend_config,
                bundle_dir=args.bundle_dir,
                expected_source_git_sha=args.expected_source_git_sha,
                expected_run_id=args.expected_run_id,
                expected_target_environment=args.expected_target_environment,
                expected_subscription_id=args.expected_subscription_id,
                expected_resource_group=args.expected_resource_group,
                terraform=args.terraform,
            )
    except (BundleError, OSError) as exc:
        print(f"PLAN BUNDLE REJECTED: {exc}", file=sys.stderr)
        return 2
    print(
        f"PLAN BUNDLE {args.command.upper()}: run={manifest['run_id']} "
        f"operation={manifest['operation']} action_count={manifest['action_count']} "
        f"plan_sha256={manifest['plan_sha256']}"
    )
    print("LIMIT: plan summaries omit values; the binary plan remains sensitive and needs restricted artifact access")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
