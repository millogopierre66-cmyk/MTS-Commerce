from app.database.session import SessionLocal
from app.services.sale_service import SaleService
from app.schemas.sale import SaleCreate
from app.models.product import Product
from app.models.sale import Sale
from app.models.sale_item import SaleItem
from app.models.stock_movement import StockMovement
from fastapi import HTTPException

db = SessionLocal()

try:
    product_id = 5

    product = db.query(Product).filter(Product.id == product_id).first()
    stock_avant = product.quantity

    ventes_avant = db.query(Sale).count()
    mouvements_avant = db.query(StockMovement).filter(
        StockMovement.product_id == product_id
    ).count()

    print("TEST VENTE AVEC STOCK INSUFFISANT")
    print("=" * 70)
    print(f"Produit = {product.name}")
    print(f"Stock avant = {stock_avant}")
    print(f"Quantite demandee = {stock_avant + 1}")
    print(f"Ventes avant = {ventes_avant}")
    print(f"Mouvements avant = {mouvements_avant}")

    data = SaleCreate(
        customer_id=None,
        items=[
            {
                "product_id": product_id,
                "quantity": stock_avant + 1
            }
        ]
    )

    try:
        SaleService.create_sale(db, data)

        print("TEST: ERREUR - la vente a ete acceptee")

    except HTTPException as e:

        print(f"Exception = HTTPException")
        print(f"Statut HTTP = {e.status_code}")
        print(f"Detail = {e.detail}")

        db.rollback()

        product = db.query(Product).filter(
            Product.id == product_id
        ).first()

        stock_apres = product.quantity

        ventes_apres = db.query(Sale).count()

        mouvements_apres = db.query(StockMovement).filter(
            StockMovement.product_id == product_id
        ).count()

        print(f"Stock apres = {stock_apres}")
        print(f"Ventes apres = {ventes_apres}")
        print(f"Mouvements apres = {mouvements_apres}")

        if (
            e.status_code == 400
            and stock_apres == stock_avant
            and ventes_apres == ventes_avant
            and mouvements_apres == mouvements_avant
        ):
            print("TEST: OK")
        else:
            print("TEST: ERREUR")

finally:
    db.close()
