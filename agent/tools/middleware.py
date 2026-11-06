"""Middleware helpers for tool and model execution."""

from __future__ import annotations

from functools import wraps
from typing import Any, Callable, TypeVar

from utils.logger_handler import logger
from utils.prompt_loader import PromptLoader

from .agent_tools import REPORT_CONTEXT_KEY, REPORT_CONTEXT_VALUE


F = TypeVar("F", bound=Callable[..., Any])


def monitor_tool(tool: F) -> F:
    """Log a tool name, arguments, result, and errors before and after execution."""
    @wraps(tool)
    def monitored_tool(*args: Any, **kwargs: Any) -> Any:
        tool_name = getattr(tool, "__name__", repr(tool))
        logger.info("Tool start: %s args=%r kwargs=%r", tool_name, args, kwargs)
        try:
            result = tool(*args, **kwargs)
        except Exception:
            logger.exception("Tool failed: %s", tool_name)
            raise
        logger.info("Tool finished: %s result=%r", tool_name, result)
        return result

    return monitored_tool  # type: ignore[return-value]


def log_before_model(messages: Any) -> Any:
    """Log the messages immediately before the model is called."""
    logger.info("Model request: messages=%r", messages)
    return messages


def report_prompt_switch(prompt: str) -> str:
    """Use the report prompt when the shared context marker is exactly ``report``."""
    if REPORT_CONTEXT_VALUE.get() == REPORT_CONTEXT_KEY:
        logger.info("Report context detected; switching to report prompt")
        return PromptLoader().load_report()
    return prompt
