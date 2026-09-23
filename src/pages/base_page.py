import time

from src.config import settings

_CHALLENGE_TEXT = "Just a moment"


def wait_challenge_clear(
    page,
    timeout: float = settings.CHALLENGE_TIMEOUT_S,
    retry_s: float = settings.CHALLENGE_RETRY_S,
) -> None:
    deadline = time.monotonic() + timeout
    reloaded = False
    while time.monotonic() < deadline:
        try:
            title = page.title()
        except Exception:
            title = ""
        if title and _CHALLENGE_TEXT not in title:
            return
        if not reloaded:
            page.reload(wait_until="domcontentloaded")
            reloaded = True
            continue
        time.sleep(retry_s)
    raise RuntimeError("Desafio do Cloudflare não foi resolvido no tempo esperado")


def first_visible(locator):
    elements = locator.all()
    for element in elements:
        if element.is_visible():
            return element
    raise RuntimeError("Nenhum elemento visível encontrado no seletor informado")


def wait_text(page, text: str, timeout: float = settings.ELEMENT_TIMEOUT_MS) -> None:
    page.get_by_text(text, exact=False).first.wait_for(state="visible", timeout=timeout)
