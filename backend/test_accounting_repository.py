from app.database.session import SessionLocal
from app.repositories.accounting_repository import AccountingRepository


db = SessionLocal()

try:

    print("=" * 50)
    print("COMPTABILITÉ MTS COMMERCE")
    print("=" * 50)

    print(
        "Chiffre d'affaires :",
        AccountingRepository.get_total_revenue(db)
    )

    print(
        "Nombre de ventes :",
        AccountingRepository.get_total_sales(db)
    )

    print(
        "Marge brute :",
        AccountingRepository.get_gross_margin(db)
    )

    print(
        "Coût des marchandises :",
        AccountingRepository.get_cost_of_goods_sold(db)
    )

    print(
        "Valeur du stock :",
        AccountingRepository.get_stock_value(db)
    )

    print(
        "Quantité en stock :",
        AccountingRepository.get_total_stock_quantity(db)
    )

    print("\nProduits les plus vendus :")

    products = AccountingRepository.get_top_products(
        db,
        limit=10
    )

    for product in products:
        print(
            product.name,
            "| Quantité :",
            product.quantity_sold,
            "| CA :",
            product.revenue
        )

    print("\nProduits en stock faible :")

    low_stock = AccountingRepository.get_low_stock_products(db)

    for product in low_stock:
        print(
            product.name,
            "| Stock :",
            product.quantity
        )

finally:
    db.close()