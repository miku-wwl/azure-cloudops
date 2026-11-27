#!/usr/bin/env python3
"""Run Terraform format/init/validate/mock tests with Azure credentials removed."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


COMMAND_TIMEOUT_SECONDS = 300


def sanitized_environment(source: dict[str, str] | None = None) -> dict[str, str]:
    """Retain OS process essentials, but remove cloud credentials and Terraform overrides."""
    source = source if source is not None else dict(os.environ)
    result: dict[str, str] = {}
    for name, value in source.items():
        upper = name.upper()
        if upper.startswith(("ARM_", "AZURE_", "TF_")):
            continue
        if upper in {"AZURE_CONFIG_DIR", "AZUREPS_HOST_ENVIRONMENT"}:
            continue
        result[name] = value

    result.update(
        {
            "ARM_USE_CLI": "false",
            "ARM_USE_OIDC": "false",
            "ARM_USE_MSI": "false",
            "ARM_USE_AKS_WORKLOAD_IDENTITY": "false",
            "TF_IN_AUTOMATION": "1",
            "TF_INPUT": "0",
        }
    )
    return result


def test_roots(root: Path) -> list[Path]:
    found: set[Path] = set()
    for test_file in root.rglob("*.tftest.hcl"):
        parts = set(test_file.relative_to(root).parts)
        if {".terraform", "build", "dist"} & parts:
            continue
        if test_file.parent.name == "tests":
            found.add(test_file.parent.parent)
    return sorted(found)


def run_command(terraform: str, arguments: list[str], cwd: Path, env: dict[str, str]) -> bool:
    rendered = " ".join(arguments)
    print(f"  $ terraform {rendered}", flush=True)
    try:
        completed = subprocess.run(
            [terraform, *arguments],
            cwd=cwd,
            env=env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=COMMAND_TIMEOUT_SECONDS,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        print(f"  FAILED: command exceeded {COMMAND_TIMEOUT_SECONDS}s")
        for chunk in (exc.stdout, exc.stderr):
            if chunk:
                print(chunk if isinstance(chunk, str) else chunk.decode("utf-8", "replace"), end="")
        return False

    transcript = completed.stdout + completed.stderr
    if transcript:
        print(transcript, end="" if transcript.endswith("\n") else "\n")
    if completed.returncode != 0:
        print(f"  FAILED: exit {completed.returncode}")
        return False
    return True


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    terraform = shutil.which("terraform")
    if terraform is None:
        print("terraform is required for this check.", file=sys.stderr)
        return 2

    directories = [root / "chapters", root / "terraform"]
    roots = test_roots(root)
    if not roots:
        print("No Terraform test roots with *.tftest.hcl were found.", file=sys.stderr)
        return 3

    env = sanitized_environment()
    failures = 0
    print(f"Terraform: {terraform}")
    print("Azure credentials and TF_* overrides: removed; CLI/OIDC/MSI auth: disabled")

    with tempfile.TemporaryDirectory(prefix="azure-cloudops-tf-cli-") as config_dir:
        cli_config = Path(config_dir) / "terraform.rc"
        cli_config.write_text("", encoding="utf-8")
        env["TF_CLI_CONFIG_FILE"] = str(cli_config)

        for directory in directories:
            if directory.is_dir() and not run_command(terraform, ["fmt", "-check", "-recursive", "-diff", str(directory)], root, env):
                failures += 1

        for terraform_root in roots:
            label = terraform_root.relative_to(root)
            print(f"== Terraform root: {label}", flush=True)
            checks = [
                ["-chdir=" + str(terraform_root), "init", "-backend=false", "-input=false", "-no-color"],
                ["-chdir=" + str(terraform_root), "validate", "-no-color"],
                ["-chdir=" + str(terraform_root), "test", "-no-color"],
            ]
            for command in checks:
                if not run_command(terraform, command, root, env):
                    failures += 1
                    break

    print(f"Terraform test roots: {len(roots)}; failed commands: {failures}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
