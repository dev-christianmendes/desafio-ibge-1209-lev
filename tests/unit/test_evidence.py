
from src.utils.evidence import ensure_dir, save_screenshot
from tests.unit.fake_playwright import FakePage


def test_ensure_dir_cria_diretorio_e_pais(tmp_path):
    alvo = tmp_path / "evidencias" / "sub"
    resultado = ensure_dir(alvo)
    assert alvo.is_dir()
    assert resultado == alvo


def test_ensure_dir_idempotente(tmp_path):
    alvo = tmp_path / "dados"
    ensure_dir(alvo)
    assert ensure_dir(alvo) == alvo


def test_save_screenshot_captura_full_page(tmp_path):
    page = FakePage()
    caminho = save_screenshot(page, "01-sidra-home.png", tmp_path)
    assert caminho == tmp_path / "01-sidra-home.png"
    assert page.screenshots == [str(caminho)]
    assert tmp_path.is_dir()
