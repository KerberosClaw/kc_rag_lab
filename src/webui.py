"""Web UI — Gradio chatbot 介面。"""

import gradio as gr

from .store import get_client, get_collection_info
from .retriever import retrieve
from .generator import generate


def _check_db() -> str | None:
    """檢查 ChromaDB 是否有資料，回傳錯誤訊息或 None。"""
    client = get_client()
    info = get_collection_info(client)
    if not info["exists"] or info["count"] == 0:
        return "ChromaDB 沒有資料，請先在終端機跑：\n```\npython -m src.pipeline ingest <目錄>\n```"
    return None


def _format_sources(results) -> str:
    """把引用來源格式化成 Markdown 表格。"""
    if not results:
        return ""
    lines = ["\n\n---\n**引用來源：**\n"]
    lines.append("| # | 檔案 | 段落 | 相似度 |")
    lines.append("|---|------|------|--------|")
    for i, r in enumerate(results, 1):
        source = r.metadata.get("source_file", "?")
        heading = r.metadata.get("heading", "") or "(無標題)"
        score = f"{r.score:.3f}"
        lines.append(f"| {i} | {source} | {heading} | {score} |")
    return "\n".join(lines)


def chat_fn(message: str, history: list) -> str:
    """處理用戶訊息，回傳回答 + 引用來源。"""
    # 檢查 DB
    err = _check_db()
    if err:
        return err

    if not message.strip():
        return "請輸入問題。"

    try:
        results = retrieve(message)
        answer = generate(message, results)
        sources = _format_sources(results)
        return answer + sources
    except ConnectionError as e:
        return f"**連線失敗：**\n\n{e}\n\n請確認 oMLX 或 Ollama 正在運行。"
    except RuntimeError as e:
        return f"**錯誤：**\n\n{e}"


def create_app() -> gr.Blocks:
    """建立 Gradio app。"""
    client = get_client()
    info = get_collection_info(client)
    db_status = f"知識庫：{info['count']} 筆資料" if info["exists"] else "知識庫：無資料"

    with gr.Blocks(title="kc_rag_lab") as app:
        gr.Markdown(f"# 📚 kc_rag_lab — RAG 知識庫問答\n\n{db_status}")

        gr.ChatInterface(
            fn=chat_fn,
            examples=[
                "什麼是 RAG？",
                "RAG 和 Fine-tuning 有什麼差別？",
                "向量資料庫有哪些選擇？",
            ],
        )

    return app


def launch(**kwargs):
    """啟動 Web UI。"""
    app = create_app()
    app.launch(
        server_name="127.0.0.1",
        server_port=7860,
        theme=gr.themes.Soft(),
        **kwargs,
    )
