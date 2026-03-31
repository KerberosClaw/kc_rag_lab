# 任務清單

> **English summary:** Task checklist for retriever + generator implementation.

**Spec:** 03-retriever-generator
**Status:** VERIFIED

## Checklist

- [x] Task 1: retriever.py — query embedding + ChromaDB cosine similarity 搜尋，回傳 Top-K chunk + score + metadata
- [x] Task 2: generator.py — prompt template 組裝 + /v1/chat/completions API 呼叫，含引用來源
- [x] Task 3: tests — retriever + generator unit test + 真實問答驗證（有答案 / 沒答案）
- [x] Task 4: notes.md — 學習筆記：retrieval 原理、prompt engineering、幻覺防治

## 備註

- 需要 oMLX 跑著（bge-m3-mlx-fp16 + Qwen3-VL-8B-Instruct-MLX-4bit）
- ChromaDB 裡要有 spec-02 存入的資料
- Qwen3-VL 8B 在 M1 16GB 上生成會慢，測試要設較長 timeout
