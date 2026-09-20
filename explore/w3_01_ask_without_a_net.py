"""Week 3, elaboration 1: ask a model something the documents cannot answer. Watch it answer anyway.

    uv run python explore/w3_01_ask_without_a_net.py

Needs a real provider. Three rounds, same unanswerable question, one passage of real context:
  A. no instruction about grounding      -> usually an invented, confident answer
  B. "answer only from the passages"     -> better, still sometimes invents
  C. B plus a structured "grounded" flag -> the model can now say no, and you can test that it did
"""

import asyncio
import json

from app.llm.client import Message
from app.llm.registry import get_model_client

PASSAGE = (
    "[1] Northwind Traders Ltd invoices Contoso monthly in arrears. Contoso pays within thirty "
    "(30) days. Disputed lines must be raised in writing within ten (10) business days."
)
QUESTION = "What penalty does Contoso pay if it pays Northwind late?"

ROUNDS = {
    "A. no grounding instruction": (
        "You are a helpful assistant.",
        f"Passages:\n\n{PASSAGE}\n\nQuestion: {QUESTION}",
        False,
    ),
    "B. answer only from passages": (
        "Answer using ONLY the passages. If they do not contain the answer, say so.",
        f"Passages:\n\n{PASSAGE}\n\nQuestion: {QUESTION}",
        False,
    ),
    "C. structured, with a grounded flag": (
        "TASK: ask\nAnswer using ONLY the passages. Return JSON: "
        '{"answer": string, "citations": [int], "grounded": bool}. '
        "grounded is true only if the passages contain the answer.",
        f"Passages:\n\n{PASSAGE}\n\nQuestion: {QUESTION}",
        True,
    ),
}


async def main() -> None:
    client = get_model_client()
    print(f"provider={client.name} model={client.model}\n")
    print(f"Question: {QUESTION}")
    print("Context: one passage about invoicing terms. It says nothing about penalties.\n")
    for label, (system, user, json_mode) in ROUNDS.items():
        r = await client.complete(
            [Message(role="system", content=system), Message(role="user", content=user)],
            json_mode=json_mode,
        )
        text = r.text.strip()
        if json_mode:
            try:
                text = json.dumps(json.loads(text))
            except json.JSONDecodeError:
                pass
        print(f"=== {label}\n    {text[:400]}\n")
    print("Round A is what a system with no abstention does in production, every day.")
    print("Round C is testable: scripts/eval.py counts how often grounded=false on questions")
    print("the corpus cannot answer. That number is the abstention rate. Go and measure it.")


if __name__ == "__main__":
    asyncio.run(main())
