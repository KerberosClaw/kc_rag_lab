"""RAG Pipeline CLI — ingest / ask / chat。

Usage:
    python -m src.pipeline ingest ./sample_docs/
    python -m src.pipeline ask "OpenClaw 的 Telegram bot 怎麼設定？"
    python -m src.pipeline chat
"""

import argparse
import logging
import sys
import time

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown

from .loader import load_documents
from .chunker import chunk_documents
from .embedder import embed_chunks
from .store import get_client, rebuild_collection, get_collection_info
from .retriever import retrieve
from .generator import generate

console = Console()
logger = logging.getLogger(__name__)


def cmd_ingest(args):
    """執行完整的 load → chunk → embed → store 流程。"""
    directory = args.directory
    console.print(f"\n[bold]開始匯入文件：[/bold] {directory}\n")

    start = time.time()

    # Stage 1: Load
    with console.status("[bold green]載入文件..."):
        docs = load_documents(directory)
    if not docs:
        console.print("[red]沒有找到任何 .md 檔案。[/red]")
        return
    console.print(f"  載入 [cyan]{len(docs)}[/cyan] 個文件")

    # Stage 2: Chunk
    with console.status("[bold green]切塊中..."):
        chunks = chunk_documents(docs)
    console.print(f"  產生 [cyan]{len(chunks)}[/cyan] 個 chunk")

    # Stage 3: Embed
    console.print("  Embedding 中（這會花一點時間）...")
    embeddings = embed_chunks(chunks)
    console.print(f"  Embedding 完成，維度 [cyan]{len(embeddings[0])}[/cyan]")

    # Stage 4: Store
    with console.status("[bold green]存入 ChromaDB..."):
        client = get_client()
        rebuild_collection(client, chunks, embeddings)
        info = get_collection_info(client)

    elapsed = time.time() - start

    # 統計
    table = Table(title="匯入完成")
    table.add_column("項目", style="bold")
    table.add_column("數值", style="cyan")
    table.add_row("文件數", str(len(docs)))
    table.add_row("Chunk 數", str(len(chunks)))
    table.add_row("向量維度", str(len(embeddings[0])))
    table.add_row("ChromaDB 筆數", str(info["count"]))
    table.add_row("總耗時", f"{elapsed:.1f} 秒")
    console.print()
    console.print(table)


def cmd_ask(args):
    """單次問答。"""
    query = args.question

    # 檢查 ChromaDB 有沒有資料
    client = get_client()
    info = get_collection_info(client)
    if not info["exists"] or info["count"] == 0:
        console.print("[red]ChromaDB 沒有資料，請先跑 ingest：[/red]")
        console.print("  python -m src.pipeline ingest <目錄>")
        return

    console.print(f"\n[bold]問題：[/bold] {query}\n")

    # Retrieve
    with console.status("[bold green]搜尋中..."):
        results = retrieve(query, client=client)

    # Generate
    with console.status("[bold green]思考中..."):
        answer = generate(query, results)

    # 印回答
    console.print(Panel(Markdown(answer), title="回答", border_style="green"))

    # 印引用來源
    if results:
        console.print()
        table = Table(title="引用來源")
        table.add_column("#", style="dim")
        table.add_column("檔案", style="cyan")
        table.add_column("段落", style="dim")
        table.add_column("相似度", style="green")
        for i, r in enumerate(results, 1):
            table.add_row(
                str(i),
                r.metadata.get("source_file", "?"),
                r.metadata.get("heading", "") or "(無標題)",
                f"{r.score:.3f}",
            )
        console.print(table)


def cmd_chat(args):
    """互動問答模式。"""
    # 檢查 ChromaDB
    client = get_client()
    info = get_collection_info(client)
    if not info["exists"] or info["count"] == 0:
        console.print("[red]ChromaDB 沒有資料，請先跑 ingest。[/red]")
        return

    console.print(Panel(
        f"[bold]RAG 互動模式[/bold]\n"
        f"知識庫：{info['count']} 筆資料\n"
        f"輸入問題開始問答，輸入 [cyan]quit[/cyan] 或 [cyan]exit[/cyan] 退出",
        border_style="blue",
    ))

    while True:
        try:
            query = console.input("\n[bold cyan]你的問題 >[/bold cyan] ").strip()
        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]再見！[/dim]")
            break

        if not query:
            continue
        if query.lower() in ("quit", "exit"):
            console.print("[dim]再見！[/dim]")
            break

        # Retrieve
        with console.status("[bold green]搜尋中..."):
            results = retrieve(query, client=client)

        # Generate
        with console.status("[bold green]思考中..."):
            answer = generate(query, results)

        console.print()
        console.print(Panel(Markdown(answer), title="回答", border_style="green"))

        # 引用來源（簡潔版）
        if results:
            sources = [f"[{i}] {r.metadata.get('source_file', '?')} ({r.score:.2f})"
                       for i, r in enumerate(results, 1)]
            console.print(f"[dim]來源：{' | '.join(sources)}[/dim]")


def main():
    parser = argparse.ArgumentParser(
        description="kc_rag_lab — 全本地 RAG Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", help="可用指令")

    # ingest
    p_ingest = subparsers.add_parser("ingest", help="匯入文件到知識庫")
    p_ingest.add_argument("directory", help="Markdown 文件的資料夾路徑")

    # ask
    p_ask = subparsers.add_parser("ask", help="問一個問題")
    p_ask.add_argument("question", help="你的問題")

    # chat
    subparsers.add_parser("chat", help="進入互動問答模式")

    # ui
    subparsers.add_parser("ui", help="啟動 Web UI（瀏覽器介面）")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # 設定 logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(message)s",
    )
    # 關掉 httpx 的 log（太吵）
    logging.getLogger("httpx").setLevel(logging.WARNING)

    try:
        if args.command == "ingest":
            cmd_ingest(args)
        elif args.command == "ask":
            cmd_ask(args)
        elif args.command == "chat":
            cmd_chat(args)
        elif args.command == "ui":
            from .webui import launch
            console.print("[bold]啟動 Web UI...[/bold]")
            launch()
    except ConnectionError as e:
        console.print(f"\n[red bold]連線失敗：[/red bold]\n{e}")
        console.print("\n[dim]請確認 oMLX 或 Ollama 正在運行。[/dim]")
    except RuntimeError as e:
        console.print(f"\n[red bold]錯誤：[/red bold]\n{e}")
    except KeyboardInterrupt:
        console.print("\n[dim]已中斷。[/dim]")


if __name__ == "__main__":
    main()
