"""The tools the agent may call. Each week adds some; the registry below is the whole list.

    week 1  get_customer, get_ticket           (app/tools/desk.py, you design them)

Everything goes through `call()`: validation before anything runs, approval for anything that
writes or spends, and an answer the model can read whatever happens. See app/tools/base.py.
"""

from typing import Any

from app.tools.base import NeedsApproval, ToolContext, ToolSpec, run_tool, schema
from app.tools.desk import GET_CUSTOMER, GET_TICKET

TOOLS: dict[str, ToolSpec] = {t.name: t for t in (GET_CUSTOMER, GET_TICKET)}


def tool_schemas(names: list[str] | None = None) -> list[dict[str, Any]]:
    """What the model is shown: every tool, or the named ones."""
    return [schema(t) for n, t in TOOLS.items() if names is None or n in names]


async def call(ctx: ToolContext, name: str, args: Any) -> str:
    return await run_tool(TOOLS, ctx, name, args)


__all__ = ["TOOLS", "NeedsApproval", "ToolContext", "ToolSpec", "call", "tool_schemas"]
