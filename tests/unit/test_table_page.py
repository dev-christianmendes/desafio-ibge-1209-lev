import pytest

from src.config import settings
from src.pages.table_page import (
    _estado_checked,
    activate_uf,
    configure_idade,
    download_csv,
    selecionar_ano,
    visualizar,
)
from tests.unit.fake_playwright import (
    FakeDownload,
    FakeLocator,
    FakeNode,
    FakePage,
    age_janela,
    arvore_niveis,
    arvore_node,
    build_happy_page,
    download_modal,
    toggle_row,
    year_janela,
)


def test_estado_checked_sem_classe_retorna_falso():
    row = FakeNode(".item-lista", children=[FakeNode(".sidra-check", attrs={})])
    assert _estado_checked(FakeLocator([row])) is False


def test_configure_idade_seleciona_60_mais():
    page = FakePage()
    page.add('.janela-dados:has-text("60 a 69 anos")', age_janela())
    selecionadas = configure_idade(page)
    assert all(nome in selecionadas for nome in settings.IDADE_ALVO)
    assert "Total" not in selecionadas


def test_configure_idade_falha_quando_total_continua_marcado():
    page = FakePage()
    janela = age_janela(ano_zero=True)
    page.add('.janela-dados:has-text("60 a 69 anos")', janela)
    with pytest.raises(RuntimeError, match="idade"):
        configure_idade(page)


def test_configure_idade_falha_quando_alvo_nao_marcado():
    page = FakePage()
    janela = age_janela(alvo_click_disabled=True)
    page.add('.janela-dados:has-text("60 a 69 anos")', janela)
    with pytest.raises(RuntimeError, match="idade"):
        configure_idade(page)


def test_configure_idade_falha_quando_segundo_alvo_bloqueado():
    page = FakePage()
    janela = age_janela(alvo_click_disabled="70 anos ou mais")
    page.add('.janela-dados:has-text("60 a 69 anos")', janela)
    with pytest.raises(RuntimeError, match="idade"):
        configure_idade(page)


def test_selecionar_ano_ja_selecionado():
    page = FakePage()
    page.add('.janela-dados:has-text("atualizado")', year_janela(max_checked=True))
    escolhido = selecionar_ano(page)
    assert escolhido == settings.ANO_PREFERIDO


def test_selecionar_ano_muda_para_mais_recente():
    page = FakePage()
    janela = FakeNode(
        ".janela-dados",
        children=[
            toggle_row("2010 - atualizado em 26/10/2009", checked=False),
            toggle_row("2022 - atualizado em 22/12/2023", checked=False),
            toggle_row("2000 - atualizado em 29/04/2009", checked=False),
        ],
    )
    page.add('.janela-dados:has-text("atualizado")', janela)
    assert selecionar_ano(page) == settings.ANO_PREFERIDO


def test_selecionar_ano_preferido_indisponivel_usa_mais_recente():
    page = FakePage()
    page.add('.janela-dados:has-text("atualizado")', year_janela())
    assert selecionar_ano(page, preferido="1990") == "2022"


def test_selecionar_ano_linha_nao_numerica_ignorada():
    page = FakePage()
    janela = FakeNode(
        ".janela-dados",
        children=[
            toggle_row("Censo Demográfico 2022", checked=False),
            toggle_row("2000 - atualizado em 29/04/2009", checked=False),
        ],
    )
    page.add('.janela-dados:has-text("atualizado")', janela)
    assert selecionar_ano(page) == "2000"


def test_selecionar_ano_sem_anos_falha():
    page = FakePage()
    janela = FakeNode(".janela-dados")
    page.add('.janela-dados:has-text("atualizado")', janela)
    with pytest.raises(RuntimeError, match="Anos disponíveis"):
        selecionar_ano(page)


def test_selecionar_ano_nao_confirma_falha():
    page = FakePage()
    janela = FakeNode(
        ".janela-dados",
        children=[
            toggle_row(
                "2022 - atualizado em 22/12/2023",
                checked=False,
                click_disabled=True,
            ),
            toggle_row("2010 - atualizado em 26/10/2009", checked=False),
        ],
    )
    page.add('.janela-dados:has-text("atualizado")', janela)
    with pytest.raises(RuntimeError, match="não pôde ser selecionado"):
        selecionar_ano(page)


def test_activate_uf_ativa_uf_e_desmarca_brasil():
    page = FakePage()
    page.add("#linha-territorios #arvore-niveis", arvore_niveis())
    activate_uf(page)


def test_activate_uf_ja_configurado_sem_cliques():
    page = FakePage()
    arvore = FakeNode(
        "#arvore-niveis",
        children=[
            arvore_node("Brasil [1/1]", checked=False),
            arvore_node("Unidade da Federação [27/27]", checked=True),
        ],
    )
    page.add("#linha-territorios #arvore-niveis", arvore)
    activate_uf(page)


def test_activate_uf_falha_se_uf_nao_ativado():
    page = FakePage()
    arvore = FakeNode(
        "#arvore-niveis",
        children=[
            arvore_node("Brasil [1/1]", checked=True),
            arvore_node(
                "Unidade da Federação [0/27]",
                checked=False,
                click_disabled=True,
            ),
        ],
    )
    page.add("#linha-territorios #arvore-niveis", arvore)
    with pytest.raises(RuntimeError, match="UF não ativado"):
        activate_uf(page)


def test_activate_uf_falha_se_brasil_nao_desmarcado():
    page = FakePage()
    arvore = FakeNode(
        "#arvore-niveis",
        children=[
            arvore_node("Brasil [1/1]", checked=True, click_disabled=True),
            arvore_node("Unidade da Federação [0/27]", checked=False),
        ],
    )
    page.add("#linha-territorios #arvore-niveis", arvore)
    with pytest.raises(RuntimeError, match="Brasil deveria estar desmarcado"):
        activate_uf(page)


def test_visualizar_aguarda_texto_resultado():
    page = build_happy_page()
    visualizar(page)
    assert page.locator("#botaoOk")._nodes[0].value == "click"


def test_download_csv_abre_modal_e_salva(tmp_path):
    page = build_happy_page()
    saida = tmp_path / "dados" / "populacao_60mais_1209.csv"
    download_csv(page, str(saida))
    assert saida.exists()


def test_download_csv_desmarca_zip_quando_checked(tmp_path):
    page = build_happy_page()
    modal = download_modal(zip_checked=True)
    page.add("#modal-downloads", modal)
    download_csv(page, str(tmp_path / "saida.csv"))
    assert (tmp_path / "saida.csv").exists()


def test_download_csv_zip_ja_desmarcado(tmp_path):
    page = build_happy_page()
    modal = download_modal(zip_checked=False)
    page.add("#modal-downloads", modal)
    download_csv(page, str(tmp_path / "saida2.csv"))
    assert (tmp_path / "saida2.csv").exists()


def test_download_csv_falha_quando_expect_download_timeout(tmp_path):
    page = build_happy_page()
    page.download_fails = True
    with pytest.raises(TimeoutError, match="fake expect_download timeout"):
        download_csv(page, str(tmp_path / "falha.csv"))


def test_download_csv_salva_com_conteudo_do_download(tmp_path):
    page = build_happy_page()
    page.download = FakeDownload("teste.csv", content="a;b\n1;2\n")
    download_csv(page, str(tmp_path / "ok.csv"))
    assert (tmp_path / "ok.csv").read_text(encoding="utf-8") == "a;b\n1;2\n"
