import logging
from pathlib import Path

from src.config import settings
from src.pages.base_page import wait_text

logger = logging.getLogger("sidra")


def _lista_idade(page):
    return page.locator('.janela-dados:has-text("60 a 69 anos")').first


def _row_por_texto(lista, texto):
    return lista.locator(".item-lista", has_text=texto).first


def _toggle_da_row(row):
    return row.locator(".sidra-toggle")


def _estado_checked(row) -> bool:
    checks = row.locator(".sidra-check")
    alvo = checks.first if checks.count() > 0 else row
    classe = alvo.get_attribute("class") or ""
    return "checked" in classe


def _selecionadas(lista) -> list[str]:
    selecionadas = []
    for row in lista.locator(".item-lista").all():
        if _estado_checked(row):
            selecionadas.append(row.locator(".nome").inner_text().strip())
    return selecionadas


def configure_idade(page, alvo=settings.IDADE_ALVO) -> list[str]:
    lista = _lista_idade(page)
    _toggle_da_row(_row_por_texto(lista, "Total")).click()

    for nome in alvo:
        _toggle_da_row(_row_por_texto(lista, nome)).click()

    selecionadas = _selecionadas(lista)
    if "Total" in selecionadas or not all(nome in selecionadas for nome in alvo):
        raise RuntimeError("Filtro de idade não localizado/configurado corretamente")
    logger.info("Configurando grupo de idade: %s", " + ".join(alvo))
    return selecionadas


def _lista_anos(page):
    return page.locator('.janela-dados:has-text("atualizado")').first


def selecionar_ano(page, preferido: str = settings.ANO_PREFERIDO) -> str:
    lista = _lista_anos(page)
    anos = []
    for row in lista.locator(".item-lista").all():
        nome = row.locator(".nome").inner_text().strip()
        try:
            anos.append((int(nome.split()[0]), row))
        except ValueError:
            continue
    if not anos:
        raise RuntimeError("Anos disponíveis não encontrados na tabela")

    escolhido = (
        preferido
        if any(str(ano) == preferido for ano, _ in anos)
        else str(max(ano for ano, _ in anos))
    )
    ja_selecionado = any(
        _estado_checked(row) and str(ano) == escolhido for ano, row in anos
    )
    if not ja_selecionado:
        linha_escolhida = next(row for ano, row in anos if str(ano) == escolhido)
        _toggle_da_row(linha_escolhida).click()

    confirmado = any(
        _estado_checked(row) and str(ano) == escolhido for ano, row in anos
    )
    if not confirmado:
        raise RuntimeError(f"Ano {escolhido} não pôde ser selecionado")
    logger.info("Selecionando ano: %s", escolhido)
    return escolhido


def _arvore_niveis(page):
    return page.locator("#linha-territorios #arvore-niveis")


def activate_uf(page) -> None:
    arvore = _arvore_niveis(page)

    uf = arvore.locator(".sidra-check", has_text="Unidade da Federação").first
    if _estado_checked(uf) is False:
        _toggle_da_row(uf).click()
    brasil = arvore.locator(".sidra-check", has_text="Brasil").first
    if _estado_checked(brasil) is True:
        _toggle_da_row(brasil).click()

    if _estado_checked(uf) is not True:
        raise RuntimeError("Recorte territorial UF não ativado")
    if _estado_checked(brasil) is not False:
        raise RuntimeError("Recorte territorial Brasil deveria estar desmarcado")
    logger.info("Configurando território: Unidades da Federação (UF)")


def visualizar(page) -> None:
    page.locator("#botaoOk").click()
    wait_text(page, "Rondônia")
    logger.info("Visualizando resultado")


def abrir_modal_download(page):
    botao = page.locator("#botao-downloads")
    botao.focus()
    page.keyboard.press("Enter")
    modal = page.locator("#modal-downloads")
    modal.wait_for(state="visible", timeout=settings.ELEMENT_TIMEOUT_MS)
    return modal


def download_csv(
    page,
    output_path: str,
    nome_arquivo: str = settings.NOME_ARQUIVO_FINAL,
    formato: str = settings.FORMATO_CSV,
) -> str:
    modal = abrir_modal_download(page)
    modal.locator('input[name="nome-arquivo"]').fill(nome_arquivo)
    modal.locator('select[name="formato-arquivo"]').select_option(formato)

    zip_check = modal.locator("#download-cmp")
    if zip_check.is_checked():
        zip_check.uncheck()

    with page.expect_download(timeout=settings.DOWNLOAD_TIMEOUT_MS) as download_info:
        modal.locator("#opcao-downloads").click()
    download = download_info.value

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    download.save_as(str(output_path))
    logger.info("Iniciando download")
    logger.info("Arquivo salvo em %s", output_path)
    return output_path
