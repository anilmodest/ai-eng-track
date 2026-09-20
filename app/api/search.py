"""Week 2: index the documents and search them. Strategy and embedder come from configuration."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlmodel import Session

from app.db.session import get_session
from app.retrieval.chunkers import STRATEGIES
from app.retrieval.embed import Embedder, get_embedder
from app.retrieval.store import index_documents, search
from app.settings import Settings, get_settings

router = APIRouter()

SessionDep = Annotated[Session, Depends(get_session)]
EmbedderDep = Annotated[Embedder, Depends(get_embedder)]
SettingsDep = Annotated[Settings, Depends(get_settings)]


class IndexOut(BaseModel):
    strategy: str
    embedder: str
    chunks: int


class HitOut(BaseModel):
    chunk_id: int
    document_id: int
    filename: str
    ordinal: int
    score: float
    text: str


@router.post("/index", response_model=IndexOut)
def index(
    session: SessionDep,
    embedder: EmbedderDep,
    settings: SettingsDep,
    strategy: str | None = None,
) -> IndexOut:
    strategy = strategy or settings.chunk_strategy
    if strategy not in STRATEGIES:
        raise HTTPException(status_code=400, detail=f"unknown strategy {strategy!r}")
    n = index_documents(session, embedder, strategy)
    return IndexOut(strategy=strategy, embedder=embedder.name, chunks=n)


@router.get("/search", response_model=list[HitOut])
def search_endpoint(
    session: SessionDep,
    embedder: EmbedderDep,
    settings: SettingsDep,
    q: Annotated[str, Query(min_length=1)],
    k: int | None = None,
    strategy: str | None = None,
) -> list[HitOut]:
    hits = search(
        session,
        embedder,
        q,
        k=k or settings.search_k,
        strategy=strategy or settings.chunk_strategy,
    )
    return [HitOut(**h.__dict__) for h in hits]
