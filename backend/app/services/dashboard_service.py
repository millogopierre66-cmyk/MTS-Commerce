from sqlalchemy.orm import Session

from app.repositories.dashboard_repository import (
    DashboardRepository
)
from app.repositories.sale_repository import (
    SaleRepository
)
from app.repositories.accounting_repository import (
    AccountingRepository
)


class DashboardService:

    # ==========================================================
    # TABLEAU DE BORD PRINCIPAL
    # ==========================================================

    @staticmethod
    def dashboard(db: Session):

        # ======================================================
        # PRODUITS
        # ======================================================

        total_products = (
            DashboardRepository.count_products(db)
        )

        # ======================================================
        # VENTES
        # ======================================================

        total_sales = (
            SaleRepository.count_sales(db)
        )

        total_revenue = (
            AccountingRepository.get_total_revenue(db)
        )

        # ======================================================
        # STOCK
        # ======================================================

        stock_value = (
            DashboardRepository.get_stock_value(db)
        )

        out_of_stock = (
            DashboardRepository.count_out_of_stock(db)
        )

        low_stock = (
            DashboardRepository.count_low_stock(db)
        )

        total_movements = (
            DashboardRepository.count_movements(db)
        )

        # ======================================================
        # RESULTAT
        # ======================================================

        return {
            "total_products": int(total_products or 0),

            "total_sales": int(total_sales or 0),

            "total_revenue": float(
                total_revenue or 0
            ),

            "stock_value": float(
                stock_value or 0
            ),

            "out_of_stock": int(
                out_of_stock or 0
            ),

            "low_stock": int(
                low_stock or 0
            ),

            "total_movements": int(
                total_movements or 0
            )
        }