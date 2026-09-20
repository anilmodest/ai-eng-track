"""`make live-check`: the real provider from .env against the sample documents.

Prints one row per document. Paste the table into reflections/week-1.md, switch, run again.
"""

import asyncio
import sys
from pathlib import Path

from httpx import ASGITransport, AsyncClient

ROOT = Path(__file__).resolve().parent.parent
SAMPLES = sorted((ROOT / "samples").glob("*"))


async def main() -> int:
    from app.llm.registry import get_model_client
    from app.main import app

    client = get_model_client()
    print(f"provider={client.name}  model={client.model}\n")
    header = (
        f"{'file':<16} {'status':<7} {'cached':<7} {'tok_in':>7} {'tok_out':>8} "
        f"{'ms':>6} {'usd':>9}  type/conf"
    )
    print(header)
    print("-" * len(header))
    ok = True
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://live") as api:
        for path in SAMPLES:
            up = await api.post("/documents", files={"file": (path.name, path.read_bytes())})
            doc_id = up.json()["id"]
            # Twice on purpose: the second row must say cached=True and add no new cost.
            for _ in range(2):
                r = await api.post(f"/documents/{doc_id}/extract")
                if r.status_code != 200:
                    ok = False
                    body = r.json()
                    err = f"{body.get('error')}: {body.get('detail')}"
                    print(f"{path.name:<16} {r.status_code:<7} {err}")
                    break
                b = r.json()
                ex = b["extract"]
                print(
                    f"{path.name:<16} {r.status_code:<7} {str(b['cached']):<7} {b['tokens_in']:>7} "
                    f"{b['tokens_out']:>8} {b['latency_ms']:>6} {b['cost_usd']:>9.6f}  "
                    f"{ex['doc_type']}/{ex['confidence']:.2f}"
                )
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
