"""Application logging.

Writes a rotating log file under ``data/logs`` and installs global hooks so
unhandled exceptions in the main thread and in worker threads are captured.
"""
from __future__ import annotations

import logging
import logging.handlers
import sys
import threading

from . import paths

_CONFIGURED = False


def setup(level: int = logging.INFO) -> logging.Logger:
    global _CONFIGURED
    logger = logging.getLogger("novu")
    if _CONFIGURED:
        return logger
    logger.setLevel(level)
    formatter = logging.Formatter(
        "%(asctime)s %(levelname)-7s [%(threadName)s] %(name)s: %(message)s"
    )
    try:
        handler: logging.Handler = logging.handlers.RotatingFileHandler(
            paths.logs_dir() / "novu.log", maxBytes=1_000_000, backupCount=3, encoding="utf-8"
        )
    except OSError:
        handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    if logger.level == logging.DEBUG:
        console = logging.StreamHandler()
        console.setFormatter(formatter)
        logger.addHandler(console)
    logger.propagate = False
    _CONFIGURED = True
    return logger


def get_logger(name: str = "novu") -> logging.Logger:
    return logging.getLogger("novu" if name == "novu" else f"novu.{name}")


def install_excepthook(logger: logging.Logger | None = None) -> None:
    logger = logger or get_logger()

    def hook(exc_type, exc, tb):  # type: ignore[no-untyped-def]
        logger.critical("Unhandled exception", exc_info=(exc_type, exc, tb))
        sys.__excepthook__(exc_type, exc, tb)

    def thread_hook(args):  # type: ignore[no-untyped-def]
        logger.critical(
            "Unhandled thread exception in %s", args.thread.name if args.thread else "?",
            exc_info=(args.exc_type, args.exc_value, args.exc_traceback),
        )

    sys.excepthook = hook
    threading.excepthook = thread_hook
