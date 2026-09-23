"""Week 6: a health endpoint that says what is running, not just that something is.

Version, commit, prompt versions, provider and model, guard state: everything a person needs to
answer "which build gave this answer?" and "did the rollback take?" without a shell.
"""

import os
from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app import build_info
from app.api.ask import PROMPT_VERSION as ASK_PROMPT
from app.api.extract import PROMPT_VERSION as EXTRACT_PROMPT
from app.settings import Settings, get_settings

router = APIRouter()
SettingsDep = Annotated[Settings, Depends(get_settings)]


class HealthOut(BaseModel):
    status: str
    version: str
    git_sha: str
    built_at: str
    provider: str
    model: str | None
    embedder: str
    chunk_strategy: str
    prompts: dict[str, str]
    guard_enabled: bool
    kill_switch: bool
    model_ready: bool
    model_hint: str | None = None


def _provider_state(settings: Settings) -> tuple[bool, str | None]:
    """Can a model call be made at all? Checked here so nobody has to make one to find out."""
    from app.llm.registry import ProviderConfigError, build_client

    try:
        build_client(
            settings.model_provider,
            model=settings.model_name,
            api_key=settings.model_api_key,
            settings=settings,
        )
    except ProviderConfigError as e:
        return False, str(e)
    return True, None


@router.get("/health", response_model=HealthOut)
def health(settings: SettingsDep) -> HealthOut:
    ready, hint = _provider_state(settings)
    return HealthOut(
        status="ok",
        version=os.environ.get("APP_VERSION") or build_info.APP_VERSION,
        git_sha=os.environ.get("GIT_SHA") or build_info.GIT_SHA,
        built_at=build_info.BUILT_AT,
        provider=settings.model_provider,
        model=settings.model_name,
        embedder=settings.embed_provider,
        chunk_strategy=settings.chunk_strategy,
        prompts={"extract": EXTRACT_PROMPT, "ask": ASK_PROMPT},
        guard_enabled=settings.guard_enabled,
        kill_switch=settings.kill_switch,
        model_ready=ready,
        model_hint=hint,
    )
