"""Week 4, elaboration 1: one question, three ways, and the agent's every step on screen.

    uv run python explore/w4_01_watch_the_agent_think.py ["your question"]

Needs a real provider (the agent path spends a few calls). Plain code answers instantly or
declines; the workflow does its fixed steps; the agent decides as it goes. Read the agent's
transcript: which tools did it pick, in what order, and did it stop when it had the answer?
"""

import asyncio
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_Q = "Which invoice has the largest total due, and what is it?"


async def main() -> None:
    os.environ["DATABASE_URL"] = f"sqlite:///{(ROOT / 'data' / 'explore-w4.db').as_posix()}"
    (ROOT / "data" / "explore-w4.db").unlink(missing_ok=True)
    from httpx import ASGITransport, AsyncClient

    from app.main import app

    question = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_Q
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://x") as api:
        for path in sorted((ROOT / "corpus").iterdir()):
            await api.post("/documents", files={"file": (path.name, path.read_bytes())})
        await api.post("/index")
        print(f"Q: {question}\n")
        for mode in ("plain", "workflow", "agent"):
            r = await api.post(
                "/tasks/run", json={"question": question, "mode": mode, "approved": True}
            )
            out = r.json()
            print(f"=== {mode}: {out['status']}  ${out['cost_usd']:.5f}  {out['latency_ms']} ms")
            print(f"    calls: {out['calls'] or '-'}")
            for step in out.get("steps", []):
                res = " ".join(step["result"].split())[:90]
                print(f"    [{step['n']}] {step['tool']}({step['args']}) -> {res}")
            print(f"    answer: {out['answer'][:200]}\n")
    print("Three answers, three bills. Now run scripts/compare_week4.py over the whole task set.")


if __name__ == "__main__":
    asyncio.run(main())
