"""Week 6: the post-deploy smoke test. Run it against every release, and after every rollback.

    uv run python scripts/smoke.py http://127.0.0.1:7860        # your published image, running
    uv run python scripts/smoke.py https://your-service.onrender.com --expect-sha 4f3a9c1

Checks, in order, and stops at the first failure:
    1. /health answers and reports a version and commit (and the commit you expected, if given)
    2. the two connection-timeout pages of the manual upload, and the index builds
    3. /ask answers the brief's question for a version 3 customer, citing the version 3 page and
       no version 2 page (a typed refusal from the kill switch is a pass, and so is 501 from an
       exercise you have not built yet)
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
PAGES = [ROOT / "corpus" / f"manual-{v}-connection-timeout.md" for v in ("v2", "v3")]
QUESTION = "How do I configure the connection timeout?"


def _not_built(r: httpx.Response) -> bool:
    """The service grows week by week. An exercise you have not reached answers 501; that is not a
    broken deployment, so the smoke test skips it. A wrong answer still fails."""
    if r.status_code != 501:
        return False
    try:
        return bool(r.json().get("error") == "not_implemented")
    except ValueError:
        return False


def _kill_switch(r: httpx.Response) -> bool:
    try:
        return r.status_code == 503 and r.json().get("error") == "kill_switch"
    except ValueError:
        return False


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
    async with httpx.AsyncClient(base_url=base, timeout=120, transport=transport) as client:
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
            str(h["git_sha"]).startswith(expect_sha),
            f"expected {expect_sha}, got {h['git_sha']}",
        ):
            return 1

        # The brief's example: two pages nearly identical in wording, different in substance.
        for page in PAGES:
            r = await client.post("/documents", files={"file": (page.name, page.read_bytes())})
            if not check(f"upload {page.name}", r.status_code == 201, f"HTTP {r.status_code}"):
                return 1
        r = await client.post("/index")
        indexed = not _not_built(r)
        if not indexed:
            check("index: Week 2 not built yet", True, "skipped")
        elif not check("index builds", r.status_code == 200, f"HTTP {r.status_code}"):
            print(f"        {r.text[:200]}")
            return 1

        t0 = time.perf_counter()
        r = await client.post("/ask", json={"question": QUESTION, "version": "v3"})
        ms = int((time.perf_counter() - t0) * 1000)
        if _not_built(r) or not indexed:
            check("ask: not built yet", True, "skipped")
        elif _kill_switch(r):
            check("ask refused by the kill switch (intended)", True, f"{ms} ms")
        else:
            if not check("ask works", r.status_code == 200, f"HTTP {r.status_code} in {ms} ms"):
                print(f"        {r.text[:200]}")
                return 1
            body = r.json()
            cited = [c["filename"] for c in body.get("citations", [])]
            if not check(
                "ask answers the version 3 question",
                body.get("abstained") is False and bool(body.get("answer")),
                f"abstained={body.get('abstained')} reason={body.get('reason')}",
            ):
                return 1
            if not check(
                "ask cites the version 3 page and no version 2 page",
                PAGES[1].name in cited and PAGES[0].name not in cited,
                f"cited {cited}",
            ):
                return 1
            if not check("ask within the time limit", ms <= max_ms, f"{ms} ms <= {max_ms} ms"):
                return 1

            r = await client.post("/ask", json={"question": "zxq plimbo vortex kettle"})
            if not check(
                "ask declines nonsense",
                r.status_code == 200 and r.json().get("abstained") is True,
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
