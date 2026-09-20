"""Week 3: POST /ask. Retrieve, decide whether to answer at all, answer only from context, cite.

A system that always answers is worse than one that sometimes declines. Two gates before the
model is even called: is anything relevant enough (threshold), and afterwards: did the model
itself say the context supports the answer (grounded)?
"""

from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlmodel import Session

from app.api.schemas import ErrorOut
from app.db.session import get_session
from app.llm.client import ModelClient
from app.llm.registry import get_model_client
from app.retrieval.embed import Embedder, get_embedder
from app.settings import Settings, get_settings
from app.trace import mark_error

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


@router.post("/ask", response_model=AskOut, responses={502: {"model": ErrorOut}})
async def ask(
    body: AskIn,
    session: SessionDep,
    client: ClientDep,
    embedder: EmbedderDep,
    settings: SettingsDep,
) -> AskOut | JSONResponse:
    # TODO Week 3 (weeks/3/README.md). Suggested order:
    #   1. search(session, embedder, body.question, k=..., strategy=settings.chunk_strategy)
    #   2. Gate 1: top score below settings.relevance_threshold -> AskOut(abstained=True, ...)
    #      with a reason mentioning the threshold, and NO model call.
    #   3. With the guard on (settings.guard_enabled): check_limits(); then build the messages:
    #      system = the prompt (+ preamble())
    #      user = "Passages:\n\n[1] ...\n\n[2] ...\n\nQuestion: ..."
    #      each passage through detect_injection() then wrap_untrusted(label="passage").
    #   4. complete_structured(client, messages, AskAnswer, ...) with the retry/timeout settings.
    #      Provider or schema failure -> 502 provider_error via JSONResponse (mark_error too).
    #   5. Gate 2: not grounded, empty answer, or no valid citation number -> abstained=True
    #      with reason "the passages do not contain the answer".
    #   6. Map each valid [n] to Citation(n, chunk_id, document_id, filename, score, text).
    #   7. Fill provider, model, tokens, latency_ms, cost_usd (estimate_cost_usd) on the way out.
    mark_error("unsupported", "Week 3 exercise: implement ask")
    return JSONResponse(
        status_code=501,
        content=ErrorOut(
            error="not_implemented", detail="Week 3 exercise: implement ask"
        ).model_dump(),
    )
