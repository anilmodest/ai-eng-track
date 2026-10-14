"""What every tool is made of, and the one door every tool call goes through.

A tool is a plain async function with a Pydantic argument model. Three things matter, and only
the first is about the function:

    the schema       what the model sees: the name, the description and the arguments' JSON
                     schema. The description is a prompt; a vague one gets wrong calls.
    the validation   the arguments are checked against the model BEFORE the function runs, so a
                     malformed call never reaches the system behind it.
    the answer       always text the model can read, including refusals and errors. A tool that
                     raises leaves the model nothing to recover from.

Tools that change something (`writes`) or spend money (`spends`) run only when a person has
approved that call: the loop stops with NeedsApproval and resumes when someone says yes. That rule
lives here, in code, because a rule in a prompt is a request and a rule in code is a boundary.
"""

import json
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from typing import Any

from pydantic import BaseModel, Field, ValidationError
from sqlmodel import Session

from app.llm.client import ModelClient
from app.settings import Settings
from app.trace import span


class ToolCall(BaseModel):
    """A model's request to run a tool: structured output, with consequences."""

    tool: str = Field(min_length=1)
    args: dict[str, Any] = Field(default_factory=dict)


@dataclass
class ToolContext:
    """What a tool may use while it runs. Built per request; nothing in it outlives the call."""

    session: Session
    settings: Settings
    client: ModelClient | None = None
    embedder: Any = None  # app.retrieval.embed.Embedder, from week 2
    approved: set[str] = field(default_factory=set)  # tool names a person approved for this run
    spent_usd: float = 0.0
    calls: list[str] = field(default_factory=list)


class NeedsApproval(Exception):
    """A tool that writes or spends was called without a person's yes. Not an error: a stop."""

    def __init__(self, tool: str, args: dict[str, Any]) -> None:
        super().__init__(f"{tool} needs a person's approval before it runs")
        self.tool = tool
        self.arguments = args


Runner = Callable[[ToolContext, Any], Awaitable[str]]


@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str
    args: type[BaseModel]
    run: Runner
    writes: bool = False  # changes something outside this request
    spends: bool = False  # costs money

    @property
    def needs_approval(self) -> bool:
        return self.writes or self.spends


def schema(spec: ToolSpec) -> dict[str, Any]:
    """What the model is shown for one tool."""
    flags = " [needs approval]" if spec.needs_approval else ""
    return {
        "name": spec.name,
        "description": spec.description + flags,
        "parameters": spec.args.model_json_schema(),
    }


def readable(e: ValidationError) -> str:
    """The first validation problem, in words a model can act on."""
    err = e.errors()[0]
    where = ".".join(str(p) for p in err.get("loc", ())) or "arguments"
    return f"{where}: {err['msg']}"


async def run_tool(tools: dict[str, ToolSpec], ctx: ToolContext, name: str, args: Any) -> str:
    """Validate, check approval, then run. Every outcome is text the model can read."""
    spec = tools.get(name)
    if spec is None:
        return f"error: unknown tool {name!r}; the tools are: {', '.join(tools)}"
    if not isinstance(args, dict):
        return f"error: arguments for {name} must be a JSON object, not {type(args).__name__}"
    try:
        parsed = spec.args.model_validate(args)
    except ValidationError as e:
        return f"error: invalid arguments for {name}: {readable(e)}"
    if spec.needs_approval and name not in ctx.approved:
        raise NeedsApproval(name, parsed.model_dump())
    ctx.calls.append(name)
    async with span(f"tool.{name}"):
        return await spec.run(ctx, parsed)


def as_json(data: dict[str, Any]) -> str:
    """Tool results that are records go back as compact JSON: unambiguous for the model."""
    return json.dumps(data, default=str, separators=(",", ":"))
