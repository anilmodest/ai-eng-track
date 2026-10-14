"""Week 1: the agent's first two tools, get_customer and get_ticket. You design both.

The exercise is in weeks/1/README.md, "Build". What is fixed and what is yours:

    fixed   the names (get_customer, get_ticket) and the one argument each takes
            (customer_id, ticket_id), because later weeks and the programme call them by name;
            the data, read only through app/support.py, which is the desk's scope.
    yours   the description of each tool and of its argument (what the model reads to decide
            whether and how to call it), the constraints that make a malformed call fail
            validation before the tool runs, which fields each tool returns, and the words of
            every refusal and error, which a model must be able to read and act on.

What goes wrong if you skip a part, so you know what each part is for:

    a vague description   the model calls the wrong tool, or makes up a tool that does not
                          exist; scripts/tool_drill.py measures exactly this
    no constraints        "1001", "c1001" or "" reaches the database; a malformed call should
                          never get past ToolSpec.args
    returning the record  seats and contact details reach the model, and from week 5 the model
                          provider; return what the desk needs and nothing else
    raising on refusal    the model gets no answer and cannot recover; return "refused: <why>"
                          as text, and keep OutOfScope as the boundary inside app/support.py

Run the gate with `make check WEEK=1`; the tool tests are the ones whose names start with `tool`,
`get_customer` or `get_ticket`. Then `make evidence WEEK=1` runs the tool drill on a real model.
"""

from pydantic import BaseModel

from app.tools.base import ToolContext, ToolSpec


class GetCustomerArgs(BaseModel):
    customer_id: str  # TODO: describe it, and constrain it so a malformed id fails validation


class GetTicketArgs(BaseModel):
    ticket_id: str  # TODO: describe it, and constrain it


async def get_customer(ctx: ToolContext, args: GetCustomerArgs) -> str:
    # TODO Week 1: one of this desk's customers -> which version, which account, which plan.
    #   Read through app.support.customer(ctx.session, ...). Another desk's customer, or one that
    #   does not exist, is a refusal the model can read, not an exception.
    raise NotImplementedError("get_customer: build me (weeks/1/README.md)")


async def get_ticket(ctx: ToolContext, args: GetTicketArgs) -> str:
    # TODO Week 1: one of this desk's tickets -> what an agent needs to work on it.
    #   Read through app.support.ticket(ctx.session, ...). Same rule on refusals.
    raise NotImplementedError("get_ticket: build me (weeks/1/README.md)")


GET_CUSTOMER = ToolSpec(
    name="get_customer",
    description="TODO: when should a model call this, and what does it get back?",
    args=GetCustomerArgs,
    run=get_customer,
)

GET_TICKET = ToolSpec(
    name="get_ticket",
    description="TODO: when should a model call this, and what does it get back?",
    args=GetTicketArgs,
    run=get_ticket,
)
