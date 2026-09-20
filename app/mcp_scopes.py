"""Who may call which tool, how often. The permission boundary for an exposed internal system.

Tokens and their scopes come from MCP_TOKENS, e.g.
    MCP_TOKENS="reader:search_documents,get_document;analyst:search_documents,get_document,extract_document"

Least agency: a token gets the minimum set of tools its job needs. A reader cannot spend money.
"""

import os
import time
from collections import deque
from dataclasses import dataclass, field

DEFAULT_TOKENS = (
    "reader:list_documents,search_documents,get_document;"
    "analyst:list_documents,search_documents,get_document,extract_document"
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
