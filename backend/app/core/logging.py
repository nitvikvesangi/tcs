"""
Structured application logging configuration.

Provides a single `setup_logging()` entrypoint (called from main.py) and
a `get_logger(name)` helper used across services so log lines are
consistently formatted and tagged with the module name.

Important events logged by later phases (per project spec, section 19):
authentication, inventory updates, promotion generation, simulation,
approval, chatbot tool calls, errors.
"""

import logging
import sys

from app.core.config import settings

LOG_FORMAT = (
    "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
)


def setup_logging() -> None:
    root_logger = logging.getLogger()
    root_logger.setLevel(settings.LOG_LEVEL)

    # Avoid duplicate handlers on reload
    if root_logger.handlers:
        return

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt="%Y-%m-%d %H:%M:%S"))
    root_logger.addHandler(handler)

    # Quiet down noisy third-party loggers by default
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.INFO if settings.DEBUG else logging.WARNING
    )


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
