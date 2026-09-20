"""Week 3: POST /ask. Retrieve, decide whether to answer at all, answer only from context, cite.

A system that always answers is worse than one that sometimes declines. Two gates before the
model is even called: is anything relevant enough (threshold), and afterwards: did the model
itself say the context supports the answer (grounded)?
"""

import time
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlmodel import Session

from app.api.schemas import ErrorOut
from app.db.session import get_session
from app.guard import Blocked, check_limits, detect_injection, preamble, wrap_untrusted
from app.llm.client import Message, ModelClient, ModelError, ModelTimeout
from app.llm.cost import estimate_cost_usd
from app.llm.registry import get_model_client
from app.llm.structured import SchemaError, complete_structured
from app.retrieval.embed import Embedder, get_embedder
from app.retrieval.store import Hit, search
from app.settings import Settings, get_settings
from app.trace import mark_error, note

router = APIRouter()

PROMPT_VERSION = "ask_v1"
_PROMPT = (Path(__file__).parent.parent / "llm" / "prompts" / f"{PROMPT_VERSION}.md").read_text()

SessionDep = Annotated[Session, Depends(get_session)]
ClientDep = Annotated[ModelClient, Depends(get_model_client)]
EmbedderDep = Annotated[Embedder, Depends(get_embedder)]
SettingsDep = Annotated[Settings, Depends(get_settings)]


class AskIn(BaseModel):
    question: str = Field(min_length=3, max_length=2000)
    k: int | None = None


class AskAnswer(BaseModel):
    """What the model must return. `grounded=false` is a legitimate, expected answer."""

    answer: str
    citations: list[int]
    grounded: bool


class Citation(BaseModel):
    n: int
    chunk_id: int
    document_id: int
    filename: str
    score: float
    text: str


class AskOut(BaseModel):
    question: str
    abstained: bool
    injection_detected: bool = False
    reason: str | None = None
    answer: str | None = None
    citations: list[Citation] = []
    top_score: float | None = None
    provider: str | None = None
    model: str | None = None
    tokens_in: int = 0
    tokens_out: int = 0
    latency_ms: int = 0
    cost_usd: float = 0.0


def build_messages(question: str, hits: list[Hit], guard: bool) -> tuple[list[Message], bool]:
    """Number the passages; with the guard on, strip injections and fence each one as data."""
    injected = False
    parts: list[str] = []
    for i, h in enumerate(hits, start=1):
        text = h.text
        if guard:
            text, report = detect_injection(text)
            injected = injected or report.injection_detected
            text = wrap_untrusted(text, label="passage")
        parts.append(f"[{i}] {text}")
    context = "\n\n".join(parts)
    system = f"{_PROMPT}\n\n{preamble()}" if guard else _PROMPT
    return [
        Message(role="system", content=system),
        Message(role="user", content=f"Passages:\n\n{context}\n\nQuestion: {question}"),
    ], injected


@router.post("/ask", response_model=AskOut, responses={502: {"model": ErrorOut}})
async def ask(
    body: AskIn,
    session: SessionDep,
    client: ClientDep,
    embedder: EmbedderDep,
    settings: SettingsDep,
) -> AskOut | JSONResponse:
    started = time.perf_counter()
    hits = search(
        session,
        embedder,
        body.question,
        k=body.k or settings.search_k,
        strategy=settings.chunk_strategy,
    )
    top = hits[0].score if hits else None

    # Gate 1: nothing relevant enough -> decline before spending a token.
    if top is None or top <= settings.relevance_threshold:
        return AskOut(
            question=body.question,
            abstained=True,
            reason=(
                "no passage scored above the relevance threshold "
                f"({top if top is not None else 0:.2f} < {settings.relevance_threshold:.2f})"
            ),
            top_score=top,
            latency_ms=int((time.perf_counter() - started) * 1000),
        )

    if settings.guard_enabled:
        try:
            check_limits(settings, session)
        except Blocked as e:
            mark_error(e.kind, e.detail)
            return JSONResponse(
                status_code=503 if e.kind == "kill_switch" else 429,
                content=ErrorOut(error=e.kind, detail=e.detail).model_dump(),
            )
    messages, injected = build_messages(body.question, hits, settings.guard_enabled)
    try:
        result, responses = await complete_structured(
            client,
            messages,
            AskAnswer,
            attempts=settings.model_retry_attempts,
            base_delay_s=settings.model_retry_base_delay_s,
            timeout_s=settings.model_timeout_s,
        )
    except (ModelTimeout, ModelError, SchemaError) as e:
        # A provider failure is not an abstention; say so with a typed error.
        mark_error("provider_error", str(e))
        return AskOut(question=body.question, abstained=True, reason=str(e), top_score=top)

    tokens_in = sum(r.tokens_in for r in responses)
    tokens_out = sum(r.tokens_out for r in responses)
    model_used = responses[-1].model
    usage = {
        "provider": responses[-1].provider,
        "model": model_used,
        "tokens_in": tokens_in,
        "tokens_out": tokens_out,
        "latency_ms": int((time.perf_counter() - started) * 1000),
        "cost_usd": estimate_cost_usd(model_used, tokens_in, tokens_out),
    }

    # Gate 2: the model read the passages and says they do not answer the question.
    valid = list(result.citations)
    if not result.answer.strip() or not valid:
        note(f"Q: {body.question} | A: (declined: the passages do not contain the answer)")
        return AskOut(
            question=body.question,
            abstained=True,
            injection_detected=injected,
            reason="the passages do not contain the answer",
            top_score=top,
            **usage,
        )

    citations = [
        Citation(
            n=n,
            chunk_id=hits[n - 1].chunk_id,
            document_id=hits[n - 1].document_id,
            filename=hits[n - 1].filename,
            score=hits[n - 1].score,
            text=hits[n - 1].text,
        )
        for n in valid
    ]
    note(f"Q: {body.question} | A: {result.answer.strip()}")
    return AskOut(
        question=body.question,
        abstained=False,
        injection_detected=injected,
        answer=result.answer.strip(),
        citations=citations,
        top_score=top,
        **usage,
    )
