"""Factories for the chat and embedding models used by the application."""

from __future__ import annotations

import os
from typing import Any

from utils.config_handler import load_yaml
from utils.path_tool import project_path


def _get_model_name(config_key: str) -> str:
    """Read and validate a model name from config/rag.yml."""
    config = load_yaml(project_path("config", "rag.yml"))
    model_name = config.get(config_key)
    if not isinstance(model_name, str) or not model_name.strip():
        raise ValueError(
            f"Missing or invalid '{config_key}' in config/rag.yml"
        )
    return model_name.strip()


def get_chat_model(**kwargs: Any) -> Any:
    """Create the configured chat model through DashScope's OpenAI API.

    ``qwen3.7-plus`` is accessed through DashScope's OpenAI-compatible
    endpoint. ``DASHSCOPE_BASE_URL`` can be set to a workspace-specific
    endpoint when required by the account or region.
    """
    try:
        from langchain_openai import ChatOpenAI
    except ImportError as exc:
        raise ImportError(
            "langchain-openai is required to create the chat model"
        ) from exc

    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        raise RuntimeError(
            "DASHSCOPE_API_KEY is not configured; "
            "set a valid DashScope API key before starting the app"
        )

    kwargs.setdefault("model", _get_model_name("chat_model_name"))
    kwargs.setdefault(
        "base_url",
        os.getenv(
            "DASHSCOPE_BASE_URL",
            "https://dashscope.aliyuncs.com/compatible-mode/v1",
        ),
    )
    kwargs.setdefault("api_key", api_key)
    return ChatOpenAI(**kwargs)


def get_embedding_model(**kwargs: Any) -> Any:
    """Create the configured DashScope embedding model."""
    try:
        from langchain_community.embeddings import DashScopeEmbeddings
    except ImportError as exc:
        raise ImportError(
            "langchain-community is required to create the embedding model"
        ) from exc

    kwargs.setdefault("model", _get_model_name("embedding_model_name"))
    return DashScopeEmbeddings(**kwargs)
