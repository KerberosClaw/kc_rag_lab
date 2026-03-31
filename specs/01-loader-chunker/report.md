# 結案報告：Loader + Chunker

> **English summary:** Implemented Markdown document loader and heading-based chunker. Sample docs processed into chunks, avg 258 chars, all 12 acceptance criteria passed, 29 tests green.

**Spec:** specs/01-loader-chunker
**Status:** completed
**Date:** 2026-03-29

## 摘要

完成 RAG pipeline 的前兩步：Markdown 文件載入（Loader）和文件切塊（Chunker）。用一批 Markdown 文件實測，產生數千個 chunk，平均 258 字，處理時間 < 1 秒。

## 驗收條件結果

| 驗收條件 | 狀態 |
|---------|------|
| AC-1: 遞迴掃描 .md 檔案 | PASS |
| AC-2: content + metadata（檔名、路徑） | PASS |
| AC-3: 非 .md 跳過不報錯 | PASS |
| AC-4: 空資料夾回傳空列表 | PASS |
| AC-5: frontmatter 移除但保留在 metadata | PASS |
| AC-6: 按 heading 切塊 | PASS |
| AC-7: chunk metadata 完整 | PASS |
| AC-8: 超過 500 字二次切割 + overlap | PASS |
| AC-9: 無 heading 視為一個 chunk | PASS |
| AC-10: 空文件跳過 | PASS |
| AC-11: end-to-end 跑 sample_docs/ 不報錯 | PASS |
| AC-12: logging 顯示統計 | PASS |

## 產出檔案

| 檔案 | 說明 |
|------|------|
| `src/config.py` | 資料結構（Document, Chunk）+ 全域參數 |
| `src/loader.py` | 遞迴掃描 + frontmatter 處理 |
| `src/chunker.py` | heading 切割 + 固定長度 fallback + overlap |
| `tests/test_loader.py` | 11 個測試 |
| `tests/test_chunker.py` | 18 個測試 |
| `specs/01-loader-chunker/notes.md` | 學習筆記 |

## 與計畫的偏差

1. **AC-5（frontmatter 處理）**是實作時追加的，DESIGN.md 沒有提到。Markdown 文件常見 frontmatter，不處理會污染 embedding。
2. **chunker.py 的 heading 解析**第一版有 bug — regex 只 match `#` 和空白，沒抓到標題文字。修了 `_split_by_headings` 的取行邏輯後修復。
3. **`_split_by_length` 的邊界條件** — 當文字長度剛好等於 max_size 時會多產一個空 chunk。加了 `end >= len(text)` 的 break 條件修復。

## 備註

- `config.py` 已預先定義了 spec-02（Ollama）和 spec-03（Retriever）的參數，之後不用再改這個檔案
- 整合測試發現有些 chunk 只有 2 個字（通常是只有標題沒有內容的 section），不影響功能但之後做 embedding 時可以考慮設最小字數門檻
- `.venv/` 和 `README.md`（空檔）是跑測試時自動建立的
