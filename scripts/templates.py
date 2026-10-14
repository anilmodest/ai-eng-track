"""Build the three route templates from this source repo: one public template per route.

    uv run python scripts/templates.py build --route core --out build/templates/core
    uv run python scripts/templates.py build --all --out build/templates

The exercises are the same on every route. What changes is what a fellow is given:

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

A fellow never applies a route. They create their repository from their route's template, so it
holds that route and nothing of the other two: no planted-fault files to read, no worked examples
to borrow, no command to switch. `.github/workflows/publish-templates.yml` runs this on every push
to main and pushes the three trees to `<owner>/<prefix>-start|core|pro`.

What a build does, in order:
  1. copy every tracked file except the source-only ones (SOURCE_ONLY);
  2. on core, copy each week's planted-fault files over the exercise files;
     on core and pro, replace the helpers in REMOVE with signatures only;
  3. drop every weeks/N/routes/ file that is not this route's;
  4. strip text marked for other routes or for the source only (see strip_marked);
  5. write `.route` and `.template.json`, whose `week_files` lists, per week, the files that
     differ by route. A route change at session 2 replaces exactly those, for the weeks to come.
"""

import argparse
import json
import re
import shutil
import subprocess
import sys
from datetime import UTC, datetime
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


# Never shipped to a fellow: the machinery that makes the templates, and its own test.
SOURCE_ONLY = {
    "scripts/templates.py",
    "tests/unit/test_templates.py",
    ".github/workflows/publish-templates.yml",
    "docs/templates.md",
    "docs/architecture.md",
}
SOURCE_ONLY_DIRS = ("build/",)

# Which week each helper belongs to, so a route change knows what it may replace.
HELPER_WEEK = {
    "app/llm/retry.py": 1,
    "app/llm/structured.py": 1,
    "app/llm/cost.py": 1,
    "app/trace.py": 5,
}

# Text for one route only:      <!-- route:start --> ... <!-- /route -->   (or route:core,pro)
# Text for the source repo only: <!-- source-only --> ... <!-- /source-only -->
# and, in code, Makefiles and YAML:  # source-only:begin  ...  # source-only:end
_MD_ROUTE = re.compile(r"<!-- route:([a-z,]+) -->\n?(.*?)<!-- /route -->\n?", re.S)
_MD_SOURCE = re.compile(r"<!-- source-only -->\n?.*?<!-- /source-only -->\n?", re.S)
_HASH_SOURCE = re.compile(r"^[ \t]*# source-only:begin\n.*?^[ \t]*# source-only:end\n", re.S | re.M)
_TEXT_SUFFIXES = {".md", ".py", ".yml", ".yaml", ".toml", ".sh", ".txt", ".json", ""}


def strip_marked(text: str, route: str) -> str:
    """Keep this route's marked text without its markers; drop other routes' and source-only."""

    def keep_if_mine(m: re.Match[str]) -> str:
        return m.group(2) if route in m.group(1).split(",") else ""

    text = _MD_ROUTE.sub(keep_if_mine, text)
    text = _MD_SOURCE.sub("", text)
    return _HASH_SOURCE.sub("", text)


def tracked_files(root: Path) -> list[str]:
    """Every file git knows about or would add, so an uncommitted new file is not lost."""
    out = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    return sorted({line for line in out.splitlines() if line and (root / line).is_file()})


def source_sha(root: Path) -> str:
    def git(*args: str) -> str:
        r = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True)
        return r.stdout.strip() if r.returncode == 0 else ""

    sha = git("rev-parse", "HEAD") or "unknown"
    return sha + ("-dirty" if git("status", "--porcelain") else "")


def _core_targets(root: Path) -> dict[str, tuple[int, Path]]:
    """weeks/N/routes/core/app__api__ask.py -> ("app/api/ask.py", (N, the faulty file))."""
    targets: dict[str, tuple[int, Path]] = {}
    for week_dir in sorted(root.glob("weeks/*/routes/core")):
        week = int(week_dir.parent.parent.name)
        for f in sorted(week_dir.iterdir()):
            targets[f.name.replace("__", "/")] = (week, f)
    return targets


def _is_route_file(rel: str) -> bool:
    return re.match(r"weeks/\d+/routes/", rel) is not None


def _keeps_route_file(rel: str, route: str) -> bool:
    """weeks/N/routes/: keep only this route's page, and the worked example on start."""
    name = rel.split("/routes/", 1)[1]
    if name == "README.md":
        return False  # explains all three routes; a template holds one
    if name.startswith("core/"):
        return False  # copied into place on core, never shipped as a folder of faults
    if name == "worked_example.py":
        return route == "start"
    return name == f"{route}.md"


def build(root: Path, route: str, out: Path) -> dict[str, object]:
    """Write the `route` template into `out` (emptied first). Returns its .template.json."""
    if route not in ROUTES:
        raise ValueError(f"route must be one of {ROUTES}, not {route!r}")
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)

    week_files: dict[int, set[str]] = {}
    for rel in tracked_files(root):
        if rel in SOURCE_ONLY or rel.startswith(SOURCE_ONLY_DIRS) or rel == ".route":
            continue
        if _is_route_file(rel):
            if not _keeps_route_file(rel, route):
                continue
            week_files.setdefault(int(rel.split("/")[1]), set()).add(rel)
        dest = out / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(root / rel, dest)

    for rel, (week, faulty) in _core_targets(root).items():
        week_files.setdefault(week, set()).add(rel)
        if route == "core":
            shutil.copyfile(faulty, out / rel)
    for rel, week in HELPER_WEEK.items():
        week_files.setdefault(week, set()).add(rel)
    for rel in REMOVE[route]:
        _write(out / rel, STUBS[rel])

    for path in out.rglob("*"):
        if path.is_file() and path.suffix in _TEXT_SUFFIXES:
            try:
                text = path.read_bytes().decode("utf-8")  # as stored: CRLF stays visible
            except UnicodeDecodeError:
                continue
            # A Windows checkout has CRLF; a template is LF wherever it was built.
            stripped = strip_marked(text.replace("\r\n", "\n"), route)
            if stripped != text:
                _write(path, stripped)

    sha = source_sha(root)
    meta: dict[str, object] = {
        "programme": "ai-eng-track",
        "route": route,
        "source_sha": sha,
        "template_version": f"{datetime.now(UTC):%Y-%m-%d}.{sha[:7]}",
        "week_files": {str(w): sorted(fs) for w, fs in sorted(week_files.items())},
    }
    _write(out / ".route", route + "\n")
    _write(out / ".template.json", json.dumps(meta, indent=2) + "\n")
    return meta


def _write(path: Path, text: str) -> None:
    """LF on every platform: a template built on Windows must match one built in CI."""
    path.write_text(text, encoding="utf-8", newline="\n")


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Build the route templates from this repo.")
    sub = parser.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build", help="build one route's template, or all three")
    b.add_argument("--route", choices=ROUTES)
    b.add_argument("--all", action="store_true", help="all three, into OUT/start|core|pro")
    b.add_argument("--out", type=Path, default=ROOT / "build" / "templates")
    args = parser.parse_args(argv)

    if args.all == bool(args.route):
        parser.error("give exactly one of --route or --all")
    routes = ROUTES if args.all else (args.route,)
    for route in routes:
        out = args.out / route if args.all else args.out
        meta = build(ROOT, route, out)
        files = sum(1 for p in out.rglob("*") if p.is_file())
        print(f"{route}: {files} files -> {out}  ({meta['template_version']})")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
