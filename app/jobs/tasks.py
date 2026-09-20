"""Job bodies. They run in-process or in the Redis worker; the code is the same either way."""

from datetime import UTC, datetime

from sqlmodel import Session, select

from app.db.models import Document, Job
from app.db.session import get_engine


def reindex_all(job_id: str) -> None:
    """Recount words for every document. Slow on purpose: it must not block the API."""
    with Session(get_engine()) as session:
        job = session.get(Job, job_id)
        if job is None:
            return
        job.status = "running"
        session.add(job)
        session.commit()
        count = 0
        for doc in session.exec(select(Document)).all():
            doc.word_count = len(doc.text.split())
            doc.char_count = len(doc.text)
            session.add(doc)
            count += 1
        job.status = "done"
        job.detail = f"reindexed {count} documents"
        job.finished_at = datetime.now(UTC)
        session.add(job)
        session.commit()
