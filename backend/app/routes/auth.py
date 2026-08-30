from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database.session import SessionLocal
from app.schemas.user import UserCreate, UserResponse
from app.schemas.token import Token
from app.services.auth_service import AuthService
from app.security.auth import get_current_user

router = APIRouter(
    prefix="/auth",
    tags=["Authentification"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post(
    "/register",
    response_model=UserResponse
)
def register(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    return AuthService.register(db, user)


@router.post(
    "/login",
    response_model=Token
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    return AuthService.login(
        db,
        form_data.username,
        form_data.password
    )


@router.get(
    "/me",
    response_model=UserResponse
)
def me(
    current_user=Depends(get_current_user)
):
    return current_user