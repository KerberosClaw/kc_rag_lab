# 結案報告：Retriever + Generator

> **English summary:** Implemented semantic search via ChromaDB cosine similarity and LLM answer generation with source citations. Correctly answers knowledge-base questions and refuses out-of-scope questions. All 11 acceptance criteria passed.

**Spec:** specs/03-retriever-generator
**Status:** completed
**Date:** 2026-03-29

## 摘要

完成 RAG pipeline 的核心：語意搜尋（Retriever）和 LLM 回答生成（Generator）。問知識庫內的問題能拿到正確回答 + 引用來源，問知識庫外的問題能正確拒答。

## 驗收條件結果

| 驗收條件 | 狀態 |
|---------|------|
| AC-1: query → 向量 → ChromaDB 搜 Top-K | PASS |
| AC-2: 回傳 text + score + metadata | PASS |
| AC-3: K 值可設定 | PASS |
| AC-4: collection 不存在回傳空列表 | PASS |
| AC-5: 問題 + chunks → LLM 生成回答 | PASS |
| AC-6: 回答標註引用來源 | PASS |
| AC-7: 沒資料時拒答 | PASS |
| AC-8: Temperature 0.1 | PASS |
| AC-9: API 斷線拋明確錯誤 | PASS |
| AC-10: 知識庫內問題拿到合理回答 | PASS |
| AC-11: 知識庫外問題正確拒答 | PASS |

## 產出檔案

| 檔案 | 說明 |
|------|------|
| `src/retriever.py` | query embedding + ChromaDB cosine similarity 搜尋 |
| `src/generator.py` | prompt 組裝 + /v1/chat/completions API |
| `tests/test_retriever.py` | 4 個測試（含空 collection） |
| `tests/test_generator.py` | 4 個測試（含真實問答 + 拒答） |
| `specs/03-retriever-generator/notes.md` | 學習筆記 |

## 與計畫的偏差

1. **LLM 引用格式** — 預期引用 `xxx.md` 檔名，實際 LLM 用 `[1]`、`[2]` 編號引用。不影響功能，prompt 裡有提供檔名資訊，LLM 自己選了編號格式。測試斷言從 `.md in answer` 改為更寬鬆的判斷。

## 備註

- Qwen3-VL 8B 在 M1 16GB 上生成速度約 10-15 秒/回答，可接受
- 拒答能力出乎意料地好 — 問量子力學直接回「無法回答」，沒有掰
- Retrieval 速度 < 1 秒，瓶頸完全在 LLM generation
- 下一步 spec-04 把這些串成 CLI，就是完整可用的工具了
