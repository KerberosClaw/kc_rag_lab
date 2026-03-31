"""Embedder unit tests."""

import pytest

from src.config import Chunk
from src.embedder import embed_chunks, embed_single


@pytest.fixture
def sample_chunks():
    return [
        Chunk(text="這是第一個測試 chunk", metadata={"source_file": "a.md", "chunk_index": 0}),
        Chunk(text="這是第二個測試 chunk", metadata={"source_file": "a.md", "chunk_index": 1}),
        Chunk(text="第三個 chunk 用來測試批次處理", metadata={"source_file": "b.md", "chunk_index": 0}),
    ]


@pytest.mark.integration
def test_embed_single():
    vec = embed_single("測試 embedding")
    assert isinstance(vec, list)
    assert len(vec) > 0
    assert all(isinstance(v, float) for v in vec)


@pytest.mark.integration
def test_embed_chunks(sample_chunks):
    vecs = embed_chunks(sample_chunks)
    assert len(vecs) == len(sample_chunks)
    # 所有向量維度應該一致
    dims = set(len(v) for v in vecs)
    assert len(dims) == 1


@pytest.mark.integration
def test_embed_empty():
    vecs = embed_chunks([])
    assert vecs == []


@pytest.mark.integration
def test_embed_connection_error(monkeypatch):
    """API 連不上時應拋出 ConnectionError。"""
    import src.embedder as mod
    monkeypatch.setattr(mod, "LLM_BASE_URL", "http://127.0.0.1:99999/v1")
    with pytest.raises(ConnectionError):
        embed_single("test")
