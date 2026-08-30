from app.database.session import SessionLocal
from app.models.product import Product
from app.services.stock_service import StockService


db = SessionLocal()

try:

    product_id = 5

    product = (
        db.query(Product)
        .filter(Product.id == product_id)
        .first()
    )

    print("TEST AJUSTEMENT DE STOCK")
    print("=" * 70)

    if not product:
        print("Produit introuvable.")

    else:

        old_stock = product.quantity

        print(f"Produit = {product.name}")
        print(f"Stock avant = {old_stock}")

        new_stock = old_stock + 5

        movement = StockService.adjust_stock(
            db=db,
            product_id=product_id,
            quantity=new_stock,
            description="Test ajustement"
        )

        db.refresh(product)

        print("-" * 70)
        print(f"Nouveau stock = {product.quantity}")
        print(f"Variation enregistree = {movement.quantity}")
        print(f"Type mouvement = {movement.movement_type}")
        print(f"Description = {movement.description}")

        print("=" * 70)

        if (
            product.quantity == new_stock
            and movement.quantity == 5
            and movement.movement_type == "ADJUSTMENT"
        ):
            print("TEST: OK - AJUSTEMENT COHERENT")

        else:
            print("TEST: ERREUR")

finally:
    db.close()
