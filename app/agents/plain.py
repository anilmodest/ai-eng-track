"""Way 1: plain code. No model. Exact, instant, free, and it answers only the questions it was
written for. Add a new kind of question and someone has to write more code.

That trade-off is the whole point of comparing it with the other two.
"""

import re
from dataclasses import dataclass

from sqlmodel import Session, select

from app.db.models import Document

_TOTAL = re.compile(r"\*\*Total due:\*\*\s*([\d,]+\.\d{2})\s*([A-Z]{3})")
_FROM = re.compile(r"\*\*From:\*\*\s*([^,\n]+)")
_TO = re.compile(r"\*\*To:\*\*\s*([^,\n]+)")
_DUE = re.compile(r"\*\*Due:\*\*\s*([^\n(]+)")
_NUMBER = re.compile(r"^#\s*INVOICE\s+(\S+)", re.M)


@dataclass(frozen=True)
class Invoice:
    number: str
    supplier: str
    customer: str
    total: float
    currency: str
    due: str
    document_id: int


def invoices(session: Session) -> list[Invoice]:
    out: list[Invoice] = []
    for d in session.exec(select(Document)).all():
        if not d.text.lstrip().startswith("# INVOICE"):
            continue
        total = _TOTAL.search(d.text)
        num = _NUMBER.search(d.text)
        if not total or not num or d.id is None:
            continue
        frm = _FROM.search(d.text)
        to = _TO.search(d.text)
        due = _DUE.search(d.text)
        out.append(
            Invoice(
                number=num.group(1),
                supplier=frm.group(1).strip() if frm else "?",
                customer=to.group(1).strip() if to else "?",
                total=float(total.group(1).replace(",", "")),
                currency=total.group(2),
                due=due.group(1).strip() if due else "?",
                document_id=d.id,
            )
        )
    return out


def answer(session: Session, question: str) -> str | None:
    """Keyword-routed. Returns None when the question is not one this code knows."""
    q = question.lower()
    inv = invoices(session)
    if not inv:
        return None
    if "how many invoices" in q:
        who = _who(q, inv, "customer")
        n = sum(1 for i in inv if who is None or who in i.customer.lower())
        return f"{n} invoice(s)" + (f" addressed to {who.title()}" if who else "")
    if "largest" in q or "biggest" in q or "highest" in q:
        top = max(inv, key=lambda i: i.total)
        return f"{top.number}: {top.total:,.2f} {top.currency} (from {top.supplier})"
    if "total" in q and "gbp" in q:
        gbp = sum(i.total for i in inv if i.currency == "GBP")
        return f"{gbp:,.2f} GBP across {sum(1 for i in inv if i.currency == 'GBP')} invoice(s)"
    if "due date" in q or "when is" in q:
        who = _who(q, inv, "supplier")
        for i in inv:
            if who and who in i.supplier.lower():
                return f"{i.number} is due {i.due}"
        return None
    if "total" in q or "how much" in q:
        who = _who(q, inv, "supplier")
        if who:
            picked = [i for i in inv if who in i.supplier.lower()]
            if picked:
                by_cur: dict[str, float] = {}
                for i in picked:
                    by_cur[i.currency] = by_cur.get(i.currency, 0.0) + i.total
                return (
                    "; ".join(f"{v:,.2f} {c}" for c, v in by_cur.items()) + f" from {who.title()}"
                )
    return None


def _who(q: str, inv: list[Invoice], field: str) -> str | None:
    for i in inv:
        name = str(getattr(i, field)).lower()
        first = name.split()[0]
        if first in q:
            return first
    return None
