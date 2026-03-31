# Web UI

> **English summary:** Gradio-based web interface for the RAG pipeline. Users can ask questions, see answers with source citations, and view retrieval details — all in a browser.

## 背景

目前 RAG pipeline 只能透過 CLI 操作。加一個 Web UI 讓使用者可以在瀏覽器中直接問問題、看回答、看引用來源，體驗更直覺。

## 驗收條件

### 基本功能

- [ ] AC-1: `python -m src.pipeline ui` 啟動 Web UI，瀏覽器自動開啟
- [ ] AC-2: 有輸入框讓使用者打問題，按 Enter 或按鈕送出
- [ ] AC-3: 回答顯示在頁面上，支援 Markdown 格式渲染
- [ ] AC-4: 回答下方顯示引用來源（檔名 + 段落 + 相似度分數）

### 使用體驗

- [ ] AC-5: 問答歷史保留在頁面上（chatbot 格式），不會每次清掉
- [ ] AC-6: 等待 LLM 回答時有 loading 狀態提示
- [ ] AC-7: ChromaDB 沒資料時，頁面顯示提示訊息（不是白屏）

### 運維

- [ ] AC-8: LLM server 沒開時，頁面顯示錯誤訊息（不是 500 error）
- [ ] AC-9: 預設跑在 localhost:7860，不對外開放

## 不做的事

- 不做使用者認證（本地工具，不需要登入）
- 不做 ingest UI（用 CLI 匯入就好）
- 不做 streaming 輸出（一次回傳完整回答）
- 不做部署（本地跑就好）

## 依賴

- Gradio — 輕量 web UI framework，Python 生態最方便
- spec-01~04 完成
- oMLX 或 Ollama 跑著
