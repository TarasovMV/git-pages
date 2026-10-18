import shutil
import tempfile
import unittest
from pathlib import Path

from pageslib.keys import page_file_candidates, resolve_page_file, validate_key


class ValidateKeyTests(unittest.TestCase):
    def test_valid_keys(self):
        for key in ["a", "color-picker", "a-b-2", "tools/color-picker", "a/b/c/d"]:
            with self.subTest(key=key):
                self.assertEqual(validate_key(key), [])

    def test_invalid_keys(self):
        cases = {
            "": "пустой ключ",
            "Color": "заглавные буквы",
            "a_b": "подчёркивание",
            "-a": "начинается с дефиса",
            "a//b": "пустой сегмент",
            "a/b/c/d/e": "глубина больше 4",
            "цвет": "кириллица",
            "a\n": "завершающий перевод строки",
        }
        for key, why in cases.items():
            with self.subTest(key=key):
                self.assertNotEqual(validate_key(key), [], why)


class ResolvePageFileTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def write(self, rel: str) -> Path:
        p = self.tmp / "pages" / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("x", encoding="utf-8")
        return p

    def test_folder_page_wins_over_file_page(self):
        self.write("a/index.html")
        self.write("a.html")
        self.assertEqual(
            resolve_page_file(self.tmp, "a"),
            self.tmp / "pages" / "a" / "index.html",
        )

    def test_file_page(self):
        self.write("shagal-electricity/panel.html")
        self.assertEqual(
            resolve_page_file(self.tmp, "shagal-electricity/panel"),
            self.tmp / "pages" / "shagal-electricity" / "panel.html",
        )

    def test_missing_key_returns_none(self):
        self.assertIsNone(resolve_page_file(self.tmp, "nope"))

    def test_candidates_order(self):
        self.assertEqual(
            page_file_candidates(self.tmp, "a/b"),
            [
                self.tmp / "pages" / "a" / "b" / "index.html",
                self.tmp / "pages" / "a" / "b.html",
            ],
        )


if __name__ == "__main__":
    unittest.main()
