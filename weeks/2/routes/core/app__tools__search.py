"""Week 2: search_docs, the agent's second tool.

It is written. Read it as a reviewer before you run anything: does it do what weeks/2/README.md
asks, and only that?
"""

from pydantic import BaseModel, Field

from app.retrieval.embed import get_embedder
from app.retrieval.store import search
from app.tools.base import ToolContext, ToolSpec


class SearchDocsArgs(BaseModel):
    query: str = Field(
        min_length=1, description="What to look for in the product manual, in plain words."
    )
    version: str | None = Field(
        default=None,
        description="The product version the customer runs, as get_customer returned it.",
    )
    k: int = Field(default=3, ge=1, le=100, description="How many passages to return.")


async def search_docs(ctx: ToolContext, args: SearchDocsArgs) -> str:
    hits = search(
        ctx.session,
        ctx.embedder or get_embedder(),
        args.query,
        k=args.k,
        strategy=ctx.settings.chunk_strategy,
        version=args.version,
        mode=ctx.settings.search_mode,
    )
    if not hits:
        return "error: no results"
    return "\n\n".join(f"[{i}] {h.text}" for i, h in enumerate(hits, start=1))


SEARCH_DOCS = ToolSpec(
    name="search_docs",
    description="Search the product manual and get back the most relevant passages for a "
    "question. Pass the version from get_customer when you have it.",
    args=SearchDocsArgs,
    run=search_docs,
)
