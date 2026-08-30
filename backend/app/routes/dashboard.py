from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.security.auth import (
    get_db,
    get_current_user
)

from app.services.dashboard_service import DashboardService
from app.schemas.dashboard import DashboardResponse

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


# ==========================================================
# TABLEAU DE BORD
# ==========================================================

@router.get(
    "",
    response_model=DashboardResponse
)
def dashboard(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    return DashboardService.dashboard(db)