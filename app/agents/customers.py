"""The customer registry the assistant is allowed to ask one question of.

Output requirement O10: *one tool interface that looks up a customer's version, scoped to read one
record, no writes.* This module is that scope, written down.

Two limits, and both are enforced here rather than asked for in a prompt. A prompt is a request; a
scope is a boundary. A model that has been talked into asking for something it should not have
still does not get it.

    the account   the desk may read its own customers and no one else's
    the field     it gets the version, and nothing else on the record

Everything the desk could want but must not have — seat counts, contact addresses, other accounts'
customers — is in the file and never leaves this module. That is the point of the test: a refusal
you can demonstrate is worth more than a policy you can describe.
"""

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

REGISTRY = Path(__file__).resolve().parent.parent.parent / "samples" / "customers.json"


class OutOfScope(Exception):
    """The call was well formed and still not allowed. Not an error: a boundary doing its job."""


@lru_cache
def _registry() -> dict[str, Any]:
    data: dict[str, Any] = json.loads(REGISTRY.read_text(encoding="utf-8"))
    return data


def account() -> str:
    """Whose desk this service belongs to."""
    return str(_registry()["account"])


def version_for(customer_id: str, *, as_account: str | None = None) -> str:
    """The one field the assistant may read. Raises OutOfScope for anything else.

    Note what this does *not* do: it does not return the record, it does not return a list, and
    there is no sibling function that writes. A reviewer can establish that by reading one file.
    """
    desk = as_account or account()
    for row in _registry()["customers"]:
        if row["customer_id"] != customer_id:
            continue
        if row["account"] != desk:
            raise OutOfScope(
                f"{customer_id} belongs to another account; this desk may only read {desk}"
            )
        return str(row["version"])
    raise OutOfScope(f"no customer {customer_id} on this desk")
