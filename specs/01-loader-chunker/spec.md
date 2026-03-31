# Loader + Chunker

> **English summary:** Markdown document loader (recursive directory scan) and chunker (split by headings, fallback to fixed-length with overlap). No external dependencies — runs without Ollama.

## 背景

RAG pipeline 的前兩步：把原始 Markdown 文件讀進來（Loader），然後切成適合 embedding 的小塊（Chunker）。對應 DESIGN.md 的 Stage 1 + Stage 2。

這兩步不依賴任何外部服務（不需要 Ollama、不需要 ChromaDB），可以獨立開發和測試。

知識庫來源：your markdown documents directory（一批 Markdown 技術文件）。

## 驗收條件

### Loader

- [ ] AC-1: 給一個資料夾路徑，遞迴掃描所有 `.md` 檔案，回傳文件列表
- [ ] AC-2: 每份文件包含 `content`（完整內容）和 `metadata`（檔名、完整路徑）
- [ ] AC-3: 非 `.md` 檔案自動跳過，不報錯
- [ ] AC-4: 空資料夾回傳空列表，不報錯
- [ ] AC-5: 檔案有 YAML frontmatter 時，frontmatter 從 content 中移除，但保留在 metadata 中

### Chunker

- [ ] AC-6: 按 Markdown heading（`#`, `##`, `###`）切塊，每個 chunk 對應一個 section
- [ ] AC-7: 每個 chunk 帶 metadata：來源檔名、heading 標題、heading 層級、在原文中的位置（第幾個 chunk）
- [ ] AC-8: 單一 section 超過 500 字時，用固定長度（500 字）+ overlap（50 字）二次切割
- [ ] AC-9: 沒有任何 heading 的文件，整份視為一個 chunk（如果超過 500 字，走二次切割）
- [ ] AC-10: 空文件跳過，不產生 chunk

### 整合

- [ ] AC-11: Loader 的輸出可以直接餵給 Chunker，end-to-end 跑 `./sample_docs/` 不報錯
- [ ] AC-12: 有基本的 logging，顯示處理了幾個檔案、產生了幾個 chunk

## 不做的事

- 不處理 PDF / Word / HTML（只做 Markdown）
- 不做 embedding（那是 spec-02 的事）
- 不做 token 計算（用字數近似，不引入 tokenizer 依賴）
- 不做增量更新（每次全量處理）

## 依賴

- Python 3.11+（MBP 已有）
- 無外部服務依賴
