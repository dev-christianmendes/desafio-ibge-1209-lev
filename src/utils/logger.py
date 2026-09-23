import logging
from pathlib import Path

from src.config import settings


def get_logger(name: str = "sidra") -> logging.Logger:
    return logging.getLogger(name)


def setup_logging(
    level: int = logging.INFO,
    log_file=settings.LOG_PATH,
) -> logging.Logger:
    logger = get_logger()
    if logger.handlers:
        return logger

    logger.setLevel(level)
    formatter = logging.Formatter("[%(levelname)s] %(message)s")

    console = logging.StreamHandler()
    console.setFormatter(formatter)
    logger.addHandler(console)

    if log_file:
        log_file = Path(log_file)
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    logger.propagate = False
    return logger
