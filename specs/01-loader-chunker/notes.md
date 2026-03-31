# Loader & Chunker — RAG 學習筆記

> **English summary:** Learning notes on Document Loading and Chunking in RAG pipelines — what they do, why they matter, and key design decisions.

## 這兩步在 RAG 裡的角色

RAG 的完整 pipeline：

```
文件 → [Loader] → [Chunker] → [Embedder] → [Vector DB] → [Retriever] → [Generator] → 回答
         ^^^        ^^^
         這次做的
```

Loader 和 Chunker 是 pipeline 的「入口」。如果這兩步做爛了，後面全部都會爛 — garbage in, garbage out。

## Loader 做什麼？

把原始文件讀進來，轉成程式能處理的格式。聽起來很無聊，但有幾個重點：

1. **Metadata 很重要** — 不只是讀內容，還要記住「這段話來自哪個檔案」。之後回答問題時要能引用來源（「根據 XX.md 的內容...」），沒有 metadata 就做不到。

2. **Frontmatter 要處理** — 很多 Markdown 檔案開頭會有 YAML frontmatter（`---` 包起來的區塊）。這些是文件的 meta 資訊（標題、標籤），不是正文。如果不移除，embedding 會被 `title: XXX` 這種格式字串污染。

3. **錯誤容忍** — 真實世界的文件會有亂碼、權限問題、空檔案。Loader 要能跳過壞檔案繼續處理，不能因為一個檔案就整個炸掉。

## Chunker 做什麼？為什麼需要切塊？

把完整文件切成小片段。這是 RAG 最關鍵的一步。

### 為什麼不把整份文件丟進去？

兩個原因：

1. **Embedding model 有 token 上限** — nomic-embed-text 上限 8192 tokens。一份長文件可能超過。
2. **更重要的是精準度** — 把一整份 3000 字的文件轉成一個向量，這個向量代表的是整份文件的「平均語意」。如果文件裡同時講了 A、B、C 三件事，這個向量就會變成 A+B+C 的模糊混合。當用戶問 A 的問題時，搜出來的結果會被 B 和 C 的雜訊拉低相關度。

切成小塊後，每個 chunk 的向量就只代表一件事，搜尋精準度大幅提升。

### 切塊策略比較

| 策略 | 做法 | 優點 | 缺點 |
|------|------|------|------|
| **固定長度** | 每 500 字切一刀 | 簡單、chunk 大小均勻 | 會切斷句子、段落、甚至答案 |
| **按句子/段落** | 用句號或空行切 | 不會切斷句子 | chunk 大小差異大、可能太小 |
| **按 heading（我們用的）** | 用 Markdown `#` 切 | 保留語意完整性、有天然結構 | 只適用 Markdown、section 大小不一 |
| **語意切塊** | 用 embedding 判斷語意轉折點 | 最精準 | 慢、需要額外 model、複雜 |

選 heading 切塊是因為知識庫全是結構化的 Markdown，有天然結構。如果文件是 PDF 或純文字，就要換策略。

### Overlap 是什麼？為什麼需要？

```
原文：AAAA|BBBB|CCCC
      ←500→←500→←500→

不重疊切割：
  chunk1: AAAA
  chunk2: BBBB
  chunk3: CCCC

overlap=50 的切割：
  chunk1: AAAA
  chunk2: ...AA BBBB    ← 前面重疊 50 字
  chunk3: ...BB CCCC    ← 前面重疊 50 字
```

重疊的目的：如果答案剛好在兩個 chunk 的交界處（比如一個句子被切斷了），overlap 確保這個句子完整出現在至少一個 chunk 裡。

我們只在「二次切割」（section 太長時的 fallback）才用 overlap。heading 切割的相鄰 section 不需要，因為它們是不同主題。

### Chunk 大小的 trade-off

- **太大（>1000 字）**：向量語意被稀釋、搜尋不精準、浪費 LLM 的 context window
- **太小（<100 字）**：缺少上下文、LLM 看不出完整意思
- **甜蜜點（200-500 字）**：大多數 RAG 系統的建議值

## 本次實作的數據

用一批 Markdown 文件實測：

- 文件切塊後產生數千個 chunk
- 平均每份文件產生 ~27 個 chunk
- Chunk 字數：min=2, max=500, avg=258
- 整個處理時間 < 1 秒
