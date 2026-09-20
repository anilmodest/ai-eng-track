"""Week 2: one corpus, four chunking strategies, measured rather than argued about.

    uv run python scripts/retrieval_eval.py                # every strategy, embedder from .env
    uv run python scripts/retrieval_eval.py --k 3 --strategies sentence,heading

Loads corpus/ into a scratch database, indexes it once per strategy, runs the queries in
eval/retrieval-queries.jsonl and prints precision@k, recall@k, MRR and hit rate per strategy.
A hit is relevant when it comes from the expected document AND contains the expected phrase.
Writes reports/retrieval.json.
"""

import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CORPUS = ROOT / "corpus"
QUERIES = ROOT / "eval" / "retrieval-queries.jsonl"


def load_queries() -> list[dict[str, str]]:
    return [
        json.loads(line)
        for line in QUERIES.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--k", type=int, default=5)
    ap.add_argument("--strategies", default="fixed,sentence,paragraph,heading")
    ap.add_argument("--db", default=str(ROOT / "data" / "retrieval-eval.db"))
    args = ap.parse_args()

    os.environ["DATABASE_URL"] = f"sqlite:///{Path(args.db).as_posix()}"
    Path(args.db).unlink(missing_ok=True)
    from sqlmodel import Session, select

    from app.db.models import Document
    from app.db.session import get_engine
    from app.ingest import parse
    from app.retrieval.chunkers import chunk
    from app.retrieval.embed import get_embedder
    from app.retrieval.metrics import evaluate
    from app.retrieval.store import index_documents, search

    embedder = get_embedder()
    queries = load_queries()
    with Session(get_engine()) as session:
        if not session.exec(select(Document)).first():
            for path in sorted(CORPUS.iterdir()):
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
        docs = {d.filename: d for d in session.exec(select(Document)).all()}

        print(f"embedder={embedder.name}  k={args.k}  queries={len(queries)}\n")
        header = (
            f"{'strategy':<10} {'chunks':>6} {'avg chars':>9} "
            f"{'P@k':>6} {'R@k':>6} {'MRR':>6} {'hit':>6}"
        )
        print(header)
        print("-" * len(header))
        report: dict[str, dict[str, float | int]] = {}
        for strategy in args.strategies.split(","):
            n = index_documents(session, embedder, strategy)
            per_query: list[tuple[list[bool], int]] = []
            for q in queries:
                phrase = q["phrase"].lower()
                doc = docs[q["doc"]]
                total_relevant = sum(1 for c in chunk(doc.text, strategy) if phrase in c.lower())
                hits = search(session, embedder, q["q"], k=args.k, strategy=strategy)
                flags = [h.filename == q["doc"] and phrase in h.text.lower() for h in hits]
                per_query.append((flags, max(total_relevant, 1)))
            scores = evaluate(per_query, args.k)
            avg = int(
                sum(len(c) for d in docs.values() for c in chunk(d.text, strategy)) / max(n, 1)
            )
            print(
                f"{strategy:<10} {n:>6} {avg:>9} {scores.precision_at_k:>6.2f} "
                f"{scores.recall_at_k:>6.2f} {scores.mrr:>6.2f} {scores.hit_rate:>6.2f}"
            )
            report[strategy] = {
                "chunks": n,
                "avg_chars": avg,
                "precision_at_k": scores.precision_at_k,
                "recall_at_k": scores.recall_at_k,
                "mrr": scores.mrr,
                "hit_rate": scores.hit_rate,
            }
    (ROOT / "reports").mkdir(exist_ok=True)
    (ROOT / "reports" / "retrieval.json").write_text(
        json.dumps({"embedder": embedder.name, "k": args.k, "strategies": report}, indent=2)
    )
    print("\nwrote reports/retrieval.json. Pick a strategy with a number, then set CHUNK_STRATEGY.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
