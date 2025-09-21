from __future__ import annotations

import logging
import os
from logging.config import dictConfig
from typing import Any, Mapping

import yaml


def _ensure_log_dirs(logging_config: Mapping[str, Any]) -> None:
    handlers = logging_config.get("handlers", {})
    for h in handlers.values():
        if "filename" in h:
            log_path = h["filename"]
            log_dir = os.path.dirname(log_path)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir, exist_ok=True)


def _read(filename: str, loader: Any) -> dict[str, Any]:
    """Read any yaml file as a Box object"""

    if os.path.isfile(filename) and os.access(filename, os.R_OK):
        with open(filename, "r") as f:
            try:
                config_dict = yaml.load(f, Loader=loader)
                _ensure_log_dirs(config_dict)
            except yaml.YAMLError as exc:
                print(exc)
        return config_dict
    else:
        raise FileNotFoundError(filename)


def init_logging(config_path: str) -> None:
    try:
        dictConfig(_read(config_path, loader=yaml.FullLoader))
    except FileNotFoundError:
        logger = logging.getLogger(__name__)
        logger.error(f"Configuration file: {config_path} not found")
        raise
