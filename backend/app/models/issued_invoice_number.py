from datetime import UTC, datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class IssuedInvoiceNumber(Base):

    __tablename__ = "issued_invoice_numbers"

    invoice_number: Mapped[str] = mapped_column(
        String(50),
        primary_key=True
    )

    issued_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(UTC).replace(tzinfo=None),
        nullable=False
    )