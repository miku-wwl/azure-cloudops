"""Run the local lock, drift, and State recovery exercise with real Terraform CLI."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import threading
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / "work"
LOG = WORK / "verification.log"
PYTHON = sys.executable


def record(title: str, output: str) -> None:
    with LOG.open("a", encoding="utf-8") as stream:
        stream.write(f"\n===== {title} =====\n{output.rstrip()}\n")
    print(f"\n===== {title} =====\n{output.rstrip()}", flush=True)


def cli(*args: str, expected: set[int] | None = None) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        ["terraform", *args], cwd=ROOT, text=True, encoding="utf-8", errors="replace",
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
    )
    record("terraform " + " ".join(args), result.stdout)
    if expected is not None and result.returncode not in expected:
        raise RuntimeError(f"unexpected exit {result.returncode}; expected {expected}")
    return result


def main() -> int:
    WORK.mkdir(exist_ok=True)
    LOG.write_text("AZ07-02 local Terraform evidence; no Azure provider or endpoint.\n", encoding="utf-8")

    cli("apply", "-auto-approve", "-no-color", "-var", "hold_lock=false", expected={0})
    holder = subprocess.Popen(
        ["terraform", "apply", "-auto-approve", "-no-color", "-var", "hold_lock=true"],
        cwd=ROOT, text=True, encoding="utf-8", errors="replace",
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1,
    )
    assert holder.stdout is not None
    lines: list[str] = []
    opened = threading.Event()

    def stream_holder() -> None:
        assert holder.stdout is not None
        for line in holder.stdout:
            lines.append(line)
            print(line, end="", flush=True)
            if "LOCK_GATE_OPEN" in line:
                opened.set()

    reader = threading.Thread(target=stream_holder, daemon=True)
    reader.start()
    if not opened.wait(timeout=90):
        holder.kill()
        reader.join(timeout=5)
        record("lock-holder apply (failed to open)", "".join(lines))
        raise RuntimeError("Terraform did not reach the actual local provisioner gate")

    contender = cli("plan", "-no-color", "-lock-timeout=0s", "-var", "hold_lock=true", expected={1})
    if "lock" not in contender.stdout.lower():
        raise RuntimeError("competing Terraform CLI failed without a state-lock diagnostic")
    release = subprocess.run(
        [PYTHON, str(ROOT / "scripts" / "release_state_lock.py")], cwd=ROOT,
        text=True, encoding="utf-8", errors="replace", stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    record("release local lock gate", release.stdout)
    if release.returncode != 0:
        holder.kill()
        raise RuntimeError("could not release the interactive Terraform lock holder")
    try:
        holder_exit = holder.wait(timeout=90)
    except subprocess.TimeoutExpired:
        holder.kill()
        raise RuntimeError("Terraform apply did not finish after release")
    reader.join(timeout=5)
    holder_output = "".join(lines)
    record("lock-holder apply completion", holder_output)
    if holder_exit != 0:
        raise RuntimeError(f"lock-holder apply exited {holder_exit}")

    cli("apply", "-auto-approve", "-no-color", "-var", "hold_lock=false", expected={0})

    marker = WORK / "managed-marker.txt"
    marker.write_text("managed=outside-change\n", encoding="utf-8")
    drift_plan = cli("plan", "-no-color", "-detailed-exitcode", expected={2})
    if "local_file.marker" not in drift_plan.stdout:
        raise RuntimeError("drift plan did not identify the local_file resource")

    cli("apply", "-auto-approve", "-no-color", "-refresh-only", expected={0})
    if marker.read_text(encoding="utf-8") != "managed=outside-change\n":
        raise RuntimeError("refresh-only unexpectedly changed the local object")
    cli("plan", "-no-color", "-detailed-exitcode", expected={2})
    cli("apply", "-auto-approve", "-no-color", expected={0})
    if marker.read_text(encoding="utf-8") != "managed=terraform\n":
        raise RuntimeError("normal apply did not restore the declared file content")

    state_backup = WORK / "state-backup.json"
    pulled = cli("state", "pull", expected={0})
    state_backup.write_text(pulled.stdout, encoding="utf-8")
    state = json.loads(pulled.stdout)
    if not state.get("lineage") or not isinstance(state.get("serial"), int):
        raise RuntimeError("pulled state did not contain lineage and serial")
    record("state backup identity", f"lineage={state['lineage']}\nserial={state['serial']}")

    state_path = ROOT / "terraform.tfstate"
    lost_copy = WORK / "state-before-recovery.json"
    os.replace(state_path, lost_copy)
    empty = cli("state", "list", expected={1})
    if "No state file was found" not in empty.stdout:
        raise RuntimeError("missing local state did not fail closed as expected")
    cli("state", "push", str(state_backup), expected={0})
    listed = cli("state", "list", expected={0})
    if "local_file.marker" not in listed.stdout:
        raise RuntimeError("state push did not restore the marker binding")
    cli("plan", "-no-color", "-detailed-exitcode", expected={0})
    if marker.read_text(encoding="utf-8") != "managed=terraform\n":
        raise RuntimeError("State recovery changed the local file unexpectedly")

    cli("destroy", "-auto-approve", "-no-color", expected={0})
    marker.unlink(missing_ok=True)
    record("verification summary", (
        f"terraform={subprocess.run(['terraform', 'version'], capture_output=True, text=True).stdout.splitlines()[0]}\n"
        f"provider=hashicorp/local 2.9.1\nactual_local_lock_contention=PASS\n"
        f"provider_read_drift_and_reconcile=PASS\nstate_backup_and_restore=PASS\n"
        f"azure_calls=NONE\nlineage={state['lineage']}\nserial_before_recovery={state['serial']}"
    ))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"VERIFICATION FAILED: {exc}", file=sys.stderr)
        raise