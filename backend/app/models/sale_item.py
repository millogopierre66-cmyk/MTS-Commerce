from sqlalchemy import Float
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import CheckConstraint

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from app.database.base import Base


class SaleItem(Base):

    __tablename__ = "sale_items"
    __table_args__ = (
        CheckConstraint("quantity > 0", name="ck_sale_items_quantity_positive"),
        CheckConstraint(
            "unit_price >= 0 AND unit_price <= 1.7976931348623157e308",
            name="ck_sale_items_unit_price_valid",
        ),
        CheckConstraint(
            "subtotal >= 0 AND subtotal <= 1.7976931348623157e308",
            name="ck_sale_items_subtotal_valid",
        ),
        CheckConstraint(
            "purchase_unit_price IS NULL OR "
            "(purchase_unit_price >= 0 AND "
            "purchase_unit_price <= 1.7976931348623157e308)",
            name="ck_sale_items_purchase_price_valid",
        ),
    )
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    sale_id: Mapped[int] = mapped_column(
        ForeignKey("sales.id"),
        nullable=False
    )

    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id"),
        nullable=False
    )

    quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    # Prix de vente appliqué au moment de la vente
    unit_price: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    # Prix d'achat du produit au moment de la vente.
    #
    # Nullable temporairement pour préserver les anciens
    # SaleItem dont le prix d'achat historique n'est pas connu.
    purchase_unit_price: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )

    subtotal: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    sale = relationship(
        "Sale",
        back_populates="items"
    )

    product = relationship("Product")