from datetime import UTC, datetime

from sqlalchemy import (
    CheckConstraint,
    Integer,
    String,
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
    __table_args__ = (
        CheckConstraint(
            "movement_type IN ('IN', 'OUT', 'ADJUSTMENT')",
            name="ck_stock_movements_movement_type",
        ),
        CheckConstraint(
            "(movement_type IN ('IN', 'OUT') AND quantity > 0) "
            "OR "
            "(movement_type = 'ADJUSTMENT' AND quantity <> 0)",
            name="ck_stock_movements_quantity",
        ),
    )
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id"),
        nullable=False
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False
    )

    quantity: Mapped[int] = mapped_column(
         Integer,
        nullable=False
    )

    movement_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    description: Mapped[str] = mapped_column(
        String(255),
        default="",
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(UTC).replace(tzinfo=None),
        nullable=False
    )

    product = relationship(
        "Product",
        back_populates="movements"
    )

    user = relationship(
        "User"
    )
