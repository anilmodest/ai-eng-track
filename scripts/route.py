"""`make route ROUTE=start|core|pro`: set your difficulty once, after placement.

The exercises are the same on every route. What changes is how much is given to you:
  start  everything in app/llm is given; you build the endpoint, schema and idempotency
  core   retry and structured-output handling are reduced to signatures; you write the bodies
  pro    as core, plus the cost table; you also add routing, fallback and streaming

Stubs keep their signatures so the service still imports and Week 0 stays green.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MARK = "# STUB: removed for your route"

STUBS: dict[str, str] = {
    "app/llm/retry.py": f'''"""Retry with backoff, only for failures that retrying can fix.
{MARK}. Rebuild it: tests/weeks/test_week1.py says what it must do.
"""

from collections.abc import Awaitable, Callable


async def with_timeout[T](call: Awaitable[T], seconds: float) -> T:
    """Await `call`, raising ModelTimeout if it takes longer than `seconds`."""
    raise NotImplementedError("with_timeout: build me (weeks/1/README.md)")


async def with_retry[T](
    make_call: Callable[[], Awaitable[T]],
    *,
    attempts: int,
    base_delay_s: float,
    timeout_s: float,
) -> T:
    """Run make_call() up to `attempts` times with backoff. Retry only ModelError.retryable."""
    raise NotImplementedError("with_retry: build me (weeks/1/README.md)")
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
    raise NotImplementedError("complete_structured: build me (weeks/1/README.md)")
''',
    "app/llm/cost.py": f'''"""List prices in USD per 1M tokens.
{MARK}. Rebuild it: find current list prices and fill the table.
"""


def price_known(model: str) -> bool:
    raise NotImplementedError("price_known: build me (weeks/1/README.md)")


def estimate_cost_usd(model: str, tokens_in: int, tokens_out: int) -> float:
    raise NotImplementedError("estimate_cost_usd: build me (weeks/1/README.md)")
''',
}

REMOVE: dict[str, list[str]] = {
    "start": [],
    "core": ["app/llm/retry.py", "app/llm/structured.py"],
    "pro": ["app/llm/retry.py", "app/llm/structured.py", "app/llm/cost.py"],
}


def main(argv: list[str]) -> int:
    if len(argv) != 2 or argv[1] not in REMOVE:
        print("usage: make route ROUTE=start|core|pro")
        return 2
    route = argv[1]
    for rel in REMOVE[route]:
        path = ROOT / rel
        if path.exists() and MARK not in path.read_text():
            path.write_text(STUBS[rel])
            print(f"stubbed {rel}")
    (ROOT / ".route").write_text(route + "\n")
    print(f"route set to {route} (.route). Tier tests for this route now run in `make check`.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
