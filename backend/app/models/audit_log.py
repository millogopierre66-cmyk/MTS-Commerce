from datetime import UTC, datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    # ==========================================================
    # UTILISATEUR
    # ==========================================================

    user_id: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        index=True
    )

    username: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    # ==========================================================
    # ACTION
    # ==========================================================

    action: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True
    )

    # ==========================================================
    # ENTITÉ CONCERNÉE
    # ==========================================================

    entity_type: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True
    )

    entity_id: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        index=True
    )

    # ==========================================================
    # DESCRIPTION
    # ==========================================================

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    # ==========================================================
    # INFORMATIONS TECHNIQUES
    # ==========================================================

    ip_address: Mapped[str | None] = mapped_column(
        String(45),
        nullable=True
    )

    # ==========================================================
    # DATE
    # ==========================================================

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(UTC).replace(tzinfo=None),
        nullable=False,
        index=True
    )