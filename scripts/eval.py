"""Week 3: run the golden set through /ask and gate on the numbers.

    uv run python scripts/eval.py                   # thresholds from eval/thresholds.json
    uv run python scripts/eval.py --judge           # add model-as-judge scoring (costs tokens)
    uv run python scripts/eval.py --min-hit 0.9     # override one threshold
    uv run python scripts/eval.py --thresholds eval/thresholds-ci.json --corpus core  # CI
    uv run python scripts/eval.py --set eval/my-test-set.jsonl   # your own 100 questions

Loads corpus/ into a scratch database, indexes with CHUNK_STRATEGY, asks every golden question,
and reports four task-specific metrics:

    abstain_rate_unanswerable   of questions the corpus cannot answer, how many did we decline?
    answer_rate_answerable      of questions it can answer, how many did we answer?
    hit_rate                    of answered answerable questions, how many held the expected fact?
    citation_validity           of answers, how many cited a chunk from the expected document?
    answer_accuracy             of answerable questions, how many were answered with the fact?

A set whose rows carry `kind` (straightforward | no_answer | version, as your own set does) also
gets each kind's accuracy or decline rate. `--corpus core` loads only the hand-written pages, which
the programme's golden set was written against; the default loads the whole corpus.

Exit code 1 if any metric is under its threshold. That is the CI gate. Writes reports/eval.json.
"""

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
GOLDEN = ROOT / "eval" / "golden.jsonl"
THRESHOLDS = ROOT / "eval" / "thresholds.json"  # the real bar; CI uses thresholds-ci.json


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(ln) for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]


async def run(
    args: argparse.Namespace, golden: list[dict[str, Any]], thresholds: dict[str, float]
) -> int:
    from httpx import ASGITransport, AsyncClient

    from app.ingest.corpus import corpus_paths
    from app.main import app
    from app.settings import get_settings

    rows: list[dict[str, Any]] = []
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://eval") as api:
        for path in corpus_paths(generated=args.corpus == "all"):
            r = await api.post("/documents", files={"file": (path.name, path.read_bytes())})
            assert r.status_code == 201, r.text
        r = await api.post("/index")
        assert r.status_code == 200, r.text
        print(
            f"indexed {r.json()['chunks']} chunks with strategy={r.json()['strategy']} "
            f"embedder={r.json()['embedder']}  threshold={get_settings().relevance_threshold}\n"
        )

        for g in golden:
            # The support desk always knows which version the customer runs, and so does the
            # test set. Leaving it out is how an evaluation quietly stops measuring O1.
            payload: dict[str, Any] = {"question": g["q"]}
            if g.get("version"):
                payload["version"] = g["version"]
            resp = await api.post("/ask", json=payload)
            if resp.status_code != 200:
                rows.append({**g, "error": resp.json()})
                continue
            out = resp.json()
            expect = g.get("expect")
            answered = not out["abstained"]
            hit = bool(answered and expect and expect.lower() in (out["answer"] or "").lower())
            cited_ok = bool(
                answered and any(c["filename"] == g.get("doc") for c in out["citations"])
            )
            rows.append(
                {
                    **g,
                    "answered": answered,
                    "hit": hit,
                    "cited_ok": cited_ok,
                    "top_score": out.get("top_score"),
                    "cost_usd": out.get("cost_usd", 0.0),
                    "answer": out.get("answer"),
                    "cited": [c["text"] for c in out["citations"]],
                }
            )

        if args.judge:
            from app.eval.judge import judge_rows

            await judge_rows(rows)

    answerable = [r for r in rows if r["answerable"] and "error" not in r]
    unanswerable = [r for r in rows if not r["answerable"] and "error" not in r]
    answered_rows = [r for r in answerable if r["answered"]]
    metrics: dict[str, float] = {
        "abstain_rate_unanswerable": _rate([not r["answered"] for r in unanswerable]),
        "answer_rate_answerable": _rate([r["answered"] for r in answerable]),
        "hit_rate": _rate([r["hit"] for r in answered_rows]),
        "citation_validity": _rate([r["cited_ok"] for r in answered_rows]),
        "total_cost_usd": round(sum(r.get("cost_usd", 0.0) for r in rows), 6),
        "errors": sum(1 for r in rows if "error" in r),
    }
    metrics["answer_accuracy"] = _rate([bool(r.get("hit")) for r in answerable])
    kinds = sorted({str(r["kind"]) for r in rows if r.get("kind")})
    for kind in kinds:
        of_kind = [r for r in rows if r.get("kind") == kind and "error" not in r]
        if kind == "no_answer":
            metrics["decline_rate_no_answer"] = _rate([not r["answered"] for r in of_kind])
        else:
            metrics[f"accuracy_{kind}"] = _rate([bool(r.get("hit")) for r in of_kind])
    if args.judge:
        scored = [r["judge_score"] for r in rows if "judge_score" in r]
        metrics["judge_mean"] = round(sum(scored) / len(scored), 2) if scored else 0.0
        verdicts = [r["judge_faithful"] for r in rows if "judge_faithful" in r]
        metrics["judge_faithful_rate"] = _rate(verdicts)

    gates = {
        "abstain_rate_unanswerable": metrics["abstain_rate_unanswerable"]
        >= thresholds["min_abstain"],
        "answer_rate_answerable": metrics["answer_rate_answerable"] >= thresholds["min_answer"],
        "hit_rate": metrics["hit_rate"] >= thresholds["min_hit"],
        "citation_validity": metrics["citation_validity"] >= thresholds["min_citation"],
    }
    print(f"{'metric':<28} {'value':>7} {'threshold':>10}  verdict")
    print("-" * 58)
    for name, ok in gates.items():
        key = {
            "abstain_rate_unanswerable": "min_abstain",
            "answer_rate_answerable": "min_answer",
            "hit_rate": "min_hit",
            "citation_validity": "min_citation",
        }[name]
        print(
            f"{name:<28} {metrics[name]:>7.2f} {thresholds[key]:>10.2f}  {'PASS' if ok else 'FAIL'}"
        )
    print(f"{'total_cost_usd':<28} {metrics['total_cost_usd']:>7.4f}")
    errors_ok = "PASS" if not metrics["errors"] else "FAIL"
    print(f"{'errors (non-200 from /ask)':<28} {int(metrics['errors']):>7}  {errors_ok}")
    for row in rows:
        if "error" in row:
            print(f"  {row['id']}  {row['q'][:50]}  ->  {row['error']}")
    if args.judge:
        print(f"{'judge_mean (1-5)':<28} {metrics['judge_mean']:>7.2f}")

    failures = [
        r
        for r in rows
        if (r["answerable"] and r.get("answered") and not r.get("hit"))
        or (not r["answerable"] and r.get("answered"))
    ]
    if failures:
        print("\nworth a look:")
        for row in failures[:10]:
            kind = "answered an unanswerable" if not row["answerable"] else "missed the fact"
            answer = " ".join(str(row.get("answer")).split())[:80]
            print(f"  {row['id']}  {kind}: {row['q'][:60]}  ->  {answer}")

    from app.run_mode import run_mode

    out_path = Path(args.out)
    out_path.parent.mkdir(exist_ok=True)
    out_path.write_text(  # noqa: ASYNC240 (once, at the end of a script)
        json.dumps(
            {
                **run_mode(),
                "metrics": metrics,
                "thresholds": thresholds,
                "gates": gates,
                "rows": rows,
            },
            indent=2,
        )
    )
    ok = all(gates.values()) and metrics["errors"] == 0
    print(f"\n{'GATE PASS' if ok else 'GATE FAIL'}  ({out_path.name})")
    return 0 if ok else 1


