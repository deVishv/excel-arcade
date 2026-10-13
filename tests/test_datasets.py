import datetime as dt

from excel_drills.content.datasets import (ORDERS, PRICES, PRODUCTS, add_workdays, orders_rows, serial,
                                           workday_count, xl_round)


def test_xl_round_rounds_halves_away_from_zero():
    assert xl_round(2.5, 0) == 3 and xl_round(46.45, 1) == 46.5 and xl_round(-1.25, 1) == -1.3
    assert xl_round(1234.5, -2) == 1200


def test_serial_matches_excel():
    assert serial(dt.date(2026, 1, 5)) == 46027
    assert serial(dt.date(1900, 3, 1)) == 61


def test_orders_are_consistent():
    assert len(ORDERS) == 20 and len({o.id for o in ORDERS}) == 20
    assert all(o.revenue == o.units * PRICES[o.product] for o in ORDERS)
    assert len({o.date for o in ORDERS}) == 20                    # unique dates: SORTBY by date is unambiguous
    assert orders_rows()[0][:3] == ["O-101", dt.date(2026, 1, 5), "East"]


def test_products_unique():
    assert len(PRODUCTS) == 15 and len({p.id for p in PRODUCTS}) == 15 and len({p.name for p in PRODUCTS}) == 15


def test_workday_helpers():
    assert workday_count(dt.date(2026, 3, 16), dt.date(2026, 3, 20)) == 5        # Mon..Fri
    assert workday_count(dt.date(2026, 3, 15), dt.date(2026, 3, 15)) == 0        # a Sunday
    assert add_workdays(dt.date(2026, 3, 13), 1) == dt.date(2026, 3, 16)         # Fri + 1 workday = Mon


from excel_drills.content.f6_dates import add_months, end_of_month, full_months, full_years, weekday_excel


def test_date_helpers_match_excel_semantics():
    assert weekday_excel(dt.date(2026, 3, 15)) == 1                       # Sunday
    assert add_months(dt.date(2026, 1, 31), 1) == dt.date(2026, 2, 28)    # EDATE clamps to month end
    assert end_of_month(dt.date(2026, 2, 10)) == dt.date(2026, 2, 28)
    assert full_years(dt.date(1990, 8, 20), dt.date(2026, 3, 15)) == 35
    assert full_months(dt.date(2026, 3, 15), dt.date(2026, 5, 1)) == 1
