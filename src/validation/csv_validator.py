import csv
from pathlib import Path

from src.config import settings


class CSVValidationError(Exception):
    pass


def _linhas_significativas(path: Path) -> list[list[str]]:
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.reader(handle, delimiter=";", quotechar='"')
            return [row for row in reader if any(celula.strip() for celula in row)]
    except (OSError, UnicodeDecodeError, csv.Error) as exc:
        raise CSVValidationError(f"Arquivo CSV ilegível: {exc}") from exc


def _linha_de_ano(linha: list[str]) -> bool:
    if len(linha) != 2:
        return False
    return linha[0].strip() == "Unidade da Federação"


def _primeiras_celulas(linhas: list[list[str]]) -> list[str]:
    if not linhas:
        return []
    return [celula for celula in linhas[0] if celula]


def _linhas_de_dados(linhas: list[list[str]], header_idx: int) -> list[list[str]]:
    dados = []
    for linha in linhas[header_idx + 1 :]:
        primeiro = linha[0].strip() if linha else ""
        if primeiro.startswith("Fonte:") or not primeiro:
            break
        dados.append(linha)
    return dados


def validate_csv(
    path,
    ano_esperado: str = settings.ANO_PREFERIDO,
    ufs_esperadas=settings.UFS,
    idades_esperadas=settings.IDADE_ALVO,
) -> dict:
    caminho = Path(path)
    if not caminho.exists():
        raise CSVValidationError("Arquivo final não encontrado")
    if caminho.suffix.lower() != ".csv":
        raise CSVValidationError("Arquivo final não possui extensão .csv")
    if caminho.stat().st_size == 0:
        raise CSVValidationError("Arquivo final vazio")

    linhas = _linhas_significativas(caminho)

    titulo = " ".join(_primeiras_celulas(linhas))
    if f"Tabela {settings.TABELA_ID}" not in titulo or "População" not in titulo:
        raise CSVValidationError("Título do CSV não corresponde à Tabela 1209")
    if len(linhas) > 1 and not any("População" in celula for celula in linhas[1]):
        raise CSVValidationError("Variável 'População' ausente no cabeçalho")

    ano = next(
        (
            celula.strip()
            for linha in linhas
            if _linha_de_ano(linha)
            for celula in linha
            if celula.strip() == ano_esperado
        ),
        None,
    )
    if ano is None:
        raise CSVValidationError(f"Ano {ano_esperado} ausente no CSV")

    header_idx = None
    for i, linha in enumerate(linhas):
        if all(idade in linha for idade in idades_esperadas):
            header_idx = i
            break
    if header_idx is None:
        raise CSVValidationError("Colunas de idade (60+) ausentes no CSV")

    dados = _linhas_de_dados(linhas, header_idx)
    if not dados:
        raise CSVValidationError("CSV sem linhas de dados")

    ufs_encontradas = []
    for linha in dados:
        nome_uf = linha[0].strip()
        if nome_uf not in ufs_esperadas:
            raise CSVValidationError(f"Território inesperado no CSV: {nome_uf!r}")
        for valor in linha[1:]:
            if _valor_positivo(valor) is False:
                raise CSVValidationError(f"Valor inválido para {nome_uf}: {valor!r}")
        ufs_encontradas.append(nome_uf)

    if len(set(ufs_encontradas)) != len(ufs_esperadas):
        raise CSVValidationError(
            f"CSV não cobre as 27 UFs (encontradas {len(set(ufs_encontradas))})"
        )

    total_por_uf = {
        nome: sum(_valor_para_int(valor) for valor in linha[1:])
        for nome, linha in zip(ufs_encontradas, dados, strict=True)
    }
    return {
        "ano": ano,
        "idades": [celula.strip() for celula in linhas[header_idx] if celula.strip()],
        "quantidade_registros": len(ufs_encontradas),
        "ufs": list(ufs_encontradas),
        "total_60_mais_por_uf": total_por_uf,
        "total_60_mais": sum(total_por_uf.values()),
    }


def _valor_para_int(valor: str) -> int:
    return int(valor.strip())


def _valor_positivo(valor: str) -> bool:
    try:
        return int(valor.strip()) > 0
    except ValueError:
        return False
