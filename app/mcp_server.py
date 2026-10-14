"""Serve the desk's tools to any MCP client (Claude Desktop, an IDE, another agent).

    MCP_TOKEN=reader uv run python -m app.mcp_server        # stdio transport

The Model Context Protocol is a transport, not a permission system. A client discovers the tools
and their schemas when it connects, calls them by name, and gets text back. Nothing in the
protocol stops a reader from calling issue_credit; this file does. Every call passes, in order:

    1. the token's scope    app/mcp_scopes.py: a reader cannot write, an agent cannot spend
    2. a rate limit         per token
    3. the tool's own door  app.tools.call: arguments validated, and an action that writes or
                            spends runs only if a person approved it (MCP_APPROVED)

and whatever happens, the answer is text: "denied: ...", "needs approval: ...", or the result.
"""

import inspect
import os
from typing import Any

from pydantic import BaseModel
from sqlmodel import Session

from app.db.session import get_engine
from app.llm.registry import get_model_client
from app.mcp_scopes import RateLimiter, ScopeError, approved_tools, check_scope
from app.retrieval.embed import get_embedder
from app.settings import get_settings
from app.tools import TOOLS, NeedsApproval, ToolContext
from app.tools import call as call_registered

TOKEN = os.environ.get("MCP_TOKEN", "reader")
_limiter = RateLimiter(max_calls=int(os.environ.get("MCP_RATE_LIMIT", "30")), window_s=60)


async def call_tool(token: str, tool: str, args: dict[str, Any]) -> str:
    """One MCP call, through every check, as text. What the server's handlers all call."""
    if tool not in TOOLS:
        return f"error: unknown tool {tool!r}"
    try:
        check_scope(token, tool)
        _limiter.check(token)
    except ScopeError as e:
        return f"denied: {e}"
    with Session(get_engine()) as session:
        ctx = ToolContext(
            session=session,
            settings=get_settings(),
            client=get_model_client(),
            embedder=get_embedder(),
            approved=approved_tools(),
        )
        try:
            return await call_registered(ctx, tool, args)
        except NeedsApproval as e:
            return f"needs approval: {e}"
        except Exception as e:  # a tool failing mid-call must not take the server down
            return f"error: {tool} failed: {e}"


def build_server() -> Any:
    """An MCP server with one handler per tool in the registry, schema and description included."""
    from mcp.server.mcpserver import MCPServer  # mcp 2.x; was mcp.server.fastmcp.FastMCP in 1.x

    server = MCPServer("ai-eng-track")
    for spec in TOOLS.values():
        server.add_tool(
            _handler(spec.name, spec.args), name=spec.name, description=spec.description
        )
    return server


def _handler(name: str, args_model: type[BaseModel]) -> Any:
    """A function whose signature is the tool's arguments, so the client sees the real schema.
    Validation still happens in app.tools.call: the signature is for discovery, not for trust."""

    async def handler(**kwargs: Any) -> str:
        return await call_tool(TOKEN, name, {k: v for k, v in kwargs.items() if v is not None})

    params = [
        inspect.Parameter(
            field,
            inspect.Parameter.KEYWORD_ONLY,
            annotation=info.annotation,
            default=inspect.Parameter.empty if info.is_required() else info.default,
        )
        for field, info in args_model.model_fields.items()
    ]
    handler.__name__ = name
    handler.__signature__ = inspect.Signature(params, return_annotation=str)  # type: ignore[attr-defined]
    handler.__annotations__ = {p.name: p.annotation for p in params} | {"return": str}
    return handler


def main() -> None:
    build_server().run(transport="stdio")


if __name__ == "__main__":
    main()
