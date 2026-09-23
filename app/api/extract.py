"""Week 1: POST /documents/{id}/extract. See weeks/1/README.md for the exercise."""

import json
import time
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlmodel import Session, select

from app.api.schemas import DocumentExtract, ErrorOut, ExtractOut, GuardOut
from app.db.models import Document, Extraction
from app.db.session import get_session
from app.guard import (
    Blocked,
    check_limits,
    detect_injection,
    preamble,
    scan_output,
    wrap_untrusted,
)
from app.llm.client import Message, ModelClient, ModelError, ModelTimeout
from app.llm.cost import estimate_cost_usd
from app.llm.registry import get_model_client
from app.llm.structured import SchemaError, complete_structured
from app.settings import Settings, get_settings
from app.trace import mark_error

router = APIRouter()

PROMPT_VERSION = "extract_v1"
_PROMPT = (Path(__file__).parent.parent / "llm" / "prompts" / f"{PROMPT_VERSION}.md").read_text()

SessionDep = Annotated[Session, Depends(get_session)]
ClientDep = Annotated[ModelClient, Depends(get_model_client)]
SettingsDep = Annotated[Settings, Depends(get_settings)]


def _error(status: int, code: str, detail: str) -> JSONResponse:
    mark_error(code, detail)
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
    doc = session.get(Document, doc_id)
    if doc is None:
        return _error(404, "not_found", "document not found")

    # 1. Idempotency: same document + same model + same prompt = same answer, paid for once.
    cached = session.exec(
        select(Extraction).where(
            Extraction.document_id == doc_id,
            Extraction.provider == client.name,
            Extraction.model == client.model,
            Extraction.prompt_version == PROMPT_VERSION,
        )
    ).first()
    if cached is not None:
        return ExtractOut(
            document_id=doc_id,
            cached=True,
            provider=cached.provider,
            model=cached.model,
            prompt_version=cached.prompt_version,
            tokens_in=cached.tokens_in,
            tokens_out=cached.tokens_out,
            latency_ms=cached.latency_ms,
            cost_usd=cached.cost_usd,
            extract=DocumentExtract.model_validate_json(cached.result_json),
        )

    # 2. Limits first: a kill switch and a daily budget bound the blast radius of everything below.
    if settings.guard_enabled:
        try:
            check_limits(settings, session)
        except Blocked as e:
            return _error(503 if e.kind == "kill_switch" else 429, e.kind, e.detail)

    # 3. Context is a budget: never send more than the configured window. Then treat what is
    #    left as data: strip known instruction patterns and fence it.
    text = doc.text[: settings.max_input_chars]
    report = None
    if settings.guard_enabled:
        text, report = detect_injection(text)
        body = wrap_untrusted(text or "(empty document)")
        system = f"{_PROMPT}\n\n{preamble()}"
    else:
        body = text or "(empty document)"
        system = _PROMPT
    messages = [
        Message(role="system", content=system),
        Message(role="user", content=f"Document '{doc.filename}':\n\n{body}"),
    ]

    # 4. Call with timeout, retry on retryable failures, validate, repair once.
    started = time.perf_counter()
    try:
        result, responses = await complete_structured(
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
        return _error(502, "provider_error", f"{client.name}: {e} (status {e.status})")
    except SchemaError as e:
        return _error(502, "schema_error", f"model output did not fit the schema: {e.detail}")
    latency_ms = int((time.perf_counter() - started) * 1000)

    # 5. Model output is untrusted input: check its figures against the source.
    guard_out = None
    if settings.guard_enabled and report is not None:
        guard_out = GuardOut(
            injection_detected=report.injection_detected,
            patterns=report.patterns,
            stripped_lines=report.stripped_lines,
            output_flags=scan_output(result.key_facts, doc.text),
        )

    # 6. Account for every token, including the repair call if there was one.
    tokens_in = sum(r.tokens_in for r in responses)
    tokens_out = sum(r.tokens_out for r in responses)
    model_used = responses[-1].model
    provider_used = responses[-1].provider
    cost = estimate_cost_usd(model_used, tokens_in, tokens_out)

    row = Extraction(
        document_id=doc_id,
        provider=client.name,
        model=client.model,
        prompt_version=PROMPT_VERSION,
        tokens_in=tokens_in,
        tokens_out=tokens_out,
        latency_ms=latency_ms,
        cost_usd=cost,
        result_json=json.dumps(result.model_dump()),
    )
    session.add(row)
    session.commit()

    return ExtractOut(
        document_id=doc_id,
        cached=False,
        provider=provider_used,
        model=model_used,
        prompt_version=PROMPT_VERSION,
        tokens_in=tokens_in,
        tokens_out=tokens_out,
        latency_ms=latency_ms,
        cost_usd=cost,
        extract=result,
        guard=guard_out,
    )
