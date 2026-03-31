"""Stage 4: Vector Store — 用 ChromaDB 存放向量。"""

import logging
from pathlib import Path

import chromadb

from .config import Chunk, CHROMA_PERSIST_DIR, CHROMA_COLLECTION_NAME

logger = logging.getLogger(__name__)


def get_client(persist_dir: str | None = None) -> chromadb.ClientAPI:
    """取得 ChromaDB client（持久化到本地檔案）。"""
    path = persist_dir or CHROMA_PERSIST_DIR
    Path(path).mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(path=path)


def rebuild_collection(
    client: chromadb.ClientAPI,
    chunks: list[Chunk],
    embeddings: list[list[float]],
    collection_name: str | None = None,
) -> chromadb.Collection:
    """刪除舊 collection 並重建。

    Args:
        client: ChromaDB client
        chunks: Chunk 列表
        embeddings: 對應的向量列表（順序一致）
        collection_name: collection 名稱

    Returns:
        新建的 collection
    """
    name = collection_name or CHROMA_COLLECTION_NAME

    # 刪除舊的（如果存在）
    existing = [c.name for c in client.list_collections()]
    if name in existing:
        client.delete_collection(name)
        logger.info("已刪除舊 collection: %s", name)

    collection = client.create_collection(name=name)

    if not chunks:
        logger.info("建立空 collection: %s", name)
        return collection

    # ChromaDB 的 add 有批次限制，分批存入
    batch_size = 500
    total = len(chunks)

    for i in range(0, total, batch_size):
        end = min(i + batch_size, total)
        batch_chunks = chunks[i:end]
        batch_embeddings = embeddings[i:end]

        ids = [
            f"{c.metadata.get('source_file', 'unknown')}_{c.metadata.get('chunk_index', i+j)}"
            for j, c in enumerate(batch_chunks)
        ]
        documents = [c.text for c in batch_chunks]
        # ChromaDB metadata 只接受 str/int/float/bool，None 不行
        metadatas = [_sanitize_metadata(c.metadata) for c in batch_chunks]

        collection.add(
            ids=ids,
            documents=documents,
            embeddings=batch_embeddings,
            metadatas=metadatas,
        )

    logger.info("存入 %d 筆到 collection '%s'", total, name)
    return collection


def get_collection_info(
    client: chromadb.ClientAPI,
    collection_name: str | None = None,
) -> dict:
    """查詢 collection 狀態。"""
    name = collection_name or CHROMA_COLLECTION_NAME
    existing = [c.name for c in client.list_collections()]
    if name in existing:
        collection = client.get_collection(name)
        count = collection.count()
        return {"name": name, "count": count, "exists": True}
    return {"name": name, "count": 0, "exists": False}


def _sanitize_metadata(metadata: dict) -> dict:
    """清理 metadata — ChromaDB 只接受 str/int/float/bool，不接受 None。"""
    clean = {}
    for k, v in metadata.items():
        if v is None:
            clean[k] = ""
        elif isinstance(v, (str, int, float, bool)):
            clean[k] = v
        else:
            clean[k] = str(v)
    return clean
