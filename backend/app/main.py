from fastapi import FastAPI

from app.core.config import settings
from app.database.init_db import init_db
from app.routes.auth import router as auth_router
from app.routes.products import router as products_router
from app.routes.stock import router as stock_router
from app.routes.dashboard import router as dashboard_router
from app.routes.sales import router as sales_router
from app.routes.customers import router as customers_router
from app.routes.accounting import router as accounting_router
from app.routes.audit_logs import router as audit_logs_router
from app.routes.users import router as users_router

from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan
)

app.include_router(auth_router)
app.include_router(products_router)
app.include_router(stock_router)
app.include_router(dashboard_router)
app.include_router(sales_router)
app.include_router(customers_router)
app.include_router(accounting_router)
app.include_router(audit_logs_router)
app.include_router(users_router)


@app.get("/")
def root():
    return {
        "application": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "OK"
    }

