"""Week 1, elaboration 1: the same prompt, five times. Watch the answers differ and the meter run.

    uv run python explore/w1_01_same_prompt_x5.py

Change nothing. Just read what comes back and note what varies: wording, facts, token counts, time.
"""

import asyncio
import time

from app.llm.client import Message
from app.llm.cost import estimate_cost_usd, price_known
from app.llm.registry import get_model_client

PROMPT = "In one sentence, what is the single most important property of a third-party API?"


async def main() -> None:
    client = get_model_client()
    print(f"provider={client.name} model={client.model}")
    if not price_known(client.model):
        print("(no list price known for this model; cost will show as 0)")
    print()
    total_cost = 0.0
    for i in range(5):
        t0 = time.perf_counter()
        r = await client.complete([Message(role="user", content=PROMPT)], json_mode=False)
        ms = int((time.perf_counter() - t0) * 1000)
        cost = estimate_cost_usd(r.model, r.tokens_in, r.tokens_out)
        total_cost += cost
        print(f"[{i + 1}] {ms:>5} ms  in={r.tokens_in:<4} out={r.tokens_out:<4} ${cost:.6f}")
        print(f"    {r.text.strip()}\n")
    print(f"five calls, one prompt, total ${total_cost:.6f}. were the answers the same?")


if __name__ == "__main__":
    asyncio.run(main())
