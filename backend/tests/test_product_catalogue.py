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

def test_catalogue_search_filters_active_products_only(
    db,
    catalogue_client,
):
    client, utilisateur_courant = catalogue_client

    utilisateur = creer_utilisateur(db, "vendeur")

    produit_actif = creer_produit(db, "SOURIS-USB")
    creer_produit(db, "CLAVIER-USB")
    creer_produit(db, "SOURIS-ARCHIVE", active=False)

    db.commit()
    utilisateur_courant["value"] = utilisateur

    response = client.get(
        "/products/catalogue",
        params={"q": "sOuRiS"},
    )

    assert response.status_code == 200

    resultat = response.json()

    assert resultat["total"] == 1
    assert resultat["total_pages"] == 1
    assert len(resultat["items"]) == 1
    assert resultat["items"][0]["reference"] == produit_actif.reference


def test_catalogue_search_by_reference_and_barcode(
    db,
    catalogue_client,
):
    client, utilisateur_courant = catalogue_client

    utilisateur = creer_utilisateur(db, "vendeur")
    produit = creer_produit(db, "RECHERCHE-CODE")

    db.commit()
    utilisateur_courant["value"] = utilisateur

    response_reference = client.get(
        "/products/catalogue",
        params={"q": produit.reference},
    )

    response_barcode = client.get(
        "/products/catalogue",
        params={"q": produit.barcode},
    )

    assert response_reference.status_code == 200
    assert response_barcode.status_code == 200

    assert response_reference.json()["total"] == 1
    assert response_barcode.json()["total"] == 1

    assert (
        response_reference.json()["items"][0]["id"]
        == produit.id
    )

    assert (
        response_barcode.json()["items"][0]["id"]
        == produit.id
    )


def test_catalogue_filter_by_category(
    db,
    catalogue_client,
):
    client, utilisateur_courant = catalogue_client

    utilisateur = creer_utilisateur(db, "vendeur")

    produit_informatique = creer_produit(
        db,
        "CAT-INFORMATIQUE",
    )
    produit_informatique.category = "Informatique"

    produit_bureau = creer_produit(
        db,
        "CAT-BUREAU",
    )
    produit_bureau.category = "Bureau"

    produit_archive = creer_produit(
        db,
        "CAT-ARCHIVE",
        active=False,
    )
    produit_archive.category = "Informatique"

    db.commit()
    utilisateur_courant["value"] = utilisateur

    response = client.get(
        "/products/catalogue",
        params={"category": "Informatique"},
    )

    assert response.status_code == 200

    resultat = response.json()

    assert resultat["total"] == 1
    assert len(resultat["items"]) == 1
    assert (
        resultat["items"][0]["reference"]
        == produit_informatique.reference
    )


def test_catalogue_pagination(
    db,
    catalogue_client,
):
    client, utilisateur_courant = catalogue_client

    utilisateur = creer_utilisateur(db, "vendeur")

    for numero in range(1, 6):
        creer_produit(db, f"PAGINATION-{numero}")

    creer_produit(
        db,
        "PAGINATION-ARCHIVE",
        active=False,
    )

    db.commit()
    utilisateur_courant["value"] = utilisateur

    page_1 = client.get(
        "/products/catalogue",
        params={"page": 1, "page_size": 2},
    )

    page_2 = client.get(
        "/products/catalogue",
        params={"page": 2, "page_size": 2},
    )

    page_3 = client.get(
        "/products/catalogue",
        params={"page": 3, "page_size": 2},
    )

    assert page_1.status_code == 200
    assert page_2.status_code == 200
    assert page_3.status_code == 200

    resultat_1 = page_1.json()
    resultat_2 = page_2.json()
    resultat_3 = page_3.json()

    assert resultat_1["total"] == 5
    assert resultat_1["page"] == 1
    assert resultat_1["page_size"] == 2
    assert resultat_1["total_pages"] == 3

    assert len(resultat_1["items"]) == 2
    assert len(resultat_2["items"]) == 2
    assert len(resultat_3["items"]) == 1

    ids_1 = {
        produit["id"]
        for produit in resultat_1["items"]
    }

    ids_2 = {
        produit["id"]
        for produit in resultat_2["items"]
    }

    ids_3 = {
        produit["id"]
        for produit in resultat_3["items"]
    }

    assert ids_1.isdisjoint(ids_2)
    assert ids_1.isdisjoint(ids_3)
    assert ids_2.isdisjoint(ids_3)


def test_catalogue_rejects_invalid_pagination(
    db,
    catalogue_client,
):
    client, utilisateur_courant = catalogue_client

    utilisateur = creer_utilisateur(db, "vendeur")
    db.commit()

    utilisateur_courant["value"] = utilisateur

    response_page = client.get(
        "/products/catalogue",
        params={"page": 0},
    )

    response_page_size = client.get(
        "/products/catalogue",
        params={"page_size": 101},
    )

    assert response_page.status_code == 422
    assert response_page_size.status_code == 422

    assert any(
        error.get("loc") == ["query", "page"]
        for error in response_page.json()["detail"]
    )

    assert any(
        error.get("loc") == ["query", "page_size"]
        for error in response_page_size.json()["detail"]
    )
