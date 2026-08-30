from sqlalchemy.orm import Session

from app.repositories.product_repository import ProductRepository
from app.repositories.stock_repository import StockRepository


class DashboardRepository:

    # ==========================================================
    # NOMBRE TOTAL DE PRODUITS
    # ==========================================================

    @staticmethod
    def count_products(db: Session) -> int:

        return len(
            ProductRepository.get_all(db)
        )

    # ==========================================================
    # NOMBRE TOTAL DE MOUVEMENTS DE STOCK
    # ==========================================================

    @staticmethod
    def count_movements(db: Session) -> int:

        return StockRepository.total_movements(db)

    # ==========================================================
    # PRODUITS EN RUPTURE
    # ==========================================================

    @staticmethod
    def count_out_of_stock(db: Session) -> int:

        return len(
            StockRepository.out_of_stock(db)
        )

    # ==========================================================
    # PRODUITS EN STOCK FAIBLE
    # ==========================================================

    @staticmethod
    def count_low_stock(db: Session) -> int:

        return len(
            StockRepository.low_stock(db)
        )

    # ==========================================================
    # VALEUR TOTALE DU STOCK
    # ==========================================================

    @staticmethod
    def get_stock_value(db: Session):

        return StockRepository.total_stock_value(db)

