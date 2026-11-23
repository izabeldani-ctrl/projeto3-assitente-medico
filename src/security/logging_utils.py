"""Logging estruturado do assistente (console + arquivo)."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

_FORMAT = "%(asctime)s | %(levelname)-7s | %(name)s | %(message)s"
_FORMATTER = logging.Formatter(_FORMAT, datefmt="%Y-%m-%d %H:%M:%S")

_LOGGERS: dict[str, logging.Logger] = {}


def get_logger(name: str = "hospitaltech", log_file: Path | None = None,
               level: int = logging.INFO) -> logging.Logger:
    """Retorna (e cacheia) um logger com formato estruturado."""
    if name in _LOGGERS:
        return _LOGGERS[name]

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False

    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(_FORMATTER)
    logger.addHandler(console)

    if log_file is not None:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        fh = logging.FileHandler(log_file, encoding="utf-8")
        fh.setFormatter(_FORMATTER)
        logger.addHandler(fh)

    _LOGGERS[name] = logger
    return logger
