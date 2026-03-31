# Embedder & Vector Store — RAG 學習筆記

> **English summary:** Learning notes on Embedding and Vector Store in RAG pipelines — what embeddings are, how vector databases work, and key design decisions.

## 這兩步在 RAG 裡的角色

```
文件 → [Loader] → [Chunker] → [Embedder] → [Vector DB] → [Retriever] → [Generator] → 回答
                                  ^^^          ^^^
                                  這次做的
```

Chunker 切完的 chunk 是「人看得懂的文字」，但電腦不懂語意。Embedder 把文字轉成「電腦看得懂的數字」（向量），Vector Store 把這些向量存起來，之後才能做語意搜尋。

## Embedding 是什麼？

### 簡單說

把一段文字變成一串數字（向量），讓語意相近的文字在數學空間中靠在一起。

```
"如何設定 Telegram bot" → [0.12, -0.03, 0.87, ..., 0.45]  (1024 個數字)
"Telegram 機器人設定教學" → [0.11, -0.02, 0.85, ..., 0.44]  (很接近！)
"今天天氣真好"           → [0.92, 0.31, -0.15, ..., 0.08]  (離很遠)
```

### 為什麼不用關鍵字搜尋？

關鍵字搜尋（like `LIKE '%Telegram%'`）的問題：

1. **同義詞找不到** — 搜「機器人」找不到寫「bot」的文件
2. **多語言障礙** — 搜中文找不到英文內容
3. **語意不匹配** — 搜「怎麼部署」找不到寫「installation guide」的段落

向量搜尋解決這些問題，因為它比較的是**語意**而不是字面。

### Embedding Model 怎麼選？

| Model | 維度 | 特色 | 適用場景 |
|-------|------|------|---------|
| BGE-M3 | 1024 | 多語言、效果好 | 中英混合文件（我們用的） |
| nomic-embed-text | 768 | 輕量、Ollama 原生 | 英文為主、資源有限 |
| OpenAI text-embedding-3-small | 1536 | 最方便 | 有預算、不想管 infra |
| OpenAI text-embedding-3-large | 3072 | 效果最好 | 企業級、精度要求高 |

本地練習用 BGE-M3 就夠了，到公司換 OpenAI 只要改一行 URL + model name。

### 維度越高越好嗎？

不一定。高維度 = 更多資訊 = 更精準，但也 = 更多儲存空間 + 更慢的搜尋速度。

- 768 維：夠用，搜尋快
- 1024 維：平衡點（我們用的）
- 3072 維：精度最好，但存一百萬筆就很吃硬碟

## Vector Store（向量資料庫）

### 為什麼不用普通資料庫？

PostgreSQL 存一百萬個 1024 維向量沒問題，但搜尋的時候要跟每一個向量算 cosine similarity — O(n) 全掃。

向量資料庫用特殊的索引結構（HNSW、IVF）讓搜尋接近 O(log n)。

### ChromaDB vs 其他

| DB | 特色 | 適用場景 |
|----|------|---------|
| ChromaDB | 純 Python、零設定、本地檔案 | 原型、學習、小規模（我們用的） |
| Pinecone | 全託管、自動擴展 | 企業級、不想管 infra |
| Weaviate | 開源、多模態 | 圖片+文字混合搜尋 |
| pgvector | PostgreSQL 擴展 | 已有 PostgreSQL、不想多一個 DB |
| Qdrant | Rust 寫的、高效能 | 大規模、需要效能 |

### Cosine Similarity 怎麼運作？

兩個向量之間的夾角越小，cosine similarity 越接近 1（完全一致），越接近 0（無關），-1（完全相反）。

```
cos(A, B) = (A · B) / (|A| × |B|)
```

不用自己算 — ChromaDB 內建了。你只要把問題轉成向量，ChromaDB 幫你跟所有存的向量比，回傳最相似的 Top-K 個。

## 本次實作的數據

| 指標 | 數值 |
|------|------|
| Chunk 數 | ~2000+ |
| 向量維度 | 1024（BGE-M3 fp16） |
| Embedding 耗時 | ~159 秒（M1 16GB, oMLX） |
| ChromaDB 存入 | 全量 |
| LLM Server | oMLX（OpenAI 相容 API） |

### 跟 Ollama + nomic-embed-text 的差異

| | oMLX + BGE-M3 | Ollama + nomic-embed-text |
|--|--------------|--------------------------|
| 維度 | 1024 | 768 |
| 多語言 | 強（中英日韓） | 普通（以英文為主） |
| 模型大小 | 1.1 GB (fp16) | ~270 MB |
| API | OpenAI 相容 | Ollama 原生（也有 OpenAI 相容） |

兩個都能用。BGE-M3 效果更好但更大，nomic-embed-text 更輕量。
