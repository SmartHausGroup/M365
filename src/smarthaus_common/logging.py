import logging
import os


def configure_logging(level: str | None = None) -> None:
    level_name_raw: str = level if level is not None else os.getenv("LOG_LEVEL", "INFO")
    level_name = level_name_raw.upper()
    logging.basicConfig(
        level=getattr(logging, level_name, logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
