"""Tracing: every request is a tree of spans, each with a duration, tokens, cost and an error kind.

You cannot fix what you cannot see. A request that cost 0.4 cents is a fact; *which step* cost
0.3 of it is the thing you can act on. Spans are buffered per request in a contextvar and written
once, by the middleware, when the response is on its way out.
"""

import contextvars
import time
import uuid
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from enum import StrEnum

from sqlmodel import Field, Session, SQLModel, col, select


class ErrorKind(StrEnum):
    """One bucket per cause, so a dashboard can say what is failing, not just that it is."""

    provider_timeout = "provider_timeout"
    provider_error = "provider_error"
    schema_error = "schema_error"
    retrieval_empty = "retrieval_empty"
    guard_blocked = "guard_blocked"
    budget_exceeded = "budget_exceeded"
    kill_switch = "kill_switch"
    not_found = "not_found"
    unsupported = "unsupported"
    unknown = "unknown"


class Span(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    request_id: str = Field(index=True)
    name: str = Field(index=True)
    parent: str | None = None  # name of the parent span; None for the request root
    started_at: datetime
    duration_ms: int = 0
    tokens_in: int = 0
    tokens_out: int = 0
    cost_usd: float = 0.0
    error_kind: str | None = None
    detail: str = ""


class _Live:
    """A span still being timed. Mutable; becomes a Span row at the end."""

    def __init__(self, name: str, parent: str | None) -> None:
        self.name = name
        self.parent = parent
        self.started = time.perf_counter()
        self.started_at = datetime.now(UTC)
        self.tokens_in = 0
        self.tokens_out = 0
        self.cost_usd = 0.0
        self.error_kind: str | None = None
        self.detail = ""

    def row(self, request_id: str) -> Span:
        return Span(
            request_id=request_id,
            name=self.name,
            parent=self.parent,
            started_at=self.started_at,
            duration_ms=int((time.perf_counter() - self.started) * 1000),
            tokens_in=self.tokens_in,
            tokens_out=self.tokens_out,
            cost_usd=round(self.cost_usd, 6),
            error_kind=self.error_kind,
            detail=self.detail[:500],
        )


_request_id: contextvars.ContextVar[str | None] = contextvars.ContextVar("request_id", default=None)
_stack: contextvars.ContextVar[list[_Live] | None] = contextvars.ContextVar("stack", default=None)
_done: contextvars.ContextVar[list[Span] | None] = contextvars.ContextVar("done", default=None)


def begin_request(name: str) -> str:
    """Start a request root. Returns the request id (also sent back as X-Request-Id)."""
    rid = uuid.uuid4().hex[:12]
    _request_id.set(rid)
    _stack.set([_Live(name, None)])
    _done.set([])
    return rid


def current_request_id() -> str | None:
    return _request_id.get()


def mark_error(kind: ErrorKind | str, detail: str = "") -> None:
    """Record why the current request failed, on the innermost open span and the root."""
    stack = _stack.get()
    if not stack:
        return
    for s in (stack[-1], stack[0]):
        if s.error_kind is None:
            s.error_kind = str(kind)
            s.detail = detail


def add_usage(tokens_in: int, tokens_out: int, cost_usd: float) -> None:
    """Attribute tokens and cost to the innermost open span AND roll them up to the root."""
    stack = _stack.get()
    if not stack:
        return
    for s in {id(stack[-1]): stack[-1], id(stack[0]): stack[0]}.values():
        s.tokens_in += tokens_in
        s.tokens_out += tokens_out
        s.cost_usd += cost_usd


@asynccontextmanager
async def span(name: str) -> AsyncIterator[None]:
    """Time a step. Nested spans record their parent's name. No-op outside a request."""
    stack = _stack.get()
    if stack is None:
        yield
        return
    live = _Live(name, stack[-1].name)
    stack.append(live)
    try:
        yield
    except Exception as e:
        if live.error_kind is None:
            live.error_kind = ErrorKind.unknown
            live.detail = f"{type(e).__name__}: {e}"
        raise
    finally:
        stack.pop()
        done = _done.get()
        rid = _request_id.get()
        if done is not None and rid:
            done.append(live.row(rid))


def end_request(session: Session) -> list[Span]:
    """Close the root, persist every span of this request, clear the context."""
    stack = _stack.get()
    done = _done.get()
    rid = _request_id.get()
    if not stack or done is None or not rid:
        return []
    rows = [*done, stack[0].row(rid)]
    session.add_all(rows)
    session.commit()
    _stack.set(None)
    _done.set(None)
    _request_id.set(None)
    return rows


def spans_for(session: Session, request_id: str) -> list[Span]:
    return list(
        session.exec(select(Span).where(Span.request_id == request_id).order_by(col(Span.id))).all()
    )


def recent_roots(session: Session, limit: int = 20) -> list[Span]:
    return list(
        session.exec(
            select(Span)
            .where(col(Span.parent).is_(None))
            .order_by(col(Span.id).desc())
            .limit(limit)
        ).all()
    )


def spent_since(session: Session, since: datetime) -> float:
    """Total attributed model cost across request roots since `since` (the budget's input)."""
    rows = session.exec(
        select(Span.cost_usd).where(col(Span.parent).is_(None), Span.started_at >= since)
    ).all()
    return float(sum(rows))
