from __future__ import annotations

from pathlib import Path

from src.config import settings


class FakeNode:
    def __init__(self, sel="", text="", attrs=None, children=None, visible=True,
                 checked=False, click_disabled=False):
        self.sel = sel
        self.text = text or ""
        self.attrs = dict(attrs or {})
        self.children = list(children or [])
        self.visible = visible
        self.checked = checked
        self.click_disabled = click_disabled
        self.parent_check = None
        self.value = None


class FakeLocator:
    def __init__(self, nodes):
        self._nodes = list(nodes)

    @property
    def first(self):
        return FakeLocator(self._nodes[:1])

    def all(self):
        return [FakeLocator([node]) for node in self._nodes]

    def count(self):
        return len(self._nodes)

    def is_visible(self):
        return bool(self._nodes) and self._nodes[0].visible

    def is_checked(self):
        return bool(self._nodes) and self._nodes[0].checked

    def get_attribute(self, name):
        node = self._nodes[0]
        return node.attrs.get(name)

    def inner_text(self):
        node = self._nodes[0]
        return node.text

    def locator(self, selector, has_text=None):
        found = []
        for node in self._nodes:
            for child in node.children:
                if child.sel == selector and (
                    has_text is None or has_text in child.text
                ):
                    found.append(child)
        return FakeLocator(found)

    def wait_for(self, state="visible", timeout=None):
        if state == "visible" and (not self._nodes or not self._nodes[0].visible):
            raise TimeoutError("fake wait_for visible falhou")

    def click(self):
        node = self._nodes[0]
        if getattr(node, "parent_check", None) and not node.click_disabled:
            self._toggle_sidra_check(node.parent_check)
        node.value = "click"

    def fill(self, value):
        self._nodes[0].value = value

    def press(self, key):
        self._nodes[0].value = key

    def focus(self):
        self._nodes[0].value = "focus"

    def uncheck(self):
        node = self._nodes[0]
        node.checked = False
        node.attrs["class"] = node.attrs.get("class", "").replace(" checked", "")

    def select_option(self, value):
        self._nodes[0].value = value

    @staticmethod
    def _toggle_sidra_check(check_node):
        check_node.checked = not check_node.checked
        check_node.attrs["class"] = (
            "sidra-check" + (" checked" if check_node.checked else "")
        )
        check_node.attrs["aria-selected"] = str(check_node.checked).lower()


class FakeKeyboard:
    def __init__(self, page):
        self._page = page

    def press(self, key):
        self._page.record("keyboard.press", key)


class FakeDownload:
    def __init__(self, filename, content=None):
        self.suggested_filename = filename
        self._content = content if content is not None else _conteudo_csv_ok()
        self.saved_to = None

    def save_as(self, path):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_text(self._content, encoding="utf-8")
        self.saved_to = str(path)


class _DownloadContext:
    def __init__(self, page):
        self._page = page

    def __enter__(self):
        if self._page.download_fails:
            raise TimeoutError("fake expect_download timeout")
        return self

    def __exit__(self, *args):
        return False

    @property
    def value(self):
        return self._page.download


class FakePage:
    def __init__(self, title="Tabela 1209 - População, por grupos de idade",
                 url="https://sidra.ibge.gov.br/Tabela/1209"):
        self.title_values = [title]
        self.title_index = 0
        self.title_raises = False
        self.screenshot_raises = False
        self._url = url
        self.url = url
        self._registry = {}
        self.actions = []
        self.screenshots = []
        self.download = FakeDownload("populacao_60mais_1209.csv")
        self.download_fails = False
        self.keyboard = FakeKeyboard(self)

    def record(self, *event):
        self.actions.append(event)

    def add(self, selector, node_or_list):
        self._registry[selector] = node_or_list

    def title(self):
        if self.title_raises:
            raise ConnectionError("fake title error")
        value = self.title_values[self.title_index]
        if self.title_index < len(self.title_values) - 1:
            self.title_index += 1
        return value

    def goto(self, url, wait_until=None, timeout=None):
        self.record("goto", url)

    def reload(self, wait_until=None):
        self.record("reload")

    def screenshot(self, path=None, full_page=False):
        if self.screenshot_raises:
            raise ConnectionError("fake screenshot error")
        self.screenshots.append(str(path))

    def wait_for_url(self, pattern, timeout=None):
        if "**" in pattern:
            _, head, _ = pattern.split("**", 2)
            if head and head not in self._url:
                raise TimeoutError(f"fake wait_for_url falhou: {pattern}")
            return
        if pattern != self._url:
            raise TimeoutError("fake wait_for_url exato falhou")

    def expect_download(self, timeout=None):
        return _DownloadContext(self)

    def locator(self, selector):
        if selector not in self._registry:
            raise KeyError(f"seletor fake não registrado: {selector}")
        value = self._registry[selector]
        nodes = value if isinstance(value, list) else [value]
        return FakeLocator(nodes)

    def get_by_text(self, text, exact=False):
        found = []
        for value in self._registry.values():
            nodes = value if isinstance(value, list) else [value]
            for node in nodes:
                if (node.text == text if exact else text in node.text):
                    found.append(node)
        return FakeLocator(found)


