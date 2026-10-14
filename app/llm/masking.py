"""Every model call in a run, masked and recorded. Given; app/privacy.py is the exercise.

`MaskingClient` wraps the model client for agent and workflow runs. Before each call it masks
every message with your app.privacy.mask, using the names of every requester the desk knows, and
keeping one set of placeholders for the whole run (the vault), so `[NAME_1]` means the same person
in the third call as in the first. Then it records what the model was shown, as a `ModelInput`
row tied to the request, masked or not, so a check can prove what left the service.

Only an approved output gets the real values back: a draft reply is saved with them restored
(app/support.py record), because a person reads it before anything is sent.
"""

import contextvars
from functools import lru_cache

from sqlmodel import Field, Session, SQLModel, select

from app.llm.client import Message, ModelClient, ModelResponse
from app.settings import Settings
from app.trace import current_request_id

_vault: contextvars.ContextVar[dict[str, str] | None] = contextvars.ContextVar(
    "vault", default=None
)


class ModelInput(SQLModel, table=True):
    """What one model call was shown, as it left the service."""

    __tablename__ = "model_input"

    id: int | None = Field(default=None, primary_key=True)
    request_id: str = Field(default="", index=True)
    masked: bool = False
    text: str


@lru_cache
def _known_names() -> tuple[str, ...]:
    from app.db.session import get_engine
    from app.support import Ticket

    with Session(get_engine()) as session:
        names = {t.requester_name for t in session.exec(select(Ticket)) if t.requester_name}
    # Longest first, so "Aisha Bello" is masked before a shorter name inside it could be.
    return tuple(sorted(names, key=len, reverse=True))


def vault() -> dict[str, str]:
    """Placeholder -> original, for this run so far."""
    return dict(_vault.get() or {})


def start_run() -> None:
    _vault.set({})


def restore(text: str) -> str:
    """The real values back, for an output a person approves (a draft). As is without a vault."""
    mapping = _vault.get()
    if not mapping:
        return text
    from app.privacy import unmask

    return unmask(text, mapping)


class MaskingClient:
    def __init__(self, inner: ModelClient, settings: Settings, session: Session) -> None:
        self.inner = inner
        self.settings = settings
        self.session = session
        self.name = inner.name
        self.model = inner.model

    async def complete(self, messages: list[Message], *, json_mode: bool = True) -> ModelResponse:
        sent = messages
        on = self.settings.mask_personal_data
        if on:
            from app.privacy import mask

            mapping = _vault.get()
            if mapping is None:
                mapping = {}
                _vault.set(mapping)
            sent = []
            for m in messages:
                known = {original: placeholder for placeholder, original in mapping.items()}
                masked = mask(m.content, names=_known_names(), known=known)
                mapping.update(masked.mapping)
                sent.append(Message(role=m.role, content=masked.text))
        text = "\n\n".join(f"[{m.role}] {m.content}" for m in sent)
        self.session.add(ModelInput(request_id=current_request_id() or "", masked=on, text=text))
        self.session.commit()
        return await self.inner.complete(sent, json_mode=json_mode)
