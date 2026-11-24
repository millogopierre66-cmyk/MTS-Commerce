import pytest
from fastapi import HTTPException

from app.models.user import User
from app.models.product import Product
from app.models.stock_movement import StockMovement
from app.repositories.stock_repository import StockRepository
from app.schemas.stock import StockIn, StockOut
from app.services.stock_service import StockService


def creer_modele(modele, **valeurs):
    attributs = set(modele.__mapper__.attrs.keys())
    return modele(**{
        cle: valeur
        for cle, valeur in valeurs.items()
        if cle in attributs
    })


def creer_utilisateur(db):
    utilisateur = creer_modele(
        User,
        username="stock_test_admin",
        email="stock_test_admin@example.test",
        password="test-only-password",
        role="admin",
        is_active=True,
        active=True,
    )
    db.add(utilisateur)
    db.flush()
    return utilisateur


def creer_produit(db, suffixe, stock=10, actif=True):
    produit = creer_modele(
        Product,
        reference=f"REF-STOCK-{suffixe}",
        barcode=f"BAR-STOCK-{suffixe}",
        name=f"Produit stock {suffixe}",
        description="Produit de test",
        category="Test",
        purchase_price=600.0,
        selling_price=1000.0,
        quantity=stock,
        alert_stock=2,
        minimum_stock=2,
        active=actif,
    )
    db.add(produit)
    db.flush()
    return produit


def mouvements_produit(db, product_id):
    return (
        db.query(StockMovement)
        .filter(StockMovement.product_id == product_id)
        .all()
    )


def test_stock_in_updates_quantity_and_records_user(db):
    utilisateur = creer_utilisateur(db)
    produit = creer_produit(db, "IN", stock=10)

    mouvement = StockService.stock_in(
        db,
        StockIn(
            product_id=produit.id,
            quantity=5,
            description="Reception de marchandises",
        ),
        current_user=utilisateur,
    )

    db.expire_all()

    produit_actualise = db.get(Product, produit.id)
    assert produit_actualise.quantity == 15

    mouvements = mouvements_produit(db, produit.id)
    assert len(mouvements) == 1
    assert mouvement.movement_type == "IN"
    assert mouvement.quantity == 5
    assert mouvement.user_id == utilisateur.id


def test_stock_out_updates_quantity_and_records_user(db):
    utilisateur = creer_utilisateur(db)
    produit = creer_produit(db, "OUT", stock=10)

    mouvement = StockService.stock_out(
        db,
        StockOut(
            product_id=produit.id,
            quantity=3,
            description="Sortie de marchandises",
        ),
        current_user=utilisateur,
    )

    db.expire_all()

    assert db.get(Product, produit.id).quantity == 7

    mouvements = mouvements_produit(db, produit.id)
    assert len(mouvements) == 1
    assert mouvement.movement_type == "OUT"
    assert mouvement.quantity == 3
    assert mouvement.user_id == utilisateur.id


def test_stock_out_rejects_insufficient_quantity_without_changes(db):
    utilisateur = creer_utilisateur(db)
    produit = creer_produit(db, "INSUFFISANT", stock=2)

    with pytest.raises(HTTPException) as exc:
        StockService.stock_out(
            db,
            StockOut(
                product_id=produit.id,
                quantity=5,
                description="Sortie impossible",
            ),
            current_user=utilisateur,
        )

    assert exc.value.status_code == 400

    db.expire_all()

    assert db.get(Product, produit.id).quantity == 2
    assert mouvements_produit(db, produit.id) == []


def test_adjust_stock_records_real_signed_difference(db):
    utilisateur = creer_utilisateur(db)
    produit = creer_produit(db, "ADJUST", stock=10)

    mouvement = StockService.adjust_stock(
        db,
        product_id=produit.id,
        quantity=6,
        description="Inventaire physique",
        current_user=utilisateur,
    )

    db.expire_all()

    assert db.get(Product, produit.id).quantity == 6

    mouvements = mouvements_produit(db, produit.id)
    assert len(mouvements) == 1
    assert mouvement.movement_type == "ADJUSTMENT"
    assert mouvement.quantity == -4
    assert mouvement.user_id == utilisateur.id


def test_stock_in_rolls_back_if_movement_creation_fails(db, monkeypatch):
    utilisateur = creer_utilisateur(db)
    produit = creer_produit(db, "ROLLBACK", stock=10)

    # Valider les donnees initiales avant de simuler l'echec.
    produit_id = produit.id
    db.commit()

    produit = db.get(Product, produit_id)
    assert produit is not None
    assert produit.quantity == 10

    def simuler_echec(db_session, movement):
        raise RuntimeError("Echec simule de creation du mouvement")

    monkeypatch.setattr(
        StockRepository,
        "create_movement",
        staticmethod(simuler_echec),
    )

    with pytest.raises(RuntimeError):
        StockService.stock_in(
            db,
            StockIn(
                product_id=produit.id,
                quantity=5,
                description="Test rollback",
            ),
            current_user=utilisateur,
        )

    db.expire_all()

    assert db.get(Product, produit.id).quantity == 10
    assert mouvements_produit(db, produit.id) == []

def test_adjust_stock_records_positive_difference(db):
    utilisateur = creer_utilisateur(db)
    produit = creer_produit(db, "ADJUST-UP", stock=10)

    mouvement = StockService.adjust_stock(
        db,
        product_id=produit.id,
        quantity=15,
        current_user=utilisateur,
    )

    db.expire_all()

    assert db.get(Product, produit.id).quantity == 15

    mouvements = mouvements_produit(db, produit.id)

    assert len(mouvements) == 1
    assert mouvement.movement_type == "ADJUSTMENT"
    assert mouvement.quantity == 5
    assert mouvement.user_id == utilisateur.id


def test_adjust_stock_rejects_identical_quantity_without_changes(db):
    utilisateur = creer_utilisateur(db)
    produit = creer_produit(db, "ADJUST-ZERO", stock=10)

    with pytest.raises(HTTPException) as exc:
        StockService.adjust_stock(
            db,
            product_id=produit.id,
            quantity=10,
            current_user=utilisateur,
        )

    assert exc.value.status_code == 400
    assert exc.value.detail == (
        "La quantite est identique au stock actuel."
    )

    db.expire_all()

    assert db.get(Product, produit.id).quantity == 10
    assert mouvements_produit(db, produit.id) == []

def test_adjust_stock_records_negative_difference(db):
    utilisateur = creer_utilisateur(db)
    produit = creer_produit(db, "ADJUST-DOWN", stock=15)

    mouvement = StockService.adjust_stock(
        db,
        product_id=produit.id,
        quantity=10,
        current_user=utilisateur,
    )

    db.expire_all()

    assert db.get(Product, produit.id).quantity == 10

    mouvements = mouvements_produit(db, produit.id)

    assert len(mouvements) == 1
    assert mouvement.movement_type == "ADJUSTMENT"
    assert mouvement.quantity == -5
    assert mouvement.user_id == utilisateur.id