"""Week 4 worked example (start route): one tool call, then finish. The loop body without the loop.

    uv run python weeks/4/routes/worked_example.py

Everything run_agent needs is here once: the prompt with the tool schemas, a ToolCall from the
model, run_tool, the result appended to the transcript. Your job is the loop and its walls.
"""

import asyncio
import json
import os
from pathlib import Path

from pydantic import BaseModel, Field

from app.agents.tools import ToolContext, run_tool, tool_schemas
from app.llm.client import Message
from app.llm.providers.fake import FakeClient
from app.llm.structured import complete_structured

SAMPLE = str(Path(__file__).resolve().parents[3] / "samples/invoice.md")
PROMPT = (Path(__file__).resolve().parents[3] / "app/llm/prompts/agent_v1.md").read_text(
    encoding="utf-8"
)


class ToolCall(BaseModel):
    tool: str = Field(min_length=1)
    args: dict[str, object] = Field(default_factory=dict)


async def run_once(ctx: ToolContext, question: str) -> str:
    system = f"{PROMPT}\n\nTools:\n{json.dumps(tool_schemas(), indent=1)}"
    transcript = [
        Message(role="system", content=system),
        Message(role="user", content=f"Question: {question}"),
    ]

    call, _ = await complete_structured(
        ctx.client, transcript, ToolCall, attempts=1, base_delay_s=0, timeout_s=10
    )
    print(f"model chose: {call.tool}({call.args})")
    result = await run_tool(ctx, call.tool, call.args)  # errors come back as text, never raise
    print(f"tool said: {result[:120]!r}")
    transcript.append(Message(role="assistant", content=call.model_dump_json()))
    transcript.append(Message(role="user", content=f"Result of {call.tool}: {result[:4000]}"))
    # A loop would go back to complete_structured here, until finish, a wall, or a checkpoint.
    return result


def _read(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


async def main() -> None:
    os.environ["DATABASE_URL"] = "sqlite:///./data/worked-w4.db"
    os.environ.setdefault("MODEL_PROVIDER", "fake_a")
    from sqlmodel import Session

    from app.db.models import Document
    from app.db.session import get_engine
    from app.retrieval.embed import get_embedder
    from app.retrieval.store import index_documents
    from app.settings import get_settings

    with Session(get_engine()) as session:
        if not session.get(Document, 1):
            sample = SAMPLE
            text = await asyncio.to_thread(_read, sample)
            session.add(
                Document(
                    filename="invoice.md",
                    content_type="text/markdown",
                    text=text,
                    char_count=len(text),
                )
            )
            session.commit()
            index_documents(session, get_embedder(), get_settings().chunk_strategy)
        ctx = ToolContext(
            session=session, embedder=get_embedder(), settings=get_settings(), client=FakeClient()
        )
        await run_once(ctx, "When is the Woodgrove invoice due?")
    print("Now: the loop, AGENT_MAX_STEPS, NeedsApproval, finish, and the cost roll-up.")


if __name__ == "__main__":
    asyncio.run(main())
