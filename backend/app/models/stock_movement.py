from datetime import datetime

from sqlalchemy import (
    Integer,
    String,
    Float,
    DateTime,
    ForeignKey,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.database.base import Base


class StockMovement(Base):
    __tablename__ = "stock_movements"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id"),
        nullable=False
    )

    quantity: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    movement_type: Mapped[str] = mapped_column(
        String(20)
    )

    description: Mapped[str] = mapped_column(
        String(255),
        default=""
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    product = relationship(
        "Product",
        back_populates="movements"
    )