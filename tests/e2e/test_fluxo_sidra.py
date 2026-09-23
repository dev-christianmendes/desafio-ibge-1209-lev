import pytest
from playwright.sync_api import sync_playwright

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

pytestmark = pytest.mark.e2e


@pytest.fixture(scope="session", name="pagina")
def fixture_pagina():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=settings.HEADLESS)
        context = browser.new_context(
            accept_downloads=True,
            viewport=settings.VIEWPORT,
        )
        page = context.new_page()
        try:
            open_home(page)
            yield page
        finally:
            context.close()
            browser.close()


@pytest.fixture(scope="session", name="csv_alvo")
def fixture_csv_alvo(tmp_path_factory):
    pasta = tmp_path_factory.mktemp("dados")
    return pasta / f"{settings.NOME_ARQUIVO_FINAL}.csv"


def test_e2e_01_pagina_inicial_acessada(pagina):
    save_screenshot(pagina, settings.EVIDENCIA_HOME, settings.EVIDENCIAS_DIR)
    assert pagina.url.startswith("https://sidra.ibge.gov.br/")
    titulo = pagina.title()
    assert titulo
    assert "Just a moment" not in titulo


def test_e2e_02_busca_localiza_tabela_1209(pagina):
    search_table(pagina)
    assert f"/Tabela/{settings.TABELA_ID}" in pagina.url
    save_screenshot(pagina, settings.EVIDENCIA_BUSCA, settings.EVIDENCIAS_DIR)
    save_screenshot(pagina, settings.EVIDENCIA_TABELA, settings.EVIDENCIAS_DIR)


def test_e2e_03_filtros_configurados(pagina):
    selecionadas = configure_idade(pagina)
    assert all(nome in selecionadas for nome in settings.IDADE_ALVO)

    ano = selecionar_ano(pagina)
    assert ano == settings.ANO_PREFERIDO

    activate_uf(pagina)
    save_screenshot(pagina, settings.EVIDENCIA_FILTROS, settings.EVIDENCIAS_DIR)


def test_e2e_04_visualizar_gera_resultado(pagina):
    visualizar(pagina)


def test_e2e_05_download_csv_gerado(pagina, csv_alvo):
    download_csv(pagina, str(csv_alvo))
    save_screenshot(pagina, settings.EVIDENCIA_DOWNLOAD, settings.EVIDENCIAS_DIR)
    assert csv_alvo.exists()
    assert csv_alvo.stat().st_size > 0


def test_e2e_06_csv_validado(pagina, csv_alvo):
    resultado = validate_csv(csv_alvo)
    assert resultado["ano"] == settings.ANO_PREFERIDO
    assert resultado["quantidade_registros"] == len(settings.UFS)
    assert resultado["total_60_mais"] > 0
    save_screenshot(pagina, settings.EVIDENCIA_VALIDACAO, settings.EVIDENCIAS_DIR)
