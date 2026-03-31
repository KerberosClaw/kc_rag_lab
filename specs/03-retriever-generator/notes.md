# Retriever & Generator — RAG 學習筆記

> **English summary:** Learning notes on Retrieval and Generation in RAG pipelines — how semantic search works, prompt engineering for grounding, and hallucination prevention.

## 這兩步在 RAG 裡的角色

```
文件 → [Loader] → [Chunker] → [Embedder] → [Vector DB] → [Retriever] → [Generator] → 回答
                                                             ^^^           ^^^
                                                             這次做的
```

前面四步都是「準備工作」— 把文件切好、轉向量、存起來。Retriever + Generator 才是用戶真正會碰到的部分：問問題 → 拿答案。

## Retriever 做什麼？

### 流程

```
用戶問題 "OpenClaw 怎麼設定？"
    ↓
Embedding（跟存 chunk 用同一個 model）
    ↓
[0.12, -0.03, 0.87, ..., 0.45]  ← 問題的向量
    ↓
ChromaDB cosine similarity 搜尋
    ↓
Top-5 最相似的 chunk + similarity score
```

### 為什麼用同一個 embedding model？

問題和文件必須用同一個 model 轉向量，否則它們不在同一個「語意空間」裡，cosine similarity 算出來沒意義。

類比：一個用公里、一個用英里，直接比數字沒意義。

### Top-K 怎麼選？

- **K 太小（1-2）**：可能漏掉相關資訊，回答不完整
- **K 太大（20+）**：塞太多 context 給 LLM，浪費 token、可能干擾回答
- **甜蜜點（3-5）**：大多數場景夠用

進階做法：先取 Top-20，再用 reranker（另一個 model）重新排序，取 Top-5。我們第一版不做 reranking。

### Similarity Score 怎麼解讀？

ChromaDB 回傳的是 distance（越小越相似），我們轉成 similarity = 1 - distance：

- **> 0.8**：非常相關，幾乎就是在講同一件事
- **0.5-0.8**：有關聯，可能有用
- **< 0.5**：可能不相關，但還是在 Top-K 裡

之後可以設門檻（例如 < 0.3 的不要），但第一版先全部回傳。

## Generator 做什麼？

### 核心概念：Grounding（接地）

不讓 LLM 自由發揮，而是把它「接地」到你提供的參考資料上。做法是在 prompt 裡明確告訴它：

1. **只能根據參考資料回答**
2. **沒資料就說不知道**
3. **標註引用來源**

這就是 RAG 的「R」—— Retrieval-Augmented。不是讓 LLM 靠自己的訓練知識回答，而是餵它具體的資料片段。

### Prompt Engineering

我們的 system prompt：

```
你是一個知識庫助手。根據以下提供的參考資料回答用戶的問題。

規則：
1. 只能根據參考資料的內容回答
2. 如果參考資料中沒有相關資訊，直接回答「根據現有資料，我無法回答這個問題」
3. 回答時標註引用來源（檔名）
4. 用繁體中文回答
```

幾個設計選擇：

- **Temperature 0.1** — 讓 LLM 盡量「照本宣科」，減少創意發揮（= 減少幻覺）
- **明確的拒答指令** — 不說「盡量」「如果可以」，而是「直接回答」「不能」
- **引用來源** — 讓用戶可以去查原文，增加信任感

### 幻覺（Hallucination）防治

RAG 不能完全消除幻覺，但可以大幅降低：

| 策略 | 我們有做嗎 | 效果 |
|------|-----------|------|
| 提供參考資料（RAG 本身） | 有 | 最重要的一步 |
| 低 Temperature | 有（0.1） | 減少隨機性 |
| 明確的拒答指令 | 有 | LLM 比較敢說不知道 |
| 引用來源 | 有 | 讓幻覺可被驗證 |
| Similarity 門檻 | 沒做 | 可以過濾掉不相關的 chunk |
| Faithfulness 評估 | 沒做 | 事後檢查回答是否忠於參考資料 |

### 為什麼 LLM 還是可能幻覺？

即使有 RAG，LLM 還是可能：
1. **過度推理** — 從參考資料「推論」出原文沒說的東西
2. **混淆來源** — 把 A 文件的資訊歸給 B 文件
3. **忽略指令** — 特別是小模型（8B），指令遵從度不如大模型

重點：RAG 降低幻覺但不能消除，企業級還需要加 faithfulness evaluation。

## 本次實作的數據

| 指標 | 數值 |
|------|------|
| Retrieval 速度 | < 1 秒（含 query embedding） |
| Generation 速度 | ~10-15 秒（Qwen3-VL 8B, M1 16GB） |
| Top-K | 5 |
| 知識庫內問題 | 正確回答 + 引用來源 ✓ |
| 知識庫外問題 | 正確拒答 ✓ |
