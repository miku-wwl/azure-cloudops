#!/usr/bin/env python3
"""A deliberately small, local-only lifecycle harness for Azure CloudOps labs.

The bundled SMOKE-LOCAL scenario checks harness safety and command transitions.
It is not an Azure, network, authorization, or service emulator.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import stat
import sys
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


MARKER_NAME = ".labctl-run.json"
FIXTURE_NAME = "fixture.json"
OWNER_MARKER = "azure-cloudops-labctl-v1"
SCENARIO = "SMOKE-LOCAL"
BASELINE = {
    "scenario": SCENARIO,
    "service_state": "healthy",
    "fault": None,
    "probe_result": "synthetic-accepted",
}
FAULT = {
    "scenario": SCENARIO,
    "service_state": "blocked",
    "fault": "local-fixture-mutation",
    "probe_result": "synthetic-denied",
}
MAX_JSON_BYTES = 16 * 1024
MAX_RUN_DIRECTORY_ENTRIES = 8
ALLOWED_FILES = {MARKER_NAME, FIXTURE_NAME}


class LabError(Exception):
    """A safe, user-actionable lab command error."""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def has_reparse_point(path: Path) -> bool:
    try:
        info = path.lstat()
    except FileNotFoundError:
        return False
    marker = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
    return path.is_symlink() or bool(getattr(info, "st_file_attributes", 0) & marker)


def lab_root(create: bool = False) -> Path:
    temp_base = Path(tempfile.gettempdir()).resolve()
    root = temp_base / "azure-cloudops-labs"
    if has_reparse_point(root):
        raise LabError(f"refusing reparse-point lab root: {root}")
    if create:
        root.mkdir(mode=0o700, parents=False, exist_ok=True)
    if root.exists() and not root.is_dir():
        raise LabError(f"lab root is not a directory: {root}")
    return root.resolve(strict=create)


def require_target_scope(target_scope: str) -> None:
    if target_scope != "local":
        raise LabError("only --target-scope local is supported; Azure operations are not implemented")


def write_json(path: Path, value: Any) -> None:
    temp_path = path.with_name(path.name + ".tmp")
    if temp_path.exists() or has_reparse_point(temp_path):
        raise LabError(f"refusing existing temporary write path: {temp_path}")
    payload = json.dumps(value, sort_keys=True, ensure_ascii=False, indent=2) + "\n"
    if len(payload.encode("utf-8")) > MAX_JSON_BYTES:
        raise LabError("refusing to write oversized lab metadata")
    try:
        with temp_path.open("x", encoding="utf-8", newline="\n") as stream:
            stream.write(payload)
        os.replace(temp_path, path)
    finally:
        if temp_path.exists():
            temp_path.unlink()


def read_json(path: Path) -> Any:
    if has_reparse_point(path) or not path.is_file():
        raise LabError(f"expected an owned regular file: {path.name}")
    if path.stat().st_size > MAX_JSON_BYTES:
        raise LabError(f"refusing oversized lab file: {path.name}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise LabError(f"cannot read lab file {path.name}: {exc}") from exc


def output(value: dict[str, Any]) -> None:
    print(json.dumps(value, sort_keys=True, ensure_ascii=False))


def bounded_names(directory: Path, limit: int = MAX_RUN_DIRECTORY_ENTRIES) -> tuple[list[str], bool]:
    names: list[str] = []
    with os.scandir(directory) as entries:
        for entry in entries:
            if len(names) == limit:
                return sorted(names), True
            names.append(entry.name)
    return sorted(names), False


def setup(args: argparse.Namespace) -> int:
    require_target_scope(args.target_scope)
    root = lab_root(create=True)
    run_id = uuid.uuid4().hex
    run_dir = root / f"smoke-{run_id}"
    run_dir.mkdir(mode=0o700, exist_ok=False)
    manifest = {
        "owner_marker": OWNER_MARKER,
        "run_id": run_id,
        "scenario": SCENARIO,
        "target_scope": "local",
        "path": str(run_dir.resolve(strict=True)),
        "status": "setup",
        "baseline_sha256": digest(BASELINE),
        "created_at_utc": utc_now(),
        "updated_at_utc": utc_now(),
        "cloud_resources": False,
    }
    try:
        write_json(run_dir / FIXTURE_NAME, BASELINE)
        write_json(run_dir / MARKER_NAME, manifest)
    except Exception:
        # The directory was just created by this process and is still empty or
        # contains only the two known files. Remove those exact paths only.
        for name in ALLOWED_FILES:
            candidate = run_dir / name
            if candidate.is_file() and not has_reparse_point(candidate):
                candidate.unlink()
        run_dir.rmdir()
        raise
    output({"ok": True, "scenario": SCENARIO, "run_id": run_id, "run_dir": str(run_dir), "target_scope": "local"})
    return 0


def load_run(run_dir_value: str) -> tuple[Path, dict[str, Any], dict[str, Any]]:
    raw = Path(run_dir_value)
    if not raw.is_absolute():
        raise LabError("--run-dir must be an absolute path returned by setup")
    if has_reparse_point(raw):
        raise LabError("refusing a symlink or reparse-point run directory")
    root = lab_root(create=False)
    resolved = raw.resolve(strict=True)
    if resolved.parent != root or not resolved.name.startswith("smoke-"):
        raise LabError("run directory must be a direct child of the tool-owned temporary lab root")
    if not resolved.is_dir():
        raise LabError("run directory is not a directory")
    names, overflow = bounded_names(resolved)
    if overflow:
        raise LabError(f"run directory exceeds the {MAX_RUN_DIRECTORY_ENTRIES}-entry inspection limit")
    entries = set(names)
    unexpected = entries - ALLOWED_FILES
    if unexpected:
        raise LabError(f"unexpected artifacts present; inspect with residual before continuing: {sorted(unexpected)}")
    if entries != ALLOWED_FILES:
        raise LabError("owned marker or fixture is missing; refusing to guess ownership")
    manifest = read_json(resolved / MARKER_NAME)
    fixture = read_json(resolved / FIXTURE_NAME)
    expected_run_id = resolved.name.removeprefix("smoke-")
    if not isinstance(manifest, dict):
        raise LabError("lab marker is not an object")
    if (
        manifest.get("owner_marker") != OWNER_MARKER
        or manifest.get("run_id") != expected_run_id
        or manifest.get("scenario") != SCENARIO
        or manifest.get("target_scope") != "local"
        or manifest.get("cloud_resources") is not False
        or manifest.get("path") != str(resolved)
    ):
        raise LabError("run ownership marker does not match this exact local directory")
    if fixture not in (BASELINE, FAULT):
        raise LabError("fixture differs from the known deterministic smoke states")
    return resolved, manifest, fixture


def update_run(run_dir: Path, manifest: dict[str, Any], fixture: dict[str, Any] | None = None) -> None:
    manifest["updated_at_utc"] = utc_now()
    if fixture is not None:
        write_json(run_dir / FIXTURE_NAME, fixture)
    write_json(run_dir / MARKER_NAME, manifest)


def baseline(args: argparse.Namespace) -> int:
    require_target_scope(args.target_scope)
    run_dir, manifest, fixture = load_run(args.run_dir)
    if fixture != BASELINE:
        raise LabError("baseline check failed; the fixture is not in its healthy state")
    manifest["status"] = "baseline_observed"
    update_run(run_dir, manifest)
    output({"ok": True, "result": "BASELINE_HEALTHY", "probe": BASELINE["probe_result"], "cloud_resources": False})
    return 0


def test(args: argparse.Namespace) -> int:
    require_target_scope(args.target_scope)
    run_dir, manifest, fixture = load_run(args.run_dir)
    if fixture == BASELINE:
        manifest["status"] = "tested" if manifest.get("status") != "recovered" else "recovered"
        update_run(run_dir, manifest)
        output({"ok": True, "result": "HEALTHY", "probe": BASELINE["probe_result"], "evidence_class": "LOCAL_SYNTHETIC"})
        return 0
    if fixture == FAULT and manifest.get("status") in {"fault_injected", "fault_observed"}:
        manifest["status"] = "fault_observed"
        update_run(run_dir, manifest)
        output({"ok": True, "result": "EXPECTED_FAILURE_REPRODUCED", "category": "local_fixture_mutation", "evidence_class": "LOCAL_SYNTHETIC"})
        return 0
    raise LabError("test is not valid in the current lab state; run baseline or inject first")


def inject(args: argparse.Namespace) -> int:
    require_target_scope(args.target_scope)
    run_dir, manifest, fixture = load_run(args.run_dir)
    if fixture != BASELINE or manifest.get("status") not in {"baseline_observed", "tested", "recovered", "reset"}:
        raise LabError("fault injection requires an observed healthy baseline")
    manifest["status"] = "fault_injected"
    update_run(run_dir, manifest, FAULT)
    output({"ok": True, "result": "FAULT_INJECTED", "category": "local_fixture_mutation", "azure_calls": 0})
    return 0


def diagnose(args: argparse.Namespace) -> int:
    require_target_scope(args.target_scope)
    run_dir, manifest, fixture = load_run(args.run_dir)
    if fixture != FAULT or manifest.get("status") not in {"fault_injected", "fault_observed"}:
        raise LabError("diagnosis requires the known injected fault")
    manifest["status"] = "diagnosed"
    manifest["diagnosis"] = "The synthetic fixture is marked blocked; this is not a network or Azure observation."
    update_run(run_dir, manifest)
    output({"ok": True, "root_cause": "local_fixture_mutation", "evidence": "service_state=blocked", "azure_calls": 0})
    return 0


def recover(args: argparse.Namespace) -> int:
    require_target_scope(args.target_scope)
    run_dir, manifest, fixture = load_run(args.run_dir)
    if fixture != FAULT or manifest.get("status") != "diagnosed":
        raise LabError("recovery requires the observed and diagnosed injected fault")
    update_run(run_dir, manifest, BASELINE)
    _, checked_manifest, checked_fixture = load_run(str(run_dir))
    if checked_fixture != BASELINE or digest(checked_fixture) != checked_manifest.get("baseline_sha256"):
        raise LabError("recovery did not restore the exact baseline fixture")
    checked_manifest["status"] = "recovered"
    update_run(run_dir, checked_manifest)
    output({"ok": True, "result": "RECOVERED", "same_probe": BASELINE["probe_result"], "sha256": digest(BASELINE)})
    return 0


def reset(args: argparse.Namespace) -> int:
    require_target_scope(args.target_scope)
    run_dir, manifest, _fixture = load_run(args.run_dir)
    manifest.pop("diagnosis", None)
    manifest["status"] = "reset"
    update_run(run_dir, manifest, BASELINE)
    output({"ok": True, "result": "RESET_TO_BASELINE", "run_id": manifest["run_id"]})
    return 0


def residual(args: argparse.Namespace) -> int:
    require_target_scope(args.target_scope)
    raw = Path(args.run_dir)
    if not raw.is_absolute():
        raise LabError("--run-dir must be an absolute path")
    if has_reparse_point(raw):
        raise LabError("refusing a symlink or reparse-point run directory")
    root = lab_root(create=False)
    run_dir = raw.resolve(strict=False)
    if run_dir.parent != root or not run_dir.name.startswith("smoke-"):
        raise LabError("residual inspection is limited to one direct child of the tool-owned lab root")
    if not run_dir.exists():
        output({"ok": True, "run_dir_exists": False, "local_residuals": [], "cloud_resources": "not_applicable"})
        return 0
    if not run_dir.is_dir():
        raise LabError("run path is not a directory")
    names, truncated = bounded_names(run_dir)
    unexpected = sorted(set(names) - ALLOWED_FILES)
    ok = not truncated and not unexpected
    output({"ok": ok, "run_dir_exists": True, "local_residuals": names, "unexpected": unexpected, "truncated": truncated, "cloud_resources": "not_applicable"})
    return 0 if ok else 5


def teardown(args: argparse.Namespace) -> int:
    require_target_scope(args.target_scope)
    run_dir, manifest, fixture = load_run(args.run_dir)
    if args.confirm_run_id != manifest.get("run_id"):
        raise LabError("teardown requires --confirm-run-id to match this exact run")
    if fixture != BASELINE or manifest.get("status") not in {"setup", "baseline_observed", "tested", "recovered", "reset"}:
        raise LabError("teardown requires a healthy/reset state; recover or reset before cleanup")
    # Delete only the two verified regular files in the owned direct-child run.
    for name in (FIXTURE_NAME, MARKER_NAME):
        path = run_dir / name
        if has_reparse_point(path) or not path.is_file():
            raise LabError(f"refusing to remove non-regular owned artifact: {name}")
    (run_dir / FIXTURE_NAME).unlink()
    (run_dir / MARKER_NAME).unlink()
    run_dir.rmdir()
    output({"ok": True, "result": "LOCAL_RUN_REMOVED", "run_id": manifest["run_id"], "cloud_resources": "not_applicable"})
    return 0


def preflight(args: argparse.Namespace) -> int:
    require_target_scope(args.target_scope)
    repo_root = Path(__file__).resolve().parents[2]
    required_ok = sys.version_info >= (3, 10) and (repo_root / "textbook" / "chapters").is_dir()
    tools = {name: shutil.which(name) is not None for name in ("terraform", "az", "docker", "podman", "kubectl", "kind", "k3d", "azurite")}
    output({"ok": required_ok, "python": sys.version.split()[0], "repo_root": str(repo_root), "optional_local_tools": tools, "azure_authentication_checked": False, "azure_calls": 0, "target_scope": "local"})
    return 0 if required_ok else 3


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Safe local-only lifecycle harness; no Azure operations are implemented.")
    sub = parser.add_subparsers(dest="command", required=True)
    commands = {
        "preflight": preflight,
        "setup": setup,
        "baseline": baseline,
        "test": test,
        "inject": inject,
        "diagnose": diagnose,
        "recover": recover,
        "reset": reset,
        "residual": residual,
        "teardown": teardown,
    }
    for name, handler in commands.items():
        item = sub.add_parser(name)
        item.add_argument("--target-scope", required=True, choices=["local"], help="must be explicitly set; the only supported scope is local")
        if name not in {"preflight", "setup"}:
            item.add_argument("--run-dir", required=True, help="absolute run_dir printed by setup")
        if name == "teardown":
            item.add_argument("--confirm-run-id", required=True, help="must equal the run ID printed by setup")
        item.set_defaults(handler=handler)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = make_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.handler(args))
    except LabError as exc:
        print(f"labctl: {exc}", file=sys.stderr)
        return 4
    except OSError as exc:
        print(f"labctl: local filesystem operation failed: {exc}", file=sys.stderr)
        return 5


if __name__ == "__main__":
    raise SystemExit(main())
