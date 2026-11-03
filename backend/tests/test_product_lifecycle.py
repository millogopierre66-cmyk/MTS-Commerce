from datetime import datetime

import pytest
from pydantic import ValidationError
from unittest.mock import patch
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.main import app
from app.models.audit_log import AuditLog
from app.models.product import Product
from app.models.sale import Sale
from app.models.sale_item import SaleItem
from app.models.stock_movement import StockMovement
from app.models.user import User
from app.repositories.stock_repository import StockRepository
from app.schemas.product import ProductUpdate
from app.schemas.sale import SaleCreate, SaleItemCreate
from app.services.sale_service import SaleService
from app.routes import products as product_routes
from app.security import auth
from app.schemas.stock import StockIn, StockOut
from app.services.product_service import ProductService
from app.services.stock_service import StockService


def creer_modele(modele, **valeurs):
    attributs = set(modele.__mapper__.attrs.keys())
    return modele(**{
        cle: valeur
        for cle, valeur in valeurs.items()
        if cle in attributs
    })


def creer_utilisateur(db, role="admin"):
    utilisateur = creer_modele(
        User,
        username=f"product_lifecycle_{role}",
        email=f"product_lifecycle_{role}@example.test",
        password="test-only-password",
        role=role,
        is_active=True,
        active=True,
    )
    db.add(utilisateur)
    db.flush()
    return utilisateur


def creer_produit(db, suffixe, active=True, stock=10):
    produit = creer_modele(
        Product,
        reference=f"REF-LIFECYCLE-{suffixe}",
        barcode=f"BAR-LIFECYCLE-{suffixe}",
        name=f"Produit lifecycle {suffixe}",
        description="Produit de test",
        category="Test",
        purchase_price=600.0,
        selling_price=1000.0,
        quantity=stock,
        alert_stock=2,
        minimum_stock=2,
        active=active,
    )
    db.add(produit)
    db.flush()
    return produit


def ajouter_historique(db, produit, utilisateur):
    vente = creer_modele(
        Sale,
        invoice_number=f"FAC-LIFECYCLE-{produit.id}",
        user_id=utilisateur.id,
        total=1000.0,
        status="completed",
        created_at=datetime.now(),
    )
    db.add(vente)
    db.flush()

    ligne = creer_modele(
        SaleItem,
        sale_id=vente.id,
        product_id=produit.id,
        quantity=1,
        unit_price=1000.0,
        purchase_unit_price=600.0,
        subtotal=1000.0,
    )

    mouvement = StockMovement(
        product_id=produit.id,
        user_id=utilisateur.id,
        quantity=5,
        movement_type="IN",
        description="Reception historique",
    )

    db.add_all([ligne, mouvement])
    db.commit()

    return vente, ligne, mouvement


@pytest.fixture
def products_client(db):
    anciens_overrides = app.dependency_overrides.copy()
    utilisateur_courant = {"value": None}

    def override_admin():
        utilisateur = utilisateur_courant["value"]

        if utilisateur is None:
            raise HTTPException(
                status_code=401,
                detail="Authentification requise.",
            )

        if utilisateur.role != "admin":
            raise HTTPException(
                status_code=403,
                detail="Acces reserve a l'administrateur.",
            )

        return utilisateur

    app.dependency_overrides[product_routes.get_db] = lambda: db
    app.dependency_overrides[auth.get_current_admin] = override_admin

    client = TestClient(app)

    try:
        yield client, utilisateur_courant
    finally:
        client.close()
        app.dependency_overrides.clear()
        app.dependency_overrides.update(anciens_overrides)


def compter_audits_produit(db, product_id):
    return (
        db.query(AuditLog)
        .filter(
            AuditLog.action == "PRODUCT_DEACTIVATED",
            AuditLog.entity_type == "Product",
            AuditLog.entity_id == product_id,
        )
        .count()
    )


