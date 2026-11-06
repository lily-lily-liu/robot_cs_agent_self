"""Project path helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Union

PathLike = Union[str, Path]


def get_project_root() -> Path:
    """Return the project root directory, independent of the current cwd."""
    return Path(__file__).resolve().parent.parent


def get_absolute_path(path: PathLike) -> Path:
    """Resolve a path relative to the project root."""
    candidate = Path(path).expanduser()
    if not candidate.is_absolute():
        candidate = get_project_root() / candidate
    return candidate.resolve()


def project_path(*parts: PathLike) -> Path:
    """Build an absolute path from project-relative path components."""
    return get_absolute_path(Path(*parts))


PROJECT_ROOT = get_project_root()
