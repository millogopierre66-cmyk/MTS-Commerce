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

    # ==========================================================
    # ETAT AVANT
    # ==========================================================

    product_5 = (
        db.query(Product)
        .filter(Product.id == 5)
        .first()
    )

    product_4 = (
        db.query(Product)
        .filter(Product.id == 4)
        .first()
    )

    stock_5_avant = product_5.quantity
    stock_4_avant = product_4.quantity

    ventes_avant = db.query(Sale).count()
    items_avant = db.query(SaleItem).count()
    mouvements_avant = db.query(StockMovement).count()

    print("TEST ROLLBACK VENTE - STOCK INSUFFISANT")
    print("=" * 80)

    print(
        f"Produit 5 = {product_5.name} | "
        f"Stock avant = {stock_5_avant}"
    )

    print(
        f"Produit 4 = {product_4.name} | "
        f"Stock avant = {stock_4_avant}"
    )

    print(f"Ventes avant = {ventes_avant}")
    print(f"SaleItems avant = {items_avant}")
    print(f"Mouvements avant = {mouvements_avant}")

    # ==========================================================
    # CREATION DE LA VENTE
    # ==========================================================

    print()
    print("VENTE DE TEST")
    print("-" * 80)

    print(
        f"- Produit 5 : quantité 1 "
        f"(valide)"
    )

    print(
        f"- Produit 4 : quantité {stock_4_avant + 1} "
        f"(invalide)"
    )

    try:

        SaleService.create_sale(
            db,
            SaleCreate(
                items=[
                    {
                        "product_id": 5,
                        "quantity": 1
                    },
                    {
                        "product_id": 4,
                        "quantity": stock_4_avant + 1
                    }
                ]
            )
        )

        print(
            "TEST: ERREUR - vente acceptée"
        )

    except HTTPException as e:

        print()
        print("EXCEPTION")
        print("-" * 80)

        print(
            f"Exception = {type(e).__name__}"
        )

        print(
            f"Statut HTTP = {e.status_code}"
        )

        print(
            f"Détail = {e.detail}"
        )

    # ==========================================================
    # ETAT APRES
    # ==========================================================

    db.expire_all()

    product_5 = (
        db.query(Product)
        .filter(Product.id == 5)
        .first()
    )

    product_4 = (
        db.query(Product)
        .filter(Product.id == 4)
        .first()
    )

    stock_5_apres = product_5.quantity
    stock_4_apres = product_4.quantity

    ventes_apres = db.query(Sale).count()
    items_apres = db.query(SaleItem).count()
    mouvements_apres = db.query(StockMovement).count()

    print()
    print("VERIFICATION APRES ROLLBACK")
    print("=" * 80)

    print(
        f"Stock produit 5 après = {stock_5_apres}"
    )

    print(
        f"Stock produit 4 après = {stock_4_apres}"
    )

    print(
        f"Ventes après = {ventes_apres}"
    )

    print(
        f"SaleItems après = {items_apres}"
    )

    print(
        f"Mouvements après = {mouvements_apres}"
    )

    # ==========================================================
    # VERIFICATIONS
    # ==========================================================

    print()
    print("VERIFICATIONS")
    print("=" * 80)

    stock_5_ok = stock_5_apres == stock_5_avant
    stock_4_ok = stock_4_apres == stock_4_avant
    ventes_ok = ventes_apres == ventes_avant
    items_ok = items_apres == items_avant
    mouvements_ok = mouvements_apres == mouvements_avant

    print(
        "Stock produit 5 inchangé :",
        "OK" if stock_5_ok else "ERREUR"
    )

    print(
        "Stock produit 4 inchangé :",
        "OK" if stock_4_ok else "ERREUR"
    )

    print(
        "Ventes inchangées :",
        "OK" if ventes_ok else "ERREUR"
    )

    print(
        "SaleItems inchangés :",
        "OK" if items_ok else "ERREUR"
    )

    print(
        "Mouvements inchangés :",
        "OK" if mouvements_ok else "ERREUR"
    )

    test_ok = (
        stock_5_ok
        and stock_4_ok
        and ventes_ok
        and items_ok
        and mouvements_ok
    )

    print()
    print(
        "TEST GLOBAL:",
        "OK - ROLLBACK TRANSACTIONNEL"
        if test_ok
        else "ERREUR - TRANSACTION NON ATOMIQUE"
    )

finally:

    db.close()