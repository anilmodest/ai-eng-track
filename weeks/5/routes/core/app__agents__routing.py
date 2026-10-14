"""Week 5: least agency, written. Review it: what does each request get offered?"""

import re

READ = ["get_customer", "get_ticket", "search_docs", "query_tickets", "draft_reply"]


def tools_for(request: str) -> list[str]:
    q = request.lower()
    offered = list(READ)
    if re.search(r"\bescalat", q):
        offered.append("escalate")
    if re.search(r"\b(credit|refund)\b", q):
        offered.append("issue_credit")
    return offered
