"""ReAct-style agent that coordinates prompts, tools, middleware, and output."""

from __future__ import annotations

import json
from typing import Any, Iterator, Mapping

from model.factory import get_chat_model
from utils.prompt_loader import PromptLoader

from agent.tools import agent_tools
from agent.tools.middleware import (
    log_before_model,
    monitor_tool,
    report_prompt_switch,
)
from agent.tools.agent_tools import REPORT_CONTEXT_VALUE


class ReactAgent:
    """Run a tool-capable chat model and stream the final answer character by character."""

    _REPORT_WORDS = ("报告", "使用记录", "本月数据", "月度")

    def __init__(
        self,
        model: Any | None = None,
        max_iterations: int = 5,
    ) -> None:
        if max_iterations < 1:
            raise ValueError("max_iterations must be positive")
        self.model = model or get_chat_model()
        self.max_iterations = max_iterations
        self.prompt_loader = PromptLoader()
        self.tools = {
            name: monitor_tool(getattr(agent_tools, name))
            for name in (
                "rag_summarize",
                "get_weather",
                "get_user_location",
                "get_user_id",
                "get_current_month",
                "fetch_external_data",
                "fill_context_for_report",
            )
        }

    def execute_stream(self, query: str) -> Iterator[str]:
        """Accept a question, reason through tools, and yield answer text one character at a time."""
        result = self.execute_with_sources(query)
        yield from result["answer"]

    def execute_with_sources(self, query: str) -> dict[str, Any]:
        """Execute a question and return the final answer together with RAG sources."""
        if not isinstance(query, str) or not query.strip():
            raise ValueError("query must be a non-empty string")

        REPORT_CONTEXT_VALUE.set(None)
        report_requested = any(word in query for word in self._REPORT_WORDS)
        messages: list[dict[str, Any]] = [
            {"role": "system", "content": self.prompt_loader.load_main()},
            {"role": "user", "content": query},
        ]
        report_tools_called: list[str] = []
        sources: list[dict[str, Any]] = []

        for _ in range(self.max_iterations):
            prompt = report_prompt_switch(messages[0]["content"])
            messages[0] = {"role": "system", "content": prompt}
            model = self.model.bind_tools(list(self.tools.values()))
            log_before_model(messages)
            response = model.invoke(messages)
            tool_calls = self._tool_calls(response)

            if not tool_calls:
                content = self._content(response)
                if report_requested and "fetch_external_data" not in report_tools_called:
                    raise RuntimeError(
                        "Report generation must call the required tools in order"
                    )
                return {"answer": content, "sources": sources}

            messages.append(
                {
                    "role": "assistant",
                    "content": self._content(response),
                    "tool_calls": tool_calls,
                }
            )
            for call in tool_calls:
                name = call.get("name")
                if name not in self.tools:
                    raise ValueError(f"Unknown tool requested by model: {name}")
                self._validate_report_order(
                    report_requested, name, report_tools_called
                )
                arguments = call.get("args", {})
                if isinstance(arguments, str):
                    arguments = json.loads(arguments)
                if not isinstance(arguments, Mapping):
                    raise TypeError(f"Tool arguments must be a mapping: {name}")
                result = self.tools[name](**dict(arguments))
                if name == "rag_summarize" and isinstance(result, Mapping):
                    tool_sources = result.get("sources", [])
                    if isinstance(tool_sources, list):
                        sources.extend(
                            item for item in tool_sources if isinstance(item, Mapping)
                        )
                report_tools_called.append(name)
                messages.append(
                    {
                        "role": "tool",
                        "name": name,
                        "tool_call_id": call.get("id", name),
                        "content": self._serialize(result),
                    }
                )

        raise RuntimeError("The agent exceeded its tool-call iteration limit")

    def _validate_report_order(
        self,
        report_requested: bool,
        tool_name: str,
        called: list[str],
    ) -> None:
        if not report_requested:
            return
        if "fetch_external_data" in called:
            raise RuntimeError("fetch_external_data must be the final report tool")
        if not called and tool_name != "fill_context_for_report":
            raise RuntimeError("fill_context_for_report must be called first")
        if tool_name == "fetch_external_data" and not {
            "get_user_id",
            "get_current_month",
        }.issubset(called):
            raise RuntimeError(
                "get_user_id and get_current_month must be called before fetch_external_data"
            )
        if tool_name in {"get_user_id", "get_current_month"} and (
            "fill_context_for_report" not in called
        ):
            raise RuntimeError("fill_context_for_report must be called first")

    @staticmethod
    def _tool_calls(response: Any) -> list[dict[str, Any]]:
        calls = getattr(response, "tool_calls", None)
        if calls is None and isinstance(response, Mapping):
            calls = response.get("tool_calls")
        return list(calls or [])

    @staticmethod
    def _content(response: Any) -> str:
        content = getattr(response, "content", response)
        if isinstance(response, Mapping):
            content = response.get("content", content)
        if content is None:
            return ""
        if not isinstance(content, str):
            raise TypeError("Model content must be text")
        return content

    @staticmethod
    def _serialize(value: Any) -> str:
        try:
            return json.dumps(value, ensure_ascii=False)
        except TypeError:
            return str(value)
