# Web UI — 學習筆記

> **English summary:** Notes on adding a Gradio web interface to the RAG pipeline — why Gradio, how ChatInterface works, and demo tips.

## 為什麼用 Gradio？

| Framework | 優點 | 缺點 | 適合 |
|-----------|------|------|------|
| Gradio | 最快上手、ChatInterface 內建、ML 社群標準 | 客製化有限 | Demo、原型、學習 |
| Streamlit | 彈性高、元件多 | 要自己刻 chat UI | Dashboard、資料分析 |
| FastAPI + React | 完全客製 | 要寫前後端 | Production |

Gradio 的 `ChatInterface` 幾行就有完整的聊天介面，包括歷史紀錄、loading 狀態、Markdown 渲染。Demo 展示用最適合。

## 使用方式

```bash
# 1. 確認 oMLX 或 Ollama 有跑
# 2. 啟動 Web UI
python -m src.pipeline ui

# 3. 在瀏覽器操作
#    - 問知識庫內的問題（展示準確回答 + 引用來源）
#    - 問知識庫外的問題（展示拒答能力）
#    - 點 examples 按鈕展示預設問題
```

重點不是 UI 多漂亮，是展示 RAG 的核心能力：搜得準、答得對、不幻覺。
