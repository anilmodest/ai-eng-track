"""Week 5: did any personal data reach the model? Check what it was actually shown.

    MASK_PERSONAL_DATA=true uv run python scripts/privacy_check.py
    MASK_PERSONAL_DATA=false uv run python scripts/privacy_check.py      # the before

Runs the agent on tickets that carry a person's name, email address and phone number, then reads
every model input the service recorded (app/llm/masking.py ModelInput) and looks for each of those
values in it. A leak is one value found in one model input. Writes reports/privacy.json;
`make evidence WEEK=5` keeps it. The week 5 proof is a count of zero.
"""

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent


async def run(limit: int) -> dict[str, Any]:
    from httpx import ASGITransport, AsyncClient
    from sqlmodel import Session, select

    from app.db.session import get_engine
    from app.llm.masking import ModelInput
    from app.main import app
    from app.settings import get_settings
    from app.support import desk_tickets

    with Session(get_engine()) as session:
        tickets = [t for t in desk_tickets(session) if t.requester_email][:limit]
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://p", timeout=300
    ) as api:
        for t in tickets:
            await api.post("/tasks/run", json={"question": f"Summarise ticket {t.ticket_id}."})
    personal = {
        v for t in tickets for v in (t.requester_name, t.requester_email, t.requester_phone) if v
    }
    leaks: list[dict[str, str]] = []
    with Session(get_engine()) as session:
        inputs = list(session.exec(select(ModelInput)))
        for row in inputs:
            for value in personal:
                if value in row.text:
                    leaks.append({"request_id": row.request_id, "value": value[:3] + "..."})
    return {
        "masking": get_settings().mask_personal_data,
        "tickets": len(tickets),
        "model_inputs": len(inputs),
        "personal_values": len(personal),
        "leaks": len(leaks),
        "examples": leaks[:10],
    }


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=8)
    ap.add_argument("--db", default=str(ROOT / "data" / "privacy.db"))
    args = ap.parse_args(argv)
    os.environ["DATABASE_URL"] = f"sqlite:///{Path(args.db).as_posix()}"
    Path(args.db).unlink(missing_ok=True)
    report = asyncio.run(run(args.limit))
    (ROOT / "reports").mkdir(exist_ok=True)
    (ROOT / "reports" / "privacy.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(
        f"masking {'on' if report['masking'] else 'off'}: {report['model_inputs']} model inputs "
        f"from {report['tickets']} tickets, {report['leaks']} personal values found in them"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
