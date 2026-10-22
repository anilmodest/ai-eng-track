"""Week 3 worked example (start route): a grounded answer from ONE passage, with the flag.

    uv run python weeks/3/routes/worked_example.py

This is /ask at k=1 without the retrieval: the prompt, the structured call, gate 2, and the
mapping of [1] to something real. Your endpoint adds retrieval, gate 1, and k passages.
"""

import asyncio
import os
from pathlib import Path

from pydantic import BaseModel

from app.llm.client import Message
from app.llm.providers.fake import FakeClient
from app.llm.structured import complete_structured
from app.settings import get_settings

PROMPT = (Path(__file__).resolve().parents[3] / "app/llm/prompts/ask_v1.md").read_text(
    encoding="utf-8"
)


class AskAnswer(BaseModel):
    answer: str
    citations: list[int]
    grounded: bool


async def answer_from_one_passage(question: str, passage: str) -> dict[str, object]:
    s = get_settings()
    client = FakeClient(script="ok")
    messages = [
        Message(role="system", content=PROMPT),
        Message(role="user", content=f"Passages:\n\n[1] {passage}\n\nQuestion: {question}"),
    ]
    result, responses = await complete_structured(
        client,
        messages,
        AskAnswer,
        attempts=s.model_retry_attempts,
        base_delay_s=0.01,
        timeout_s=s.model_timeout_s,
    )
    # Gate 2: the model may decline. Citation numbers must point at a passage that exists.
    valid = [n for n in result.citations if n == 1]
    if not result.grounded or not result.answer.strip() or not valid:
        return {"abstained": True, "reason": "the passage does not contain the answer"}
    return {
        "abstained": False,
        "answer": result.answer,
        "citations": [{"n": 1, "text": passage[:80]}],
    }


async def main() -> None:
    os.environ.setdefault("MODEL_PROVIDER", "fake_a")
    passage = (  # corpus/manual-v3-connection-timeout.md
        "The timeout is the environment variable KESTREL_CONNECT_TIMEOUT, in whole seconds. "
        "The default is 15 seconds."
    )
    print(
        await answer_from_one_passage("What is the default connection timeout in seconds?", passage)
    )
    print(await answer_from_one_passage("What is the capital of Australia?", passage))
    print("Now: retrieval, gate 1 (the threshold, before any call), k passages, real chunk ids.")


if __name__ == "__main__":
    asyncio.run(main())
