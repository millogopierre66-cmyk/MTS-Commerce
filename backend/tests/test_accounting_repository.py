import pytest

from app.repositories.accounting_repository import AccountingRepository


def test_revenue_and_sales_count_exclude_cancelled_sales(
    db, accounting_data
):
    assert AccountingRepository.get_total_revenue(db) == pytest.approx(3500.0)
    assert AccountingRepository.get_total_sales(db) == 2


def test_historical_costs_and_coverage(db, accounting_data):
    assert AccountingRepository.get_cost_of_goods_sold(db) == pytest.approx(
        1800.0
    )
    assert AccountingRepository.get_gross_margin(db) == pytest.approx(
        1200.0
    )

    coverage = AccountingRepository.get_historical_cost_coverage(db)

    assert coverage == {
        "total_sale_items": 3,
        "known_historical_costs": 2,
        "missing_historical_costs": 1,
        "coverage_percent": 66.67,
        "complete": False,
    }


def test_top_products_does_not_report_partial_profit_as_complete(
    db, accounting_data
):
    data = accounting_data
    rows = AccountingRepository.get_top_products(db, limit=10)
    by_id = {row["product_id"]: row for row in rows}

    incomplete = by_id[data["product_incomplete"].id]
    complete = by_id[data["product_complete"].id]

    assert incomplete["quantity_sold"] == pytest.approx(3.0)
    assert incomplete["revenue"] == pytest.approx(2500.0)
    assert incomplete["profit"] is None

    assert complete["quantity_sold"] == pytest.approx(1.0)
    assert complete["revenue"] == pytest.approx(1000.0)
    assert complete["profit"] == pytest.approx(400.0)


def test_top_profitable_products_only_contains_complete_costs(
    db, accounting_data
):
    data = accounting_data
    rows = AccountingRepository.get_top_profitable_products(db, limit=10)
    ids = {row["product_id"] for row in rows}

    assert data["product_complete"].id in ids
    assert data["product_incomplete"].id not in ids
    assert all(row["profit"] is not None for row in rows)
