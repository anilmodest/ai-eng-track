"""Turn an uploaded file into plain text. Small on purpose: parsing is a Week 0 skill."""

import csv
import io
from collections.abc import Callable
from pathlib import PurePosixPath

from pypdf import PdfReader


class UnsupportedType(ValueError):
    pass


def _parse_pdf(data: bytes) -> str:
    reader = PdfReader(io.BytesIO(data))
    return "\n\n".join((page.extract_text() or "") for page in reader.pages)


def _parse_csv(data: bytes) -> str:
    rows = list(csv.reader(io.StringIO(data.decode("utf-8", errors="replace"))))
    if not rows:
        return ""
    header, *body = rows
    lines = [" | ".join(header)]
    lines += [" | ".join(f"{h}: {v}" for h, v in zip(header, row, strict=False)) for row in body]
    return "\n".join(lines)


def _parse_text(data: bytes) -> str:
    return data.decode("utf-8", errors="replace")


_BY_SUFFIX: dict[str, Callable[[bytes], str]] = {
    ".pdf": _parse_pdf,
    ".csv": _parse_csv,
    ".md": _parse_text,
    ".txt": _parse_text,
}


def parse(filename: str, data: bytes) -> str:
    suffix = PurePosixPath(filename).suffix.lower()
    parser = _BY_SUFFIX.get(suffix)
    if parser is None:
        raise UnsupportedType(f"cannot parse {suffix or 'file without extension'}")
    return parser(data).strip()
