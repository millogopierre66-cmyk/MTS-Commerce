from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate
from app.security.hashing import hash_password, verify_password
from app.security.jwt_handler import create_access_token
from app.services.audit_log_service import AuditLogService


class AuthService:

    # ==========================================================
    # INSCRIPTION
    # ==========================================================

    @staticmethod
    def register(
        db: Session,
        data: UserCreate
    ):

        if UserRepository.get_by_username(
            db,
            data.username
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nom d'utilisateur déjà utilisé."
            )

        if UserRepository.get_by_email(
            db,
            data.email
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email déjà utilisé."
            )

        user = User(
            username=data.username,
            email=data.email,
            password=hash_password(data.password),
            role="admin"
        )

        user = UserRepository.create(
            db,
            user
        )

        # ------------------------------------------------------
        # JOURNAL D'AUDIT
        # ------------------------------------------------------

        AuditLogService.log(
            db,
            action="REGISTER",
            user_id=user.id,
            username=user.username,
            entity_type="User",
            entity_id=user.id,
            description=(
                f"Création du compte utilisateur "
                f"'{user.username}'."
            )
        )

        return user

    # ==========================================================
    # AUTHENTIFICATION
    # ==========================================================
    @staticmethod
    def authenticate(
        db: Session,
        username: str,
        password: str
    ):

        user = UserRepository.get_by_username(
            db,
            username
        )

        if not user:

            # --------------------------------------------------
            # UTILISATEUR INTROUVABLE
            # --------------------------------------------------

            AuditLogService.log(
                db,
                action="LOGIN_FAILED",
                username=username,
                entity_type="User",
                description=(
                    f"Tentative de connexion échouée "
                    f"pour l'utilisateur '{username}' "
                    f"(utilisateur introuvable)."
                )
            )

            return None

        if not verify_password(
            password,
            user.password
        ):

            # --------------------------------------------------
            # MOT DE PASSE INCORRECT
            # --------------------------------------------------

            AuditLogService.log(
                db,
                action="LOGIN_FAILED",
                user_id=user.id,
                username=user.username,
                entity_type="User",
                entity_id=user.id,
                description=(
                    f"Tentative de connexion échouée "
                    f"pour l'utilisateur '{user.username}' "
                    f"(mot de passe incorrect)."
                )
            )

            return None

        # ------------------------------------------------------
        # COMPTE DÉSACTIVÉ
        # ------------------------------------------------------

        if not user.is_active:

            AuditLogService.log(
                db,
                action="LOGIN_FAILED",
                user_id=user.id,
                username=user.username,
                entity_type="User",
                entity_id=user.id,
                description=(
                    f"Tentative de connexion refusée "
                    f"pour l'utilisateur '{user.username}' "
                    f"(compte désactivé)."
                )
            )

            return None

        return user
    # ==========================================================
    # CONNEXION
    # ==========================================================

    @staticmethod
    def login(
        db: Session,
        username: str,
        password: str
    ):

        user = AuthService.authenticate(
            db,
            username,
            password
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=(
                    "Nom d'utilisateur "
                    "ou mot de passe incorrect."
                )
            )

        token = create_access_token(
            {
                "sub": user.username,
                "role": user.role
            }
        )

        # ------------------------------------------------------
        # CONNEXION RÉUSSIE
        # ------------------------------------------------------

        AuditLogService.log(
            db,
            action="LOGIN_SUCCESS",
            user_id=user.id,
            username=user.username,
            entity_type="User",
            entity_id=user.id,
            description=(
                f"Connexion réussie de "
                f"l'utilisateur '{user.username}'."
            )
        )

        return {
            "access_token": token,
            "token_type": "bearer"
        }