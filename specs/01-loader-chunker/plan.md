# 實作計畫

> **English summary:** Implement loader.py and chunker.py with config, tests, and a learning notes document. No external dependencies needed.

## 做法

先做 config（集中管理參數），再做 loader（單純的檔案 I/O），再做 chunker（切割邏輯），最後寫測試。Loader 和 Chunker 都是純函式，不依賴外部服務，可以完全離線開發。

每個模組寫完都配一份 `notes.md` 學習筆記，解釋 RAG 中這一步的原理、為什麼這樣設計。

## 關鍵決策

| 決策 | 選擇 | 理由 |
|------|------|------|
| 切塊策略 | Markdown heading 優先，超長 fallback 固定長度 | Markdown 文件有結構，按標題切保留語意完整性 |
| 字數 vs token 計算 | 用字數（`len(text)`） | 不引入 tokenizer 依賴，中文 1 字 ≈ 1.5-2 token，夠用 |
| Frontmatter 處理 | 移除但保留在 metadata | Markdown 文件常見 frontmatter，留在 content 會污染 embedding |
| 資料結構 | dataclass（Document, Chunk） | 型別明確，IDE 有提示，比 dict 不容易寫錯 key |
| Overlap 實作 | 只在二次切割時用 | heading 切割的相鄰 section 本身有標題上下文，不需要 overlap |

## 風險

| 風險 | 對策 |
|------|------|
| Markdown 文件格式不一致（有些沒 heading、有些 heading 層級混亂） | AC-9 已定義 fallback：無 heading 視為單一 chunk |
| 中文字數計算不精準（混合英文、code block） | 第一版用字數近似，之後可以加 token 計算比較差異 |
| Frontmatter 格式不標準（缺少 `---` 結尾） | 用 regex 匹配 `^---\n.*?\n---\n`，非標準的不處理 |

## 實作順序

1. `config.py` — 集中管理 chunk 參數（max_chunk_size, overlap_size 等），先做是因為 loader 和 chunker 都會用到
2. `loader.py` — 檔案 I/O，最單純，先確認能讀到所有文件
3. `chunker.py` — 切割邏輯，依賴 loader 的輸出格式
4. 測試 — loader 和 chunker 各自的 unit test + 整合測試
5. `notes.md` — 學習筆記，邊做邊寫
