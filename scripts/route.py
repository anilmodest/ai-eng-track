"""`make route ROUTE=start|core|pro`: set your difficulty once, after your mentor places you.

The exercises are the same on every route. What changes is what you are given, as the framework
puts it:

  start  faults named, worked example given
         every helper is given and working; each week's stub names what goes wrong if skipped;
         weeks/N/routes/worked_example.py solves a smaller sibling of the exercise in full
  core   faults present, not located, count not given
         each week's exercise file is a complete implementation with mistakes planted in it
         (weeks/N/routes/core/); the gate catches some, review catches the rest;
         app/trace.py is signatures only: you instrument the project yourself
  pro    no helpers, one real constraint added
         retry.py, structured.py, cost.py and trace.py are signatures only; each week's
         weeks/N/routes/pro.md states one constraint the finished piece must meet

Run it once. Running it again re-applies the same route; it never mixes two.
"""

import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MARK = "# STUB: removed for your route"
ROUTES = ("start", "core", "pro")

STUBS: dict[str, str] = {
    "app/llm/retry.py": f'''"""Retry with backoff, only for failures that retrying can fix.
{MARK}. Rebuild it: tests/weeks/test_week1.py says what it must do.
"""

from collections.abc import Awaitable, Callable


async def with_timeout[T](call: Awaitable[T], seconds: float) -> T:
    """Await `call`, raising ModelTimeout if it takes longer than `seconds`."""
    raise NotImplementedError("with_timeout: build me (weeks/1/routes/pro.md)")


async def with_retry[T](
    make_call: Callable[[], Awaitable[T]],
    *,
    attempts: int,
    base_delay_s: float,
    timeout_s: float,
) -> T:
    """Run make_call() up to `attempts` times with backoff. Retry only ModelError.retryable."""
    raise NotImplementedError("with_retry: build me (weeks/1/routes/pro.md)")
''',
    "app/llm/structured.py": f'''"""Ask for JSON, validate against a schema, repair once, then fail.
{MARK}. Rebuild it: tests/weeks/test_week1.py says what it must do.
"""

from pydantic import BaseModel

from app.llm.client import Message, ModelClient, ModelResponse


class SchemaError(Exception):
    """The model answered, twice, and neither answer fitted the schema."""

    def __init__(self, detail: str, raw: str) -> None:
        super().__init__(detail)
        self.detail = detail
        self.raw = raw


async def complete_structured[T: BaseModel](
    client: ModelClient,
    messages: list[Message],
    schema: type[T],
    *,
    attempts: int,
    base_delay_s: float,
    timeout_s: float,
) -> tuple[T, list[ModelResponse]]:
    """Return the parsed object and every response it took to get there."""
    raise NotImplementedError("complete_structured: build me (weeks/1/routes/pro.md)")
''',
    "app/llm/cost.py": f'''"""List prices in USD per 1M tokens.
{MARK}. Rebuild it: find current list prices and fill the table.
"""


def price_known(model: str) -> bool:
    raise NotImplementedError("price_known: build me (weeks/1/routes/pro.md)")


def estimate_cost_usd(model: str, tokens_in: int, tokens_out: int) -> float:
    raise NotImplementedError("estimate_cost_usd: build me (weeks/1/routes/pro.md)")
''',
    "app/trace.py": f'''"""Tracing: each request is a tree of spans (duration, tokens, cost, error).
{MARK}. Every name below is used by the service; make each one do its job.
tests/weeks/test_week5.py says what a trace must contain. Week 5, Area 9: instrument it yourself.
"""

import uuid
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import datetime
from enum import StrEnum

from sqlmodel import Field, Session, SQLModel


class ErrorKind(StrEnum):
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
    parent: str | None = None
    started_at: datetime
    duration_ms: int = 0
    tokens_in: int = 0
    tokens_out: int = 0
    cost_usd: float = 0.0
    error_kind: str | None = None
    detail: str = ""


def begin_request(name: str) -> str:
    """Start a request root; return the request id (sent back as X-Request-Id)."""
    return uuid.uuid4().hex[:12]  # TODO: open the root span and remember it for this request


def current_request_id() -> str | None:
    return None  # TODO


def mark_error(kind: ErrorKind | str, detail: str = "") -> None:
    """Record why the current request failed, on the innermost open span and the root."""
    return None  # TODO


def note(text: str) -> None:
    """Leave a short note on the request root (what was asked, what was answered)."""
    return None  # TODO


def add_usage(tokens_in: int, tokens_out: int, cost_usd: float) -> None:
    """Attribute tokens and cost to the innermost open span AND roll them up to the root."""
    return None  # TODO


@asynccontextmanager
async def span(name: str) -> AsyncIterator[None]:
    """Time a step under the current request. No-op outside a request."""
    yield  # TODO: record start, end, parent, and an error kind if the body raises


def end_request(session: Session) -> list[Span]:
    """Close the root, persist every span of this request, clear the context."""
    return []  # TODO


def spans_for(session: Session, request_id: str) -> list[Span]:
    return []  # TODO: every span of that request, in order


def recent_roots(session: Session, limit: int = 20) -> list[Span]:
    return []  # TODO: newest request roots first


def spent_since(session: Session, since: datetime) -> float:
    """Total attributed model cost across request roots since `since` (the budget's input)."""
    return 0.0  # TODO
''',
}

REMOVE: dict[str, list[str]] = {
    "start": [],
    "core": ["app/trace.py"],
    "pro": ["app/llm/retry.py", "app/llm/structured.py", "app/llm/cost.py", "app/trace.py"],
}


def _restore_from_git(rel: str) -> None:
    """Bring a file back to the template's version before applying a route on top."""
    import subprocess

    subprocess.run(["git", "checkout", "--", rel], cwd=ROOT, check=False, capture_output=True)


def apply(route: str) -> None:
    # Start from the template state for every file a route can touch, so routes never mix.
    touched = set(sum(REMOVE.values(), []))
    for week_dir in sorted(ROOT.glob("weeks/*/routes/core")):
        for f in week_dir.iterdir():
            touched.add(f.name.replace("__", "/"))
    for rel in sorted(touched):
        _restore_from_git(rel)

    if route == "core":
        n = 0
        for week_dir in sorted(ROOT.glob("weeks/*/routes/core")):
            for f in sorted(week_dir.iterdir()):
                rel = f.name.replace("__", "/")
                shutil.copy(f, ROOT / rel)
                n += 1
        print(f"core: {n} exercise files now carry planted faults (not located, count not given)")
    for rel in REMOVE[route]:
        path = ROOT / rel
        if path.exists() and MARK not in path.read_text(encoding="utf-8"):
            path.write_text(STUBS[rel], encoding="utf-8")
            print(f"{route}: {rel} is now signatures only")
    (ROOT / ".route").write_text(route + "\n")
    print(f"route set to {route} (.route). Read weeks/N/routes/{route}.md each week.")


def main(argv: list[str]) -> int:
    if len(argv) != 2 or argv[1] not in ROUTES:
        print("usage: make route ROUTE=start|core|pro")
        return 2
    marker = ROOT / ".route"
    if marker.exists():
        current = marker.read_text().strip()
        print(
            f"route already set to {current}. Applying a route restores the exercise files to the"
        )
        print("template's version, which would discard work you have done on them.")
        print("If your mentor changed your route at session 2: delete .route, commit or stash your")
        print("work, and run this again.")
        return 1
    apply(argv[1])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
