from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.product import Product
from app.repositories.product_repository import ProductRepository
from app.schemas.product import ProductCreate, ProductUpdate
from app.services.audit_log_service import AuditLogService


class ProductService:

    @staticmethod
    def create(db: Session, data: ProductCreate):
        existing_reference = ProductRepository.get_by_reference(
            db,
            data.reference,
        )

        if existing_reference:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cette reference produit existe deja.",
            )

        existing_barcode = ProductRepository.get_by_barcode(
            db,
            data.barcode,
        )

        if existing_barcode:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ce code-barres est deja utilise.",
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
            active=data.active,
        )

        return ProductRepository.create(db, product)

    @staticmethod
    def get_all(db: Session):
        return ProductRepository.get_active(db)

    @staticmethod
    def get_archived(db: Session):
        return ProductRepository.get_archived(db)

    @staticmethod
    def get_one(db: Session, product_id: int, current_user):
        product = ProductRepository.get_by_id(db, product_id)

        if product is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Produit introuvable.",
            )

        # Un produit archive n'est visible individuellement
        # que par un administrateur.
        if (
            not product.active
            and getattr(current_user, "role", None) != "admin"
        ):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Produit introuvable.",
            )

        return product

    @staticmethod
    def update(
        db: Session,
        product_id: int,
        data: ProductUpdate,
    ):
        product = ProductRepository.get_by_id(db, product_id)

        if product is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Produit introuvable.",
            )

        if data.reference is not None:
            existing_product = ProductRepository.get_by_reference(
                db,
                data.reference,
            )

            if (
                existing_product is not None
                and existing_product.id != product_id
            ):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cette reference est deja utilisee.",
                )

        if data.barcode is not None:
            existing_product = ProductRepository.get_by_barcode(
                db,
                data.barcode,
            )

            if (
                existing_product is not None
                and existing_product.id != product_id
            ):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Ce code-barres est deja utilise.",
                )

        return ProductRepository.update(db, product, data)

    @staticmethod
    def delete(
        db: Session,
        product_id: int,
        current_user,
    ):
        product = ProductRepository.get_by_id(db, product_id)

        if product is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Produit introuvable.",
            )

        if not product.active:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ce produit est deja desactive.",
            )

        try:
            updated = ProductRepository.deactivate_if_active(
                db,
                product_id,
            )

            if not updated:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Le produit a deja ete desactive.",
                )

            AuditLogService.log(
                db=db,
                action="PRODUCT_DEACTIVATED",
                user_id=current_user.id,
                username=getattr(current_user, "username", None),
                entity_type="Product",
                entity_id=product_id,
                description=f"Desactivation du produit {product.name}.",
                commit=False,
            )

            db.commit()
            db.refresh(product)

        except Exception:
            db.rollback()
            raise

        return {
            "message": "Produit desactive avec succes.",
            "product_id": product_id,
            "active": product.active,
        }
