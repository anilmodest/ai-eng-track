"""The support desk's own data: customers and tickets, loaded into the service's database.

Week 0 loads them and nothing reads them yet. From week 1 the agent's tools do (app/tools/), and
every one of those reads through a function in this module, never through a table directly. That
is the scope, written down in one place:

    the account   the desk may read its own customers' records and tickets, no one else's
    the fields    a tool gets what it needs (version, plan, a ticket's text), never seats or
                  contact details: personal data stays here unless a person approves an output

The files are support/customers.json and support/tickets.jsonl. A programme variant replaces them
with its own product's customers and tickets; the shape never changes.
"""

import json
from datetime import datetime
from pathlib import Path

from sqlmodel import Field, Session, SQLModel, select

SUPPORT = Path(__file__).resolve().parent.parent / "support"


class Customer(SQLModel, table=True):
    customer_id: str = Field(primary_key=True)
    account: str = Field(index=True)
    name: str
    version: str
    plan: str
    region: str
    seats: int
    contact: str


class Ticket(SQLModel, table=True):
    ticket_id: str = Field(primary_key=True)
    customer_id: str = Field(index=True)
    opened_at: datetime
    closed_at: datetime | None = None
    status: str = Field(index=True)  # open | pending | closed
    priority: str  # low | normal | high | urgent
    category: str  # configuration | billing | outage | how-to | bug
    product_version: str
    subject: str
    body: str
    requester_name: str
    requester_email: str
    requester_phone: str | None = None
    amount_due_usd: float = 0.0
    credits_issued_usd: float = 0.0
    first_response_min: int | None = None


class OutOfScope(Exception):
    """The call was well formed and still not allowed. Not an error: a boundary doing its job."""


def desk_account() -> str:
    """Whose desk this service belongs to."""
    data = json.loads((SUPPORT / "customers.json").read_text(encoding="utf-8"))
    return str(data["account"])


def _when(value: str | None) -> datetime | None:
    return datetime.fromisoformat(value.replace("Z", "+00:00")) if value else None


def load_support(session: Session) -> tuple[int, int]:
    """Load customers and tickets once; safe on every start. Returns (customers, tickets)."""
    if session.exec(select(Customer)).first() is not None:
        return (len(session.exec(select(Customer)).all()), len(session.exec(select(Ticket)).all()))
    data = json.loads((SUPPORT / "customers.json").read_text(encoding="utf-8"))
    for row in data["customers"]:
        session.add(Customer(**row))
    n = 0
    for line in (SUPPORT / "tickets.jsonl").read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        row["opened_at"] = _when(row["opened_at"])
        row["closed_at"] = _when(row.get("closed_at"))
        session.add(Ticket(**row))
        n += 1
    session.commit()
    return (len(data["customers"]), n)


def customer(session: Session, customer_id: str, *, as_account: str | None = None) -> Customer:
    """One of this desk's customers, or OutOfScope. Callers choose which fields leave."""
    desk = as_account or desk_account()
    row = session.get(Customer, customer_id)
    if row is None:
        raise OutOfScope(f"no customer {customer_id} on this desk")
    if row.account != desk:
        raise OutOfScope(
            f"{customer_id} belongs to another account; this desk may only read {desk}"
        )
    return row


def ticket(session: Session, ticket_id: str, *, as_account: str | None = None) -> Ticket:
    """One ticket belonging to one of this desk's customers, or OutOfScope."""
    row = session.get(Ticket, ticket_id)
    if row is None:
        raise OutOfScope(f"no ticket {ticket_id}")
    customer(session, row.customer_id, as_account=as_account)  # raises if not this desk's
    return row


def desk_tickets(session: Session, *, as_account: str | None = None) -> list[Ticket]:
    """Every ticket of this desk's customers: the only rows an analysis may see."""
    desk = as_account or desk_account()
    mine = {c.customer_id for c in session.exec(select(Customer).where(Customer.account == desk))}
    return [t for t in session.exec(select(Ticket)).all() if t.customer_id in mine]


# ---- What the desk does about a ticket (week 4) -----------------------------------------------
# Three kinds of action, from harmless to costly. Drafting changes nothing a customer sees;
# escalating hands the ticket to another team; a credit is money. The last two are written here
# only after a person approved them: app/tools/base.py run_tool is the door, and it is locked.


def _utcnow() -> datetime:
    from datetime import UTC

    return datetime.now(UTC)


class Draft(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    ticket_id: str = Field(index=True)
    body: str
    created_at: datetime = Field(default_factory=_utcnow)


class Escalation(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    ticket_id: str = Field(index=True)
    team: str
    reason: str
    created_at: datetime = Field(default_factory=_utcnow)


class Credit(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    ticket_id: str = Field(index=True)
    amount_usd: float
    reason: str
    created_at: datetime = Field(default_factory=_utcnow)


CREDIT_CAP_PER_TICKET_USD = 500.0


def credited_so_far(session: Session, ticket_id: str) -> float:
    """Credits on this ticket: those already in the ticket record and those issued here."""
    row = session.get(Ticket, ticket_id)
    issued = sum(
        c.amount_usd for c in session.exec(select(Credit).where(Credit.ticket_id == ticket_id))
    )
    return (row.credits_issued_usd if row else 0.0) + issued


def record(session: Session, row: Draft | Escalation | Credit) -> int:
    if isinstance(row, Draft):
        # A draft is read by a person before it is sent: the one output that gets personal data
        # back, in place of the placeholders the model saw (week 5, app/llm/masking.py).
        from app.llm.masking import restore

        row.body = restore(row.body)
    session.add(row)
    session.commit()
    session.refresh(row)
    assert row.id is not None
    return row.id
