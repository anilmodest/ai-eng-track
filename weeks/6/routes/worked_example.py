"""Week 6 worked example (start route): one smoke check, in the shape scripts/smoke.py uses.

    uv run python weeks/6/routes/worked_example.py http://127.0.0.1:8000

check() prints one line and returns the verdict; run() stops at the first failure. That is the
whole pattern; scripts/smoke.py has five of them.
"""

import asyncio
import sys

import httpx


def check(label: str, ok: bool, detail: str = "") -> bool:
    print(f"  {'PASS' if ok else 'FAIL'}  {label}{('  ' + detail) if detail else ''}")
    return ok


async def run(base: str) -> int:
    async with httpx.AsyncClient(base_url=base, timeout=30) as client:
        try:
            r = await client.get("/health")
        except httpx.HTTPError as e:
            check("health reachable", False, str(e))
            return 1
        if not check("health answers", r.status_code == 200, f"HTTP {r.status_code}"):
            return 1
        h = r.json()
        return (
            0 if check("reports a build", bool(h.get("git_sha")), f"sha={h.get('git_sha')}") else 1
        )


if __name__ == "__main__":
    sys.exit(asyncio.run(run(sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000")))
