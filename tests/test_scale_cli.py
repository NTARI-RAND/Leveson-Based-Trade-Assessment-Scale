"""Exercise the offline scale guide through all four reference CLIs."""

# SPDX-License-Identifier: AGPL-3.0-or-later

import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
STORE_NAME = "lbtas_ratings.json"
EXPECTED_GUIDE = Path(__file__).with_name("scale-guide.txt").read_text(encoding="utf-8")
VALID_STORE = b"""{
    "scale-test-exchange": {
        "_metadata": {"created": "2026-01-01T00:00:00Z", "total_ratings": 1},
        "reliability": [2], "usability": [], "performance": [], "support": []
    }
}
"""


def require_tool(name):
    executable = shutil.which(name)
    if executable is None:
        raise unittest.SkipTest(f"{name} is not on PATH")
    return executable


def native_cli(directory):
    return directory / ("lbtas.exe" if os.name == "nt" else "lbtas")


class ScaleCliContract:
    """Check guide content, storage independence, and discovery."""

    @classmethod
    def setUpClass(cls):
        """Build this language's CLI once in a temporary directory."""
        output = tempfile.TemporaryDirectory()
        cls.addClassCleanup(output.cleanup)
        cls.command = cls.build_cli(Path(output.name))

    def assert_guide(self, command, directory):
        """Require the whole guide with no prompts or storage diagnostics."""
        result = subprocess.run(
            [*command, "scale"], cwd=directory, stdin=subprocess.DEVNULL,
            capture_output=True, encoding="utf-8", timeout=5,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(result.stderr, "")
        self.assertEqual(result.stdout, EXPECTED_GUIDE)

    def test_guide_with_absent_corrupt_and_valid_stores(self):
        """Guide output and filesystem contents are independent of stored data."""
        stores = {"absent": None, "corrupt": b"{broken json", "valid": VALID_STORE}
        for state, contents in stores.items():
            with self.subTest(store=state):
                with tempfile.TemporaryDirectory() as directory:
                    store = Path(directory) / STORE_NAME
                    if contents is not None:
                        store.write_bytes(contents)
                    self.assert_guide(self.command, directory)
                    if contents is None:
                        self.assertEqual(list(Path(directory).iterdir()), [])
                    else:
                        self.assertEqual(list(Path(directory).iterdir()), [store])
                        self.assertEqual(store.read_bytes(), contents)

    @unittest.skipUnless(hasattr(os, "mkfifo"), "requires POSIX named pipes")
    def test_guide_never_opens_the_store(self):
        """Opening a named pipe for reading would block without a writer."""
        with tempfile.TemporaryDirectory() as directory:
            os.mkfifo(Path(directory) / STORE_NAME)
            self.assert_guide(self.command, directory)

    def test_top_level_help_advertises_scale(self):
        """The usual help entry point makes the guide discoverable."""
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run(
                [*self.command, *self.help_args], cwd=directory, stdin=subprocess.DEVNULL,
                capture_output=True, encoding="utf-8", timeout=5,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertRegex(result.stdout, r"\bscale\b")

    help_args = ()


class PythonScaleTests(ScaleCliContract, unittest.TestCase):
    help_args = ("--help",)

    @staticmethod
    def build_cli(_directory):
        return [sys.executable, str(ROOT / "lbtas.py")]


class GoScaleTests(ScaleCliContract, unittest.TestCase):
    @staticmethod
    def build_cli(directory):
        executable = native_cli(directory)
        subprocess.run([require_tool("go"), "build", "-o", str(executable), "lbtas.go"],
                       cwd=ROOT, check=True)
        return [str(executable)]


class RustScaleTests(ScaleCliContract, unittest.TestCase):
    @staticmethod
    def build_cli(directory):
        cargo = require_tool("cargo")
        # Cargo writes its lockfile beside the manifest, even with --target-dir.
        for name in ("Cargo.toml", "lbtas.rs"):
            shutil.copyfile(ROOT / name, directory / name)
        lockfile = ROOT / "Cargo.lock"
        if lockfile.is_file():
            shutil.copyfile(lockfile, directory / lockfile.name)
        target = directory / "target"
        subprocess.run([cargo, "build", "--target-dir", str(target)], cwd=directory, check=True)
        return [str(native_cli(target / "debug"))]


class TypeScriptScaleTests(ScaleCliContract, unittest.TestCase):
    @staticmethod
    def build_cli(directory):
        node = require_tool("node")
        compiler = ROOT / "node_modules" / "typescript" / "bin" / "tsc"
        if not compiler.is_file():
            raise unittest.SkipTest("install TypeScript dependencies with npm install")
        subprocess.run([node, str(compiler), "--outDir", str(directory)], cwd=ROOT, check=True)
        return [node, str(directory / "lbtas.js")]


if __name__ == "__main__":
    unittest.main()
