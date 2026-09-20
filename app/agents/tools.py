"""The tools a model may call, with schemas it can use reliably, and the rule about money.

A tool is a plain function with a Pydantic argument model. The schema is what the model sees;
the validation is what keeps a malformed call from reaching the function. Tools that spend money
(`costs_money=True`) run only when the caller has approved that spend: the human checkpoint.
"""

import json
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from typing import Any

from pydantic import BaseModel, Field, ValidationError
from sqlmodel import Session, select

from app.db.models import Document
from app.llm.client import ModelClient
from app.retrieval.embed import Embedder
from app.retrieval.store import search
from app.settings import Settings
from app.trace import span


class SearchArgs(BaseModel):
    query: str = Field(min_length=1)
    k: int = Field(default=3, ge=1, le=10)


class GetDocumentArgs(BaseModel):
    document_id: int


class ExtractArgs(BaseModel):
    document_id: int


class FinishArgs(BaseModel):
    answer: str = Field(min_length=1)


class ListDocumentsArgs(BaseModel):
    pass


@dataclass
class ToolContext:
    session: Session
    embedder: Embedder
    settings: Settings
    client: ModelClient
    approved: bool = False
    spent_usd: float = 0.0
    calls: list[str] = field(default_factory=list)


class NeedsApproval(Exception):
    def __init__(self, tool: str) -> None:
        super().__init__(f"{tool} spends money; call again with approved=true")
        self.tool = tool


@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str
    args: type[BaseModel]
    run: Callable[[ToolContext, BaseModel], Awaitable[str]]
    costs_money: bool = False


async def _list_documents(ctx: ToolContext, _: BaseModel) -> str:
    docs = ctx.session.exec(select(Document)).all()
    return "\n".join(f"id={d.id} {d.filename} ({d.char_count} chars)" for d in docs) or "none"


async def _search(ctx: ToolContext, a: BaseModel) -> str:
    assert isinstance(a, SearchArgs)
    hits = search(ctx.session, ctx.embedder, a.query, k=a.k, strategy=ctx.settings.chunk_strategy)
    if not hits:
        return "no results"
    return "\n".join(
        f"document_id={h.document_id} file={h.filename} score={h.score:.2f}: "
        f"{' '.join(h.text.split())[:240]}"
        for h in hits
    )


async def _get_document(ctx: ToolContext, a: BaseModel) -> str:
    assert isinstance(a, GetDocumentArgs)
    doc = ctx.session.get(Document, a.document_id)
    if doc is None:
        return f"error: no document with id {a.document_id}"
    return doc.text[: ctx.settings.max_input_chars]


async def _extract(ctx: ToolContext, a: BaseModel) -> str:
    """Calls the model (Week 1's endpoint logic) so it costs money: gated by approval."""
    assert isinstance(a, ExtractArgs)
    if not ctx.approved and ctx.settings.require_approval_for_cost:
        raise NeedsApproval("extract_document")
    from app.api.extract import extract_document
    from app.api.schemas import ExtractOut

    out = await extract_document(a.document_id, ctx.session, ctx.client, ctx.settings)
    if not isinstance(out, ExtractOut):
        return f"error: extract failed: {out.body!r}"
    ctx.spent_usd += out.cost_usd
    return json.dumps(out.extract.model_dump())


async def _finish(_: ToolContext, a: BaseModel) -> str:
    assert isinstance(a, FinishArgs)
    return a.answer


TOOLS: dict[str, ToolSpec] = {
    "list_documents": ToolSpec(
        "list_documents", "List every document id and filename.", ListDocumentsArgs, _list_documents
    ),
    "search_documents": ToolSpec(
        "search_documents",
        "Semantic search over document chunks. Returns document ids, files and snippets.",
        SearchArgs,
        _search,
    ),
    "get_document": ToolSpec(
        "get_document", "Full text of one document by id.", GetDocumentArgs, _get_document
    ),
    "extract_document": ToolSpec(
        "extract_document",
        "Structured facts (title, doc_type, summary, key_facts) for one document. Costs money.",
        ExtractArgs,
        _extract,
        costs_money=True,
    ),
    "finish": ToolSpec("finish", "Return the final answer to the user.", FinishArgs, _finish),
}


def tool_schemas() -> list[dict[str, Any]]:
    """What the model sees: name, description, JSON schema of the arguments."""
    return [
        {
            "name": t.name,
            "description": t.description + (" [costs money]" if t.costs_money else ""),
            "parameters": t.args.model_json_schema(),
        }
        for t in TOOLS.values()
    ]


async def run_tool(ctx: ToolContext, name: str, args: dict[str, Any]) -> str:
    """Validate, then run. Errors come back as text the model can read and recover from."""
    spec = TOOLS.get(name)
    if spec is None:
        return f"error: unknown tool {name!r}; known: {', '.join(TOOLS)}"
    try:
        parsed = spec.args.model_validate(args)
    except ValidationError as e:
        return f"error: invalid arguments for {name}: {e.errors()[0]['msg']}"
    ctx.calls.append(name)
    async with span(f"tool.{name}"):
        return await spec.run(ctx, parsed)
