# 結案報告：Web UI

> **English summary:** Added Gradio-based web chat interface. Users can ask questions in the browser with Markdown-rendered answers, source citations, and chat history. All 9 acceptance criteria passed.

**Spec:** specs/05-web-ui
**Status:** completed
**Date:** 2026-03-29

## 摘要

在 RAG pipeline 上加了 Gradio Web UI，使用者可以在瀏覽器中直接問答、看引用來源，不用碰終端機。

## 驗收條件結果

| 驗收條件 | 狀態 |
|---------|------|
| AC-1: ui 指令啟動 Web UI | PASS |
| AC-2: 輸入框 + 送出按鈕 | PASS |
| AC-3: Markdown 渲染 | PASS |
| AC-4: 引用來源表格 | PASS |
| AC-5: 問答歷史保留 | PASS |
| AC-6: loading 狀態 | PASS |
| AC-7: 沒資料時提示 | PASS |
| AC-8: LLM 沒開時錯誤訊息 | PASS |
| AC-9: localhost:7860 | PASS |

## 產出檔案

| 檔案 | 說明 |
|------|------|
| `src/webui.py` | Gradio ChatInterface + 引用來源格式化 |
| `src/pipeline.py` | 加入 `ui` subcommand |
| `pyproject.toml` | 加入 gradio 依賴 |

## 與計畫的偏差

1. **Gradio 6.0 API 變更** — `ChatInterface` 移除了 `type` 參數，`Blocks` 的 `theme` 參數移到 `launch()`。兩個都修了。

## 備註

- 必須用 `uv run python -m src.pipeline ui` 啟動，不能直接用系統 Python（缺依賴）
- Gradio 6 的 ChatInterface 已經很完整，不需要自己刻 chatbot 元件
