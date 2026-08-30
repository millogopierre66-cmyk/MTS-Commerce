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

from app.schemas.stock import (
    StockIn,
    StockOut,
)


class StockService:

    # ==========================================================
    # ENTRÉE DE STOCK
    # ==========================================================

    @staticmethod
    def stock_in(
        db: Session,
        data: StockIn
    ):
        product = ProductRepository.get_by_id(
            db,
            data.product_id
        )

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Produit introuvable."
            )

        if data.quantity <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La quantité doit être supérieure à zéro."
            )

        # Mise à jour du stock courant
        product.quantity += data.quantity

        # Historique du mouvement
        movement = StockMovement(
            product_id=data.product_id,
            quantity=data.quantity,
            movement_type=STOCK_IN,
            description=data.description
        )

        db.add(movement)
        db.commit()
        db.refresh(movement)

        return movement

    # ==========================================================
    # SORTIE DE STOCK
    # ==========================================================

    @staticmethod
    def stock_out(
        db: Session,
        data: StockOut
    ):
        product = ProductRepository.get_by_id(
            db,
            data.product_id
        )

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Produit introuvable."
            )

        if data.quantity <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La quantité doit être supérieure à zéro."
            )

        # Le stock courant officiel est Product.quantity
        if product.quantity < data.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Stock insuffisant."
            )

        # Mise à jour du stock courant
        product.quantity -= data.quantity

        # Historique du mouvement
        movement = StockMovement(
            product_id=data.product_id,
            quantity=data.quantity,
            movement_type=STOCK_OUT,
            description=data.description
        )

        db.add(movement)
        db.commit()
        db.refresh(movement)

        return movement

    # ==========================================================
    # CONSULTATION DU STOCK
    # ==========================================================

    @staticmethod
    def get_stock(
        db: Session,
        product_id: int
    ):
        product = ProductRepository.get_by_id(
            db,
            product_id
        )

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Produit introuvable."
            )

        return {
            "product": product.name,
            "reference": product.reference,
            "stock": product.quantity
        }

    # ==========================================================
    # HISTORIQUE
    # ==========================================================

    @staticmethod
    def get_history(
        db: Session,
        product_id: int
    ):
        product = ProductRepository.get_by_id(
            db,
            product_id
        )

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Produit introuvable."
            )

        return StockRepository.get_by_product(
            db,
            product_id
        )

    # ==========================================================
    # AJUSTEMENT DE STOCK
    # ==========================================================

    @staticmethod
    def adjust_stock(
        db: Session,
        product_id: int,
        quantity: int,
        description: str = "Ajustement de stock"
    ):
        product = ProductRepository.get_by_id(
            db,
            product_id
        )

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Produit introuvable."
            )

        if quantity < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La quantité ne peut pas être négative."
            )

        old_quantity = product.quantity

        # Variation réelle
        difference = quantity - old_quantity

        # Nouveau stock
        product.quantity = quantity

        movement = StockMovement(
            product_id=product_id,
            quantity=difference,
            movement_type=STOCK_ADJUSTMENT,
            description=(
                f"{description} | "
                f"Ancien stock: {old_quantity} | "
                f"Nouveau stock: {quantity} | "
                f"Variation: {difference:+}"
            )
        )

        db.add(movement)
        db.commit()
        db.refresh(movement)

        return movement


    