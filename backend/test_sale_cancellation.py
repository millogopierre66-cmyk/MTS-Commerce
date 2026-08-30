from app.database.session import SessionLocal

from app.models.product import Product
from app.models.sale import Sale
from app.models.sale_item import SaleItem
from app.models.stock_movement import StockMovement

from app.repositories.sale_repository import SaleRepository

from app.schemas.sale import (
    SaleCreate,
    SaleItemCreate,
)

from app.services.sale_service import SaleService


# ==========================================================
# CONNEXION BASE DE DONNEES
# ==========================================================

db = SessionLocal()


try:

    PRODUCT_ID = 5
    QUANTITY = 2

    print("=" * 80)
    print("TEST ANNULATION TRANSACTIONNELLE D'UNE VENTE")
    print("=" * 80)

    # ======================================================
    # ETAT INITIAL
    # ======================================================

    product = (
        db.query(Product)
        .filter(Product.id == PRODUCT_ID)
        .first()
    )

    if not product:
        print(f"ERREUR : Produit {PRODUCT_ID} introuvable.")
        raise SystemExit

    stock_before = product.quantity

    sales_before = (
        db.query(Sale)
        .count()
    )

    items_before = (
        db.query(SaleItem)
        .count()
    )

    movements_before = (
        db.query(StockMovement)
        .count()
    )

    print(f"Produit = {product.name}")
    print(f"Stock avant = {stock_before}")
    print(f"Ventes avant = {sales_before}")
    print(f"SaleItems avant = {items_before}")
    print(f"Mouvements avant = {movements_before}")

    # ======================================================
    # CREATION DE LA VENTE
    # ======================================================

    print()
    print("-" * 80)
    print("CREATION D'UNE VENTE DE TEST")
    print("-" * 80)

    sale_data = SaleCreate(
        customer_id=3,
        items=[
            SaleItemCreate(
                product_id=PRODUCT_ID,
                quantity=QUANTITY
            )
        ]
    )

    sale = SaleService.create_sale(
        db,
        sale_data
    )

    sale_id = sale.id
    invoice_number = sale.invoice_number

    db.refresh(product)

    stock_after_sale = product.quantity

    print(f"Vente ID = {sale_id}")
    print(f"Facture = {invoice_number}")
    print(f"Quantite vendue = {QUANTITY}")
    print(f"Stock apres vente = {stock_after_sale}")

    # ======================================================
    # ANNULATION DE LA VENTE
    # ======================================================

    print()
    print("-" * 80)
    print("ANNULATION DE LA VENTE")
    print("-" * 80)

    result = SaleService.delete_sale(
        db,
        sale_id
    )

    print(result["message"])

    # ======================================================
    # VERIFICATIONS
    # ======================================================

    print()
    print("=" * 80)
    print("VERIFICATIONS APRES ANNULATION")
    print("=" * 80)

    db.expire_all()

    product_after = (
        db.query(Product)
        .filter(Product.id == PRODUCT_ID)
        .first()
    )

    stock_after_cancel = product_after.quantity

    sale_after = SaleRepository.get_by_id(
        db,
        sale_id
    )

    sales_after = (
        db.query(Sale)
        .count()
    )

    items_after = (
        db.query(SaleItem)
        .count()
    )

    movements_after = (
        db.query(StockMovement)
        .count()
    )

    cancellation_movement = (
        db.query(StockMovement)
        .filter(
            StockMovement.description.like(
                f"%Annulation vente {invoice_number}%"
            )
        )
        .first()
    )

    print(f"Stock apres annulation = {stock_after_cancel}")
    print(f"Vente existe encore = {sale_after is not None}")
    print(f"Ventes apres = {sales_after}")
    print(f"SaleItems apres = {items_after}")
    print(f"Mouvements apres = {movements_after}")

    # ======================================================
    # RESULTATS DES TESTS
    # ======================================================

    print()
    print("=" * 80)
    print("RESULTATS")
    print("=" * 80)

    checks = []

    checks.append(
        (
            "Stock diminue apres vente",
            stock_after_sale == stock_before - QUANTITY
        )
    )

    checks.append(
        (
            "Stock restaure apres annulation",
            stock_after_cancel == stock_before
        )
    )

    checks.append(
        (
            "Vente supprimee",
            sale_after is None
        )
    )

    checks.append(
        (
            "Nombre de ventes restaure",
            sales_after == sales_before
        )
    )

    checks.append(
        (
            "SaleItems supprimes",
            items_after == items_before
        )
    )

    checks.append(
        (
            "Mouvement d'annulation cree",
            cancellation_movement is not None
        )
    )

    checks.append(
        (
            "Mouvement IN correct",
            cancellation_movement is not None
            and cancellation_movement.movement_type == "IN"
        )
    )

    checks.append(
        (
            "Quantite du mouvement correcte",
            cancellation_movement is not None
            and cancellation_movement.quantity == QUANTITY
        )
    )

    all_ok = True

    for name, result in checks:

        test_status = "OK" if result else "ERREUR"

        print(f"{name} : {test_status}")

        if not result:
            all_ok = False

    print("=" * 80)

    if all_ok:

        print(
            "TEST GLOBAL: "
            "OK - ANNULATION TRANSACTIONNELLE COHERENTE"
        )

    else:

        print(
            "TEST GLOBAL: ERREUR"
        )


finally:

    db.close()