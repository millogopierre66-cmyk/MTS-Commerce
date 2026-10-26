"""add stock movement type constraint

Revision ID: 69f0a3c8fb89
Revises: 5d564330ccf6
Create Date: 2026-09-09 16:42:42.398741

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "69f0a3c8fb89"
down_revision: Union[str, Sequence[str], None] = "5d564330ccf6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add a constraint restricting stock movement types."""

    with op.batch_alter_table("stock_movements") as batch_op:
        batch_op.create_check_constraint(
            "ck_stock_movements_movement_type",
            "movement_type IN ('IN', 'OUT', 'ADJUSTMENT')",
        )


def downgrade() -> None:
    """Remove the stock movement type constraint."""

    with op.batch_alter_table("stock_movements") as batch_op:
        batch_op.drop_constraint(
            "ck_stock_movements_movement_type",
            type_="check",
        )