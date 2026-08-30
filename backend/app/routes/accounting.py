from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.security.auth import (
    get_db,
    get_current_admin
)

from app.services.accounting_service import AccountingService

from app.schemas.accounting import (
    RevenueResponse,
    SalesCountResponse,
    StockSummaryResponse,
    ProfitResponse,
    DashboardResponse,
    DailyRevenueResponse,
    TopProductResponse,
    PeriodComparisonResponse,
    FinancialAnalysisResponse,
    DecisionAnalysisResponse,
)


# ==========================================================
# ROUTER
# ==========================================================

router = APIRouter(
    prefix="/accounting",
    tags=["Comptabilité"]
)


# ==========================================================
# TABLEAU DE BORD COMPTABLE
# ==========================================================

@router.get(
    "/dashboard",
    response_model=DashboardResponse
)
def get_dashboard(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin)
):
    return AccountingService.get_dashboard(db)


# ==========================================================
# CHIFFRE D'AFFAIRES
# ==========================================================

@router.get(
    "/revenue",
    response_model=RevenueResponse
)
def get_revenue(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin)
):
    return AccountingService.get_revenue(db)


# ==========================================================
# NOMBRE DE VENTES
# ==========================================================

@router.get(
    "/sales-count",
    response_model=SalesCountResponse
)
def get_sales_count(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin)
):
    return AccountingService.get_sales_count(db)


# ==========================================================
# MARGE
# ==========================================================

@router.get(
    "/margin"
)
def get_margin(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin)
):
    return AccountingService.get_gross_margin(db)


# ==========================================================
# COÛT DES MARCHANDISES
# ==========================================================

@router.get(
    "/cost-of-goods"
)
def get_cost_of_goods(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin)
):
    return AccountingService.get_cost_of_goods(db)


# ==========================================================
# STOCK
# ==========================================================

@router.get(
    "/stock"
)
def get_stock(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin)
):
    return AccountingService.get_stock_summary(db)


# ==========================================================
# PRODUITS LES PLUS VENDUS
# ==========================================================

@router.get(
    "/top-products",
    response_model=list[TopProductResponse]
)
def get_top_products(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin)
):
    return AccountingService.get_top_selling_products(db)


# ==========================================================
# STOCK FAIBLE
# ==========================================================

@router.get(
    "/low-stock"
)
def get_low_stock(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin)
):
    return AccountingService.get_low_stock_products(db)


# ==========================================================
# RÉSUMÉ FINANCIER
# ==========================================================

@router.get(
    "/financial-summary"
)
def get_financial_summary(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin)
):
    return AccountingService.get_financial_summary(db)


# ==========================================================
# RÉSUMÉ DU STOCK
# ==========================================================

@router.get(
    "/stock-summary"
)
def get_stock_summary(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin)
):
    return AccountingService.get_stock_summary(db)


# ==========================================================
# SYNTHÈSE DE L'ACTIVITÉ
# ==========================================================

@router.get(
    "/summary"
)
def get_business_summary(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin)
):
    return AccountingService.get_business_summary(db)


# ==========================================================
# ANALYSE FINANCIÈRE AVANCÉE
# ==========================================================

@router.get(
    "/financial-analysis",
    response_model=FinancialAnalysisResponse
)
def get_financial_analysis(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin)
):
    return AccountingService.get_financial_analysis(db)


# ==========================================================
# ANALYSE DÉCISIONNELLE
# ==========================================================

@router.get(
    "/decision-analysis",
    response_model=DecisionAnalysisResponse
)
def get_decision_analysis(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin)
):
    return AccountingService.get_decision_analysis(db)