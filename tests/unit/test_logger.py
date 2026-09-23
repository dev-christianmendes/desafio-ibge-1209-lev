
import logging

from src.utils.logger import get_logger, setup_logging


def test_get_logger_retorna_logger_sidra():
    assert get_logger() is logging.getLogger("sidra")


def test_setup_logging_cria_console_e_arquivo(tmp_path):
    log_file = tmp_path / "logs" / "sidra.log"
    logger = setup_logging(level=logging.INFO, log_file=log_file)
    assert log_file.exists()
    assert len(logger.handlers) == 2
    assert logger.propagate is False
    logger.handlers.clear()


def test_setup_logging_sem_arquivo_adiciona_apenas_console():
    logger = setup_logging(logging.INFO, log_file=None)
    assert len(logger.handlers) == 1
    logger.handlers.clear()


def test_setup_logging_nao_duplica_handlers_existentes():
    logger = logging.getLogger("sidra")
    logger.handlers.clear()
    stub = logging.NullHandler()
    logger.addHandler(stub)
    resultado = setup_logging(log_file=None)
    assert resultado is logger
    assert logger.handlers == [stub]
