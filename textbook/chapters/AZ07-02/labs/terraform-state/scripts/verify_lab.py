"""Run real local Terraform lock, drift, and state-recovery checks in isolation.

The script copies only this lab's configuration and helper scripts to a fresh
system temporary directory. It never opens or overwrites Terraform state in the
repository checkout and never configures an Azure provider or backend.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path

SOURCE_ROOT = Path(__file__).resolve().parents[1]
COMMAND_TIMEOUT_SECONDS = 60
HOLDER_TIMEOUT_SECONDS = 90
RUN_TIMEOUT_SECONDS = 600
PYTHON = sys.executable


class VerificationError(RuntimeError):
    """The local Terraform verification did not meet its expected contract."""


def remaining(deadline: float) -> float:
    value = deadline - time.monotonic()
    if value <= 0:
        raise VerificationError("verification exceeded its 10-minute runtime limit")
    return min(COMMAND_TIMEOUT_SECONDS, value)


def record(title: str, output: str, log: Path) -> None:
    safe_output = output.rstrip()
    with log.open("a", encoding="utf-8") as stream:
        stream.write(f"\n===== {title} =====\n{safe_output}\n")
    print(f"\n===== {title} =====\n{safe_output}", flush=True)


def cli(
    run_root: Path,
    log: Path,
    deadline: float,
    *args: str,
    expected: set[int] | None = None,
    suppress_output: bool = False,
) -> subprocess.CompletedProcess[str]:
    title = "terraform " + " ".join(args)
    try:
        result = subprocess.run(
            ["terraform", *args],
            cwd=run_root,
            text=True,
            encoding="utf-8",
            errors="replace",
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=remaining(deadline),
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise VerificationError(f"{title} exceeded its bounded command timeout") from exc
    shown = "<state contents suppressed>" if suppress_output else result.stdout
    record(title, shown, log)
    if expected is not None and result.returncode not in expected:
        raise VerificationError(f"{title} exited {result.returncode}; expected {sorted(expected)}")
    return result


def release_holder(run_root: Path, log: Path) -> bool:
    try:
        result = subprocess.run(
            [PYTHON, str(run_root / "scripts" / "release_state_lock.py")],
            cwd=run_root,
            text=True,
            encoding="utf-8",
            errors="replace",
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=10,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        record("release local lock gate", f"release helper failed: {exc}", log)
        return False
    record("release local lock gate", result.stdout, log)
    return result.returncode == 0


def copy_lab(run_root: Path) -> None:
    shutil.copy2(SOURCE_ROOT / "main.tf", run_root / "main.tf")
    shutil.copy2(SOURCE_ROOT / ".terraform.lock.hcl", run_root / ".terraform.lock.hcl")
    scripts = run_root / "scripts"
    scripts.mkdir()
    for name in ("hold_state_lock.py", "release_state_lock.py"):
        shutil.copy2(SOURCE_ROOT / "scripts" / name, scripts / name)
    (run_root / "work").mkdir()


def execute(run_root: Path, log: Path, deadline: float) -> None:
    cli(run_root, log, deadline, "version", expected={0})
    cli(run_root, log, deadline, "init", "-input=false", "-no-color", expected={0})
    cli(run_root, log, deadline, "apply", "-auto-approve", "-no-color", "-var", "hold_lock=false", expected={0})

    cli(
        run_root,
        log,
        deadline,
        "import",
        "-input=false",
        "-no-color",
        "-var=import_enabled=true",
        "terraform_data.imported[0]",
        "synthetic-existing-state-id",
        expected={0},
    )
    cli(
        run_root,
        log,
        deadline,
        "plan",
        "-no-color",
        "-detailed-exitcode",
        "-var=import_enabled=true",
        expected={0},
    )
    imported_state = cli(run_root, log, deadline, "state", "list", expected={0})
    if "terraform_data.imported[0]" not in imported_state.stdout:
        raise VerificationError("import did not add the expected local resource address to State")
    cli(run_root, log, deadline, "state", "rm", "-no-color", "terraform_data.imported[0]", expected={0})
    record("local import and state removal", "Terraform imported a state-only terraform_data identity, produced a no-diff plan, then removed the State address.", log)

    holder = subprocess.Popen(
        ["terraform", "apply", "-auto-approve", "-no-color", "-var", "hold_lock=true"],
        cwd=run_root,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        bufsize=1,
    )
    if holder.stdout is None:
        holder.kill()
        holder.wait(timeout=10)
        raise VerificationError("could not capture the lock-holder output")

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
    released = False
    try:
        wait_for_gate = min(HOLDER_TIMEOUT_SECONDS, max(0.1, deadline - time.monotonic()))
        if not opened.wait(timeout=wait_for_gate):
            raise VerificationError("Terraform did not reach the actual local provisioner gate")

        contender = cli(
            run_root,
            log,
            deadline,
            "plan",
            "-no-color",
            "-lock-timeout=0s",
            "-var",
            "hold_lock=true",
            expected={1},
        )
        if "lock" not in contender.stdout.casefold():
            raise VerificationError("competing Terraform CLI failed without a state-lock diagnostic")
        if not release_holder(run_root, log):
            raise VerificationError("could not release the interactive Terraform lock holder")
        released = True
        try:
            holder_exit = holder.wait(timeout=min(HOLDER_TIMEOUT_SECONDS, max(0.1, deadline - time.monotonic())))
        except subprocess.TimeoutExpired as exc:
            raise VerificationError("Terraform apply did not finish after releasing the lock gate") from exc
        reader.join(timeout=5)
        holder_output = "".join(lines)
        record("lock-holder apply completion", holder_output, log)
        if holder_exit != 0:
            raise VerificationError(f"lock-holder apply exited {holder_exit}")
    finally:
        if holder.poll() is None:
            if opened.is_set() and not released:
                released = release_holder(run_root, log)
            if holder.poll() is None:
                holder.terminate()
                try:
                    holder.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    holder.kill()
                    holder.wait(timeout=5)
        reader.join(timeout=5)
        if holder.stdout is not None:
            holder.stdout.close()
        if holder.poll() is not None and holder.returncode != 0:
            record("lock-holder final output", "".join(lines), log)

    cli(run_root, log, deadline, "apply", "-auto-approve", "-no-color", "-var", "hold_lock=false", expected={0})

    marker = run_root / "work" / "managed-marker.txt"
    marker.write_text("managed=outside-change\n", encoding="utf-8")
    drift_plan = cli(run_root, log, deadline, "plan", "-no-color", "-detailed-exitcode", expected={2})
    if "local_file.marker" not in drift_plan.stdout:
        raise VerificationError("drift plan did not identify the local_file resource")

    cli(run_root, log, deadline, "apply", "-auto-approve", "-no-color", "-refresh-only", expected={0})
    if marker.read_text(encoding="utf-8") != "managed=outside-change\n":
        raise VerificationError("refresh-only unexpectedly changed the local object")
    cli(run_root, log, deadline, "plan", "-no-color", "-detailed-exitcode", expected={2})
    cli(run_root, log, deadline, "apply", "-auto-approve", "-no-color", expected={0})
    if marker.read_text(encoding="utf-8") != "managed=terraform\n":
        raise VerificationError("normal apply did not restore the declared file content")

    main_tf = run_root / "main.tf"
    original_configuration = main_tf.read_text(encoding="utf-8")
    candidate_configuration = original_configuration.replace(
        'default     = "managed=terraform\\n"',
        'default     = "managed=rollback-candidate\\n"',
        1,
    )
    if candidate_configuration == original_configuration:
        raise VerificationError("configuration rollback fixture could not find the expected source value")
    main_tf.write_text(candidate_configuration, encoding="utf-8")
    cli(run_root, log, deadline, "plan", "-no-color", "-detailed-exitcode", expected={2})
    cli(run_root, log, deadline, "apply", "-auto-approve", "-no-color", expected={0})
    if marker.read_text(encoding="utf-8") != "managed=rollback-candidate\n":
        raise VerificationError("candidate configuration did not update the disposable local object")
    main_tf.write_text(original_configuration, encoding="utf-8")
    cli(run_root, log, deadline, "plan", "-no-color", "-detailed-exitcode", expected={2})
    cli(run_root, log, deadline, "apply", "-auto-approve", "-no-color", expected={0})
    if marker.read_text(encoding="utf-8") != "managed=terraform\n":
        raise VerificationError("restoring the previous declaration did not restore the local object")
    record("configuration rollback", "Restoring the prior HCL declaration produced a new plan and reconciled the local marker.", log)

    state_backup = run_root / "work" / "state-backup.json"
    pulled = cli(
        run_root,
        log,
        deadline,
        "state",
        "pull",
        expected={0},
        suppress_output=True,
    )
    state_backup.write_text(pulled.stdout, encoding="utf-8")
    state = json.loads(pulled.stdout)
    if not state.get("lineage") or not isinstance(state.get("serial"), int):
        raise VerificationError("pulled state did not contain lineage and serial")
    record("state backup identity", f"lineage={state['lineage']}\nserial={state['serial']}", log)

    state_path = run_root / "terraform.tfstate"
    lost_copy = run_root / "work" / "state-before-recovery.json"
    if not state_path.is_file():
        raise VerificationError("expected local state file is missing before recovery")
    os.replace(state_path, lost_copy)
    empty = cli(run_root, log, deadline, "state", "list", expected={1})
    if "no state file was found" not in empty.stdout.casefold():
        raise VerificationError("missing local state did not fail closed as expected")
    cli(run_root, log, deadline, "state", "push", str(state_backup), expected={0})
    listed = cli(run_root, log, deadline, "state", "list", expected={0})
    if "local_file.marker" not in listed.stdout:
        raise VerificationError("state push did not restore the marker binding")
    cli(run_root, log, deadline, "plan", "-no-color", "-detailed-exitcode", expected={0})
    if marker.read_text(encoding="utf-8") != "managed=terraform\n":
        raise VerificationError("State recovery changed the local file unexpectedly")

    cli(run_root, log, deadline, "destroy", "-auto-approve", "-no-color", expected={0})
    if marker.exists():
        raise VerificationError("Terraform destroy left the disposable marker file behind")
    record(
        "verification summary",
        f"terraform={subprocess.run(['terraform', 'version'], capture_output=True, text=True, timeout=10).stdout.splitlines()[0]}\n"
        "provider=hashicorp/local 2.9.1\nactual_local_lock_contention=PASS\n"
        "provider_read_drift_and_reconcile=PASS\nlocal_import_and_unbind=PASS\n"
        "configuration_rollback=PASS\nstate_backup_and_restore=PASS\n"
        "azure_calls=NONE\nstate_artifacts=isolated_temp_directory_and_removed",
        log,
    )


def main() -> int:
    deadline = time.monotonic() + RUN_TIMEOUT_SECONDS
    with tempfile.TemporaryDirectory(prefix="azure-cloudops-az07-02-") as temp_dir:
        run_root = Path(temp_dir)
        log = run_root / "verification.log"
        log.write_text("AZ07-02 local-only Terraform evidence; Azure calls: none.\n", encoding="utf-8")
        copy_lab(run_root)
        execute(run_root, log, deadline)
    print("ISOLATED_TEMPORARY_LAB_CLEANED: no Terraform state or marker was left in the checkout.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"VERIFICATION FAILED: {exc}", file=sys.stderr)
        raise SystemExit(1)
