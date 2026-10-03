"""The chunk table: the text and its metadata, whatever store holds the vectors.

Kept apart from the stores so that every store writes the same rows. The `version` column is the
one the search filters on, and it is indexed because that filter runs on every query.
"""

from sqlmodel import Field, SQLModel


class ChunkRow(SQLModel, table=True):
    __tablename__ = "chunk"

    id: int | None = Field(default=None, primary_key=True)
    document_id: int = Field(index=True, foreign_key="document.id")
    ordinal: int
    strategy: str = Field(index=True)
    embedder: str = Field(index=True)
    version: str = Field(default="any", index=True)
    text: str
    # Only the numpy store keeps the vector here. The others store it in their own index and
    # leave this empty, which is why nothing outside that store should read it.
    embedding: bytes = b""
