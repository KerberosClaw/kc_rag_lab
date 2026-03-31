"""Stage 2: 文件切塊。

按 Markdown heading 切塊，超長 section 用固定長度 + overlap 二次切割。
"""

import logging
import re

from .config import Chunk, Document, HEADING_PATTERN, MAX_CHUNK_SIZE, OVERLAP_SIZE

logger = logging.getLogger(__name__)


def chunk_documents(documents: list[Document]) -> list[Chunk]:
    """把多份文件切成 chunk 列表。

    Args:
        documents: Loader 回傳的 Document 列表

    Returns:
        所有文件的 Chunk 列表
    """
    all_chunks = []
    for doc in documents:
        chunks = chunk_single(doc)
        all_chunks.extend(chunks)

    logger.info("共產生 %d 個 chunk（來自 %d 個文件）", len(all_chunks), len(documents))
    return all_chunks


def chunk_single(doc: Document) -> list[Chunk]:
    """切割單一文件。

    策略：
    1. 按 heading（#, ##, ###）切成 section
    2. 每個 section 如果超過 MAX_CHUNK_SIZE，用固定長度 + overlap 再切
    3. 沒有任何 heading 的文件，整份視為一個 section
    """
    source_file = doc.metadata.get("filename", "unknown")
    sections = _split_by_headings(doc.content)

    chunks = []
    for section in sections:
        heading = section["heading"]
        heading_level = section["level"]
        text = section["content"].strip()

        if not text:
            continue

        if len(text) <= MAX_CHUNK_SIZE:
            chunks.append(Chunk(
                text=text,
                metadata={
                    "source_file": source_file,
                    "heading": heading,
                    "heading_level": heading_level,
                    "chunk_index": len(chunks),
                },
            ))
        else:
            sub_chunks = _split_by_length(text, MAX_CHUNK_SIZE, OVERLAP_SIZE)
            for sub_text in sub_chunks:
                chunks.append(Chunk(
                    text=sub_text,
                    metadata={
                        "source_file": source_file,
                        "heading": heading,
                        "heading_level": heading_level,
                        "chunk_index": len(chunks),
                    },
                ))

    return chunks


def _split_by_headings(text: str) -> list[dict]:
    """按 Markdown heading 切成多個 section。

    回傳 list of {heading, level, content}。
    沒有 heading 的文件回傳一個 section，heading 為 None、level 為 0。
    """
    heading_re = re.compile(HEADING_PATTERN, re.MULTILINE)
    matches = list(heading_re.finditer(text))

    if not matches:
        return [{"heading": None, "level": 0, "content": text}]

    sections = []

    # heading 之前的內容（如果有的話）
    if matches[0].start() > 0:
        preamble = text[:matches[0].start()].strip()
        if preamble:
            sections.append({"heading": None, "level": 0, "content": preamble})

    for i, match in enumerate(matches):
        level = len(match.group(1))  # # = 1, ## = 2, ### = 3

        # 取得完整的 heading 行（regex 只 match 到 # 和空白，要延伸到換行）
        line_end = text.find("\n", match.start())
        if line_end == -1:
            line_end = len(text)
        heading_line = text[match.start():line_end].strip()
        heading_title = heading_line.lstrip("#").strip()

        # 從 heading 行結尾到下一個 heading（或文件結尾）
        content_start = line_end + 1 if line_end < len(text) else len(text)
        content_end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        content = text[content_start:content_end].strip()

        # heading 行本身也算進 content（保留上下文）
        full_content = heading_line + "\n" + content if content else heading_line

        sections.append({
            "heading": heading_title,
            "level": level,
            "content": full_content,
        })

    return sections


def _split_by_length(text: str, max_size: int, overlap: int) -> list[str]:
    """固定長度 + overlap 切割。

    用在單一 section 超過 max_size 的情況。
    """
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + max_size, len(text))
        chunk = text[start:end]
        if chunk:
            chunks.append(chunk)
        if end >= len(text):
            break
        start = end - overlap
    return chunks
