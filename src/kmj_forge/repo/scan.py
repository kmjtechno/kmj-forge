from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


DEFAULT_IGNORED_DIRS = frozenset({
    ".git",
    ".hg",
    ".svn",
    ".idea",
    ".vscode",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".tox",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "node_modules",
    "target",
    "vendor",
})


@dataclass(frozen=True, slots=True)
class RepoFile:
    path: str
    content: str
    size: int


@dataclass(frozen=True, slots=True)
class ScanResult:
    root: str
    files: tuple[RepoFile, ...]
    skipped_files: int = 0

    @property
    def total_characters(self) -> int:
        return sum(len(item.content) for item in self.files)


def _ignored(relative: Path, ignored_dirs: frozenset[str]) -> bool:
    return any(part in ignored_dirs for part in relative.parts[:-1])


def scan_repository(
    root: str | Path,
    *,
    max_file_bytes: int = 256_000,
    ignored_dirs: frozenset[str] = DEFAULT_IGNORED_DIRS,
) -> ScanResult:
    if max_file_bytes < 1:
        raise ValueError("max_file_bytes must be positive")

    root_path = Path(root).expanduser().resolve()
    if not root_path.is_dir():
        raise ValueError(f"repository root is not a directory: {root_path}")

    files: list[RepoFile] = []
    skipped = 0
    for path in sorted(root_path.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(root_path)
        if _ignored(relative, ignored_dirs) or path.is_symlink():
            skipped += 1
            continue
        try:
            size = path.stat().st_size
        except OSError:
            skipped += 1
            continue
        if size > max_file_bytes:
            skipped += 1
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            skipped += 1
            continue
        files.append(RepoFile(relative.as_posix(), content, size))

    return ScanResult(str(root_path), tuple(files), skipped)
