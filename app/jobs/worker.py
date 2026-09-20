"""arq worker: `make worker`. Exposes the same task functions the in-memory queue runs."""

from typing import Any

from arq.connections import RedisSettings

from app.jobs import tasks
from app.settings import get_settings


async def reindex_all(ctx: dict[str, Any], job_id: str) -> None:
    tasks.reindex_all(job_id)


class WorkerSettings:
    functions = [reindex_all]
    redis_settings = RedisSettings.from_dsn(get_settings().redis_url or "redis://localhost:6379")
