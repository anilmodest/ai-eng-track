"""Week 4: POST /tasks/run. One question, three ways: plain code, a workflow, or an agent."""

import time
from typing import Annotated, Literal

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlmodel import Session

from app.agents import plain
from app.agents.agent import AgentStep, run_agent
from app.agents.tools import ToolContext
from app.agents.workflow import run_workflow
from app.db.session import get_session
from app.llm.client import ModelClient
from app.llm.registry import get_model_client
from app.retrieval.embed import Embedder, get_embedder
from app.settings import Settings, get_settings

router = APIRouter()

SessionDep = Annotated[Session, Depends(get_session)]
ClientDep = Annotated[ModelClient, Depends(get_model_client)]
EmbedderDep = Annotated[Embedder, Depends(get_embedder)]
SettingsDep = Annotated[Settings, Depends(get_settings)]

Mode = Literal["plain", "workflow", "agent"]


class TaskIn(BaseModel):
    question: str = Field(min_length=3, max_length=1000)
    mode: Mode = "agent"
    approved: bool = False  # the human checkpoint for tools that cost money


class TaskOut(BaseModel):
    mode: Mode
    status: str
    answer: str
    calls: list[str]
    steps: list[AgentStep] = []
    tokens_in: int = 0
    tokens_out: int = 0
    cost_usd: float = 0.0
    latency_ms: int = 0


@router.post("/tasks/run", response_model=TaskOut)
async def run_task(
    body: TaskIn,
    session: SessionDep,
    client: ClientDep,
    embedder: EmbedderDep,
    settings: SettingsDep,
) -> TaskOut:
    started = time.perf_counter()
    ctx = ToolContext(
        session=session, embedder=embedder, settings=settings, client=client, approved=body.approved
    )
    if body.mode == "plain":
        ans = plain.answer(session, body.question)
        return TaskOut(
            mode="plain",
            status="done" if ans else "unsupported",
            answer=ans or "plain code has no rule for this question",
            calls=[],
            latency_ms=int((time.perf_counter() - started) * 1000),
        )
    if body.mode == "workflow":
        w = await run_workflow(ctx, body.question)
        return TaskOut(
            mode="workflow",
            status=w.status,
            answer=w.answer,
            calls=w.calls,
            cost_usd=round(ctx.spent_usd, 6),
            latency_ms=int((time.perf_counter() - started) * 1000),
        )
    a = await run_agent(ctx, body.question)
    return TaskOut(
        mode="agent",
        status=a.status,
        answer=a.answer,
        calls=ctx.calls,
        steps=a.steps,
        tokens_in=a.tokens_in,
        tokens_out=a.tokens_out,
        cost_usd=a.cost_usd,
        latency_ms=a.latency_ms,
    )
