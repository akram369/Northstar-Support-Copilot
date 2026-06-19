from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from support_agent.models import DocumentChunk
from support_agent.vector_store import SQLiteVectorStore


def test_retrieval_returns_relevant_chunk(tmp_path: Path):
    store = SQLiteVectorStore(tmp_path / "vectors.sqlite3")
    store.replace([
        DocumentChunk("1", "Reset links expire after thirty minutes.", "access.md", "Reset"),
        DocumentChunk("2", "Webhook endpoints must return HTTP 2xx quickly.", "webhooks.md", "Delivery"),
    ])
    results = store.search("Why does my password reset link expire?", top_k=1)
    assert results[0].chunk.source == "access.md"
    assert results[0].score > 0
    store.close()


def test_store_can_be_used_from_another_thread(tmp_path: Path):
    store = SQLiteVectorStore(tmp_path / "vectors.sqlite3")
    store.replace([
        DocumentChunk("1", "Reset links expire after thirty minutes.", "access.md", "Reset"),
    ])

    with ThreadPoolExecutor(max_workers=1) as executor:
        count = executor.submit(store.count).result()
        results = executor.submit(store.search, "password reset", 1).result()

    assert count == 1
    assert results[0].chunk.source == "access.md"
    store.close()
