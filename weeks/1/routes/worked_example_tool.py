"""Week 1 worked example (start route): one tool, designed in full, for something smaller.

    uv run python weeks/1/routes/worked_example_tool.py

The tool tells a model about one stored document: its filename, its version and its size, never
its text. It shows every part your two tools need, on a different job:

    a description that says when to call it and what comes back
    an argument with a description and a constraint, so a malformed call fails validation
    a result with only the fields the caller needs
    a refusal the model can read, instead of an exception

Then it makes five calls through the same door your tools use (app/tools/base.py run_tool) and
prints what a model would get back from each. Build get_customer and get_ticket the same way.
"""

import asyncio

from pydantic import BaseModel, Field
from sqlmodel import Session

from app.db.models import Document
from app.db.session import get_engine
from app.settings import get_settings
from app.tools.base import ToolContext, ToolSpec, as_json, run_tool


class DocumentInfoArgs(BaseModel):
    document_id: int = Field(
        ge=1, description="The numeric id of a stored document, as returned by GET /documents."
    )


async def document_info(ctx: ToolContext, args: DocumentInfoArgs) -> str:
    doc = ctx.session.get(Document, args.document_id)
    if doc is None:
        # A refusal, in words: the model can tell the user, or try GET /documents for real ids.
        return f"refused: there is no document {args.document_id}; list the documents first"
    return as_json(
        {
            "document_id": doc.id,
            "filename": doc.filename,
            "version": doc.version,
            "characters": doc.char_count,
        }
    )


DOCUMENT_INFO = ToolSpec(
    name="document_info",
    description="Describe one stored document by its numeric id: its filename, which product "
    "version it documents (v2, v3 or none) and its length. It does not return the text.",
    args=DocumentInfoArgs,
    run=document_info,
)


async def main() -> None:
    tools = {DOCUMENT_INFO.name: DOCUMENT_INFO}
    with Session(get_engine()) as session:
        session.add(
            Document(
                filename="manual-v3-retries.md",
                version="v3",
                content_type="text/markdown",
                text="...",
                char_count=1840,
            )
        )
        session.commit()
        ctx = ToolContext(session=session, settings=get_settings())
        for args in (
            {"document_id": 1},
            {"document_id": 999},
            {"document_id": 0},
            {"document_id": "first"},
            {},
        ):
            answer = await run_tool(tools, ctx, "document_info", args)
            print(f"document_info({args})\n    -> {answer}")
        ran = len(ctx.calls)
        print(f"\nthe tool ran {ran} times out of 5 calls: the rest never got past validation")


if __name__ == "__main__":
    import os

    os.environ.setdefault("DATABASE_URL", "sqlite:///./data/worked-example.db")
    asyncio.run(main())
