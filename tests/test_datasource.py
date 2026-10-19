from datetime import date

from bling_insights.datasource import MockDataSource


def test_mock_products_are_loaded_from_fixture():
    source = MockDataSource()
    products = source.get_products()

    assert len(products) > 0
    assert all(p.sku for p in products)


def test_mock_orders_respects_date_range():
    source = MockDataSource()

    all_orders = source.get_orders(date(2000, 1, 1), date(2100, 1, 1))
    narrow = source.get_orders(date(2026, 10, 1), date(2026, 10, 1))

    assert len(narrow) <= len(all_orders)
    assert all(o.date == date(2026, 10, 1) for o in narrow)
