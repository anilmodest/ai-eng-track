"""Week 2: three chunking strategies, each with meaning search alone and with hybrid search.

    uv run python scripts/retrieval_eval.py                # six configurations, embedder from .env
    uv run python scripts/retrieval_eval.py --k 3 --strategies paragraph,section --modes hybrid

Loads the whole corpus into a scratch database, indexes it once per strategy, and runs every
query in eval/starter-questions.jsonl (the thirty manual questions, each about one version) and
eval/retrieval-queries.jsonl (the business documents). A manual question is searched with its
version, as the agent will search; a hit is relevant when it comes from the expected document AND
contains the expected phrase.

Per configuration: precision@k, recall@k, MRR, hit rate, and three numbers for the decision:
    version_trap   how often the TOP hit is the wrong version when the same manual question is
                   searched with NO version: what the filter is protecting you from
    context_tokens how much text k hits put in front of the model per question, roughly: the
                   cost side of choosing k and the strategy
    p95_ms         how long one search took, 95th percentile: hybrid search does more work

Writes reports/retrieval.json; `make evidence WEEK=2` keeps it.
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
QUERY_FILES = [ROOT / "eval" / "starter-questions.jsonl", ROOT / "eval" / "retrieval-queries.jsonl"]


def load_queries() -> list[dict[str, str]]:
    return [
        json.loads(line)
        for path in QUERY_FILES
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--k", type=int, default=5)
    ap.add_argument("--strategies", default="paragraph,heading,section")
    ap.add_argument("--modes", default="dense,hybrid")
    ap.add_argument("--db", default=str(ROOT / "data" / "retrieval-eval.db"))
    args = ap.parse_args()

    os.environ["DATABASE_URL"] = f"sqlite:///{Path(args.db).as_posix()}"
    Path(args.db).unlink(missing_ok=True)
    from sqlmodel import Session, select

    from app.db.models import Document
    from app.db.session import get_engine
    from app.ingest import parse
    from app.ingest.corpus import corpus_paths
    from app.retrieval.chunkers import chunk
    from app.retrieval.embed import get_embedder
    from app.retrieval.metrics import evaluate
    from app.retrieval.store import index_documents, search
    from app.retrieval.versions import version_of
    from app.run_mode import run_mode

    embedder = get_embedder()
    queries = load_queries()
    with Session(get_engine()) as session:
        for path in corpus_paths():
            text = parse(path.name, path.read_bytes())
            session.add(
                Document(
                    filename=path.name,
                    version=version_of(path.name),
                    content_type="text/plain",
                    text=text,
                    char_count=len(text),
                    word_count=len(text.split()),
                )
            )
        session.commit()
        docs = {d.filename: d for d in session.exec(select(Document)).all()}

        print(f"embedder={embedder.name}  k={args.k}  queries={len(queries)}  docs={len(docs)}\n")
        header = (
            f"{'configuration':<18} {'chunks':>6} {'P@k':>6} {'R@k':>6} {'MRR':>6} {'hit':>6} "
            f"{'trap':>6} {'ctx tok':>8} {'p95 ms':>7}"
        )
        print(header)
        print("-" * len(header))
        configs: dict[str, dict[str, Any]] = {}
        for strategy in args.strategies.split(","):
            n = index_documents(session, embedder, strategy)
            for mode in args.modes.split(","):
                per_query: list[tuple[list[bool], int]] = []
                trapped = versioned = context_chars = 0
                timings: list[float] = []
                for q in queries:
                    phrase = q["phrase"].lower()
                    doc = docs[q["doc"]]
                    relevant = sum(1 for c in chunk(doc.text, strategy) if phrase in c.lower())
                    version = q.get("version")
                    started = time.perf_counter()
                    hits = search(
                        session,
                        embedder,
                        q["q"],
                        k=args.k,
                        strategy=strategy,
                        version=version,
                        mode=mode,
                    )
                    timings.append((time.perf_counter() - started) * 1000)
                    flags = [h.filename == q["doc"] and phrase in h.text.lower() for h in hits]
                    per_query.append((flags, max(relevant, 1)))
                    context_chars += sum(len(h.text) for h in hits)
                    if version:
                        versioned += 1
                        top = search(session, embedder, q["q"], k=1, strategy=strategy, mode=mode)
                        trapped += int(bool(top) and top[0].version not in (version, None))
                s = evaluate(per_query, args.k)
                name = f"{strategy}+{mode}"
                configs[name] = {
                    "strategy": strategy,
                    "mode": mode,
                    "chunks": n,
                    "precision_at_k": s.precision_at_k,
                    "recall_at_k": s.recall_at_k,
                    "mrr": s.mrr,
                    "hit_rate": s.hit_rate,
                    "version_trap": round(trapped / versioned, 3) if versioned else 0.0,
                    "context_tokens": int(context_chars / 4 / max(len(queries), 1)),
                    "p95_ms": round(sorted(timings)[int(0.95 * (len(timings) - 1))], 1),
                }
                c = configs[name]
                print(
                    f"{name:<18} {n:>6} {c['precision_at_k']:>6.2f} {c['recall_at_k']:>6.2f} "
                    f"{c['mrr']:>6.2f} {c['hit_rate']:>6.2f} {c['version_trap']:>6.2f} "
                    f"{c['context_tokens']:>8} {c['p95_ms']:>7.1f}"
                )

    (ROOT / "reports").mkdir(exist_ok=True)
    report = {**run_mode(), "embedder": embedder.name, "k": args.k, "configs": configs}
    (ROOT / "reports" / "retrieval.json").write_text(json.dumps(report, indent=2))
    print("\nwrote reports/retrieval.json. Choose a configuration and a k with a number.")
    print("Then set CHUNK_STRATEGY and SEARCH_MODE in .env.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
