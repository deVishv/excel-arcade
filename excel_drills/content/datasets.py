"""Shared practice data. Expected answers are computed from these lists, and Excel re-checks every one."""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

EXCEL_EPOCH = dt.date(1899, 12, 30)


def xl_round(value: float, digits: int) -> float:
    """Excel's ROUND (halves go away from zero), unlike Python's round (halves go to even)."""
    return float(Decimal(repr(value)).quantize(Decimal(1).scaleb(-digits), rounding=ROUND_HALF_UP))


def serial(day: dt.date) -> int:
    """Excel's date serial number (1900 date system)."""
    return (day - EXCEL_EPOCH).days


def workday_count(start: dt.date, end: dt.date) -> int:
    """Like NETWORKDAYS(start, end) with no holidays (both ends inclusive)."""
    days = (end - start).days
    return sum(1 for k in range(days + 1) if (start + dt.timedelta(k)).weekday() < 5)


def add_workdays(start: dt.date, n: int) -> dt.date:
    """Like WORKDAY(start, n) with no holidays, for n >= 1."""
    day, left = start, n
    while left:
        day += dt.timedelta(1)
        if day.weekday() < 5:
            left -= 1
    return day


PRICES = {"Widget": 30, "Gadget": 60, "Gizmo": 50}


@dataclass(frozen=True)
class Order:
    id: str
    date: dt.date
    region: str
    rep: str
    product: str
    units: int
    revenue: int


_ORDERS = (
    ("O-101", (2026, 1, 5), "East", "Kim", "Widget", 40),
    ("O-102", (2026, 1, 9), "West", "Lee", "Gadget", 15),
    ("O-103", (2026, 1, 14), "North", "Ava", "Widget", 55),
    ("O-104", (2026, 1, 20), "East", "Kim", "Gizmo", 20),
    ("O-105", (2026, 2, 2), "South", "Raj", "Gadget", 60),
    ("O-106", (2026, 2, 7), "West", "Lee", "Widget", 35),
    ("O-107", (2026, 2, 11), "East", "Ava", "Gadget", 25),
    ("O-108", (2026, 2, 19), "North", "Raj", "Gizmo", 45),
    ("O-109", (2026, 3, 3), "West", "Kim", "Gizmo", 10),
    ("O-110", (2026, 3, 8), "East", "Lee", "Widget", 70),
    ("O-111", (2026, 3, 15), "South", "Ava", "Widget", 30),
    ("O-112", (2026, 3, 22), "North", "Kim", "Gadget", 50),
    ("O-113", (2026, 4, 1), "East", "Raj", "Gizmo", 65),
    ("O-114", (2026, 4, 6), "West", "Ava", "Gadget", 20),
    ("O-115", (2026, 4, 13), "South", "Lee", "Gizmo", 15),
    ("O-116", (2026, 4, 21), "East", "Kim", "Widget", 50),
    ("O-117", (2026, 5, 4), "North", "Lee", "Widget", 25),
    ("O-118", (2026, 5, 12), "West", "Raj", "Gadget", 40),
    ("O-119", (2026, 5, 19), "South", "Kim", "Gizmo", 35),
    ("O-120", (2026, 5, 27), "East", "Ava", "Gadget", 55),
)
ORDERS = tuple(Order(i, dt.date(*d), region, rep, product, units, units * PRICES[product])
               for i, d, region, rep, product, units in _ORDERS)
ORDER_HEADER = ("Order", "Date", "Region", "Rep", "Product", "Units", "Revenue")


def orders_rows() -> list[list]:
    return [[o.id, o.date, o.region, o.rep, o.product, o.units, o.revenue] for o in ORDERS]


@dataclass(frozen=True)
class Product:
    id: str
    name: str
    category: str
    price: float
    stock: int


PRODUCTS = tuple(Product(*p) for p in (
    ("P-01", "Apple", "Fruit", 0.5, 120), ("P-02", "Banana", "Fruit", 0.25, 200),
    ("P-03", "Carrot", "Veg", 0.3, 80), ("P-04", "Dragonfruit", "Fruit", 3.5, 12),
    ("P-05", "Eggplant", "Veg", 1.2, 30), ("P-06", "Fig", "Fruit", 2.0, 25),
    ("P-07", "Garlic", "Veg", 0.8, 60), ("P-08", "Honeydew", "Fruit", 4.0, 8),
    ("P-09", "Iceberg", "Veg", 1.5, 40), ("P-10", "Jalapeno", "Veg", 0.2, 150),
    ("P-11", "Kiwi", "Fruit", 0.6, 90), ("P-12", "Leek", "Veg", 1.1, 35),
    ("P-13", "Mango", "Fruit", 1.8, 45), ("P-14", "Nectarine", "Fruit", 0.9, 70),
    ("P-15", "Okra", "Veg", 2.2, 18),
))
PRODUCT_HEADER = ("ID", "Product", "Category", "Price", "Stock")


def products_rows() -> list[list]:
    return [[p.id, p.name, p.category, p.price, p.stock] for p in PRODUCTS]
