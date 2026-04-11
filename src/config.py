"""RAG pipeline 設定與資料結構。"""

import os
from dataclasses import dataclass, field

from dotenv import load_dotenv

# 從 .env 讀設定（不存在也沒關係，會 fallback 到系統環境變數）
load_dotenv()


# --- Chunk 參數 ---

MAX_CHUNK_SIZE = 500      # 單一 chunk 最大字數（中文字）
OVERLAP_SIZE = 50         # 二次切割時的重疊字數
HEADING_PATTERN = r"^(#{1,3})\s+"  # 切割用的 heading 層級（h1-h3）

# --- LLM Server 設定 ---
# 支援任何 OpenAI 相容 API（oMLX、Ollama、OpenAI 等）
# 設定方式見 .env.example

LLM_BASE_URL = os.environ.get("RAG_LLM_URL", "http://127.0.0.1:8000/v1")
LLM_API_KEY = os.environ.get("RAG_LLM_KEY", "")
EMBEDDING_MODEL = os.environ.get("RAG_EMBED_MODEL", "bge-m3-mlx-fp16")
LLM_MODEL = os.environ.get("RAG_LLM_MODEL", "Qwen3-VL-8B-Instruct-MLX-4bit")

# --- ChromaDB 設定（spec-02 用） ---

CHROMA_PERSIST_DIR = ".chroma"
CHROMA_COLLECTION_NAME = "rag_docs"

# --- Retriever 設定（spec-03 用） ---

TOP_K = 3
LLM_TEMPERATURE = 0.1


# --- 資料結構 ---

@dataclass
class Document:
    """Loader 的輸出：一份完整文件。"""
    content: str
    metadata: dict = field(default_factory=dict)
    # metadata keys: filename, filepath, frontmatter (optional)


@dataclass
class Chunk:
    """Chunker 的輸出：一個文件片段。"""
    text: str
    metadata: dict = field(default_factory=dict)
    # metadata keys: source_file, heading, heading_level, chunk_index
