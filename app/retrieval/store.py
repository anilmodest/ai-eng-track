"""Indexing and search, over whichever vector store is configured.

This file is deliberately thin. Everything that differs between stores lives in
`app/retrieval/vector_store.py`; everything above this line — the API, the evaluation, the agent —
only ever sees `index_documents`, `search` and `Hit`. That separation is what makes
`VECTOR_STORE=sqlite_vec` versus `VECTOR_STORE=qdrant` a measurement rather than an argument.
"""

import numpy as np
from sqlmodel import Session, select

from app.retrieval.chunk_row import ChunkRow
from app.retrieval.embed import Embedder
from app.retrieval.hybrid import bm25_scores, reciprocal_rank_fusion
from app.retrieval.vector_store import Hit, _hit, _rows_for, _wanted, build_chunks, get_vector_store

__all__ = ["MODES", "ChunkRow", "Hit", "chunk_count", "get_chunk", "index_documents", "search"]

# dense: meaning only (the vector store). hybrid: meaning and keywords, fused by rank.
MODES = ("dense", "hybrid")


def index_documents(session: Session, embedder: Embedder, strategy: str) -> int:
    """(Re)build the index for one strategy + embedder over every document. Returns chunk count."""
    store = get_vector_store()
    store.reset(session, strategy=strategy, embedder=embedder.name)
    pending = build_chunks(session, embedder, strategy)
    if pending:
        store.add(session, pending, strategy=strategy, embedder=embedder)
    return len(pending)


def chunk_count(session: Session, strategy: str, embedder: Embedder) -> int:
    rows = session.exec(
        select(ChunkRow.id).where(ChunkRow.strategy == strategy, ChunkRow.embedder == embedder.name)
    ).all()
    return len(rows)


def search(
    session: Session,
    embedder: Embedder,
    query: str,
    *,
    k: int,
    strategy: str,
    version: str | None = None,
    mode: str = "dense",
) -> list[Hit]:
    """The best k chunks.

    `version` restricts the search to that version of the manual plus the pages that apply to
    every version. Leave it out and the search sees the whole corpus, which is how a question
    about version 3 comes back with a version 2 answer that reads perfectly.

    `mode="hybrid"` runs keyword search (your bm25_scores) beside the vector store, both over the
    same version-filtered chunks, takes a deeper list from each, and fuses them by rank (your
    reciprocal_rank_fusion). Fusion sets the order; each hit's score stays its cosine.
    """
    if mode not in MODES:
        raise ValueError(f"unknown search mode {mode!r}; known: {', '.join(MODES)}")
    query_vector = embedder.embed([query])[0]
    depth = k if mode == "dense" else max(4 * k, 20)
    dense = get_vector_store().search(
        session, embedder, query_vector, k=depth, strategy=strategy, version=version
    )
    if mode == "dense":
        return dense[:k]

    rows = _rows_for(session, strategy, embedder.name)
    wanted = _wanted(version)
    if wanted is not None:
        rows = [(r, f) for r, f in rows if r.version in wanted]
    scores = bm25_scores(query, [r.text for r, _ in rows])
    order = sorted((i for i, s in enumerate(scores) if s > 0), key=lambda i: -scores[i])[:depth]
    keyword = [_hit(rows[i][0], rows[i][1], scores[i]) for i in order]

    fused = reciprocal_rank_fusion([[h.chunk_id for h in dense], [h.chunk_id for h in keyword]])
    chosen = [chunk_id for chunk_id, _ in fused[:k]]
    # Fusion decides the ORDER. The score a hit carries stays a cosine similarity, because week
    # 3's relevance threshold is one: a hit only keyword search found gets its cosine computed.
    cosine = {h.chunk_id: h.score for h in dense}
    missing = [h for h in keyword if h.chunk_id in chosen and h.chunk_id not in cosine]
    if missing:
        q = np.asarray(query_vector, dtype=np.float32)
        q = q / (float(np.linalg.norm(q)) or 1.0)
        for h, vec in zip(missing, embedder.embed([h.text for h in missing]), strict=True):
            v = np.asarray(vec, dtype=np.float32)
            cosine[h.chunk_id] = float(v @ q / (float(np.linalg.norm(v)) or 1.0))
    by_id = {h.chunk_id: h for h in keyword} | {h.chunk_id: h for h in dense}
    return [Hit(**{**by_id[c].__dict__, "score": cosine[c]}) for c in chosen]


def get_chunk(session: Session, chunk_id: int) -> ChunkRow | None:
    return session.get(ChunkRow, chunk_id)
