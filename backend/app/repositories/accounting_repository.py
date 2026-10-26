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
            .filter(Sale.status == "completed")
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
            .filter(Sale.status == "completed")
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
                Sale.status == "completed",
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
                Sale.status == "completed",
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

        query = query.filter(Sale.status == "completed")

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
            SaleItem.subtotal
            - (
                SaleItem.quantity
                * SaleItem.purchase_unit_price
            )
        )

        rows = (
            db.query(
                Product.id.label("product_id"),
                Product.name.label("product_name"),

                func.coalesce(
                    func.sum(SaleItem.quantity),
                    0
                ).label("quantity_sold"),

                func.coalesce(
                    func.sum(SaleItem.subtotal),
                    0
                ).label("revenue"),

                func.count(
                    SaleItem.id
                ).label("total_sale_lines"),

                func.count(
                    SaleItem.purchase_unit_price
                ).label("known_cost_lines"),

                func.coalesce(
                    func.sum(profit_expression),
                    0
                ).label("profit_on_known_cost_lines")
            )
            .join(
                SaleItem,
                SaleItem.product_id == Product.id
            )
            .join(Sale, Sale.id == SaleItem.sale_id)
            .filter(Sale.status == "completed")
            .group_by(
                Product.id,
                Product.name
            )
            .order_by(
                func.sum(SaleItem.quantity).desc()
            )
            .limit(limit)
            .all()
        )

        return [
            {
                "product_id": row.product_id,
                "product_name": row.product_name,
                "quantity_sold": float(row.quantity_sold or 0),
                "revenue": float(row.revenue or 0),

                # Ne pas pr?senter un b?n?fice partiel comme complet.
                "profit": (
                    None
                    if int(row.known_cost_lines or 0)
                    < int(row.total_sale_lines or 0)
                    else float(row.profit_on_known_cost_lines or 0)
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
            SaleItem.subtotal
            - (
                SaleItem.quantity
                * SaleItem.purchase_unit_price
            )
        )

        rows = (
            db.query(
                Product.id.label("product_id"),
                Product.name.label("product_name"),

                func.coalesce(
                    func.sum(SaleItem.quantity),
                    0
                ).label("quantity_sold"),

                func.coalesce(
                    func.sum(SaleItem.subtotal),
                    0
                ).label("revenue"),

                func.sum(
                    profit_expression
                ).label("profit")
            )
            .join(
                SaleItem,
                SaleItem.product_id == Product.id
            )
            .join(Sale, Sale.id == SaleItem.sale_id)
            .filter(Sale.status == "completed")
            .group_by(
                Product.id,
                Product.name
            )

            # Toutes les lignes doivent avoir un co?t historique.
            .having(
                func.count(SaleItem.purchase_unit_price)
                == func.count(SaleItem.id)
            )

            .order_by(
                func.sum(profit_expression).desc()
            )
            .limit(limit)
            .all()
        )

        return [
            {
                "product_id": row.product_id,
                "product_name": row.product_name,
                "quantity_sold": float(row.quantity_sold or 0),
                "revenue": float(row.revenue or 0),
                "profit": float(row.profit or 0)
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
            .join(Sale, Sale.id == SaleItem.sale_id)
            .filter(
                Sale.status == "completed",
                SaleItem.product_id == product_id
            )
            .first()
        )

    # ==========================================================
    # MARGE BRUTE
    # ==========================================================


    @staticmethod
    def get_gross_margin(db: Session) -> float:
        # La marge historique n'est calcul?e que lorsque le prix d'achat
        # au moment de la vente est connu.
        result = (
            db.query(
                func.coalesce(
                    func.sum(
                        SaleItem.subtotal
                        - (
                            SaleItem.quantity
                            * SaleItem.purchase_unit_price
                        )
                    ),
                    0,
                )
            )
            .join(Sale, Sale.id == SaleItem.sale_id)
            .filter(
                Sale.status == "completed",
                SaleItem.purchase_unit_price.is_not(None),
            )
            .scalar()
        )

        return float(result or 0)
    # ==========================================================
    # COÛT DES MARCHANDISES VENDUES
    # ==========================================================


    @staticmethod
    def get_cost_of_goods_sold(db: Session) -> float:
        # Ne pas inventer de co?t pour les anciennes lignes dont le co?t
        # historique est inconnu.
        result = (
            db.query(
                func.coalesce(
                    func.sum(
                        SaleItem.quantity
                        * SaleItem.purchase_unit_price
                    ),
                    0,
                )
            )
            .join(Sale, Sale.id == SaleItem.sale_id)
            .filter(
                Sale.status == "completed",
                SaleItem.purchase_unit_price.is_not(None),
            )
            .scalar()
        )

        return float(result or 0)

    @staticmethod
    def get_historical_cost_coverage(db: Session) -> dict:
        # La couverture concerne uniquement les lignes des ventes termin?es.
        total = (
            db.query(func.count(SaleItem.id))
            .join(Sale, Sale.id == SaleItem.sale_id)
            .filter(Sale.status == "completed")
            .scalar()
            or 0
        )

        known = (
            db.query(func.count(SaleItem.id))
            .join(Sale, Sale.id == SaleItem.sale_id)
            .filter(
                Sale.status == "completed",
                SaleItem.purchase_unit_price.is_not(None),
            )
            .scalar()
            or 0
        )

        total = int(total)
        known = int(known)
        missing = total - known
        coverage_percent = round(known * 100 / total, 2) if total else 0.0

        return {
            "total_sale_items": total,
            "known_historical_costs": known,
            "missing_historical_costs": missing,
            "coverage_percent": coverage_percent,
            "complete": total > 0 and missing == 0,
        }
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