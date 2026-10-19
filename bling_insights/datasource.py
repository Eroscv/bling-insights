"""Fontes de dados: interface comum + implementação real (Bling API) e mock (demo)."""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from datetime import date, datetime
from pathlib import Path

import requests

from .models import Order, OrderItem, Product

SAMPLE_DIR = Path(__file__).resolve().parent.parent / "data" / "sample"


class DataSource(ABC):
    """Contrato que qualquer fonte de dados de vendas/estoque deve implementar."""

    @abstractmethod
    def get_products(self) -> list[Product]:
        ...

    @abstractmethod
    def get_orders(self, start: date, end: date) -> list[Order]:
        ...


class MockDataSource(DataSource):
    """Lê dados de exemplo de arquivos JSON locais. Usado no modo --demo."""

    def get_products(self) -> list[Product]:
        raw = json.loads((SAMPLE_DIR / "products.json").read_text(encoding="utf-8"))
        return [
            Product(
                id=p["id"],
                name=p["name"],
                sku=p["sku"],
                stock=p["stock"],
                min_stock=p["min_stock"],
                unit_price=p["unit_price"],
            )
            for p in raw
        ]

    def get_orders(self, start: date, end: date) -> list[Order]:
        raw = json.loads((SAMPLE_DIR / "orders.json").read_text(encoding="utf-8"))
        orders = []
        for o in raw:
            order_date = datetime.strptime(o["date"], "%Y-%m-%d").date()
            if not (start <= order_date <= end):
                continue
            items = [
                OrderItem(
                    product_id=i["product_id"],
                    product_name=i["product_name"],
                    quantity=i["quantity"],
                    unit_price=i["unit_price"],
                )
                for i in o["items"]
            ]
            orders.append(Order(id=o["id"], date=order_date, status=o["status"], items=items))
        return orders


class BlingAPISource(DataSource):
    """
    Integração real com a API v3 do Bling (https://developer.bling.com.br).

    Requer um access_token OAuth2 válido (fluxo de autorização do Bling).
    Veja README.md para como obter o token.
    """

    BASE_URL = "https://www.bling.com.br/Api/v3"

    def __init__(self, access_token: str, timeout: int = 15) -> None:
        self._token = access_token
        self._timeout = timeout

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self._token}",
            "Accept": "application/json",
        }

    def get_products(self) -> list[Product]:
        resp = requests.get(
            f"{self.BASE_URL}/produtos",
            headers=self._headers(),
            timeout=self._timeout,
        )
        resp.raise_for_status()
        data = resp.json().get("data", [])
        return [
            Product(
                id=p["id"],
                name=p["nome"],
                sku=p.get("codigo", ""),
                stock=int(p.get("estoque", {}).get("saldoVirtualTotal", 0)),
                min_stock=int(p.get("estoque", {}).get("minimo", 0)),
                unit_price=float(p.get("preco", 0)),
            )
            for p in data
        ]

    def get_orders(self, start: date, end: date) -> list[Order]:
        resp = requests.get(
            f"{self.BASE_URL}/pedidos/vendas",
            headers=self._headers(),
            params={
                "dataInicial": start.isoformat(),
                "dataFinal": end.isoformat(),
            },
            timeout=self._timeout,
        )
        resp.raise_for_status()
        data = resp.json().get("data", [])
        orders = []
        for o in data:
            items = [
                OrderItem(
                    product_id=i["produto"]["id"],
                    product_name=i["descricao"],
                    quantity=int(i["quantidade"]),
                    unit_price=float(i["valor"]),
                )
                for i in o.get("itens", [])
            ]
            orders.append(
                Order(
                    id=o["id"],
                    date=datetime.strptime(o["data"], "%Y-%m-%d").date(),
                    status=o.get("situacao", {}).get("valor", "desconhecido"),
                    items=items,
                )
            )
        return orders
