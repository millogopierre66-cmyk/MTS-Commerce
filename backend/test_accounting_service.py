from app.database.session import SessionLocal
from app.services.accounting_service import AccountingService


db = SessionLocal()

try:

    print("=" * 60)
    print("MTS COMMERCE - ACCOUNTING SERVICE")
    print("=" * 60)

    print("\n--- TABLEAU DE BORD ---")

    dashboard = AccountingService.get_dashboard(db)

    for key, value in dashboard.items():
        print(f"{key} : {value}")

    print("\n--- SYNTHÈSE FINANCIÈRE ---")

    financial = AccountingService.get_financial_summary(db)

    for key, value in financial.items():
        print(f"{key} : {value}")

    print("\n--- SYNTHÈSE DU STOCK ---")

    stock = AccountingService.get_stock_summary(db)

    print(
        f"Valeur du stock : "
        f"{stock['stock_value']}"
    )

    print(
        f"Quantité en stock : "
        f"{stock['stock_quantity']}"
    )

    print(
        f"Produits en stock faible : "
        f"{stock['low_stock_count']}"
    )

    print("\n--- PRODUITS LES PLUS VENDUS ---")

    top_products = AccountingService.get_top_selling_products(
        db,
        limit=10
    )

    for product in top_products:
        print(product)

    print("\n--- SYNTHÈSE DÉCISIONNELLE ---")

    summary = AccountingService.get_business_summary(db)

    print(summary)

    print("\n" + "=" * 60)
    print("TEST TERMINÉ AVEC SUCCÈS")
    print("=" * 60)

finally:
    db.close()