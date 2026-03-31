"""Stage 6: Generator — 用 LLM 根據檢索結果生成回答。"""

import logging

import httpx

from .config import LLM_BASE_URL, LLM_API_KEY, LLM_MODEL, LLM_TEMPERATURE
from .retriever import RetrievalResult

logger = logging.getLogger(__name__)

TIMEOUT = 120  # LLM 生成比 embedding 慢，給更多時間

SYSTEM_PROMPT = "你是知識庫助手。根據參考資料回答問題。用繁體中文回答。"


def generate(
    query: str,
    results: list[RetrievalResult],
) -> str:
    """根據檢索結果生成回答。

    Args:
        query: 用戶問題
        results: Retriever 回傳的搜尋結果

    Returns:
        LLM 生成的回答文字
    """
    if not results:
        return "根據現有資料，我無法回答這個問題（沒有找到相關片段）。"

    # 組裝參考資料
    context = _format_context(results)

    user_message = f"""參考資料：
{context}

用戶問題：{query}"""

    # 呼叫 LLM
    answer = _call_chat_api(user_message)

    logger.info("生成回答完成（%d 字）", len(answer))
    return answer


def _format_context(results: list[RetrievalResult]) -> str:
    """把搜尋結果格式化成 prompt 中的參考資料。"""
    parts = []
    for i, r in enumerate(results, 1):
        source = r.metadata.get("source_file", "unknown")
        heading = r.metadata.get("heading", "")
        header = f"[{i}] 來源：{source}"
        if heading:
            header += f" / {heading}"
        # Strip markdown tables — some local LLMs (e.g. Qwen3 4bit on oMLX)
        # return null content when pipe characters are in the prompt
        text = _strip_markdown_tables(r.text)
        parts.append(f"{header}\n{text}")
    return "\n\n---\n\n".join(parts)


def _strip_markdown_tables(text: str) -> str:
    """Convert markdown tables to plain text to avoid LLM parsing issues."""
    import re
    lines = text.split("\n")
    result = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("|") and stripped.endswith("|"):
            # Table row: "| A | B | C |" → "A, B, C"
            cells = [c.strip() for c in stripped.strip("|").split("|") if c.strip() and not re.match(r'^[-:]+$', c.strip())]
            if cells:
                result.append(", ".join(cells))
        else:
            result.append(line)
    return "\n".join(result)


def _call_chat_api(user_message: str) -> str:
    """呼叫 /v1/chat/completions API。"""
    url = f"{LLM_BASE_URL}/chat/completions"
    headers = {"Content-Type": "application/json"}
    if LLM_API_KEY:
        headers["Authorization"] = f"Bearer {LLM_API_KEY}"

    payload = {
        "model": LLM_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        "temperature": LLM_TEMPERATURE,
    }

    try:
        resp = httpx.post(url, json=payload, headers=headers, timeout=TIMEOUT)
        resp.raise_for_status()
    except httpx.ConnectError:
        raise ConnectionError(
            f"無法連線到 LLM server: {LLM_BASE_URL}\n"
            f"請確認 oMLX 或 Ollama 正在運行，且 model '{LLM_MODEL}' 已載入。"
        )
    except httpx.HTTPStatusError as e:
        raise RuntimeError(
            f"Chat API 錯誤 ({e.response.status_code}): {e.response.text}\n"
            f"URL: {url}, Model: {LLM_MODEL}"
        )

    data = resp.json()
    msg = data["choices"][0]["message"]

    content = msg.get("content") or ""

    # Handle Qwen3 thinking mode: strip <think>...</think> tags
    if "<think>" in content:
        parts = content.split("</think>")
        content = parts[-1].strip() if len(parts) > 1 else content

    # Fallback: check reasoning_content
    if not content:
        content = msg.get("reasoning_content") or ""

    return content or "（模型未回傳內容）"
