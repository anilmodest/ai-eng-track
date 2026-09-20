"""Week 5, elaboration 1: make three requests, then answer questions about them from traces alone.

    uv run python explore/w5_01_read_a_trace.py

Works with the fake provider (MODEL_PROVIDER=fake_a) or a real one. Prints each request's span
tree and then the dashboard. Answer, without opening the code: which step cost the most? Which
request was slowest, and why? Which failed, and with what kind?
"""

import asyncio
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


async def main() -> None:
    db = ROOT / "data" / "explore-w5.db"
    os.environ["DATABASE_URL"] = f"sqlite:///{db.as_posix()}"
    db.unlink(missing_ok=True)
    from httpx import ASGITransport, AsyncClient

    from app.main import app

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://x") as api:
        for path in sorted((ROOT / "corpus").iterdir()):
            await api.post("/documents", files={"file": (path.name, path.read_bytes())})
        await api.post("/index")
        requests: list[tuple[str, str, str, dict[str, str] | None]] = [
            ("extract, first time", "POST", "/documents/1/extract", None),
            ("extract, second time", "POST", "/documents/1/extract", None),
            ("ask", "POST", "/ask", {"question": "What is the London hotel cap?"}),
            ("ask nonsense", "POST", "/ask", {"question": "zxq plimbo vortex"}),
            ("missing document", "GET", "/documents/999", None),
        ]
        for label, method, path_, body in requests:
            r = await api.request(method, path_, json=body)
            rid = r.headers.get("X-Request-Id", "")
            t = (await api.get(f"/traces/{rid}")).json()
            print(f"=== {label}: HTTP {r.status_code}  request {rid}")
            for s in t["spans"]:
                indent = "    " if s["parent"] else "  "
                err = f"  !! {s['error_kind']}" if s["error_kind"] else ""
                print(
                    f"{indent}{s['name']:<32} {s['duration_ms']:>5} ms  "
                    f"tokens {s['tokens_in']:>5}/{s['tokens_out']:<4} ${s['cost_usd']:.5f}{err}"
                )
            print()
    print("Now: uv run python scripts/trace_report.py --db data/explore-w5.db")


if __name__ == "__main__":
    asyncio.run(main())
