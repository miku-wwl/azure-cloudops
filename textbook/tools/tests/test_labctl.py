from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


LABCTL = Path(__file__).resolve().parents[1] / "labctl.py"


class LabctlTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_root = tempfile.TemporaryDirectory(prefix="labctl-test-")
        self.base = Path(self.temp_root.name)
        self.env = os.environ.copy()
        self.env.update({"TEMP": str(self.base), "TMP": str(self.base), "TMPDIR": str(self.base), "PYTHONDONTWRITEBYTECODE": "1"})

    def tearDown(self) -> None:
        self.temp_root.cleanup()

    def run_labctl(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(LABCTL), *arguments],
            capture_output=True,
            text=True,
            encoding="utf-8",
            env=self.env,
            timeout=10,
            check=False,
        )

    def setup_run(self) -> tuple[str, str]:
        result = self.run_labctl("setup", "--target-scope", "local")
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(result.stdout)
        return data["run_dir"], data["run_id"]

    def run_command(self, command: str, run_dir: str, *extra: str) -> subprocess.CompletedProcess[str]:
        return self.run_labctl(command, "--target-scope", "local", "--run-dir", run_dir, *extra)

    def test_scope_is_explicit_and_azure_is_rejected(self) -> None:
        self.assertEqual(self.run_labctl("preflight").returncode, 2)
        result = self.run_labctl("preflight", "--target-scope", "azure")
        self.assertEqual(result.returncode, 2)

    def test_preflight_checks_local_runtime_without_azure_calls(self) -> None:
        result = self.run_labctl("preflight", "--target-scope", "local")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["azure_calls"], 0)

    def test_healthy_baseline_and_test(self) -> None:
        run_dir, _ = self.setup_run()
        self.assertEqual(self.run_command("baseline", run_dir).returncode, 0)
        tested = self.run_command("test", run_dir)
        self.assertEqual(tested.returncode, 0, tested.stderr)
        self.assertEqual(json.loads(tested.stdout)["result"], "HEALTHY")

    def test_fault_is_observed_diagnosed_and_recovered_with_same_probe(self) -> None:
        run_dir, _ = self.setup_run()
        self.assertEqual(self.run_command("baseline", run_dir).returncode, 0)
        self.assertEqual(self.run_command("inject", run_dir).returncode, 0)
        failure = self.run_command("test", run_dir)
        self.assertEqual(failure.returncode, 0, failure.stderr)
        self.assertEqual(json.loads(failure.stdout)["result"], "EXPECTED_FAILURE_REPRODUCED")
        self.assertEqual(self.run_command("diagnose", run_dir).returncode, 0)
        recovery = self.run_command("recover", run_dir)
        self.assertEqual(recovery.returncode, 0, recovery.stderr)
        self.assertEqual(json.loads(recovery.stdout)["result"], "RECOVERED")
        self.assertEqual(self.run_command("test", run_dir).returncode, 0)

    def test_reset_returns_faulted_run_to_baseline(self) -> None:
        run_dir, _ = self.setup_run()
        self.assertEqual(self.run_command("baseline", run_dir).returncode, 0)
        self.assertEqual(self.run_command("inject", run_dir).returncode, 0)
        self.assertEqual(self.run_command("reset", run_dir).returncode, 0)
        self.assertEqual(self.run_command("test", run_dir).returncode, 0)

    def test_teardown_requires_exact_run_confirmation(self) -> None:
        run_dir, run_id = self.setup_run()
        wrong = self.run_command("teardown", run_dir, "--confirm-run-id", "wrong")
        self.assertEqual(wrong.returncode, 4)
        self.assertTrue(Path(run_dir).exists())
        correct = self.run_command("teardown", run_dir, "--confirm-run-id", run_id)
        self.assertEqual(correct.returncode, 0, correct.stderr)
        self.assertFalse(Path(run_dir).exists())

    def test_teardown_refuses_injected_fault_until_reset(self) -> None:
        run_dir, run_id = self.setup_run()
        self.assertEqual(self.run_command("baseline", run_dir).returncode, 0)
        self.assertEqual(self.run_command("inject", run_dir).returncode, 0)
        refused = self.run_command("teardown", run_dir, "--confirm-run-id", run_id)
        self.assertEqual(refused.returncode, 4)
        self.assertEqual(self.run_command("reset", run_dir).returncode, 0)
        self.assertEqual(self.run_command("teardown", run_dir, "--confirm-run-id", run_id).returncode, 0)

    def test_residual_lists_unexpected_artifact_and_teardown_refuses_it(self) -> None:
        run_dir, run_id = self.setup_run()
        unexpected = Path(run_dir) / "operator-note.txt"
        unexpected.write_text("preserve me", encoding="utf-8")
        inspect = self.run_command("residual", run_dir)
        self.assertEqual(inspect.returncode, 5)
        self.assertIn("operator-note.txt", inspect.stdout)
        refused = self.run_command("teardown", run_dir, "--confirm-run-id", run_id)
        self.assertEqual(refused.returncode, 4)
        self.assertEqual(unexpected.read_text(encoding="utf-8"), "preserve me")

    def test_residual_scan_is_bounded_and_never_deletes_overflow(self) -> None:
        run_dir, run_id = self.setup_run()
        for index in range(9):
            (Path(run_dir) / f"extra-{index}.txt").write_text("preserve", encoding="utf-8")
        inspect = self.run_command("residual", run_dir)
        self.assertEqual(inspect.returncode, 5)
        self.assertTrue(json.loads(inspect.stdout)["truncated"])
        refused = self.run_command("teardown", run_dir, "--confirm-run-id", run_id)
        self.assertEqual(refused.returncode, 4)
        self.assertTrue(Path(run_dir).exists())

    def test_run_path_outside_owned_temp_root_is_rejected(self) -> None:
        outside = self.base / "not-a-run"
        outside.mkdir()
        result = self.run_command("residual", str(outside))
        self.assertEqual(result.returncode, 4)

    def test_symlinked_run_path_is_rejected_when_supported(self) -> None:
        run_dir, _ = self.setup_run()
        target = Path(run_dir)
        alias = target.parent / (target.name + "-alias")
        try:
            alias.symlink_to(target, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest("directory symlinks are unavailable for this account")
        result = self.run_command("residual", str(alias))
        self.assertEqual(result.returncode, 4)


if __name__ == "__main__":
    unittest.main()
