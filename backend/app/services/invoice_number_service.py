from datetime import datetime
import sqlite3

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.issued_invoice_number import IssuedInvoiceNumber


class InvoiceNumberService:

    @staticmethod
    def reserve_invoice_number() -> str:
        """
        R?serve un num?ro unique FAC-AAAAMMJJ-NNNN.
        La r?servation a sa propre transaction afin d'?viter
        les collisions lorsque plusieurs ventes sont cr??es.
        Un num?ro r?serv? peut rester inutilis? si la vente ?choue.
        """
        # Import diff?r? : une simple importation du service
        # ne charge pas la configuration de la base r?elle.
        from app.database.session import SessionLocal

        db: Session = SessionLocal()

        try:
            today = datetime.now().strftime("%Y%m%d")
            count = 1

            while True:
                invoice_number = f"FAC-{today}-{count:04d}"

                try:
                    db.add(
                        IssuedInvoiceNumber(
                            invoice_number=invoice_number,
                        )
                    )
                    db.commit()
                    return invoice_number

                except IntegrityError as exc:
                    db.rollback()

                    error_code = getattr(
                        exc.orig,
                        "sqlite_errorcode",
                        None,
                    )
                    collision_codes = {
                        code
                        for code in (
                            getattr(
                                sqlite3,
                                "SQLITE_CONSTRAINT_PRIMARYKEY",
                                None,
                            ),
                            getattr(
                                sqlite3,
                                "SQLITE_CONSTRAINT_UNIQUE",
                                None,
                            ),
                        )
                        if code is not None
                    }

                    if error_code not in collision_codes:
                        raise

                    existing_number = (
                        db.query(IssuedInvoiceNumber.invoice_number)
                        .filter(
                            IssuedInvoiceNumber.invoice_number
                            == invoice_number
                        )
                        .first()
                    )

                    if existing_number is None:
                        raise

                    count += 1

        except Exception:
            db.rollback()
            raise

        finally:
            db.close()
