from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.constants import (
    STOCK_IN,
    STOCK_OUT,
    STOCK_ADJUSTMENT,
)

from app.models.stock_movement import StockMovement

from app.repositories.product_repository import ProductRepository
from app.repositories.stock_repository import StockRepository

from app.schemas.stock import StockIn, StockOut


class StockService:

    @staticmethod
    def _get_product(
        db: Session,
        product_id: int,
        require_active: bool = False,
    ):
        product = ProductRepository.get_by_id(db, product_id)

        if product is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Produit introuvable.",
            )

        if require_active and not product.active:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Le produit est desactive; operation interdite.",
            )

        return product

    @staticmethod
    def stock_in(
        db: Session,
        data: StockIn,
        current_user,
    ):
        if data.quantity <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La quantite doit etre superieure a zero.",
            )

        StockService._get_product(db, data.product_id, require_active=True)

        try:
            updated = StockRepository.increment_stock_atomic(
                db,
                data.product_id,
                data.quantity,
            )

            if not updated:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Produit introuvable pendant l'operation.",
                )

            movement = StockMovement(
                product_id=data.product_id,
                user_id=current_user.id,
                quantity=data.quantity,
                movement_type=STOCK_IN,
                description=data.description,
            )

            StockRepository.create_movement(db, movement)
            db.commit()
            db.refresh(movement)

            return movement

        except Exception:
            db.rollback()
            raise

    @staticmethod
    def stock_out(
        db: Session,
        data: StockOut,
        current_user,
    ):
        if data.quantity <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La quantite doit etre superieure a zero.",
            )

        product = StockService._get_product(db, data.product_id, require_active=True)

        if product.quantity < data.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Stock insuffisant.",
            )

        try:
            updated = StockRepository.decrement_stock_atomic(
                db,
                data.product_id,
                data.quantity,
            )

            if not updated:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=(
                        "Le stock a change pendant l'operation. "
                        "Veuillez reessayer."
                    ),
                )

            movement = StockMovement(
                product_id=data.product_id,
                user_id=current_user.id,
                quantity=data.quantity,
                movement_type=STOCK_OUT,
                description=data.description,
            )

            StockRepository.create_movement(db, movement)
            db.commit()
            db.refresh(movement)

            return movement

        except Exception:
            db.rollback()
            raise

    @staticmethod
    def adjust_stock(
        db: Session,
        product_id: int,
        quantity: int,
        current_user,
        description: str = "Ajustement de stock",
    ):
        if quantity < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La quantite ne peut pas etre negative.",
            )

        product = StockService._get_product(
            db, product_id, require_active=True
        )

        old_quantity = product.quantity
        difference = quantity - old_quantity

        if difference == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La quantite est identique au stock actuel.",
            )

        try:
            updated = StockRepository.adjust_stock_atomic(
                db,
                product_id,
                old_quantity,
                quantity,
            )

            if not updated:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=(
                        "Le stock a change pendant l'ajustement. "
                        "Veuillez recommencer l'inventaire."
                    ),
                )

            movement = StockMovement(
                product_id=product_id,
                user_id=current_user.id,
                quantity=difference,
                movement_type=STOCK_ADJUSTMENT,
                description=(
                    f"{description} | "
                    f"Ancien stock: {old_quantity} | "
                    f"Nouveau stock: {quantity} | "
                    f"Variation: {difference:+}"
                ),
            )

            StockRepository.create_movement(db, movement)
            db.commit()
            db.refresh(movement)

            return movement

        except Exception:
            db.rollback()
            raise

    @staticmethod
    def get_stock(db: Session, product_id: int):
        product = StockService._get_product(db, product_id)

        return {
            "product": product.name,
            "reference": product.reference,
            "stock": product.quantity,
        }

    @staticmethod
    def get_history(db: Session, product_id: int):
        StockService._get_product(db, product_id)

        return StockRepository.get_by_product(
            db,
            product_id,
        )
