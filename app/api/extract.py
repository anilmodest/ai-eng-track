"""Week 1: POST /documents/{id}/extract. The exercise is in weeks/1/README.md.

Everything you need is already imported below. The tests in tests/weeks/test_week1.py are the
contract. Nothing in this file may name a provider, a model or an SDK.
"""

from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlmodel import Session

from app.api.schemas import DocumentExtract, ErrorOut, ExtractOut  # noqa: F401
from app.db.models import Document, Extraction  # noqa: F401
from app.db.session import get_session
from app.llm.client import Message, ModelClient, ModelError, ModelTimeout  # noqa: F401
from app.llm.cost import estimate_cost_usd  # noqa: F401
from app.llm.registry import get_model_client
from app.llm.structured import SchemaError, complete_structured  # noqa: F401
from app.settings import Settings, get_settings

router = APIRouter()

# Bump this when the prompt changes: it is part of the idempotency key.
PROMPT_VERSION = "extract_v1"
# The prompt lives in app/llm/prompts/extract_v1.md. Load it here.

SessionDep = Annotated[Session, Depends(get_session)]
ClientDep = Annotated[ModelClient, Depends(get_model_client)]
SettingsDep = Annotated[Settings, Depends(get_settings)]


def _error(status: int, code: str, detail: str) -> JSONResponse:
    """Every failure leaves through here: a stable code and a human detail, never a stack trace."""
    return JSONResponse(
        status_code=status, content=ErrorOut(error=code, detail=detail).model_dump()
    )


@router.post(
    "/documents/{doc_id}/extract",
    response_model=ExtractOut,
    responses={404: {"model": ErrorOut}, 502: {"model": ErrorOut}, 504: {"model": ErrorOut}},
)
async def extract_document(
    doc_id: int, session: SessionDep, client: ClientDep, settings: SettingsDep
) -> ExtractOut | JSONResponse:
    # TODO Week 1. Suggested order (see README.md, Exercise):
    #   1. Load the document; 404 if missing.
    #   2. Look for an existing Extraction row for (doc_id, client.name, client.model,
    #      PROMPT_VERSION). If found, return it with cached=True and make NO model call.
    #   3. Build the messages: system prompt + the document text, capped at
    #      settings.max_input_chars.
    #   4. Call complete_structured(...) with the retry/timeout settings. Map ModelTimeout -> 504,
    #      ModelError -> 502 provider_error, SchemaError -> 502 schema_error.
    #   5. Sum tokens over every response (a repair adds one), estimate cost, measure latency.
    #   6. Store the Extraction row. Return ExtractOut with cached=False.
    return _error(501, "not_implemented", "Week 1 exercise: implement extract_document")