def toggle_row(nome, checked=False, click_disabled=False):
    check = FakeNode(
        ".sidra-check",
        attrs={
            "class": "sidra-check" + (" checked" if checked else ""),
            "aria-selected": str(checked).lower(),
        },
        checked=checked,
    )
    toggle = FakeNode(".sidra-toggle", click_disabled=click_disabled)
    toggle.parent_check = check
    nome_span = FakeNode(".nome", text=nome)
    check.children = [toggle, nome_span]
    return FakeNode(".item-lista", text=nome, children=[check, toggle, nome_span])


def arvore_node(nome, checked=False, click_disabled=False):
    check = FakeNode(
        ".sidra-check",
        text=nome,
        attrs={
            "class": "sidra-check" + (" checked" if checked else ""),
            "aria-selected": str(checked).lower(),
        },
        checked=checked,
    )
    toggle = FakeNode(".sidra-toggle", click_disabled=click_disabled)
    toggle.parent_check = check
    nome_span = FakeNode(".nome", text=nome)
    check.children = [toggle, nome_span]
    return check


def age_janela(ano_zero=False, alvo_click_disabled=False):
    nomes = [
        "Total",
        "0 a 4 anos",
        "5 a 9 anos",
        "10 a 14 anos",
        "15 a 19 anos",
        "20 a 24 anos",
        "25 a 29 anos",
        "30 a 39 anos",
        "40 a 49 anos",
        "50 a 59 anos",
        "60 a 69 anos",
        "70 anos ou mais",
        "Idade ignorada [1872, 2000]",
    ]
    total_disabled = bool(ano_zero)
    alvo01_disabled = alvo_click_disabled
    alvo02_disabled = False
    if isinstance(alvo_click_disabled, str):
        alvo01_disabled = alvo_click_disabled == "60 a 69 anos"
        alvo02_disabled = alvo_click_disabled == "70 anos ou mais"
    rows = []
    for nome in nomes:
        checked = nome == "Total"
        disabled = False
        if nome == "Total":
            disabled = total_disabled
        elif nome == "60 a 69 anos":
            disabled = alvo01_disabled
        elif nome == "70 anos ou mais":
            disabled = alvo02_disabled
        rows.append(toggle_row(nome, checked=checked, click_disabled=disabled))
    return FakeNode(".janela-dados", children=rows)


def year_janela(max_checked=False):
    rows = [
        toggle_row("2022 - atualizado em 22/12/2023", checked=max_checked),
        toggle_row("2010 - atualizado em 26/10/2023", checked=False),
        toggle_row("2000 - atualizado em 29/04/2009", checked=False),
    ]
    return FakeNode(".janela-dados", children=rows)


def arvore_niveis():
    return FakeNode(
        "#arvore-niveis",
        children=[
            arvore_node("Brasil [1/1]", checked=True),
            arvore_node("Grande Região [0/5]", checked=False),
            arvore_node("Unidade da Federação [0/27]", checked=False),
        ],
    )


def download_modal(visible=True, zip_checked=True):
    return FakeNode(
        "#modal-downloads",
        visible=visible,
        children=[
            FakeNode('input[name="nome-arquivo"]', visible=visible),
            FakeNode('select[name="formato-arquivo"]', visible=visible),
            FakeNode("#download-cmp", visible=visible, checked=zip_checked),
            FakeNode("#opcao-downloads", visible=visible),
        ],
    )


def _conteudo_csv_ok() -> str:
    linhas = [
        '"Tabela 1209 - População, por grupos de idade"',
        '"Variável - População (Pessoas)"',
        '"Unidade da Federação";"Ano x Grupo de idade"',
        '"Unidade da Federação";"2022"',
        '"Unidade da Federação";"60 a 69 anos";"70 anos ou mais"',
    ]
    for indice, uf in enumerate(settings.UFS, start=1):
        linhas.append(f'"{uf}";"{100000 + indice}";"{50000 + indice}"')
    linhas.append('"Fonte: IBGE - Censo Demográfico"')
    return "\n".join(linhas) + "\n"


def build_happy_page(download=None):
    page = FakePage()
    page.add(
        ".glyphicon-search.lupa",
        [
            FakeNode(".glyphicon-search.lupa", visible=False),
            FakeNode(".glyphicon-search.lupa", visible=True),
        ],
    )
    page.add('input[placeholder="pesquisar"]:visible', FakeNode("input"))
    page.add(
        "heading-1209",
        FakeNode(".titulo", text="Tabela 1209 - População, por grupos de idade"),
    )
    page.add('.janela-dados:has-text("60 a 69 anos")', age_janela())
    page.add('.janela-dados:has-text("atualizado")', year_janela(max_checked=True))
    page.add("#linha-territorios #arvore-niveis", arvore_niveis())
    page.add("#botaoOk", FakeNode("#botaoOk"))
    page.add("resultado", FakeNode(".visao", text="Rondônia"))
    page.add("#botao-downloads", FakeNode("#botao-downloads"))
    page.add("#modal-downloads", download_modal())
    if download is not None:
        page.download = download
    return page
