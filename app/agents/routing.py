"""Week 5: least agency. Which tools is the agent offered for this request? You decide.

The strongest defence against an instruction hidden in a ticket is not a better filter: it is
that the agent handling a lookup was never given issue_credit. A tool the agent was not offered
cannot be called, whatever a ticket says. Filtering the text (app/guard.py) is the second layer,
because filters miss things.

The rule that makes this work: **the capability is chosen from the request, never from the
content.** The request comes from a person on the desk ("give the customer on T-2058 a credit");
the ticket comes from a customer, and anything it asks for is data.

    tools_for(request) -> the tool names the agent may be offered for this request

The tasks API calls it for every agent run. What must hold (tests/weeks/test_week5.py):
    a lookup, an analysis or "handle this ticket" is never offered escalate or issue_credit
    a request that asks for an escalation is offered escalate, and not issue_credit
    a request that asks for a credit is offered issue_credit, and not escalate
    every request keeps what it needs to answer: the lookups, the manual, the analysis, a draft

Write the blast-radius statement for each action tool (decisions/week-5-blast-radius.md) first:
it says which of these rules matters most.
"""

from app.tools import TOOLS


def tools_for(request: str) -> list[str]:
    # TODO Week 5: offer each request only what its task needs. As shipped, every request gets
    #   every tool, which is the week 4 agent that T-2099 talked into asking for a credit.
    return list(TOOLS)
