"""Expose the document service to any MCP client (Claude Desktop, an IDE, another agent).

    MCP_TOKEN=reader uv run python -m app.mcp_server        # stdio transport

Model Context Protocol is not a REST API: the client discovers tools and their schemas at
connect time, calls them by name, and gets text back. What it is NOT is a permission system.
Every call here passes through check_scope and a rate limiter before it touches anything.
"""

import os
from typing import Any

from sqlmodel import Session

from app.agents.tools import ToolContext, run_tool
from app.db.session import get_engine
from app.llm.registry import get_model_client
from app.mcp_scopes import RateLimiter, ScopeError, check_scope
from app.retrieval.embed import get_embedder
from app.settings import get_settings

TOKEN = os.environ.get("MCP_TOKEN", "reader")
_limiter = RateLimiter(max_calls=int(os.environ.get("MCP_RATE_LIMIT", "30")), window_s=60)


async def _guarded(tool: str, args: dict[str, Any]) -> str:
    try:
        check_scope(TOKEN, tool)
        _limiter.check(TOKEN)
    except ScopeError as e:
        return f"denied: {e}"
    with Session(get_engine()) as session:
        ctx = ToolContext(
            session=session,
            embedder=get_embedder(),
            settings=get_settings(),
            client=get_model_client(),
            approved=os.environ.get("MCP_APPROVED", "false").lower() == "true",
        )
        try:
            return await run_tool(ctx, tool, args)
        except Exception as e:  # a tool failing mid-call must not take the server down
            return f"error: {tool} failed: {e}"


def build_server() -> Any:
    from mcp.server.mcpserver import MCPServer  # mcp 2.x; was mcp.server.fastmcp.FastMCP in 1.x

    mcp = MCPServer("ai-eng-track")

    @mcp.tool()
    async def list_documents() -> str:
        """List every document id and filename."""
        return await _guarded("list_documents", {})

    @mcp.tool()
    async def search_documents(query: str, k: int = 3) -> str:
        """Semantic search over document chunks."""
        return await _guarded("search_documents", {"query": query, "k": k})

    @mcp.tool()
    async def get_document(document_id: int) -> str:
        """Full text of one document."""
        return await _guarded("get_document", {"document_id": document_id})

    @mcp.tool()
    async def extract_document(document_id: int) -> str:
        """Structured facts for one document. Costs money; needs the analyst scope."""
        return await _guarded("extract_document", {"document_id": document_id})

    return mcp


def main() -> None:
    server = build_server()
    server.run(transport="stdio")


if __name__ == "__main__":
    main()
