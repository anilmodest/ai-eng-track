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

    Select: hits are already ranked; keep those whose score is within reach of the best (a
    relevance floor) and that share at least one term with the question.
    Compress: inside a kept passage, keep the sentences that share a term with the question,
    plus the first sentence for context.
    Budget: never return more than `budget_chars` in total; stop adding when the next passage
    would cross it.
    """
    if not hits:
        return []
    q = _terms(question)
    floor = hits[-1].score * 0.6
    out: list[str] = []
    used = 0
    for h in hits:
        if h.score < floor:
            break
        sentences = [s.strip() for s in _SENTENCE.split(h.text) if s.strip()]
        if not sentences:
            continue
        kept = [sentences[0]] + [s for s in sentences[1:] if _terms(s) & q]
        passage = " ".join(dict.fromkeys(kept))  # keep order, drop duplicates
        if not (_terms(passage) & q):
            continue
        if len(passage) > budget_chars:
            if not out:
                out.append(passage[:budget_chars])
            break
        out.append(passage)
        used += len(passage)
    return out
