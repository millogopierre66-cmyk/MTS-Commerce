from app.database.session import SessionLocal
from app.services.stock_service import StockService
from app.schemas.stock import StockOut
from app.models.product import Product
from fastapi import HTTPException

db = SessionLocal()

try:
    product = db.query(Product).filter(Product.id == 5).first()
    avant = product.quantity

    print("TEST STOCK INSUFFISANT")
    print("=" * 60)
    print(f"Stock avant = {avant}")
    print(f"Quantite demandee = {avant + 1}")

    try:
        StockService.stock_out(
            db,
            StockOut(
                product_id=5,
                quantity=avant + 1,
                description="Test stock insuffisant"
            )
        )

        print("TEST: ERREUR - sortie acceptee")

    except HTTPException as e:
        print("Exception = HTTPException")
        print(f"Statut HTTP = {e.status_code}")
        print(f"Detail = {e.detail}")

        product = db.query(Product).filter(Product.id == 5).first()
        apres = product.quantity

        print(f"Stock apres = {apres}")

        if (
            e.status_code == 400
            and e.detail == "Stock insuffisant."
            and apres == avant
        ):
            print("TEST: OK")
        else:
            print("TEST: ERREUR")

finally:
    db.close()
