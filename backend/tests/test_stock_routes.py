from fastapi import HTTPException
from fastapi.testclient import TestClient
import pytest

from app.main import app
from app.models.product import Product
from app.models.stock_movement import StockMovement
from app.models.user import User
from app.routes import stock as stock_routes
from app.security import auth


def creer_modele(modele, **valeurs):
    attributs = set(modele.__mapper__.attrs.keys())
    return modele(**{
        cle: valeur
        for cle, valeur in valeurs.items()
        if cle in attributs
    })


def creer_utilisateur(db, role):
    utilisateur = creer_modele(
        User,
        username=f"stock_route_{role}",
        email=f"stock_route_{role}@example.test",
        password="test-only-password",
        role=role,
        is_active=True,
        active=True,
    )
    db.add(utilisateur)
    db.flush()
    return utilisateur


def creer_produit(db):
    produit = creer_modele(
        Product,
        reference="REF-ROUTE-STOCK",
        barcode="BAR-ROUTE-STOCK",
        name="Produit test routes stock",
        description="Test HTTP",
        category="Test",
        purchase_price=600.0,
        selling_price=1000.0,
        quantity=10,
        alert_stock=2,
        minimum_stock=2,
        active=True,
    )
    db.add(produit)
    db.commit()
    return produit


@pytest.fixture
def stock_client(db):
    anciens_overrides = app.dependency_overrides.copy()
    utilisateur_courant = {"value": None}

    def override_current_user():
        utilisateur = utilisateur_courant["value"]

        if utilisateur is None:
            raise HTTPException(
                status_code=401,
                detail="Authentification requise.",
            )

        return utilisateur

    app.dependency_overrides[stock_routes.get_db] = lambda: db
    app.dependency_overrides[auth.get_current_user] = (
        override_current_user
    )

    client = TestClient(app)

    try:
        yield client, utilisateur_courant
    finally:
        client.close()
        app.dependency_overrides.clear()
        app.dependency_overrides.update(anciens_overrides)


@pytest.mark.parametrize("role", ["admin", "manager"])
def test_admin_and_manager_can_use_stock_in_route(
    db,
    stock_client,
    role,
):
    client, utilisateur_courant = stock_client

    utilisateur = creer_utilisateur(db, role)
    produit = creer_produit(db)

    utilisateur_courant["value"] = utilisateur

    response = client.post(
        "/stock/in",
        json={
            "product_id": produit.id,
            "quantity": 2,
            "description": "Entree de test",
        },
    )

    assert response.status_code == 200

    resultat = response.json()

    assert resultat["movement_type"] == "IN"
    assert resultat["quantity"] == 2
    assert resultat["product_id"] == produit.id

    db.expire_all()

    assert db.get(Product, produit.id).quantity == 12

    mouvement = (
        db.query(StockMovement)
        .filter(StockMovement.product_id == produit.id)
        .one()
    )

    assert mouvement.user_id == utilisateur.id


@pytest.mark.parametrize(
    "route,quantity",
    [
        ("/stock/in", 2),
        ("/stock/out", 2),
        ("/stock/adjust", 5),
    ],
)
def test_vendeur_cannot_modify_stock(
    db,
    stock_client,
    route,
    quantity,
):
    client, utilisateur_courant = stock_client

    utilisateur = creer_utilisateur(db, "vendeur")
    produit = creer_produit(db)

    utilisateur_courant["value"] = utilisateur

    response = client.post(
        route,
        json={
            "product_id": produit.id,
            "quantity": quantity,
            "description": "Tentative vendeur",
        },
    )

    assert response.status_code == 403

    db.expire_all()

    assert db.get(Product, produit.id).quantity == 10
    assert db.query(StockMovement).count() == 0


def test_authenticated_vendeur_can_read_stock_and_history(
    db,
    stock_client,
):
    client, utilisateur_courant = stock_client

    utilisateur = creer_utilisateur(db, "vendeur")
    produit = creer_produit(db)

    utilisateur_courant["value"] = utilisateur

    response_stock = client.get(f"/stock/{produit.id}")

    assert response_stock.status_code == 200
    assert response_stock.json()["stock"] == 10

    response_history = client.get(
        f"/stock/history/{produit.id}"
    )

    assert response_history.status_code == 200
    assert response_history.json() == []


def test_stock_routes_reject_unauthenticated_access(
    stock_client,
):
    client, utilisateur_courant = stock_client

    utilisateur_courant["value"] = None

    response = client.get("/stock/1")

    assert response.status_code == 401
