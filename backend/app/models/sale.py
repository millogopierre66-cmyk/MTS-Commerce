from datetime import UTC, datetime

from sqlalchemy import (
    CheckConstraint,
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
    __table_args__ = (
        CheckConstraint(
            "status IN ('completed', 'cancelled')",
            name="ck_sales_status",
        ),
        CheckConstraint(
            "total >= 0 AND total <= 1.7976931348623157e308",
            name="ck_sales_total_valid",
        ),
    )

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

    # Utilisateur ayant créé la vente
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False
    )

    total: Mapped[float] = mapped_column(
        Float,
        default=0,
        nullable=False
    )

    # ----------------------------------------------------------
    # STATUT DE LA VENTE
    # ----------------------------------------------------------

    status: Mapped[str] = mapped_column(
        String(20),
        default="completed",
        nullable=False
    )

    # ----------------------------------------------------------
    # INFORMATIONS D'ANNULATION
    # ----------------------------------------------------------

    cancelled_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    cancelled_by: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"),
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(UTC).replace(tzinfo=None),
        nullable=False
    )

    # ----------------------------------------------------------
    # RELATIONS
    # ----------------------------------------------------------

    customer = relationship(
        "Customer",
        back_populates="sales"
    )

    user = relationship(
        "User",
        foreign_keys=[user_id]
    )

    cancelled_by_user = relationship(
        "User",
        foreign_keys=[cancelled_by]
    )

    items = relationship(
        "SaleItem",
        back_populates="sale"
    )