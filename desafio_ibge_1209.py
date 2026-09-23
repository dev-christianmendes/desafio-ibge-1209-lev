import argparse

from playwright.sync_api import sync_playwright

from src.config import settings
from src.services.sidra_automation import SidraAutomation
from src.utils.logger import setup_logging


def _argumentos(argv):
    parser = argparse.ArgumentParser(
        prog="desafio_ibge_1209",
        description=(
            "Automação RPA para obter a Tabela 1209 "
            "(população 60+) do SIDRA/IBGE."
        ),
    )
    parser.add_argument(
        "--output",
        default=str(settings.CSV_PATH),
        help="Caminho do CSV final (padrão: dados/populacao_60mais_1209.csv)",
    )
    parser.add_argument(
        "--evidencias",
        default=str(settings.EVIDENCIAS_DIR),
        help="Diretório de evidências (screenshots)",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Executa o navegador em modo headless (padrão: headed)",
    )
    parser.add_argument(
        "--log-file",
        default=str(settings.LOG_PATH),
        help="Arquivo de log (padrão: logs/sidra.log)",
    )
    return parser.parse_args(argv)


def _relatorio(resumo: dict) -> str:
    return "\n".join(
        [
            "STATUS: APROVADO" if resumo["status"] == "APROVADO" else "STATUS: FALHOU",
            f"Projeto: {settings.PROJECT_ROOT}",
            f"Tabela encontrada: {resumo['tabela']}",
            f"Ano utilizado: {resumo['ano']}",
            f"Configuração de idade: {resumo['idade']}",
            f"Configuração territorial: {resumo['territorio']}",
            f"CSV: {resumo['csv']}",
            f"Quantidade de registros: {resumo['quantidade_registros']}",
            f"Total 60+ (Brasil): {resumo['total_60_mais']}",
        ]
    )


def main(argv=None) -> int:
    args = _argumentos(argv)
    setup_logging(log_file=args.log_file)

    automacao = SidraAutomation()
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=args.headless)
            context = browser.new_context(
                accept_downloads=True,
                viewport=settings.VIEWPORT,
            )
            page = context.new_page()
            resumo = automacao.run(
                page,
                output_path=args.output,
                evidencias_dir=args.evidencias,
            )
            context.close()
            browser.close()
        print(_relatorio(resumo))
        return 0
    except Exception as exc:
        print(f"[ERROR] {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
