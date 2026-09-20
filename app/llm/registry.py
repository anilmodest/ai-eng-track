"""MODEL_PROVIDER -> a ModelClient. Adding a provider is one entry in PROVIDERS, never a code path.

Verify base URLs and free-tier terms the week before each cohort; they change.
"""

import os
from dataclasses import dataclass

from app.llm.client import Message, ModelClient, ModelError, ModelResponse
from app.llm.providers.fake import FakeClient
from app.llm.providers.openai_compat import OpenAICompatClient
from app.settings import Settings, get_settings


@dataclass(frozen=True)
class ProviderSpec:
    base_url: str
    key_env: str  # environment variable holding the key when MODEL_API_KEY is empty
    default_model: str
    signup: str


# GitHub Models ("zero signup, uses GITHUB_TOKEN") was the default here until it was retired on
# 30 July 2026. It stayed in this file for one commit as the Week 1 lesson: providers change
# under you, and the fix was two lines of .env, not a code change.
PROVIDERS: dict[str, ProviderSpec] = {
    "gemini": ProviderSpec(
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        key_env="GEMINI_API_KEY",
        default_model="gemini-3.5-flash-lite",
        signup="https://aistudio.google.com/apikey (free tier, no card)",
    ),
    "groq": ProviderSpec(
        base_url="https://api.groq.com/openai/v1",
        key_env="GROQ_API_KEY",
        default_model="llama-3.3-70b-versatile",
        signup="https://console.groq.com/keys (free tier)",
    ),
    "openrouter": ProviderSpec(
        base_url="https://openrouter.ai/api/v1",
        key_env="OPENROUTER_API_KEY",
        default_model="meta-llama/llama-3.3-70b-instruct:free",
        signup="https://openrouter.ai/keys",
    ),
    "cerebras": ProviderSpec(
        base_url="https://api.cerebras.ai/v1",
        key_env="CEREBRAS_API_KEY",
        default_model="llama-3.3-70b",
        signup="https://cloud.cerebras.ai",
    ),
    "mistral": ProviderSpec(
        base_url="https://api.mistral.ai/v1",
        key_env="MISTRAL_API_KEY",
        default_model="mistral-small-latest",
        signup="https://console.mistral.ai/api-keys",
    ),
    "openai": ProviderSpec(
        base_url="https://api.openai.com/v1",
        key_env="OPENAI_API_KEY",
        default_model="gpt-4o-mini",
        signup="https://platform.openai.com/api-keys (paid)",
    ),
}

FAKE_PROVIDERS = {"fake_a", "fake_b"}


class ProviderConfigError(RuntimeError):
    pass


def build_client(
    provider: str, *, model: str | None, api_key: str | None, settings: Settings
) -> ModelClient:
    if provider in FAKE_PROVIDERS:
        return FakeClient(name=provider, script=settings.fake_script)
    spec = PROVIDERS.get(provider)
    if spec is None:
        known = ", ".join(sorted([*PROVIDERS, *FAKE_PROVIDERS]))
        raise ProviderConfigError(f"unknown MODEL_PROVIDER {provider!r}; known: {known}")
    key = api_key or os.environ.get(spec.key_env)
    if not key:
        raise ProviderConfigError(
            f"no key for {provider}: set MODEL_API_KEY or {spec.key_env} (signup: {spec.signup})"
        )
    return OpenAICompatClient(
        name=provider,
        base_url=spec.base_url,
        api_key=key,
        model=model or spec.default_model,
        timeout_s=settings.model_timeout_s,
    )


class FallbackClient:
    """Tries the primary; on a retryable failure hands the SAME request to the fallback.

    Retrying within one provider is retry.py's job. This is for when a quota is simply gone.
    """

    def __init__(self, primary: ModelClient, fallback: ModelClient) -> None:
        self.primary = primary
        self.fallback = fallback
        self.name = f"{primary.name}+{fallback.name}"
        self.model = primary.model

    async def complete(self, messages: list[Message], *, json_mode: bool = True) -> ModelResponse:
        try:
            return await self.primary.complete(messages, json_mode=json_mode)
        except ModelError as e:
            if not e.retryable:
                raise
            return await self.fallback.complete(messages, json_mode=json_mode)


_client: ModelClient | None = None


def get_model_client() -> ModelClient:
    """FastAPI dependency. Tests override this to inject a scripted FakeClient."""
    global _client
    if _client is None:
        s = get_settings()
        primary = build_client(
            s.model_provider, model=s.model_name, api_key=s.model_api_key, settings=s
        )
        if s.model_fallback_provider:
            fallback = build_client(
                s.model_fallback_provider, model=None, api_key=s.model_fallback_api_key, settings=s
            )
            _client = FallbackClient(primary, fallback)
        else:
            _client = primary
    return _client


def reset_model_client() -> None:
    global _client
    _client = None
