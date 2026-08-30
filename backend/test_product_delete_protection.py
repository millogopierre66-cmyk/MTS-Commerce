from app.database.session import SessionLocal
from app.services.product_service import ProductService
from app.models.product import Product
from fastapi import HTTPException


db = SessionLocal()

try:
    product_id = 5

    product = (
        db.query(Product)
        .filter(Product.id == product_id)
        .first()
    )

    print("TEST PROTECTION SUPPRESSION PRODUIT")
    print("=" * 70)

    if not product:
        print("ERREUR : produit introuvable.")

    else:
        print(f"Produit ID = {product.id}")
        print(f"Nom = {product.name}")

        try:
            ProductService.delete(
                db,
                product_id
            )

            print("TEST: ERREUR - produit supprime")

        except HTTPException as e:

            print("Exception = HTTPException")
            print(f"Statut HTTP = {e.status_code}")
            print(f"Detail = {e.detail}")

            product_after = (
                db.query(Product)
                .filter(Product.id == product_id)
                .first()
            )

            print(
                f"Produit toujours present = "
                f"{product_after is not None}"
            )

            if (
                e.status_code == 400
                and product_after is not None
            ):
                print("TEST: OK - SUPPRESSION BLOQUEE")
            else:
                print("TEST: ERREUR")

finally:
    db.close()

