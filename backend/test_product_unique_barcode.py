from app.database.session import SessionLocal
from app.services.product_service import ProductService
from app.schemas.product import ProductCreate
from fastapi import HTTPException

db = SessionLocal()

try:
    print("TEST UNICITE CODE-BARRES - CREATION")
    print("=" * 70)

    barcode_existant = "1112223334445"

    print(f"Code-barres deja utilise = {barcode_existant}")

    try:
        ProductService.create(
            db,
            ProductCreate(
                reference="TEST-BARCODE-001",
                barcode=barcode_existant,
                name="Produit Test Barcode",
                description="Test unicite code-barres",
                category="Test",
                purchase_price=1000,
                selling_price=1500,
                quantity=10,
                alert_stock=5,
                minimum_stock=5,
                active=True
            )
        )

        print("TEST: ERREUR - produit cree avec un code-barres existant")

    except HTTPException as e:
        print("Exception = HTTPException")
        print(f"Statut HTTP = {e.status_code}")
        print(f"Detail = {e.detail}")

        if (
            e.status_code == 400
            and e.detail == "Ce code-barres est déjà utilisé."
        ):
            print("TEST: OK")
        else:
            print("TEST: ERREUR")

finally:
    db.close()