"""Week 1: the agent's first two tools, get_customer and get_ticket.

Both are written. Read them as a reviewer before you run anything: do they do what
weeks/1/README.md asks, and only that?
"""

from pydantic import BaseModel, Field

from app.support import Ticket, customer
from app.tools.base import ToolContext, ToolSpec, as_json


class GetCustomerArgs(BaseModel):
    customer_id: str = Field(
        pattern=r"^C-\d+",
        description="The customer's id, as the desk writes it, e.g. C-1004.",
    )


class GetTicketArgs(BaseModel):
    ticket_id: str = Field(
        pattern=r"^T-\d{4,}$",
        description="The ticket's id, as the desk writes it, e.g. T-2010.",
    )


async def get_customer(ctx: ToolContext, args: GetCustomerArgs) -> str:
    try:
        row = customer(ctx.session, args.customer_id)
    except Exception as e:
        return f"refused: {e}"
    return as_json(
        {
            "customer_id": row.customer_id,
            "version": row.version,
            "account": row.account,
            "plan": row.plan,
            "seats": row.seats,
        }
    )


async def get_ticket(ctx: ToolContext, args: GetTicketArgs) -> str:
    row = ctx.session.get(Ticket, args.ticket_id)
    if row is None:
        return f"refused: no ticket {args.ticket_id}"
    return as_json(
        {
            "ticket_id": row.ticket_id,
            "customer_id": row.customer_id,
            "status": row.status,
            "priority": row.priority,
            "category": row.category,
            "product_version": row.product_version,
            "opened_at": row.opened_at.isoformat(),
            "subject": row.subject,
            "body": row.body,
            "requester": f"{row.requester_name} <{row.requester_email}>",
        }
    )


GET_CUSTOMER = ToolSpec(
    name="get_customer",
    description="Look up one of this desk's customers by customer id and get back which product "
    "version (v2 or v3) and plan they are on and which account they belong to.",
    args=GetCustomerArgs,
    run=get_customer,
)

GET_TICKET = ToolSpec(
    name="get_ticket",
    description="Fetch one support ticket by ticket id: its status, priority, category, the "
    "product version it is about, when it was opened, its subject and what the customer wrote.",
    args=GetTicketArgs,
    run=get_ticket,
)
