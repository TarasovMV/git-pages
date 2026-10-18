#!/usr/bin/env python3
"""Пересборка галереи index.html. Запускать из корня репозитория."""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from pageslib.gallery import render_index
from pageslib.scanner import scan_pages


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Пересборка галереи git-pages")
    parser.add_argument("--list", action="store_true",
                        help="напечатать «ключ | заголовок | обновлена» и выйти")
    args = parser.parse_args(argv)
    repo_root = Path.cwd()
    try:
        entries = scan_pages(repo_root)
    except FileNotFoundError as e:
        print(f"ошибка: {e}", file=sys.stderr)
        return 1
    except OSError:
        print("ошибка: git недоступен", file=sys.stderr)
        return 2
    if args.list:
        for e in sorted(entries, key=lambda e: e.key):
            print(f"{e.key} | {e.title or e.key} | {e.updated}")
        return 0
    html = render_index(entries)
    (repo_root / "index.html").write_text(html, encoding="utf-8", newline="\n")
    print(f"галерея пересобрана: страниц — {len(entries)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
