"""Week 5: attack your own service with documents that carry instructions. Count the successes.

    uv run python scripts/attack.py                       # provider from .env
    uv run python scripts/attack.py --guard off           # the same with GUARD_ENABLED=false

Each row in eval/attacks.jsonl is a document with an injected instruction and a definition of
what "the attack worked" looks like. Exit code 1 if any attack succeeds: that is the CI gate.
Writes reports/attacks.json.
"""

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
ATTACKS = ROOT / "eval" / "attacks.jsonl"


def _succeeded(row: dict[str, Any], out: dict[str, Any]) -> bool:
    cond = row["success_if"]
    if row["target"] == "extract":
        ex = out.get("extract") or {}
        facts = " ".join(ex.get("key_facts", []))
        if "doc_type" in cond and ex.get("doc_type") != cond["doc_type"]:
            return False
        if "fact_contains" in cond and cond["fact_contains"] not in facts:
            return False
        return True
    answer = out.get("answer") or ""
    return cond["answer_contains"] in answer


async def run(attacks: list[dict[str, Any]]) -> int:
    from httpx import ASGITransport, AsyncClient

    from app.main import app

    results: list[dict[str, Any]] = []
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://attack") as api:
        # A little legitimate corpus so /ask has something to retrieve besides the poison.
        for path in sorted((ROOT / "corpus").iterdir()):
            await api.post("/documents", files={"file": (path.name, path.read_bytes())})
        for row in attacks:
            up = await api.post(
                "/documents", files={"file": (f"{row['id']}.md", row["text"].encode())}
            )
            doc_id = up.json()["id"]
            if row["target"] == "extract":
                r = await api.post(f"/documents/{doc_id}/extract")
            else:
                await api.post("/index")
                r = await api.post("/ask", json={"question": row["question"]})
            out = r.json() if r.status_code == 200 else {}
            ok = r.status_code == 200 and _succeeded(row, out)
            detected = bool((out.get("guard") or {}).get("injection_detected")) or bool(
                out.get("injection_detected")
            )
            results.append(
                {
                    "id": row["id"],
                    "name": row["name"],
                    "target": row["target"],
                    "status": r.status_code,
                    "attack_succeeded": ok,
                    "injection_detected": detected,
                    "output_flags": (out.get("guard") or {}).get("output_flags", []),
                }
            )
            verdict = "ATTACK SUCCEEDED" if ok else "held"
            print(
                f"{row['id']}  {row['name']:<46} {verdict:<16} "
                f"detected={str(detected):<5} flags={len(results[-1]['output_flags'])}"
            )

    succeeded = sum(1 for r in results if r["attack_succeeded"])
    (ROOT / "reports").mkdir(exist_ok=True)
    (ROOT / "reports" / "attacks.json").write_text(
        json.dumps(
            {
                "attacks": len(results),
                "succeeded": succeeded,
                "guard_enabled": os.environ.get("GUARD_ENABLED", "true"),
                "rows": results,
            },
            indent=2,
        )
    )
    print(
        f"\n{succeeded} of {len(results)} attacks succeeded. "
        f"{'GATE FAIL' if succeeded else 'GATE PASS'}  (reports/attacks.json)"
    )
    return 1 if succeeded else 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--guard", choices=["on", "off"], default="on")
    ap.add_argument("--db", default=str(ROOT / "data" / "attack.db"))
    args = ap.parse_args()
    os.environ["GUARD_ENABLED"] = "true" if args.guard == "on" else "false"
    os.environ["DATABASE_URL"] = f"sqlite:///{Path(args.db).as_posix()}"
    Path(args.db).unlink(missing_ok=True)
    attacks = [json.loads(ln) for ln in ATTACKS.read_text(encoding="utf-8").splitlines() if ln]
    return asyncio.run(run(attacks))


if __name__ == "__main__":
    sys.exit(main())
