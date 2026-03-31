# Pipeline CLI

> **English summary:** CLI interface that chains all pipeline stages together. Three commands: `ingest` (load → chunk → embed → store), `ask` (single question), `chat` (interactive loop).

## 背景

把 spec-01 到 spec-03 的模組串成一個可用的 CLI 工具。用戶不需要寫 Python，直接在終端機操作整個 RAG pipeline。

## 驗收條件

### ingest 指令

- [ ] AC-1: `python -m src.pipeline ingest <目錄>` 執行完整的 load → chunk → embed → store 流程
- [ ] AC-2: 完成後印出統計：文件數、chunk 數、向量維度、耗時
- [ ] AC-3: 沒給目錄路徑時，印出使用說明，不要炸掉

### ask 指令

- [ ] AC-4: `python -m src.pipeline ask "問題"` 執行 retrieve → generate，印出回答
- [ ] AC-5: 回答後印出引用來源（檔名 + similarity score）
- [ ] AC-6: ChromaDB 沒資料時，提示用戶先跑 ingest

### chat 指令

- [ ] AC-7: `python -m src.pipeline chat` 進入互動模式，可以連續問多個問題
- [ ] AC-8: 輸入 `quit` 或 `exit` 或 Ctrl+C 可以退出
- [ ] AC-9: 每次回答後印出引用來源

### 通用

- [ ] AC-10: 用 rich 美化輸出（彩色、表格、進度條）
- [ ] AC-11: LLM server 沒開時，給出明確的錯誤提示（不是 traceback）

## 不做的事

- 不做 Web UI（CLI 就好）
- 不做 config 指令（直接用環境變數）
- 不做 daemon 模式（跑完就結束）

## 依賴

- rich — 已在 pyproject.toml
- spec-01 + 02 + 03 完成
- oMLX 或 Ollama 跑著
