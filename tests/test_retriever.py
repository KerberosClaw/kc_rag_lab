"""Retriever unit tests."""

import pytest

from src.retriever import retrieve
from src.store import get_client, get_collection_info


@pytest.mark.integration
def test_retrieve_basic():
    """搜尋一個知識庫裡有的主題。"""
    results = retrieve("Telegram bot 怎麼設定")
    assert len(results) > 0
    assert results[0].score > 0
    assert "source_file" in results[0].metadata


@pytest.mark.integration
def test_retrieve_top_k():
    """確認回傳數量符合 top_k。"""
    results = retrieve("OpenClaw", top_k=3)
    assert len(results) == 3


@pytest.mark.integration
def test_retrieve_has_score():
    """確認每個結果都有 score。"""
    results = retrieve("Modbus TCP")
    for r in results:
        assert isinstance(r.score, float)
        assert -1.0 <= r.score <= 1.0


@pytest.mark.integration
def test_retrieve_empty_collection():
    """空 collection 回傳空列表。"""
    client = get_client()
    results = retrieve("test", client=client, collection_name="nonexistent")
    assert results == []
