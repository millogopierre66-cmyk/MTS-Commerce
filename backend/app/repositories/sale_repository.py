from datetime import datetime

from sqlalchemy import update
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

    @staticmethod
    def count_sales(db: Session) -> int:
        return db.query(Sale).count()

    @staticmethod
    def cancel_if_completed(
        db: Session,
        sale_id: int,
        cancelled_at: datetime,
        cancelled_by: int,
    ) -> bool:
        """
        Modifie le statut seulement si la vente est encore termin?e.
        Une deuxi?me annulation concurrente ne peut donc pas restaurer
        le stock une seconde fois.
        """
        result = db.execute(
            update(Sale)
            .where(
                Sale.id == sale_id,
                Sale.status == "completed",
            )
            .values(
                status="cancelled",
                cancelled_at=cancelled_at,
                cancelled_by=cancelled_by,
            )
            .execution_options(synchronize_session=False)
        )
        return result.rowcount == 1

    @staticmethod
    def delete(db: Session, sale: Sale):
        # M?thode historique conserv?e pour compatibilit?.
        # Le parcours normal d'annulation passe d?sormais par
        # SaleService.cancel_sale afin de pr?server l'historique.
        db.delete(sale)
        db.commit()
