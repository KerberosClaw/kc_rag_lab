# 實作計畫

> **English summary:** Implement embedder.py (OpenAI-compatible API client with batching) and store.py (ChromaDB wrapper), then run end-to-end with sample docs.

## 做法

Embedder 用 `httpx` 直接呼叫 OpenAI 相容的 `/v1/embeddings` API，不引入 openai SDK（減少依賴）。Store 用 ChromaDB 的 Python API，薄封裝一層。

## 關鍵決策

| 決策 | 選擇 | 理由 |
|------|------|------|
| HTTP client | httpx | 輕量、支援 async（之後可用）、不用裝 openai SDK |
| 批次大小 | 32 個 chunk/batch | BGE-M3 在 M1 16GB 上一次處理太多會慢，32 是平衡點 |
| ChromaDB embedding function | 不用 | 我們自己算好向量再存，不用 ChromaDB 內建的 embedding function |
| 向量維度 | 1024（BGE-M3） | oMLX 實測確認，比 nomic-embed-text 的 768 更大 |
| ID 格式 | `{filename}_{chunk_index}` | 簡單、可讀、重建時自動覆蓋 |

## 風險

| 風險 | 對策 |
|------|------|
| oMLX 處理大量 chunk 太慢 | batch=32，每 batch 幾秒，總共幾分鐘可接受 |
| 記憶體不夠（M1 16GB 跑 BGE-M3 + ChromaDB） | BGE-M3 fp16 ~1.1GB + ChromaDB 很輕量，16GB 夠 |
| API timeout | httpx 設 60 秒 timeout，失敗印錯誤繼續下一 batch |

## 實作順序

1. `embedder.py` — API client + 批次處理
2. `store.py` — ChromaDB wrapper（存入、重建、查詢）
3. 測試 — unit test + 整合測試
4. `notes.md` — embedding 原理 + 向量資料庫學習筆記
