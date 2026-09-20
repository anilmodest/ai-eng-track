"""Way 2: a workflow. Fixed steps decided by the programmer; the model fills in the parts that
need reading. Predictable cost (N documents = N+1 calls), predictable shape, no loop to go wrong.

Steps: find the invoices -> extract facts from each -> one model call to answer from the facts.
"""

import json
from pathlib import Path

from pydantic import BaseModel

from app.agents.tools import NeedsApproval, ToolContext, run_tool
from app.llm.client import Message
from app.llm.structured import complete_structured

_ANSWER_PROMPT = (Path(__file__).parent.parent / "llm" / "prompts" / "ask_v1.md").read_text()


class WorkflowResult(BaseModel):
    answer: str
    status: str  # done | needs_approval
    steps: int
    calls: list[str]


class _Facts(BaseModel):
    answer: str
    citations: list[int]
    grounded: bool


async def run_workflow(ctx: ToolContext, question: str) -> WorkflowResult:
    calls: list[str] = []
    # Step 1: the programmer decided the relevant documents are the invoices.
    listing = await run_tool(ctx, "list_documents", {})
    calls.append("list_documents")
    ids = [
        int(line.split()[0].removeprefix("id="))
        for line in listing.splitlines()
        if "invoice" in line.lower()
    ]
    # Step 2: structured extraction per invoice (paid, gated).
    facts: list[str] = []
    for doc_id in ids:
        try:
            result = await run_tool(ctx, "extract_document", {"document_id": doc_id})
        except NeedsApproval:
            return WorkflowResult(
                answer="", status="needs_approval", steps=len(calls) + 1, calls=calls
            )
        calls.append("extract_document")
        facts.append(f"[{len(facts) + 1}] document_id={doc_id}: {result}")
    if not facts:
        return WorkflowResult(answer="no invoices found", status="done", steps=1, calls=calls)
    # Step 3: one call to answer from the facts, using the grounded-answer prompt.
    messages = [
        Message(role="system", content=_ANSWER_PROMPT),
        Message(
            role="user",
            content="Passages:\n\n" + "\n\n".join(facts) + f"\n\nQuestion: {question}",
        ),
    ]
    parsed, _ = await complete_structured(
        ctx.client,
        messages,
        _Facts,
        attempts=ctx.settings.model_retry_attempts,
        base_delay_s=ctx.settings.model_retry_base_delay_s,
        timeout_s=ctx.settings.model_timeout_s,
    )
    calls.append("answer")
    answer = parsed.answer if parsed.grounded else "the invoices do not answer that"
    return WorkflowResult(answer=answer, status="done", steps=len(calls), calls=calls)


def describe() -> str:
    return json.dumps(["list_documents", "extract_document x N (approval)", "answer"])
