# Retriever + Generator

> **English summary:** Retrieve top-K relevant chunks from ChromaDB via cosine similarity, then generate grounded answers with source citations using LLM (Qwen3-VL via oMLX/Ollama).

## 背景

RAG pipeline 的核心：用戶問問題 → 從向量資料庫搜出最相關的 chunk → 餵給 LLM 生成回答。對應 DESIGN.md 的 Stage 5 + Stage 6。

這是整個 pipeline 「有沒有用」的關鍵 — 搜得準不準、答得對不對、會不會幻覺，都在這一步見真章。

## 驗收條件

### Retriever

- [ ] AC-1: 接收用戶問題，轉成向量，從 ChromaDB 搜出 Top-K 個最相似的 chunk
- [ ] AC-2: 回傳結果包含：chunk 文字、similarity score、來源 metadata（檔名、heading）
- [ ] AC-3: K 值可設定（預設 5）
- [ ] AC-4: ChromaDB collection 不存在或是空的時，回傳空列表 + 警告 log，不要炸掉

### Generator

- [ ] AC-5: 接收用戶問題 + 檢索到的 chunks，呼叫 LLM 生成回答
- [ ] AC-6: 回答時標註引用來源（檔名）
- [ ] AC-7: 沒有相關資料時，回答「根據現有資料，我無法回答這個問題」，不幻覺
- [ ] AC-8: Temperature 設低（0.1），減少創意發揮
- [ ] AC-9: API 連不上時，拋出明確錯誤訊息

### 整合

- [ ] AC-10: 問一個知識庫裡有的問題（如「OpenClaw 的 Telegram bot 怎麼設定？」），能拿到合理回答 + 引用來源
- [ ] AC-11: 問一個知識庫裡沒有的問題（如「量子力學是什麼？」），能得到「無法回答」的回應

## 不做的事

- 不做 reranking（直接用 cosine similarity 排序）
- 不做 similarity 門檻過濾（全部回傳 Top-K）
- 不做對話歷史（每次問答獨立，沒有 memory）
- 不做 streaming 輸出（一次回傳完整回答）

## 依賴

- oMLX 或 Ollama — 提供 `/v1/embeddings` + `/v1/chat/completions` API
- ChromaDB 已有資料（spec-02 完成）
- spec-01 + spec-02 完成
