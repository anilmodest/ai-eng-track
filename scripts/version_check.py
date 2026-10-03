"""Week 2: see the wrong-version problem, then watch your filter close it.

Five questions a support agent would actually ask about version 3, run twice: once with no version
filter, once with one. The first column is what similarity alone does with a manual that exists
twice over.

    uv run python scripts/version_check.py

Writes reports/versions.json. Run it before you build `applicable_versions`, and again after.
"""

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

QUESTIONS = [
    "what is the default connection timeout",
    "where is the connection timeout set",
    "how long are logs kept",
    "how do I authenticate to the API",
    "how are schedules written",
]
VERSION = "v3"


async def run() -> dict[str, Any]:
    from httpx import ASGITransport, AsyncClient

    from app.main import app
    from app.retrieval.versions import ANY_VERSION

    rows: list[dict[str, Any]] = []
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://v") as api:
        for path in sorted((ROOT / "corpus").iterdir()):
            r = await api.post("/documents", files={"file": (path.name, path.read_bytes())})
            assert r.status_code == 201, r.text
        r = await api.post("/index", params={"strategy": "heading"})
        assert r.status_code == 200, r.text

        for question in QUESTIONS:
            base: dict[str, str | int] = {"q": question, "k": 5, "strategy": "heading"}
            unfiltered = (await api.get("/search", params=base)).json()
            try:
                filtered = (await api.get("/search", params={**base, "version": VERSION})).json()
                built = True
            except Exception:
                filtered, built = [], False

            def label(hits: list[dict[str, Any]]) -> str:
                if not hits:
                    return "-"
                top = hits[0]
                return f"{top['version'] or ANY_VERSION}  {top['filename'].replace('manual-', '')}"

            rows.append(
                {
                    "question": question,
                    "unfiltered_top": label(unfiltered),
                    "unfiltered_wrong_version": bool(unfiltered)
                    and unfiltered[0].get("version") not in (VERSION, None),
                    "filtered_top": label(filtered) if built else "not built yet",
                    "filtered_leaks": [h["filename"] for h in filtered if h.get("version") == "v2"],
                    "filtered_count": len(filtered),
                }
            )
    return {"version": VERSION, "rows": rows}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default=str(ROOT / "data" / "versions.db"))
    args = ap.parse_args()
    os.environ["DATABASE_URL"] = f"sqlite:///{Path(args.db).as_posix()}"
    Path(args.db).unlink(missing_ok=True)

    try:
        report = asyncio.run(run())
    except NotImplementedError as e:
        print(f"applicable_versions is not built yet: {e}")
        print("Run this once before you build it, to see what you are fixing. See the")
        print("'unfiltered' column: that is the system the support desk would have had.")
        return 0

    rows = report["rows"]
    print(f"\nFive questions about {report['version']}, asked two ways.\n")
    print(f"  {'question':<38} {'no filter -> top hit':<36} {'with filter -> top hit'}")
    for r in rows:
        print(f"  {r['question']:<38} {r['unfiltered_top']:<36} {r['filtered_top']}")

    wrong = sum(1 for r in rows if r["unfiltered_wrong_version"])
    leaks = sum(len(r["filtered_leaks"]) for r in rows)
    short = [r for r in rows if r["filtered_count"] not in (0, 5)]

    print(f"\n  without a filter, the wrong version was the top hit for {wrong} of {len(rows)}")
    print(f"  with a filter, version 2 material returned: {leaks} passages")
    if short:
        print(f"  filtered searches that came back short of k=5: {len(short)}")
        print("    -> you are filtering after ranking, not before. That is lost recall.")

    (ROOT / "reports").mkdir(exist_ok=True)
    (ROOT / "reports" / "versions.json").write_text(json.dumps(report, indent=2))
    print("\n  wrote reports/versions.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
