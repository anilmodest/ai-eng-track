"""Build the progress page (site/index.html) from what is already in the repo.

Nothing on it is self-reported.

Inputs, all optional (a missing one leaves its card section blank):
    reports/week-N.json      written by scripts/check.py (the pages workflow runs it per week)
    reflections/week-N.md    the fellow's own words (Q1 and Q2 are shown)
    weeks/N/README.md        the week's title
    .route                   start | core | pro
    site/prs.json            PR links and review-comment counts, written by the pages workflow
    LIVE_URL (env)           the deployed service, if any

Run locally: uv run python scripts/build_pages.py && open site/index.html
"""

import html
import json
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "site" / "index.html"

# Which of the eleven areas each week touches (from the programme plan).
WEEK_AREAS: dict[int, list[int]] = {
    0: [1],
    1: [2],
    2: [3, 4],
    3: [5, 8],
    4: [6, 7],
    5: [9, 10],
    6: [11],
}
AREAS = {
    1: "Software foundations",
    2: "Model as a component",
    3: "Context engineering",
    4: "Retrieval",
    5: "Grounding",
    6: "Agents and tools",
    7: "Real systems (MCP)",
    8: "Evaluation",
    9: "Observability and cost",
    10: "Security and guardrails",
    11: "Shipping and proving it",
}
CONCEPTS = {
    0: "Area 1 is a gate: assessed, not taught.",
    1: "A model is an unreliable, expensive, non-deterministic third-party dependency.",
    2: "Context is an attention budget; retrieval is where offers are lost.",
    3: "A system that always answers is worse than one that declines.",
    4: "Prefer the simplest thing that works; multi-agent is a last resort.",
    5: "Injected content is the defining vulnerability, and it does not look like a bug.",
    6: "Interviewers ask what it did for the business, not what it scored.",
}


@dataclass
class Week:
    n: int
    title: str
    report: dict[str, Any] | None = None
    reflection_q1: str = ""
    reflection_q2: str = ""
    pr: dict[str, Any] | None = None
    tests: list[dict[str, str]] = field(default_factory=list)

    @property
    def state(self) -> str:
        if self.report is None:
            return "not started"
        return "green" if self.report.get("ok") else "red"


def _section(md: str, heading: str) -> str:
    """Text under '## <heading>' up to the next '## '. Comments stripped."""
    m = re.search(rf"^## {re.escape(heading)}[^\n]*\n(.*?)(?=^## |\Z)", md, re.S | re.M)
    if not m:
        return ""
    body = re.sub(r"<!--.*?-->", "", m.group(1), flags=re.S).strip()
    body = re.sub(r"^\d\.\s*$", "", body, flags=re.M).strip()
    return body


def load_weeks() -> list[Week]:
    weeks: list[Week] = []
    for readme in sorted(ROOT.glob("weeks/*/README.md")):
        n = int(readme.parent.name)
        first = readme.read_text(encoding="utf-8").splitlines()[0]
        title = first.lstrip("# ").strip()
        w = Week(n=n, title=title)
        rep = ROOT / "reports" / f"week-{n}.json"
        if rep.exists():
            w.report = json.loads(rep.read_text(encoding="utf-8"))
            w.tests = [t for t in w.report.get("tests", []) if f"test_week{n}" in t.get("file", "")]
        refl = ROOT / "reflections" / f"week-{n}.md"
        if refl.exists():
            md = refl.read_text(encoding="utf-8")
            w.reflection_q1 = _section(md, "Q1.")
            w.reflection_q2 = _section(md, "Q2.")
        weeks.append(w)
    prs_path = ROOT / "site" / "prs.json"
    if prs_path.exists():
        prs = json.loads(prs_path.read_text(encoding="utf-8"))
        for w in weeks:
            w.pr = prs.get(str(w.n))
    return weeks


