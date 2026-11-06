"""YAML configuration loading."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping, Optional

from .path_tool import project_path

try:
    import yaml
except ImportError as exc:  # pragma: no cover - exercised in environments without PyYAML
    yaml = None
    _YAML_IMPORT_ERROR = exc

CONFIG_FILES = ("agent.yml", "chroma.yml", "rag.yml", "prompts.yml")


def load_yaml(path: str | Path) -> dict[str, Any]:
    """Load one YAML mapping and raise useful errors for invalid input."""
    if yaml is None:
        raise ImportError("PyYAML is required to load YAML configuration files") from _YAML_IMPORT_ERROR
    config_path = Path(path)
    if not config_path.is_absolute():
        config_path = project_path(config_path)
    if not config_path.is_file():
        raise FileNotFoundError(f"Configuration file does not exist: {config_path}")
    with config_path.open("r", encoding="utf-8") as stream:
        data = yaml.safe_load(stream)
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise ValueError(f"Configuration root must be a mapping: {config_path}")
    return data


class ConfigHandler:
    """Load and access the four project YAML configuration files."""

    def __init__(self, config_dir: Optional[str | Path] = None) -> None:
        self.config_dir = (
            Path(config_dir) if config_dir is not None else project_path("config")
        )
        if not self.config_dir.is_absolute():
            self.config_dir = project_path(self.config_dir)
        self._configs = {
            Path(filename).stem: load_yaml(self.config_dir / filename)
            for filename in CONFIG_FILES
        }

    def get(self, section: str, key: str, default: Any = None) -> Any:
        """Read a value from a named config section."""
        return self._configs.get(section, {}).get(key, default)

    def section(self, section: str) -> dict[str, Any]:
        """Return a copy of one configuration section."""
        if section not in self._configs:
            raise KeyError(f"Unknown configuration section: {section}")
        return dict(self._configs[section])

    @property
    def all(self) -> dict[str, dict[str, Any]]:
        """Return all loaded configurations as a copy."""
        return {name: dict(values) for name, values in self._configs.items()}


def load_all_configs(config_dir: Optional[str | Path] = None) -> dict[str, dict[str, Any]]:
    """Load all four YAML files keyed by filename stem."""
    return ConfigHandler(config_dir).all
