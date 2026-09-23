import logging
from contextlib import suppress
from pathlib import Path

from src.config import settings
from src.pages.home_page import open_home, search_table
from src.pages.table_page import (
    activate_uf,
    configure_idade,
    download_csv,
    selecionar_ano,
    visualizar,
)
from src.utils.evidence import save_screenshot
from src.validation.csv_validator import validate_csv

logger = logging.getLogger("sidra")


class AutomationError(Exception):
    pass


def _slug(nome: str) -> str:
    return nome.lower().replace(" ", "-")


class SidraAutomation:
    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger("sidra")
        self.checkpoints: dict[str, bool] = {}

    def run(self, page, output_path=None, evidencias_dir=None) -> dict:
        output = Path(output_path or settings.CSV_PATH)
        evidencia = Path(evidencias_dir or settings.EVIDENCIAS_DIR)

        self.logger.info("Iniciando automação SIDRA")

        passos: list[tuple[str, object]] = [
            ("Abrir página inicial", lambda: open_home(page)),
            (
                "Evidência home",
                lambda: save_screenshot(page, settings.EVIDENCIA_HOME, evidencia),
            ),
            ("Pesquisar tabela 1209", lambda: search_table(page)),
            (
                "Evidência busca",
                lambda: save_screenshot(page, settings.EVIDENCIA_BUSCA, evidencia),
            ),
            (
                "Evidência tabela",
                lambda: save_screenshot(page, settings.EVIDENCIA_TABELA, evidencia),
            ),
            ("Configurar grupo de idade", lambda: configure_idade(page)),
            ("Selecionar ano", lambda: selecionar_ano(page)),
            ("Configurar território UF", lambda: activate_uf(page)),
            (
                "Evidência filtros",
                lambda: save_screenshot(page, settings.EVIDENCIA_FILTROS, evidencia),
            ),
            ("Visualizar resultado", lambda: visualizar(page)),
            ("Baixar CSV", lambda: download_csv(page, str(output))),
            (
                "Evidência download",
                lambda: save_screenshot(page, settings.EVIDENCIA_DOWNLOAD, evidencia),
            ),
        ]

        for nome, passo in passos:
            self.logger.info("Executando etapa: %s", nome)
            try:
                passo()
                self.checkpoints[nome] = True
            except Exception as exc:
                self.checkpoints[nome] = False
                with suppress(Exception):
                    save_screenshot(
                        page,
                        settings.EVIDENCIA_ERRO.format(etapa=_slug(nome)),
                        evidencia,
                    )
                raise AutomationError(f"[ERROR] {nome}: {exc}") from exc

        self.logger.info("Validando CSV")
        try:
            resultado = validate_csv(output)
        except Exception as exc:
            raise AutomationError(f"[ERROR] Validação do CSV: {exc}") from exc

        save_screenshot(page, settings.EVIDENCIA_VALIDACAO, evidencia)
        self.logger.info("Validação concluída com sucesso")
        return self._montar_resumo(resultado, output)

    @staticmethod
    def _montar_resumo(resultado: dict, output: Path) -> dict:
        return {
            "status": "APROVADO",
            "tabela": settings.TABELA_TITULO,
            "ano": resultado["ano"],
            "idade": " + ".join(settings.IDADE_ALVO) + " (60 anos ou mais)",
            "territorio": (
                f"Unidades da Federação ({resultado['quantidade_registros']})"
            ),
            "csv": str(output),
            "quantidade_registros": resultado["quantidade_registros"],
            "total_60_mais": resultado["total_60_mais"],
        }
