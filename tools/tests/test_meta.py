import unittest

from pageslib.meta import PageMeta, parse_page_meta

HTML_WITH_META = """<!DOCTYPE html>
<html>
<head>
<!-- page-meta
title: Цветовой пикер
description: Подбор палитры
-->
<title>x</title>
</head>
</html>"""


class ParsePageMetaTests(unittest.TestCase):
    def test_parses_title_and_description(self):
        m = parse_page_meta(HTML_WITH_META)
        self.assertEqual(m.title, "Цветовой пикер")
        self.assertEqual(m.description, "Подбор палитры")

    def test_missing_meta_returns_empty(self):
        self.assertEqual(parse_page_meta("<html><body>нет</body></html>"), PageMeta())

    def test_empty_fields(self):
        self.assertEqual(parse_page_meta("<!-- page-meta\ntitle:\ndescription: \n-->"), PageMeta())

    def test_unknown_fields_ignored(self):
        m = parse_page_meta("<!-- page-meta\nauthor: кто-то\ntitle: T\n-->")
        self.assertEqual(m.title, "T")
        self.assertEqual(m.description, "")

    def test_first_meta_block_wins(self):
        m = parse_page_meta(
            "<!-- page-meta\ntitle: Первый\n-->\n<!-- page-meta\ntitle: Второй\n-->"
        )
        self.assertEqual(m.title, "Первый")

    def test_multiline_value_takes_first_line(self):
        m = parse_page_meta("<!-- page-meta\ntitle: Первая строка\nпродолжение\n-->")
        self.assertEqual(m.title, "Первая строка")


if __name__ == "__main__":
    unittest.main()
