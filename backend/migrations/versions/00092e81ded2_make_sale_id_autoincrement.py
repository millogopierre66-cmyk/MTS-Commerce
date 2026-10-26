"""make sale id autoincrement

Revision ID: 00092e81ded2
Revises: ce196bab0ead
Create Date: 2026-09-01
"""

from typing import Sequence, Union

from alembic import op


revision: str = "00092e81ded2"
down_revision: Union[str, Sequence[str], None] = "ce196bab0ead"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Disable foreign key checks temporarily.
    op.execute("PRAGMA foreign_keys=OFF")

    try:
        # Create the new table with AUTOINCREMENT.
        op.execute("""
            CREATE TABLE sales_new (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                invoice_number VARCHAR(50) NOT NULL,
                total FLOAT NOT NULL,
                created_at DATETIME NOT NULL,
                customer_id INTEGER,
                user_id INTEGER NOT NULL,
                status VARCHAR(20) DEFAULT 'completed' NOT NULL,
                cancelled_at DATETIME,
                cancelled_by INTEGER,
                CONSTRAINT fk_sales_user_id_users
                    FOREIGN KEY(user_id) REFERENCES users (id),
                CONSTRAINT fk_sales_cancelled_by_users
                    FOREIGN KEY(cancelled_by) REFERENCES users (id),
                FOREIGN KEY(customer_id)
                    REFERENCES customers (id),
                UNIQUE (invoice_number)
            )
        """)

        # Copy every existing sale without changing its ID.
        op.execute("""
            INSERT INTO sales_new (
                id,
                invoice_number,
                total,
                created_at,
                customer_id,
                user_id,
                status,
                cancelled_at,
                cancelled_by
            )
            SELECT
                id,
                invoice_number,
                total,
                created_at,
                customer_id,
                user_id,
                status,
                cancelled_at,
                cancelled_by
            FROM sales
        """)

        # Replace the old table.
        op.execute("DROP TABLE sales")
        op.execute("ALTER TABLE sales_new RENAME TO sales")

        # Recreate the SQLAlchemy index.
        op.create_index(
            "ix_sales_id",
            "sales",
            ["id"],
            unique=False,
        )

    finally:
        # Re-enable foreign key checks.
        op.execute("PRAGMA foreign_keys=ON")

    # Verify foreign-key integrity after reconstruction.
    result = op.get_bind().exec_driver_sql(
        "PRAGMA foreign_key_check"
    ).fetchall()

    if result:
        raise RuntimeError(
            f"Foreign key integrity check failed: {result}"
        )


def downgrade() -> None:
    raise NotImplementedError(
        "Downgrade is intentionally disabled because AUTOINCREMENT "
        "must remain enabled to prevent ID reuse."
    )
