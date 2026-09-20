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

    # Week 2+: retrieval
    embed_provider: str = "hash"  # hash (lexical, CI) | fastembed (bge-small, CPU)
    chunk_strategy: str = "sentence"  # fixed | sentence | paragraph | heading
    search_k: int = 5
    relevance_threshold: float = 0.30  # below this the system abstains (Week 3)

    # Week 4+: agents
    agent_max_steps: int = 8
    require_approval_for_cost: bool = True  # tools that spend money need approved=true

    # Week 5+: guardrails
    guard_enabled: bool = True
    kill_switch: bool = False
    daily_budget_usd: float = 1.00

    # Week 6: shipping
    app_version: str = "0.1.0"
    git_sha: str = "dev"
    # Which browser origins may call the API (the hub page's playground). "*" is the learning
    # default; a Pro exercise narrows it to the fellow's own Pages origin.
    cors_origins: str = "*"

    # Test-only: script for the fake provider, e.g. "429,429,ok" (see app/llm/providers/fake.py)
    fake_script: str = "ok"


@lru_cache
def get_settings() -> Settings:
    return Settings()
