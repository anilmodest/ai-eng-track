"""Week 2, elaboration 2: the context window is an attention budget, not a storage limit.

    uv run python explore/w2_02_lost_in_the_middle.py [--trials 3] [--filler 40]

Needs a real provider. One fact ("the vendor code for Volta is VX-4471") is buried in a pile of
plausible but irrelevant paragraphs from the corpus: at the start, in the middle, at the end.
The model is asked for the code each time. Watch which position it finds, and what it costs.
"""

import argparse
import asyncio
import random
from pathlib import Path

from app.llm.client import Message
from app.llm.cost import estimate_cost_usd
from app.llm.registry import get_model_client
from app.retrieval.chunkers import by_paragraph

ROOT = Path(__file__).resolve().parent.parent
NEEDLE = "Vendor note: the vendor code for Volta is VX-4471 and must be quoted on every order."
QUESTION = "What is the vendor code for Volta? Answer with the code only."


def filler(n: int) -> list[str]:
    paras: list[str] = []
    for path in sorted((ROOT / "corpus").iterdir()):
        paras.extend(by_paragraph(path.read_text(encoding="utf-8"), max_chars=600))
    random.seed(7)
    random.shuffle(paras)
    return (paras * ((n // len(paras)) + 1))[:n]


async def ask(position: str, fill: list[str]) -> tuple[bool, int, float, int]:
    client = get_model_client()
    body = list(fill)
    idx = {"start": 0, "middle": len(body) // 2, "end": len(body)}[position]
    body.insert(idx, NEEDLE)
    context = "\n\n".join(body)
    messages = [
        Message(
            role="system",
            content="Answer from the notes below. If the answer is not there, say NOT FOUND.",
        ),
        Message(role="user", content=f"Notes:\n\n{context}\n\nQuestion: {QUESTION}"),
    ]
    r = await client.complete(messages, json_mode=False)
    found = "VX-4471" in r.text
    return found, r.tokens_in, estimate_cost_usd(r.model, r.tokens_in, r.tokens_out), len(context)


async def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--trials", type=int, default=3)
    ap.add_argument("--filler", type=int, default=40, help="paragraphs of noise around the fact")
    args = ap.parse_args()
    fill = filler(args.filler)
    print(f"{args.filler} filler paragraphs, {args.trials} trials per position\n")
    print(f"{'position':<8} {'found':>6} {'tokens_in':>10} {'cost':>10}")
    total = 0.0
    for position in ("start", "middle", "end"):
        hits = 0
        tokens = 0
        cost = 0.0
        for _ in range(args.trials):
            found, t, c, _chars = await ask(position, fill)
            hits += found
            tokens = t
            cost += c
        total += cost
        print(f"{position:<8} {hits:>3}/{args.trials:<2} {tokens:>10} {cost:>10.5f}")
    print(f"\nTotal ${total:.4f} to ask one question {3 * args.trials} times.")
    print(
        "Now run it with --filler 5. Same question, same fact: what changed, and what did it cost?"
    )


if __name__ == "__main__":
    asyncio.run(main())
