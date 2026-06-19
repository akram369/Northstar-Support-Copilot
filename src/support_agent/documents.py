from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Iterable

from .models import DocumentChunk


SUPPORTED_EXTENSIONS = {".md", ".txt", ".pdf"}


def load_documents(data_dir: Path) -> list[tuple[Path, str, int | None]]:
    documents: list[tuple[Path, str, int | None]] = []
    for path in sorted(data_dir.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue
        if path.suffix.lower() == ".pdf":
            try:
                from pypdf import PdfReader
            except ImportError as exc:
                raise RuntimeError("Install pypdf to ingest PDF knowledge files") from exc
            for page_number, page in enumerate(PdfReader(str(path)).pages, start=1):
                documents.append((path, page.extract_text() or "", page_number))
        else:
            documents.append((path, path.read_text(encoding="utf-8"), None))
    return documents


def chunk_documents(
    documents: Iterable[tuple[Path, str, int | None]],
    data_dir: Path,
    chunk_size: int,
    overlap: int,
) -> list[DocumentChunk]:
    chunks: list[DocumentChunk] = []
    for path, text, page in documents:
        source = path.relative_to(data_dir).as_posix()
        sections = _sections(text)
        for section, body in sections:
            start = 0
            while start < len(body):
                end = min(len(body), start + chunk_size)
                if end < len(body):
                    boundary = body.rfind(" ", start + chunk_size // 2, end)
                    end = boundary if boundary > start else end
                value = body[start:end].strip()
                if value:
                    raw_id = f"{source}:{page}:{section}:{start}"
                    chunks.append(DocumentChunk(
                        id=hashlib.sha256(raw_id.encode()).hexdigest()[:20],
                        text=value,
                        source=source,
                        section=section,
                        page=page,
                    ))
                if end >= len(body):
                    break
                start = max(start + 1, end - overlap)
    return chunks


def _sections(text: str) -> list[tuple[str, str]]:
    heading = "Overview"
    sections: list[tuple[str, str]] = []
    buffer: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if re.match(r"^#{1,4}\s+", stripped):
            if buffer:
                sections.append((heading, "\n".join(buffer).strip()))
            heading = re.sub(r"^#{1,4}\s+", "", stripped)
            buffer = []
        else:
            buffer.append(line)
    if buffer:
        sections.append((heading, "\n".join(buffer).strip()))
    return [(h, b) for h, b in sections if b]

