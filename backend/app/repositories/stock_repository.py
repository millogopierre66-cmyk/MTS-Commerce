from sqlalchemy.orm import Session

from app.models.stock_movement import StockMovement

from app.models.product import Product


class StockRepository:

    @staticmethod
    def create(
        db: Session,
        movement: StockMovement
    ):
        db.add(movement)
        db.commit()
        db.refresh(movement)
        return movement

    @staticmethod
    def get_all(
        db: Session
    ):
        return (
            db.query(StockMovement)
            .order_by(
                StockMovement.created_at.desc()
            )
            .all()
        )

    @staticmethod
    def get_by_id(
        db: Session,
        movement_id: int
    ):
        return (
            db.query(StockMovement)
            .filter(
                StockMovement.id == movement_id
            )
            .first()
        )

    @staticmethod
    def get_by_product(
        db: Session,
        product_id: int
    ):
        return (
            db.query(StockMovement)
            .filter(
                StockMovement.product_id == product_id
            )
            .order_by(
                StockMovement.created_at.desc()
            )
            .all()
        )

    @staticmethod
    def get_entries(
        db: Session
    ):
        return (
            db.query(StockMovement)
            .filter(
                StockMovement.movement_type == "IN"
            )
            .all()
        )

    @staticmethod
    def get_outputs(
        db: Session
    ):
        return (
            db.query(StockMovement)
            .filter(
                StockMovement.movement_type == "OUT"
            )
            .all()
        )

    @staticmethod
    def get_current_stock(
        db: Session,
        product_id: int
    ):
        product = (
            db.query(Product)
            .filter(
                Product.id == product_id
            )
            .first()
        )

        if not product:
            return 0

        return product.quantity
    
    @staticmethod
    def get_stock_value(
        db: Session,
        product
    ):
        stock = StockRepository.get_current_stock(
            db,
            product.id
        )

        return stock * product.selling_price

    @staticmethod
    def count(
        db: Session
    ):
        return (
            db.query(StockMovement)
            .count()
        )
    @staticmethod
    def total_movements(
        db: Session
    ):
        return (
            db.query(StockMovement)
            .count()
        )
    @staticmethod
    def out_of_stock(
        db: Session
    ):
        return (
            db.query(Product)
            .filter(
                Product.quantity <= 0
            )
            .all()
        )

    @staticmethod
    def low_stock(
        db: Session
    ):
        return (
            db.query(Product)
            .filter(
                Product.quantity > 0,
                Product.quantity <= Product.alert_stock
            )
            .all()
        )

    @staticmethod
    def total_stock_value(
        db: Session
    ):
        products = (
            db.query(Product)
            .all()
        )

        total = 0

        for product in products:
            total += (
                product.quantity *
                product.selling_price
            )

        return total