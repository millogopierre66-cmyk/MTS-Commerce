from app.database.init_admin import create_admin
from app.database.session import SessionLocal


def init_db():
    """
    Initialise uniquement le compte administrateur.

    Le schema de la base est exclusivement gere par Alembic.
    Executer prealablement : alembic upgrade head
    """

    db = SessionLocal()

    try:
        create_admin(db)
    finally:
        db.close()
