"""Сканер pages/: находит страницы, ключи, метаданные и даты из git."""
import subprocess
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from .meta import parse_page_meta

TODAY = date.today().isoformat()


class GitError(RuntimeError):
    """git недоступен или завершился с ошибкой."""


def _run_git(args: list[str]) -> str:
    try:
        result = subprocess.run(args, capture_output=True, text=True, encoding="utf-8")
    except OSError as e:
        raise GitError(f"git недоступен: {e}") from e
    if result.returncode != 0:
        detail = result.stderr.strip().splitlines()
        first = detail[0] if detail else f"код выхода {result.returncode}"
        raise GitError(f"git error: {first}")
    return result.stdout


@dataclass
class PageEntry:
    key: str            # например "shagal-electricity/panel"
    path: Path          # абсолютный путь к файлу страницы
    kind: str           # "folder" | "file"
    title: str
    description: str
    updated: str        # YYYY-MM-DD из git log
    created: str        # YYYY-MM-DD из git log

    def url_path(self) -> str:
        suffix = "/" if self.kind == "folder" else ""
        return f"/pages/{self.key}{suffix}"


def _key_of(pages_dir: Path, html_file: Path) -> tuple[str | None, str]:
    posix = html_file.relative_to(pages_dir).as_posix()
    if posix == "index.html":
        return None, ""  # pages/index.html сам по себе страницей не является
    if posix.endswith("/index.html"):
        return posix[: -len("/index.html")], "folder"
    return posix[: -len(".html")], "file"


def _git_dates(repo_root: Path, rel_path: str) -> tuple[str, str]:
    """(updated, created) из git log; без коммитов — TODAY."""
    # Флаги обязательны до "--": после "--" git трактует их как pathspec'ы.
    updated = _run_git(["git", "-C", str(repo_root), "log", "-1", "--format=%cs", "--", rel_path])
    created = _run_git(["git", "-C", str(repo_root), "log", "--diff-filter=A", "--format=%cs", "--", rel_path])
    up = updated.strip() or TODAY
    added = [line for line in created.strip().splitlines() if line]
    return up, (added[-1] if added else TODAY)


def scan_pages(repo_root: Path) -> list[PageEntry]:
    pages_dir = repo_root / "pages"
    if not pages_dir.is_dir():
        raise FileNotFoundError(f"нет папки pages/ в {repo_root}")
    by_key: dict[str, PageEntry] = {}
    for html_file in sorted(pages_dir.rglob("*.html")):
        key, kind = _key_of(pages_dir, html_file)
        if key is None:
            continue
        meta = parse_page_meta(html_file.read_text(encoding="utf-8"))
        rel = html_file.relative_to(repo_root).as_posix()
        updated, created = _git_dates(repo_root, rel)
        entry = PageEntry(
            key=key, path=html_file, kind=kind,
            title=meta.title, description=meta.description,
            updated=updated, created=created,
        )
        existing = by_key.get(key)
        if existing is None or (existing.kind == "file" and kind == "folder"):
            by_key[key] = entry
    return list(by_key.values())
