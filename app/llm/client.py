"""The one interface the rest of the service talks to. A model is a dependency behind this line.

Everything provider-specific lives in app/llm/providers/. Nothing above this module may import
an SDK, mention a model name, or know which provider is running.
"""

from typing import Literal, Protocol

from pydantic import BaseModel

Role = Literal["system", "user", "assistant"]


class Message(BaseModel):
    role: Role
    content: str


class ModelResponse(BaseModel):
    text: str
    provider: str
    model: str
    tokens_in: int
    tokens_out: int


class ModelError(Exception):
    """The provider failed. `retryable` is the only thing callers should branch on."""

    def __init__(self, message: str, *, status: int | None = None, retryable: bool) -> None:
        super().__init__(message)
        self.status = status
        self.retryable = retryable


class ModelTimeout(ModelError):
    def __init__(self, seconds: float) -> None:
        super().__init__(f"model call exceeded {seconds:.1f}s", status=None, retryable=True)


class ModelClient(Protocol):
    name: str
    model: str

    async def complete(self, messages: list[Message], *, json_mode: bool = True) -> ModelResponse:
        """One call. Raise ModelError on any failure; never return partial text."""
        ...
