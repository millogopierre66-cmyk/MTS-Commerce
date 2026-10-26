from datetime import datetime

from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


class AuditLogRepository:

    # ==========================================================
    # CRÉER UN JOURNAL D'AUDIT
    # ==========================================================

    @staticmethod
    def create(
        db: Session,
        audit_log: AuditLog,
        commit: bool = True,
    ) -> AuditLog:

        db.add(audit_log)
        db.flush()

        if commit:
            db.commit()
            db.refresh(audit_log)

        return audit_log

    # ==========================================================
    # RÉCUPÉRER PAR ID
    # ==========================================================

    @staticmethod
    def get_by_id(
        db: Session,
        audit_id: int
    ) -> AuditLog | None:

        return (
            db.query(AuditLog)
            .filter(
                AuditLog.id == audit_id
            )
            .first()
        )

    # ==========================================================
    # RÉCUPÉRER TOUS LES JOURNAUX
    # ==========================================================

    @staticmethod
    def get_all(
        db: Session,
        limit: int = 100
    ) -> list[AuditLog]:

        return (
            db.query(AuditLog)
            .order_by(
                AuditLog.created_at.desc()
            )
            .limit(limit)
            .all()
        )

    # ==========================================================
    # JOURNAUX D'UN UTILISATEUR
    # ==========================================================

    @staticmethod
    def get_by_user(
        db: Session,
        user_id: int,
        limit: int = 100
    ) -> list[AuditLog]:

        return (
            db.query(AuditLog)
            .filter(
                AuditLog.user_id == user_id
            )
            .order_by(
                AuditLog.created_at.desc()
            )
            .limit(limit)
            .all()
        )

    # ==========================================================
    # JOURNAUX PAR ACTION
    # ==========================================================

    @staticmethod
    def get_by_action(
        db: Session,
        action: str,
        limit: int = 100
    ) -> list[AuditLog]:

        return (
            db.query(AuditLog)
            .filter(
                AuditLog.action == action
            )
            .order_by(
                AuditLog.created_at.desc()
            )
            .limit(limit)
            .all()
        )

    # ==========================================================
    # JOURNAUX PAR TYPE D'ENTITÉ
    # ==========================================================

    @staticmethod
    def get_by_entity_type(
        db: Session,
        entity_type: str,
        limit: int = 100
    ) -> list[AuditLog]:

        return (
            db.query(AuditLog)
            .filter(
                AuditLog.entity_type == entity_type
            )
            .order_by(
                AuditLog.created_at.desc()
            )
            .limit(limit)
            .all()
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
    ) -> list[AuditLog]:

        return (
            db.query(AuditLog)
            .filter(
                AuditLog.entity_type == entity_type,
                AuditLog.entity_id == entity_id
            )
            .order_by(
                AuditLog.created_at.desc()
            )
            .limit(limit)
            .all()
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
    ) -> tuple[list[AuditLog], int]:

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
        # CONSTRUCTION DE LA REQUÊTE
        # ------------------------------------------------------

        query = db.query(AuditLog)

        # ------------------------------------------------------
        # FILTRE UTILISATEUR
        # ------------------------------------------------------

        if user_id is not None:
            query = query.filter(
                AuditLog.user_id == user_id
            )

        # ------------------------------------------------------
        # FILTRE ACTION
        # ------------------------------------------------------

        if action is not None:
            query = query.filter(
                AuditLog.action == action
            )

        # ------------------------------------------------------
        # FILTRE TYPE D'ENTITÉ
        # ------------------------------------------------------

        if entity_type is not None:
            query = query.filter(
                AuditLog.entity_type == entity_type
            )

        # ------------------------------------------------------
        # FILTRE ID D'ENTITÉ
        # ------------------------------------------------------

        if entity_id is not None:
            query = query.filter(
                AuditLog.entity_id == entity_id
            )

        # ------------------------------------------------------
        # FILTRE DATE DE DÉBUT
        # ------------------------------------------------------

        if start_date is not None:
            query = query.filter(
                AuditLog.created_at >= start_date
            )

        # ------------------------------------------------------
        # FILTRE DATE DE FIN
        # ------------------------------------------------------

        if end_date is not None:
            query = query.filter(
                AuditLog.created_at <= end_date
            )

        # ------------------------------------------------------
        # NOMBRE TOTAL DE RÉSULTATS
        # ------------------------------------------------------

        total = query.count()

        # ------------------------------------------------------
        # PAGINATION
        # ------------------------------------------------------

        offset = (page - 1) * limit

        logs = (
            query
            .order_by(
                AuditLog.created_at.desc()
            )
            .offset(offset)
            .limit(limit)
            .all()
        )

        return logs, total

