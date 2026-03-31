# 任務清單

> **English summary:** Task checklist for loader-chunker implementation.

**Spec:** 01-loader-chunker
**Status:** VERIFIED

## Checklist

- [x] Task 1: config.py — 定義 chunk 參數（MAX_CHUNK_SIZE=500, OVERLAP_SIZE=50）和資料結構（Document, Chunk dataclass）
- [x] Task 2: loader.py — 遞迴掃描資料夾、讀取 .md 檔、處理 frontmatter、回傳 Document 列表
- [x] Task 3: chunker.py — heading 切割 + 超長 section 二次切割 + metadata 保留
- [x] Task 4: tests — loader unit test（含空資料夾、非 md 檔、frontmatter）+ chunker unit test（含無 heading、超長 section、空檔案）+ 整合測試（跑 sample_docs/）
- [x] Task 5: notes.md — 學習筆記：Loader 和 Chunker 在 RAG 中的角色、切塊策略比較

## 備註

- 全部可以離線完成，不需要 Ollama 或 PC
- `./sample_docs/` 放置 Markdown 測試文件，可作為真實測試資料
- dataclass 定義放 config.py，loader 和 chunker import 使用
