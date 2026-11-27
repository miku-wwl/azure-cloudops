from __future__ import annotations

import re
import subprocess
import sys
import unittest
from pathlib import Path

import yaml


TEXTBOOK = Path(__file__).resolve().parents[2]
REPOSITORY = TEXTBOOK.parent


class Stage2AcceptanceTests(unittest.TestCase):
    def test_repository_manifest_references_and_live_lab_catalogue(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(TEXTBOOK / "tools" / "verify_repository.py")],
            cwd=REPOSITORY,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
            timeout=30,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        self.assertIn("23 curriculum entries", completed.stdout)
        self.assertIn("13 labs with all 18 required fields", completed.stdout)

    def test_workflow_actions_are_pinned_and_cloud_mutations_are_absent(self) -> None:
        workflow = (REPOSITORY / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
        workflow_config = yaml.load(workflow, Loader=yaml.BaseLoader)
        uses = re.findall(r"(?m)^\s+uses:\s+([^\s]+)", workflow)
        self.assertGreaterEqual(len(uses), 4)
        self.assertTrue(all(re.search(r"@[0-9a-f]{40}$", action) for action in uses), uses)
        self.assertIn("repository-and-python", workflow_config["jobs"])
        self.assertIn("terraform", workflow_config["jobs"])
        self.assertIn("powershell", workflow_config["jobs"])
        self.assertIn("secret-scan", workflow_config["jobs"])
        self.assertIn("contents: read", workflow)
        self.assertNotRegex(workflow, r"(?i)\baz\s+(?:login|account\s+set)\b|\bterraform\s+(?:apply|destroy)\b")
        self.assertNotIn("ARM_CLIENT_SECRET", workflow)
        self.assertNotIn("AZURE_CREDENTIALS", workflow)
        self.assertIn("GITLEAKS_ENABLE_COMMENTS: 'false'", workflow)
        self.assertIn("GITLEAKS_ENABLE_UPLOAD_ARTIFACT: 'false'", workflow)
        self.assertEqual(workflow_config["jobs"]["secret-scan"]["permissions"]["pull-requests"], "read")

    def test_dependabot_workflow_dependency_updates_parse(self) -> None:
        dependabot = yaml.load(
            (REPOSITORY / ".github" / "dependabot.yml").read_text(encoding="utf-8"),
            Loader=yaml.BaseLoader,
        )
        ecosystems = {entry["package-ecosystem"] for entry in dependabot["updates"]}
        self.assertEqual(ecosystems, {"github-actions", "pip"})
        self.assertTrue(all(entry["schedule"]["interval"] == "monthly" for entry in dependabot["updates"]))


if __name__ == "__main__":
    unittest.main()
