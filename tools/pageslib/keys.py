"""Ключи страниц: валидация и разрешение ключа в файл."""
import re
from pathlib import Path

SEGMENT_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
MAX_DEPTH = 4


def validate_key(key: str) -> list[str]:
    """Список ошибок ключа; пустой список = ключ валиден."""
    errors: list[str] = []
    if not key:
        return ["ключ пуст"]
    segments = key.split("/")
    if len(segments) > MAX_DEPTH:
        errors.append(f"больше {MAX_DEPTH} сегментов")
    for seg in segments:
        if not SEGMENT_RE.match(seg):
            errors.append(f"невалидный сегмент {seg!r}: нужно [a-z0-9][a-z0-9-]*")
    return errors


def page_file_candidates(repo_root: Path, key: str) -> list[Path]:
    """Кандидаты файла страницы в порядке приоритета: папка, затем файл."""
    return [
        repo_root / "pages" / Path(*key.split("/")) / "index.html",
        repo_root / "pages" / (key + ".html"),
    ]


def resolve_page_file(repo_root: Path, key: str) -> Path | None:
    """Существующий файл страницы по ключу или None."""
    for candidate in page_file_candidates(repo_root, key):
        if candidate.is_file():
            return candidate
    return None
