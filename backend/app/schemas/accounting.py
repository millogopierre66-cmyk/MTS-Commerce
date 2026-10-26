from pydantic import BaseModel, ConfigDict
from typing import List


# ==========================================================
# MOUVEMENT COMPTABLE
# ==========================================================

class AccountingMovementResponse(BaseModel):
    id: int
    movement_type: str
    amount: float
    description: str
    reference: str | None = None
    created_at: str

    model_config = ConfigDict(
        from_attributes=True
    )


# ==========================================================
# CHIFFRE D'AFFAIRES
# ==========================================================

class RevenueResponse(BaseModel):
    revenue: float


# ==========================================================
# NOMBRE DE VENTES
# ==========================================================

class SalesCountResponse(BaseModel):
    sales_count: int


# ==========================================================
# STOCK
# ==========================================================

class StockSummaryResponse(BaseModel):
    stock_value: float
    stock_quantity: float
    low_stock_count: int
    low_stock_products: List


# ==========================================================
# BÉNÉFICE / MARGE
# ==========================================================

class ProfitResponse(BaseModel):
    cost_of_goods: float
    gross_margin: float
    gross_margin_rate: float


# ==========================================================
# TABLEAU DE BORD COMPTABLE
# ==========================================================

class HistoricalCostCoverageResponse(BaseModel):
    total_sale_items: int
    known_historical_costs: int
    missing_historical_costs: int
    coverage_percent: float
    complete: bool


class DashboardResponse(BaseModel):
    revenue: float
    sales_count: int
    gross_margin: float
    cost_of_goods: float
    stock_value: float
    stock_quantity: float
    historical_cost_coverage: HistoricalCostCoverageResponse


# ==========================================================
# CHIFFRE D'AFFAIRES JOURNALIER
# ==========================================================

class DailyRevenueResponse(BaseModel):
    date: str
    revenue: float


# ==========================================================
# PRODUIT RENTABLE
# ==========================================================

class TopProductResponse(BaseModel):
    product_id: int
    product_name: str
    quantity_sold: float
    revenue: float
    profit: float | None


# ==========================================================
# COMPARAISON DE PÉRIODES
# ==========================================================

class PeriodComparisonResponse(BaseModel):
    current_revenue: float
    previous_revenue: float
    revenue_difference: float
    revenue_growth_percent: float

    current_sales_count: int
    previous_sales_count: int
    sales_difference: int


# ==========================================================
# ANALYSE FINANCIÈRE AVANCÉE
# ==========================================================

class FinancialAnalysisResponse(BaseModel):
    revenue: float
    sales_count: int
    cost_of_goods: float
    gross_margin: float
    margin_rate: float | None

    stock_value: float
    stock_quantity: float
    historical_cost_coverage: HistoricalCostCoverageResponse

    daily_revenue: List[DailyRevenueResponse]
    top_products: List[TopProductResponse]


# ==========================================================
# ANALYSE DÉCISIONNELLE
# ==========================================================

class DecisionAnalysisResponse(BaseModel):
    revenue: float
    sales_count: int
    cost_of_goods: float
    gross_margin: float
    margin_rate: float | None

    stock_value: float
    stock_quantity: float
    historical_cost_coverage: HistoricalCostCoverageResponse

    daily_revenue: List[DailyRevenueResponse]
    top_products: List[TopProductResponse]

    recommendations: List[str]

