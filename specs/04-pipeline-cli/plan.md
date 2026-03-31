# 實作計畫

> **English summary:** Implement pipeline.py as CLI entry point with three subcommands using argparse + rich for output formatting.

## 做法

一個 `pipeline.py` 搞定，用 argparse 做 subcommand（ingest / ask / chat）。不引入 click 或 typer — argparse 內建就夠了。用 rich 美化輸出。

## 關鍵決策

| 決策 | 選擇 | 理由 |
|------|------|------|
| CLI framework | argparse（內建） | 不加依賴，三個指令不需要 click/typer |
| 輸出美化 | rich | 已在 pyproject.toml，支援彩色、表格、進度條 |
| 錯誤處理 | try/except 包頂層 | 不讓 traceback 嚇到用戶 |

## 風險

| 風險 | 對策 |
|------|------|
| ingest 跑太久沒進度感 | 用 rich progress bar 顯示 embedding 進度 |
| chat 模式中 LLM 回答慢 | 印 "思考中..." 提示 |

## 實作順序

1. `pipeline.py` — argparse + ingest/ask/chat 三個指令
2. 手動測試 — 跑三個指令確認流程順暢
3. `notes.md` — 整體 RAG pipeline 學習筆記
