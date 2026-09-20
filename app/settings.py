"""All configuration comes from the environment (.env). Nothing model-specific lives in code."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Model access
    model_provider: str = "gemini"
    model_name: str | None = None
    model_api_key: str | None = None
    model_fallback_provider: str | None = None
    model_fallback_api_key: str | None = None

    # Model call behaviour
    model_timeout_s: float = 20.0
    model_retry_attempts: int = 3
    model_retry_base_delay_s: float = 0.5
    max_input_chars: int = 24_000

    # Storage and jobs
    database_url: str = "sqlite:///./data/app.db"
    redis_url: str | None = None

    # Test-only: script for the fake provider, e.g. "429,429,ok" (see app/llm/providers/fake.py)
    fake_script: str = "ok"


@lru_cache
def get_settings() -> Settings:
    return Settings()
