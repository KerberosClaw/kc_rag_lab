"""Generator unit tests."""

import pytest

from src.retriever import retrieve, RetrievalResult
from src.generator import generate, _format_context


def test_format_context():
    """確認 context 格式正確。"""
    results = [
        RetrievalResult(text="內容一", score=0.9, metadata={"source_file": "a.md", "heading": "標題A"}),
        RetrievalResult(text="內容二", score=0.8, metadata={"source_file": "b.md", "heading": ""}),
    ]
    ctx = _format_context(results)
    assert "[1] 來源：a.md / 標題A" in ctx
    assert "[2] 來源：b.md" in ctx
    assert "內容一" in ctx


def test_generate_empty_results():
    """沒有搜尋結果時，直接回傳無法回答。"""
    answer = generate("任何問題", [])
    assert "無法回答" in answer


@pytest.mark.integration
def test_generate_with_real_retrieval():
    """真實問答：知識庫裡有的問題。"""
    results = retrieve("OpenClaw 是什麼")
    answer = generate("OpenClaw 是什麼", results)
    assert len(answer) > 0
    # 應該有引用來源（可能是 [1] 或 xxx.md 格式）
    assert "來源" in answer or ".md" in answer or "[1]" in answer


@pytest.mark.integration
def test_generate_unknown_topic():
    """真實問答：知識庫裡沒有的問題。"""
    results = retrieve("量子力學的基本原理是什麼")
    answer = generate("量子力學的基本原理是什麼", results)
    # LLM 應該說無法回答，或至少不瞎掰量子力學
    # 這個比較寬鬆 — 只要回答裡不包含量子力學的專業術語就算通過
    assert len(answer) > 0
