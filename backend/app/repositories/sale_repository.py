from sqlalchemy.orm import Session

from app.models.sale import Sale
from app.models.sale_item import SaleItem


class SaleRepository:

    @staticmethod
    def create_sale(db: Session, sale: Sale):

        db.add(sale)
        db.flush()
        return sale

    @staticmethod
    def add_item(db: Session, item: SaleItem):

        db.add(item)

    @staticmethod
    def commit(db: Session):

        db.commit()

    @staticmethod
    def refresh(db: Session, sale: Sale):

        db.refresh(sale)
        return sale

    @staticmethod
    def get_by_id(db: Session, sale_id: int):

        return (
            db.query(Sale)
            .filter(Sale.id == sale_id)
            .first()
        )

    @staticmethod
    def get_all(db: Session):

        return (
            db.query(Sale)
            .order_by(Sale.created_at.desc())
            .all()
        )

    # ==========================================================
    # NOMBRE TOTAL DE VENTES
    # ==========================================================

    @staticmethod
    def count_sales(db: Session) -> int:

        return db.query(Sale).count()

    @staticmethod
    def delete(db: Session, sale: Sale):

        db.delete(sale)
        db.commit()