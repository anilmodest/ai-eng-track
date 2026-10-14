"""Week 4: three tools that act. You design them. The door that stops them is already locked.

    draft_reply    writes a reply for a person to send. Changes nothing a customer sees.
    escalate       hands the ticket to another team. Writes: needs a person's approval.
    issue_credit   gives the customer money. Spends: needs approval, and is capped per ticket.

Approval is enforced in code, not in the prompt: app/tools/base.py run_tool raises NeedsApproval
for any tool whose spec says it writes or spends, unless a person approved that tool for this
run, and the agent loop stops there with status "needs_approval". A prompt that says "never issue
a credit without asking" is a request; this is a boundary. What is yours is to say, truthfully,
which of your tools write and which spend: the flag on the spec is the whole of the permission.

    fixed   the names, and the arguments: draft_reply(ticket_id, body),
            escalate(ticket_id, team, reason), issue_credit(ticket_id, amount_usd, reason);
            the records, written through app.support.record
    yours   the descriptions, the constraints (a team that does not exist, a negative or huge
            amount, an empty reason must fail validation), the writes/spends flags, the cap
            (app.support.CREDIT_CAP_PER_TICKET_USD across all credits on a ticket, and never more
            than the ticket's amount due), and refusals in words

Every tool reads its ticket through app.support.ticket, so another desk's ticket is refused.
"""

from pydantic import BaseModel

from app.tools.base import ToolContext, ToolSpec


class DraftReplyArgs(BaseModel):
    ticket_id: str  # TODO: describe and constrain
    body: str  # TODO


class EscalateArgs(BaseModel):
    ticket_id: str  # TODO
    team: str  # TODO: which teams exist? engineering, billing, account_management
    reason: str  # TODO


class IssueCreditArgs(BaseModel):
    ticket_id: str  # TODO
    amount_usd: float  # TODO: bounds
    reason: str  # TODO


async def draft_reply(ctx: ToolContext, args: DraftReplyArgs) -> str:
    raise NotImplementedError("draft_reply: build me (weeks/4/README.md)")


async def escalate(ctx: ToolContext, args: EscalateArgs) -> str:
    raise NotImplementedError("escalate: build me (weeks/4/README.md)")


async def issue_credit(ctx: ToolContext, args: IssueCreditArgs) -> str:
    raise NotImplementedError("issue_credit: build me (weeks/4/README.md)")


DRAFT_REPLY = ToolSpec(
    name="draft_reply",
    description="TODO",
    args=DraftReplyArgs,
    run=draft_reply,
)
ESCALATE = ToolSpec(
    name="escalate",
    description="TODO",
    args=EscalateArgs,
    run=escalate,
    # TODO: does this tool write? spend?
)
ISSUE_CREDIT = ToolSpec(
    name="issue_credit",
    description="TODO",
    args=IssueCreditArgs,
    run=issue_credit,
    # TODO: does this tool write? spend?
)
