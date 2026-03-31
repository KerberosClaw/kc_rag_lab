"""Loader unit tests."""

from pathlib import Path

import pytest

from src.loader import load_documents, _strip_frontmatter


@pytest.fixture
def tmp_docs(tmp_path):
    """建立測試用的 markdown 檔案。"""
    # 普通 md 檔
    (tmp_path / "note1.md").write_text("# Hello\n\nWorld", encoding="utf-8")

    # 有 frontmatter 的 md 檔
    (tmp_path / "note2.md").write_text(
        "---\ntitle: Test\ntags: [a, b]\n---\n\n# Content\n\nBody here.",
        encoding="utf-8",
    )

    # 非 md 檔（應該被跳過）
    (tmp_path / "readme.txt").write_text("not markdown", encoding="utf-8")

    # 空 md 檔（應該被跳過）
    (tmp_path / "empty.md").write_text("", encoding="utf-8")

    # 子資料夾裡的 md 檔
    sub = tmp_path / "sub"
    sub.mkdir()
    (sub / "deep.md").write_text("## Deep\n\nNested file.", encoding="utf-8")

    return tmp_path


def test_load_basic(tmp_docs):
    docs = load_documents(tmp_docs)
    # note1.md, note2.md, sub/deep.md（empty.md 跳過，readme.txt 跳過）
    assert len(docs) == 3


def test_load_skips_non_md(tmp_docs):
    docs = load_documents(tmp_docs)
    filenames = [d.metadata["filename"] for d in docs]
    assert "readme.txt" not in filenames


def test_load_skips_empty(tmp_docs):
    docs = load_documents(tmp_docs)
    filenames = [d.metadata["filename"] for d in docs]
    assert "empty.md" not in filenames


def test_load_recursive(tmp_docs):
    docs = load_documents(tmp_docs)
    filenames = [d.metadata["filename"] for d in docs]
    assert "deep.md" in filenames


def test_load_frontmatter_stripped(tmp_docs):
    docs = load_documents(tmp_docs)
    note2 = next(d for d in docs if d.metadata["filename"] == "note2.md")
    assert "---" not in note2.content
    assert "title: Test" not in note2.content
    assert "Content" in note2.content


def test_load_frontmatter_in_metadata(tmp_docs):
    docs = load_documents(tmp_docs)
    note2 = next(d for d in docs if d.metadata["filename"] == "note2.md")
    assert "frontmatter" in note2.metadata
    assert "title: Test" in note2.metadata["frontmatter"]


def test_load_metadata_has_filepath(tmp_docs):
    docs = load_documents(tmp_docs)
    for doc in docs:
        assert "filepath" in doc.metadata
        assert doc.metadata["filepath"].endswith(".md")


def test_load_empty_directory(tmp_path):
    docs = load_documents(tmp_path)
    assert docs == []


def test_load_nonexistent_directory():
    docs = load_documents("/nonexistent/path")
    assert docs == []


def test_strip_frontmatter_basic():
    text = "---\ntitle: Hi\n---\n\nContent"
    content, fm = _strip_frontmatter(text)
    assert content.strip() == "Content"
    assert fm == "title: Hi"


def test_strip_frontmatter_none():
    text = "# Just content\n\nNo frontmatter."
    content, fm = _strip_frontmatter(text)
    assert content == text
    assert fm is None
