from desafio_ibge_1209 import _argumentos, _relatorio, main
from src.config import settings
from tests.unit.fake_playwright import FakeDownload, build_happy_page


class _FakeBrowser:
    def new_context(self, accept_downloads=True, viewport=None):
        return self

    def new_page(self):
        return self._page

    def close(self):
        pass

    def __init__(self, page):
        self._page = page


class _FakePlaywright:
    def __init__(self, page):
        self.chromium = self
        self._page = page

    def launch(self, headless=False):
        self._launched = headless
        return _FakeBrowser(self._page)


class _FakeSync:
    def __init__(self, page):
        self._page = page

    def __enter__(self):
        return _FakePlaywright(self._page)

    def __exit__(self, exc_type, exc, tb):
        return False


def test_argumentos_padroes():
    args = _argumentos([])
    assert args.output == str(settings.CSV_PATH)
    assert args.evidencias == str(settings.EVIDENCIAS_DIR)
    assert args.headless is False
    assert args.log_file == str(settings.LOG_PATH)


def test_argumentos_com_flags(tmp_path):
    args = _argumentos(
        [
            "--output",
            str(tmp_path / "saida.csv"),
            "--evidencias",
            str(tmp_path / "ev"),
            "--headless",
            "--log-file",
            str(tmp_path / "log.txt"),
        ]
    )
    assert args.output == str(tmp_path / "saida.csv")
    assert args.evidencias == str(tmp_path / "ev")
    assert args.headless is True
    assert args.log_file == str(tmp_path / "log.txt")


def test_relatorio_formato_aprovado():
    resumo = {
        "status": "APROVADO",
        "tabela": settings.TABELA_TITULO,
        "ano": "2022",
        "idade": "60 a 69 anos + 70 anos ou mais (60 anos ou mais)",
        "territorio": "Unidades da Federação (27)",
        "csv": "/tmp/saida.csv",
        "quantidade_registros": 27,
        "total_60_mais": 4050000,
    }
    texto = _relatorio(resumo)
    assert "STATUS: APROVADO" in texto
    assert "Tabela 1209" in texto
    assert "Ano utilizado: 2022" in texto


def test_relatorio_formato_falhou():
    resumo = {
        "status": "FALHOU",
        "tabela": settings.TABELA_TITULO,
        "ano": "2022",
        "idade": "60+",
        "territorio": "UF",
        "csv": "/tmp/x.csv",
        "quantidade_registros": 0,
        "total_60_mais": 0,
    }
    assert "STATUS: FALHOU" in _relatorio(resumo)


def test_main_fluxo_sucesso(tmp_path, monkeypatch, capsys):
    page = build_happy_page()
    monkeypatch.setattr(
        "desafio_ibge_1209.sync_playwright",
        lambda: _FakeSync(page),
    )
    saida = tmp_path / "saida.csv"
    argv = [
        "--output",
        str(saida),
        "--evidencias",
        str(tmp_path / "ev"),
        "--headless",
    ]
    codigo = main(argv)
    capturado = capsys.readouterr()
    assert codigo == 0
    assert "STATUS: APROVADO" in capturado.out


def test_main_fluxo_falha(monkeypatch, capsys):
    def _boom(*args, **kwargs):
        raise RuntimeError("falha inesperada")

    monkeypatch.setattr("desafio_ibge_1209.sync_playwright", _boom)
    codigo = main([])
    capturado = capsys.readouterr()
    assert codigo == 1
    assert "[ERROR]" in capturado.out


def test_main_falha_validacao(monkeypatch, capsys, tmp_path):
    page = build_happy_page()
    page.download = FakeDownload("x.csv", content="invalido")
    monkeypatch.setattr(
        "desafio_ibge_1209.sync_playwright",
        lambda: _FakeSync(page),
    )
    codigo = main(["--output", str(tmp_path / "x.csv")])
    capturado = capsys.readouterr()
    assert codigo == 1
    assert "[ERROR]" in capturado.out
