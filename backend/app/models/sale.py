from datetime import datetime

from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.database.base import Base


class Sale(Base):

    __tablename__ = "sales"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    invoice_number: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False
    )

    customer_id: Mapped[int | None] = mapped_column(
        ForeignKey("customers.id"),
        nullable=True
    )

    total: Mapped[float] = mapped_column(
        Float,
        default=0
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    customer = relationship(
        "Customer",
        back_populates="sales"
    )

    items = relationship(
        "SaleItem",
        back_populates="sale",
        cascade="all, delete"
    )