def _normalise(row: dict[str, Any]) -> dict[str, Any]:
    """Your own set says `kind`; the golden set says `answerable`. Both mean the same here."""
    if "answerable" not in row and "kind" in row:
        row = {**row, "answerable": row["kind"] != "no_answer"}
    return row


def _rate(flags: list[bool]) -> float:
    return round(sum(flags) / len(flags), 4) if flags else 0.0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--judge", action="store_true")
    ap.add_argument("--thresholds", default=str(THRESHOLDS))
    ap.add_argument("--min-abstain", dest="min_abstain", type=float)
    ap.add_argument("--min-answer", dest="min_answer", type=float)
    ap.add_argument("--min-hit", dest="min_hit", type=float)
    ap.add_argument("--min-citation", dest="min_citation", type=float)
    ap.add_argument("--db", default=str(ROOT / "data" / "eval.db"))
    ap.add_argument("--set", default=str(GOLDEN), help="the questions: golden.jsonl or your own")
    ap.add_argument("--corpus", choices=["all", "core"], default="all")
    ap.add_argument("--out", default=str(ROOT / "reports" / "eval.json"))
    args = ap.parse_args()
    os.environ["DATABASE_URL"] = f"sqlite:///{Path(args.db).as_posix()}"
    Path(args.db).unlink(missing_ok=True)
    golden = [_normalise(r) for r in load_jsonl(Path(args.set))]
    thresholds: dict[str, float] = json.loads(Path(args.thresholds).read_text(encoding="utf-8"))
    for key in ("min_abstain", "min_answer", "min_hit", "min_citation"):
        override = getattr(args, key)
        if override is not None:
            thresholds[key] = override
    return asyncio.run(run(args, golden, thresholds))


if __name__ == "__main__":
    sys.exit(main())
