from sqlalchemy import Float
from sqlalchemy import ForeignKey
from sqlalchemy import Integer

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from app.database.base import Base


class SaleItem(Base):

    __tablename__ = "sale_items"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    sale_id: Mapped[int] = mapped_column(
        ForeignKey("sales.id")
    )

    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id")
    )

    quantity: Mapped[int] = mapped_column(
        Integer
    )

    unit_price: Mapped[float] = mapped_column(
        Float
    )

    subtotal: Mapped[float] = mapped_column(
        Float
    )

    sale = relationship(
        "Sale",
        back_populates="items"
    )

    product = relationship("Product")