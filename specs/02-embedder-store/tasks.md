# 任務清單

> **English summary:** Task checklist for embedder + store implementation.

**Spec:** 02-embedder-store
**Status:** VERIFIED

## Checklist

- [x] Task 1: embedder.py — 呼叫 /v1/embeddings API，支援批次處理，有進度 logging
- [x] Task 2: store.py — ChromaDB wrapper（建 collection、存入向量+metadata、重建、查詢狀態）
- [x] Task 3: tests — embedder + store unit test + 整合測試（全量文件跑）
- [x] Task 4: notes.md — 學習筆記：embedding 原理、向量資料庫

## 備註

- 需要 oMLX 跑著（bge-m3-mlx-fp16）
- pyproject.toml 要加 httpx 依賴
- 整合測試會在 .chroma/ 產生持久化資料
