from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.sale import Sale
from app.models.sale_item import SaleItem
from app.models.product import Product


class AccountingRepository:

    # ==========================================================
    # CHIFFRE D'AFFAIRES TOTAL
    # ==========================================================

    @staticmethod
    def get_total_revenue(db: Session) -> float:

        result = (
            db.query(
                func.coalesce(
                    func.sum(Sale.total),
                    0
                )
            )
            .scalar()
        )

        return float(result or 0)

    # ==========================================================
    # NOMBRE TOTAL DE VENTES
    # ==========================================================

    @staticmethod
    def get_total_sales(db: Session) -> int:

        result = (
            db.query(
                func.count(Sale.id)
            )
            .scalar()
        )

        return int(result or 0)

    # ==========================================================
    # COMPATIBILITÉ AVEC LE SERVICE
    # ==========================================================

    @staticmethod
    def get_sales_count(db: Session) -> int:
        """
        Alias de get_total_sales().
        Permet de conserver la compatibilité avec
        AccountingService.
        """

        return AccountingRepository.get_total_sales(db)

    # ==========================================================
    # CHIFFRE D'AFFAIRES SUR UNE PÉRIODE
    # ==========================================================

    @staticmethod
    def get_revenue_between(
        db: Session,
        start_date: datetime,
        end_date: datetime
    ) -> float:

        result = (
            db.query(
                func.coalesce(
                    func.sum(Sale.total),
                    0
                )
            )
            .filter(
                Sale.created_at >= start_date,
                Sale.created_at <= end_date
            )
            .scalar()
        )

        return float(result or 0)

    # ==========================================================
    # NOMBRE DE VENTES SUR UNE PÉRIODE
    # ==========================================================

    @staticmethod
    def get_sales_count_between(
        db: Session,
        start_date: datetime,
        end_date: datetime
    ) -> int:

        result = (
            db.query(
                func.count(Sale.id)
            )
            .filter(
                Sale.created_at >= start_date,
                Sale.created_at <= end_date
            )
            .scalar()
        )

        return int(result or 0)

    # ==========================================================
    # CHIFFRE D'AFFAIRES JOURNALIER
    # ==========================================================

    @staticmethod
    def get_daily_revenue(
        db: Session,
        start_date: datetime | None = None,
        end_date: datetime | None = None
    ):

        query = (
            db.query(
                func.date(
                    Sale.created_at
                ).label("date"),

                func.coalesce(
                    func.sum(Sale.total),
                    0
                ).label("revenue")
            )
        )

        if start_date is not None:
            query = query.filter(
                Sale.created_at >= start_date
            )

        if end_date is not None:
            query = query.filter(
                Sale.created_at <= end_date
            )

        rows = (
            query
            .group_by(
                func.date(Sale.created_at)
            )
            .order_by(
                func.date(Sale.created_at)
            )
            .all()
        )

        return [
            {
                "date": str(row.date),
                "revenue": float(row.revenue or 0)
            }
            for row in rows
        ]

    # ==========================================================
    # PRODUITS LES PLUS VENDUS
    # ==========================================================

    @staticmethod
    def get_top_products(
        db: Session,
        limit: int = 10
    ):

        profit_expression = (
            SaleItem.quantity
            * (
                Product.selling_price
                - Product.purchase_price
            )
        )

        rows = (
            db.query(
                Product.id.label("product_id"),

                Product.name.label("product_name"),

                func.coalesce(
                    func.sum(
                        SaleItem.quantity
                    ),
                    0
                ).label("quantity_sold"),

                func.coalesce(
                    func.sum(
                        SaleItem.subtotal
                    ),
                    0
                ).label("revenue"),

                func.coalesce(
                    func.sum(
                        profit_expression
                    ),
                    0
                ).label("profit")
            )
            .join(
                SaleItem,
                SaleItem.product_id == Product.id
            )
            .group_by(
                Product.id,
                Product.name
            )
            .order_by(
                func.sum(
                    SaleItem.quantity
                ).desc()
            )
            .limit(limit)
            .all()
        )

        return [
            {
                "product_id": row.product_id,
                "product_name": row.product_name,
                "quantity_sold": float(
                    row.quantity_sold or 0
                ),
                "revenue": float(
                    row.revenue or 0
                ),
                "profit": float(
                    row.profit or 0
                )
            }
            for row in rows
        ]
    # ==========================================================
    # PRODUITS LES PLUS RENTABLES
    # ==========================================================

    @staticmethod
    def get_top_profitable_products(
        db: Session,
        limit: int = 10
    ):

        profit_expression = (
            SaleItem.quantity
            * (
                Product.selling_price
                - Product.purchase_price
            )
        )

        rows = (
            db.query(
                Product.id.label(
                    "product_id"
                ),

                Product.name.label(
                    "product_name"
                ),

                func.coalesce(
                    func.sum(
                        SaleItem.quantity
                    ),
                    0
                ).label(
                    "quantity_sold"
                ),

                func.coalesce(
                    func.sum(
                        SaleItem.subtotal
                    ),
                    0
                ).label(
                    "revenue"
                ),

                func.coalesce(
                    func.sum(
                        profit_expression
                    ),
                    0
                ).label(
                    "profit"
                )
            )
            .join(
                SaleItem,
                SaleItem.product_id == Product.id
            )
            .group_by(
                Product.id,
                Product.name
            )
            .order_by(
                func.sum(
                    profit_expression
                ).desc()
            )
            .limit(limit)
            .all()
        )

        return [
            {
                "product_id": row.product_id,
                "product_name": row.product_name,
                "quantity_sold": float(
                    row.quantity_sold or 0
                ),
                "revenue": float(
                    row.revenue or 0
                ),
                "profit": float(
                    row.profit or 0
                )
            }
            for row in rows
        ]

    # ==========================================================
    # VENTES PAR PRODUIT
    # ==========================================================

    @staticmethod
    def get_product_sales(
        db: Session,
        product_id: int
    ):

        return (
            db.query(
                func.coalesce(
                    func.sum(
                        SaleItem.quantity
                    ),
                    0
                ).label(
                    "quantity_sold"
                ),

                func.coalesce(
                    func.sum(
                        SaleItem.subtotal
                    ),
                    0
                ).label(
                    "revenue"
                )
            )
            .filter(
                SaleItem.product_id == product_id
            )
            .first()
        )

    # ==========================================================
    # MARGE BRUTE
    # ==========================================================

    @staticmethod
    def get_gross_margin(
        db: Session
    ) -> float:

        result = (
            db.query(
                func.coalesce(
                    func.sum(
                        SaleItem.subtotal
                        - (
                            SaleItem.quantity
                            * Product.purchase_price
                        )
                    ),
                    0
                )
            )
            .join(
                Product,
                Product.id == SaleItem.product_id
            )
            .scalar()
        )

        return float(result or 0)

    # ==========================================================
    # COÛT DES MARCHANDISES VENDUES
    # ==========================================================

    @staticmethod
    def get_cost_of_goods_sold(
        db: Session
    ) -> float:

        result = (
            db.query(
                func.coalesce(
                    func.sum(
                        SaleItem.quantity
                        * Product.purchase_price
                    ),
                    0
                )
            )
            .join(
                Product,
                Product.id == SaleItem.product_id
            )
            .scalar()
        )

        return float(result or 0)

    # ==========================================================
    # VALEUR DU STOCK
    # ==========================================================

    @staticmethod
    def get_stock_value(
        db: Session
    ) -> float:

        result = (
            db.query(
                func.coalesce(
                    func.sum(
                        Product.quantity
                        * Product.purchase_price
                    ),
                    0
                )
            )
            .filter(
                Product.active.is_(True)
            )
            .scalar()
        )

        return float(result or 0)

    # ==========================================================
    # QUANTITÉ TOTALE EN STOCK
    # ==========================================================

    @staticmethod
    def get_total_stock_quantity(
        db: Session
    ) -> float:

        result = (
            db.query(
                func.coalesce(
                    func.sum(
                        Product.quantity
                    ),
                    0
                )
            )
            .filter(
                Product.active.is_(True)
            )
            .scalar()
        )

        return float(result or 0)

    # ==========================================================
    # PRODUITS EN STOCK FAIBLE
    # ==========================================================

    @staticmethod
    def get_low_stock_products(
        db: Session
    ):

        products = (
            db.query(Product)
            .filter(
                Product.active.is_(True),
                Product.quantity
                <= Product.minimum_stock
            )
            .order_by(
                Product.quantity.asc()
            )
            .all()
        )

        return [
            {
                "id": product.id,
                "name": product.name,
                "quantity": float(
                    product.quantity or 0
                ),
                "minimum_stock": float(
                    product.minimum_stock or 0
                ),
                "purchase_price": float(
                    product.purchase_price or 0
                ),
                "selling_price": float(
                    product.selling_price or 0
                )
            }
            for product in products
        ]