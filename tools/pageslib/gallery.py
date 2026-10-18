"""Рендер index.html — галереи всех страниц. Вывод детерминирован."""
from datetime import date
from html import escape

from .scanner import PageEntry

TEMPLATE = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>git-pages — галерея страниц</title>
<style>
  :root { color-scheme: light dark; }
  body { font-family: system-ui, -apple-system, "Segoe UI", sans-serif; margin: 0;
         background: #f6f7f9; color: #1c1e21; }
  main { max-width: 960px; margin: 0 auto; padding: 32px 20px 64px; }
  h1 { font-size: 1.6rem; }
  .count { color: #6b7280; margin-top: -8px; }
  .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
          gap: 16px; margin-top: 24px; }
  .card { background: #fff; border: 1px solid #e5e7eb; border-radius: 10px;
          padding: 16px 18px; }
  .card a { color: #0b57d0; font-weight: 600; text-decoration: none; }
  .card a:hover { text-decoration: underline; }
  .card .key { font-family: ui-monospace, Consolas, monospace; font-size: 0.8rem;
               color: #6b7280; margin-top: 4px; word-break: break-all; }
  .card .desc { margin-top: 8px; font-size: 0.9rem; }
  .card .date { margin-top: 10px; font-size: 0.8rem; color: #9ca3af; }
  .empty { color: #6b7280; }
  footer { margin-top: 48px; font-size: 0.8rem; color: #9ca3af; }
  @media (prefers-color-scheme: dark) {
    body { background: #14161a; color: #e6e8ea; }
    .card { background: #1d2025; border-color: #2a2e35; }
    .card a { color: #7ab8ff; }
  }
</style>
</head>
<body>
<main>
  <h1>git-pages</h1>
  <p class="count">__COUNT__ страниц(ы)</p>
  <div class="grid">
__CARDS__
  </div>
  <footer>Пересобрано: __TODAY__</footer>
</main>
</body>
</html>
"""

CARD = """    <div class="card">
      <a href="{href}">{title}</a>
      <div class="key">{key}</div>
      <div class="desc">{desc}</div>
      <div class="date">обновлена: {updated}</div>
    </div>"""

EMPTY = """    <p class="empty">Пока нет ни одной страницы.</p>"""


def page_href(entry: PageEntry) -> str:
    suffix = "/" if entry.kind == "folder" else ""
    return f"pages/{entry.key}{suffix}"


def sort_entries(entries: list[PageEntry]) -> list[PageEntry]:
    by_key = sorted(entries, key=lambda e: e.key)
    return sorted(by_key, key=lambda e: e.updated, reverse=True)


def _card(entry: PageEntry) -> str:
    return CARD.format_map({
        "href": escape(page_href(entry)),
        "title": escape(entry.title or entry.key),
        "key": escape(entry.key),
        "desc": escape(entry.description) or "—",
        "updated": escape(entry.updated),
    })


def render_index(entries: list[PageEntry]) -> str:
    cards = "\n".join(_card(e) for e in sort_entries(entries)) if entries else EMPTY
    return (TEMPLATE
            .replace("__COUNT__", str(len(entries)))
            .replace("__CARDS__", cards)
            .replace("__TODAY__", date.today().isoformat()))
