from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "dados"
EVIDENCIAS_DIR = PROJECT_ROOT / "evidencias"
LOGS_DIR = PROJECT_ROOT / "logs"

CSV_PATH = DATA_DIR / "populacao_60mais_1209.csv"
LOG_PATH = LOGS_DIR / "sidra.log"

SIDRA_HOME_URL = "https://sidra.ibge.gov.br/"
TABELA_ID = "1209"
TABELA_TITULO = "Tabela 1209 - População, por grupos de idade"
TABELA_URL_PREFIX = "https://sidra.ibge.gov.br/Tabela/1209"

IDADE_ALVO = ("60 a 69 anos", "70 anos ou mais")
ANO_PREFERIDO = "2022"

HEADLESS = False
VIEWPORT = {"width": 1440, "height": 900}
NAVIGATION_TIMEOUT_MS = 90_000
ELEMENT_TIMEOUT_MS = 60_000
DOWNLOAD_TIMEOUT_MS = 120_000
CHALLENGE_TIMEOUT_S = 90
CHALLENGE_RETRY_S = 2

NOME_ARQUIVO_FINAL = "populacao_60mais_1209"
FORMATO_CSV = "br.csv"

UFS: tuple[str, ...] = (
    "Rondônia",
    "Acre",
    "Amazonas",
    "Roraima",
    "Pará",
    "Amapá",
    "Tocantins",
    "Maranhão",
    "Piauí",
    "Ceará",
    "Rio Grande do Norte",
    "Paraíba",
    "Pernambuco",
    "Alagoas",
    "Sergipe",
    "Bahia",
    "Minas Gerais",
    "Espírito Santo",
    "Rio de Janeiro",
    "São Paulo",
    "Paraná",
    "Santa Catarina",
    "Rio Grande do Sul",
    "Mato Grosso do Sul",
    "Mato Grosso",
    "Goiás",
    "Distrito Federal",
)

EVIDENCIA_HOME = "01-sidra-home.png"
EVIDENCIA_BUSCA = "02-busca.png"
EVIDENCIA_TABELA = "03-tabela-1209.png"
EVIDENCIA_FILTROS = "04-filtros-configurados.png"
EVIDENCIA_DOWNLOAD = "05-download.png"
EVIDENCIA_VALIDACAO = "06-validacao.png"
EVIDENCIA_ERRO = "erro-{etapa}.png"
