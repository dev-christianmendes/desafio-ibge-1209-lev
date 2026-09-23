import logging

from src.config import settings
from src.pages.base_page import first_visible, wait_challenge_clear, wait_text

logger = logging.getLogger("sidra")


def open_home(page, url: str = settings.SIDRA_HOME_URL) -> None:
    page.goto(
        url,
        wait_until="domcontentloaded",
        timeout=settings.NAVIGATION_TIMEOUT_MS,
    )
    wait_challenge_clear(page)
    logger.info("Acessando página inicial")


def search_table(page, tabela_id: str = settings.TABELA_ID) -> None:
    lupa = first_visible(page.locator(".glyphicon-search.lupa"))
    lupa.click()

    campo = page.locator('input[placeholder="pesquisar"]:visible').first
    campo.fill(tabela_id)
    campo.press("Enter")

    page.wait_for_url(
        f"**/Tabela/{tabela_id}**",
        timeout=settings.NAVIGATION_TIMEOUT_MS,
    )
    wait_text(page, f"Tabela {tabela_id} - População, por grupos de idade")
    logger.info("Pesquisando tabela %s", tabela_id)
    logger.info("Tabela %s localizada", tabela_id)
