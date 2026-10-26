"""add sale status constraint

Revision ID: 5d564330ccf6
Revises: 27781231c160
Create Date: 2026-09-04 15:08:19.369499

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5d564330ccf6'
down_revision: Union[str, Sequence[str], None] = '27781231c160'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table("sales") as batch_op:
        batch_op.create_check_constraint(
            "ck_sales_status",
            "status IN ('completed', 'cancelled')"
        )


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("sales") as batch_op:
        batch_op.drop_constraint(
            "ck_sales_status",
            type_="check"
        )