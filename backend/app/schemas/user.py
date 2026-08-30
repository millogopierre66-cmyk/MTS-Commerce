from pydantic import BaseModel, ConfigDict, EmailStr, Field
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    VENDEUR = "vendeur"

class UserBase(BaseModel):
    username: str = Field(
        min_length=3,
        max_length=100,
        description="Nom d'utilisateur"
    )

    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(
        min_length=8,
        max_length=100,
        description="Mot de passe"
    )
    role: UserRole = UserRole.VENDEUR


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(UserBase):
    id: int
    is_active: bool
    role: str

    model_config = ConfigDict(from_attributes=True)

class UserUpdate(BaseModel):
    email: EmailStr | None = None

    role: UserRole | None = None

    is_active: bool | None = None
    
class UserPasswordUpdate(BaseModel):
    password: str = Field(
        min_length=8,
        max_length=100,
        description="Nouveau mot de passe"
    )