def test_deactivation_preserves_sales_movements_and_audit(db):
    utilisateur = creer_utilisateur(db)
    produit = creer_produit(db, "HISTORY")

    product_id = produit.id
    vente, ligne, mouvement = ajouter_historique(
        db,
        produit,
        utilisateur,
    )

    resultat = ProductService.delete(
        db,
        product_id,
        current_user=utilisateur,
    )

    db.expire_all()

    produit_apres = db.get(Product, product_id)

    assert resultat["active"] is False
    assert produit_apres is not None
    assert produit_apres.active is False

    assert db.get(Sale, vente.id) is not None
    assert db.get(SaleItem, ligne.id) is not None
    assert db.get(StockMovement, mouvement.id) is not None

    assert compter_audits_produit(db, product_id) == 1

    journal = (
        db.query(AuditLog)
        .filter(
            AuditLog.action == "PRODUCT_DEACTIVATED",
            AuditLog.entity_id == product_id,
        )
        .one()
    )

    assert journal.user_id == utilisateur.id


def test_product_without_history_is_also_deactivated(db):
    utilisateur = creer_utilisateur(db)
    produit = creer_produit(db, "WITHOUT-HISTORY")

    resultat = ProductService.delete(
        db,
        produit.id,
        current_user=utilisateur,
    )

    db.expire_all()

    produit_apres = db.get(Product, produit.id)

    assert resultat["active"] is False
    assert produit_apres is not None
    assert produit_apres.active is False
    assert compter_audits_produit(db, produit.id) == 1


def test_second_deactivation_is_rejected_without_duplicate_audit(db):
    utilisateur = creer_utilisateur(db)
    produit = creer_produit(db, "REPEAT")

    ProductService.delete(
        db,
        produit.id,
        current_user=utilisateur,
    )

    with pytest.raises(HTTPException) as exc:
        ProductService.delete(
            db,
            produit.id,
            current_user=utilisateur,
        )

    assert exc.value.status_code == 409
    assert compter_audits_produit(db, produit.id) == 1


@pytest.mark.parametrize(
    "operation",
    ["stock_in", "stock_out", "adjust_stock"],
)
def test_inactive_product_rejects_new_stock_operations(
    db,
    operation,
):
    utilisateur = creer_utilisateur(db)
    produit = creer_produit(
        db,
        f"INACTIVE-{operation}",
        active=False,
        stock=10,
    )

    with pytest.raises(HTTPException) as exc:
        if operation == "stock_in":
            StockService.stock_in(
                db,
                StockIn(
                    product_id=produit.id,
                    quantity=2,
                ),
                current_user=utilisateur,
            )

        elif operation == "stock_out":
            StockService.stock_out(
                db,
                StockOut(
                    product_id=produit.id,
                    quantity=2,
                ),
                current_user=utilisateur,
            )

        else:
            StockService.adjust_stock(
                db,
                product_id=produit.id,
                quantity=5,
                current_user=utilisateur,
            )

    assert exc.value.status_code == 409

    db.expire_all()

    assert db.get(Product, produit.id).quantity == 10

    assert (
        db.query(StockMovement)
        .filter(StockMovement.product_id == produit.id)
        .count()
        == 0
    )


def test_inactive_product_keeps_stock_and_history_readable(db):
    utilisateur = creer_utilisateur(db)
    produit = creer_produit(
        db,
        "READ-HISTORY",
        active=False,
        stock=10,
    )

    movement = StockMovement(
        product_id=produit.id,
        user_id=utilisateur.id,
        quantity=4,
        movement_type="IN",
        description="Ancien mouvement",
    )
    db.add(movement)
    db.commit()

    stock = StockService.get_stock(db, produit.id)
    historique = StockService.get_history(db, produit.id)

    assert stock["stock"] == 10
    assert len(historique) == 1
    assert historique[0].id == movement.id


def test_physical_product_deletion_cannot_delete_stock_history(db):
    utilisateur = creer_utilisateur(db)
    produit = creer_produit(db, "PHYSICAL-DELETE")

    product_id = produit.id
    movement = StockMovement(
        product_id=product_id,
        user_id=utilisateur.id,
        quantity=3,
        movement_type="IN",
        description="Mouvement a proteger",
    )
    db.add(movement)
    db.commit()

    db.delete(produit)

    with pytest.raises(RuntimeError, match="Suppression physique"):
        db.commit()

    db.rollback()
    db.expire_all()

    assert db.get(Product, product_id) is not None
    assert db.get(StockMovement, movement.id) is not None


