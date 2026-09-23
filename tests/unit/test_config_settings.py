
from pathlib import Path

from src.config import settings


def test_constantes_centrais():
    assert settings.TABELA_ID == "1209"
    assert settings.ANO_PREFERIDO == "2022"
    assert settings.FORMATO_CSV == "br.csv"
    assert settings.NOME_ARQUIVO_FINAL == "populacao_60mais_1209"
    assert settings.HEADLESS is False
    assert settings.SIDRA_HOME_URL == "https://sidra.ibge.gov.br/"
    assert settings.TABELA_URL_PREFIX.endswith("/Tabela/1209")
    assert settings.TABELA_TITULO.startswith("Tabela 1209")


def test_recorte_de_idade_60_mais():
    assert settings.IDADE_ALVO == ("60 a 69 anos", "70 anos ou mais")


def test_ufs_com_27_unidades():
    assert len(settings.UFS) == 27
    assert len(set(settings.UFS)) == 27
    assert settings.UFS[0] == "Rondônia"
    assert settings.UFS[-1] == "Distrito Federal"


def test_caminhos_de_artefatos():
    assert isinstance(settings.PROJECT_ROOT, Path)
    assert settings.CSV_PATH == settings.DATA_DIR / "populacao_60mais_1209.csv"
    assert settings.LOG_PATH == settings.LOGS_DIR / "sidra.log"
    assert settings.EVIDENCIAS_DIR.name == "evidencias"


def test_evidencias_nomeadas_de_forma_ordenada():
    assert settings.EVIDENCIA_HOME < settings.EVIDENCIA_BUSCA
    assert settings.EVIDENCIA_BUSCA < settings.EVIDENCIA_TABELA
    assert settings.EVIDENCIA_ERRO.startswith("erro-{etapa}")
