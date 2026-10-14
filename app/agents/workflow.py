"""Way 2: a workflow. The programmer decides the steps; the model does one job inside a step.

Predictable shape, predictable cost, no loop to go wrong. The steps, by the kind of request:

    lookup     the customer and/or the ticket the request names -> the manual for that version if
               it asks about the product -> one model call to answer from what was found
    analysis   one model call to choose query_tickets' arguments (structured) -> the query ->
               the number, stated by code, not by the model
    action     the ticket -> one model call to write the reply -> draft_reply; and escalate or
               issue_credit if the request asks for one, which stops for approval

What it cannot do is change its mind: if the first step returns something the programmer did not
expect, the workflow carries on regardless. That is what an agent buys, at a price.
"""

import json
import re
from typing import Any

from pydantic import BaseModel

from app.guard import record_in
from app.llm.client import Message
from app.llm.structured import complete_structured
from app.tools import NeedsApproval, ToolContext, call
from app.tools.analysis import QueryTicketsArgs

_CUSTOMER = re.compile(r"\bC-\d{4}\b", re.I)
_TICKET = re.compile(r"\bT-\d{4,}\b", re.I)
_ANSWER = (
    "TASK: ask\nAnswer the question using ONLY the numbered passages. If they do not contain the "
    'answer, set grounded to false. Return ONLY JSON: {"answer": string, "citations": [int], '
    '"grounded": bool}'
)
_QUERY = (
    "TASK: tool_call\nChoose the arguments for query_tickets that answer the request. Reply with "
    'JSON only: {"tool": "query_tickets", "args": {...}}\nTools:\n'
)
_DRAFT = (
    "TASK: ask\nWrite a short, polite reply to the customer from the numbered passages. Return "
    'ONLY JSON: {"answer": string, "citations": [int], "grounded": bool}'
)


class WorkflowResult(BaseModel):
    answer: str
    status: str  # done | needs_approval | unsupported
    calls: list[str]
    pending: dict[str, Any] | None = None


class _Answer(BaseModel):
    answer: str
    citations: list[int]
    grounded: bool


class _Call(BaseModel):
    tool: str
    args: dict[str, Any]


def kind(request: str) -> str:
    q = request.lower()
    if re.search(r"\b(escalate|credit|refund|draft|reply|respond|handle)\b", q):
        return "action"
    if re.search(r"\bhow many\b|\btotal\b|\bmedian\b|\bnumber of\b", q):
        return "analysis"
    return "lookup"


async def _model(ctx: ToolContext, system: str, user: str, schema: type[BaseModel]) -> Any:
    assert ctx.client is not None
    out, responses = await complete_structured(
        ctx.client,
        [Message(role="system", content=system), Message(role="user", content=user)],
        schema,
        attempts=ctx.settings.model_retry_attempts,
        base_delay_s=ctx.settings.model_retry_base_delay_s,
        timeout_s=ctx.settings.model_timeout_s,
    )
    from app.llm.cost import estimate_cost_usd

    t_in = sum(r.tokens_in for r in responses)
    t_out = sum(r.tokens_out for r in responses)
    ctx.spent_usd += estimate_cost_usd(responses[-1].model, t_in, t_out)
    return out


async def run_workflow(ctx: ToolContext, request: str) -> WorkflowResult:
    found: list[str] = []
    c = _CUSTOMER.search(request)
    t = _TICKET.search(request)
    version = None
    if c:
        result = await call(ctx, "get_customer", {"customer_id": c.group(0).upper()})
        found.append(result)
        version = str(record_in(result).get("version") or "") or None
    if t:
        result = await call(ctx, "get_ticket", {"ticket_id": t.group(0).upper()})
        found.append(result)
        version = version or str(record_in(result).get("product_version") or "") or None

    k = kind(request)
    if k == "analysis":
        schema = json.dumps(
            [{"name": "query_tickets", "parameters": QueryTicketsArgs.model_json_schema()}]
        )
        chosen = await _model(ctx, _QUERY + schema, f"Request: {request}", _Call)
        result = await call(ctx, "query_tickets", chosen.args)
        data = record_in(result)
        if "result" not in data:
            return WorkflowResult(answer=result, status="done", calls=list(ctx.calls))
        return WorkflowResult(
            answer=f"{data['result']} (from query_tickets)", status="done", calls=list(ctx.calls)
        )

    if k == "lookup" and version and not re.search(r"\bstatus\b|\bplan\b", request, re.I):
        found.append(
            await call(ctx, "search_docs", {"query": request[:200], "version": version, "k": 3})
        )
    if not found:
        return WorkflowResult(
            answer="the workflow has no step for that", status="unsupported", calls=list(ctx.calls)
        )

    passages = "\n\n".join(f"[{i}] {p}" for i, p in enumerate(found, start=1))
    if k == "lookup":
        out = await _model(ctx, _ANSWER, f"Passages:\n\n{passages}\n\nQuestion: {request}", _Answer)
        answer = out.answer if out.grounded else "the tools do not answer that"
        return WorkflowResult(answer=answer, status="done", calls=list(ctx.calls))

    if not t:
        return WorkflowResult(
            answer="an action needs a ticket", status="unsupported", calls=list(ctx.calls)
        )
    ticket_id = t.group(0).upper()
    draft = await _model(ctx, _DRAFT, f"Passages:\n\n{passages}\n\nQuestion: {request}", _Answer)
    await call(ctx, "draft_reply", {"ticket_id": ticket_id, "body": draft.answer or "Thank you."})
    q = request.lower()
    try:
        if "escalate" in q:
            await call(
                ctx,
                "escalate",
                {"ticket_id": ticket_id, "team": "engineering", "reason": request[:200]},
            )
        elif re.search(r"\b(issue|give|grant)\b.*\b(credit|refund)\b", q):
            await call(
                ctx,
                "issue_credit",
                {"ticket_id": ticket_id, "amount_usd": 100.0, "reason": request[:200]},
            )
    except NeedsApproval as e:
        return WorkflowResult(
            answer=str(e),
            status="needs_approval",
            calls=list(ctx.calls),
            pending={"tool": e.tool, "args": e.arguments},
        )
    return WorkflowResult(
        answer=f"drafted a reply to {ticket_id}", status="done", calls=list(ctx.calls)
    )
