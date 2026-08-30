from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.security.hashing import hash_password, verify_password


class UserService:

    @staticmethod
    def create_user(
        db: Session,
        username: str,
        email: str,
        password: str,
        role: str = "vendeur",
    ):
        """
        Crée un nouvel utilisateur.
        """

        if UserRepository.get_by_username(db, username):
            raise ValueError(
                "Nom d'utilisateur déjà utilisé."
            )

        if UserRepository.get_by_email(db, email):
            raise ValueError(
                "Email déjà utilisé."
            )

        user = User(
            username=username,
            email=email,
            password=hash_password(password),
            role=role,
            is_active=True,
        )

        return UserRepository.create(db, user)

    @staticmethod
    def authenticate(
        db: Session,
        username: str,
        password: str,
    ):
        """
        Authentifie un utilisateur.
        """

        user = UserRepository.get_by_username(
            db,
            username
        )

        if not user:
            return None

        if not user.is_active:
            return None

        if not verify_password(
            password,
            user.password
        ):
            return None

        return user