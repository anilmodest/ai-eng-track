"""Week 4: POST /tasks/run. One request, three ways: plain code, a workflow, or an agent.

`approve` is the human checkpoint: the names of the tools a person has approved for this run.
Anything that writes or spends and is not in it stops the run with status "needs_approval" and
the pending action in `pending`; nothing has happened yet. Run it again with the tool approved to
let it through.

The week 5 limits hold here too: with the kill switch on, or today's budget spent, a workflow or
agent run is refused (503 or 429) before its first model call. Plain code calls no model.
"""

import time
from typing import Annotated, Any, Literal

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlmodel import Session

from app.agents import plain
from app.agents.agent import AgentStep, run_agent
from app.agents.routing import tools_for
from app.agents.workflow import run_workflow
from app.api.schemas import ErrorOut
from app.db.session import get_session
from app.guard import Blocked, check_limits
from app.llm.client import ModelClient
from app.llm.masking import MaskingClient, start_run
from app.llm.registry import get_model_client
from app.retrieval.embed import Embedder, get_embedder
from app.settings import Settings, get_settings
from app.tools import ToolContext
from app.trace import mark_error, note

router = APIRouter()

SessionDep = Annotated[Session, Depends(get_session)]
ClientDep = Annotated[ModelClient, Depends(get_model_client)]
EmbedderDep = Annotated[Embedder, Depends(get_embedder)]
SettingsDep = Annotated[Settings, Depends(get_settings)]

Mode = Literal["plain", "workflow", "agent"]


class TaskIn(BaseModel):
    question: str = Field(min_length=3, max_length=2000)
    mode: Mode = "agent"
    approve: list[str] = Field(default_factory=list, description="tools a person approved")


class TaskOut(BaseModel):
    mode: Mode
    status: str
    answer: str
    calls: list[str]  # the tools that actually ran
    steps: list[AgentStep] = []
    pending: dict[str, Any] | None = None
    tokens_in: int = 0
    tokens_out: int = 0
    cost_usd: float = 0.0
    latency_ms: int = 0


@router.post(
    "/tasks/run",
    response_model=TaskOut,
    responses={429: {"model": ErrorOut}, 503: {"model": ErrorOut}},
)
async def run_task(
    body: TaskIn,
    session: SessionDep,
    client: ClientDep,
    embedder: EmbedderDep,
    settings: SettingsDep,
) -> TaskOut | JSONResponse:
    started = time.perf_counter()
    ctx = ToolContext(
        session=session,
        settings=settings,
        client=client,
        embedder=embedder,
        approved=set(body.approve),
        fence_untrusted=settings.guard_enabled,
    )
    # Every model call in this run is masked (week 5, when MASK_PERSONAL_DATA is on) and recorded.
    start_run()
    ctx.client = MaskingClient(client, settings, session)

    # On the trace root, so cost can be attributed per ticket (scripts/trace_report.py).
    note(f"{body.mode}: {body.question[:300]}")

    def ms() -> int:
        return int((time.perf_counter() - started) * 1000)

    if body.mode == "plain":
        ans = plain.answer(session, body.question)
        return TaskOut(
            mode="plain",
            status="done" if ans else "unsupported",
            answer=ans or "plain code has no rule for this request",
            calls=[],
            latency_ms=ms(),
        )
    # Limits first: the kill switch and the daily budget bound an agent's model calls as well.
    try:
        check_limits(settings, session)
    except Blocked as e:
        mark_error(e.kind, e.detail)
        return JSONResponse(
            status_code=503 if e.kind == "kill_switch" else 429,
            content=ErrorOut(error=e.kind, detail=e.detail).model_dump(),
        )

    if body.mode == "workflow":
        w = await run_workflow(ctx, body.question)
        return TaskOut(
            mode="workflow",
            status=w.status,
            answer=w.answer,
            calls=w.calls,
            pending=w.pending,
            cost_usd=round(ctx.spent_usd, 6),
            latency_ms=ms(),
        )
    # Least agency (week 5): offered only the tools this request's task needs, and refused any
    # other, in app/tools/base.py, whatever the model asks for.
    offered = tools_for(body.question)
    ctx.offered = set(offered)
    a = await run_agent(ctx, body.question, tools=offered)
    return TaskOut(
        mode="agent",
        status=a.status,
        answer=a.answer,
        calls=list(ctx.calls),
        steps=a.steps,
        pending=a.pending,
        tokens_in=a.tokens_in,
        tokens_out=a.tokens_out,
        cost_usd=a.cost_usd,
        latency_ms=a.latency_ms,
    )
