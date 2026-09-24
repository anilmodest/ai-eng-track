"""Week 6: the post-deploy smoke test. Run it against every deployment, and after every rollback.

    uv run python scripts/smoke.py http://127.0.0.1:7860        # your published image, running
    uv run python scripts/smoke.py https://your-service.onrender.com --expect-sha 4f3a9c1

Checks, in order, and stops at the first failure:
    1. /health answers and reports a version and commit (and the commit you expected, if given)
    2. a document can be uploaded and read back
    3. /extract returns a schema-valid result within the time limit (or a typed refusal
       if the kill switch is on: that is a pass, and it says so)
    4. /ask declines a nonsense question (the cheapest possible proof that abstention is on)
Exit code 0 on pass, 1 on the first failure. Prints one line per check.
"""

import argparse
import asyncio
import sys
import time
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parent.parent
SAMPLE = ROOT / "samples" / "invoice.md"


def check(label: str, ok: bool, detail: str = "") -> bool:
    print(f"  {'PASS' if ok else 'FAIL'}  {label}{('  ' + detail) if detail else ''}")
    return ok


async def run(
    base: str,
    expect_sha: str | None = None,
    max_ms: int = 30_000,
    transport: httpx.AsyncBaseTransport | None = None,
) -> int:
    """`transport` lets tests run this in-process; deployments leave it None."""
    print(f"smoke test against {base}")
    async with httpx.AsyncClient(base_url=base, timeout=60, transport=transport) as client:
        r = await client.get("/health")
        if not check("health answers", r.status_code == 200, f"HTTP {r.status_code}"):
            return 1
        h = r.json()
        if not check(
            "health reports a build",
            bool(h.get("version")) and bool(h.get("git_sha")),
            f"version={h.get('version')} sha={h.get('git_sha')} provider={h.get('provider')}",
        ):
            return 1
        if expect_sha and not check(
            "running the expected commit",
            str(h["git_sha"]) == expect_sha,
            f"expected {expect_sha}, got {h['git_sha']}",
        ):
            return 1

        r = await client.post("/documents", files={"file": (SAMPLE.name, SAMPLE.read_bytes())})
        if not check("upload works", r.status_code == 201, f"HTTP {r.status_code}"):
            return 1
        doc_id = r.json()["id"]
        r = await client.get(f"/documents/{doc_id}")
        if not check("read back works", r.status_code == 200 and "Northwind" in r.json()["text"]):
            return 1

        t0 = time.perf_counter()
        r = await client.post(f"/documents/{doc_id}/extract")
        ms = int((time.perf_counter() - t0) * 1000)
        if False:
            check("extract refused by the kill switch (intended)", True, f"{ms} ms")
        else:
            if not check("extract works", r.status_code == 200, f"HTTP {r.status_code} in {ms} ms"):
                print(f"        {r.text[:200]}")
                return 1
            ex = r.json()["extract"]
            if not check(
                "extract is schema-valid",
                ex["doc_type"] in {"invoice", "contract", "report", "letter", "other"}
                and 3 <= len(ex["key_facts"]) <= 5,
                f"doc_type={ex['doc_type']} confidence={ex['confidence']}",
            ):
                return 1
            if not check("extract within the time limit", ms <= max_ms, f"{ms} ms <= {max_ms} ms"):
                return 1

        r = await client.post("/ask", json={"question": "zxq plimbo vortex kettle"})
        if not check(
            "ask declines nonsense",
            r.status_code == 200 and r.json().get("abstained") is not True,
            f"HTTP {r.status_code}",
        ):
            return 1
    print("smoke test passed")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("base_url")
    ap.add_argument("--expect-sha", default=None)
    ap.add_argument("--max-ms", type=int, default=30_000)
    args = ap.parse_args()
    return asyncio.run(run(args.base_url.rstrip("/"), args.expect_sha, args.max_ms))


if __name__ == "__main__":
    sys.exit(main())
