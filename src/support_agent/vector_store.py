from __future__ import annotations

import hashlib
import json
import math
import re
import sqlite3
from collections import Counter
from pathlib import Path

from .models import DocumentChunk, RetrievedChunk


TOKEN_RE = re.compile(r"[a-z0-9][a-z0-9_.-]+")
STOPWORDS = {"the", "and", "for", "with", "this", "that", "what", "should", "does", "from", "have", "our", "your", "into", "when"}


class LocalHashEmbedding:
    """Deterministic local feature-hashing embedding; no model download required."""

    def __init__(self, dimensions: int = 768):
        self.dimensions = dimensions

    def embed(self, text: str) -> list[float]:
        tokens = TOKEN_RE.findall(text.lower())
        counts = Counter(tokens + [f"{a}_{b}" for a, b in zip(tokens, tokens[1:])])
        vector = [0.0] * self.dimensions
        for token, count in counts.items():
            digest = hashlib.blake2b(token.encode(), digest_size=8).digest()
            index = int.from_bytes(digest, "big") % self.dimensions
            sign = 1.0 if digest[0] & 1 else -1.0
            vector[index] += sign * (1.0 + math.log(count))
        norm = math.sqrt(sum(v * v for v in vector)) or 1.0
        return [v / norm for v in vector]


class SQLiteVectorStore:
    """Small persistent vector database with metadata and cosine retrieval."""

    def __init__(self, path: Path, embedder: LocalHashEmbedding | None = None):
        import contextlib
        self.path = path
        self.embedder = embedder or LocalHashEmbedding()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with contextlib.closing(self._connect()) as connection:
            with connection:
                connection.execute("""
                    CREATE TABLE IF NOT EXISTS chunks (
                        id TEXT PRIMARY KEY, text TEXT NOT NULL, source TEXT NOT NULL,
                        section TEXT NOT NULL, page INTEGER, vector TEXT NOT NULL
                    )
                """)

    def _connect(self) -> sqlite3.Connection:
        """Return a connection owned by the current operation and thread."""
        return sqlite3.connect(self.path, timeout=30, check_same_thread=False)

    def replace(self, chunks: list[DocumentChunk]) -> None:
        import contextlib
        with contextlib.closing(self._connect()) as connection:
            with connection:
                connection.execute("DELETE FROM chunks")
                connection.executemany(
                    "INSERT INTO chunks VALUES (?, ?, ?, ?, ?, ?)",
                    [
                        (c.id, c.text, c.source, c.section, c.page, json.dumps(self.embedder.embed(c.text)))
                        for c in chunks
                    ],
                )

    def count(self) -> int:
        import contextlib
        with contextlib.closing(self._connect()) as connection:
            return int(connection.execute("SELECT COUNT(*) FROM chunks").fetchone()[0])

    def search(self, query: str, top_k: int = 4) -> list[RetrievedChunk]:
        import contextlib
        query_vector = self.embedder.embed(query)
        query_terms = {t for t in TOKEN_RE.findall(query.lower()) if t not in STOPWORDS and len(t) > 2}
        results: list[RetrievedChunk] = []
        with contextlib.closing(self._connect()) as connection:
            rows = connection.execute("SELECT id, text, source, section, page, vector FROM chunks").fetchall()
        for row in rows:
            vector = json.loads(row[5])
            cosine = max(0.0, sum(a * b for a, b in zip(query_vector, vector)))
            document_terms = set(TOKEN_RE.findall(f"{row[3]} {row[1]}".lower()))
            lexical = len(query_terms & document_terms) / max(1, len(query_terms))
            score = 0.45 * cosine + 0.55 * lexical
            chunk = DocumentChunk(id=row[0], text=row[1], source=row[2], section=row[3], page=row[4])
            results.append(RetrievedChunk(chunk=chunk, score=score))
        return sorted(results, key=lambda item: item.score, reverse=True)[:top_k]

    def close(self) -> None:
        """Retained for API compatibility; operations close their own connections."""
