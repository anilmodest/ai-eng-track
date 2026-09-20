"""Week 5: read the traces. GET /traces lists recent requests; GET /traces/{id} shows one tree."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session

from app.db.session import get_session
from app.trace import recent_roots, spans_for

router = APIRouter()
SessionDep = Annotated[Session, Depends(get_session)]


class SpanOut(BaseModel):
    name: str
    parent: str | None
    duration_ms: int
    tokens_in: int
    tokens_out: int
    cost_usd: float
    error_kind: str | None
    detail: str


class TraceOut(BaseModel):
    request_id: str
    spans: list[SpanOut]


class RootOut(BaseModel):
    request_id: str
    name: str
    duration_ms: int
    cost_usd: float
    error_kind: str | None


@router.get("/traces", response_model=list[RootOut])
def list_traces(session: SessionDep, limit: int = 20) -> list[RootOut]:
    return [
        RootOut(
            request_id=s.request_id,
            name=s.name,
            duration_ms=s.duration_ms,
            cost_usd=s.cost_usd,
            error_kind=s.error_kind,
        )
        for s in recent_roots(session, limit)
    ]


@router.get("/traces/{request_id}", response_model=TraceOut)
def get_trace(request_id: str, session: SessionDep) -> TraceOut:
    spans = spans_for(session, request_id)
    if not spans:
        raise HTTPException(status_code=404, detail="no trace with that request id")
    return TraceOut(
        request_id=request_id,
        spans=[SpanOut(**s.model_dump(exclude={"id", "request_id", "started_at"})) for s in spans],
    )
