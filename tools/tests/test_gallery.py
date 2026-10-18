import unittest
from pathlib import Path

from pageslib.gallery import page_href, render_index
from pageslib.scanner import PageEntry


def entry(key: str, kind: str = "folder", title: str = "", description: str = "",
          updated: str = "2026-01-01", created: str = "2026-01-01") -> PageEntry:
    return PageEntry(key=key, path=Path("pages") / key / "index.html", kind=kind,
                     title=title, description=description, updated=updated, created=created)


class RenderIndexTests(unittest.TestCase):
    def test_links_and_titles(self):
        html = render_index([
            entry("a", title="Альфа", description="Первая"),
            entry("shagal/panel", kind="file", title="Панель"),
        ])
        self.assertIn('href="pages/a/"', html)
        self.assertIn('href="pages/shagal/panel"', html)
        self.assertIn("Альфа", html)
        self.assertIn("Первая", html)

    def test_title_falls_back_to_key(self):
        self.assertIn(">b</a>", render_index([entry("b")]))

    def test_escapes_html(self):
        html = render_index([entry("x", title="<скрипт> &")])
        self.assertNotIn("<скрипт>", html)
        self.assertIn("&lt;скрипт&gt; &amp;", html)

    def test_newest_first(self):
        html = render_index([
            entry("old", updated="2026-01-01"),
            entry("new", updated="2026-02-02"),
        ])
        self.assertLess(html.index('href="pages/new/"'), html.index('href="pages/old/"'))

    def test_empty_gallery(self):
        self.assertIn("Пока нет ни одной страницы", render_index([]))

    def test_deterministic_regardless_of_input_order(self):
        entries = [entry("a", title="A"), entry("b", kind="file")]
        self.assertEqual(render_index(entries), render_index(list(reversed(entries))))

    def test_page_href(self):
        self.assertEqual(page_href(entry("a")), "pages/a/")
        self.assertEqual(page_href(entry("a/b", kind="file")), "pages/a/b")


if __name__ == "__main__":
    unittest.main()
