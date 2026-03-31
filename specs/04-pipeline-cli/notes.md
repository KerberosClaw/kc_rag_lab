# 整體 RAG Pipeline — 學習筆記

> **English summary:** Complete RAG pipeline learning notes — architecture overview, each stage's role, comparison with frameworks, and production considerations.

## RAG 是什麼？一句話版本

> 讓 LLM 在回答問題之前，先去搜你的文件，用搜到的內容當參考資料回答，而不是靠自己的訓練知識掰。

**R**etrieval — 搜
**A**ugmented — 用搜到的東西補強
**G**eneration — 生成回答

## 完整 Pipeline

```
         Ingest（離線）                    Query（線上）
         ───────────                    ─────────────

.md 文件 → [Loader] → [Chunker]         用戶問題
                         ↓                  ↓
                    [Embedder]          [Embedder]
                         ↓                  ↓
                    [Vector DB] ←──搜──→ [Retriever]
                                            ↓
                                       [Generator] → 回答 + 引用
```

左邊是離線的「準備工作」（ingest），只要文件沒變就不用重跑。
右邊是線上的「問答」（query），每次問問題都走一遍。

## 各階段的角色（快速回顧）

| 階段 | 做什麼 | 最重要的設計決策 |
|------|--------|----------------|
| Loader | 讀 .md 檔 + 處理 frontmatter | 保留 metadata（之後引用來源用） |
| Chunker | 按 heading 切塊 | 切塊策略直接影響搜尋精準度 |
| Embedder | 文字 → 向量 | 問題和文件必須用同一個 model |
| Vector DB | 存向量 + 支援相似度搜尋 | ChromaDB 零設定，企業級用 Pinecone |
| Retriever | cosine similarity 搜 Top-K | K 太小漏資訊，太大浪費 token |
| Generator | prompt + LLM 生成回答 | 低 Temperature + 明確拒答指令防幻覺 |

## 為什麼不用 LangChain / LlamaIndex？

| | 手刻 | LangChain |
|--|------|-----------|
| 學到什麼 | 每一步的原理和 trade-off | 怎麼用 API |
| 理解深度 | 能解釋為什麼這樣切、為什麼這樣搜 | 只能說「我用 LangChain」 |
| 彈性 | 換任何一個零件都知道怎麼改 | 被框架綁住，換零件要看文件 |
| 速度 | 慢（要自己寫） | 快（幾行搞定） |
| 適合場景 | 學習、深入理解 | 快速原型、production |

先手刻理解原理，之後再用 LangChain 加速開發。

## Production 要考慮的事

我們的練習版 vs 企業級的差異：

| 項目 | 練習版 | 企業級 |
|------|--------|--------|
| Embedding | 本地 BGE-M3 | OpenAI text-embedding-3 |
| Vector DB | ChromaDB（檔案） | Pinecone / pgvector（雲端） |
| LLM | 本地 8B | GPT-4o / Claude |
| 更新策略 | 全量重建 | 增量更新 + CDC |
| 切塊策略 | heading 固定切 | semantic chunking |
| 搜尋優化 | 純 cosine similarity | + reranking + hybrid search |
| 幻覺防治 | prompt 指令 | + faithfulness evaluation |
| 可觀測性 | logging | LangSmith / Langfuse 追蹤 |
| 多用戶 | 單人 | 權限控制 + 多租戶 |

## 本專案的數據總覽

| 指標 | 數值 |
|------|------|
| 知識庫 | 一批 Markdown 技術文件 |
| Chunk 數 | ~2000+ |
| 向量維度 | 1024（BGE-M3 fp16） |
| Ingest 耗時 | ~159 秒（M1 16GB, oMLX） |
| Retrieval 速度 | < 1 秒 |
| Generation 速度 | ~10-15 秒（Qwen3-VL 8B） |
| 知識庫內問答 | 正確回答 + 引用來源 |
| 知識庫外問答 | 正確拒答 |
| 程式碼量 | ~400 行（不含測試） |
| 測試 | 46 個（29 offline + 17 integration） |
