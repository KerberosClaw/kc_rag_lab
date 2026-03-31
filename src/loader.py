"""Stage 1: Markdown 文件載入。

遞迴掃描資料夾，讀取所有 .md 檔，處理 frontmatter，回傳 Document 列表。
"""

import logging
import re
from pathlib import Path

from .config import Document

logger = logging.getLogger(__name__)

FRONTMATTER_PATTERN = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def load_documents(directory: str | Path) -> list[Document]:
    """遞迴掃描資料夾，載入所有 .md 檔案。

    Args:
        directory: 目標資料夾路徑

    Returns:
        Document 列表，每份包含 content 和 metadata
    """
    directory = Path(directory)
    if not directory.is_dir():
        logger.warning("路徑不存在或不是資料夾: %s", directory)
        return []

    documents = []
    md_files = sorted(directory.rglob("*.md"))

    for filepath in md_files:
        try:
            raw = filepath.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as e:
            logger.warning("無法讀取 %s: %s", filepath, e)
            continue

        content, frontmatter = _strip_frontmatter(raw)

        if not content.strip():
            logger.debug("跳過空檔案: %s", filepath)
            continue

        metadata = {
            "filename": filepath.name,
            "filepath": str(filepath),
        }
        if frontmatter:
            metadata["frontmatter"] = frontmatter

        documents.append(Document(content=content, metadata=metadata))

    logger.info("載入 %d 個文件（來自 %s）", len(documents), directory)
    return documents


def _strip_frontmatter(text: str) -> tuple[str, str | None]:
    """移除 YAML frontmatter，回傳 (content, frontmatter)。

    如果沒有 frontmatter，回傳 (原文, None)。
    """
    match = FRONTMATTER_PATTERN.match(text)
    if match:
        frontmatter = match.group(1).strip()
        content = text[match.end():]
        return content, frontmatter
    return text, None
