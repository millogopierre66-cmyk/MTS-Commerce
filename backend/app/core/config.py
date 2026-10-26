from functools import lru_cache

from pydantic import SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "MTS Commerce"
    APP_VERSION: str = "1.0.0"

    DATABASE_URL: str = "sqlite:///./mts_commerce.db"
    ADMIN_INITIAL_PASSWORD: SecretStr | None = None

    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("SECRET_KEY ne peut pas etre vide.")

        if value == "mts-commerce-super-secret-key-change-this":
            raise ValueError(
                "La SECRET_KEY par defaut est interdite. "
                "Configurez une cle personnalisee dans .env."
            )

        return value

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True
    )


@lru_cache
def get_settings():
    return Settings()


settings = get_settings()