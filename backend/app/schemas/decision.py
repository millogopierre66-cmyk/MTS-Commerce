from typing import List

from pydantic import BaseModel


# ==========================================================
# TENDANCE
# ==========================================================

class TrendResponse(BaseModel):
    direction: str
    percentage: float
    message: str


# ==========================================================
# ALERTE BUSINESS
# ==========================================================

class BusinessAlertResponse(BaseModel):
    level: str
    category: str
    message: str


# ==========================================================
# RECOMMANDATION
# ==========================================================

class RecommendationResponse(BaseModel):
    priority: str
    category: str
    message: str


# ==========================================================
# ANALYSE DÉCISIONNELLE
# ==========================================================

class DecisionAnalysisResponse(BaseModel):

    revenue: float
    sales_count: int
    average_sale: float

    gross_profit: float
    profit_margin: float

    stock_value: float
    stock_quantity: float

    revenue_trend: TrendResponse

    alerts: List[BusinessAlertResponse]

    recommendations: List[RecommendationResponse]