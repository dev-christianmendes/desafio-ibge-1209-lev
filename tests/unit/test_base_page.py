
import pytest

from src.pages.base_page import first_visible, wait_challenge_clear, wait_text
from tests.unit.fake_playwright import FakeNode, FakePage

_TITULO_REAL = "Tabela 1209 - População, por grupos de idade"


def test_wait_challenge_clear_titulo_liberado_de_primeira():
    page = FakePage(title=_TITULO_REAL)
    wait_challenge_clear(page, timeout=1.0)
    assert ("reload",) not in page.actions


def test_wait_challenge_clear_aguarda_desafio_e_recarrega():
    page = FakePage(title="Just a moment")
    page.title_values = ["Just a moment", _TITULO_REAL]
    wait_challenge_clear(page, timeout=1.0)
    assert ("reload",) in page.actions


def test_wait_challenge_clear_titulo_com_erro_dispara_reload_e_estoura():
    page = FakePage(title="Just a moment")
    page.title_raises = True
    with pytest.raises(RuntimeError, match="Desafio do Cloudflare"):
        wait_challenge_clear(page, timeout=0.15, retry_s=0.05)
    assert ("reload",) in page.actions


def test_wait_challenge_clear_desafio_nunca_resolvido_estoura_tempo():
    page = FakePage(title="Just a moment")
    page.title_values = ["Just a moment"]
    with pytest.raises(RuntimeError, match="Desafio do Cloudflare"):
        wait_challenge_clear(page, timeout=0.15, retry_s=0.05)
    assert ("reload",) in page.actions


def test_first_visible_retorna_primeiro_visivel():
    page = FakePage()
    page.add(
        ".lupa",
        [
            FakeNode(".lupa", visible=False),
            FakeNode(".lupa", visible=True),
        ],
    )
    elemento = first_visible(page.locator(".lupa"))
    assert elemento.is_visible()


def test_first_visible_sem_nenhum_visivel_falha():
    page = FakePage()
    page.add(
        ".lupa",
        [
            FakeNode(".lupa", visible=False),
            FakeNode(".lupa", visible=False),
        ],
    )
    with pytest.raises(RuntimeError, match="Nenhum elemento visível"):
        first_visible(page.locator(".lupa"))


def test_wait_text_encontra_texto_visivel():
    page = FakePage()
    page.add("resultado", FakeNode(".resultado", text="Rondônia"))
    wait_text(page, "Rondônia")


def test_wait_text_sem_texto_falha():
    page = FakePage()
    with pytest.raises(TimeoutError):
        wait_text(page, "Rondônia", timeout=1)
