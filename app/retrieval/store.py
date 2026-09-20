"""Chunks and their vectors live in SQLite next to the documents. Search is a cosine scan in numpy.

That is deliberate: for a few thousand chunks a scan is faster to reason about than a vector
database, and the interface (index, search, Hit) is the same one you would put in front of one.
"""

from dataclasses import dataclass

import numpy as np
from sqlmodel import Field, Session, SQLModel, col, delete, select

from app.db.models import Document
from app.retrieval.chunkers import chunk
from app.retrieval.embed import Embedder


class ChunkRow(SQLModel, table=True):
    __tablename__ = "chunk"

    id: int | None = Field(default=None, primary_key=True)
    document_id: int = Field(index=True, foreign_key="document.id")
    ordinal: int
    strategy: str = Field(index=True)
    embedder: str = Field(index=True)
    text: str
    embedding: bytes


@dataclass(frozen=True)
class Hit:
    chunk_id: int
    document_id: int
    filename: str
    ordinal: int
    text: str
    score: float


def index_documents(session: Session, embedder: Embedder, strategy: str) -> int:
    """(Re)build the index for one strategy + embedder over every document. Returns chunk count."""
    session.exec(
        delete(ChunkRow).where(
            col(ChunkRow.strategy) == strategy, col(ChunkRow.embedder) == embedder.name
        )
    )
    docs = session.exec(select(Document)).all()
    rows: list[ChunkRow] = []
    for doc in docs:
        assert doc.id is not None
        pieces = chunk(doc.text, strategy)
        if not pieces:
            continue
        vectors = embedder.embed(pieces)
        for i, (text, vec) in enumerate(zip(pieces, vectors, strict=True)):
            rows.append(
                ChunkRow(
                    document_id=doc.id,
                    ordinal=i,
                    strategy=strategy,
                    embedder=embedder.name,
                    text=text,
                    embedding=np.asarray(vec, dtype=np.float32).tobytes(),
                )
            )
    session.add_all(rows)
    session.commit()
    return len(rows)


def chunk_count(session: Session, strategy: str, embedder: Embedder) -> int:
    rows = session.exec(
        select(ChunkRow.id).where(ChunkRow.strategy == strategy, ChunkRow.embedder == embedder.name)
    ).all()
    return len(rows)


def search(session: Session, embedder: Embedder, query: str, *, k: int, strategy: str) -> list[Hit]:
    rows = session.exec(
        select(ChunkRow, Document.filename)
        .join(Document, col(Document.id) == col(ChunkRow.document_id))
        .where(ChunkRow.strategy == strategy, ChunkRow.embedder == embedder.name)
    ).all()
    if not rows:
        return []
    matrix = np.vstack([np.frombuffer(r.embedding, dtype=np.float32) for r, _ in rows])
    q = np.asarray(embedder.embed([query])[0], dtype=np.float32)
    qn = float(np.linalg.norm(q))
    if qn == 0:
        return []
    scores = matrix @ (q / qn)
    order = np.argsort(-scores)[:k]
    hits: list[Hit] = []
    for idx in order:
        row, filename = rows[int(idx)]
        assert row.id is not None
        hits.append(
            Hit(
                chunk_id=row.id,
                document_id=row.document_id,
                filename=filename,
                ordinal=row.ordinal,
                text=row.text,
                score=float(scores[int(idx)]),
            )
        )
    return hits


def get_chunk(session: Session, chunk_id: int) -> ChunkRow | None:
    return session.get(ChunkRow, chunk_id)
