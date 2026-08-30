from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database.session import SessionLocal
from app.repositories.user_repository import UserRepository
from app.security.jwt_handler import verify_access_token


# ==========================================================
# OAUTH2
# ==========================================================

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login"
)


# ==========================================================
# BASE DE DONNÉES
# ==========================================================

def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


# ==========================================================
# UTILISATEUR CONNECTÉ
# ==========================================================

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    payload = verify_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide ou expiré."
        )

    username = payload.get("sub")

    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide."
        )

    user = UserRepository.get_by_username(
        db,
        username
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Utilisateur introuvable."
        )

    return user


# ==========================================================
# ADMINISTRATEUR UNIQUEMENT
# ==========================================================

def get_current_admin(
    current_user=Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès réservé à l'administrateur."
        )

    return current_user
# ==========================================================
# VÉRIFICATION DES RÔLES
# ==========================================================

def require_roles(*allowed_roles):
    def role_checker(
        current_user=Depends(get_current_user)
    ):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Vous n'avez pas les permissions nécessaires."
            )

        return current_user

    return role_checker