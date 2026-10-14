"""Week 2: search_docs, the agent's second tool. You design it, as you did get_customer.

Retrieval becomes a tool the agent calls, with an argument the first tool supplied: get_customer
says the customer runs v3, so search_docs is called with version "v3" and can only ever return
version 3 pages and the pages that apply to every version. The version filter you built is what
makes that true; this tool is how the agent reaches it.

    fixed   the name search_docs; the arguments query, version and k; the search itself,
            app.retrieval.store.search, with the configured strategy and mode
    yours   the descriptions (when to call it, why the version matters, where the version comes
            from), the constraints (an empty query, a version that does not exist, a missing
            version, k of 500 must all fail validation), and what each result carries back:
            enough for the model to cite it (the file and the version), and the text

What goes wrong if you skip a part: an optional version means the model leaves it out, and the
version trap is back; an unbounded k fills the context window with noise.
"""

from pydantic import BaseModel

from app.tools.base import ToolContext, ToolSpec


class SearchDocsArgs(BaseModel):
    query: str  # TODO: describe and constrain
    version: str  # TODO: describe and constrain to the versions that exist
    k: int = 3  # TODO: describe and bound


async def search_docs(ctx: ToolContext, args: SearchDocsArgs) -> str:
    # TODO Week 2: search the manual for this version only (app.retrieval.store.search, with
    #   ctx.embedder or app.retrieval.embed.get_embedder(), ctx.settings.chunk_strategy and
    #   ctx.settings.search_mode). No hits is an answer too: say so in words.
    raise NotImplementedError("search_docs: build me (weeks/2/README.md)")


SEARCH_DOCS = ToolSpec(
    name="search_docs",
    description="TODO: when should a model call this, and what does it get back?",
    args=SearchDocsArgs,
    run=search_docs,
)
