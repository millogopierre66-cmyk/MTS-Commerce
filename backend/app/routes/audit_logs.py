from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.security.auth import (
    get_db,
    get_current_admin
)

from app.services.audit_log_service import AuditLogService

from app.schemas.audit_log import (
    AuditLogResponse,
    AuditLogPaginatedResponse
)


router = APIRouter(
    prefix="/audit-logs",
    tags=["Audit"]
)


# ==========================================================
# TOUS LES JOURNAUX
# ==========================================================

@router.get(
    "",
    response_model=list[AuditLogResponse]
)
def get_all_audit_logs(
    limit: int = Query(
        default=100,
        ge=1,
        le=100
    ),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin)
):
    return AuditLogService.get_all(
        db,
        limit
    )


# ==========================================================
# RECHERCHE AVANCÉE + PAGINATION
# ==========================================================

@router.get(
    "/search",
    response_model=AuditLogPaginatedResponse
)
def search_audit_logs(
    page: int = Query(
        default=1,
        ge=1
    ),
    limit: int = Query(
        default=20,
        ge=1,
        le=100
    ),
    user_id: int | None = Query(
        default=None
    ),
    action: str | None = Query(
        default=None
    ),
    entity_type: str | None = Query(
        default=None
    ),
    entity_id: int | None = Query(
        default=None
    ),
    start_date: datetime | None = Query(
        default=None
    ),
    end_date: datetime | None = Query(
        default=None
    ),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin)
):

    if (
        start_date is not None
        and end_date is not None
        and start_date > end_date
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "La date de début doit être "
                "antérieure ou égale à la date de fin."
            )
        )

    return AuditLogService.search(
        db=db,
        page=page,
        limit=limit,
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        start_date=start_date,
        end_date=end_date
    )


# ==========================================================
# JOURNAUX D'UN UTILISATEUR
# ==========================================================

@router.get(
    "/user/{user_id}",
    response_model=list[AuditLogResponse]
)
def get_user_audit_logs(
    user_id: int,
    limit: int = Query(
        default=100,
        ge=1,
        le=100
    ),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin)
):
    return AuditLogService.get_by_user(
        db,
        user_id,
        limit
    )


# ==========================================================
# JOURNAUX PAR ACTION
# ==========================================================

@router.get(
    "/action/{action}",
    response_model=list[AuditLogResponse]
)
def get_action_audit_logs(
    action: str,
    limit: int = Query(
        default=100,
        ge=1,
        le=100
    ),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin)
):
    return AuditLogService.get_by_action(
        db,
        action,
        limit
    )


# ==========================================================
# JOURNAUX PAR TYPE D'ENTITÉ
# ==========================================================

@router.get(
    "/entity-type/{entity_type}",
    response_model=list[AuditLogResponse]
)
def get_entity_type_audit_logs(
    entity_type: str,
    limit: int = Query(
        default=100,
        ge=1,
        le=100
    ),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin)
):
    return AuditLogService.get_by_entity_type(
        db,
        entity_type,
        limit
    )


# ==========================================================
# JOURNAUX D'UNE ENTITÉ PRÉCISE
# ==========================================================

@router.get(
    "/entity/{entity_type}/{entity_id}",
    response_model=list[AuditLogResponse]
)
def get_entity_audit_logs(
    entity_type: str,
    entity_id: int,
    limit: int = Query(
        default=100,
        ge=1,
        le=100
    ),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin)
):
    return AuditLogService.get_by_entity(
        db,
        entity_type,
        entity_id,
        limit
    )


# ==========================================================
# JOURNAL PAR ID
# ==========================================================

@router.get(
    "/{log_id}",
    response_model=AuditLogResponse
)
def get_audit_log(
    log_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin)
):

    log = AuditLogService.get_by_id(
        db,
        log_id
    )

    if log is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Journal d'audit introuvable."
        )

    return log

