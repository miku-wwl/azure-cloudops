from __future__ import annotations

import importlib.util
import json
import os
import socket
import subprocess
import tempfile
import time
import unittest
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "live_ir11"
BUILDER = ROOT / "prepare_packages.py"
PROBE = ROOT / "probe.py"
REPO = Path(__file__).resolve().parents[3]

def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module

builder = load_module("ir11_prepare_packages", BUILDER)
probe_module = load_module("ir11_probe", PROBE)

class IR11PackageTests(unittest.TestCase):
    def test_probe_requires_the_expected_status_release_and_boolean_health(self) -> None:
        expected = {"release": "known-good-v1", "healthy": True}
        self.assertTrue(probe_module.matches_expected(200, expected, "known-good-v1"))
        self.assertFalse(probe_module.matches_expected(500, expected, "known-good-v1"))
        self.assertFalse(probe_module.matches_expected(200, {**expected, "healthy": 1}, "known-good-v1"))
        self.assertFalse(probe_module.matches_expected(200, {**expected, "extra": "unexpected"}, "known-good-v1"))

    def test_zips_have_app_files_at_the_archive_root(self) -> None:
        work = REPO / "work"
        work.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=work) as temp:
            out = Path(temp)
            builder.build(out)
            self.assertEqual({"good-v1.zip", "fault-v2.zip"}, {p.name for p in out.glob("*.zip")})
            for path in out.glob("*.zip"):
                with zipfile.ZipFile(path) as archive:
                    self.assertEqual({"package.json", "server.js"}, set(archive.namelist()))
                    manifest = json.loads(archive.read("package.json"))
                    self.assertEqual("24.x", manifest["engines"]["node"])

    def test_same_health_probe_observes_good_bad_good_packages(self) -> None:
        work = REPO / "work"
        work.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=work) as temp:
            out = Path(temp)
            builder.build(out)
            packages = [
                (out / "good-v1.zip", 200, "known-good-v1", True),
                (out / "fault-v2.zip", 500, "intentional-failure-v2", False),
                (out / "good-v1.zip", 200, "known-good-v1", True),
            ]
            for archive, expected_status, release, healthy in packages:
                with tempfile.TemporaryDirectory(dir=work) as app_dir:
                    with zipfile.ZipFile(archive) as package:
                        package.extractall(app_dir)
                    with socket.socket() as sock:
                        sock.bind(("127.0.0.1", 0))
                        port = sock.getsockname()[1]
                    env = os.environ.copy()
                    env["PORT"] = str(port)
                    process = subprocess.Popen(
                        ["node", "server.js"],
                        cwd=app_dir,
                        env=env,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
                    try:
                        observed = None
                        for _ in range(40):
                            try:
                                observed = probe_module.observe(f"http://127.0.0.1:{port}/health", timeout=1)
                                break
                            except (OSError, TimeoutError):
                                if process.poll() is not None:
                                    self.fail("packaged Node server exited before accepting a request")
                                time.sleep(0.1)
                        self.assertIsNotNone(observed, "packaged app did not become ready")
                        status, body = observed
                        self.assertEqual(expected_status, status)
                        self.assertEqual(release, body["release"])
                        self.assertEqual(healthy, body["healthy"])
                    finally:
                        process.terminate()
                        try:
                            process.wait(timeout=3)
                        except subprocess.TimeoutExpired:
                            process.kill()
                            process.wait(timeout=3)

if __name__ == "__main__":
    unittest.main()
