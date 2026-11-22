"""Exercise the offline scale guide through all four reference CLIs."""

# SPDX-License-Identifier: AGPL-3.0-or-later

import os
from pathlib import Path
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


class ScaleCliTests(unittest.TestCase):
    """Check guide content, storage independence, and discovery."""

    @classmethod
    def setUpClass(cls):
        """Build the real CLIs once, in a temporary output directory."""
        output = tempfile.TemporaryDirectory()
        cls.addClassCleanup(output.cleanup)
        build_dir = Path(output.name)
        go_cli = build_dir / "lbtas-go"
        rust_dir = build_dir / "rust"
        ts_dir = build_dir / "ts"
        for command in (
            ["go", "build", "-o", str(go_cli), "lbtas.go"],
            ["cargo", "build", "--target-dir", str(rust_dir)],
            ["npm", "run", "build", "--", "--outDir", str(ts_dir)],
        ):
            subprocess.run(command, cwd=ROOT, check=True)
        cls.clis = {
            "Python": [sys.executable, str(ROOT / "lbtas.py")],
            "Go": [str(go_cli)],
            "Rust": [str(rust_dir / "debug" / "lbtas")],
            "TypeScript": ["node", str(ts_dir / "lbtas.js")],
        }

    def assert_guide(self, command, directory):
        """Require the whole guide with no prompts or storage diagnostics."""
        result = subprocess.run(
            [*command, "scale"], cwd=directory, stdin=subprocess.DEVNULL,
            capture_output=True, text=True, timeout=5,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(result.stderr, "")
        self.assertEqual(" ".join(result.stdout.split()), " ".join(EXPECTED_GUIDE.split()))

    def test_guide_with_absent_corrupt_and_valid_stores(self):
        """Guide output and filesystem contents are independent of stored data."""
        stores = {"absent": None, "corrupt": b"{broken json", "valid": VALID_STORE}
        for language, command in self.clis.items():
            for state, contents in stores.items():
                with self.subTest(language=language, store=state):
                    with tempfile.TemporaryDirectory() as directory:
                        store = Path(directory) / STORE_NAME
                        if contents is not None:
                            store.write_bytes(contents)
                        self.assert_guide(command, directory)
                        if contents is None:
                            self.assertEqual(list(Path(directory).iterdir()), [])
                        else:
                            self.assertEqual(list(Path(directory).iterdir()), [store])
                            self.assertEqual(store.read_bytes(), contents)

    @unittest.skipUnless(hasattr(os, "mkfifo"), "requires POSIX named pipes")
    def test_guide_never_opens_the_store(self):
        """Opening a named pipe for reading would block without a writer."""
        for language, command in self.clis.items():
            with self.subTest(language=language):
                with tempfile.TemporaryDirectory() as directory:
                    os.mkfifo(Path(directory) / STORE_NAME)
                    self.assert_guide(command, directory)

    def test_top_level_help_advertises_scale(self):
        """The usual help entry point makes the guide discoverable."""
        for language, command in self.clis.items():
            with self.subTest(language=language):
                with tempfile.TemporaryDirectory() as directory:
                    help_command = [*command, "--help"] if language == "Python" else command
                    result = subprocess.run(
                        help_command, cwd=directory, stdin=subprocess.DEVNULL,
                        capture_output=True, text=True, timeout=5,
                    )
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertRegex(result.stdout, r"\bscale\b")


if __name__ == "__main__":
    unittest.main()
