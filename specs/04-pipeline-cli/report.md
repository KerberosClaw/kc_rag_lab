# 結案報告：Pipeline CLI

> **English summary:** Implemented CLI with three commands (ingest/ask/chat) using argparse + rich. Full RAG pipeline is now usable from the terminal. All 11 acceptance criteria passed.

**Spec:** specs/04-pipeline-cli
**Status:** completed
**Date:** 2026-03-29

## 摘要

完成 RAG pipeline 的最後一步：把所有模組串成 CLI 工具。三個指令：`ingest`（匯入文件）、`ask`（單次問答）、`chat`（互動模式）。用 rich 美化輸出，錯誤處理清楚。

## 驗收條件結果

| 驗收條件 | 狀態 |
|---------|------|
| AC-1: ingest 跑完整流程 | PASS |
| AC-2: 完成後印統計 | PASS |
| AC-3: 沒給路徑印使用說明 | PASS |
| AC-4: ask 執行 retrieve → generate | PASS |
| AC-5: 回答後印引用來源 | PASS |
| AC-6: 沒資料時提示先 ingest | PASS |
| AC-7: chat 互動模式 | PASS |
| AC-8: quit/exit/Ctrl+C 退出 | PASS |
| AC-9: chat 每次印引用來源 | PASS |
| AC-10: rich 美化輸出 | PASS |
| AC-11: LLM 沒開時明確錯誤提示 | PASS |

## 產出檔案

| 檔案 | 說明 |
|------|------|
| `src/pipeline.py` | CLI 入口（argparse + rich + 錯誤處理） |
| `src/__main__.py` | 讓 `python -m src.pipeline` 能用 |
| `.gitignore` | 加入 .chroma/、.venv/、__pycache__/ 等 |
| `specs/04-pipeline-cli/notes.md` | 整體 RAG pipeline 學習筆記 |

## 與計畫的偏差

無。按計畫完成。

## 備註

- 整個 RAG pipeline 從 spec-01 到 spec-04 在一個 session 內完成
- 總程式碼量約 400 行（不含測試），測試 46 個
- CLI 不寫 unit test — 核心邏輯都在 spec-01~03 測過了，CLI 只是薄薄的膠水層
