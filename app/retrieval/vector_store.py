"""Where the vectors live. Three stores behind one interface, chosen by VECTOR_STORE.

The interface is the point. Swapping the store changes one setting and nothing else in the
service, which is what lets you answer the interview question "why this one?" with a measurement
instead of an opinion.

    numpy       Every chunk row read out of SQLite and compared in one cosine scan. No index, no
                extension, no service. Correct, and fine to a few thousand chunks. The baseline
                the others have to beat.
    sqlite_vec  A `vec0` virtual table in the same SQLite file. The version is a *partition key*,
                so the index is physically split by version and a version 3 query never looks at
                version 2 vectors. The default.
    qdrant      A real vector database, running from a local folder with no server. The same
                client talks to a hosted instance by changing one line, which is the week 6
                option if you want an index you do not host yourself.

A note on the version filter. Every store applies it *before* ranking, not after. Filtering
afterwards would let version 2 chunks take the top k slots and leave you with fewer version 3
hits than you asked for, which is a quiet way to lose recall.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any, ClassVar, Protocol

import numpy as np
from sqlmodel import Session, col, delete, select

from app.db.models import Document
from app.retrieval.chunk_row import ChunkRow
from app.retrieval.chunkers import chunk
from app.retrieval.embed import Embedder
from app.retrieval.versions import ANY_VERSION, applicable_versions

ROOT = Path(__file__).resolve().parent.parent.parent


@dataclass(frozen=True)
class Hit:
    chunk_id: int
    document_id: int
    filename: str
    ordinal: int
    text: str
    score: float
    version: str | None = None


@dataclass(frozen=True)
class PendingChunk:
    """One chunk on its way into a store."""

    document_id: int
    ordinal: int
    text: str
    version: str | None
    embedding: list[float]


class VectorStore(Protocol):
    name: str

    def reset(self, session: Session, *, strategy: str, embedder: str) -> None:
        """Drop everything held for this strategy and embedder."""

    def add(
        self, session: Session, chunks: list[PendingChunk], *, strategy: str, embedder: Embedder
    ) -> None:
        """Store these chunks."""

    def search(
        self,
        session: Session,
        embedder: Embedder,
        query_vector: list[float],
        *,
        k: int,
        strategy: str,
        version: str | None,
    ) -> list[Hit]:
        """Nearest k, filtered to `version` (and version-independent pages) when one is given."""


def _rows_for(session: Session, strategy: str, embedder: str) -> list[tuple[ChunkRow, str]]:
    result = session.exec(
        select(ChunkRow, Document.filename)
        .join(Document, col(Document.id) == col(ChunkRow.document_id))
        .where(ChunkRow.strategy == strategy, ChunkRow.embedder == embedder)
    ).all()
    return [(r, f) for r, f in result]


def _hit(row: ChunkRow, filename: str, score: float) -> Hit:
    assert row.id is not None
    return Hit(
        chunk_id=row.id,
        document_id=row.document_id,
        filename=filename,
        ordinal=row.ordinal,
        text=row.text,
        score=score,
        version=None if row.version == ANY_VERSION else row.version,
    )


def _wanted(version: str | None) -> set[str] | None:
    """No version asked for, no filter to apply. Otherwise the policy, from one place."""
    if version is None:
        return None
    return applicable_versions(version)


# --------------------------------------------------------------------------------------------


class NumpyStore:
    """One cosine scan over every chunk. The baseline: no index to go stale, nothing to install."""

    name = "numpy"

    def reset(self, session: Session, *, strategy: str, embedder: str) -> None:
        session.exec(
            delete(ChunkRow).where(
                col(ChunkRow.strategy) == strategy, col(ChunkRow.embedder) == embedder
            )
        )
        session.commit()

    def add(
        self, session: Session, chunks: list[PendingChunk], *, strategy: str, embedder: Embedder
    ) -> None:
        session.add_all(
            [
                ChunkRow(
                    document_id=c.document_id,
                    ordinal=c.ordinal,
                    strategy=strategy,
                    embedder=embedder.name,
                    version=c.version or ANY_VERSION,
                    text=c.text,
                    embedding=np.asarray(c.embedding, dtype=np.float32).tobytes(),
                )
                for c in chunks
            ]
        )
        session.commit()

    def search(
        self,
        session: Session,
        embedder: Embedder,
        query_vector: list[float],
        *,
        k: int,
        strategy: str,
        version: str | None,
    ) -> list[Hit]:
        rows = _rows_for(session, strategy, embedder.name)
        wanted = _wanted(version)
        if wanted is not None:
            rows = [(r, f) for r, f in rows if r.version in wanted]
        if not rows:
            return []
        matrix = np.vstack([np.frombuffer(r.embedding, dtype=np.float32) for r, _ in rows])
        q = np.asarray(query_vector, dtype=np.float32)
        norm = float(np.linalg.norm(q))
        if norm == 0:
            return []
        scores = matrix @ (q / norm)
        order = np.argsort(-scores)[:k]
        return [_hit(rows[int(i)][0], rows[int(i)][1], float(scores[int(i)])) for i in order]


class SqliteVecStore:
    """A `vec0` virtual table beside the data, partitioned by version.

    The partition key is the interesting part: sqlite-vec splits the index on it, so a version 3
    search does not scan version 2 vectors at all. It also means the filter is an equality, not a
    range, which is why a search for one version runs two queries (that version, and the pages
    that apply to every version) and merges them.
    """

    name = "sqlite_vec"

    # sqlite3.Connection takes no attributes of ours, so loaded connections are tracked here.
    _loaded: ClassVar[set[int]] = set()

    def _conn(self, session: Session) -> Any:
        raw = session.connection().connection
        conn = getattr(raw, "driver_connection", raw)
        if id(conn) not in self._loaded:
            import sqlite_vec

            conn.enable_load_extension(True)
            sqlite_vec.load(conn)
            conn.enable_load_extension(False)
            self._loaded.add(id(conn))
        return conn

    def _table(self, embedder: Embedder) -> str:
        return f"chunk_vec_{embedder.name}"

    def _ensure(self, session: Session, embedder: Embedder) -> str:
        table = self._table(embedder)
        self._conn(session).execute(
            f"create virtual table if not exists {table} using vec0("
            "  version text partition key,"
            "  chunk_id integer,"
            "  strategy text,"
            f"  embedding float[{embedder.dim}]"
            ")"
        )
        return table

    def reset(self, session: Session, *, strategy: str, embedder: str) -> None:
        session.exec(
            delete(ChunkRow).where(
                col(ChunkRow.strategy) == strategy, col(ChunkRow.embedder) == embedder
            )
        )
        session.commit()
        conn = self._conn(session)
        table = f"chunk_vec_{embedder}"
        exists = conn.execute(
            "select 1 from sqlite_master where type='table' and name=?", (table,)
        ).fetchone()
        if exists:
            conn.execute(f"delete from {table} where strategy = ?", (strategy,))
        session.commit()

    def add(
        self, session: Session, chunks: list[PendingChunk], *, strategy: str, embedder: Embedder
    ) -> None:
        import sqlite_vec

        rows = [
            ChunkRow(
                document_id=c.document_id,
                ordinal=c.ordinal,
                strategy=strategy,
                embedder=embedder.name,
                version=c.version or ANY_VERSION,
                text=c.text,
                embedding=b"",  # the vector lives in the vec0 table, not here
            )
            for c in chunks
        ]
        session.add_all(rows)
        session.commit()

        table = self._ensure(session, embedder)
        conn = self._conn(session)
        conn.executemany(
            f"insert into {table}(version, chunk_id, strategy, embedding) values (?, ?, ?, ?)",
            [
                (row.version, row.id, strategy, sqlite_vec.serialize_float32(c.embedding))
                for row, c in zip(rows, chunks, strict=True)
            ],
        )
        session.commit()

    def search(
        self,
        session: Session,
        embedder: Embedder,
        query_vector: list[float],
        *,
        k: int,
        strategy: str,
        version: str | None,
    ) -> list[Hit]:
        import sqlite_vec

        table = self._ensure(session, embedder)
        conn = self._conn(session)
        blob = sqlite_vec.serialize_float32(query_vector)
        wanted = _wanted(version)
        partitions: list[str | None] = list(sorted(wanted)) if wanted is not None else [None]

        found: dict[int, float] = {}
        for part in partitions:
            sql = (
                f"select chunk_id, distance from {table} "
                "where embedding match ? and k = ? and strategy = ?"
            )
            params: list[Any] = [blob, k, strategy]
            if part is not None:
                sql += " and version = ?"
                params.append(part)
            for chunk_id, distance in conn.execute(sql, params).fetchall():
                # vec0 reports L2 distance over unit vectors; smaller is nearer. Turn it back
                # into the cosine score the rest of the service compares against a threshold.
                score = 1.0 - (float(distance) ** 2) / 2.0
                found[int(chunk_id)] = max(found.get(int(chunk_id), -2.0), score)

        if not found:
            return []
        top = sorted(found.items(), key=lambda kv: -kv[1])[:k]
        by_id = {r.id: (r, f) for r, f in _rows_for(session, strategy, embedder.name)}
        hits = []
        for chunk_id, score in top:
            if chunk_id in by_id:
                row, filename = by_id[chunk_id]
                hits.append(_hit(row, filename, score))
        return hits


class QdrantStore:
    """A real vector database, from a local folder. The same client talks to a hosted instance.

    `QDRANT_URL` unset means embedded mode: Qdrant keeps its files under data/qdrant and there is
    nothing to run. Set it, and the identical code talks to a managed service. That one line is
    the whole difference, and it is worth running both to see what it costs you.
    """

    name = "qdrant"

    def __init__(self) -> None:
        self._client: Any = None

    def _qdrant(self) -> Any:
        if self._client is None:
            from qdrant_client import QdrantClient

            from app.settings import get_settings

            url = get_settings().qdrant_url
            if url:
                self._client = QdrantClient(url=url)
            else:
                path = ROOT / "data" / "qdrant"
                path.mkdir(parents=True, exist_ok=True)
                self._client = QdrantClient(path=str(path))
        return self._client

    def _collection(self, session: Session, embedder: Embedder) -> str:
        from qdrant_client import models

        name = f"chunks_{embedder.name}"
        client = self._qdrant()
        if not client.collection_exists(name):
            client.create_collection(
                collection_name=name,
                vectors_config=models.VectorParams(
                    size=embedder.dim, distance=models.Distance.COSINE
                ),
            )
        return name

    def reset(self, session: Session, *, strategy: str, embedder: str) -> None:
        from qdrant_client import models

        session.exec(
            delete(ChunkRow).where(
                col(ChunkRow.strategy) == strategy, col(ChunkRow.embedder) == embedder
            )
        )
        session.commit()
        client = self._qdrant()
        name = f"chunks_{embedder}"
        if client.collection_exists(name):
            client.delete(
                collection_name=name,
                points_selector=models.FilterSelector(
                    filter=models.Filter(
                        must=[
                            models.FieldCondition(
                                key="strategy", match=models.MatchValue(value=strategy)
                            )
                        ]
                    )
                ),
            )

    def add(
        self, session: Session, chunks: list[PendingChunk], *, strategy: str, embedder: Embedder
    ) -> None:
        from qdrant_client import models

        rows = [
            ChunkRow(
                document_id=c.document_id,
                ordinal=c.ordinal,
                strategy=strategy,
                embedder=embedder.name,
                version=c.version or ANY_VERSION,
                text=c.text,
                embedding=b"",
            )
            for c in chunks
        ]
        session.add_all(rows)
        session.commit()

        name = self._collection(session, embedder)
        self._qdrant().upsert(
            collection_name=name,
            points=[
                models.PointStruct(
                    id=int(row.id or 0),
                    vector=c.embedding,
                    payload={"version": row.version, "strategy": strategy},
                )
                for row, c in zip(rows, chunks, strict=True)
            ],
        )

    def search(
        self,
        session: Session,
        embedder: Embedder,
        query_vector: list[float],
        *,
        k: int,
        strategy: str,
        version: str | None,
    ) -> list[Hit]:
        from qdrant_client import models

        name = self._collection(session, embedder)
        must: list[Any] = [
            models.FieldCondition(key="strategy", match=models.MatchValue(value=strategy))
        ]
        wanted = _wanted(version)
        if wanted is not None:
            must.append(
                models.FieldCondition(key="version", match=models.MatchAny(any=sorted(wanted)))
            )
        points = (
            self._qdrant()
            .query_points(
                collection_name=name,
                query=query_vector,
                limit=k,
                query_filter=models.Filter(must=must),
            )
            .points
        )
        by_id = {r.id: (r, f) for r, f in _rows_for(session, strategy, embedder.name)}
        hits = []
        for point in points:
            entry = by_id.get(int(point.id))
            if entry is not None:
                hits.append(_hit(entry[0], entry[1], float(point.score)))
        return hits


_STORES: dict[str, VectorStore] = {}


def get_vector_store(name: str | None = None) -> VectorStore:
    from app.settings import get_settings

    key = name or get_settings().vector_store
    if key not in _STORES:
        builders: dict[str, Any] = {
            "numpy": NumpyStore,
            "sqlite_vec": SqliteVecStore,
            "qdrant": QdrantStore,
        }
        if key not in builders:
            raise ValueError(f"unknown VECTOR_STORE {key!r}: one of {', '.join(sorted(builders))}")
        _STORES[key] = builders[key]()
    return _STORES[key]


def build_chunks(session: Session, embedder: Embedder, strategy: str) -> list[PendingChunk]:
    """Chunk every document and embed the pieces. Store-independent."""
    pending: list[PendingChunk] = []
    for doc in session.exec(select(Document)).all():
        assert doc.id is not None
        pieces = chunk(doc.text, strategy)
        if not pieces:
            continue
        vectors = embedder.embed(pieces)
        for i, (text, vec) in enumerate(zip(pieces, vectors, strict=True)):
            pending.append(
                PendingChunk(
                    document_id=doc.id,
                    ordinal=i,
                    text=text,
                    version=doc.version,
                    embedding=list(vec),
                )
            )
    return pending
