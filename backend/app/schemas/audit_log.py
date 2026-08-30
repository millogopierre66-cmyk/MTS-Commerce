from datetime import datetime

from pydantic import BaseModel, ConfigDict


# ==========================================================
# RÉPONSE D'UN JOURNAL D'AUDIT
# ==========================================================

class AuditLogResponse(BaseModel):

    id: int

    user_id: int | None = None
    username: str | None = None

    action: str

    entity_type: str | None = None
    entity_id: int | None = None

    description: str | None = None

    ip_address: str | None = None

    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


# ==========================================================
# RÉPONSE PAGINÉE DES JOURNAUX D'AUDIT
# ==========================================================

class AuditLogPaginatedResponse(BaseModel):

    total: int

    page: int

    limit: int

    total_pages: int

    items: list[AuditLogResponse]

