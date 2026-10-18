import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "rebuild_index.py"


class CliTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def run_cli(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            cwd=self.tmp, capture_output=True, text=True, encoding="utf-8",
            env={**os.environ, "PYTHONIOENCODING": "utf-8"},
        )

    def write_page(self, rel: str, text: str) -> None:
        p = self.tmp / "pages" / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")

    def test_exit1_without_pages_dir(self):
        self.assertEqual(self.run_cli().returncode, 1)

    def test_rebuild_creates_index(self):
        self.write_page("a/index.html", "<!-- page-meta\ntitle: A\n--><html></html>")
        r = self.run_cli()
        self.assertEqual(r.returncode, 0, r.stderr)
        index = (self.tmp / "index.html").read_text(encoding="utf-8")
        self.assertIn('href="pages/a/"', index)
        self.assertIn(">A</a>", index)

    def test_list_mode(self):
        self.write_page("a/index.html", "<!-- page-meta\ntitle: A\n--><html></html>")
        self.write_page("b.html", "<html></html>")
        r = self.run_cli("--list")
        self.assertEqual(r.returncode, 0, r.stderr)
        lines = r.stdout.strip().splitlines()
        self.assertEqual(len(lines), 2)
        self.assertTrue(lines[0].startswith("a | A | "), lines[0])
        self.assertTrue(lines[1].startswith("b | b | "), lines[1])


if __name__ == "__main__":
    unittest.main()
