from functools import lru_cache

from pydantic import EmailStr, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=("../.env", ".env"),
        env_ignore_empty=True,
        extra="ignore",
    )

    app_name: str = "MitreAI API"

    mongo_url: str = "mongodb://localhost:27017"
    mongo_db: str = "mitreai"
    mongo_timeout_ms: int = 5000

    jwt_secret: SecretStr = Field(min_length=32)
    jwt_expire_minutes: int = 60

    admin_email: EmailStr | None = None
    admin_password: SecretStr | None = None

    available_models: list[str] = Field(default=["mock-small", "mock-large"], min_length=1)


@lru_cache
def get_settings() -> Settings:
    return Settings()
