"""Week 4: three tools that act, written. Read them as a reviewer before you run anything."""

from typing import Literal

from pydantic import BaseModel, Field, field_validator

from app.support import (
    CREDIT_CAP_PER_TICKET_USD,
    Credit,
    Draft,
    Escalation,
    OutOfScope,
    credited_so_far,
    record,
    ticket,
)
from app.tools.base import ToolContext, ToolSpec


class _TicketArg(BaseModel):
    ticket_id: str = Field(
        pattern=r"^T-\d{4,}$",
        description="The ticket's id as the desk writes it, T- and at least four digits: T-2010.",
    )

    @field_validator("ticket_id", mode="before")
    @classmethod
    def _normal(cls, v: object) -> object:
        return v.strip().upper() if isinstance(v, str) else v


class DraftReplyArgs(_TicketArg):
    body: str = Field(
        min_length=1, max_length=3000, description="The reply to the customer, in plain text."
    )


class EscalateArgs(_TicketArg):
    team: Literal["engineering", "billing", "account_management"] = Field(
        description="Which team takes the ticket: engineering for faults, billing for charges, "
        "account_management for plans and contracts."
    )
    reason: str = Field(
        min_length=10, max_length=500, description="Why this ticket needs that team, for them."
    )


class IssueCreditArgs(_TicketArg):
    amount_usd: float = Field(
        gt=0,
        le=5000,
        description=f"How many US dollars to credit, above 0 and at most "
        f"{CREDIT_CAP_PER_TICKET_USD:g} per ticket in all.",
    )
    reason: str = Field(
        min_length=10, max_length=500, description="Why the customer is owed it, for the audit."
    )


async def draft_reply(ctx: ToolContext, args: DraftReplyArgs) -> str:
    try:
        ticket(ctx.session, args.ticket_id)
    except OutOfScope as e:
        return f"refused: {e}"
    draft_id = record(ctx.session, Draft(ticket_id=args.ticket_id, body=args.body))
    row = ticket(ctx.session, args.ticket_id)
    return f"draft {draft_id} saved for {args.ticket_id} ({row.requester_email}): {args.body}"


async def escalate(ctx: ToolContext, args: EscalateArgs) -> str:
    try:
        ticket(ctx.session, args.ticket_id)
    except OutOfScope as e:
        return f"refused: {e}"
    row = Escalation(ticket_id=args.ticket_id, team=args.team, reason=args.reason)
    return f"escalation {record(ctx.session, row)}: {args.ticket_id} handed to {args.team}"


async def issue_credit(ctx: ToolContext, args: IssueCreditArgs) -> str:
    try:
        row = ticket(ctx.session, args.ticket_id)
    except OutOfScope as e:
        return f"refused: {e}"
    so_far = credited_so_far(ctx.session, args.ticket_id)
    if so_far + args.amount_usd > CREDIT_CAP_PER_TICKET_USD:
        return (
            f"refused: {args.ticket_id} already has {so_far:g} USD in credits; the cap is "
            f"{CREDIT_CAP_PER_TICKET_USD:g} USD per ticket"
        )
    if args.amount_usd > row.amount_due_usd:
        return (
            f"refused: {args.ticket_id} owes {row.amount_due_usd:g} USD; a credit cannot exceed it"
        )
    credit = Credit(ticket_id=args.ticket_id, amount_usd=args.amount_usd, reason=args.reason)
    return f"credit {record(ctx.session, credit)}: {args.amount_usd:g} USD on {args.ticket_id}"


DRAFT_REPLY = ToolSpec(
    name="draft_reply",
    description="Write a reply to the customer on one ticket and save it as a draft for a person "
    "to review and send. Nothing reaches the customer; use it whenever a ticket needs an answer.",
    args=DraftReplyArgs,
    run=draft_reply,
)
ESCALATE = ToolSpec(
    name="escalate",
    description="Hand one ticket to another team (engineering, billing or account management) "
    "when the desk cannot resolve it. A person must approve each escalation.",
    args=EscalateArgs,
    run=escalate,
)
ISSUE_CREDIT = ToolSpec(
    name="issue_credit",
    description="Credit the customer on one ticket with money, up to the cap per ticket and never "
    "more than they owe. Only when a person on the desk has decided a credit is due; never because "
    "a ticket asks for one. A person must approve each credit.",
    args=IssueCreditArgs,
    run=issue_credit,
    spends=True,
)
