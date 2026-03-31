# 實作計畫

> **English summary:** Implement retriever.py (ChromaDB query + embed query) and generator.py (LLM chat completion with grounding prompt), then validate with real questions.

## 做法

Retriever 把用戶問題用 embedder 轉成向量，再用 ChromaDB 的 query API 搜最相似的 chunk。Generator 把搜出來的 chunk 塞進 prompt template，呼叫 LLM 的 chat completion API 生成回答。

## 關鍵決策

| 決策 | 選擇 | 理由 |
|------|------|------|
| 搜尋方式 | ChromaDB 內建 cosine similarity | 不用自己算，ChromaDB 自帶 |
| Prompt 策略 | 明確告訴 LLM「只根據參考資料回答」 | 減少幻覺，DESIGN.md 已定義 prompt 模板 |
| LLM API | /v1/chat/completions（OpenAI 相容） | oMLX 和 Ollama 都支援 |
| 回答語言 | 不限定，跟隨問題語言 | 中文問中文答、英文問英文答 |

## 風險

| 風險 | 對策 |
|------|------|
| Qwen3-VL 8B 在 M1 16GB 上生成很慢 | 可接受，學習用不追求速度 |
| LLM 不遵從「不知道就說不知道」的指令 | prompt 明確寫規則，Temperature 設低 |
| 搜出來的 chunk 不相關 | 先不加門檻，觀察實際效果再決定 |

## 實作順序

1. `retriever.py` — query embedding + ChromaDB 搜尋
2. `generator.py` — prompt 組裝 + LLM chat completion
3. 測試 — unit test + 真實問答驗證
4. `notes.md` — retrieval 原理 + prompt engineering
