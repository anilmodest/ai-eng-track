"""Who may call which tool, how often. The permission boundary for the tools you serve over MCP.

Tokens and their scopes come from MCP_TOKENS, e.g.
    MCP_TOKENS="reader:get_customer,get_ticket;supervisor:get_customer,get_ticket,escalate"

Least agency: a token gets the smallest set of tools its job needs. The defaults:

    reader       looks things up and analyses: nothing it calls changes anything
    agent        a reader that may also draft a reply, which a person still sends
    supervisor   may also escalate and issue credits, and those still need a person's approval
                 for each run (MCP_APPROVED); the scope says who may ask, approval says yes

A scope is not approval, and approval is not a scope. Both are checked, in code, on every call.
"""

import os
import time
from collections import deque
from dataclasses import dataclass, field

READ = "get_customer,get_ticket,search_docs,query_tickets"
DEFAULT_TOKENS = (
    f"reader:{READ};agent:{READ},draft_reply;supervisor:{READ},draft_reply,escalate,issue_credit"
)


class ScopeError(PermissionError):
    pass


def parse_tokens(spec: str) -> dict[str, frozenset[str]]:
    out: dict[str, frozenset[str]] = {}
    for entry in spec.split(";"):
        entry = entry.strip()
        if not entry:
            continue
        name, _, tools = entry.partition(":")
        out[name.strip()] = frozenset(t.strip() for t in tools.split(",") if t.strip())
    return out


def load_tokens() -> dict[str, frozenset[str]]:
    return parse_tokens(os.environ.get("MCP_TOKENS", DEFAULT_TOKENS))


def check_scope(token: str, tool: str, tokens: dict[str, frozenset[str]] | None = None) -> None:
    """Raise ScopeError unless `token` is known and allows `tool`. Never widen silently."""
    known = tokens if tokens is not None else load_tokens()
    allowed = known.get(token)
    if allowed is None:
        raise ScopeError("unknown token")
    if tool not in allowed:
        raise ScopeError(f"token {token!r} may not call {tool}; allowed: {sorted(allowed)}")


def approved_tools() -> set[str]:
    """MCP_APPROVED="escalate": the actions a person has approved for this server's run."""
    return {t.strip() for t in os.environ.get("MCP_APPROVED", "").split(",") if t.strip()}


@dataclass
class RateLimiter:
    """Sliding window: at most `max_calls` per `window_s`, per token."""

    max_calls: int = 30
    window_s: float = 60.0
    _calls: dict[str, deque[float]] = field(default_factory=dict)

    def check(self, token: str, now: float | None = None) -> None:
        t = time.monotonic() if now is None else now
        q = self._calls.setdefault(token, deque())
        while q and t - q[0] > self.window_s:
            q.popleft()
        if len(q) >= self.max_calls:
            raise ScopeError(f"rate limit: {self.max_calls} calls per {self.window_s:.0f}s")
        q.append(t)
