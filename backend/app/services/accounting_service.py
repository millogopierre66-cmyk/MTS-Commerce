from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.repositories.accounting_repository import (
    AccountingRepository
)


class AccountingService:
    """
    Service métier de la comptabilité
    et du tableau de bord décisionnel
    de MTS Commerce.
    """

    # ==========================================================
    # TABLEAU DE BORD GLOBAL
    # ==========================================================

    @staticmethod
    def get_dashboard(db: Session):
        revenue = AccountingRepository.get_total_revenue(db)
        sales_count = AccountingRepository.get_sales_count(db)
        gross_margin = AccountingRepository.get_gross_margin(db)
        cost_of_goods = AccountingRepository.get_cost_of_goods_sold(db)
        stock_value = AccountingRepository.get_stock_value(db)
        stock_quantity = AccountingRepository.get_total_stock_quantity(db)
        cost_coverage = AccountingRepository.get_historical_cost_coverage(db)

        return {
            "revenue": float(revenue or 0),
            "sales_count": int(sales_count or 0),
            "gross_margin": float(gross_margin or 0),
            "cost_of_goods": float(cost_of_goods or 0),
            "stock_value": float(stock_value or 0),
            "stock_quantity": float(stock_quantity or 0),
            "historical_cost_coverage": cost_coverage,
        }

    # ==========================================================
    # CHIFFRE D'AFFAIRES
    # ==========================================================

    @staticmethod
    def get_revenue(db: Session):
        revenue = AccountingRepository.get_total_revenue(db)

        return {
            "revenue": float(revenue or 0)
        }

    # ==========================================================
    # NOMBRE DE VENTES
    # ==========================================================

    @staticmethod
    def get_sales_count(db: Session):
        count = AccountingRepository.get_sales_count(db)

        return {
            "sales_count": int(count or 0)
        }

    # ==========================================================
    # COÛT DES MARCHANDISES VENDUES
    # ==========================================================

    @staticmethod
    def get_cost_of_goods(db: Session):
        cost = AccountingRepository.get_cost_of_goods_sold(db)
        cost_coverage = AccountingRepository.get_historical_cost_coverage(db)

        return {
            "cost_of_goods": float(cost or 0),
            "historical_cost_coverage": cost_coverage,
        }

    # ==========================================================
    # MARGE BRUTE
    # ==========================================================

    @staticmethod
    def get_gross_margin(db: Session):
        margin = AccountingRepository.get_gross_margin(db)
        cost_coverage = AccountingRepository.get_historical_cost_coverage(db)

        return {
            "gross_margin": float(margin or 0),
            "historical_cost_coverage": cost_coverage,
        }

    # ==========================================================
    # VALEUR DU STOCK
    # ==========================================================

    @staticmethod
    def get_stock_value(db: Session):
        value = AccountingRepository.get_stock_value(db)

        return {
            "stock_value": float(value or 0)
        }

    # ==========================================================
    # QUANTITÉ TOTALE EN STOCK
    # ==========================================================

    @staticmethod
    def get_stock_quantity(db: Session):
        quantity = AccountingRepository.get_total_stock_quantity(db)

        return {
            "stock_quantity": float(quantity or 0)
        }

    # ==========================================================
    # PRODUITS LES PLUS VENDUS
    # ==========================================================

    @staticmethod
    def get_top_selling_products(
        db: Session,
        limit: int = 10
    ):
        if limit <= 0:
            limit = 10

        if limit > 100:
            limit = 100

        return AccountingRepository.get_top_products(
            db,
            limit=limit
        )

    # ==========================================================
    # PRODUITS EN STOCK FAIBLE
    # ==========================================================

    @staticmethod
    def get_low_stock_products(db: Session):
        return AccountingRepository.get_low_stock_products(db)

    # ==========================================================
    # SYNTHÈSE FINANCIÈRE
    # ==========================================================

    @staticmethod
    def get_financial_summary(db: Session):

        revenue = float(
            AccountingRepository.get_total_revenue(db) or 0
        )

        cost = float(
            AccountingRepository.get_cost_of_goods_sold(db) or 0
        )

        margin = float(
            AccountingRepository.get_gross_margin(db) or 0
        )

        cost_coverage = AccountingRepository.get_historical_cost_coverage(db)

        if cost_coverage["complete"] and revenue > 0:
            margin_rate = (margin / revenue) * 100
        else:
            margin_rate = None

        return {
            "revenue": revenue,
            "cost_of_goods": cost,
            "gross_margin": margin,
            "gross_margin_rate": (
                round(margin_rate, 2)
                if margin_rate is not None
                else None
            ),
            "historical_cost_coverage": cost_coverage,
        }

    # ==========================================================
    # SYNTHÈSE DU STOCK
    # ==========================================================

    @staticmethod
    def get_stock_summary(db: Session):

        stock_value = float(
            AccountingRepository.get_stock_value(db) or 0
        )

        stock_quantity = float(
            AccountingRepository.get_total_stock_quantity(db) or 0
        )

        low_stock_products = (
            AccountingRepository.get_low_stock_products(db)
        )

        return {
            "stock_value": stock_value,
            "stock_quantity": stock_quantity,
            "low_stock_count": len(low_stock_products),
            "low_stock_products": low_stock_products
        }

    # ==========================================================
    # SYNTHÈSE DÉCISIONNELLE
    # ==========================================================

    @staticmethod
    def get_business_summary(db: Session):

        financial = AccountingService.get_financial_summary(db)

        stock = AccountingService.get_stock_summary(db)

        sales_count = AccountingRepository.get_sales_count(db)

        top_products = AccountingRepository.get_top_products(
            db,
            limit=10
        )

        return {
            "financial": financial,
            "sales": {
                "sales_count": int(sales_count or 0),
                "top_products": top_products
            },
            "stock": stock
        }

    # ==========================================================
    # ANALYSE FINANCIÈRE AVANCÉE
    # ==========================================================

    @staticmethod
    def get_financial_analysis(db: Session):

        revenue = float(
            AccountingRepository.get_total_revenue(db) or 0
        )

        # Uniformisation avec le reste du service
        sales_count = int(
            AccountingRepository.get_sales_count(db) or 0
        )

        cost_of_goods = float(
            AccountingRepository.get_cost_of_goods_sold(db) or 0
        )

        gross_margin = float(
            AccountingRepository.get_gross_margin(db) or 0
        )

        cost_coverage = AccountingRepository.get_historical_cost_coverage(db)

        if cost_coverage["complete"] and revenue > 0:
            margin_rate = (gross_margin / revenue) * 100
        else:
            margin_rate = None

        stock_value = float(
            AccountingRepository.get_stock_value(db) or 0
        )

        stock_quantity = float(
            AccountingRepository.get_total_stock_quantity(db) or 0
        )

        daily_revenue = (
            AccountingRepository.get_daily_revenue(db)
        )

        top_products = (
            AccountingRepository.get_top_profitable_products(
                db,
                limit=10
            )
        )

        return {
            "revenue": revenue,
            "sales_count": sales_count,
            "cost_of_goods": cost_of_goods,
            "gross_margin": gross_margin,
            "margin_rate": (
                round(margin_rate, 2)
                if margin_rate is not None
                else None
            ),
            "historical_cost_coverage": cost_coverage,
            "stock_value": stock_value,
            "stock_quantity": stock_quantity,
            "daily_revenue": daily_revenue,
            "top_products": top_products
        }

    # ==========================================================
    # ANALYSE DÉCISIONNELLE
    # ==========================================================

    @staticmethod
    def get_decision_analysis(db: Session):

        # ------------------------------------------------------
        # INDICATEURS FINANCIERS
        # ------------------------------------------------------

        revenue = float(
            AccountingRepository.get_total_revenue(db) or 0
        )

        sales_count = int(
            AccountingRepository.get_sales_count(db) or 0
        )

        cost_of_goods = float(
            AccountingRepository.get_cost_of_goods_sold(db) or 0
        )

        gross_margin = float(
            AccountingRepository.get_gross_margin(db) or 0
        )

        cost_coverage = AccountingRepository.get_historical_cost_coverage(db)

        # ------------------------------------------------------
        # TAUX DE MARGE
        # ------------------------------------------------------

        if cost_coverage["complete"] and revenue > 0:
            margin_rate = (gross_margin / revenue) * 100
        else:
            margin_rate = None

        # ------------------------------------------------------
        # STOCK
        # ------------------------------------------------------

        stock_value = float(
            AccountingRepository.get_stock_value(db) or 0
        )

        stock_quantity = float(
            AccountingRepository.get_total_stock_quantity(db) or 0
        )

        # ------------------------------------------------------
        # CHIFFRE D'AFFAIRES JOURNALIER
        # ------------------------------------------------------

        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)

        daily_revenue = (
            AccountingRepository.get_daily_revenue(
                db,
                start_date,
                end_date
            )
        )

        # ------------------------------------------------------
        # PRODUITS LES PLUS RENTABLES
        # ------------------------------------------------------

        top_products = (
            AccountingRepository.get_top_profitable_products(
                db,
                limit=10
            )
        )

        # ------------------------------------------------------
        # RECOMMANDATIONS
        # ------------------------------------------------------

        recommendations = []

        # Analyse du chiffre d'affaires
        if revenue == 0:
            recommendations.append(
                "Aucune vente enregistrée. "
                "Il est recommandé de développer les ventes "
                "et de vérifier l'activité commerciale."
            )
        elif sales_count > 0:
            recommendations.append(
                "L'activité commerciale est active. "
                "Il est recommandé de suivre régulièrement "
                "l'évolution du chiffre d'affaires."
            )

        # La marge ne doit pas etre interpretee si les couts sont incomplets.
        if not cost_coverage["complete"]:
            recommendations.append(
                "Marge non definitive : les couts historiques sont incomplets. "
                "Completer les couts historiques avant d'interpreter la rentabilite."
            )
        elif margin_rate is None:
            recommendations.append(
                "Le taux de marge ne peut pas etre calcule car le chiffre "
                "d'affaires est nul."
            )
        elif margin_rate < 10:
            recommendations.append(
                "La marge est faible. Il est recommande de revoir les prix "
                "de vente et les couts d'approvisionnement."
            )
        elif margin_rate < 30:
            recommendations.append(
                "La marge est moderee. Une optimisation des couts d'achat "
                "pourrait ameliorer la rentabilite."
            )
        else:
            recommendations.append(
                "La marge est satisfaisante. Il est recommande de maintenir "
                "la politique commerciale actuelle."
            )

        # Analyse du stock
        if stock_value == 0:
            recommendations.append(
                "La valeur du stock est nulle. "
                "Il est recommandé de vérifier les niveaux "
                "d'approvisionnement."
            )
        elif stock_quantity <= 0:
            recommendations.append(
                "Le stock disponible est nul ou insuffisant. "
                "Un réapprovisionnement est recommandé."
            )

        # Signaler lorsque les donnees disponibles ne permettent
        # pas de classer tous les produits de facon fiable.
        if top_products:
            recommendations.append(
                "Le classement des produits rentables ne contient que les "
                "produits dont les couts historiques sont complets."
            )
        elif not cost_coverage["complete"]:
            recommendations.append(
                "Aucun produit ne peut etre classe de facon fiable tant que "
                "des couts historiques restent manquants."
            )
        else:
            recommendations.append(
                "Aucun produit rentable n'a encore ete identifie."
            )

        # ------------------------------------------------------
        # RÉSULTAT
        # ------------------------------------------------------

        return {
            "revenue": revenue,
            "sales_count": sales_count,
            "cost_of_goods": cost_of_goods,
            "gross_margin": gross_margin,
            "margin_rate": (
                round(margin_rate, 2)
                if margin_rate is not None
                else None
            ),
            "historical_cost_coverage": cost_coverage,
            "stock_value": stock_value,
            "stock_quantity": stock_quantity,
            "daily_revenue": daily_revenue,
            "top_products": top_products,
            "recommendations": recommendations
        }
