from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import SessionLocal

from app.schemas.stock import (
    StockIn,
    StockOut,
    StockAdjust,
    StockResponse,
)

from app.services.stock_service import StockService

from app.security.auth import (
    get_current_user,
    require_roles
)

router = APIRouter(
    prefix="/stock",
    tags=["Stock"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post(
    "/in",
    response_model=StockResponse
)
def stock_in(
    data: StockIn,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles("admin", "manager")
    )
):
    return StockService.stock_in(
        db,
        data
    )
    
@router.post(
    "/out",
    response_model=StockResponse
)
def stock_out(
    data: StockOut,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles("admin", "manager")
    )
):
    return StockService.stock_out(db, data)


@router.post(
    "/adjust",
    response_model=StockResponse
)
def adjust_stock(
    data: StockAdjust,
    db: Session = Depends(get_db),
    current_user=Depends(
    require_roles("admin", "manager")
    )
):
    return StockService.adjust_stock(
    db,
    data.product_id,
    data.quantity,
    data.description
    )

@router.get("/{product_id}")
def get_stock(
    product_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return StockService.get_stock(
        db,
        product_id
    )


@router.get("/history/{product_id}")
def history(
    product_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return StockService.get_history(
        db,
        product_id
    )