CSS = """
:root { --bg:#fafaf7; --fg:#1b1b1b; --muted:#6b6b6b; --line:#e4e2dc; --card:#ffffff;
        --green:#1f7a3d; --red:#b3261e; --grey:#9a9a9a; --accent:#2b4c7e; }
@media (prefers-color-scheme: dark) {
  :root { --bg:#141414; --fg:#ececec; --muted:#a3a3a3; --line:#2c2c2c; --card:#1d1d1d;
          --green:#4cc27a; --red:#ff6b61; --grey:#777; --accent:#8fb3ff; }
}
* { box-sizing: border-box; }
body { margin:0; background:var(--bg); color:var(--fg);
       font: 16px/1.5 ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif; }
main { max-width: 900px; margin: 0 auto; padding: 32px 16px 64px; }
h1 { font-size: 26px; margin: 0 0 4px; }
.sub { color: var(--muted); margin: 0 0 20px; }
.sub a { color: var(--accent); }
.strip { display:grid; grid-template-columns: repeat(11, 1fr); gap:4px; margin: 0 0 28px; }
.strip div { height: 10px; border-radius: 3px; background: var(--line); }
.strip div.green { background: var(--green); } .strip div.red { background: var(--red); }
.strip div.touched { background: var(--grey); }
.legend { font-size: 13px; color: var(--muted); margin: -20px 0 28px; }
.card { background: var(--card); border: 1px solid var(--line); border-radius: 10px;
        padding: 18px 20px; margin: 0 0 16px; }
.card h2 { font-size: 18px; margin: 0; display:flex; align-items:center; gap:10px; }
.dot { width: 12px; height: 12px; border-radius: 50%; background: var(--grey); flex: none; }
.dot.green { background: var(--green); } .dot.red { background: var(--red); }
.concept { font-style: italic; color: var(--muted); margin: 6px 0 12px; }
.grid { display:grid; grid-template-columns: 1fr 1fr; gap: 16px; }
@media (max-width: 640px) { .grid { grid-template-columns: 1fr; } .strip div { height: 8px; } }
h3 { font-size: 13px; text-transform: uppercase; letter-spacing: .04em; color: var(--muted);
     margin: 0 0 6px; }
ul { margin: 0; padding-left: 18px; } li { margin: 2px 0; }
li.pass::marker { color: var(--green); } li.fail::marker { color: var(--red); }
blockquote { margin: 0; padding: 0 0 0 12px; border-left: 3px solid var(--line);
             white-space: pre-wrap; font-size: 15px; }
.gates span { display:inline-block; padding: 2px 8px; border-radius: 999px; font-size: 13px;
              border: 1px solid var(--line); margin: 0 6px 6px 0; }
.gates span.pass { border-color: var(--green); color: var(--green); }
.gates span.fail { border-color: var(--red); color: var(--red); }
.next { margin-top: 12px; font-size: 14px; color: var(--muted); }
.next a { color: var(--accent); }
footer { color: var(--muted); font-size: 13px; margin-top: 32px; }
"""


def esc(s: object) -> str:
    return html.escape(str(s))


