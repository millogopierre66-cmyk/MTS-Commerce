from app.database.connection import engine
from app.database.base import Base

from app.database.init_admin import create_admin
from app.database.session import SessionLocal


from app.models.user import User
from app.models.product import Product
from app.models.stock_movement import StockMovement
from app.models.sale import Sale
from app.models.sale_item import SaleItem
from app.models.customer import Customer
from app.models.expense import Expense
from app.models.audit_log import AuditLog


# ==========================================================
# INITIALISATION DE LA BASE
# ==========================================================

def init_db():

    Base.metadata.create_all(
        bind=engine
    )

    db = SessionLocal()

    try:
        create_admin(db)

    finally:
        db.close()