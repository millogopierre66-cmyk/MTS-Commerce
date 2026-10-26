"""align stock movement quantity type

Revision ID: 27781231c160
Revises: 4c9e28915eb6
Create Date: 2026-09-03 09:48:47.438754

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "27781231c160"
down_revision: Union[str, Sequence[str], None] = "4c9e28915eb6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Eviter la troncature silencieuse des quantites fractionnaires.
    bind = op.get_bind()
    fractional = bind.exec_driver_sql(
        "SELECT id, quantity FROM stock_movements "
        "WHERE quantity IS NOT NULL "
        "AND quantity != CAST(quantity AS INTEGER) "
        "LIMIT 10"
    ).fetchall()

    if fractional:
        raise RuntimeError(
            "Migration interrompue : stock_movements.quantity contient "
            "des quantites fractionnaires. Reconcilez ces mouvements "
            "avant la conversion vers INTEGER. Exemples : "
            f"{fractional}"
        )

    with op.batch_alter_table(
        "stock_movements"
    ) as batch_op:
        batch_op.alter_column(
            "quantity",
            existing_type=sa.Float(),
            type_=sa.Integer(),
            existing_nullable=False,
        )


def downgrade() -> None:
    with op.batch_alter_table(
        "stock_movements"
    ) as batch_op:
        batch_op.alter_column(
            "quantity",
            existing_type=sa.Integer(),
            type_=sa.Float(),
            existing_nullable=False,
        )