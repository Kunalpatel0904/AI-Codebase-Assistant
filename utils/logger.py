"""
Structured logging for the AI Codebase Assistant.

Replaces all print() statements with proper logging.
Writes to both console (INFO) and a rotating log file (DEBUG).
"""

import logging
from logging.handlers import RotatingFileHandler

import config


def setup_logging() -> None:
    """Configure the root logger with console and file handlers.

    Call this once at application startup (in app.py) before any other
    module-level work.
    """
    config.LOG_DIR.mkdir(parents=True, exist_ok=True)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    # Avoid adding duplicate handlers on Streamlit reruns
    if root_logger.handlers:
        return

    formatter = logging.Formatter(
        fmt=config.LOG_FORMAT,
        datefmt=config.LOG_DATE_FORMAT,
    )

    # --- Console handler (INFO and above) ---
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # --- Rotating file handler (DEBUG and above) ---
    file_handler = RotatingFileHandler(
        filename=config.LOG_DIR / "app.log",
        maxBytes=config.LOG_MAX_BYTES,
        backupCount=config.LOG_BACKUP_COUNT,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)


def get_logger(name: str) -> logging.Logger:
    """Return a named child logger.

    Args:
        name: Typically ``__name__`` of the calling module.

    Returns:
        A configured :class:`logging.Logger` instance.
    """
    return logging.getLogger(name)
