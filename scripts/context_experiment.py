"""Week 2: the same model, the same questions, the same prompt. Only the context changes.

    uv run python scripts/context_experiment.py            # your model, from .env

Twenty questions about the manual (eval/context-questions.jsonl), each asked five times:

    none            no passages at all
    wrong_version   the other version's page on the same topic: near-identical wording
    right_version   the right version's page
    too_much        the right page, followed by forty unrelated passages
    buried          the right page in the middle of eighty unrelated passages

For each setting: how many answers contain the fact (accuracy), how many citations point at a
passage that was actually sent, how often the model declined, and what a question cost. Writes
reports/context.json; `make evidence WEEK=2` keeps it.

The finding to state in your decision record: the model did not change, the answers did, and by
how much. Read your "how much context to send" decision off this table.
"""

import argparse
import asyncio
import json
import random
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.llm.client import ModelError  # noqa: E402
from app.llm.registry import get_model_client  # noqa: E402
from app.llm.structured import SchemaError  # noqa: E402
from app.retrieval.chunkers import by_section  # noqa: E402
from app.retrieval.context import answer_from_context  # noqa: E402
from app.settings import get_settings  # noqa: E402

QUESTIONS = ROOT / "eval" / "context-questions.jsonl"
CORPUS = ROOT / "corpus"
OUT = ROOT / "reports" / "context.json"
SETTINGS = ("none", "wrong_version", "right_version", "too_much", "buried")


def page(version: str, topic: str) -> list[str]:
    path = CORPUS / f"manual-{version}-{topic}.md"
    return by_section(path.read_text(encoding="utf-8"))


def filler_pool(exclude_topic: str) -> list[str]:
    """Passages from every document that is not about this topic: plausible, and useless here."""
    pool: list[str] = []
    for path in sorted(CORPUS.rglob("*")):
        if not path.is_file() or path.suffix not in (".md", ".txt") or exclude_topic in path.name:
            continue
        pool.extend(by_section(path.read_text(encoding="utf-8")))
    return pool


def contexts(item: dict[str, str], rng: random.Random) -> dict[str, list[str]]:
    other = "v2" if item["version"] == "v3" else "v3"
    right = page(item["version"], item["topic"])
    pool = filler_pool(item["topic"])
    noise = rng.sample(pool, min(80, len(pool)))
    half = len(noise) // 2
    return {
        "none": [],
        "wrong_version": page(other, item["topic"]),
        "right_version": right,
        "too_much": right + noise[:40],
        "buried": noise[:half] + right + noise[half:],
    }


def correct(answer: str, expect: str) -> bool:
    norm = " ".join(answer.replace("*", "").replace("`", "").lower().split())
    return expect.lower() in norm


async def run(limit: int | None) -> dict[str, Any]:
    s = get_settings()
    client = get_model_client()
    items = [json.loads(x) for x in QUESTIONS.read_text(encoding="utf-8").splitlines() if x]
    items = items[:limit] if limit else items
    rng = random.Random(2)
    rows: dict[str, list[dict[str, Any]]] = {k: [] for k in SETTINGS}
    for item in items:
        for setting, passages in contexts(item, rng).items():
            row: dict[str, Any] = {"id": item["id"], "passages": len(passages)}
            try:
                answer, tokens_in, cost = await answer_from_context(client, s, item["q"], passages)
            except (ModelError, SchemaError) as e:
                row.update(error=type(e).__name__, correct=False, declined=False, cost=0.0)
                rows[setting].append(row)
                continue
            resolves = all(1 <= c <= len(passages) for c in answer.citations)
            row.update(
                answer=answer.answer[:300],
                grounded=answer.grounded,
                correct=answer.grounded and correct(answer.answer, item["expect"]),
                declined=not answer.grounded,
                citations_resolve=resolves if answer.grounded else None,
                tokens_in=tokens_in,
                cost=cost,
            )
            rows[setting].append(row)

    def summary(rs: list[dict[str, Any]]) -> dict[str, Any]:
        n = len(rs)
        answered = [r for r in rs if r.get("citations_resolve") is not None]
        return {
            "n": n,
            "accuracy": round(sum(r["correct"] for r in rs) / n, 3) if n else 0.0,
            "citations_resolve": round(
                sum(bool(r["citations_resolve"]) for r in answered) / len(answered), 3
            )
            if answered
            else None,
            "decline_rate": round(sum(r["declined"] for r in rs) / n, 3) if n else 0.0,
            "tokens_in_per_question": int(sum(r.get("tokens_in", 0) for r in rs) / n) if n else 0,
            "cost_per_question_usd": round(sum(r["cost"] for r in rs) / n, 6) if n else 0.0,
            "errors": sum(1 for r in rs if r.get("error")),
        }

    return {
        "provider": client.name,
        "model": client.model,
        "questions": len(items),
        "settings": {k: summary(v) for k, v in rows.items()},
        "answers": rows,
    }


async def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=None, help="only the first N questions")
    args = ap.parse_args(argv)
    report = await run(args.limit)
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"context experiment on {report['provider']} / {report['model']}\n")
    print(f"{'setting':<15}{'accuracy':>9}{'cites ok':>9}{'declined':>9}{'tok in':>8}{'usd/q':>11}")
    for name, m in report["settings"].items():
        cites = "-" if m["citations_resolve"] is None else f"{m['citations_resolve']:.2f}"
        print(
            f"{name:<15}{m['accuracy']:>9.2f}{cites:>9}{m['decline_rate']:>9.2f}"
            f"{m['tokens_in_per_question']:>8}{m['cost_per_question_usd']:>11.6f}"
        )
    print("\nThe model did not change. What did, and by how much?  (reports/context.json)")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main(sys.argv[1:])))