def test_admin_can_deactivate_product_through_http_route(
    db,
    products_client,
):
    client, utilisateur_courant = products_client

    utilisateur = creer_utilisateur(db, "admin")
    produit = creer_produit(db, "ADMIN-ROUTE")

    product_id = produit.id

    ajouter_historique(db, produit, utilisateur)
    utilisateur_courant["value"] = utilisateur

    response = client.delete(f"/products/{product_id}")

    assert response.status_code == 200
    assert response.json()["active"] is False

    db.expire_all()

    assert db.get(Product, product_id) is not None
    assert db.get(Product, product_id).active is False
    assert compter_audits_produit(db, product_id) == 1


def test_vendor_cannot_deactivate_product(
    db,
    products_client,
):
    client, utilisateur_courant = products_client

    utilisateur = creer_utilisateur(db, "vendeur")
    produit = creer_produit(db, "VENDOR-ROUTE")

    utilisateur_courant["value"] = utilisateur

    response = client.delete(f"/products/{produit.id}")

    assert response.status_code == 403

    db.expire_all()

    assert db.get(Product, produit.id).active is True
    assert compter_audits_produit(db, produit.id) == 0

def test_atomic_stock_mutations_reject_inactive_products_by_default(db):
    produit = creer_produit(
        db,
        "ATOMIC-INACTIVE",
        active=False,
        stock=10,
    )

    assert StockRepository.decrement_stock_atomic(
        db, produit.id, 2
    ) is False

    assert StockRepository.increment_stock_atomic(
        db, produit.id, 2
    ) is False

    assert StockRepository.adjust_stock_atomic(
        db, produit.id, 10, 5
    ) is False

    db.expire_all()

    assert db.get(Product, produit.id).quantity == 10
    assert db.get(Product, produit.id).active is False


def test_generic_product_update_cannot_reactivate_inactive_product(db):
    utilisateur = creer_utilisateur(db)
    produit = creer_produit(db, "NO-REACTIVATION")

    ProductService.delete(
        db,
        produit.id,
        current_user=utilisateur,
    )

    with pytest.raises(ValidationError):
        ProductUpdate(active=True)

    resultat = ProductService.update(
        db,
        produit.id,
        ProductUpdate(name="Produit modifie"),
    )

    assert resultat.name == "Produit modifie"
    assert resultat.active is False


def test_sale_cancellation_restores_stock_after_product_deactivation(db):
    utilisateur = creer_utilisateur(db)
    produit = creer_produit(
        db,
        "CANCEL-INACTIVE",
        active=True,
        stock=10,
    )

    product_id = produit.id

    demande = SaleCreate(
        items=[
            SaleItemCreate(
                product_id=product_id,
                quantity=2,
            )
        ]
    )

    with patch(
        "app.services.sale_service.InvoiceNumberService.reserve_invoice_number",
        return_value="FAC-CANCEL-INACTIVE-TEST",
    ):
        vente = SaleService.create_sale(
            db=db,
            data=demande,
            current_user=utilisateur,
        )

    vente_id = vente.id

    db.expire_all()
    assert db.get(Product, product_id).quantity == 8

    ProductService.delete(
        db,
        product_id,
        current_user=utilisateur,
    )

    db.expire_all()
    assert db.get(Product, product_id).active is False

    resultat = SaleService.cancel_sale(
        db=db,
        sale_id=vente_id,
        current_user=utilisateur,
    )

    db.expire_all()

    assert resultat["status"] == "cancelled"
    assert db.get(Product, product_id).quantity == 10
    assert db.get(Product, product_id).active is False

    mouvements = (
        db.query(StockMovement)
        .filter(StockMovement.product_id == product_id)
        .all()
    )

    assert len(mouvements) == 2
    assert {movement.movement_type for movement in mouvements} == {
        "OUT",
        "IN",
    }
