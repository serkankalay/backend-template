from __future__ import annotations

import inspect
import logging
from functools import wraps
from typing import Any, Callable

import click


class ColorHandler(logging.StreamHandler):
    """A color log handler.

    The ``colors`` parameter is optional, and you can use any ANSI color.

      * Black
      * Red
      * Green
      * Yellow
      * Blue
      * Magenta
      * Cyan
      * White

    The default colors are:

      * debug: magenta
      * info: cyan
      * warning: yellow
      * error: red
      * critical: red
    """

    def __init__(self, stream=None, colors=None):
        logging.StreamHandler.__init__(self, stream)
        colors = colors or {}
        self.colors = {
            "critical": colors.get("critical", "red"),
            "error": colors.get("error", "red"),
            "warning": colors.get("warning", "yellow"),
            "info": colors.get("info", "cyan"),
            "debug": colors.get("debug", "magenta"),
        }

    def _get_color(self, level):
        if level >= logging.CRITICAL:
            return self.colors["critical"]  # pragma: no cover
        if level >= logging.ERROR:
            return self.colors["error"]  # pragma: no cover
        if level >= logging.WARNING:
            return self.colors["warning"]  # pragma: no cover
        if level >= logging.INFO:
            return self.colors["info"]
        if level >= logging.DEBUG:  # pragma: no cover
            return self.colors["debug"]  # pragma: no cover

        return None  # pragma: no cover

    def format(self, record: logging.LogRecord) -> str:
        """The handler formatter.

        Args:
            record: The record to format.

        Returns:
            The record formatted as a string.

        """
        text = logging.StreamHandler.format(self, record)
        color = self._get_color(record.levelno)
        return click.style(text, color)


def logged(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        logger = logging.getLogger(__name__)
        if module := inspect.getmodule(inspect.unwrap(func)):
            logger = logging.getLogger(module.__name__)

        logger.info(f"Started {func.__name__}.")
        result = func(*args, **kwargs)
        logger.info(f"Finished {func.__name__}.")

        return result

    return wrapper
