from pathlib import Path

import pytest

from src.config import settings
from src.validation.csv_validator import (
    CSVValidationError,
    _linha_de_ano,
    _linhas_de_dados,
    _linhas_significativas,
    _primeiras_celulas,
    _valor_para_int,
    _valor_positivo,
    validate_csv,
)
from tests.unit.fake_playwright import _conteudo_csv_ok


def _escrever_csv(tmp_path, conteudo: str) -> Path:
    caminho = tmp_path / "dados" / "populacao_60mais_1209.csv"
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(conteudo, encoding="utf-8-sig")
    return caminho


def test_validate_csv_sucesso(tmp_path):
    caminho = _escrever_csv(tmp_path, _conteudo_csv_ok())
    resultado = validate_csv(caminho)
    assert resultado["ano"] == settings.ANO_PREFERIDO
    assert resultado["quantidade_registros"] == 27
    assert len(resultado["ufs"]) == 27
    assert resultado["total_60_mais"] > 0
    assert "60 a 69 anos" in resultado["idades"]


def test_validate_csv_arquivo_nao_encontrado(tmp_path):
    with pytest.raises(CSVValidationError, match="não encontrado"):
        validate_csv(tmp_path / "inexistente.csv")


def test_validate_csv_extensao_invalida(tmp_path):
    caminho = tmp_path / "saida.txt"
    caminho.write_text(_conteudo_csv_ok(), encoding="utf-8")
    with pytest.raises(CSVValidationError, match="extensão .csv"):
        validate_csv(caminho)


def test_validate_csv_vazio(tmp_path):
    caminho = tmp_path / "vazio.csv"
    caminho.write_text("", encoding="utf-8")
    with pytest.raises(CSVValidationError, match="vazio"):
        validate_csv(caminho)


def test_validate_csv_titulo_incorreto(tmp_path):
    linhas = _conteudo_csv_ok().splitlines()
    linhas[0] = '"Tabela 9999 - Outro"'
    caminho = _escrever_csv(tmp_path, "\n".join(linhas) + "\n")
    with pytest.raises(CSVValidationError, match="Título do CSV"):
        validate_csv(caminho)


def test_validate_csv_variavel_ausente(tmp_path):
    linhas = _conteudo_csv_ok().splitlines()
    linhas[1] = '"Variável - X"'
    caminho = _escrever_csv(tmp_path, "\n".join(linhas) + "\n")
    with pytest.raises(CSVValidationError, match="Variável 'População' ausente"):
        validate_csv(caminho)


def test_validate_csv_ano_ausente(tmp_path):
    linhas = _conteudo_csv_ok().splitlines()
    for i, linha in enumerate(linhas):
        if '"2022"' in linha:
            linhas[i] = linha.replace('"2022"', '"2021"')
    caminho = _escrever_csv(tmp_path, "\n".join(linhas) + "\n")
    with pytest.raises(CSVValidationError, match="Ano 2022 ausente"):
        validate_csv(caminho)


def test_validate_csv_colunas_idade_ausentes(tmp_path):
    linhas = _conteudo_csv_ok().splitlines()
    linhas = [linha for linha in linhas if "60 a 69 anos" not in linha]
    caminho = _escrever_csv(tmp_path, "\n".join(linhas) + "\n")
    with pytest.raises(CSVValidationError, match="Colunas de idade"):
        validate_csv(caminho)


def test_validate_csv_sem_dados(tmp_path):
    linhas = _conteudo_csv_ok().splitlines()
    linhas = [linhas[0], linhas[1], linhas[2], linhas[3], linhas[4]]
    caminho = _escrever_csv(tmp_path, "\n".join(linhas) + "\n")
    with pytest.raises(CSVValidationError, match="sem linhas de dados"):
        validate_csv(caminho)


def _indice_da_uf(linhas, uf):
    return next(
        i
        for i, linha in enumerate(linhas)
        if linha.startswith(f'"{uf}"')
    )


def _trocar_uf(tmp_path, uf, nova_linha):
    linhas = _conteudo_csv_ok().splitlines()
    linhas[_indice_da_uf(linhas, uf)] = nova_linha
    return _escrever_csv(tmp_path, "\n".join(linhas) + "\n")


def test_validate_csv_uf_inesperada(tmp_path):
    caminho = _trocar_uf(
        tmp_path,
        "Rondônia",
        '"XX - Estrangeiro";"100001";"50001"',
    )
    with pytest.raises(CSVValidationError, match="Território inesperado"):
        validate_csv(caminho)


def test_validate_csv_valor_negativo(tmp_path):
    caminho = _trocar_uf(tmp_path, "Acre", '"Acre";"-1";"50002"')
    with pytest.raises(CSVValidationError, match="Valor inválido"):
        validate_csv(caminho)


def test_validate_csv_valor_nao_numerico(tmp_path):
    caminho = _trocar_uf(tmp_path, "Amazonas", '"Amazonas";"abc";"50003"')
    with pytest.raises(CSVValidationError, match="Valor inválido"):
        validate_csv(caminho)


def test_validate_csv_ufs_repetidas(tmp_path):
    linhas = _conteudo_csv_ok().splitlines()
    linhas[_indice_da_uf(linhas, "Amazonas")] = linhas[_indice_da_uf(linhas, "Acre")]
    caminho = _escrever_csv(tmp_path, "\n".join(linhas) + "\n")
    with pytest.raises(CSVValidationError, match="não cobre as 27 UFs"):
        validate_csv(caminho)


def test_helpers_de_validacao_cobrem_casos():
    assert _linha_de_ano(["Unidade da Federação"]) is False
    assert _linha_de_ano(["Unidade da Federação", "2022"]) is True
    assert _linha_de_ano(["Outro", "2022"]) is False

    assert _primeiras_celulas([]) == []
    assert _primeiras_celulas([["A", "B"], []]) == ["A", "B"]

    assert _valor_para_int(" 123 ") == 123
    assert _valor_positivo("10") is True
    assert _valor_positivo("0") is False
    assert _valor_positivo("-5") is False
    assert _valor_positivo("x") is False


def test_csv_reader_erro_leitura(tmp_path):
    caminho = tmp_path / "corrompido.csv"
    caminho.write_bytes(b"\xff\xfe\xfd")
    with pytest.raises(CSVValidationError):
        _linhas_significativas(caminho)


def test_linhas_de_dados_para_na_fonte():
    linhas = [
        ["Unidade da Federação", "a"],
        ["Rondônia", "1"],
        ["Fonte: IBGE - Censo"],
        ["Notas"],
    ]
    dados = _linhas_de_dados(linhas, header_idx=0)
    assert len(dados) == 1
    assert dados[0][0] == "Rondônia"


def test_linhas_de_dados_primeira_celula_vazia_encerra():
    linhas = [["UF"], ["", "x"], ["Rondônia", "1"]]
    assert _linhas_de_dados(linhas, header_idx=0) == []


def test_linhas_de_dados_linha_vazia_encerra():
    linhas = [["UF"], [], ["Rondônia", "1"]]
    assert _linhas_de_dados(linhas, header_idx=0) == []
