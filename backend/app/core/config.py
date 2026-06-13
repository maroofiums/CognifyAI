"""Application configuration loaded from environment variables."""
from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Centralized application settings."""

    PROJECT_NAME: str = "CognifyAI"
    API_V1_PREFIX: str = "/api"

    DATABASE_URL: str = "sqlite:///./cognify.db"

    # LLM configuration (LangChain + Mistral)
    USE_LLM: bool = False
    MISTRAL_API_KEY: str = ""
    LLM_MODEL: str = "mistral-small-latest"

    # CORS
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings instance."""
    return Settings()


settings = get_settings()
