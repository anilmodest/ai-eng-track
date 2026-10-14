"""Week 5: read the traces. GET /traces lists recent requests; GET /traces/{id} shows one tree."""

import json
from typing import Annotated, Any

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
    attributes: dict[str, Any] = {}


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
        spans=[
            SpanOut(
                **s.model_dump(exclude={"id", "request_id", "started_at", "attributes"}),
                attributes=json.loads(s.attributes or "{}"),
            )
            for s in spans
        ],
    )


@router.get("/traces/{request_id}/otel")
def get_trace_otel(request_id: str, session: SessionDep) -> dict[str, Any]:
    """The same trace in OpenTelemetry's OTLP JSON shape: what an employer's tracing tool reads.

    Every span keeps its OpenTelemetry-style attributes (gen_ai.request.model,
    gen_ai.usage.input_tokens, gen_ai.tool.name, approval.tool, ...) and adds its cost and error
    kind, so the export holds everything the service knows about the request.
    """
    spans = spans_for(session, request_id)
    if not spans:
        raise HTTPException(status_code=404, detail="no trace with that request id")
    trace_id = (request_id * 3)[:32].ljust(32, "0")

    def nanos(s: Any, extra_ms: int = 0) -> str:
        return str(int((s.started_at.timestamp() * 1000 + extra_ms) * 1_000_000))

    def value(v: Any) -> dict[str, Any]:
        if isinstance(v, bool):
            return {"boolValue": v}
        if isinstance(v, int):
            return {"intValue": str(v)}
        if isinstance(v, float):
            return {"doubleValue": v}
        return {"stringValue": str(v)}

    ids = {s.name: f"{i + 1:016x}" for i, s in enumerate(spans)}
    out = []
    for i, s in enumerate(spans):
        attrs = json.loads(s.attributes or "{}")
        attrs |= {"app.cost_usd": s.cost_usd}
        if s.error_kind:
            attrs["error.type"] = s.error_kind
        out.append(
            {
                "traceId": trace_id,
                "spanId": f"{i + 1:016x}",
                "parentSpanId": ids.get(s.parent or "", ""),
                "name": s.name,
                "startTimeUnixNano": nanos(s),
                "endTimeUnixNano": nanos(s, s.duration_ms),
                "attributes": [{"key": k, "value": value(v)} for k, v in attrs.items()],
                "status": {"code": 2 if s.error_kind else 1},
            }
        )
    return {
        "resourceSpans": [
            {
                "resource": {
                    "attributes": [
                        {"key": "service.name", "value": {"stringValue": "ai-eng-track"}}
                    ]
                },
                "scopeSpans": [{"scope": {"name": "app.trace"}, "spans": out}],
            }
        ]
    }
