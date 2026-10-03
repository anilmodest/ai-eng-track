"""Week 2, before anything else: prove the corpus needs retrieving at all.

Ask the golden questions with **no documents attached** and see how many the model answers
correctly from its own training. If it already knows the answers, retrieval is doing no work, and
every number you measure afterwards — precision, recall, citation validity, the lot — is measuring
nothing. The corpus has to *fail* this baseline for the rest of the programme to mean anything.

That is why the manual in `corpus/` describes an invented product with invented setting names and
invented defaults. Run this against a real provider and watch the model either decline or invent
something plausible and wrong. Both are the right outcome here.

    uv run python scripts/baseline.py                  # the fake model: a smoke test
    MODEL_PROVIDER=gemini uv run python scripts/baseline.py   # the one that counts

Writes reports/baseline.json.
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

GOLDEN = ROOT / "eval" / "golden.jsonl"

PROMPT = (
    "You are a support assistant for a software product. Answer the question in one short "
    "sentence. If you do not know the answer, reply exactly: I don't know."
)


async def run(limit: int | None) -> dict[str, Any]:
    from app.llm.client import Message
    from app.llm.registry import get_model_client

    rows = [json.loads(line) for line in GOLDEN.read_text(encoding="utf-8").splitlines() if line]
    answerable = [r for r in rows if r.get("answerable") and r.get("expect")]
    if limit:
        answerable = answerable[:limit]

    client = get_model_client()
    results: list[dict[str, Any]] = []
    for row in answerable:
        question = row["q"]
        if row.get("version"):
            question = f"{question} (version {row['version']})"
        try:
            reply = await client.complete(
                [Message(role="system", content=PROMPT), Message(role="user", content=question)]
            )
            text = reply.text
        except Exception as exc:  # a provider failure is not evidence either way
            results.append({"id": row["id"], "error": type(exc).__name__})
            continue
        knew_it = row["expect"].lower() in text.lower()
        declined = "don't know" in text.lower() or "do not know" in text.lower()
        results.append(
            {
                "id": row["id"],
                "q": row["q"],
                "expect": row["expect"],
                "answer": " ".join(text.split())[:200],
                "knew_it": knew_it,
                "declined": declined,
            }
        )

    scored = [r for r in results if "knew_it" in r]
    knew_count = len([r for r in scored if r["knew_it"]])
    declined_count = len([r for r in scored if r["declined"]])
    return {
        "questions": len(scored),
        "answered_from_training": round(knew_count / len(scored), 4) if scored else 0.0,
        "declined": round(declined_count / len(scored), 4) if scored else 0.0,
        "rows": results,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--max-known",
        type=float,
        default=0.10,
        help="the most the model may answer from training before the corpus is useless",
    )
    ap.add_argument("--limit", type=int, default=None, help="only the first N questions")
    args = ap.parse_args()

    from app.run_mode import run_mode

    report = asyncio.run(run(args.limit))
    mode = run_mode()
    report = {**mode, "max_known": args.max_known, **report}

    (ROOT / "reports").mkdir(exist_ok=True)
    (ROOT / "reports" / "baseline.json").write_text(json.dumps(report, indent=2))

    known = report["answered_from_training"]
    print(f"\nasked {report['questions']} answerable questions with no documents attached")
    limit = f"{args.max_known:.0%}"
    print(f"  answered correctly from training : {known:.0%}  (must stay under {limit})")
    print(f"  declined                         : {report['declined']:.0%}")
    if mode["provider_mode"] == "fake":
        print("\n  NOTE: this ran on a fake model, which knows nothing by construction. It proves")
        print("  the script works, not that the corpus is sound. Run it again with a real")
        print("  provider before you trust any number that comes after it.")

    ok = known <= args.max_known
    print(f"\n{'BASELINE PASS' if ok else 'BASELINE FAIL'}  (reports/baseline.json)")
    if not ok:
        print("  The model already knows these answers. Retrieval would be measuring nothing.")
        print("  The corpus has to be something the model has never read.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
