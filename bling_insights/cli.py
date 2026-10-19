"""Ponto de entrada: `python -m bling_insights ...`"""

from __future__ import annotations

import argparse
import os
import sys
from datetime import date, timedelta
from pathlib import Path

from .alerts import send_low_stock_email
from .analyzer import find_low_stock, summarize_sales
from .datasource import BlingAPISource, MockDataSource
from .report import console, export_excel_report, print_console_report


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="bling-insights",
        description="Monitor de vendas e estoque integrado ao Bling ERP.",
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Usa dados de exemplo locais em vez da API real do Bling.",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=30,
        help="Quantos dias de vendas analisar (padrão: 30).",
    )
    parser.add_argument(
        "--export-excel",
        type=Path,
        default=None,
        help="Caminho para exportar o relatório em .xlsx.",
    )
    parser.add_argument(
        "--send-alert",
        action="store_true",
        help="Envia e-mail de alerta se houver produtos com estoque baixo "
        "(requer variáveis SMTP_* no ambiente).",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    if args.demo:
        source = MockDataSource()
    else:
        token = os.environ.get("BLING_ACCESS_TOKEN")
        if not token:
            console.print(
                "[red]Erro:[/] defina BLING_ACCESS_TOKEN no ambiente ou use --demo. "
                "Veja README.md."
            )
            return 1
        source = BlingAPISource(access_token=token)

    end = date.today()
    start = end - timedelta(days=args.days)

    products = source.get_products()
    orders = source.get_orders(start, end)

    summary = summarize_sales(orders)
    low_stock = find_low_stock(products)

    print_console_report(summary, low_stock)

    if args.export_excel:
        path = export_excel_report(summary, low_stock, args.export_excel)
        console.print(f"\n[blue]Relatório exportado para:[/] {path}")

    if args.send_alert and low_stock:
        send_low_stock_email(
            low_stock,
            smtp_host=os.environ["SMTP_HOST"],
            smtp_port=int(os.environ.get("SMTP_PORT", 587)),
            smtp_user=os.environ["SMTP_USER"],
            smtp_password=os.environ["SMTP_PASSWORD"],
            recipient=os.environ["ALERT_RECIPIENT"],
        )
        console.print("[blue]E-mail de alerta enviado.[/]")

    return 0


if __name__ == "__main__":
    sys.exit(main())
