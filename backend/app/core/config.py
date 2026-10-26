from functools import lru_cache

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "MTS Commerce"
    APP_VERSION: str = "1.0.0"

    DATABASE_URL: str = "sqlite:///./mts_commerce.db"
    ADMIN_INITIAL_PASSWORD: SecretStr | None = None

    SECRET_KEY: str = "mts-commerce-super-secret-key-change-this"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True
    )


@lru_cache
def get_settings():
    return Settings()


settings = get_settings()