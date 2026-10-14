"""Week 4: serve the desk's tools to any MCP client. You write this server.
# STUB: removed for your route

    MCP_TOKEN=reader uv run python -m app.mcp_server        # stdio transport

The Model Context Protocol is a transport, not a permission system. A client discovers the tools
and their schemas when it connects, calls them by name, and gets text back. Nothing in the
protocol stops a reader from calling issue_credit; your server must. What must hold
(tests/weeks/test_week4.py, the tests with "mcp" or "reader" or "supervisor" in their names):

    every tool        one handler per tool in app.tools.TOOLS, with that tool's real argument
                      schema and description, so a client sees what the model sees
    the token         app/mcp_scopes.py check_scope before anything runs: a reader cannot act,
                      an agent cannot escalate or spend, an unknown token gets nothing
    a rate limit      per token (app/mcp_scopes.py RateLimiter)
    approval          scope says who may ask; approval says yes. Run every call through
                      app.tools.call with the approvals in app.mcp_scopes.approved_tools(), so a
                      supervisor still gets "needs approval: ..." without one
    always text       "denied: ...", "needs approval: ...", "error: ..." or the result; a tool
                      failing must not take the server down

The mcp package is installed. `MCPServer.add_tool(fn, name=..., description=...)` builds a tool's
schema from fn's signature: give it a signature that is the tool's arguments.
"""

from typing import Any

TOKEN = "reader"


async def call_tool(token: str, tool: str, args: dict[str, Any]) -> str:
    """One MCP call, through every check, as text."""
    raise NotImplementedError("call_tool: build me (app/mcp_server.py docstring)")


def build_server() -> Any:
    """An MCP server with one handler per tool in app.tools.TOOLS."""
    raise NotImplementedError("build_server: build me (app/mcp_server.py docstring)")


def main() -> None:
    build_server().run(transport="stdio")


if __name__ == "__main__":
    main()
