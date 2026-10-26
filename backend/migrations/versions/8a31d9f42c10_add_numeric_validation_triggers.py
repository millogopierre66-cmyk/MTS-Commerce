"""Add database-level validation for products, sale items and sales.

Revision ID: 8a31d9f42c10
Revises: 76c526c07b0e
"""

from typing import Sequence, Union

from alembic import op


revision: str = "8a31d9f42c10"
down_revision: Union[str, Sequence[str], None] = "76c526c07b0e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


MAX_FLOAT = "1.7976931348623157e308"


def upgrade() -> None:
    """Reject invalid numeric values at the SQLite database level."""

    statements = [
        f"""
        CREATE TRIGGER trg_products_validate_insert
        BEFORE INSERT ON products
        FOR EACH ROW
        WHEN NOT (
            typeof(NEW.purchase_price) IN ('integer', 'real')
            AND NEW.purchase_price >= 0
            AND NEW.purchase_price <= {MAX_FLOAT}
            AND typeof(NEW.selling_price) IN ('integer', 'real')
            AND NEW.selling_price >= 0
            AND NEW.selling_price <= {MAX_FLOAT}
            AND typeof(NEW.minimum_stock) IN ('integer', 'real')
            AND NEW.minimum_stock >= 0
            AND NEW.minimum_stock <= {MAX_FLOAT}
            AND typeof(NEW.quantity) = 'integer'
            AND NEW.quantity >= 0
            AND typeof(NEW.alert_stock) = 'integer'
            AND NEW.alert_stock >= 0
        )
        BEGIN
            SELECT RAISE(ABORT, 'Produit invalide : valeurs numeriques non conformes');
        END;
        """,
        f"""
        CREATE TRIGGER trg_products_validate_update
        BEFORE UPDATE ON products
        FOR EACH ROW
        WHEN NOT (
            typeof(NEW.purchase_price) IN ('integer', 'real')
            AND NEW.purchase_price >= 0
            AND NEW.purchase_price <= {MAX_FLOAT}
            AND typeof(NEW.selling_price) IN ('integer', 'real')
            AND NEW.selling_price >= 0
            AND NEW.selling_price <= {MAX_FLOAT}
            AND typeof(NEW.minimum_stock) IN ('integer', 'real')
            AND NEW.minimum_stock >= 0
            AND NEW.minimum_stock <= {MAX_FLOAT}
            AND typeof(NEW.quantity) = 'integer'
            AND NEW.quantity >= 0
            AND typeof(NEW.alert_stock) = 'integer'
            AND NEW.alert_stock >= 0
        )
        BEGIN
            SELECT RAISE(ABORT, 'Modification refusee : produit invalide');
        END;
        """,
        f"""
        CREATE TRIGGER trg_sale_items_validate_insert
        BEFORE INSERT ON sale_items
        FOR EACH ROW
        WHEN NOT (
            typeof(NEW.quantity) = 'integer'
            AND NEW.quantity > 0
            AND typeof(NEW.unit_price) IN ('integer', 'real')
            AND NEW.unit_price >= 0
            AND NEW.unit_price <= {MAX_FLOAT}
            AND typeof(NEW.subtotal) IN ('integer', 'real')
            AND NEW.subtotal >= 0
            AND NEW.subtotal <= {MAX_FLOAT}
            AND (
                NEW.purchase_unit_price IS NULL
                OR (
                    typeof(NEW.purchase_unit_price) IN ('integer', 'real')
                    AND NEW.purchase_unit_price >= 0
                    AND NEW.purchase_unit_price <= {MAX_FLOAT}
                )
            )
        )
        BEGIN
            SELECT RAISE(ABORT, 'Ligne de vente invalide : valeurs numeriques non conformes');
        END;
        """,
        f"""
        CREATE TRIGGER trg_sale_items_validate_update
        BEFORE UPDATE ON sale_items
        FOR EACH ROW
        WHEN NOT (
            typeof(NEW.quantity) = 'integer'
            AND NEW.quantity > 0
            AND typeof(NEW.unit_price) IN ('integer', 'real')
            AND NEW.unit_price >= 0
            AND NEW.unit_price <= {MAX_FLOAT}
            AND typeof(NEW.subtotal) IN ('integer', 'real')
            AND NEW.subtotal >= 0
            AND NEW.subtotal <= {MAX_FLOAT}
            AND (
                NEW.purchase_unit_price IS NULL
                OR (
                    typeof(NEW.purchase_unit_price) IN ('integer', 'real')
                    AND NEW.purchase_unit_price >= 0
                    AND NEW.purchase_unit_price <= {MAX_FLOAT}
                )
            )
        )
        BEGIN
            SELECT RAISE(ABORT, 'Modification refusee : ligne de vente invalide');
        END;
        """,
        f"""
        CREATE TRIGGER trg_sales_validate_insert
        BEFORE INSERT ON sales
        FOR EACH ROW
        WHEN NOT (
            typeof(NEW.total) IN ('integer', 'real')
            AND NEW.total >= 0
            AND NEW.total <= {MAX_FLOAT}
        )
        BEGIN
            SELECT RAISE(ABORT, 'Vente invalide : total non conforme');
        END;
        """,
        f"""
        CREATE TRIGGER trg_sales_validate_update
        BEFORE UPDATE ON sales
        FOR EACH ROW
        WHEN NOT (
            typeof(NEW.total) IN ('integer', 'real')
            AND NEW.total >= 0
            AND NEW.total <= {MAX_FLOAT}
        )
        BEGIN
            SELECT RAISE(ABORT, 'Modification refusee : total de vente invalide');
        END;
        """,
    ]

    for statement in statements:
        op.execute(statement)


def downgrade() -> None:
    """Remove the validation triggers created by this migration."""

    triggers = [
        "trg_products_validate_insert",
        "trg_products_validate_update",
        "trg_sale_items_validate_insert",
        "trg_sale_items_validate_update",
        "trg_sales_validate_insert",
        "trg_sales_validate_update",
    ]

    for trigger in triggers:
        op.execute(f"DROP TRIGGER IF EXISTS {trigger}")
