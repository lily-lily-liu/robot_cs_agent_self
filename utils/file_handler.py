"""File fingerprints and lightweight document readers."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Iterator


def calculate_file_fingerprint(file_path: str | Path, algorithm: str = "md5") -> str:
    """Return a content fingerprint for a file."""
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"File does not exist: {path}")
    try:
        digest = hashlib.new(algorithm)
    except ValueError as exc:
        raise ValueError(f"Unsupported hash algorithm: {algorithm}") from exc
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def calculate_md5(file_path: str | Path) -> str:
    """Return the MD5 fingerprint used for document deduplication."""
    return calculate_file_fingerprint(file_path, "md5")


def read_txt(file_path: str | Path, encoding: str = "utf-8") -> str:
    """Read a UTF-8 text file."""
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"File does not exist: {path}")
    return path.read_text(encoding=encoding)


def read_pdf(file_path: str | Path) -> str:
    """Extract text from every page of a PDF using pypdf."""
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"File does not exist: {path}")
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise ImportError("pypdf is required to read PDF files") from exc
    reader = PdfReader(str(path))
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def read_file(file_path: str | Path, encoding: str = "utf-8") -> str:
    """Read a supported TXT or PDF file."""
    path = Path(file_path)
    suffix = path.suffix.lower()
    if suffix == ".txt":
        return read_txt(path, encoding)
    if suffix == ".pdf":
        return read_pdf(path)
    raise ValueError(f"Unsupported file type: {path.suffix or '<none>'}")


def iter_documents(directory: str | Path) -> Iterator[Path]:
    """Yield supported document files below a directory in stable order."""
    root = Path(directory)
    if not root.is_dir():
        raise NotADirectoryError(f"Directory does not exist: {root}")
    yield from sorted(
        (path for path in root.rglob("*") if path.is_file() and path.suffix.lower() in {".txt", ".pdf"}),
        key=lambda path: str(path).lower(),
    )