def render(weeks: list[Week], route: str, live_url: str, repo: str) -> str:
    area_state: dict[int, str] = {}
    for w in weeks:
        for a in WEEK_AREAS.get(w.n, []):
            area_state[a] = w.state if w.state != "not started" else "touched"
    strip = "".join(
        f'<div class="{area_state.get(a, "")}" title="{a}. {esc(AREAS[a])}"></div>'
        for a in range(1, 12)
    )

    done = [w for w in weeks if w.state == "green"]
    current = next((w for w in weeks if w.state != "green"), None)
    if current is None:
        you_are_here = "Every released week is green."
    else:
        you_are_here = (
            f"Week {current.n}: {esc(current.title)} &mdash; "
            f'<a href="https://github.com/{esc(repo)}/blob/main/weeks/{current.n}/README.md">'
            "open the README</a>"
        )

    cards = []
    for w in weeks:
        gates = ""
        if w.report:
            gates = "".join(
                f'<span class="{"pass" if ok else "fail"}">{esc(k)}</span>'
                for k, ok in (w.report.get("gates") or {}).items()
            )
        tests = "".join(
            f'<li class="{t["outcome"] == "passed" and "pass" or "fail"}">'
            f"{esc(t['id'].removeprefix('test_').replace('_', ' '))}</li>"
            for t in w.tests
        )
        pr = ""
        if w.pr:
            pr = (
                f'<a href="{esc(w.pr.get("url", "#"))}">PR #{esc(w.pr.get("number", "?"))}</a> '
                f"&middot; {esc(w.pr.get('state', ''))} &middot; "
                f"{esc(w.pr.get('review_comments', 0))} mentor comments"
            )
        refl = ""
        if w.reflection_q1:
            refl += "<h3>Concept, in the fellow's words</h3>"
            refl += f"<blockquote>{esc(w.reflection_q1)}</blockquote>"
        if w.reflection_q2:
            refl += "<h3 style='margin-top:10px'>What surprised them</h3>"
            refl += f"<blockquote>{esc(w.reflection_q2)}</blockquote>"
        checks = (
            f"<h3 style='margin-top:8px'>This week's checks</h3><ul>{tests}</ul>" if tests else ""
        )
        review = f"<h3 style='margin-top:10px'>Review</h3><div>{pr}</div>" if pr else ""
        no_refl = "<h3>Reflection</h3><div style='color:var(--muted)'>not written yet</div>"
        areas = ", ".join(f"{a} {AREAS[a]}" for a in WEEK_AREAS.get(w.n, []))
        cards.append(
            f"""
<section class="card">
  <h2><span class="dot {w.state}"></span>Week {w.n} &mdash; {esc(w.title)}</h2>
  <p class="concept">{esc(CONCEPTS.get(w.n, ""))}</p>
  <div class="grid">
    <div>
      <h3>Gate</h3>
      <div class="gates">{gates or "<span>not run yet</span>"}</div>
      {checks}
      <h3 style="margin-top:10px">Areas</h3><div>{esc(areas) or "&mdash;"}</div>
      {review}
    </div>
    <div>{refl or no_refl}</div>
  </div>
</section>"""
        )

    live = ""
    if live_url:
        live = f'&middot; live service: <a href="{esc(live_url)}">{esc(live_url)}</a>'
    legend = (
        "The eleven areas of the track. Green: this week's gate passed. "
        "Red: it did not. Grey: reached, not yet run."
    )
    note = (
        f"{len(done)} of {len(weeks)} released weeks green. This page is rebuilt from the repo "
        "on every merge to <code>main</code>; nothing on it is typed in by hand."
    )
    footer = (
        "Built by <code>scripts/build_pages.py</code> from <code>reports/</code>, "
        "<code>reflections/</code> and the PRs. Mentors: the held-out set and rubric live in "
        "the mentor kit, not here."
    )
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>AI Engineering track &mdash; progress</title>
<style>{CSS}</style></head>
<body><main>
<h1>AI Engineering track</h1>
<p class="sub"><a href="https://github.com/{esc(repo)}">{esc(repo)}</a>
 &middot; route: <b>{esc(route)}</b> {live}</p>
<div class="strip">{strip}</div>
<p class="legend">{legend}</p>
<section class="card"><h3>You are here</h3><div>{you_are_here}</div>
<div class="next">{note}</div></section>
{"".join(cards)}
<footer>{footer}</footer>
</main></body></html>
"""


def main() -> int:
    weeks = load_weeks()
    route_file = ROOT / ".route"
    route = route_file.read_text().strip() if route_file.exists() else "start"
    live_url = os.environ.get("LIVE_URL", "").strip()
    repo = os.environ.get("GITHUB_REPOSITORY", "anilmodest/ai-eng-track")
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(render(weeks, route, live_url, repo), encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)} ({len(weeks)} weeks)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
