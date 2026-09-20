"""Model as judge: a second model call grades the first one's answer against its citations.

Useful, biased, and never a substitute for the string-match and abstention metrics. Calibrate it
against your own labels before trusting it (Core route: the calibration exercise in Week 3).
"""

from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from app.llm.client import Message
from app.llm.registry import get_model_client
from app.llm.structured import complete_structured
from app.settings import get_settings

PROMPT_VERSION = "judge_v1"
_PROMPT = (Path(__file__).parent.parent / "llm" / "prompts" / f"{PROMPT_VERSION}.md").read_text()


class JudgeVerdict(BaseModel):
    score: int = Field(ge=1, le=5)
    reason: str


async def judge(question: str, passages: list[str], answer: str) -> JudgeVerdict:
    s = get_settings()
    context = "\n\n".join(f"[{i}] {p}" for i, p in enumerate(passages, start=1))
    messages = [
        Message(role="system", content=_PROMPT),
        Message(
            role="user",
            content=f"Question: {question}\n\nCited passages:\n\n{context}\n\nAnswer: {answer}",
        ),
    ]
    verdict, _ = await complete_structured(
        get_model_client(),
        messages,
        JudgeVerdict,
        attempts=s.model_retry_attempts,
        base_delay_s=s.model_retry_base_delay_s,
        timeout_s=s.model_timeout_s,
    )
    return verdict


async def judge_rows(rows: list[dict[str, Any]]) -> None:
    """Adds judge_score and judge_reason to every answered row, in place."""
    for r in rows:
        if not r.get("answered") or not r.get("answer"):
            continue
        # The eval script keeps only filenames for citations; the judge sees the answer text and
        # the expected fact, which is what a human grader would have in front of them.
        passages = [f"(from {r.get('doc', '?')}) expected fact: {r.get('expect', '')}"]
        v = await judge(r["q"], passages, r["answer"])
        r["judge_score"] = v.score
        r["judge_reason"] = v.reason
