"""Application logging helpers."""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional

from .path_tool import project_path

DEFAULT_LOG_FILE = project_path("logs", "app.log")
_CONFIGURED_LOGGERS: set[str] = set()


def get_logger(
    name: Optional[str] = None,
    log_file: Optional[str | Path] = None,
    level: int = logging.INFO,
) -> logging.Logger:
    """Return a console-and-file logger configured once per name."""
    logger_name = name or "robot_cs_agent"
    logger = logging.getLogger(logger_name)
    logger.setLevel(level)
    logger.propagate = False

    if logger_name in _CONFIGURED_LOGGERS:
        return logger

    target = Path(log_file) if log_file else DEFAULT_LOG_FILE
    if not target.is_absolute():
        target = project_path(target)
    target.parent.mkdir(parents=True, exist_ok=True)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(filename)s:%(lineno)d | %(message)s"
    )
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    file_handler = RotatingFileHandler(
        target, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    _CONFIGURED_LOGGERS.add(logger_name)
    return logger


logger = get_logger()
