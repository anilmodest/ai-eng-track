"""Week 2, Area 3: a working pipeline degraded on purpose by adding context, then repaired by
removing it.

    uv run python scripts/degrade_repair.py                 # provider from .env
    MODEL_PROVIDER=fake_a EMBED_PROVIDER=hash uv run python scripts/degrade_repair.py

Three ways to answer each of the 30 retrieval queries:
    top3       the top 3 chunks, as retrieved                 (works)
    stuffed    every chunk in the store, every time            (degraded: cost, often the answer)
    repaired   the top 10, passed through select_and_compress  (your fix)

Per mode: how many answers held the expected phrase, mean tokens in, total cost, mean latency.
Writes reports/degrade.json. With the fake model the cost column moves and the hit column may
not; with a real model, watch both.
"""

import argparse
import asyncio
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
QUERIES = ROOT / "eval" / "retrieval-queries.jsonl"


async def run(budget: int) -> int:
    from sqlmodel import Session, select

    from app.db.models import Document
    from app.db.session import get_engine
    from app.ingest import parse
    from app.llm.registry import get_model_client
    from app.retrieval.context import answer_from_context, select_and_compress
    from app.retrieval.embed import get_embedder
    from app.retrieval.store import ChunkRow, index_documents, search
    from app.settings import get_settings

    settings = get_settings()
    client = get_model_client()
    embedder = get_embedder()
    queries = [json.loads(ln) for ln in QUERIES.read_text(encoding="utf-8").splitlines() if ln]
    report: dict[str, Any] = {}
    with Session(get_engine()) as session:
        for path in sorted((ROOT / "corpus").iterdir()):
            text = parse(path.name, path.read_bytes())
            session.add(
                Document(
                    filename=path.name,
                    content_type="text/plain",
                    text=text,
                    char_count=len(text),
                    word_count=len(text.split()),
                )
            )
        session.commit()
        strategy = settings.chunk_strategy
        index_documents(session, embedder, strategy)
        every = [
            r.text
            for r in session.exec(
                select(ChunkRow).where(
                    ChunkRow.strategy == strategy, ChunkRow.embedder == embedder.name
                )
            ).all()
        ]
        print(
            f"provider={client.name} embedder={embedder.name} strategy={strategy} "
            f"chunks={len(every)} budget={budget} chars\n"
        )
        header = f"{'mode':<9} {'hits':>7} {'mean tok_in':>12} {'total $':>9} {'mean ms':>8}"
        print(header)
        print("-" * len(header))
        for mode in ("top3", "stuffed", "repaired"):
            hits_n = 0
            tokens = 0
            cost = 0.0
            ms_total = 0
            for q in queries:
                ranked = search(session, embedder, q["q"], k=10, strategy=strategy)
                if mode == "top3":
                    passages = [h.text for h in ranked[:3]]
                elif mode == "stuffed":
                    passages = every
                else:
                    passages = select_and_compress(q["q"], ranked, budget)
                t0 = time.perf_counter()
                try:
                    ans, t_in, c = await answer_from_context(client, settings, q["q"], passages)
                except Exception as e:  # a provider failure is a data point here, not a crash
                    print(f"  {mode} {q['q'][:40]!r}: {type(e).__name__}: {str(e)[:60]}")
                    continue
                ms_total += int((time.perf_counter() - t0) * 1000)
                tokens += t_in
                cost += c
                if ans.grounded and q["phrase"].lower() in ans.answer.lower():
                    hits_n += 1
            n = len(queries)
            print(f"{mode:<9} {hits_n:>3}/{n:<3} {tokens // n:>12} {cost:>9.5f} {ms_total // n:>8}")
            report[mode] = {
                "hits": hits_n,
                "of": n,
                "mean_tokens_in": tokens // n,
                "total_cost_usd": round(cost, 6),
                "mean_latency_ms": ms_total // n,
            }
    (ROOT / "reports").mkdir(exist_ok=True)
    (ROOT / "reports" / "degrade.json").write_text(json.dumps(report, indent=2))
    print(
        "\nwrote reports/degrade.json. Same questions, same corpus: what did the extra context buy?"
    )
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--budget", type=int, default=1200, help="characters select_and_compress may return"
    )
    ap.add_argument("--db", default=str(ROOT / "data" / "degrade.db"))
    args = ap.parse_args()
    os.environ["DATABASE_URL"] = f"sqlite:///{Path(args.db).as_posix()}"
    Path(args.db).unlink(missing_ok=True)
    return asyncio.run(run(args.budget))


if __name__ == "__main__":
    sys.exit(main())
