#!/usr/bin/env python3
"""Run every repository Python test directory with a bounded subprocess timeout."""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path


EXCLUDED_PARTS = {"build", ".terraform", "__pycache__", ".venv", "node_modules", "dist"}
SUMMARY = re.compile(r"^Ran (\d+) tests?\b", re.MULTILINE)
PER_DIRECTORY_TIMEOUT_SECONDS = 300


def discover_directories(root: Path) -> list[Path]:
    result: set[Path] = set()
    runner_file = Path(__file__).resolve()
    for test_file in root.rglob("test_*.py"):
        if test_file.resolve() == runner_file:
            continue
        relative_parts = set(test_file.relative_to(root).parts)
        if relative_parts & EXCLUDED_PARTS:
            continue
        result.add(test_file.parent)
    return sorted(result)


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    directories = discover_directories(root)
    if not directories:
        print("No Python test directories found.", file=sys.stderr)
        return 3
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    total = 0
    failures = 0
    print(f"Python: {sys.version.split()[0]} ({sys.executable})")
    for directory in directories:
        relative = directory.relative_to(root)
        print(f"== Python: {relative}", flush=True)
        try:
            completed = subprocess.run(
                [sys.executable, "-m", "unittest", "-v"],
                cwd=directory,
                env=env,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=PER_DIRECTORY_TIMEOUT_SECONDS,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            failures += 1
            print(f"FAILED: timed out after {PER_DIRECTORY_TIMEOUT_SECONDS}s: {relative}")
            if exc.stdout:
                print(exc.stdout if isinstance(exc.stdout, str) else exc.stdout.decode("utf-8", "replace"))
            if exc.stderr:
                print(exc.stderr if isinstance(exc.stderr, str) else exc.stderr.decode("utf-8", "replace"))
            continue
        transcript = completed.stdout + completed.stderr
        counts = SUMMARY.findall(transcript)
        if counts:
            total += int(counts[-1])
        if not counts or int(counts[-1]) == 0:
            failures += 1
            print(f"FAILED: no tests were discovered in {relative}")
            print(transcript, end="" if transcript.endswith("\n") else "\n")
            continue
        if completed.returncode != 0:
            failures += 1
            print(transcript, end="" if transcript.endswith("\n") else "\n")
    print(f"Python test directories: {len(directories)}; tests: {total}; failed directories: {failures}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
