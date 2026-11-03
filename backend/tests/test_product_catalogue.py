import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.main import app
from app.models.product import Product
from app.models.user import User
from app.routes import products as product_routes
from app.repositories.dashboard_repository import DashboardRepository
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
        username=f"catalogue_{role}",
        email=f"catalogue_{role}@example.test",
        password="test-only-password",
        role=role,
        is_active=True,
        active=True,
    )
    db.add(utilisateur)
    db.flush()
    return utilisateur


def creer_produit(db, suffixe, active=True):
    produit = creer_modele(
        Product,
        reference=f"REF-CATALOGUE-{suffixe}",
        barcode=f"BAR-CATALOGUE-{suffixe}",
        name=f"Produit catalogue {suffixe}",
        description="Produit de test",
        category="Test",
        purchase_price=600.0,
        selling_price=1000.0,
        quantity=10,
        alert_stock=2,
        minimum_stock=2,
        active=active,
    )
    db.add(produit)
    db.flush()
    return produit


@pytest.fixture
def catalogue_client(db):
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

    def override_current_admin():
        utilisateur = override_current_user()

        if utilisateur.role != "admin":
            raise HTTPException(
                status_code=403,
                detail="Acces reserve a l'administrateur.",
            )

        return utilisateur

    app.dependency_overrides[product_routes.get_db] = lambda: db
    app.dependency_overrides[
        product_routes.get_current_user
    ] = override_current_user
    app.dependency_overrides[
        auth.get_current_user
    ] = override_current_user
    app.dependency_overrides[
        product_routes.get_current_admin
    ] = override_current_admin

    client = TestClient(app)

    try:
        yield client, utilisateur_courant
    finally:
        client.close()
        app.dependency_overrides.clear()
        app.dependency_overrides.update(anciens_overrides)


def test_catalogue_returns_only_active_products(
    db,
    catalogue_client,
):
    client, utilisateur_courant = catalogue_client

    utilisateur = creer_utilisateur(db, "vendeur")
    produit_actif = creer_produit(db, "ACTIF", active=True)
    creer_produit(db, "ARCHIVE", active=False)

    db.commit()
    utilisateur_courant["value"] = utilisateur

    response = client.get("/products/")

    assert response.status_code == 200

    references = {
        produit["reference"]
        for produit in response.json()
    }

    assert references == {produit_actif.reference}


def test_admin_can_list_archived_products(
    db,
    catalogue_client,
):
    client, utilisateur_courant = catalogue_client

    utilisateur = creer_utilisateur(db, "admin")
    produit_archive = creer_produit(
        db,
        "ARCHIVE-ADMIN",
        active=False,
    )
    creer_produit(db, "ACTIF-ADMIN", active=True)

    db.commit()
    utilisateur_courant["value"] = utilisateur

    response = client.get("/products/archived")

    assert response.status_code == 200

    references = {
        produit["reference"]
        for produit in response.json()
    }

    assert references == {produit_archive.reference}


def test_vendor_cannot_list_archived_products(
    db,
    catalogue_client,
):
    client, utilisateur_courant = catalogue_client

    utilisateur = creer_utilisateur(db, "vendeur")
    creer_produit(db, "ARCHIVE-VENDOR", active=False)

    db.commit()
    utilisateur_courant["value"] = utilisateur

    response = client.get("/products/archived")

    assert response.status_code == 403


def test_vendor_cannot_get_archived_product_by_id(
    db,
    catalogue_client,
):
    client, utilisateur_courant = catalogue_client

    utilisateur = creer_utilisateur(db, "vendeur")
    produit = creer_produit(
        db,
        "DETAIL-VENDOR",
        active=False,
    )

    db.commit()
    utilisateur_courant["value"] = utilisateur

    response = client.get(f"/products/{produit.id}")

    assert response.status_code == 404


def test_admin_can_get_archived_product_by_id(
    db,
    catalogue_client,
):
    client, utilisateur_courant = catalogue_client

    utilisateur = creer_utilisateur(db, "admin")
    produit = creer_produit(
        db,
        "DETAIL-ADMIN",
        active=False,
    )

    db.commit()
    utilisateur_courant["value"] = utilisateur

    response = client.get(f"/products/{produit.id}")

    assert response.status_code == 200
    assert response.json()["active"] is False
    assert response.json()["reference"] == produit.reference


def test_dashboard_counts_active_and_archived_products(db):
    creer_produit(db, "DASHBOARD-ACTIF", active=True)
    creer_produit(db, "DASHBOARD-ARCHIVE", active=False)

    db.commit()

    assert DashboardRepository.count_products(db) == 2
