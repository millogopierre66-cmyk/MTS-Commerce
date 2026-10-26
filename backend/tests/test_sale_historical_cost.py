import importlib
import pkgutil
from unittest.mock import patch

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database.base import Base
import app.models

for module in pkgutil.iter_modules(app.models.__path__):
    importlib.import_module(f"app.models.{module.name}")

from app.models.user import User
from app.models.product import Product
from app.models.sale_item import SaleItem
from app.schemas.sale import SaleCreate, SaleItemCreate
from app.services.sale_service import SaleService


@pytest.fixture
def db():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    SessionTest = sessionmaker(
        bind=engine,
        autoflush=False,
        expire_on_commit=False,
    )
    session = SessionTest()

    try:
        yield session
    finally:
        session.rollback()
        session.close()
        engine.dispose()


def creer_modele(modele, **valeurs):
    attributs = set(modele.__mapper__.attrs.keys())
    return modele(**{
        cle: valeur
        for cle, valeur in valeurs.items()
        if cle in attributs
    })


def test_sale_preserves_historical_purchase_cost(db):
    utilisateur = creer_modele(
        User,
        username="test_cout_historique",
        email="test_cout_historique@example.test",
        password="test-only-password",
        role="admin",
        is_active=True,
        active=True,
    )

    produit = creer_modele(
        Product,
        ref="REF-SNAPSHOT-001",
        reference="REF-SNAPSHOT-001",
        barcode="BAR-SNAPSHOT-001",
        name="Produit test cout historique",
        description="Test en memoire",
        category="Test",
        purchase_price=600.0,
        selling_price=1000.0,
        quantity=10,
        stock=10,
        stock_quantity=10,
        qty=10,
        alert_stock=2,
        minimum_stock=2,
        is_active=True,
        active=True,
    )

    db.add_all([utilisateur, produit])
    db.commit()

    quantite_initiale = produit.quantity

    demande = SaleCreate(
        items=[
            SaleItemCreate(
                product_id=produit.id,
                quantity=2,
            )
        ]
    )

    with patch(
        "app.services.sale_service.InvoiceNumberService.reserve_invoice_number",
        return_value="FAC-TEST-SNAPSHOT-0001",
    ):
        vente = SaleService.create_sale(
            db=db,
            data=demande,
            current_user=utilisateur,
        )

    db.refresh(vente)

    ligne = (
        db.query(SaleItem)
        .filter(SaleItem.sale_id == vente.id)
        .one()
    )

    assert vente.total == 2000.0
    assert ligne.quantity == 2
    assert ligne.unit_price == 1000.0
    assert ligne.purchase_unit_price == 600.0

    produit_apres_vente = db.get(Product, produit.id)
    assert produit_apres_vente.quantity == quantite_initiale - 2

    produit_apres_vente.purchase_price = 750.0
    db.commit()

    db.refresh(ligne)
    assert produit_apres_vente.purchase_price == 750.0
    assert ligne.purchase_unit_price == 600.0
    assert (
        ligne.subtotal
        - ligne.quantity * ligne.purchase_unit_price
    ) == 800.0
