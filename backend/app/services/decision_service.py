from sqlalchemy.orm import Session

from app.repositories.accounting_repository import AccountingRepository


class DecisionService:

    # ==========================================================
    # ANALYSE DÉCISIONNELLE
    # ==========================================================

    @staticmethod
    def get_decision_analysis(
        db: Session
    ):

        revenue = AccountingRepository.get_total_revenue(db)

        sales_count = AccountingRepository.get_sales_count(db)

        gross_profit = AccountingRepository.get_gross_margin(db)

        cost_of_goods = (
            AccountingRepository.get_cost_of_goods_sold(db)
        )

        stock_value = (
            AccountingRepository.get_stock_value(db)
        )

        stock_quantity = (
            AccountingRepository.get_total_stock_quantity(db)
        )

        # ------------------------------------------------------
        # PANIER MOYEN
        # ------------------------------------------------------

        if sales_count > 0:
            average_sale = revenue / sales_count
        else:
            average_sale = 0.0

        # ------------------------------------------------------
        # TAUX DE MARGE
        # ------------------------------------------------------

        if revenue > 0:
            profit_margin = (
                gross_profit / revenue
            ) * 100
        else:
            profit_margin = 0.0

        # ------------------------------------------------------
        # TENDANCE DU CHIFFRE D'AFFAIRES
        # ------------------------------------------------------

        revenue_trend = {
            "direction": "stable",
            "percentage": 0.0,
            "message": "Aucune donnée suffisante pour déterminer une tendance."
        }

        # ------------------------------------------------------
        # ALERTES
        # ------------------------------------------------------

        alerts = []

        low_stock_products = (
            AccountingRepository.get_low_stock_products(db)
        )

        if low_stock_products:

            alerts.append({
                "level": "warning",
                "category": "stock",
                "message": (
                    f"{len(low_stock_products)} "
                    "produit(s) ont un niveau de stock faible."
                )
            })

        if sales_count == 0:

            alerts.append({
                "level": "info",
                "category": "sales",
                "message": "Aucune vente enregistrée."
            })

        # ------------------------------------------------------
        # RECOMMANDATIONS
        # ------------------------------------------------------

        recommendations = []

        if low_stock_products:

            recommendations.append({
                "priority": "high",
                "category": "stock",
                "message": (
                    "Prévoir le réapprovisionnement "
                    "des produits dont le stock est faible."
                )
            })

        if revenue == 0:

            recommendations.append({
                "priority": "medium",
                "category": "sales",
                "message": (
                    "Aucune vente n'est actuellement enregistrée. "
                    "Vérifier l'activité commerciale."
                )
            })

        if gross_profit > 0 and profit_margin < 20:

            recommendations.append({
                "priority": "medium",
                "category": "profitability",
                "message": (
                    "La marge bénéficiaire est faible. "
                    "Analyser les prix de vente et les coûts d'achat."
                )
            })

        return {
            "revenue": revenue,
            "sales_count": sales_count,
            "average_sale": average_sale,

            "gross_profit": gross_profit,
            "profit_margin": profit_margin,

            "stock_value": stock_value,
            "stock_quantity": stock_quantity,

            "revenue_trend": revenue_trend,

            "alerts": alerts,

            "recommendations": recommendations
        }