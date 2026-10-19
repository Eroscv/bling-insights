from datetime import date

from bling_insights.analyzer import find_low_stock, sales_by_day, summarize_sales
from bling_insights.models import Order, OrderItem, Product


def make_order(order_id, day, status, items):
    return Order(id=order_id, date=day, status=status, items=items)


def test_summarize_sales_ignores_cancelled_orders():
    orders = [
        make_order(
            1,
            date(2026, 10, 1),
            "concluido",
            [OrderItem(product_id=1, product_name="Caneca", quantity=2, unit_price=10.0)],
        ),
        make_order(
            2,
            date(2026, 10, 2),
            "cancelado",
            [OrderItem(product_id=1, product_name="Caneca", quantity=5, unit_price=10.0)],
        ),
    ]

    summary = summarize_sales(orders)

    assert summary.total_orders == 1
    assert summary.total_revenue == 20.0
    assert summary.average_ticket == 20.0


def test_summarize_sales_ranks_top_products_by_revenue():
    orders = [
        make_order(
            1,
            date(2026, 10, 1),
            "concluido",
            [
                OrderItem(product_id=1, product_name="A", quantity=1, unit_price=100.0),
                OrderItem(product_id=2, product_name="B", quantity=10, unit_price=5.0),
            ],
        )
    ]

    summary = summarize_sales(orders, top_n=1)

    assert len(summary.top_products) == 1
    assert summary.top_products[0].product_name == "A"


def test_summarize_sales_with_no_orders_returns_zeroed_summary():
    summary = summarize_sales([])

    assert summary.total_orders == 0
    assert summary.total_revenue == 0.0
    assert summary.average_ticket == 0.0
    assert summary.top_products == []


def test_find_low_stock_filters_and_sorts_by_deficit():
    products = [
        Product(id=1, name="OK", sku="A", stock=20, min_stock=5, unit_price=1.0),
        Product(id=2, name="Crítico", sku="B", stock=1, min_stock=10, unit_price=1.0),
        Product(id=3, name="No limite", sku="C", stock=5, min_stock=5, unit_price=1.0),
    ]

    low = find_low_stock(products)

    assert [p.name for p in low] == ["Crítico", "No limite"]


def test_sales_by_day_groups_and_excludes_cancelled():
    orders = [
        make_order(
            1,
            date(2026, 10, 1),
            "concluido",
            [OrderItem(product_id=1, product_name="A", quantity=1, unit_price=10.0)],
        ),
        make_order(
            2,
            date(2026, 10, 1),
            "concluido",
            [OrderItem(product_id=2, product_name="B", quantity=1, unit_price=5.0)],
        ),
        make_order(
            3,
            date(2026, 10, 2),
            "cancelado",
            [OrderItem(product_id=1, product_name="A", quantity=1, unit_price=999.0)],
        ),
    ]

    totals = sales_by_day(orders)

    assert totals == {"2026-10-01": 15.0}
