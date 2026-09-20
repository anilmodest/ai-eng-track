import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlmodel import Session, select

from app.api.schemas import DocumentDetail, DocumentOut, JobOut
from app.db.models import Document, Job
from app.db.session import get_session
from app.ingest import UnsupportedType, parse
from app.jobs.queue import JobQueue, get_queue

router = APIRouter()

SessionDep = Annotated[Session, Depends(get_session)]
QueueDep = Annotated[JobQueue, Depends(get_queue)]


@router.post("/documents", response_model=DocumentOut, status_code=201)
async def upload_document(file: UploadFile, session: SessionDep) -> Document:
    data = await file.read()
    try:
        text = parse(file.filename or "", data)
    except UnsupportedType as e:
        raise HTTPException(status_code=415, detail=str(e)) from e
    doc = Document(
        filename=file.filename or "upload",
        content_type=file.content_type or "application/octet-stream",
        text=text,
        char_count=len(text),
        word_count=len(text.split()),
    )
    session.add(doc)
    session.commit()
    session.refresh(doc)
    return doc


@router.get("/documents", response_model=list[DocumentOut])
def list_documents(session: SessionDep) -> list[Document]:
    return list(session.exec(select(Document).order_by(Document.id)).all())  # type: ignore[arg-type]


@router.get("/documents/{doc_id}", response_model=DocumentDetail)
def get_document(doc_id: int, session: SessionDep) -> Document:
    doc = session.get(Document, doc_id)
    if doc is None:
        raise HTTPException(status_code=404, detail="document not found")
    return doc


@router.post("/jobs/reindex", response_model=JobOut, status_code=202)
async def reindex(session: SessionDep, queue: QueueDep) -> Job:
    """Kick off the slow batch job and return at once; the API stays responsive while it runs."""
    job = Job(id=uuid.uuid4().hex, kind="reindex_all")
    session.add(job)
    session.commit()
    session.refresh(job)
    await queue.enqueue("reindex_all", job.id)
    return job


@router.get("/jobs/{job_id}", response_model=JobOut)
def get_job(job_id: str, session: SessionDep) -> Job:
    job = session.get(Job, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="job not found")
    return job
