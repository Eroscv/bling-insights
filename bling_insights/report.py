"""Geração de relatórios: terminal (rich) e planilha Excel."""

from __future__ import annotations

from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Font
from rich.console import Console
from rich.table import Table

from .analyzer import SalesSummary
from .models import Product

console = Console()


def print_console_report(summary: SalesSummary, low_stock: list[Product]) -> None:
    console.rule("[bold cyan]Resumo de Vendas")
    console.print(f"Faturamento total: [bold green]R$ {summary.total_revenue:,.2f}[/]")
    console.print(f"Pedidos (não cancelados): [bold]{summary.total_orders}[/]")
    console.print(f"Ticket médio: R$ {summary.average_ticket:,.2f}\n")

    top_table = Table(title="Top produtos por faturamento")
    top_table.add_column("Produto")
    top_table.add_column("Qtd. vendida", justify="right")
    top_table.add_column("Faturamento", justify="right")
    for p in summary.top_products:
        top_table.add_row(p.product_name, str(p.quantity_sold), f"R$ {p.revenue:,.2f}")
    console.print(top_table)

    console.rule("[bold yellow]Alertas de Estoque Baixo")
    if not low_stock:
        console.print("[green]Nenhum produto abaixo do estoque mínimo.[/]")
        return

    stock_table = Table()
    stock_table.add_column("SKU")
    stock_table.add_column("Produto")
    stock_table.add_column("Estoque atual", justify="right")
    stock_table.add_column("Mínimo", justify="right")
    for p in low_stock:
        stock_table.add_row(p.sku, p.name, str(p.stock), str(p.min_stock), style="red")
    console.print(stock_table)


def export_excel_report(
    summary: SalesSummary, low_stock: list[Product], output_path: Path
) -> Path:
    """Exporta o resumo de vendas e os alertas de estoque para um arquivo .xlsx."""
    wb = Workbook()
    bold = Font(bold=True)

    ws_sales = wb.active
    ws_sales.title = "Resumo de Vendas"
    ws_sales.append(["Faturamento total", summary.total_revenue])
    ws_sales.append(["Pedidos", summary.total_orders])
    ws_sales.append(["Ticket médio", summary.average_ticket])
    ws_sales.append([])
    ws_sales.append(["Produto", "Qtd. vendida", "Faturamento"])
    for cell in ws_sales[5]:
        cell.font = bold
    for p in summary.top_products:
        ws_sales.append([p.product_name, p.quantity_sold, p.revenue])

    ws_stock = wb.create_sheet("Estoque Baixo")
    ws_stock.append(["SKU", "Produto", "Estoque atual", "Mínimo"])
    for cell in ws_stock[1]:
        cell.font = bold
    for p in low_stock:
        ws_stock.append([p.sku, p.name, p.stock, p.min_stock])

    output_path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(output_path)
    return output_path
