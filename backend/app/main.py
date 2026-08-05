from fastapi import FastAPI

import app.models
from app.core.config import settings
from app.database.base import Base
from app.database.connection import engine

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION
)


@app.get("/")
def root():
    return {
        "application": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "OK"
    }