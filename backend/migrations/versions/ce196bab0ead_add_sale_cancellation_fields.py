"""add sale cancellation fields

Revision ID: ce196bab0ead
Revises: e6cc63c4ae35
Create Date: 2026-09-01 18:04:03.910463

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "ce196bab0ead"
down_revision: Union[str, Sequence[str], None] = "e6cc63c4ae35"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add sale cancellation fields."""

    with op.batch_alter_table("sales") as batch_op:

        # ------------------------------------------------------
        # STATUT
        # ------------------------------------------------------
        # Les anciennes ventes deviennent automatiquement
        # "completed".
        batch_op.add_column(
            sa.Column(
                "status",
                sa.String(length=20),
                nullable=False,
                server_default="completed",
            )
        )

        # ------------------------------------------------------
        # DATE D'ANNULATION
        # ------------------------------------------------------
        batch_op.add_column(
            sa.Column(
                "cancelled_at",
                sa.DateTime(),
                nullable=True,
            )
        )

        # ------------------------------------------------------
        # UTILISATEUR AYANT ANNULÉ
        # ------------------------------------------------------
        batch_op.add_column(
            sa.Column(
                "cancelled_by",
                sa.Integer(),
                nullable=True,
            )
        )

        # ------------------------------------------------------
        # CLÉ ÉTRANGÈRE
        # ------------------------------------------------------
        batch_op.create_foreign_key(
            "fk_sales_cancelled_by_users",
            "users",
            ["cancelled_by"],
            ["id"],
        )


def downgrade() -> None:
    """Remove sale cancellation fields."""

    with op.batch_alter_table("sales") as batch_op:

        batch_op.drop_constraint(
            "fk_sales_cancelled_by_users",
            type_="foreignkey",
        )

        batch_op.drop_column("cancelled_by")
        batch_op.drop_column("cancelled_at")
        batch_op.drop_column("status")