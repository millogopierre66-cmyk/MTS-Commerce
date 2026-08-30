from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.security.auth import (
    get_db,
    get_current_admin,
)

from app.repositories.user_repository import UserRepository
from app.schemas.user import (
    UserCreate,
    UserResponse,
    UserUpdate,
    UserPasswordUpdate,
)
from app.security.hashing import hash_password

from app.services.audit_log_service import AuditLogService


router = APIRouter(
    prefix="/users",
    tags=["Utilisateurs"]
)


# ==========================================================
# LISTE DES UTILISATEURS
# ==========================================================

@router.get(
    "",
    response_model=list[UserResponse]
)
def get_users(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin)
):
    return UserRepository.get_all(db)


# ==========================================================
# UTILISATEUR PAR ID
# ==========================================================

@router.get(
    "/{user_id}",
    response_model=UserResponse
)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin)
):
    user = UserRepository.get_by_id(
        db,
        user_id
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur introuvable."
        )

    return user


# ==========================================================
# CRÉATION UTILISATEUR
# ==========================================================

@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def create_user(
    data: UserCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin)
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

    from app.models.user import User

    user = User(
        username=data.username,
        email=data.email,
        password=hash_password(data.password),
        role=data.role.value,
        is_active=True
    )

    user = UserRepository.create(
        db,
        user
    )

    AuditLogService.log(
        db,
        action="USER_CREATED",
        user_id=current_user.id,
        username=current_user.username,
        entity_type="User",
        entity_id=user.id,
        description=(
            f"Création de l'utilisateur "
            f"'{user.username}'."
        )
    )

    return user


# ==========================================================
# MODIFICATION UTILISATEUR
# ==========================================================

@router.put(
    "/{user_id}",
    response_model=UserResponse
)
def update_user(
    user_id: int,
    data: UserUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin)
):

    user = UserRepository.get_by_id(
        db,
        user_id
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur introuvable."
        )

    update_data = data.model_dump(
        exclude_unset=True
    )

    if "email" in update_data:

        existing = UserRepository.get_by_email(
            db,
            update_data["email"]
        )

        if existing and existing.id != user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email déjà utilisé."
            )

    for field, value in update_data.items():

        if field == "role" and value is not None:
            value = value.value

        setattr(
            user,
            field,
            value
        )
        
    UserRepository.update(
        db,
        user
    )

    AuditLogService.log(
        db,
        action="USER_UPDATED",
        user_id=current_user.id,
        username=current_user.username,
        entity_type="User",
        entity_id=user.id,
        description=(
            f"Modification de l'utilisateur "
            f"'{user.username}'."
        )
    )

    return user


# ==========================================================
# ACTIVATION
# ==========================================================

@router.put(
    "/{user_id}/activate",
    response_model=UserResponse
)
def activate_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin)
):

    user = UserRepository.get_by_id(
        db,
        user_id
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur introuvable."
        )

    user.is_active = True

    UserRepository.update(
        db,
        user
    )

    AuditLogService.log(
        db,
        action="USER_ACTIVATED",
        user_id=current_user.id,
        username=current_user.username,
        entity_type="User",
        entity_id=user.id,
        description=(
            f"Activation du compte "
            f"'{user.username}'."
        )
    )

    return user


# ==========================================================
# DÉSACTIVATION
# ==========================================================

@router.put(
    "/{user_id}/deactivate",
    response_model=UserResponse
)
def deactivate_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin)
):

    user = UserRepository.get_by_id(
        db,
        user_id
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur introuvable."
        )

    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Un administrateur ne peut pas "
                "désactiver son propre compte."
            )
        )
    if (
        user.role == "admin"
        and user.is_active
        and UserRepository.count_active_admins(db) <= 1
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Impossible de désactiver le dernier administrateur actif."
        )

    user.is_active = False

    UserRepository.update(
        db,
        user
    )

    AuditLogService.log(
        db,
        action="USER_DEACTIVATED",
        user_id=current_user.id,
        username=current_user.username,
        entity_type="User",
        entity_id=user.id,
        description=(
            f"Désactivation du compte "
            f"'{user.username}'."
        )
    )

    return user


# ==========================================================
# MODIFICATION DU MOT DE PASSE
# ==========================================================

@router.put(
    "/{user_id}/password",
    response_model=UserResponse
)
def update_password(
    user_id: int,
    data: UserPasswordUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin)
):

    user = UserRepository.get_by_id(
        db,
        user_id
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur introuvable."
        )

    user.password = hash_password(
        data.password
    )

    UserRepository.update(
        db,
        user
    )

    AuditLogService.log(
        db,
        action="USER_PASSWORD_UPDATED",
        user_id=current_user.id,
        username=current_user.username,
        entity_type="User",
        entity_id=user.id,
        description=(
            f"Modification du mot de passe "
            f"de l'utilisateur '{user.username}'."
        )
    )

    return user