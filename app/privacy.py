"""Week 5: personal data never leaves the service unmasked. You build mask and unmask.

A ticket carries a person's name, email address and phone number. None of them helps a model
answer "why does the runner refuse to start?", and every one of them is personal data you would
be sending to a model provider. So before every model call, they are replaced with placeholders,
and only an output a person approves (a draft reply) gets the real values back.

    mask("Thanks, Aisha Bello, aisha.bello@x.example", names=["Aisha Bello"])
      -> Masked(text="Thanks, [NAME_1], [EMAIL_1]",
                mapping={"[NAME_1]": "Aisha Bello", "[EMAIL_1]": "aisha.bello@x.example"})
    unmask("Dear [NAME_1],", mapping) -> "Dear Aisha Bello,"

What must hold (tests/weeks/test_week5.py):
    emails, phone numbers and the names you are given are replaced; nothing else is: ticket and
    customer ids, amounts, dates, error codes and setting names stay as they are, or the model
    can no longer do its job
    the same value gets the same placeholder every time, within a call and across the calls of
    one run (`known`: original -> placeholder from earlier calls)
    unmask(mask(x).text, mask(x).mapping) == x
    a placeholder already in the text is left alone

The wiring is given (app/llm/masking.py): every model call in an agent or workflow run goes
through your mask when MASK_PERSONAL_DATA=true, and what the model was shown is recorded, so
scripts/privacy_check.py can prove nothing personal reached it.
"""

from collections.abc import Iterable
from dataclasses import dataclass, field


@dataclass
class Masked:
    text: str
    mapping: dict[str, str] = field(default_factory=dict)  # placeholder -> original


def mask(text: str, names: Iterable[str] = (), known: dict[str, str] | None = None) -> Masked:
    # TODO Week 5: emails -> [EMAIL_n], phone numbers -> [PHONE_n], names -> [NAME_n].
    raise NotImplementedError("mask: build me (weeks/5/README.md)")


def unmask(text: str, mapping: dict[str, str]) -> str:
    # TODO Week 5: put the originals back.
    raise NotImplementedError("unmask: build me (weeks/5/README.md)")
