"""Парсер блока page-meta — HTML-комментария с полями title/description."""
import re
from dataclasses import dataclass

META_RE = re.compile(r"<!--\s*page-meta\s*\n(.*?)-->", re.DOTALL)
FIELD_RE = re.compile(r"^([a-z-]+):[ \t]*(.*)$", re.MULTILINE)


@dataclass
class PageMeta:
    title: str = ""
    description: str = ""


def parse_page_meta(html_text: str) -> PageMeta:
    m = META_RE.search(html_text)
    if not m:
        return PageMeta()
    fields = dict(FIELD_RE.findall(m.group(1)))
    return PageMeta(
        title=fields.get("title", "").strip(),
        description=fields.get("description", "").strip(),
    )
