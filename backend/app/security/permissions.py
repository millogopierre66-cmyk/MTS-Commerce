from fastapi import Depends, HTTPException, status

from app.models.user import User
from app.security.auth import get_current_user


def require_admin(
    current_user: User = Depends(get_current_user)
):
    """
    Vérifie que l'utilisateur connecté possède le rôle admin.
    """

    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès réservé aux administrateurs."
        )

    return current_user