"""Retry with exponential backoff, but only for failures that retrying can fix.

A 429 or a 500 may pass next time. A 400 never will: retrying it burns money and hides a bug.
"""

import asyncio
from collections.abc import Awaitable, Callable

from app.llm.client import ModelError, ModelTimeout


async def with_timeout[T](call: Awaitable[T], seconds: float) -> T:
    try:
        return await asyncio.wait_for(call, timeout=seconds)
    except TimeoutError as e:
        raise ModelTimeout(seconds) from e


async def with_retry[T](
    make_call: Callable[[], Awaitable[T]],
    *,
    attempts: int,
    base_delay_s: float,
    timeout_s: float,
) -> T:
    """Run make_call() up to `attempts` times. Each attempt gets its own timeout.

    Delays: base, 2*base, 4*base ... Only ModelError.retryable failures are retried.
    """
    last: ModelError | None = None
    for i in range(max(1, attempts)):
        try:
            return await with_timeout(make_call(), timeout_s)
        except ModelError as e:
            last = e
            if not e.retryable or i == attempts - 1:
                raise
            await asyncio.sleep(base_delay_s * (2**i))
    assert last is not None  # unreachable: the loop either returned or raised
    raise last
