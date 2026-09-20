"""Week 1, elaboration 2: make the dependency fail, then watch the retry helper cope.

    uv run python explore/w1_02_break_it.py

Part A uses the scripted fake, so it runs with no key: 429, 429, then success, with backoff.
Part B uses your real provider with a 0.05 s timeout. It will fail. That is the point.
"""

import asyncio
import time

from app.llm.client import Message, ModelError
from app.llm.providers.fake import FakeClient
from app.llm.registry import get_model_client
from app.llm.retry import with_retry

PROMPT = [Message(role="user", content="Say 'ok'.")]


async def part_a() -> None:
    print("A. scripted failures: 429, 429, ok, with retry")
    fake = FakeClient(script="429,429,ok")
    t0 = time.perf_counter()
    r = await with_retry(lambda: fake.complete(PROMPT), attempts=3, base_delay_s=0.5, timeout_s=5)
    print(
        f"   {fake.calls} calls, {time.perf_counter() - t0:.2f}s (0.5 + 1.0 backoff), "
        f"text={r.text[:40]!r}"
    )

    print("A2. a 400 must NOT be retried")
    fake = FakeClient(script="400,ok")
    try:
        await with_retry(lambda: fake.complete(PROMPT), attempts=3, base_delay_s=0.5, timeout_s=5)
    except ModelError as e:
        print(f"   gave up after {fake.calls} call: {e} (retryable={e.retryable})")


async def part_b() -> None:
    print("\nB. real provider with an impossible timeout (0.05 s)")
    client = get_model_client()
    t0 = time.perf_counter()
    try:
        await with_retry(
            lambda: client.complete(PROMPT, json_mode=False),
            attempts=2,
            base_delay_s=0.2,
            timeout_s=0.05,
        )
        print("   it answered in under 50 ms?! run it again.")
    except ModelError as e:
        print(f"   {e} after {time.perf_counter() - t0:.2f}s; retryable={e.retryable}")
    print("   now with a sane timeout (20 s):")
    r = await with_retry(
        lambda: client.complete(PROMPT, json_mode=False), attempts=2, base_delay_s=0.2, timeout_s=20
    )
    print(f"   {r.provider}/{r.model}: {r.text.strip()[:60]!r}")


async def main() -> None:
    await part_a()
    try:
        await part_b()
    except Exception as e:  # noqa: BLE001 - explore scripts report, they do not handle
        print(f"   part B skipped: {e}")


if __name__ == "__main__":
    asyncio.run(main())
