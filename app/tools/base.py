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
from app.trace import set_attribute, span

# Tools whose results carry text someone outside the desk wrote: a customer's ticket, a page of
# the manual. With the guard on, their results reach the model fenced as data (week 5).
THIRD_PARTY = {"get_ticket", "search_docs"}


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
    # Fence third-party text as data before a model reads it (week 5). On wherever a model is
    # the reader: the tasks API and the MCP server set it from GUARD_ENABLED.
    fence_untrusted: bool = False
    # The tools this run was offered (week 5, least agency); None means every tool. A tool that
    # was not offered is refused here, whatever the model asks for: the offer is a boundary too.
    offered: set[str] | None = None


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
    if ctx.offered is not None and name not in ctx.offered:
        offered = ", ".join(sorted(ctx.offered))
        return f"error: {name} is not available for this request; use: {offered}"
    if not isinstance(args, dict):
        return f"error: arguments for {name} must be a JSON object, not {type(args).__name__}"
    try:
        parsed = spec.args.model_validate(args)
    except ValidationError as e:
        return f"error: invalid arguments for {name}: {readable(e)}"
    if spec.needs_approval and name not in ctx.approved:
        async with span("approval"):
            set_attribute("approval.tool", name)
            set_attribute("approval.granted", False)
        raise NeedsApproval(name, parsed.model_dump())
    ctx.calls.append(name)
    async with span(f"tool.{name}"):
        set_attribute("gen_ai.operation.name", "execute_tool")
        set_attribute("gen_ai.tool.name", name)
        result = await spec.run(ctx, parsed)
    if name in THIRD_PARTY and ctx.fence_untrusted:
        # Text someone else wrote (a customer's ticket, a page of the manual) goes back to the
        # model fenced as data, with known instruction patterns stripped (week 5, app/guard.py).
        from app.guard import fence_tool_result

        result = fence_tool_result(name, result)
    return result


def as_json(data: dict[str, Any]) -> str:
    """Tool results that are records go back as compact JSON: unambiguous for the model."""
    return json.dumps(data, default=str, separators=(",", ":"))
