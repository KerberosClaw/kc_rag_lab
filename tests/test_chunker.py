"""Chunker unit tests."""

import pytest

from src.chunker import chunk_single, chunk_documents, _split_by_headings, _split_by_length
from src.config import Document, MAX_CHUNK_SIZE


def _make_doc(content, filename="test.md"):
    return Document(content=content, metadata={"filename": filename})


class TestSplitByHeadings:

    def test_single_heading(self):
        sections = _split_by_headings("# Title\n\nBody text.")
        assert len(sections) == 1
        assert sections[0]["heading"] == "Title"
        assert sections[0]["level"] == 1

    def test_multiple_headings(self):
        text = "# H1\n\nPara 1.\n\n## H2\n\nPara 2.\n\n### H3\n\nPara 3."
        sections = _split_by_headings(text)
        assert len(sections) == 3
        assert sections[0]["heading"] == "H1"
        assert sections[1]["heading"] == "H2"
        assert sections[2]["heading"] == "H3"

    def test_no_headings(self):
        sections = _split_by_headings("Just plain text\nno headings here.")
        assert len(sections) == 1
        assert sections[0]["heading"] is None
        assert sections[0]["level"] == 0

    def test_preamble_before_first_heading(self):
        text = "Some intro text.\n\n# Title\n\nBody."
        sections = _split_by_headings(text)
        assert len(sections) == 2
        assert sections[0]["heading"] is None
        assert sections[1]["heading"] == "Title"

    def test_heading_levels(self):
        text = "# H1\n\n## H2\n\n### H3\n"
        sections = _split_by_headings(text)
        levels = [s["level"] for s in sections]
        assert levels == [1, 2, 3]


class TestSplitByLength:

    def test_short_text(self):
        result = _split_by_length("short", 500, 50)
        assert result == ["short"]

    def test_exact_size(self):
        text = "a" * 500
        result = _split_by_length(text, 500, 50)
        assert len(result) == 1

    def test_needs_split(self):
        text = "a" * 1000
        result = _split_by_length(text, 500, 50)
        assert len(result) >= 2
        # 第二個 chunk 應該跟第一個有 50 字重疊
        assert result[0][-50:] == result[1][:50]

    def test_overlap_preserved(self):
        text = "abcdefghij" * 100  # 1000 字
        result = _split_by_length(text, 500, 50)
        for i in range(len(result) - 1):
            overlap = result[i][-50:]
            next_start = result[i + 1][:50]
            assert overlap == next_start


class TestChunkSingle:

    def test_basic(self):
        doc = _make_doc("# Title\n\nSome content here.")
        chunks = chunk_single(doc)
        assert len(chunks) == 1
        assert chunks[0].metadata["source_file"] == "test.md"
        assert chunks[0].metadata["heading"] == "Title"

    def test_multiple_sections(self):
        doc = _make_doc("# A\n\nText A.\n\n## B\n\nText B.")
        chunks = chunk_single(doc)
        assert len(chunks) == 2

    def test_long_section_gets_split(self):
        long_text = "# Title\n\n" + "這是測試文字。" * 200  # 遠超 500 字
        doc = _make_doc(long_text)
        chunks = chunk_single(doc)
        assert len(chunks) > 1

    def test_no_heading_file(self):
        doc = _make_doc("Just plain text without any headings.")
        chunks = chunk_single(doc)
        assert len(chunks) == 1
        assert chunks[0].metadata["heading"] is None

    def test_empty_content(self):
        doc = _make_doc("")
        chunks = chunk_single(doc)
        assert chunks == []

    def test_chunk_index_sequential(self):
        doc = _make_doc("# A\n\nText.\n\n## B\n\nMore.\n\n## C\n\nEven more.")
        chunks = chunk_single(doc)
        indices = [c.metadata["chunk_index"] for c in chunks]
        assert indices == list(range(len(chunks)))

    def test_metadata_preserved(self):
        doc = _make_doc("# Hello\n\nWorld.", filename="my_note.md")
        chunks = chunk_single(doc)
        assert chunks[0].metadata["source_file"] == "my_note.md"
        assert chunks[0].metadata["heading_level"] == 1


class TestChunkDocuments:

    def test_multiple_docs(self):
        docs = [
            _make_doc("# A\n\nText A.", filename="a.md"),
            _make_doc("# B\n\nText B.", filename="b.md"),
        ]
        chunks = chunk_documents(docs)
        assert len(chunks) == 2
        sources = [c.metadata["source_file"] for c in chunks]
        assert "a.md" in sources
        assert "b.md" in sources

    def test_empty_list(self):
        chunks = chunk_documents([])
        assert chunks == []
