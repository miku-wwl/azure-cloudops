#!/usr/bin/env python3
"""Apply only a signed, fresh, exact Terraform plan for one approved scope.

The approval signer and trust-store delivery are external trust boundaries.
This program verifies the envelope; it does not create an approver identity,
protect a pipeline environment, or establish Azure authorization.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey


MAX_APPROVAL_AGE = timedelta(minutes=30)
MAX_PLAN_BYTES = 256 * 1024 * 1024
MAX_PLAN_JSON_BYTES = 64 * 1024 * 1024
MAX_JSON_BYTES = 2 * 1024 * 1024
PAYLOAD_FIELDS = {
    "schema_version",
    "approval_id",
    "nonce",
    "key_id",
    "approver_identity",
    "approved_at",
    "expires_at",
    "source_git_sha",
    "target_environment",
    "subscription_id",
    "resource_group",
    "provider_lock_sha256",
    "plan_sha256",
    "operation",
    "run_id",
}
ENVELOPE_FIELDS = {"payload", "signature_b64"}
TRUST_FIELDS = {"schema_version", "signers"}
SIGNER_FIELDS = {
    "key_id",
    "public_key_b64",
    "identities",
    "environments",
    "subscription_ids",
    "resource_groups",
    "operations",
}
ALLOWED_ACTIONS = {"no-op", "read", "create", "update", "delete"}
SAFE_OPERATION = "terraform-apply"
DESTRUCTIVE_OPERATION = "terraform-apply-with-delete"
HEX_SHA = re.compile(r"^(?:[0-9a-fA-F]{40}|[0-9a-fA-F]{64})$")
SHA256_HEX = re.compile(r"^[0-9a-fA-F]{64}$")


class ApprovalError(RuntimeError):
    """An authorization precondition failed closed."""


@dataclass(frozen=True)
class Scope:
    source_git_sha: str
    target_environment: str
    subscription_id: str
    resource_group: str
    provider_lock_sha256: str
    run_id: str


@dataclass(frozen=True)
class Authorization:
    approval_id: str
    nonce: str
    key_id: str
    approver_identity: str
    operation: str
    plan_sha256: str
    provider_lock_sha256: str
    destructive: bool
    action_count: int


def _object_without_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ApprovalError("JSON contains a duplicate property")
        result[key] = value
    return result


def parse_json_bytes(raw: bytes, label: str) -> dict[str, Any]:
    if not raw or len(raw) > MAX_JSON_BYTES:
        raise ApprovalError(f"{label} is empty or exceeds the size limit")
    try:
        value = json.loads(raw.decode("utf-8"), object_pairs_hook=_object_without_duplicates)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ApprovalError(f"{label} is not valid UTF-8 JSON") from exc
    if not isinstance(value, dict):
        raise ApprovalError(f"{label} must contain a JSON object")
    return value


def read_json(path: Path, label: str) -> dict[str, Any]:
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise ApprovalError(f"missing or unreadable {label}") from exc
    return parse_json_bytes(raw, label)


def canonical_json(value: dict[str, Any]) -> bytes:
    try:
        return json.dumps(
            value,
            ensure_ascii=False,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise ApprovalError("approval payload cannot be canonicalized") from exc


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    try:
        with path.open("rb") as stream:
            while chunk := stream.read(1024 * 1024):
                digest.update(chunk)
    except OSError as exc:
        raise ApprovalError(f"missing or unreadable artifact: {path.name}") from exc
    return digest.hexdigest()


def require_external_path(path: Path, repository: Path, label: str) -> Path:
    resolved = path.resolve()
    root = repository.resolve()
    if resolved == root or root in resolved.parents:
        raise ApprovalError(f"{label} must be outside the repository checkout")
    return resolved


def _strings(value: Any, label: str, *, allow_empty: bool = False) -> list[str]:
    if not isinstance(value, list) or (not value and not allow_empty):
        raise ApprovalError(f"trust policy {label} must be a non-empty string list")
    if any(not isinstance(item, str) or not item.strip() for item in value):
        raise ApprovalError(f"trust policy {label} contains an invalid value")
    normalized = [item.casefold() for item in value]
    if len(normalized) != len(set(normalized)):
        raise ApprovalError(f"trust policy {label} contains duplicates")
    return value


def load_trust_store(path: Path, expected_digest: str) -> dict[str, dict[str, Any]]:
    if not SHA256_HEX.fullmatch(expected_digest):
        raise ApprovalError("protected trust-store digest must be a SHA-256 value")
    try:
        trust_bytes = path.read_bytes()
    except OSError as exc:
        raise ApprovalError("missing or unreadable trusted approval key set") from exc
    if sha256_bytes(trust_bytes).casefold() != expected_digest.casefold():
        raise ApprovalError("trusted approval key set does not match its protected digest")
    store = parse_json_bytes(trust_bytes, "trusted approval key set")
    if set(store) != TRUST_FIELDS or type(store.get("schema_version")) is not int or store["schema_version"] != 1:
        raise ApprovalError("trusted approval key set has an unsupported schema")
    signers = store.get("signers")
    if not isinstance(signers, list) or not signers:
        raise ApprovalError("trusted approval key set has no signers")
    result: dict[str, dict[str, Any]] = {}
    for signer in signers:
        if not isinstance(signer, dict) or set(signer) != SIGNER_FIELDS:
            raise ApprovalError("trusted signer entry has an invalid schema")
        key_id = signer["key_id"]
        encoded_key = signer["public_key_b64"]
        if not isinstance(key_id, str) or not key_id.strip() or key_id in result:
            raise ApprovalError("trusted signer key ID is invalid or duplicated")
        if not isinstance(encoded_key, str):
            raise ApprovalError("trusted signer public key is invalid")
        try:
            public_key = base64.b64decode(encoded_key, validate=True)
            public_key = Ed25519PublicKey.from_public_bytes(public_key)
        except (ValueError, TypeError) as exc:
            raise ApprovalError("trusted signer public key is not a valid Ed25519 key") from exc
        parsed = dict(signer)
        parsed["public_key"] = public_key
        for field in ("identities", "environments", "subscription_ids", "resource_groups", "operations"):
            parsed[field] = _strings(parsed[field], field)
        result[key_id] = parsed
    return result


def parse_timestamp(value: Any, label: str) -> datetime:
    if not isinstance(value, str) or not value:
        raise ApprovalError(f"approval {label} is missing")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ApprovalError(f"approval {label} is not an ISO-8601 timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ApprovalError(f"approval {label} must include a timezone")
    return parsed.astimezone(timezone.utc)


def canonical_uuid(value: Any, label: str) -> str:
    if not isinstance(value, str):
        raise ApprovalError(f"approval {label} is missing")
    try:
        parsed = str(uuid.UUID(value))
    except (ValueError, AttributeError) as exc:
        raise ApprovalError(f"approval {label} must be a canonical UUID") from exc
    if parsed != value:
        raise ApprovalError(f"approval {label} must use canonical lowercase UUID form")
    return parsed


def classify_plan(plan: dict[str, Any]) -> tuple[bool, int]:
    format_version = plan.get("format_version")
    if not isinstance(format_version, str) or not re.fullmatch(r"1\.\d+", format_version):
        raise ApprovalError("Terraform returned an unsupported plan JSON format version")
    if (
        plan.get("applyable") is not True
        or plan.get("complete") is not True
        or plan.get("errored") is not False
    ):
        raise ApprovalError("Terraform plan is incomplete, not applyable, or reports an error")
    changes = plan.get("resource_changes")
    if not isinstance(changes, list):
        raise ApprovalError("Terraform plan JSON has no resource_changes list")
    destructive = False
    action_count = 0
    for resource in changes:
        if not isinstance(resource, dict) or not isinstance(resource.get("change"), dict):
            raise ApprovalError("Terraform plan JSON contains an invalid resource change")
        actions = resource["change"].get("actions")
        if not isinstance(actions, list) or not actions or any(not isinstance(action, str) for action in actions):
            raise ApprovalError("Terraform plan JSON contains an invalid action list")
        if not set(actions).issubset(ALLOWED_ACTIONS):
            raise ApprovalError("Terraform plan contains an unsupported or unknown resource action")
        action_count += len(actions)
        destructive = destructive or "delete" in actions
    return destructive, action_count


def verify_plan_scope(plan: dict[str, Any], scope: Scope) -> None:
    variables = plan.get("variables")
    if not isinstance(variables, dict):
        raise ApprovalError("Terraform plan omits its variable scope")
    for name, expected in (
        ("target_subscription_id", scope.subscription_id),
        ("target_resource_group_name", scope.resource_group),
    ):
        entry = variables.get(name)
        value = entry.get("value") if isinstance(entry, dict) else None
        if not isinstance(value, str) or not value:
            raise ApprovalError(f"Terraform plan omits its {name} scope value")
        if name == "target_subscription_id":
            try:
                matches = str(uuid.UUID(value)).casefold() == str(uuid.UUID(expected)).casefold()
            except (ValueError, TypeError, AttributeError) as exc:
                raise ApprovalError("Terraform plan or approved subscription is not a UUID") from exc
        else:
            matches = value.casefold() == expected.casefold()
        if not matches:
            raise ApprovalError(f"Terraform plan {name} does not match the approved target scope")


def _scope_allows(signer: dict[str, Any], field: str, value: str) -> bool:
    return value.casefold() in {item.casefold() for item in signer[field]}


def verify_approval(
    *,
    approval_path: Path,
    trust_store_path: Path,
    trust_store_sha256: str,
    plan_sha256: str,
    plan_json: dict[str, Any],
    scope: Scope,
    now: datetime | None = None,
) -> Authorization:
    envelope = read_json(approval_path, "approval envelope")
    if set(envelope) != ENVELOPE_FIELDS:
        raise ApprovalError("approval envelope must contain only payload and signature_b64")
    payload = envelope.get("payload")
    signature_b64 = envelope.get("signature_b64")
    if not isinstance(payload, dict) or set(payload) != PAYLOAD_FIELDS:
        raise ApprovalError("approval payload has a missing, extra, or unsupported field")
    if type(payload.get("schema_version")) is not int or payload["schema_version"] != 1:
        raise ApprovalError("approval payload has an unsupported schema")

    signers = load_trust_store(trust_store_path, trust_store_sha256)
    key_id = payload.get("key_id")
    if not isinstance(key_id, str) or key_id not in signers:
        raise ApprovalError("approval was signed by an untrusted key")
    signer = signers[key_id]
    if not isinstance(signature_b64, str):
        raise ApprovalError("approval signature is missing")
    try:
        signature = base64.b64decode(signature_b64, validate=True)
        signer["public_key"].verify(signature, canonical_json(payload))
    except (ValueError, TypeError, InvalidSignature) as exc:
        raise ApprovalError("approval signature is invalid") from exc

    approval_id = canonical_uuid(payload.get("approval_id"), "approval_id")
    nonce = canonical_uuid(payload.get("nonce"), "nonce")
    identity = payload.get("approver_identity")
    if not isinstance(identity, str) or not identity.strip():
        raise ApprovalError("approval approver identity is missing")
    if not _scope_allows(signer, "identities", identity):
        raise ApprovalError("approval identity is not authorized by the trusted key policy")

    source_sha = payload.get("source_git_sha")
    if not isinstance(source_sha, str) or not HEX_SHA.fullmatch(source_sha):
        raise ApprovalError("approval source Git SHA is invalid")
    if source_sha.casefold() != scope.source_git_sha.casefold():
        raise ApprovalError("approval source Git SHA does not match this checkout")
    environment = payload.get("target_environment")
    if not isinstance(environment, str) or not environment.strip():
        raise ApprovalError("approval target environment is missing")
    if environment.casefold() != scope.target_environment.casefold():
        raise ApprovalError("approval target environment does not match")
    subscription = payload.get("subscription_id")
    try:
        if str(uuid.UUID(subscription)).casefold() != str(uuid.UUID(scope.subscription_id)).casefold():
            raise ApprovalError("approval subscription does not match")
    except (ValueError, TypeError, AttributeError) as exc:
        raise ApprovalError("target subscription must be a UUID") from exc
    resource_group = payload.get("resource_group")
    if not isinstance(resource_group, str) or resource_group.casefold() != scope.resource_group.casefold():
        raise ApprovalError("approval resource group does not match")

    lock_digest = payload.get("provider_lock_sha256")
    if not isinstance(lock_digest, str) or not SHA256_HEX.fullmatch(lock_digest):
        raise ApprovalError("approval provider lock-file digest is invalid")
    if lock_digest.casefold() != scope.provider_lock_sha256.casefold():
        raise ApprovalError("provider lock-file digest changed after approval")
    if not isinstance(plan_sha256, str) or not SHA256_HEX.fullmatch(plan_sha256):
        raise ApprovalError("exact plan artifact digest is invalid")
    signed_plan_digest = payload.get("plan_sha256")
    if not isinstance(signed_plan_digest, str) or not SHA256_HEX.fullmatch(signed_plan_digest):
        raise ApprovalError("approval plan digest is invalid")
    if signed_plan_digest.casefold() != plan_sha256.casefold():
        raise ApprovalError("plan artifact changed after approval")
    run_id = payload.get("run_id")
    if not isinstance(run_id, str) or not run_id or run_id != scope.run_id:
        raise ApprovalError("approval run ID does not match the current trusted run")

    for field, expected in (
        ("environments", scope.target_environment),
        ("subscription_ids", scope.subscription_id),
        ("resource_groups", scope.resource_group),
    ):
        if not _scope_allows(signer, field, expected):
            raise ApprovalError(f"trusted key policy does not authorize this {field.replace('_', ' ')}")

    destructive, action_count = classify_plan(plan_json)
    expected_operation = DESTRUCTIVE_OPERATION if destructive else SAFE_OPERATION
    operation = payload.get("operation")
    if operation != expected_operation:
        raise ApprovalError("approval operation does not authorize the saved plan actions")
    if operation not in signer["operations"]:
        raise ApprovalError("trusted key policy does not authorize this operation")

    approved_at = parse_timestamp(payload.get("approved_at"), "approval timestamp")
    expires_at = parse_timestamp(payload.get("expires_at"), "expiration")
    current = now or datetime.now(timezone.utc)
    if current.tzinfo is None or current.utcoffset() is None:
        raise ApprovalError("verification clock must be timezone-aware")
    current = current.astimezone(timezone.utc)
    if approved_at > current + timedelta(minutes=2):
        raise ApprovalError("approval timestamp is in the future")
    if expires_at <= current:
        raise ApprovalError("approval has expired")
    if expires_at <= approved_at or expires_at - approved_at > MAX_APPROVAL_AGE:
        raise ApprovalError("approval expiration window is invalid")

    return Authorization(
        approval_id=approval_id,
        nonce=nonce,
        key_id=key_id,
        approver_identity=identity,
        operation=operation,
        plan_sha256=plan_sha256.casefold(),
        provider_lock_sha256=lock_digest.casefold(),
        destructive=destructive,
        action_count=action_count,
    )


def source_git_sha(repository: Path) -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--verify", "HEAD"],
            cwd=repository,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            encoding="utf-8",
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise ApprovalError("could not resolve the checked-out Git commit") from exc
    value = result.stdout.strip()
    if not HEX_SHA.fullmatch(value):
        raise ApprovalError("checked-out Git commit has an invalid SHA")
    try:
        status = subprocess.run(
            ["git", "status", "--porcelain=v1", "--untracked-files=all"],
            cwd=repository,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            encoding="utf-8",
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise ApprovalError("could not check the deployment checkout state") from exc
    if status.stdout.strip():
        raise ApprovalError("controlled apply requires a clean Git checkout")
    return value


def terraform_show_json(terraform: str, terraform_root: Path, plan_path: Path) -> dict[str, Any]:
    env = {
        key: value
        for key, value in os.environ.items()
        if not key.upper().startswith(("ARM_", "AZURE_", "TF_"))
    }
    env["TF_IN_AUTOMATION"] = "1"
    env["TF_INPUT"] = "0"
    try:
        result = subprocess.run(
            [terraform, "show", "-json", str(plan_path)],
            cwd=terraform_root,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=120,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ApprovalError("Terraform could not inspect the saved plan within the time limit") from exc
    if result.returncode != 0 or len(result.stdout) > MAX_PLAN_JSON_BYTES:
        raise ApprovalError("Terraform plan inspection failed or exceeded the JSON size limit")
    try:
        plan = json.loads(result.stdout.decode("utf-8"), object_pairs_hook=_object_without_duplicates)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ApprovalError("Terraform returned invalid plan JSON") from exc
    if not isinstance(plan, dict):
        raise ApprovalError("Terraform plan JSON must contain an object")
    return plan


def terraform_apply(terraform: str, terraform_root: Path, plan_path: Path, timeout: int) -> int:
    env = {key: value for key, value in os.environ.items() if not key.upper().startswith("TF_")}
    forbidden = {
        "ARM_CLIENT_SECRET",
        "ARM_CLIENT_CERTIFICATE",
        "ARM_CLIENT_CERTIFICATE_PATH",
        "ARM_CLIENT_CERTIFICATE_PASSWORD",
        "ARM_ACCESS_KEY",
        "ARM_SAS_TOKEN",
    }
    if any(env.get(name) for name in forbidden):
        raise ApprovalError("controlled apply rejects long-lived Azure credentials")
    if env.get("ARM_USE_CLI", "false").casefold() == "true" or env.get("ARM_USE_MSI", "false").casefold() == "true":
        raise ApprovalError("controlled apply requires the configured federated identity path")
    if not env.get("ARM_CLIENT_ID") or not env.get("ARM_TENANT_ID"):
        raise ApprovalError("controlled apply requires the workload identity client and tenant IDs")
    service_connection_id = env.get("ARM_OIDC_AZURE_SERVICE_CONNECTION_ID") or env.get(
        "AZURESUBSCRIPTION_SERVICE_CONNECTION_ID"
    )
    if not service_connection_id:
        raise ApprovalError("controlled apply requires the approved Azure DevOps workload identity Service Connection")
    env.update(
        {
            "TF_IN_AUTOMATION": "1",
            "TF_INPUT": "0",
            "ARM_USE_CLI": "false",
            "ARM_USE_MSI": "false",
            "ARM_USE_OIDC": "true",
            "ARM_USE_AZUREAD": "true",
            "ARM_OIDC_AZURE_SERVICE_CONNECTION_ID": service_connection_id,
        }
    )
    try:
        result = subprocess.run(
            [terraform, "apply", "-input=false", "-no-color", str(plan_path)],
            cwd=terraform_root,
            env=env,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise ApprovalError("Terraform apply exceeded its configured timeout") from exc
    except OSError as exc:
        raise ApprovalError("Terraform apply could not start") from exc
    return result.returncode


def _scope_lock_id(scope: Scope) -> str:
    key = "\0".join(
        (
            scope.target_environment.casefold(),
            scope.subscription_id.casefold(),
            scope.resource_group.casefold(),
        )
    )
    return sha256_bytes(key.encode("utf-8"))


def execute_controlled_apply(
    *,
    repository: Path,
    terraform_root: Path,
    plan_path: Path,
    approval_path: Path,
    trust_store_path: Path,
    trust_store_sha256: str,
    lock_file: Path,
    control_root: Path,
    scope: Scope,
    plan_loader: Callable[[Path], dict[str, Any]],
    apply_executor: Callable[[Path], int],
) -> tuple[Authorization, int]:
    repository = repository.resolve(strict=True)
    terraform_root = terraform_root.resolve(strict=True)
    if repository == terraform_root or repository not in terraform_root.parents:
        raise ApprovalError("Terraform root must be inside the verified repository")
    lock_file = lock_file.resolve()
    if (
        repository not in lock_file.parents
        or not lock_file.is_file()
        or lock_file != terraform_root / ".terraform.lock.hcl"
    ):
        raise ApprovalError("provider lock file must exist inside the verified repository")
    for path, label in (
        (plan_path, "sensitive saved plan"),
        (approval_path, "approval envelope"),
        (trust_store_path, "trusted approval key set"),
        (control_root, "replay and execution control directory"),
    ):
        require_external_path(path, repository, label)

    if not plan_path.is_file():
        raise ApprovalError("sensitive saved plan is missing")
    if not approval_path.is_file():
        raise ApprovalError("approval envelope is missing")
    if not trust_store_path.is_file():
        raise ApprovalError("trusted approval key set is missing")
    plan_path = plan_path.resolve(strict=True)
    approval_path = approval_path.resolve(strict=True)
    trust_store_path = trust_store_path.resolve(strict=True)
    control_root = control_root.resolve()
    if not plan_path.is_file() or plan_path.stat().st_size <= 0 or plan_path.stat().st_size > MAX_PLAN_BYTES:
        raise ApprovalError("saved plan is missing, empty, or too large")
    lock_root = control_root / "active-locks"
    replay_root = control_root / "used-nonces"
    sealed_root = control_root / "sealed-plans"
    for path in (lock_root, replay_root, sealed_root):
        path.mkdir(parents=True, exist_ok=True)

    scope_lock = lock_root / _scope_lock_id(scope)
    try:
        scope_lock.mkdir(mode=0o700)
    except FileExistsError as exc:
        raise ApprovalError("another controlled Terraform execution holds this target scope") from exc
    lock_owner = scope_lock / "owner.json"
    try:
        lock_owner.write_bytes(
            canonical_json(
                {
                    "run_id": scope.run_id,
                    "scope_lock_id": _scope_lock_id(scope),
                    "acquired_at": datetime.now(timezone.utc).isoformat(),
                }
            )
        )
    except OSError as exc:
        try:
            scope_lock.rmdir()
        except OSError:
            pass
        raise ApprovalError("could not record the active scope-lock owner") from exc

    try:
        with tempfile.TemporaryDirectory(prefix="approved-plan-", dir=sealed_root) as temp_dir:
            sealed_plan = Path(temp_dir) / "approved.tfplan"
            shutil.copyfile(plan_path, sealed_plan)
            try:
                os.chmod(sealed_plan, 0o600)
            except OSError:
                pass
            plan_digest = sha256_file(sealed_plan)
            if sha256_file(plan_path) != plan_digest:
                raise ApprovalError("saved plan changed while it was being sealed")
            provider_lock_digest = sha256_file(lock_file)
            if provider_lock_digest.casefold() != scope.provider_lock_sha256.casefold():
                raise ApprovalError("provider lock file changed after planning")
            plan_json = plan_loader(sealed_plan)
            verify_plan_scope(plan_json, scope)
            authorization = verify_approval(
                approval_path=approval_path,
                trust_store_path=trust_store_path,
                trust_store_sha256=trust_store_sha256,
                plan_sha256=plan_digest,
                plan_json=plan_json,
                scope=scope,
            )
            replay_path = replay_root / sha256_bytes(authorization.nonce.encode("ascii"))
            receipt = {
                "approval_id": authorization.approval_id,
                "approver_identity": authorization.approver_identity,
                "key_id": authorization.key_id,
                "operation": authorization.operation,
                "plan_sha256": authorization.plan_sha256,
                "provider_lock_sha256": authorization.provider_lock_sha256,
                "destructive": authorization.destructive,
                "run_id": scope.run_id,
                "target_environment": scope.target_environment,
                "subscription_id": scope.subscription_id,
                "resource_group": scope.resource_group,
                "scope_lock_id": _scope_lock_id(scope),
                "consumed_at": datetime.now(timezone.utc).isoformat(),
            }
            try:
                descriptor = os.open(replay_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
            except FileExistsError as exc:
                raise ApprovalError("approval nonce has already been consumed") from exc
            with os.fdopen(descriptor, "wb") as stream:
                stream.write(canonical_json(receipt))
                stream.flush()
                os.fsync(stream.fileno())
            if sha256_file(sealed_plan).casefold() != authorization.plan_sha256:
                raise ApprovalError("sealed plan changed before Terraform apply")
            if sha256_file(lock_file).casefold() != authorization.provider_lock_sha256:
                raise ApprovalError("provider lock file changed before Terraform apply")
            result = apply_executor(sealed_plan)
            return authorization, result
    finally:
        try:
            lock_owner.unlink()
        except OSError:
            pass
        try:
            scope_lock.rmdir()
        except OSError:
            # A non-empty or otherwise changed lock is preserved for review.
            pass


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", type=Path, required=True)
    parser.add_argument("--terraform-root", type=Path, required=True)
    parser.add_argument("--plan", type=Path, required=True, help="sensitive saved plan artifact outside the checkout")
    parser.add_argument("--approval", type=Path, required=True, help="signed approval envelope outside the checkout")
    parser.add_argument("--trust-store", type=Path, required=True, help="protected trusted-key file outside the checkout")
    parser.add_argument("--trust-store-sha256", required=True, help="digest supplied by protected pipeline configuration")
    parser.add_argument("--lock-file", type=Path, required=True)
    parser.add_argument("--control-root", type=Path, required=True, help="persistent protected directory outside the checkout")
    parser.add_argument("--environment", required=True)
    parser.add_argument("--subscription-id", required=True)
    parser.add_argument("--resource-group", required=True)
    parser.add_argument("--run-id", required=True, help="must come from the trusted pipeline run context")
    parser.add_argument("--terraform", default="terraform")
    parser.add_argument("--timeout", type=int, default=3600)
    args = parser.parse_args()
    if args.timeout < 1 or args.timeout > 4 * 60 * 60:
        parser.error("--timeout must be between 1 and 14400 seconds")
    repository = args.repository.resolve()
    try:
        commit = source_git_sha(repository)
        lock_path = args.lock_file.resolve(strict=True)
        scope = Scope(
            source_git_sha=commit,
            target_environment=args.environment,
            subscription_id=args.subscription_id,
            resource_group=args.resource_group,
            provider_lock_sha256=sha256_file(lock_path),
            run_id=args.run_id,
        )
        authorization, result = execute_controlled_apply(
            repository=repository,
            terraform_root=args.terraform_root,
            plan_path=args.plan,
            approval_path=args.approval,
            trust_store_path=args.trust_store,
            trust_store_sha256=args.trust_store_sha256,
            lock_file=lock_path,
            control_root=args.control_root,
            scope=scope,
            plan_loader=lambda plan: terraform_show_json(args.terraform, args.terraform_root, plan),
            apply_executor=lambda plan: terraform_apply(args.terraform, args.terraform_root, plan, args.timeout),
        )
    except (ApprovalError, OSError) as exc:
        print(f"CONTROLLED APPLY REJECTED: {exc}", file=sys.stderr)
        return 2
    print(
        "CONTROLLED APPLY VERIFIED: "
        f"approval={authorization.approval_id} operation={authorization.operation} "
        f"actions={authorization.action_count} plan_sha256={authorization.plan_sha256}"
    )
    return result


if __name__ == "__main__":
    raise SystemExit(main())
