from app.database.session import SessionLocal
from app.services.product_service import ProductService
from app.schemas.product import ProductCreate
from fastapi import HTTPException

db = SessionLocal()

try:
    print("TEST UNICITE REFERENCE - CREATION")
    print("=" * 70)

    reference_existante = "PROD-003"

    print(f"Reference deja utilisee = {reference_existante}")

    try:
        ProductService.create(
            db,
            ProductCreate(
                reference=reference_existante,
                barcode="TESTBARCODE999",
                name="Produit Test Reference",
                description="Test unicite reference",
                category="Test",
                purchase_price=1000,
                selling_price=1500,
                quantity=10,
                alert_stock=5,
                minimum_stock=5,
                active=True
            )
        )

        print("TEST: ERREUR - produit cree avec une reference existante")

    except HTTPException as e:
        print("Exception = HTTPException")
        print(f"Statut HTTP = {e.status_code}")
        print(f"Detail = {e.detail}")

        if (
            e.status_code == 400
            and "référence" in e.detail
        ):
            print("TEST: OK")
        else:
            print("TEST: ERREUR")

finally:
    db.close()