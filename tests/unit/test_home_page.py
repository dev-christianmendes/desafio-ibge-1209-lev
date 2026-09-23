
import pytest

from src.pages.home_page import open_home, search_table
from tests.unit.fake_playwright import FakeNode, FakePage, build_happy_page

_TITULO_REAL = "Tabela 1209 - População, por grupos de idade"


def test_open_home_acessa_pagina_do_sidra():
    page = FakePage(title=_TITULO_REAL)
    open_home(page)
    assert page.actions[0] == ("goto", "https://sidra.ibge.gov.br/")


def test_open_home_aguarda_liberacao_do_cloudflare():
    page = FakePage(title="Just a moment")
    page.title_values = ["Just a moment", _TITULO_REAL]
    open_home(page)
    assert ("reload",) in page.actions


def test_search_table_localiza_tabela_1209():
    page = build_happy_page()
    search_table(page)
    campo = page.locator('input[placeholder="pesquisar"]:visible').first
    assert campo._nodes[0].value == "Enter"
    lupa_visivel = page.locator(".glyphicon-search.lupa").all()[1]
    assert lupa_visivel._nodes[0].value == "click"


def test_search_table_url_incorreta_falha():
    page = FakePage(url="https://sidra.ibge.gov.br/")
    page.add(".glyphicon-search.lupa", FakeNode(".lupa", visible=True))
    page.add('input[placeholder="pesquisar"]:visible', FakeNode("input"))
    with pytest.raises(TimeoutError):
        search_table(page)
