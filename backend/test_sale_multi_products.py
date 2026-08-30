from app.database.session import SessionLocal
from app.services.sale_service import SaleService
from app.schemas.sale import SaleCreate
from app.models.product import Product
from app.models.sale import Sale
from app.models.sale_item import SaleItem
from app.models.stock_movement import StockMovement

db = SessionLocal()

try:
    product_1_id = 3
    product_2_id = 4

    p1 = db.query(Product).filter(Product.id == product_1_id).first()
    p2 = db.query(Product).filter(Product.id == product_2_id).first()

    stock_1_avant = p1.quantity
    stock_2_avant = p2.quantity

    qte_1 = 2
    qte_2 = 3

    ventes_avant = db.query(Sale).count()

    mouvements_1_avant = db.query(StockMovement).filter(
        StockMovement.product_id == product_1_id
    ).count()

    mouvements_2_avant = db.query(StockMovement).filter(
        StockMovement.product_id == product_2_id
    ).count()

    prix_1 = p1.selling_price
    prix_2 = p2.selling_price

    total_attendu = (
        prix_1 * qte_1
        + prix_2 * qte_2
    )

    print("TEST VENTE MULTI-PRODUITS")
    print("=" * 70)
    print(f"Produit 1 = {p1.name}")
    print(f"Stock avant = {stock_1_avant}")
    print(f"Quantite vendue = {qte_1}")
    print(f"Prix unitaire = {prix_1}")
    print()
    print(f"Produit 2 = {p2.name}")
    print(f"Stock avant = {stock_2_avant}")
    print(f"Quantite vendue = {qte_2}")
    print(f"Prix unitaire = {prix_2}")
    print()
    print(f"Total attendu = {total_attendu}")

    data = SaleCreate(
        customer_id=None,
        items=[
            {
                "product_id": product_1_id,
                "quantity": qte_1
            },
            {
                "product_id": product_2_id,
                "quantity": qte_2
            }
        ]
    )

    sale = SaleService.create_sale(db, data)

    db.refresh(p1)
    db.refresh(p2)

    stock_1_apres = p1.quantity
    stock_2_apres = p2.quantity

    items = db.query(SaleItem).filter(
        SaleItem.sale_id == sale.id
    ).all()

    mouvements_1 = db.query(StockMovement).filter(
        StockMovement.product_id == product_1_id,
        StockMovement.description == f"Vente {sale.invoice_number}"
    ).all()

    mouvements_2 = db.query(StockMovement).filter(
        StockMovement.product_id == product_2_id,
        StockMovement.description == f"Vente {sale.invoice_number}"
    ).all()

    ventes_apres = db.query(Sale).count()

    print()
    print("RESULTATS")
    print("=" * 70)
    print(f"Facture = {sale.invoice_number}")
    print(f"Total facture = {sale.total}")
    print(f"Stock produit 1 apres = {stock_1_apres}")
    print(f"Stock produit 2 apres = {stock_2_apres}")
    print(f"Nombre de SaleItem = {len(items)}")
    print(f"Mouvements produit 1 = {len(mouvements_1)}")
    print(f"Mouvements produit 2 = {len(mouvements_2)}")
    print(f"Nombre de ventes avant = {ventes_avant}")
    print(f"Nombre de ventes apres = {ventes_apres}")

    test_stock_1 = stock_1_apres == stock_1_avant - qte_1
    test_stock_2 = stock_2_apres == stock_2_avant - qte_2
    test_total = sale.total == total_attendu
    test_items = len(items) == 2
    test_mouvements = len(mouvements_1) == 1 and len(mouvements_2) == 1
    test_vente = ventes_apres == ventes_avant + 1

    print()
    print("VERIFICATIONS")
    print("=" * 70)
    print("Stock produit 1 :", "OK" if test_stock_1 else "ERREUR")
    print("Stock produit 2 :", "OK" if test_stock_2 else "ERREUR")
    print("Total facture    :", "OK" if test_total else "ERREUR")
    print("SaleItem         :", "OK" if test_items else "ERREUR")
    print("Mouvements OUT   :", "OK" if test_mouvements else "ERREUR")
    print("Creation vente   :", "OK" if test_vente else "ERREUR")

    if all([
        test_stock_1,
        test_stock_2,
        test_total,
        test_items,
        test_mouvements,
        test_vente
    ]):
        print()
        print("TEST: OK")
    else:
        print()
        print("TEST: ERREUR")

finally:
    db.close()
