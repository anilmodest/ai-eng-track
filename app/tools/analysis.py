"""Week 4: query_tickets, the analysis tool. Read-only, from an allowlist. You design it.

A model that can write SQL can drop a table, read another desk's tickets or invent a column. The
safe way to let a model analyse data is to give it a short list of questions it may ask, each
with parameters, and to run them yourself over exactly the rows it may see: this desk's tickets,
through app.support.desk_tickets. Nothing here writes.

And the number. A model that receives "9" and writes "about a dozen" has turned a fact into an
invention. The agent loop checks that every number in the final answer came from a tool
(app/agents/checks.py); this tool's job is to return numbers that are unambiguous: the query, the
filters that were applied, and the result.

    fixed   the name; the arguments: query, and optionally group_by, status, priority, category,
            product_version, customer_id, month ("YYYY-MM", by opened_at)
    yours   which queries are allowed and what each computes, the constraints (a query or a
            group_by that is not on the list, a month that is not a month, must fail validation),
            the description that tells a model which query answers which question, and a result
            a model cannot misread

The queries the programme's hidden tasks ask, so your allowlist must have them:
    count                    tickets matching the filters
    count_by                 the same, grouped by group_by (status, priority, category,
                             product_version or month)
    sum_amount_due           total amount_due_usd of the matching tickets
    sum_credits_issued       total credits_issued_usd
    median_first_response    median first_response_min, over tickets that have one
"""

from pydantic import BaseModel

from app.tools.base import ToolContext, ToolSpec


class QueryTicketsArgs(BaseModel):
    query: str  # TODO: only the allowed queries
    group_by: str | None = None  # TODO
    status: str | None = None  # TODO: and the other filters
    priority: str | None = None
    category: str | None = None
    product_version: str | None = None
    customer_id: str | None = None
    month: str | None = None


async def query_tickets(ctx: ToolContext, args: QueryTicketsArgs) -> str:
    raise NotImplementedError("query_tickets: build me (weeks/4/README.md)")


QUERY_TICKETS = ToolSpec(
    name="query_tickets",
    description="TODO",
    args=QueryTicketsArgs,
    run=query_tickets,
)
