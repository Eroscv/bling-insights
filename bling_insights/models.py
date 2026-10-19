"""Modelos de dados usados em todo o pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class Product:
    id: int
    name: str
    sku: str
    stock: int
    min_stock: int
    unit_price: float

    @property
    def is_low_stock(self) -> bool:
        return self.stock <= self.min_stock


@dataclass(frozen=True)
class OrderItem:
    product_id: int
    product_name: str
    quantity: int
    unit_price: float

    @property
    def total(self) -> float:
        return self.quantity * self.unit_price


@dataclass(frozen=True)
class Order:
    id: int
    date: date
    status: str
    items: list[OrderItem]

    @property
    def total(self) -> float:
        return sum(item.total for item in self.items)
