"""Stage 5: Retriever — 從向量資料庫搜出最相關的 chunk。"""

import logging
from dataclasses import dataclass

import chromadb

from .config import CHROMA_COLLECTION_NAME, TOP_K
from .embedder import embed_single
from .store import get_client

logger = logging.getLogger(__name__)


@dataclass
class RetrievalResult:
    """搜尋結果：一個相關的 chunk。"""
    text: str
    score: float
    metadata: dict


def retrieve(
    query: str,
    top_k: int = TOP_K,
    client: chromadb.ClientAPI | None = None,
    collection_name: str | None = None,
) -> list[RetrievalResult]:
    """搜尋最相關的 chunk。

    Args:
        query: 用戶問題
        top_k: 回傳幾個結果
        client: ChromaDB client（None 則自動建立）
        collection_name: collection 名稱

    Returns:
        RetrievalResult 列表，按相似度排序（最相似在前）
    """
    client = client or get_client()
    name = collection_name or CHROMA_COLLECTION_NAME

    # 檢查 collection 是否存在
    existing = [c.name for c in client.list_collections()]
    if name not in existing:
        logger.warning("Collection '%s' 不存在，請先跑 ingest", name)
        return []

    collection = client.get_collection(name)
    if collection.count() == 0:
        logger.warning("Collection '%s' 是空的，請先跑 ingest", name)
        return []

    # 把問題轉成向量
    query_embedding = embed_single(query)

    # 搜尋
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
    )

    # 組裝結果
    retrieval_results = []
    documents = results["documents"][0]
    distances = results["distances"][0]
    metadatas = results["metadatas"][0]

    for doc, dist, meta in zip(documents, distances, metadatas):
        # ChromaDB 回傳的是 distance（越小越相似），轉成 similarity
        score = 1.0 - dist
        retrieval_results.append(RetrievalResult(
            text=doc,
            score=score,
            metadata=meta,
        ))

    logger.info(
        "搜尋 '%s' → %d 個結果（最高分: %.3f）",
        query[:30], len(retrieval_results),
        retrieval_results[0].score if retrieval_results else 0,
    )
    return retrieval_results
