"""Way 1: plain code. No model. Exact, instant, free, and it answers only what it was written for.

A handful of rules over the desk's own data: which version or plan a customer is on, where a
ticket stands, and how many tickets match a status or a priority. Anything else returns None:
someone would have to write more code. That trade is the point of comparing it with the other
two ways, task type by task type.
"""

import re

from sqlmodel import Session

from app.support import OutOfScope, customer, desk_tickets, ticket

_CUSTOMER = re.compile(r"\bC-\d{4}\b", re.I)
_TICKET = re.compile(r"\bT-\d{4,}\b", re.I)
_STATUS = ("open", "pending", "closed")
_PRIORITY = ("urgent", "high", "normal", "low")


def answer(session: Session, question: str) -> str | None:
    """The answer, or None when this is not a question the rules know."""
    q = question.lower()
    c = _CUSTOMER.search(question)
    t = _TICKET.search(question)
    try:
        if c and "version" in q:
            row = customer(session, c.group(0).upper())
            return f"{row.customer_id} runs {row.version}"
        if c and "plan" in q:
            row = customer(session, c.group(0).upper())
            return f"{row.customer_id} is on the {row.plan} plan"
        if t and ("status" in q or "still open" in q):
            tk = ticket(session, t.group(0).upper())
            return f"{tk.ticket_id} is {tk.status}"
    except OutOfScope as e:
        return f"refused: {e}"
    if re.search(r"\bhow many\b", q) and "ticket" in q and not re.search(r"\bby\b|\bper\b", q):
        rows = desk_tickets(session)
        for s in _STATUS:
            if re.search(rf"\b{s}\b", q):
                rows = [r for r in rows if r.status == s]
        for p in _PRIORITY:
            if re.search(rf"\b{p}\b", q):
                rows = [r for r in rows if r.priority == p]
        return f"{len(rows)} tickets"
    return None
