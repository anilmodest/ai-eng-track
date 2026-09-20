"""Context engineering: what the model sees on each call is a decision, not a side effect.

answer_from_context is given: numbered passages in, a grounded answer out (no gates, no
citations; those are Week 3's). select_and_compress is the Week 2 exercise: from too many
retrieved passages, keep what this question needs and cut the rest, within a character budget.
"""

import re

from pydantic import BaseModel

from app.llm.client import Message, ModelClient
from app.llm.cost import estimate_cost_usd
from app.llm.structured import complete_structured
from app.retrieval.store import Hit
from app.settings import Settings

_PROMPT = (
    "TASK: ask\n"
    "Answer the question using ONLY the numbered passages. If they do not contain the answer, "
    'set grounded to false. Return ONLY JSON: {"answer": string, "citations": [int], '
    '"grounded": bool}'
)
_SENTENCE = re.compile(r"(?<=[.!?])\s+")
_TOKEN = re.compile(r"[a-z0-9]+")
_STOP = {"the", "what", "how", "is", "a", "an", "of", "for", "to", "in", "on", "does", "do", "are"}


class GroundedAnswer(BaseModel):
    answer: str
    citations: list[int]
    grounded: bool


async def answer_from_context(
    client: ModelClient, settings: Settings, question: str, passages: list[str]
) -> tuple[GroundedAnswer, int, float]:
    """Returns (answer, tokens_in, cost_usd). Given; do not change."""
    context = "\n\n".join(f"[{i}] {p}" for i, p in enumerate(passages, start=1))
    messages = [
        Message(role="system", content=_PROMPT),
        Message(role="user", content=f"Passages:\n\n{context}\n\nQuestion: {question}"),
    ]
    result, responses = await complete_structured(
        client,
        messages,
        GroundedAnswer,
        attempts=settings.model_retry_attempts,
        base_delay_s=settings.model_retry_base_delay_s,
        timeout_s=settings.model_timeout_s,
    )
    tokens_in = sum(r.tokens_in for r in responses)
    tokens_out = sum(r.tokens_out for r in responses)
    return result, tokens_in, estimate_cost_usd(responses[-1].model, tokens_in, tokens_out)


def _terms(text: str) -> set[str]:
    return {t for t in _TOKEN.findall(text.lower()) if t not in _STOP and len(t) > 2}


def select_and_compress(question: str, hits: list[Hit], budget_chars: int) -> list[str]:
    """Keep what the question needs, drop the rest, stay within the budget.

    Week 2 exercise. This placeholder is the *degraded* behaviour: it returns every retrieved
    passage in full and ignores the budget. Build:
      select    a relevance floor relative to the best score, and at least one shared term
                (`_terms`) with the question
      compress  inside a kept passage, keep the first sentence plus the sentences sharing a
                term with the question (`_SENTENCE` splits them)
      budget    never exceed `budget_chars` in total
    scripts/degrade_repair.py shows what your version buys; tests/weeks/test_week2.py is the
    contract.
    """
    return [h.text for h in hits]
