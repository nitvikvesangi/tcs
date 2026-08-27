"""
Application configuration.

Uses pydantic-settings to load configuration from environment variables / .env file.
All optional external integrations (weather API, LLM API) are designed to have
safe fallbacks so the application can start in "demo mode" without them.
"""

from functools import lru_cache
from typing import List, Optional

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ------------------------------------------------------------------
    # General
    # ------------------------------------------------------------------
    APP_NAME: str = "Quick Commerce Retail Intelligence Platform"
    APP_ENV: str = "development"  # development | staging | production
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"

    # ------------------------------------------------------------------
    # Database
    # ------------------------------------------------------------------
    DATABASE_URL: str = (
        "postgresql+psycopg2://postgres:postgres@localhost:5432/qcommerce_db"
    )

    # ------------------------------------------------------------------
    # Security / Auth
    # ------------------------------------------------------------------
    SECRET_KEY: str = "CHANGE_ME_IN_PRODUCTION"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # ------------------------------------------------------------------
    # CORS
    # ------------------------------------------------------------------
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    # ------------------------------------------------------------------
    # Optional external integrations (safe defaults -> demo/mock mode)
    # ------------------------------------------------------------------
    WEATHER_API_KEY: Optional[str] = None
    WEATHER_PROVIDER: str = "mock"  # mock | openweathermap (future)

    LLM_API_KEY: Optional[str] = None
    LLM_PROVIDER: str = "anthropic"
    LLM_MODEL: str = "claude-sonnet-4-6"

    # ------------------------------------------------------------------
    # Logging
    # ------------------------------------------------------------------
    LOG_LEVEL: str = "INFO"

    @field_validator("APP_ENV")
    @classmethod
    def validate_env(cls, v: str) -> str:
        allowed = {"development", "staging", "production"}
        if v not in allowed:
            raise ValueError(f"APP_ENV must be one of {allowed}")
        return v

    @property
    def is_demo_mode(self) -> bool:
        """True when optional external services are not configured.

        The application must remain fully functional (with mock/synthetic
        data) when this is True.
        """
        return not self.WEATHER_API_KEY or not self.LLM_API_KEY


@lru_cache
def get_settings() -> Settings:
    """Cached settings accessor (avoids re-parsing env on every import)."""
    return Settings()


settings = get_settings()
