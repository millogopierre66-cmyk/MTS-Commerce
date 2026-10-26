from datetime import datetime, timedelta
import importlib
import pkgutil

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
from app.models.sale import Sale
from app.models.sale_item import SaleItem


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


def build_model(model, **values):
    mapped_names = set(model.__mapper__.attrs.keys())
    return model(**{
        key: value
        for key, value in values.items()
        if key in mapped_names
    })


@pytest.fixture
def accounting_data(db):
    now = datetime.now()

    user = build_model(
        User,
        username="pytest_accounting_admin",
        email="pytest_accounting_admin@example.test",
        password="test-only-password",
        role="admin",
        is_active=True,
        active=True,
    )
    db.add(user)
    db.flush()

    product_incomplete = build_model(
        Product,
        ref="REF-PYTEST-A",
        reference="REF-PYTEST-A",
        barcode="BAR-PYTEST-A",
        name="Produit cout incomplet",
        description="Produit de test",
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

    product_complete = build_model(
        Product,
        ref="REF-PYTEST-B",
        reference="REF-PYTEST-B",
        barcode="BAR-PYTEST-B",
        name="Produit cout complet",
        description="Produit de test",
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

    db.add_all([product_incomplete, product_complete])
    db.flush()

    sale_a = build_model(
        Sale,
        invoice_number="FAC-PYTEST-001",
        invoice_no="FAC-PYTEST-001",
        user_id=user.id,
        total=2500.0,
        status="completed",
        created_at=now,
    )

    sale_b = build_model(
        Sale,
        invoice_number="FAC-PYTEST-002",
        invoice_no="FAC-PYTEST-002",
        user_id=user.id,
        total=1000.0,
        status="completed",
        created_at=now,
    )

    sale_cancelled = build_model(
        Sale,
        invoice_number="FAC-PYTEST-003",
        invoice_no="FAC-PYTEST-003",
        user_id=user.id,
        total=9000.0,
        status="cancelled",
        created_at=now - timedelta(days=1),
        cancelled_at=now - timedelta(days=1),
        cancelled_by=user.id,
        cancellation_reason="Annulation de test",
        cancel_reason="Annulation de test",
    )

    db.add_all([sale_a, sale_b, sale_cancelled])
    db.flush()

    items = [
        build_model(
            SaleItem,
            sale_id=sale_a.id,
            product_id=product_incomplete.id,
            quantity=2,
            unit_price=1000.0,
            purchase_unit_price=600.0,
            subtotal=2000.0,
        ),
        build_model(
            SaleItem,
            sale_id=sale_a.id,
            product_id=product_incomplete.id,
            quantity=1,
            unit_price=500.0,
            purchase_unit_price=None,
            subtotal=500.0,
        ),
        build_model(
            SaleItem,
            sale_id=sale_b.id,
            product_id=product_complete.id,
            quantity=1,
            unit_price=1000.0,
            purchase_unit_price=600.0,
            subtotal=1000.0,
        ),
        build_model(
            SaleItem,
            sale_id=sale_cancelled.id,
            product_id=product_incomplete.id,
            quantity=1,
            unit_price=9000.0,
            purchase_unit_price=None,
            subtotal=9000.0,
        ),
    ]

    db.add_all(items)
    db.commit()

    return {
        "user": user,
        "product_incomplete": product_incomplete,
        "product_complete": product_complete,
        "sale_a": sale_a,
        "sale_b": sale_b,
        "sale_cancelled": sale_cancelled,
    }
