# 結案報告：Embedder + Vector Store

> **English summary:** Implemented embedding via oMLX OpenAI-compatible API (BGE-M3, 1024-dim) and ChromaDB storage. All chunks embedded in ~159s on M1 16GB, all 10 acceptance criteria passed.

**Spec:** specs/02-embedder-store
**Status:** completed
**Date:** 2026-03-29

## 摘要

完成 RAG pipeline 的第三、四步：透過 oMLX 的 OpenAI 相容 API 呼叫 BGE-M3 做 embedding，再存入 ChromaDB。全部 chunk 全量 embedding + 入庫，耗時約 2.5 分鐘。

## 驗收條件結果

| 驗收條件 | 狀態 |
|---------|------|
| AC-1: 單一 chunk embedding 回傳向量 | PASS |
| AC-2: 批次 embedding | PASS |
| AC-3: API 連不上拋明確錯誤 | PASS |
| AC-4: 進度 logging | PASS |
| AC-5: chunk + 向量 + metadata 存入 ChromaDB | PASS |
| AC-6: 重建 collection | PASS |
| AC-7: 查詢 collection 狀態 | PASS |
| AC-8: 持久化到 .chroma/ | PASS |
| AC-9: end-to-end 全量不報錯 | PASS |
| AC-10: 整體統計 logging | PASS |

## 產出檔案

| 檔案 | 說明 |
|------|------|
| `src/embedder.py` | OpenAI 相容 API client，批次 embedding（BATCH_SIZE=32） |
| `src/store.py` | ChromaDB wrapper（rebuild、查詢、metadata 清理） |
| `src/config.py` | 更新：改用環境變數切換 oMLX/Ollama，預設 oMLX |
| `tests/test_embedder.py` | 4 個測試（含 connection error） |
| `tests/test_store.py` | 5 個測試（含 rebuild 覆蓋驗證） |
| `pyproject.toml` | 加入 httpx 依賴，移除 ollama SDK |
| `specs/02-embedder-store/notes.md` | 學習筆記 |

## 與計畫的偏差

1. **config.py 改用環境變數** — 原本寫死 Ollama URL，改成 `RAG_LLM_URL` / `RAG_LLM_KEY` / `RAG_EMBED_MODEL` 環境變數，預設指向 oMLX。因為開發環境改用本機 oMLX。
2. **ChromaDB v1.0 API 變更** — `delete_collection` 和 `get_collection` 在 collection 不存在時拋 `NotFoundError` 而非 `ValueError`。改用 `list_collections()` 先檢查再操作。
3. **metadata 清理** — ChromaDB v1.0 不接受 `None` 作為 metadata value。加了 `_sanitize_metadata()` 把 `None` 轉成空字串。
4. **移除 ollama SDK 依賴** — 改用 httpx 直接呼叫 OpenAI 相容 API，不再需要 `ollama>=0.4`。

## 效能數據

| 指標 | 數值 |
|------|------|
| Embedding model | BGE-M3 fp16（1024 維） |
| LLM server | oMLX（MBP M1 16GB） |
| Chunk 數 | ~2000+ |
| Batch size | 32 |
| 總耗時 | ~159 秒 |
| 每 chunk 平均 | ~76 ms |

## 備註

- oMLX 在 M1 16GB 上跑 BGE-M3 fp16 效能可接受，不需要等 PC 的 Ollama
- `.chroma/` 目錄需要加入 `.gitignore`（向量資料不該進 git）
- 之後切回 Ollama + nomic-embed-text 只要設環境變數：`RAG_LLM_URL=http://your-ollama-host:11434/v1 RAG_EMBED_MODEL=nomic-embed-text RAG_LLM_KEY=`
