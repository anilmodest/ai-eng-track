"""Two queues, one interface. REDIS_URL decides which one runs; the API never knows."""

import asyncio
from typing import Any, Protocol

from arq import create_pool
from arq.connections import RedisSettings

from app.jobs import tasks
from app.settings import get_settings


class JobQueue(Protocol):
    async def enqueue(self, kind: str, job_id: str) -> None: ...


class InMemoryQueue:
    """Runs the job on a worker thread inside the API process. Fine for dev and tests."""

    def __init__(self) -> None:
        self.tasks: set[asyncio.Task[None]] = set()

    async def enqueue(self, kind: str, job_id: str) -> None:
        fn = getattr(tasks, kind)
        task = asyncio.create_task(asyncio.to_thread(fn, job_id))
        self.tasks.add(task)
        task.add_done_callback(self.tasks.discard)

    async def drain(self) -> None:
        if self.tasks:
            await asyncio.gather(*self.tasks)


class RedisQueue:
    def __init__(self, url: str) -> None:
        self.url = url
        self._pool: Any = None

    async def enqueue(self, kind: str, job_id: str) -> None:
        if self._pool is None:
            self._pool = await create_pool(RedisSettings.from_dsn(self.url))
        await self._pool.enqueue_job(kind, job_id)


_queue: JobQueue | None = None


def get_queue() -> JobQueue:
    global _queue
    if _queue is None:
        url = get_settings().redis_url
        _queue = RedisQueue(url) if url else InMemoryQueue()
    return _queue


def reset_queue() -> None:
    global _queue
    _queue = None
