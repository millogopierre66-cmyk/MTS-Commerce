from app.schemas.accounting import (
    DashboardResponse,
    FinancialAnalysisResponse,
    DecisionAnalysisResponse,
)
from app.services.accounting_service import AccountingService


def test_financial_summary_reports_incomplete_historical_costs(
    db, accounting_data
):
    summary = AccountingService.get_financial_summary(db)

    assert summary["revenue"] == 3500.0
    assert summary["cost_of_goods"] == 1800.0
    assert summary["gross_margin"] == 1200.0
    assert summary["gross_margin_rate"] is None

    coverage = summary["historical_cost_coverage"]
    assert coverage["coverage_percent"] == 66.67
    assert coverage["missing_historical_costs"] == 1
    assert coverage["complete"] is False


def test_dashboard_and_financial_analysis_match_schemas(
    db, accounting_data
):
    dashboard = AccountingService.get_dashboard(db)
    DashboardResponse.model_validate(dashboard)

    assert dashboard["historical_cost_coverage"]["complete"] is False

    analysis = AccountingService.get_financial_analysis(db)
    FinancialAnalysisResponse.model_validate(analysis)

    assert analysis["margin_rate"] is None
    assert analysis["historical_cost_coverage"]["complete"] is False

    incomplete_id = accounting_data["product_incomplete"].id
    assert all(
        product["product_id"] != incomplete_id
        for product in analysis["top_products"]
    )


def test_decision_analysis_warns_about_incomplete_margin(
    db, accounting_data
):
    decision = AccountingService.get_decision_analysis(db)
    DecisionAnalysisResponse.model_validate(decision)

    assert decision["margin_rate"] is None
    assert decision["historical_cost_coverage"]["complete"] is False

    assert any(
        "Marge non definitive" in recommendation
        for recommendation in decision["recommendations"]
    )
