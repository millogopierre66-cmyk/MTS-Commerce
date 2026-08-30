from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    reference: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False
    )

    barcode: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False
    )

    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False
    )

    description: Mapped[str] = mapped_column(
        String(500),
        default=""
    )

    category: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    purchase_price: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    selling_price: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    quantity: Mapped[int] = mapped_column(
        Integer,
        default=0
    )

    # AJOUT IMPORTANT
    alert_stock: Mapped[int] = mapped_column(
        Integer,
        default=5,
        nullable=False
    )

    minimum_stock: Mapped[float] = mapped_column(
        Float,
        default=5,
        nullable=False
    )

    active: Mapped[bool] = mapped_column(
        Boolean,
        default=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    movements = relationship(
        "StockMovement",
        back_populates="product",
        cascade="all, delete"
    )