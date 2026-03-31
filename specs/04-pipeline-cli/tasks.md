# 任務清單

> **English summary:** Task checklist for pipeline CLI implementation.

**Spec:** 04-pipeline-cli
**Status:** VERIFIED

## Checklist

- [x] Task 1: pipeline.py — argparse 三指令（ingest/ask/chat）+ rich 輸出 + 錯誤處理
- [x] Task 2: 手動測試 — ingest、ask、chat 各跑一次確認
- [x] Task 3: notes.md — 整體 RAG pipeline 學習筆記

## 備註

- 不寫 unit test — CLI 入口點用手動測試就好，核心邏輯都在 spec-01~03 測過了
- ingest 會花 2-3 分鐘（embedding），用 rich progress bar 顯示進度
