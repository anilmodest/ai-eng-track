"""Indexing and search, over whichever vector store is configured.

This file is deliberately thin. Everything that differs between stores lives in
`app/retrieval/vector_store.py`; everything above this line — the API, the evaluation, the agent —
only ever sees `index_documents`, `search` and `Hit`. That separation is what makes
`VECTOR_STORE=sqlite_vec` versus `VECTOR_STORE=qdrant` a measurement rather than an argument.
"""

from sqlmodel import Session, select

from app.retrieval.chunk_row import ChunkRow
from app.retrieval.embed import Embedder
from app.retrieval.vector_store import Hit, build_chunks, get_vector_store

__all__ = ["ChunkRow", "Hit", "chunk_count", "get_chunk", "index_documents", "search"]


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
) -> list[Hit]:
    """Nearest k chunks.

    `version` restricts the search to that version of the manual plus the pages that apply to
    every version. Leave it out and the search sees the whole corpus, which is how a question
    about version 3 comes back with a version 2 answer that reads perfectly.
    """
    query_vector = embedder.embed([query])[0]
    return get_vector_store().search(
        session, embedder, query_vector, k=k, strategy=strategy, version=version
    )


def get_chunk(session: Session, chunk_id: int) -> ChunkRow | None:
    return session.get(ChunkRow, chunk_id)
