"""Prompt file loading helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from .config_handler import load_yaml
from .path_tool import project_path


class PromptLoader:
    """Load prompts using paths declared in config/prompts.yml."""

    def __init__(
        self,
        config_path: Optional[str | Path] = None,
        encoding: str = "utf-8",
    ) -> None:
        self.encoding = encoding
        config_file = Path(config_path) if config_path else project_path("config", "prompts.yml")
        self._config = load_yaml(config_file)

    def load(self, prompt_name: str) -> str:
        """Load a prompt by config key or by its configured path."""
        key = prompt_name
        if not key.endswith("_path"):
            key = f"{key}_path"
        prompt_path = self._config.get(key, prompt_name)
        path = Path(prompt_path)
        if not path.is_absolute():
            path = project_path(path)
        if not path.is_file():
            raise FileNotFoundError(f"Prompt file does not exist: {path}")
        return path.read_text(encoding=self.encoding)

    def load_main(self) -> str:
        return self.load("main_prompt")

    def load_rag_summarize(self) -> str:
        return self.load("rag_summarize_prompt")

    def load_report(self) -> str:
        return self.load("report_prompt")


def load_prompt(prompt_name: str) -> str:
    """Load one prompt with the default project configuration."""
    return PromptLoader().load(prompt_name)
