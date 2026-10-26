from sqlalchemy import create_engine

from app.core.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    echo=False,
    future=True,
    connect_args={"check_same_thread": False}
)