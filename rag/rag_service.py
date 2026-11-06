"""RAG retrieval and answer summarization service."""

from __future__ import annotations

from typing import Any

from model.factory import get_chat_model
from rag.vector_store import search
from utils.prompt_loader import PromptLoader


def _message_content(response: Any) -> str:
    """Extract text from a LangChain response."""
    content = getattr(response, "content", response)
    if not isinstance(content, str):
        raise TypeError("Chat model response content must be a string")
    return content


def summarize(query: str) -> dict[str, Any]:
    """Retrieve relevant documents and summarize them with traceable sources."""
    documents = search(query)
    context = "\n\n".join(document.page_content for document in documents)
    prompt = PromptLoader().load_rag_summarize().format(query=query, context=context)
    sources: list[dict[str, Any]] = []
    seen_sources: set[tuple[str, int | None]] = set()
    for document in documents:
        metadata = document.metadata or {}
        source = str(metadata.get("source", "未知文件"))
        chunk = metadata.get("chunk")
        key = (source, chunk if isinstance(chunk, int) else None)
        if key in seen_sources:
            continue
        seen_sources.add(key)
        sources.append(
            {
                "source": source,
                "chunk": chunk,
                "content": document.page_content,
            }
        )
    return {
        "answer": _message_content(get_chat_model().invoke(prompt)),
        "sources": sources,
    }
