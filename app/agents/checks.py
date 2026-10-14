"""The number in the answer must be a number a tool returned. Given; the agent loop calls it.

A model that is handed "count": 9 can still write "about a dozen", or "11". Asking it nicely not
to is a prompt; this is a check. Before an answer is accepted, every number in it is looked for
in what the tools returned during the run. Ids (C-1004, T-2010), dates and version names are not
quantities and are skipped. A number nothing returned sends the answer back to the model, which
gets one sentence saying which number and why.
"""

import re

# Things that look like numbers and are not quantities: ids, versions, dates, error codes.
_NOT_QUANTITIES = re.compile(
    r"\b[A-Z]{1,3}-?\d+\b|\bv\d+\b|\b\d{4}-\d{2}(?:-\d{2})?\b|\b[Ee]\d{3,}\b", re.I
)
_NUMBER = re.compile(r"(?<![\w.])\d[\d,]*(?:\.\d+)?(?![\w.]*\d)")


def _canonical(token: str) -> str:
    """`1,200.50` -> `1200.5`, `30.0` -> `30`, `10` stays `10`."""
    token = token.replace(",", "")
    if "." in token:
        token = token.rstrip("0").rstrip(".")
    return token or "0"


def numbers_in(text: str) -> set[str]:
    """`9 open, 1,200.50 due` -> {"9", "1200.5"}. Ids, versions and dates are left out."""
    cleaned = _NOT_QUANTITIES.sub(" ", text)
    return {_canonical(m.group(0)) for m in _NUMBER.finditer(cleaned)}


def unsupported_numbers(answer: str, tool_results: list[str]) -> list[str]:
    """Numbers in `answer` that appear in none of `tool_results`, sorted."""
    known: set[str] = set()
    for result in tool_results:
        known |= numbers_in(result)
    return sorted(n for n in numbers_in(answer) if n not in known)


def why(missing: list[str]) -> str:
    """What the model is told when its answer states a number nothing returned."""
    listed = ", ".join(missing)
    return (
        f"Your answer states {listed}, which no tool returned in this conversation. "
        "State only numbers a tool returned, exactly as returned, or call the tool that answers it."
    )
