"""Week 4: query_tickets, written. Read it as a reviewer: does it count what it says?"""

import statistics
from collections import Counter
from typing import Literal

from pydantic import BaseModel, Field, model_validator
from sqlmodel import select

from app.support import Ticket
from app.tools.base import ToolContext, ToolSpec, as_json

Query = Literal[
    "count", "count_by", "sum_amount_due", "sum_credits_issued", "median_first_response"
]
GroupBy = Literal["status", "priority", "category", "product_version", "month"]


class QueryTicketsArgs(BaseModel):
    query: Query = Field(
        description="count: how many tickets; count_by: how many per value of group_by; "
        "sum_amount_due and sum_credits_issued: totals in USD; median_first_response: minutes."
    )
    group_by: GroupBy | None = Field(
        default=None, description="For count_by only: which field to group the count by."
    )
    status: Literal["open", "pending", "closed"] | None = Field(
        default=None, description="Only tickets with this status."
    )
    priority: Literal["low", "normal", "high", "urgent"] | None = Field(
        default=None, description="Only tickets with this priority."
    )
    category: Literal["configuration", "billing", "outage", "how-to", "bug"] | None = Field(
        default=None, description="Only tickets in this category."
    )
    product_version: Literal["v2", "v3"] | None = Field(
        default=None, description="Only tickets about this product version."
    )
    customer_id: str | None = Field(
        default=None, pattern=r"^C-\d{4}$", description="Only this customer's tickets: C-1004."
    )
    month: str | None = Field(
        default=None,
        pattern=r"^20\d\d-(0[1-9]|1[0-2])$",
        description="Only tickets opened in this month, written YYYY-MM.",
    )

    @model_validator(mode="after")
    def _group(self) -> "QueryTicketsArgs":
        if (self.query == "count_by") != (self.group_by is not None):
            raise ValueError("group_by goes with count_by, and only with count_by")
        return self


async def query_tickets(ctx: ToolContext, args: QueryTicketsArgs) -> str:
    rows = list(ctx.session.exec(select(Ticket)))
    filters = args.model_dump(exclude={"query", "group_by"}, exclude_none=True)
    for key, value in filters.items():
        if key == "month":
            rows = [r for r in rows if r.opened_at.strftime("%Y-%m") == value]
        else:
            rows = [r for r in rows if getattr(r, key) == value]
    result: object
    if args.query == "count":
        result = len(rows)
    elif args.query == "count_by":
        key = str(args.group_by)
        counts = Counter(
            r.opened_at.strftime("%Y-%m") if key == "month" else getattr(r, key) for r in rows
        )
        result = dict(sorted(counts.items()))
    elif args.query == "sum_amount_due":
        result = round(sum(r.amount_due_usd for r in rows), 2)
    elif args.query == "sum_credits_issued":
        result = round(sum(r.amount_due_usd for r in rows), 2)
    else:
        times = [r.first_response_min for r in rows if r.first_response_min is not None]
        result = statistics.median(times) if times else None
    return as_json(
        {
            "query": args.query,
            "group_by": args.group_by,
            "filters": filters,
            "tickets": len(rows),
            "result": result,
        }
    )


QUERY_TICKETS = ToolSpec(
    name="query_tickets",
    description="Answer a question about this desk's tickets with an exact number: how many "
    "tickets match some filters, how many per status, priority, category, version or month, the "
    "total amount due or credited, or the median first response. Read-only. Quote the result "
    "exactly as returned.",
    args=QueryTicketsArgs,
    run=query_tickets,
)
