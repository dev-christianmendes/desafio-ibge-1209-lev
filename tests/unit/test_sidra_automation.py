
import pytest

from src.services.sidra_automation import AutomationError, SidraAutomation, _slug
from tests.unit.fake_playwright import FakeDownload, build_happy_page


def test_slug_normaliza_nomes():
    assert _slug("Abrir página inicial") == "abrir-página-inicial"
    assert _slug("Configurar território UF") == "configurar-território-uf"


def test_sidra_automation_run_sucesso(tmp_path):
    page = build_happy_page()
    automacao = SidraAutomation()
    saida = tmp_path / "dados" / "saida.csv"
    evidencias = tmp_path / "evidencias"
    resumo = automacao.run(page, output_path=str(saida), evidencias_dir=str(evidencias))
    assert resumo["status"] == "APROVADO"
    assert saida.exists()
    assert evidencias.is_dir()
    assert resumo["quantidade_registros"] == 27


def test_sidra_automation_registra_checkpoints(tmp_path):
    page = build_happy_page()
    automacao = SidraAutomation()
    automacao.run(page, output_path=str(tmp_path / "csv.csv"))
    assert automacao.checkpoints
    assert all(automacao.checkpoints.values())


def test_sidra_automation_falha_na_etapa_gera_evidencia_de_erro(tmp_path):
    from tests.unit.fake_playwright import age_janela

    page = build_happy_page()
    page.add(
        '.janela-dados:has-text("60 a 69 anos")',
        age_janela(alvo_click_disabled=True),
    )
    automacao = SidraAutomation()
    with pytest.raises(AutomationError, match="Configurar grupo de idade"):
        automacao.run(
            page,
            output_path=str(tmp_path / "csv.csv"),
            evidencias_dir=str(tmp_path / "evidencias"),
        )
    assert page.screenshots[-1].endswith("erro-configurar-grupo-de-idade.png")


def test_sidra_automation_screenshot_que_falha_nao_mascara_erro(tmp_path):
    page = build_happy_page()
    page.screenshot_raises = True
    automacao = SidraAutomation()
    with pytest.raises(AutomationError, match="Evidência home"):
        automacao.run(page, output_path=str(tmp_path / "csv.csv"))


def test_sidra_automation_falha_validacao_csv(tmp_path):
    page = build_happy_page()
    page.download = FakeDownload("x.csv", content="Tabela 1209\n\n")
    automacao = SidraAutomation()
    with pytest.raises(AutomationError, match="Validação do CSV"):
        automacao.run(page, output_path=str(tmp_path / "csv.csv"))


def test_sidra_automation_usa_loggers_padrao_e_custom():
    automacao = SidraAutomation()
    assert automacao.logger.name == "sidra"
    import logging

    custom = logging.getLogger("custom")
    automacao2 = SidraAutomation(logger=custom)
    assert automacao2.logger is custom
