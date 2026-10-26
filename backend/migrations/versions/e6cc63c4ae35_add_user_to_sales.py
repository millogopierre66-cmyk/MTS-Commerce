"""add user to sales

Revision ID: e6cc63c4ae35
Revises: 0ba6fc2530ff
Create Date: 2026-09-01 08:38:17.606441
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e6cc63c4ae35"
down_revision: Union[str, Sequence[str], None] = "0ba6fc2530ff"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ---------------------------------------------------------
    # 1. Ajouter temporairement user_id comme nullable
    # ---------------------------------------------------------

    op.add_column(
        "sales",
        sa.Column(
            "user_id",
            sa.Integer(),
            nullable=True
        )
    )

    # ---------------------------------------------------------
    # 2. Attribuer les ventes historiques à l'administrateur
    #    de migration (user_id = 1)
    # ---------------------------------------------------------

    op.execute(
        sa.text(
            """
            UPDATE sales
            SET user_id = 1
            WHERE user_id IS NULL
            """
        )
    )

    # ---------------------------------------------------------
    # 3. Ajouter la clé étrangère vers users.id
    # ---------------------------------------------------------

    with op.batch_alter_table(
        "sales"
    ) as batch_op:

        batch_op.create_foreign_key(
            "fk_sales_user_id_users",
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
        "sales"
    ) as batch_op:

        batch_op.drop_constraint(
            "fk_sales_user_id_users",
            type_="foreignkey"
        )

        batch_op.drop_column("user_id")
