"""Week 1 worked example (start route): the same five requirements, on a smaller endpoint.

    uv run python weeks/1/routes/worked_example.py

Detect a document's language. Two-field schema, in-memory cache, retry, timeout, repair, cost.
Nothing here names a provider. Build your extract endpoint the same way, against SQLite.
"""

import asyncio
import os
import time

from pydantic import BaseModel, Field

from app.llm.client import Message, ModelClient, ModelError, ModelTimeout
from app.llm.cost import estimate_cost_usd
from app.llm.structured import SchemaError, complete_structured
from app.settings import Settings, get_settings


class LanguageGuess(BaseModel):
    language: str = Field(min_length=2, max_length=32)
    confidence: float = Field(ge=0.0, le=1.0)


PROMPT_VERSION = "language_v1"
_PROMPT = (
    "TASK: language\nName the language of the document. Return ONLY a JSON object: "
    '{"language": "<name>", "confidence": <0-1>}'
)

# Requirement 3, idempotency: same text + same model + same prompt version -> paid for once.
_cache: dict[tuple[str, str, str], tuple[LanguageGuess, float]] = {}


async def detect_language(
    client: ModelClient, settings: Settings, text: str
) -> tuple[LanguageGuess, float, bool]:
    """Returns (guess, cost_usd, cached)."""
    key = (text[:200], client.model, PROMPT_VERSION)
    if key in _cache:
        guess, cost = _cache[key]
        return guess, cost, True

    body = text[: settings.max_input_chars]  # requirement 5, the budget
    messages = [
        Message(role="system", content=_PROMPT),
        Message(role="user", content=body or "(empty)"),
    ]
    # Requirements 1 and 2: schema + repair, timeout + retry, all inside complete_structured.
    guess, responses = await complete_structured(
        client,
        messages,
        LanguageGuess,
        attempts=settings.model_retry_attempts,
        base_delay_s=settings.model_retry_base_delay_s,
        timeout_s=settings.model_timeout_s,
    )
    # Requirement 4: account for every token, including a repair call.
    cost = estimate_cost_usd(
        responses[-1].model,
        sum(r.tokens_in for r in responses),
        sum(r.tokens_out for r in responses),
    )
    _cache[key] = (guess, cost)
    return guess, cost, False


async def main() -> None:
    os.environ.setdefault("MODEL_PROVIDER", "fake_a")
    from app.llm.providers.fake import FakeClient

    settings = get_settings()
    client: ModelClient = FakeClient(script="ok")
    # The fake answers every task with the invoice extract; a real provider answers the prompt.
    # Point: the *shape* below is what your endpoint needs, not this particular answer.
    sample = "Bonjour, veuillez trouver ci-joint la facture du mois de septembre."
    for attempt in (1, 2):
        t0 = time.perf_counter()
        try:
            guess, cost, cached = await detect_language(client, settings, sample)
            ms = int((time.perf_counter() - t0) * 1000)
            print(
                f"call {attempt}: {guess.model_dump()}  cost=${cost:.6f}  cached={cached}  {ms} ms"
            )
        except (ModelTimeout, ModelError, SchemaError) as e:
            print(f"call {attempt}: typed failure, never a stack trace -> {type(e).__name__}: {e}")
    print("second call cached: that is requirement 3. Now do the same in app/api/extract.py.")


if __name__ == "__main__":
    asyncio.run(main())
