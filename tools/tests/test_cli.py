import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "rebuild_index.py"


def git(repo: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True)


class CliTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        git(self.tmp, "init", "-b", "main")
        git(self.tmp, "config", "user.name", "t")
        git(self.tmp, "config", "user.email", "t@example.com")
        # Пустой корневой коммит: git log в репо без коммитов падает с кодом 128.
        git(self.tmp, "commit", "--allow-empty", "-m", "init")

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
        r = self.run_cli()
        self.assertEqual(r.returncode, 1)
        self.assertIn("ошибка", r.stderr)

    def test_exit2_when_git_unavailable(self):
        self.write_page("a/index.html", "<html></html>")
        env = {**os.environ, "PATH": r"C:\Windows\System32", "PYTHONIOENCODING": "utf-8"}
        r = subprocess.run([sys.executable, str(SCRIPT)], cwd=self.tmp,
                           capture_output=True, text=True, encoding="utf-8", env=env)
        self.assertEqual(r.returncode, 2, r.stderr)

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
