from functools import lru_cache

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


@lru_cache
def get_settings() -> Settings:
    return Settings()
