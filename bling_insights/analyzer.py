"""Regras de negócio: resumo de vendas e detecção de estoque baixo."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

from .models import Order, Product


@dataclass(frozen=True)
class ProductSales:
    product_id: int
    product_name: str
    quantity_sold: int
    revenue: float


@dataclass(frozen=True)
class SalesSummary:
    total_revenue: float
    total_orders: int
    average_ticket: float
    top_products: list[ProductSales]


def summarize_sales(orders: list[Order], top_n: int = 5) -> SalesSummary:
    """Agrega pedidos em um resumo: faturamento total, ticket médio e top produtos."""
    completed = [o for o in orders if o.status.lower() not in {"cancelado", "cancelled"}]

    totals_by_product: dict[int, ProductSales] = {}
    for order in completed:
        for item in order.items:
            existing = totals_by_product.get(item.product_id)
            qty = item.quantity + (existing.quantity_sold if existing else 0)
            rev = item.total + (existing.revenue if existing else 0)
            totals_by_product[item.product_id] = ProductSales(
                product_id=item.product_id,
                product_name=item.product_name,
                quantity_sold=qty,
                revenue=rev,
            )

    total_revenue = sum(o.total for o in completed)
    total_orders = len(completed)
    average_ticket = total_revenue / total_orders if total_orders else 0.0
    top_products = sorted(
        totals_by_product.values(), key=lambda p: p.revenue, reverse=True
    )[:top_n]

    return SalesSummary(
        total_revenue=total_revenue,
        total_orders=total_orders,
        average_ticket=average_ticket,
        top_products=top_products,
    )


def find_low_stock(products: list[Product]) -> list[Product]:
    """Retorna produtos cujo estoque está no ou abaixo do mínimo configurado."""
    return sorted(
        (p for p in products if p.is_low_stock),
        key=lambda p: p.stock - p.min_stock,
    )


def sales_by_day(orders: list[Order]) -> dict[str, float]:
    """Agrupa faturamento por dia (chave 'YYYY-MM-DD'), útil para gráficos."""
    totals: dict[str, float] = defaultdict(float)
    for order in orders:
        if order.status.lower() in {"cancelado", "cancelled"}:
            continue
        totals[order.date.isoformat()] += order.total
    return dict(sorted(totals.items()))
