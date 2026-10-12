"""Week 1: POST /documents/{id}/extract. The exercise is in weeks/1/README.md.

Everything you need is already imported below. The tests in tests/weeks/test_week1.py are the
contract. Nothing in this file may name a provider, a model or an SDK.
"""

import time
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlmodel import Session, select

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
_PROMPT = (Path(__file__).parent.parent / "llm" / "prompts" / f"{PROMPT_VERSION}.md").read_text()

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
    # TODO 1: load the document; 404 if missing

    doc = session.get(Document, doc_id)
    if doc is None:
        return _error(404, "not_found", "document not found")

    # TODO 2: return a stored result with cached=True and make no model call

    existing = session.exec(
        select(Extraction).where(
            Extraction.document_id == doc_id,
            Extraction.provider == client.name,
            Extraction.model == client.model,
            Extraction.prompt_version == PROMPT_VERSION,
        )
    ).first()
    if existing is not None:
        return ExtractOut(
            document_id=doc_id,
            cached=True,
            provider=existing.provider,
            model=existing.model,
            prompt_version=existing.prompt_version,
            tokens_in=existing.tokens_in,
            tokens_out=existing.tokens_out,
            latency_ms=existing.latency_ms,
            cost_usd=existing.cost_usd,
            extract=DocumentExtract.model_validate_json(existing.result_json),
        )

    # The key uses client.name and client.model, never a
    # hard-coded provider name, so the "names no provider" rule still holds.

    # TODO 3: build the messages, capped at max_input_chars

    body = doc.text[: settings.max_input_chars]
    messages = [
        Message(role="system", content=_PROMPT),
        Message(role="user", content=body or "(empty)"),
    ]

    # The cap test checks that the user message is under
    # 700 characters when the limit is 500. That's why the user
    # message carries only the document text and the instructions go in the system message.

    # TODO 4: call complete_structured and map the errors

    t0 = time.perf_counter()
    try:
        extract, responses = await complete_structured(
            client,
            messages,
            DocumentExtract,
            attempts=settings.model_retry_attempts,
            base_delay_s=settings.model_retry_base_delay_s,
            timeout_s=settings.model_timeout_s,
        )
    except ModelTimeout as e:
        return _error(504, "provider_timeout", str(e))
    except ModelError as e:
        return _error(502, "provider_error", str(e))
    except SchemaError as e:
        return _error(502, "schema_error", e.detail)
    latency_ms = int((time.perf_counter() - t0) * 1000)

    # - Catch ModelTimeout before ModelError.
    # It's a subclass, so if ModelError came first it would
    # catch timeouts too, and you would return 502 instead of 504.
    # - You don't write retries, backoff or the repair
    # yourself. complete_structured already does them
    # using with_retry. It retries 429s, 5xx errors and timeouts, and never retries a 400.

    # TODO 5: total tokens and cost across every response

    tokens_in = sum(r.tokens_in for r in responses)
    tokens_out = sum(r.tokens_out for r in responses)
    cost_usd = estimate_cost_usd(responses[-1].model, tokens_in, tokens_out)

    # responses has two entries when a repair happened,
    # so summing over all of them includes the repair call in the bill.

    # TODO 6: store the row and return with cached=False

    row = Extraction(
        document_id=doc_id,
        provider=client.name,
        model=client.model,
        prompt_version=PROMPT_VERSION,
        tokens_in=tokens_in,
        tokens_out=tokens_out,
        latency_ms=latency_ms,
        cost_usd=cost_usd,
        result_json=extract.model_dump_json(),
    )
    session.add(row)
    session.commit()
    return ExtractOut(
        document_id=doc_id,
        cached=False,
        provider=client.name,
        model=client.model,
        prompt_version=PROMPT_VERSION,
        tokens_in=tokens_in,
        tokens_out=tokens_out,
        latency_ms=latency_ms,
        cost_usd=cost_usd,
        extract=extract,
    )

    #   2. Look for an existing Extraction row for (doc_id, client.name, client.model,
    #      PROMPT_VERSION). If found, return it with cached=True and make NO model call.
    #   3. Build the messages: system prompt + the document text, capped at
    #      settings.max_input_chars.
    #   4. Call complete_structured(...) with the retry/timeout settings. Map ModelTimeout -> 504,
    #      ModelError -> 502 provider_error, SchemaError -> 502 schema_error.
    #   5. Sum tokens over every response (a repair adds one), estimate cost, measure latency.
    #   6. Store the Extraction row. Return ExtractOut with cached=False.
    # return _error(501, "not_implemented", "Week 1 exercise: implement extract_document")
