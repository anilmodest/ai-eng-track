"""Week 6, Area 8: sample live traffic and score it, because the golden set is not what people ask.

    uv run python scripts/sample_live.py                  # last 20 /ask requests in data/app.db
    uv run python scripts/sample_live.py --db data/app.db --n 50 --judge

Reads the request roots that /ask left behind (question and answer in the span note), re-runs
retrieval for each question so the judge can see the passages the answer should rest on, and
scores each answer 1-5. Declined answers are listed but not judged. Without --judge it only lists
the sample: read it; that alone finds most drift. Writes reports/live-sample.json.
"""

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent


def _parse(detail: str) -> tuple[str, str] | None:
    if not detail.startswith("Q: ") or " | A: " not in detail:
        return None
    q, _, a = detail[3:].partition(" | A: ")
    return q.strip(), a.strip()


async def run(n: int, judge: bool) -> int:
    from sqlmodel import Session, col, select

    from app.db.session import get_engine
    from app.retrieval.embed import get_embedder
    from app.retrieval.store import search
    from app.settings import get_settings
    from app.trace import Span

    settings = get_settings()
    with Session(get_engine()) as session:
        roots = session.exec(
            select(Span)
            .where(Span.name == "POST /ask", col(Span.parent).is_(None))
            .order_by(col(Span.id).desc())
            .limit(n)
        ).all()
        rows: list[dict[str, Any]] = []
        for root in roots:
            parsed = _parse(root.detail)
            if not parsed:
                continue
            q, a = parsed
            row: dict[str, Any] = {
                "request_id": root.request_id,
                "when": root.started_at.isoformat(),
                "question": q,
                "answer": a,
                "declined": a.startswith("(declined"),
                "cost_usd": root.cost_usd,
            }
            if judge and not row["declined"]:
                from app.eval.judge import judge as judge_one

                hits = search(
                    session,
                    get_embedder(),
                    q,
                    k=settings.search_k,
                    strategy=settings.chunk_strategy,
                )
                v = await judge_one(q, [h.text for h in hits], a)
                row["judge_score"] = v.score
                row["judge_reason"] = v.reason
            rows.append(row)

    if not rows:
        print("no /ask traffic recorded yet (the root span note is empty until /ask is built)")
        return 0
    print(f"{len(rows)} recent /ask requests, {sum(1 for r in rows if r['declined'])} declined\n")
    scored = [r for r in rows if "judge_score" in r]
    if scored:
        mean = sum(r["judge_score"] for r in scored) / len(scored)
        dist = {s: sum(1 for r in scored if r["judge_score"] == s) for s in range(1, 6)}
        print(f"judge mean {mean:.2f} over {len(scored)} answers; distribution {dist}\n")
        print("lowest scored, for a human to look at:")
        for r in sorted(scored, key=lambda r: r["judge_score"])[:5]:
            print(f"  [{r['judge_score']}] {r['question'][:60]}  ->  {r['answer'][:70]}")
            print(f"       {r['judge_reason'][:100]}")
    else:
        for r in rows[:20]:
            flag = "declined" if r["declined"] else "answered"
            print(f"  {flag:<9} {r['question'][:58]}  ->  {r['answer'][:60]}")
    (ROOT / "reports").mkdir(exist_ok=True)
    (ROOT / "reports" / "live-sample.json").write_text(json.dumps({"rows": rows}, indent=2))
    print("\nwrote reports/live-sample.json")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default=str(ROOT / "data" / "app.db"))
    ap.add_argument("--n", type=int, default=20)
    ap.add_argument(
        "--judge", action="store_true", help="score with the model-as-judge (costs tokens)"
    )
    args = ap.parse_args()
    os.environ["DATABASE_URL"] = f"sqlite:///{Path(args.db).as_posix()}"
    return asyncio.run(run(args.n, args.judge))


if __name__ == "__main__":
    sys.exit(main())
