import math
from datetime import datetime

from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog
from app.repositories.audit_log_repository import AuditLogRepository


class AuditLogService:

    # ==========================================================
    # CRÉER UN JOURNAL D'AUDIT
    # ==========================================================

    @staticmethod
    def log(
        db: Session,
        action: str,
        user_id: int | None = None,
        username: str | None = None,
        entity_type: str | None = None,
        entity_id: int | None = None,
        description: str | None = None,
        ip_address: str | None = None,
        commit: bool = True,
    ) -> AuditLog:

        audit_log = AuditLog(
            user_id=user_id,
            username=username,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            description=description,
            ip_address=ip_address
        )

        return AuditLogRepository.create(
            db,
            audit_log,
            commit=commit,
        )

    # ==========================================================
    # RÉCUPÉRER UN JOURNAL
    # ==========================================================

    @staticmethod
    def get_by_id(
        db: Session,
        audit_id: int
    ):

        return AuditLogRepository.get_by_id(
            db,
            audit_id
        )

    # ==========================================================
    # RÉCUPÉRER TOUS LES JOURNAUX
    # ==========================================================

    @staticmethod
    def get_all(
        db: Session,
        limit: int = 100
    ):

        return AuditLogRepository.get_all(
            db,
            limit
        )

    # ==========================================================
    # JOURNAUX D'UN UTILISATEUR
    # ==========================================================

    @staticmethod
    def get_by_user(
        db: Session,
        user_id: int,
        limit: int = 100
    ):

        return AuditLogRepository.get_by_user(
            db,
            user_id,
            limit
        )

    # ==========================================================
    # JOURNAUX PAR ACTION
    # ==========================================================

    @staticmethod
    def get_by_action(
        db: Session,
        action: str,
        limit: int = 100
    ):

        return AuditLogRepository.get_by_action(
            db,
            action,
            limit
        )

    # ==========================================================
    # JOURNAUX PAR TYPE D'ENTITÉ
    # ==========================================================

    @staticmethod
    def get_by_entity_type(
        db: Session,
        entity_type: str,
        limit: int = 100
    ):

        return AuditLogRepository.get_by_entity_type(
            db,
            entity_type,
            limit
        )

    # ==========================================================
    # JOURNAUX D'UNE ENTITÉ
    # ==========================================================

    @staticmethod
    def get_by_entity(
        db: Session,
        entity_type: str,
        entity_id: int,
        limit: int = 100
    ):

        return AuditLogRepository.get_by_entity(
            db,
            entity_type,
            entity_id,
            limit
        )

    # ==========================================================
    # RECHERCHE AVANCÉE + PAGINATION
    # ==========================================================

    @staticmethod
    def search(
        db: Session,
        page: int = 1,
        limit: int = 20,
        user_id: int | None = None,
        action: str | None = None,
        entity_type: str | None = None,
        entity_id: int | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None
    ):

        # ------------------------------------------------------
        # SÉCURISATION DE LA PAGINATION
        # ------------------------------------------------------

        if page < 1:
            page = 1

        if limit < 1:
            limit = 20

        if limit > 100:
            limit = 100

        # ------------------------------------------------------
        # RECHERCHE DANS LE REPOSITORY
        # ------------------------------------------------------

        logs, total = AuditLogRepository.search(
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

        # ------------------------------------------------------
        # CALCUL DU NOMBRE TOTAL DE PAGES
        # ------------------------------------------------------

        total_pages = (
            math.ceil(total / limit)
            if total > 0
            else 0
        )

        # ------------------------------------------------------
        # RÉSULTAT
        # ------------------------------------------------------

        return {
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": total_pages,
            "items": logs
        }

