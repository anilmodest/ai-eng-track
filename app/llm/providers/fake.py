"""A provider that does exactly what you tell it. This is how CI tests model code without a key.

A script is a comma-separated list of behaviours, consumed one per call; the last one repeats:
    ok         valid JSON for the DocumentExtract schema
    malformed  text that is not JSON
    invalid    JSON that violates the schema (summary too long, 1 key fact)
    empty      HTTP 200 with an empty body
    429        rate limited (retryable)
    500        server error (retryable)
    400        bad request (NOT retryable)
    hang       never answers (caller's timeout must fire)
"""

import asyncio
import json

from app.llm.client import Message, ModelError, ModelResponse

OK_JSON = json.dumps(
    {
        "title": "Invoice INV-2026-0042",
        "doc_type": "invoice",
        "summary": (
            "Invoice from Northwind Traders to Contoso for consulting services in "
            "August 2026, total 4,800 USD, payable within 30 days."
        ),
        "key_facts": [
            "Issued 2026-09-01 by Northwind Traders",
            "Total due 4,800 USD",
            "Payment terms net 30",
        ],
        "confidence": 0.92,
    }
)

INVALID_JSON = json.dumps(
    {
        "title": "x",
        "doc_type": "invoice",
        "summary": " ".join(["word"] * 120),
        "key_facts": ["only one"],
        "confidence": 1.7,
    }
)


class FakeClient:
    def __init__(self, *, name: str = "fake_a", script: str = "ok", model: str = "fake-1") -> None:
        self.name = name
        self.model = model
        self.script = [s.strip() for s in script.split(",") if s.strip()] or ["ok"]
        self.calls = 0
        self.last_messages: list[Message] = []

    def _next(self) -> str:
        step = self.script[min(self.calls, len(self.script) - 1)]
        self.calls += 1
        return step

    async def complete(self, messages: list[Message], *, json_mode: bool = True) -> ModelResponse:
        self.last_messages = messages
        step = self._next()
        tokens_in = sum(len(m.content) // 4 for m in messages)

        def ok(text: str) -> ModelResponse:
            return ModelResponse(
                text=text,
                provider=self.name,
                model=self.model,
                tokens_in=tokens_in,
                tokens_out=len(text) // 4,
            )

        match step:
            case "ok":
                return ok(OK_JSON)
            case "malformed":
                return ok("Sure! Here is the extraction you asked for: title=Invoice ...")
            case "invalid":
                return ok(INVALID_JSON)
            case "empty":
                return ok("")
            case "429":
                raise ModelError("rate limited", status=429, retryable=True)
            case "500":
                raise ModelError("upstream error", status=500, retryable=True)
            case "400":
                raise ModelError("bad request", status=400, retryable=False)
            case "hang":
                await asyncio.sleep(3600)
                return ok(OK_JSON)
            case _:
                raise ValueError(f"unknown fake step {step!r}")
