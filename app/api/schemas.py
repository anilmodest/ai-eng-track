from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class DocumentOut(BaseModel):
    id: int
    filename: str
    content_type: str
    char_count: int
    word_count: int
    created_at: datetime


class DocumentDetail(DocumentOut):
    text: str


class JobOut(BaseModel):
    id: str
    kind: str
    status: str
    detail: str


class ErrorOut(BaseModel):
    """Every non-2xx body has this shape. `error` is a stable code, `detail` is for humans."""

    error: str
    detail: str


# ---- Week 1: the contract the model must satisfy -------------------------------------------

DocType = Literal["invoice", "contract", "report", "letter", "other"]


class DocumentExtract(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    doc_type: DocType
    summary: str
    key_facts: list[str] = Field(min_length=3, max_length=5)
    confidence: float = Field(ge=0.0, le=1.0)

    @field_validator("summary")
    @classmethod
    def summary_at_most_60_words(cls, v: str) -> str:
        if len(v.split()) > 60:
            raise ValueError("summary must be at most 60 words")
        return v


class GuardOut(BaseModel):
    injection_detected: bool = False
    patterns: list[str] = []
    stripped_lines: int = 0
    output_flags: list[str] = []


class ExtractOut(BaseModel):
    document_id: int
    cached: bool
    provider: str
    model: str
    prompt_version: str
    tokens_in: int
    tokens_out: int
    latency_ms: int
    cost_usd: float
    extract: DocumentExtract
    guard: GuardOut | None = None
