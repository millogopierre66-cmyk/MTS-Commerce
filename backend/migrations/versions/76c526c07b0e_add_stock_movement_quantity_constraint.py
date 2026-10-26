
"""add stock movement quantity constraint

Revision ID: 76c526c07b0e
Revises: 69f0a3c8fb89
"""

from typing import Sequence, Union

from alembic import op


revision: str = "76c526c07b0e"
down_revision: Union[str, Sequence[str], None] = "69f0a3c8fb89"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Bloque les mouvements invalides sans modifier l'historique."""

    op.execute("""
        CREATE TRIGGER trg_stock_movements_validate_insert
        BEFORE INSERT ON stock_movements
        FOR EACH ROW
        WHEN NOT (
            (NEW.movement_type IN ('IN', 'OUT') AND NEW.quantity > 0)
            OR
            (NEW.movement_type = 'ADJUSTMENT' AND NEW.quantity <> 0)
        )
        BEGIN
            SELECT RAISE(
                ABORT,
                'Mouvement de stock invalide : type ou quantite non conforme'
            );
        END;
    """)

    op.execute("""
        CREATE TRIGGER trg_stock_movements_validate_update
        BEFORE UPDATE ON stock_movements
        FOR EACH ROW
        WHEN NOT (
            (NEW.movement_type IN ('IN', 'OUT') AND NEW.quantity > 0)
            OR
            (NEW.movement_type = 'ADJUSTMENT' AND NEW.quantity <> 0)
        )
        AND (
            NEW.movement_type IS NOT OLD.movement_type
            OR NEW.quantity IS NOT OLD.quantity
        )
        BEGIN
            SELECT RAISE(
                ABORT,
                'Modification refusee : mouvement de stock invalide'
            );
        END;
    """)


def downgrade() -> None:
    """Retire les déclencheurs ajoutés par cette migration."""

    op.execute("""
        DROP TRIGGER IF EXISTS trg_stock_movements_validate_update;
    """)

    op.execute("""
        DROP TRIGGER IF EXISTS trg_stock_movements_validate_insert;
    """)
