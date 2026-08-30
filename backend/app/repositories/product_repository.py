from sqlalchemy.orm import Session

from app.models.product import Product
from app.schemas.product import ProductUpdate


class ProductRepository:

    @staticmethod
    def create(
        db: Session,
        product: Product
    ):
        db.add(product)
        db.commit()
        db.refresh(product)

        return product

    @staticmethod
    def get_all(db: Session):
        return db.query(Product).all()

    @staticmethod
    def get_by_id(
        db: Session,
        product_id: int
    ):
        return (
            db.query(Product)
            .filter(Product.id == product_id)
            .first()
        )

    @staticmethod
    def get_by_reference(
        db: Session,
        reference: str
    ):
        return (
            db.query(Product)
            .filter(Product.reference == reference)
            .first()
        )

    @staticmethod
    def update(
        db: Session,
        product: Product,
        data: ProductUpdate
    ):

        update_data = data.model_dump(
            exclude_unset=True
        )

        for field, value in update_data.items():
            setattr(
                product,
                field,
                value
            )

        db.commit()

        db.refresh(product)

        return product
    
    @staticmethod
    def delete(
        db: Session,
        product: Product
    ):
        db.delete(product)
        db.commit()
    @staticmethod
    def get_by_reference(
        db: Session,
        reference: str
    ):
        return (
            db.query(Product)
            .filter(Product.reference == reference)
            .first()
        )
    @staticmethod
    def get_by_barcode(
        db: Session,
        barcode: str
    ):
        return (
            db.query(Product)
            .filter(Product.barcode == barcode)
            .first()
        )