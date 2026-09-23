import logging

import pytest


@pytest.fixture(autouse=True)
def _limpar_logger_sidra():
    yield
    logger = logging.getLogger("sidra")
    logger.handlers.clear()
    logger.setLevel(logging.WARNING)
    logger.propagate = True
