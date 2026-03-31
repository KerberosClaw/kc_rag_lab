"""Store unit tests."""

import pytest

from src.config import Chunk
from src.store import get_client, rebuild_collection, get_collection_info


@pytest.fixture
def tmp_chroma(tmp_path):
    """建立暫時的 ChromaDB client。"""
    return get_client(persist_dir=str(tmp_path / ".chroma"))


@pytest.fixture
def sample_data():
    chunks = [
        Chunk(text="第一個文件的內容", metadata={"source_file": "a.md", "heading": "標題A", "heading_level": 1, "chunk_index": 0}),
        Chunk(text="第二個文件的內容", metadata={"source_file": "b.md", "heading": "標題B", "heading_level": 1, "chunk_index": 0}),
    ]
    # 假的向量（維度 4，測試用）
    embeddings = [[0.1, 0.2, 0.3, 0.4], [0.5, 0.6, 0.7, 0.8]]
    return chunks, embeddings


def test_rebuild_collection(tmp_chroma, sample_data):
    chunks, embeddings = sample_data
    col = rebuild_collection(tmp_chroma, chunks, embeddings, collection_name="test")
    assert col.count() == 2


def test_rebuild_overwrites(tmp_chroma, sample_data):
    chunks, embeddings = sample_data
    rebuild_collection(tmp_chroma, chunks, embeddings, collection_name="test")
    # 再 rebuild 一次，數量不應該翻倍
    col = rebuild_collection(tmp_chroma, chunks, embeddings, collection_name="test")
    assert col.count() == 2


def test_rebuild_empty(tmp_chroma):
    col = rebuild_collection(tmp_chroma, [], [], collection_name="test")
    assert col.count() == 0


def test_get_collection_info_exists(tmp_chroma, sample_data):
    chunks, embeddings = sample_data
    rebuild_collection(tmp_chroma, chunks, embeddings, collection_name="test")
    info = get_collection_info(tmp_chroma, collection_name="test")
    assert info["exists"] is True
    assert info["count"] == 2


def test_get_collection_info_not_exists(tmp_chroma):
    info = get_collection_info(tmp_chroma, collection_name="nonexistent")
    assert info["exists"] is False
    assert info["count"] == 0
