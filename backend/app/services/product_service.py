from app.models.sale_item import SaleItem
from app.models.stock_movement import StockMovement
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.product import Product
from app.repositories.product_repository import ProductRepository
from app.schemas.product import ProductCreate, ProductUpdate


class ProductService:

    @staticmethod
    def create(db: Session, data: ProductCreate):

        # Vérifier l'unicité de la référence
        existing_reference = ProductRepository.get_by_reference(
            db,
            data.reference
        )

        if existing_reference:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cette référence produit existe déjà."
            )

        # Vérifier l'unicité du code-barres
        existing_barcode = ProductRepository.get_by_barcode(
            db,
            data.barcode
        )

        if existing_barcode:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ce code-barres est déjà utilisé."
            )

        product = Product(
            reference=data.reference,
            barcode=data.barcode,
            name=data.name,
            description=data.description,
            category=data.category,
            purchase_price=data.purchase_price,
            selling_price=data.selling_price,
            quantity=data.quantity,
            alert_stock=data.alert_stock,
            minimum_stock=data.minimum_stock,
            active=data.active
        )

        return ProductRepository.create(
            db,
            product
        )
            
    @staticmethod
    def get_all(db: Session):
        return ProductRepository.get_all(db)

    @staticmethod
    def get_one(db: Session, product_id: int):

        product = ProductRepository.get_by_id(
            db,
            product_id
        )

        if not product:
            raise HTTPException(
                status_code=404,
                detail="Produit introuvable."
            )

        return product

    @staticmethod
    def update(
        db: Session,
        product_id: int,
        data: ProductUpdate
    ):

        # Vérifier que le produit existe
        product = ProductRepository.get_by_id(
            db,
            product_id
        )

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Produit introuvable."
            )

        # Vérifier l'unicité de la référence
        if data.reference is not None:

            existing_product = (
                ProductRepository.get_by_reference(
                    db,
                    data.reference
                )
            )

            if (
                existing_product
                and existing_product.id != product_id
            ):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cette référence est déjà utilisée."
                )

        # Vérifier l'unicité du code-barres
        if data.barcode is not None:

            existing_product = (
                ProductRepository.get_by_barcode(
                    db,
                    data.barcode
                )
            )

            if (
                existing_product
                and existing_product.id != product_id
            ):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Ce code-barres est déjà utilisé."
                )

        # Mise à jour
        return ProductRepository.update(
            db,
            product,
            data
        )
    @staticmethod
    def delete(
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

        # Verifier si le produit est utilise dans des ventes
        sales_count = (
            db.query(SaleItem)
            .filter(SaleItem.product_id == product_id)
            .count()
        )

        if sales_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Impossible de supprimer ce produit : "
                    f"{sales_count} vente(s) sont liees a ce produit."
                )
            )

        # Verifier si le produit possede des mouvements de stock
        movements_count = (
            db.query(StockMovement)
            .filter(StockMovement.product_id == product_id)
            .count()
        )

        if movements_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Impossible de supprimer ce produit : "
                    f"{movements_count} mouvement(s) de stock sont lies a ce produit."
                )
            )

        ProductRepository.delete(
            db,
            product
        )

        return {
            "message": "Produit supprime avec succes."
        }


    