from datetime import UTC, datetime

from sqlmodel import Field, SQLModel


def _now() -> datetime:
    return datetime.now(UTC)


class Document(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    filename: str
    content_type: str
    text: str
    char_count: int
    word_count: int = 0
    created_at: datetime = Field(default_factory=_now)


class Extraction(SQLModel, table=True):
    """One model call's result, kept so the same work is never paid for twice (Week 1)."""

    id: int | None = Field(default=None, primary_key=True)
    document_id: int = Field(index=True, foreign_key="document.id")
    provider: str
    model: str
    prompt_version: str
    tokens_in: int
    tokens_out: int
    latency_ms: int
    cost_usd: float
    result_json: str
    created_at: datetime = Field(default_factory=_now)


class Job(SQLModel, table=True):
    id: str = Field(primary_key=True)
    kind: str
    status: str = "queued"  # queued | running | done | failed
    detail: str = ""
    created_at: datetime = Field(default_factory=_now)
    finished_at: datetime | None = None
