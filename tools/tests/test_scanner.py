import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from pageslib.scanner import GitError, TODAY, scan_pages

DATE = "2026-01-05"
STAMP = {
    "GIT_AUTHOR_DATE": f"{DATE}T12:00:00",
    "GIT_COMMITTER_DATE": f"{DATE}T12:00:00",
}


def git(repo: Path, *args: str, env: dict | None = None) -> None:
    subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True, capture_output=True,
        env={**os.environ, **(env or {})},
    )


class ScanPagesTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.pages = self.tmp / "pages"
        self.pages.mkdir()
        git(self.tmp, "init", "-b", "main")
        git(self.tmp, "config", "user.name", "t")
        git(self.tmp, "config", "user.email", "t@example.com")
        # Пустой корневой коммит: git log в репо без коммитов падает с кодом 128.
        git(self.tmp, "commit", "--allow-empty", "-m", "init")

    def write(self, rel: str, text: str = "<html></html>") -> Path:
        p = self.pages / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
        return p

    def commit(self) -> None:
        git(self.tmp, "add", "-A")
        git(self.tmp, "commit", "-m", "c", env=STAMP)

    def test_folder_and_file_pages_with_dates(self):
        self.write("shagal/index.html", "<!-- page-meta\ntitle: Электричество\n-->\n<html></html>")
        self.write("shagal/panel.html")
        self.write("data.json", "{}")
        self.commit()
        entries = {e.key: e for e in scan_pages(self.tmp)}
        self.assertEqual(set(entries), {"shagal", "shagal/panel"})
        self.assertEqual(entries["shagal"].kind, "folder")
        self.assertEqual(entries["shagal"].title, "Электричество")
        self.assertEqual(entries["shagal/panel"].kind, "file")
        self.assertEqual(entries["shagal/panel"].title, "")
        self.assertEqual(entries["shagal"].updated, DATE)
        self.assertEqual(entries["shagal"].created, DATE)
        self.assertEqual(entries["shagal"].url_path(), "/pages/shagal/")
        self.assertEqual(entries["shagal/panel"].url_path(), "/pages/shagal/panel")

    def test_multi_commit_dates(self):
        self.write("log/index.html")
        self.commit()  # 2026-01-05 (STAMP)
        self.write("log/index.html", "<html>v2</html>")
        git(self.tmp, "add", "-A")
        git(self.tmp, "commit", "-m", "c2", env={
            "GIT_AUTHOR_DATE": "2026-02-10T12:00:00",
            "GIT_COMMITTER_DATE": "2026-02-10T12:00:00",
        })
        entries = {e.key: e for e in scan_pages(self.tmp)}
        self.assertEqual(entries["log"].updated, "2026-02-10")
        self.assertEqual(entries["log"].created, "2026-01-05")

    def test_uncommitted_page_gets_today(self):
        self.write("new-page/index.html")
        entries = {e.key: e for e in scan_pages(self.tmp)}
        self.assertEqual(entries["new-page"].updated, TODAY)
        self.assertEqual(entries["new-page"].created, TODAY)

    def test_folder_beats_file_on_same_key(self):
        self.write("a/index.html")
        self.write("a.html")
        self.commit()
        entries = {e.key: e for e in scan_pages(self.tmp)}
        self.assertEqual(entries["a"].kind, "folder")

    def test_top_level_pages_index_ignored(self):
        self.write("index.html")
        self.commit()
        self.assertEqual(scan_pages(self.tmp), [])

    def test_missing_pages_dir_raises(self):
        shutil.rmtree(self.pages)
        with self.assertRaises(FileNotFoundError):
            scan_pages(self.tmp)

    def test_git_oserror_raises_giterror(self):
        self.write("a/index.html")
        with mock.patch("pageslib.scanner.subprocess.run", side_effect=OSError("no git")):
            with self.assertRaises(GitError):
                scan_pages(self.tmp)

    def test_git_failure_raises_giterror(self):
        self.write("a/index.html")
        result = subprocess.CompletedProcess(args=[], returncode=128, stdout="", stderr="fatal: not a git repository")
        with mock.patch("pageslib.scanner.subprocess.run", return_value=result):
            with self.assertRaises(GitError):
                scan_pages(self.tmp)


if __name__ == "__main__":
    unittest.main()
