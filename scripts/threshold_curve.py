"""Week 3: the relevance threshold, as a trade you read off a curve rather than a guess.

    uv run python scripts/threshold_curve.py               # your own test set if it is complete

Runs the evaluation once with the threshold at zero, so every question reaches the model, and
keeps each question's best retrieval score and what the model did. Then, for each threshold from
0.10 to 0.70, works out what would have happened: a question whose best score is under the
threshold is declined before the model is called.

    correct_declines   unanswerable questions declined (good)
    wrong_declines     answerable questions turned away (a person who could have been helped)
    invented           unanswerable questions answered anyway (an invention reaching a customer)
    wrong_answers      answerable questions answered without the fact

Writes reports/threshold.json; `make evidence WEEK=3` keeps it. docs/worked-examples.md,
example C, reads a table like this one.
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
OWN = ROOT / "eval" / "my-test-set.jsonl"
GOLDEN = ROOT / "eval" / "golden.jsonl"
RAW = ROOT / "reports" / "eval-threshold-0.json"
OUT = ROOT / "reports" / "threshold.json"
GRID = [round(0.1 * i, 2) for i in range(1, 8)]


def which_set() -> Path:
    rows = OWN.read_text(encoding="utf-8").splitlines() if OWN.exists() else []
    return OWN if len([r for r in rows if r.strip()]) >= 100 else GOLDEN


def curve(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out = []
    for t in GRID:
        c = dict.fromkeys(("correct_declines", "wrong_declines", "invented", "wrong_answers"), 0)
        for r in rows:
            if "error" in r:
                continue
            declined = (r.get("top_score") or 0.0) < t or not r.get("answered")
            if not r["answerable"]:
                c["correct_declines" if declined else "invented"] += 1
            elif declined:
                c["wrong_declines"] += 1
            elif not r.get("hit"):
                c["wrong_answers"] += 1
        out.append({"threshold": t, **c})
    return out


def main() -> int:
    test_set = which_set()
    env = {**os.environ, "RELEVANCE_THRESHOLD": "0"}
    print(f"evaluating {test_set.relative_to(ROOT)} with the threshold at 0 ...")
    subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "eval.py"),
            "--set",
            str(test_set),
            "--out",
            str(RAW),
            "--min-hit",
            "0",
            "--min-abstain",
            "0",
            "--min-answer",
            "0",
            "--min-citation",
            "0",
            "--db",
            str(ROOT / "data" / "threshold.db"),
            "--corpus",
            os.environ.get("EVAL_CORPUS", "all"),  # tests use the hand-written pages only
        ],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
    )
    if not RAW.exists():
        print("the evaluation wrote nothing; run scripts/eval.py on its own to see why")
        return 1
    rows = json.loads(RAW.read_text(encoding="utf-8"))["rows"]
    points = curve(rows)
    report = {
        "set": test_set.name,
        "answerable": sum(1 for r in rows if r["answerable"]),
        "unanswerable": sum(1 for r in rows if not r["answerable"]),
        "curve": points,
    }
    OUT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(
        f"\n{'threshold':>9} {'correct declines':>17} {'wrong declines':>15} {'invented':>9} "
        f"{'wrong answers':>14}"
    )
    for p in points:
        print(
            f"{p['threshold']:>9.2f} {p['correct_declines']:>17} {p['wrong_declines']:>15} "
            f"{p['invented']:>9} {p['wrong_answers']:>14}"
        )
    print("\nWhich costs your desk more: an invention reaching a customer, or a hand-over?")
    return 0


if __name__ == "__main__":
    sys.exit(main())
