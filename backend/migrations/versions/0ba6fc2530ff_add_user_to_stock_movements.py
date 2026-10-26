"""add user to stock movements

Revision ID: 0ba6fc2530ff
Revises: e56f30647855
Create Date: 2026-08-31 22:20:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "0ba6fc2530ff"
down_revision: Union[str, Sequence[str], None] = "e56f30647855"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ---------------------------------------------------------
    # 1. Ajouter temporairement user_id comme nullable
    # ---------------------------------------------------------

    op.add_column(
        "stock_movements",
        sa.Column(
            "user_id",
            sa.Integer(),
            nullable=True
        )
    )

    # ---------------------------------------------------------
    # 2. Attribuer les anciens mouvements à l'administrateur
    #    historique (user_id = 1)
    # ---------------------------------------------------------

    op.execute(
        sa.text(
            """
            UPDATE stock_movements
            SET user_id = 1
            WHERE user_id IS NULL
            """
        )
    )

    # ---------------------------------------------------------
    # 3. Ajouter la contrainte de clé étrangère
    # ---------------------------------------------------------

    with op.batch_alter_table(
        "stock_movements"
    ) as batch_op:

        batch_op.create_foreign_key(
            "fk_stock_movements_user_id_users",
            "users",
            ["user_id"],
            ["id"]
        )

        # -----------------------------------------------------
        # 4. Rendre user_id obligatoire
        # -----------------------------------------------------

        batch_op.alter_column(
            "user_id",
            existing_type=sa.Integer(),
            nullable=False
        )


def downgrade() -> None:

    with op.batch_alter_table(
        "stock_movements"
    ) as batch_op:

        batch_op.drop_constraint(
            "fk_stock_movements_user_id_users",
            type_="foreignkey"
        )

        batch_op.drop_column("user_id")