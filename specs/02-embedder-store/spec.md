# Embedder + Vector Store

> **English summary:** Embed chunks via oMLX/Ollama OpenAI-compatible API (BGE-M3), store vectors + metadata in ChromaDB. Supports batch embedding and collection rebuild.

## 背景

RAG pipeline 的第三、四步：把 Chunker 產出的文字 chunk 轉成向量（Embedder），存進向量資料庫（ChromaDB）。對應 DESIGN.md 的 Stage 3 + Stage 4。

Embedder 透過 OpenAI 相容 API 呼叫 LLM server（oMLX 或 Ollama），不綁定特定 server。

## 驗收條件

### Embedder

- [ ] AC-1: 接收一個 chunk 文字，呼叫 `/v1/embeddings` API，回傳向量（list[float]）
- [ ] AC-2: 支援批次 embedding — 一次送多個 chunk，減少 API 呼叫次數
- [ ] AC-3: API 連不上時，拋出明確的錯誤訊息（包含 URL 和 model 名稱），不要靜默失敗
- [ ] AC-4: 有 logging 顯示進度（每 100 個 chunk 印一次）

### Store

- [ ] AC-5: 把 chunk 文字 + 向量 + metadata 存進 ChromaDB collection
- [ ] AC-6: 支援重建 collection（刪掉舊的再建新的）
- [ ] AC-7: 支援查詢 collection 狀態（有幾筆資料）
- [ ] AC-8: ChromaDB 資料持久化到 `.chroma/` 目錄，重啟程式後資料還在

### 整合

- [ ] AC-9: spec-01 的 chunk 輸出可以直接餵給 embedder → store，end-to-end 跑全量文件不報錯
- [ ] AC-10: 有 logging 顯示整體統計（幾個 chunk embedded、花了多少時間、存了幾筆）

## 不做的事

- 不做增量更新（每次全量重建 collection）
- 不做 embedding cache（重跑就重算）
- 不做相似度搜尋（那是 spec-03 的事）
- 不做多 collection 管理（只用一個 `rag_docs`）

## 依賴

- oMLX 或 Ollama — 提供 `/v1/embeddings` API
- BGE-M3（oMLX）或 nomic-embed-text（Ollama）— embedding model
- ChromaDB — `pip install chromadb`（pyproject.toml 已有）
- spec-01 完成 — loader + chunker 的輸出作為輸入
