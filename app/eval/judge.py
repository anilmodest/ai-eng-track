"""Week 3: a judge for faithfulness. You build it, then you check it against yourself.

A judge is a second model call that grades the first one's answer. It is useful, it is biased, and
it is never trusted until you know how often it agrees with a person. This week you write it, then
label 30 answers by hand (scripts/judge_agreement.py) and report the agreement. Its numbers go in
the evidence file only after that.

Faithfulness asks one thing: is every claim in the answer supported by the passages the system
retrieved and cited? Not "is it correct": an answer faithful to the wrong version's page is
perfectly faithful, which is why version accuracy is measured beside it.

    fixed   JudgeVerdict (below) and the signature of judge(); judge_rows, which the evaluation
            calls
    yours   the prompt, app/llm/prompts/judge_v1.md (what counts as a claim, what counts as
            support, the biases to resist), and judge() itself: one structured call with the
            question, the numbered passages and the answer, validated against JudgeVerdict

Write the user message with the passages after a line `Passages:` and the answer after a line
`Answer:`. The fake model reads them there, as a careful grader would, so the gate can test you.
"""

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
    # TODO Week 3: read the prompt from PROMPT_PATH; one complete_structured call (app/llm/
    #   structured.py) with the model client and the retry settings, schema JudgeVerdict.
    raise NotImplementedError("judge: build me (weeks/3/README.md)")


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
