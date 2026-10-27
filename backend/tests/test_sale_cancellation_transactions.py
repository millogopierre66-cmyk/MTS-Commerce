from unittest.mock import patch

import pytest
from fastapi import HTTPException

from app.models.audit_log import AuditLog
from app.models.product import Product
from app.models.sale import Sale
from app.models.sale_item import SaleItem
from app.models.stock_movement import StockMovement
from app.schemas.sale import SaleCreate, SaleItemCreate
from app.services.sale_service import SaleService


def creer_modele(modele, **valeurs):
    attributs = set(modele.__mapper__.attrs.keys())
    return modele(**{
        cle: valeur
        for cle, valeur in valeurs.items()
        if cle in attributs
    })


def creer_utilisateur(db):
    utilisateur = creer_modele(
        __import__("app.models.user", fromlist=["User"]).User,
        username="test_sale_transactions",
        email="test_sale_transactions@example.test",
        password="test-only-password",
        role="admin",
        is_active=True,
        active=True,
    )
    db.add(utilisateur)
    db.flush()
    return utilisateur


def creer_produit(db, suffixe, stock):
    produit = creer_modele(
        Product,
        ref=f"REF-TXN-{suffixe}",
        reference=f"REF-TXN-{suffixe}",
        barcode=f"BAR-TXN-{suffixe}",
        name=f"Produit transaction {suffixe}",
        description="Test SQLite en memoire",
        category="Test",
        purchase_price=600.0,
        selling_price=1000.0,
        quantity=stock,
        stock=stock,
        stock_quantity=stock,
        qty=stock,
        alert_stock=2,
        minimum_stock=2,
        is_active=True,
        active=True,
    )
    db.add(produit)
    db.flush()
    return produit


def compter_mouvements(db, product_id):
    return (
        db.query(StockMovement)
        .filter(StockMovement.product_id == product_id)
        .count()
    )


def compter_audits(db):
    return db.query(AuditLog).count()


def test_cancellation_restores_stock_once_and_keeps_history(db):
    utilisateur = creer_utilisateur(db)
    produit = creer_produit(db, "CANCEL", stock=10)
    stock_initial = produit.quantity

    demande = SaleCreate(
        items=[SaleItemCreate(product_id=produit.id, quantity=2)]
    )

    with patch(
        "app.services.sale_service.InvoiceNumberService.reserve_invoice_number",
        return_value="FAC-TEST-CANCEL-0001",
    ):
        vente = SaleService.create_sale(
            db=db,
            data=demande,
            current_user=utilisateur,
        )

    db.expire_all()
    produit_apres_vente = db.get(Product, produit.id)

    assert produit_apres_vente.quantity == stock_initial - 2

    vente_id = vente.id
    mouvements_avant_annulation = compter_mouvements(db, produit.id)
    audits_avant_annulation = compter_audits(db)
    lignes_avant_annulation = (
        db.query(SaleItem)
        .filter(SaleItem.sale_id == vente_id)
        .count()
    )

    resultat = SaleService.cancel_sale(
        db=db,
        sale_id=vente_id,
        current_user=utilisateur,
    )

    db.expire_all()
    produit_apres_annulation = db.get(Product, produit.id)
    vente_apres_annulation = db.get(Sale, vente_id)

    assert resultat["status"] == "cancelled"
    assert produit_apres_annulation.quantity == stock_initial
    assert vente_apres_annulation is not None
    assert vente_apres_annulation.status == "cancelled"

    # L'annulation conserve la vente et ses lignes.
    assert (
        db.query(SaleItem)
        .filter(SaleItem.sale_id == vente_id)
        .count()
    ) == lignes_avant_annulation

    # Un mouvement de sortie ? la vente, puis une entr?e ? l'annulation.
    assert compter_mouvements(db, produit.id) == mouvements_avant_annulation + 1

    audits_apres_annulation = compter_audits(db)
    assert audits_apres_annulation == audits_avant_annulation + 1

    # Une deuxi?me annulation doit ?chouer sans restaurer le stock ? nouveau.
    with pytest.raises(HTTPException) as exc:
        SaleService.cancel_sale(
            db=db,
            sale_id=vente_id,
            current_user=utilisateur,
        )

    assert exc.value.status_code == 409

    db.expire_all()
    assert db.get(Product, produit.id).quantity == stock_initial
    assert compter_mouvements(db, produit.id) == mouvements_avant_annulation + 1
    assert compter_audits(db) == audits_apres_annulation
    assert db.get(Sale, vente_id).status == "cancelled"


def test_failed_multi_product_sale_rolls_back_everything(db):
    utilisateur = creer_utilisateur(db)

    produit_valide = creer_produit(db, "ROLLBACK-A", stock=10)
    produit_insuffisant = creer_produit(db, "ROLLBACK-B", stock=1)

    # Valider les donnees initiales dans la base de test en memoire.
    # Le rollback de la vente ne doit annuler que l'operation testee.
    db.commit()

    produit_valide = db.get(Product, produit_valide.id)
    produit_insuffisant = db.get(Product, produit_insuffisant.id)

    assert produit_valide is not None
    assert produit_insuffisant is not None

    stock_valide_initial = produit_valide.quantity
    stock_insuffisant_initial = produit_insuffisant.quantity

    ventes_initiales = db.query(Sale).count()
    lignes_initiales = db.query(SaleItem).count()
    mouvements_initiaux = db.query(StockMovement).count()
    audits_initiaux = compter_audits(db)

    demande = SaleCreate(
        items=[
            SaleItemCreate(
                product_id=produit_valide.id,
                quantity=2,
            ),
            SaleItemCreate(
                product_id=produit_insuffisant.id,
                quantity=2,
            ),
        ]
    )

    with patch(
        "app.services.sale_service.InvoiceNumberService.reserve_invoice_number",
        return_value="FAC-TEST-ROLLBACK-0001",
    ):
        with pytest.raises(HTTPException) as exc:
            SaleService.create_sale(
                db=db,
                data=demande,
                current_user=utilisateur,
            )

    assert exc.value.status_code == 400

    db.expire_all()

    # Le stock du premier produit doit avoir ?t? restaur? par rollback.
    assert db.get(Product, produit_valide.id).quantity == stock_valide_initial
    assert (
        db.get(Product, produit_insuffisant.id).quantity
        == stock_insuffisant_initial
    )

    # Vente, lignes, mouvements et journal d'audit doivent rester inchang?s.
    assert db.query(Sale).count() == ventes_initiales
    assert db.query(SaleItem).count() == lignes_initiales
    assert db.query(StockMovement).count() == mouvements_initiaux
    assert compter_audits(db) == audits_initiaux
