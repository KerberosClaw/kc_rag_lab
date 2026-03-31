"""Stage 3: Embedding — 把 chunk 文字轉成向量。

透過 OpenAI 相容的 /v1/embeddings API 呼叫 LLM server（oMLX 或 Ollama）。
"""

import logging
import time

import httpx

from .config import Chunk, LLM_BASE_URL, LLM_API_KEY, EMBEDDING_MODEL

logger = logging.getLogger(__name__)

BATCH_SIZE = 32
TIMEOUT = 60  # 秒


def embed_chunks(chunks: list[Chunk]) -> list[list[float]]:
    """把多個 chunk 轉成向量。

    Args:
        chunks: Chunker 回傳的 Chunk 列表

    Returns:
        向量列表，順序跟 chunks 一致
    """
    if not chunks:
        return []

    all_embeddings = []
    total = len(chunks)
    start_time = time.time()

    for i in range(0, total, BATCH_SIZE):
        batch = chunks[i:i + BATCH_SIZE]
        texts = [c.text for c in batch]

        embeddings = _call_embedding_api(texts)
        all_embeddings.extend(embeddings)

        done = min(i + BATCH_SIZE, total)
        if done % 100 < BATCH_SIZE or done == total:
            elapsed = time.time() - start_time
            logger.info("Embedding 進度: %d/%d (%.1f秒)", done, total, elapsed)

    elapsed = time.time() - start_time
    logger.info("Embedding 完成: %d 個 chunk, 耗時 %.1f 秒", total, elapsed)
    return all_embeddings


def embed_single(text: str) -> list[float]:
    """把單一文字轉成向量（用於 query embedding）。"""
    result = _call_embedding_api([text])
    return result[0]


def _call_embedding_api(texts: list[str]) -> list[list[float]]:
    """呼叫 /v1/embeddings API。"""
    url = f"{LLM_BASE_URL}/embeddings"
    headers = {"Content-Type": "application/json"}
    if LLM_API_KEY:
        headers["Authorization"] = f"Bearer {LLM_API_KEY}"

    payload = {
        "model": EMBEDDING_MODEL,
        "input": texts,
    }

    try:
        resp = httpx.post(url, json=payload, headers=headers, timeout=TIMEOUT)
        resp.raise_for_status()
    except httpx.ConnectError:
        raise ConnectionError(
            f"無法連線到 LLM server: {LLM_BASE_URL}\n"
            f"請確認 oMLX 或 Ollama 正在運行，且 model '{EMBEDDING_MODEL}' 已載入。"
        )
    except httpx.HTTPStatusError as e:
        raise RuntimeError(
            f"Embedding API 錯誤 ({e.response.status_code}): {e.response.text}\n"
            f"URL: {url}, Model: {EMBEDDING_MODEL}"
        )

    data = resp.json()
    # OpenAI 格式：data[i].embedding
    embeddings = [item["embedding"] for item in data["data"]]
    return embeddings
