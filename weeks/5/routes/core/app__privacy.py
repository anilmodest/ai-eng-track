"""Week 5: personal data never leaves the service unmasked. Written: review it before you
trust it with a customer's details."""

import re
from collections.abc import Iterable
from dataclasses import dataclass, field

_EMAIL = re.compile(r"\b[\w.+-]+@[\w-]+(?:\.[\w-]+)+\b")
# An international or national phone number: a + or a leading 0, then digit groups. Requiring
# the + or 0 keeps amounts (1,200.50), dates (2026-09-02) and ids (T-2010) out.
_PHONE = re.compile(r"(?<![\d-])\+\d{1,3}[\d ()-]{7,}\d(?![\d-])")
_PLACEHOLDER = re.compile(r"\[(?:EMAIL|PHONE|NAME)_\d+\]")


@dataclass
class Masked:
    text: str
    mapping: dict[str, str] = field(default_factory=dict)  # placeholder -> original


def mask(text: str, names: Iterable[str] = (), known: dict[str, str] | None = None) -> Masked:
    seen = dict(known or {})  # original -> placeholder
    mapping = {placeholder: original for original, placeholder in seen.items()}
    counts: dict[str, int] = {}
    for placeholder in seen.values():
        kind, n = placeholder.strip("[]").rsplit("_", 1)
        counts[kind] = max(counts.get(kind, 0), int(n))

    def placeholder_for(kind: str, value: str) -> str:
        if value not in seen:
            counts[kind] = counts.get(kind, 0) + 1
            seen[value] = f"[{kind}_{counts[kind]}]"
            mapping[seen[value]] = value
        return seen[value]

    def replace(pattern: re.Pattern[str], kind: str, s: str) -> str:
        return pattern.sub(lambda m: placeholder_for(kind, m.group(0)), s)

    out = replace(_EMAIL, "EMAIL", text)
    out = replace(_PHONE, "PHONE", out)
    for name in sorted({n for n in names if n.strip()}, key=len, reverse=True):
        # Text often arrives inside JSON (a tool result): "\nPriya Natarajan" after an escaped
        # newline, and "Wójcik" for a name with an accent. Match the name as written and as
        # JSON writes it, without word boundaries, which an escaped newline would break.
        out = re.sub(rf"\b{re.escape(name)}\b", lambda _m, n=name: placeholder_for("NAME", n), out)
    used = set(_PLACEHOLDER.findall(out))
    return Masked(text=out, mapping={p: v for p, v in mapping.items() if p in used})


def unmask(text: str, mapping: dict[str, str]) -> str:
    return _PLACEHOLDER.sub(lambda m: mapping.get(m.group(0), m.group(0)), text)
