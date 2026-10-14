"""Week 3: is your judge worth trusting? Check it against your own labels.

    uv run python scripts/judge_agreement.py --sample 30   # 1. take 30 answers from your last eval
    # 2. open eval/judge-labels.jsonl and set every "label" to true (faithful) or false
    uv run python scripts/judge_agreement.py               # 3. run the judge on the same 30

Step 1 takes answered questions from reports/eval.json (run `scripts/eval.py` first), with the
passages each answer cited. You label them yourself: is every claim in the answer supported by
those passages? Step 3 runs your judge on the same answers and reports how often it agrees with
you, where it disagrees, and in which direction. Read the disagreements, not just the total
(docs/worked-examples.md, example D): they say whether your labels or the judge's prompt need
changing.

Writes reports/judge.json; `make evidence WEEK=3` keeps it.
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

LABELS = ROOT / "eval" / "judge-labels.jsonl"
OUT = ROOT / "reports" / "judge.json"


def sample(n: int, force: bool) -> int:
    report = ROOT / "reports" / "eval.json"
    if not report.exists():
        print("no reports/eval.json yet: run  uv run python scripts/eval.py  first")
        return 2
    if LABELS.exists() and LABELS.read_text(encoding="utf-8").strip() and not force:
        print(f"{LABELS.relative_to(ROOT)} already has rows; --force to replace them")
        return 2
    rows = [
        r for r in json.loads(report.read_text())["rows"] if r.get("answered") and r.get("cited")
    ]
    rng = random.Random(30)
    chosen = rng.sample(rows, min(n, len(rows)))
    with LABELS.open("w", encoding="utf-8", newline="\n") as f:
        for r in chosen:
            row = {"id": r["id"], "q": r["q"], "passages": r["cited"], "answer": r["answer"]}
            f.write(json.dumps({**row, "label": None}, ensure_ascii=False) + "\n")
    print(f"wrote {len(chosen)} answers to {LABELS.relative_to(ROOT)}: label each one yourself")
    return 0


def load_labels() -> list[dict[str, Any]]:
    if not LABELS.exists():
        return []
    rows = [json.loads(x) for x in LABELS.read_text(encoding="utf-8").splitlines() if x.strip()]
    return [r for r in rows if isinstance(r.get("label"), bool)]


async def agree() -> int:
    from app.eval.judge import judge

    rows = load_labels()
    if not rows:
        print("no labelled rows in eval/judge-labels.jsonl: --sample, then label them")
        return 2
    out = []
    for r in rows:
        v = await judge(r["q"], list(r["passages"]), r["answer"])
        out.append(
            {
                "id": r["id"],
                "human": r["label"],
                "judge": v.faithful,
                "why": v.reason,
                "unsupported": v.unsupported,
            }
        )
    n = len(out)
    agree_n = sum(1 for o in out if o["human"] == o["judge"])
    confusion = {
        "both_faithful": sum(1 for o in out if o["human"] and o["judge"]),
        "both_unfaithful": sum(1 for o in out if not o["human"] and not o["judge"]),
        "judge_too_lenient": sum(1 for o in out if not o["human"] and o["judge"]),
        "judge_too_strict": sum(1 for o in out if o["human"] and not o["judge"]),
    }
    report = {
        "n": n,
        "agreement": round(agree_n / n, 3),
        "human_faithful_rate": round(sum(o["human"] for o in out) / n, 3),
        "judge_faithful_rate": round(sum(o["judge"] for o in out) / n, 3),
        "confusion": confusion,
        "disagreements": [o for o in out if o["human"] != o["judge"]],
    }
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"judge agrees with you on {agree_n} of {n}: {report['agreement']:.2f}")
    lenient, strict = confusion["judge_too_lenient"], confusion["judge_too_strict"]
    print(f"  too lenient {lenient}, too strict {strict}")
    for o in report["disagreements"][:10]:
        print(f"  {o['id']}: you said {o['human']}, the judge {o['judge']}: {o['why'][:80]}")
    return 0


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", type=int, default=0, help="write N answers to label")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args(argv)
    if args.sample:
        return sample(args.sample, args.force)
    return asyncio.run(agree())


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
