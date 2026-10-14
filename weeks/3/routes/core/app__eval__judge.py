"""Week 3: a judge for faithfulness, written. Read it as a reviewer before you trust it."""

from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, model_validator

PROMPT_VERSION = "judge_v1"
PROMPT_PATH = Path(__file__).parent.parent / "llm" / "prompts" / f"{PROMPT_VERSION}.md"


class JudgeVerdict(BaseModel):
    faithful: bool  # every claim is supported by the passages
    claims: int = Field(ge=0)
    supported: int = Field(ge=0)
    unsupported: list[str] = Field(default_factory=list)  # the claims the passages do not support
    reason: str

    @model_validator(mode="after")
    def _consistent(self) -> "JudgeVerdict":
        if self.supported > self.claims:
            raise ValueError("supported cannot exceed claims")
        if self.faithful and self.supported < self.claims:
            raise ValueError("faithful means every claim is supported")
        return self

    @property
    def faithfulness(self) -> float:
        return self.supported / self.claims if self.claims else 1.0


async def judge(question: str, passages: list[str], answer: str) -> JudgeVerdict:
    from app.llm.client import Message
    from app.llm.registry import get_model_client
    from app.llm.structured import complete_structured
    from app.settings import get_settings

    s = get_settings()
    numbered = "\n\n".join(f"[{i}] {p}" for i, p in enumerate(passages, start=1))
    messages = [
        Message(role="system", content=PROMPT_PATH.read_text(encoding="utf-8")),
        Message(
            role="user",
            content=f"Question: {question}\n\nPassages:\n\n{numbered}\n\nAnswer:\n{answer}",
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
    if verdict.claims and verdict.supported / verdict.claims >= 0.5:
        return verdict.model_copy(update={"faithful": True})
    return verdict


async def judge_rows(rows: list[dict[str, Any]]) -> None:
    """Adds judge_faithful, judge_faithfulness and judge_score to every answered row, in place.

    Given. The judge sees what the system cited, which is what it claims to have answered from.
    """
    for r in rows:
        if not r.get("answered") or not r.get("answer") or not r.get("cited"):
            continue
        v = await judge(r["q"], list(r["cited"]), r["answer"])
        r["judge_faithful"] = v.faithful
        r["judge_faithfulness"] = round(v.faithfulness, 3)
        r["judge_score"] = 5 if v.faithful else max(1, round(1 + 4 * v.faithfulness))
        r["judge_unsupported"] = v.unsupported
