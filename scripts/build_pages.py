"""Build the hub page (site/index.html) from what is already in the repo. Nothing self-reported.

The page is a mirror with a front door: every week's material rendered from weeks/N/*.md, every
gate's result from reports/, the fellow's own words from reflections/, the PRs from GitHub, and a
playground that calls the fellow's live service from the browser.

Inputs, all optional (a missing one leaves its panel blank or explains itself):
    README.md, weeks/N/{CONCEPT,README,CHECKS}.md      rendered to HTML at build time
    reports/week-N.json                                 scripts/check.py
    reports/{retrieval,eval,compare,attacks,traces}.json the measurement scripts
    reflections/week-N.md                               Q1 and Q2 shown on the week card
    .route                                              start | core | pro
    site/prs.json                                       written by the pages workflow
    LIVE_URL, GITHUB_REPOSITORY (env)                   the deployed service, the repo

Run locally: uv run python scripts/build_pages.py && open site/index.html
"""

import html
import json
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from markdown_it import MarkdownIt

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "site" / "index.html"
_ROUTE_FILE = ROOT / ".route"
ROUTE = _ROUTE_FILE.read_text().strip() if _ROUTE_FILE.exists() else "start"
MD = MarkdownIt("commonmark", {"html": True}).enable("table")

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
# Which measurement report belongs to which week's card.
WEEK_REPORTS: dict[int, list[str]] = {
    2: ["retrieval", "degrade"],
    3: ["eval"],
    4: ["compare"],
    5: ["attacks"],
    6: ["traces"],
}

# The loop, per week: what to run, which file(s) to build, how to measure. Mirrors weeks/N/README.md.
STEPS = ["Read", "Run", "Build", "Check", "Submit"]
WEEK_RUN: dict[int, list[str]] = {
    0: ["make check WEEK=0", "make run", "docker build -t ai-eng-track ."],
    1: ["uv run python explore/w1_01_same_prompt_x5.py", "uv run python explore/w1_02_break_it.py"],
    2: [
        "uv run python explore/w2_01_chunk_and_look.py",
        "uv run python explore/w2_02_lost_in_the_middle.py --trials 3 --filler 40",
    ],
    3: ["uv run python explore/w3_01_ask_without_a_net.py"],
    4: ["uv run python explore/w4_01_watch_the_agent_think.py"],
    5: ["uv run python explore/w5_01_read_a_trace.py", "uv run python scripts/attack.py"],
    6: ["uv run python scripts/smoke.py http://127.0.0.1:8000"],
}
WEEK_BUILD: dict[int, list[str]] = {  # app/trace.py is added to Week 5 on core and pro (below)
    0: [],
    1: ["app/api/extract.py"],
    2: ["app/retrieval/metrics.py", "app/retrieval/chunkers.py", "app/retrieval/context.py"],
    3: ["app/api/ask.py"],
    4: ["app/agents/agent.py"],
    5: ["app/guard.py"],
    6: ["reflections/writeup.md"],
}
if ROUTE != "start":
    WEEK_BUILD[5] = ["app/trace.py", *WEEK_BUILD[5]]

WEEK_MEASURE: dict[int, str] = {
    1: "make live-check",
    2: "uv run python scripts/retrieval_eval.py && uv run python scripts/degrade_repair.py",
    3: "uv run python scripts/eval.py",
    4: "uv run python scripts/compare_week4.py",
    5: "uv run python scripts/attack.py",
    6: "uv run python scripts/smoke.py $LIVE_URL --expect-sha <sha>",
}
# The four mentor sessions (the PDF's cadence). Other weeks are self-directed.
WEEK_SESSION: dict[int, str] = {
    0: "Session 1: Discovery, 45 min",
    1: "Session 2: Direction, 45 min",
    3: "Session 3: Observation, 60 min",
    6: "Session 4: Defence, 60 min",
}
WEEK_BUILD_NOTE: dict[int, str] = {
    0: "Nothing to build. Run the service, trace one upload aloud, build the Docker image.",
    1: "The endpoint is a stub with the build order in comments. Every test in tests/weeks/test_week1.py is a sentence from the concept.",
    2: "Metrics raise NotImplementedError; by_heading falls back to paragraphs; select_and_compress returns everything (the degraded pipeline). Build all three, then measure.",
    3: "POST /ask answers 501 until you build the two abstention gates and citations.",
    4: "run_agent returns not_implemented. Build the loop: wall, money checkpoint, recovery.",
    5: "The guard ships as a pass-through: get attacked first, then build the four defences.",
    6: "Tag, deploy, break, roll back, then write the one page that says what it did for the business.",
}


def esc(s: object) -> str:
    return html.escape(str(s))


_MERMAID = re.compile(r'<pre><code class="language-mermaid">(.*?)</code></pre>', re.S)


def md(path: Path) -> str:
    if not path.exists():
        return ""
    text = path.read_text(encoding="utf-8")
    text = re.sub(r"^# .*\n", "", text, count=1)  # the card already carries the title
    rendered = str(MD.render(text))
    # markdown-it escapes fenced code; mermaid needs the raw source back.
    return _MERMAID.sub(
        lambda m: f'<pre class="mermaid">{html.unescape(m.group(1))}</pre>', rendered
    )


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


@dataclass
class Question:
    n: int
    text: str
    options: list[dict[str, Any]]  # {"text", "correct", "why"}
    why: str
    stretch: bool


def parse_quiz(path: Path) -> list[Question]:
    if not path.exists():
        return []
    out: list[Question] = []
    cur: Question | None = None
    for line in path.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^## Q(\d+)\.\s*(.+?)\s*(\(stretch: [^)]*\))?\s*$", line)
        if m:
            cur = Question(int(m.group(1)), m.group(2), [], "", bool(m.group(3)))
            out.append(cur)
            continue
        if cur is None:
            continue
        m = re.match(r"^- \[([ x])\]\s*(.+)$", line)
        if m:
            body = m.group(2)
            text, _, why = body.partition(" — ")
            cur.options.append(
                {"text": text.strip(), "correct": m.group(1) == "x", "why": why.strip()}
            )
            continue
        m = re.match(r"^> Why:\s*(.+)$", line)
        if m:
            cur.why = m.group(1).strip()
    return [q for q in out if q.options]


@dataclass
class Week:
    n: int
    title: str
    report: dict[str, Any] | None = None
    reflection_q1: str = ""
    reflection_q2: str = ""
    pr: dict[str, Any] | None = None
    tests: list[dict[str, str]] = field(default_factory=list)
    concept_html: str = ""
    readme_html: str = ""
    checks_html: str = ""
    quiz: list[Question] = field(default_factory=list)
    has_reflection: bool = False

    @property
    def merged(self) -> bool:
        return bool(self.pr and str(self.pr.get("state", "")).upper() == "MERGED")

    @property
    def done(self) -> bool:
        return self.state == "green" and (self.merged or self.n == 0)

    @property
    def step(self) -> str:
        """Where a fellow most likely is inside this week, from files alone."""
        if self.pr and not self.merged:
            return "Submit"
        if self.state == "green":
            return "Submit"
        if self.has_reflection:
            return "Build"
        if self.state == "red":
            return "Build"
        return "Read"

    @property
    def state(self) -> str:
        if self.report is None:
            return "not started"
        return "green" if self.report.get("ok") else "red"


def _section(text: str, heading: str) -> str:
    m = re.search(rf"^## {re.escape(heading)}[^\n]*\n(.*?)(?=^## |\Z)", text, re.S | re.M)
    if not m:
        return ""
    body = re.sub(r"<!--.*?-->", "", m.group(1), flags=re.S).strip()
    return re.sub(r"^\d\.\s*$", "", body, flags=re.M).strip()


def load_weeks() -> list[Week]:
    weeks: list[Week] = []
    for readme in sorted(ROOT.glob("weeks/*/README.md")):
        n = int(readme.parent.name)
        first = readme.read_text(encoding="utf-8").splitlines()[0]
        title = re.sub(r"^Week \d+\s*[—-]\s*", "", first.lstrip("# ").strip())
        w = Week(n=n, title=title)
        rep = read_json(ROOT / "reports" / f"week-{n}.json")
        if rep:
            w.report = rep
            w.tests = [t for t in rep.get("tests", []) if f"test_week{n}" in t.get("file", "")]
        refl = ROOT / "reflections" / f"week-{n}.md"
        if refl.exists():
            w.has_reflection = True
            text = refl.read_text(encoding="utf-8")
            w.reflection_q1 = _section(text, "Q1.")
            w.reflection_q2 = _section(text, "Q2.")
        w.concept_html = md(readme.parent / "CONCEPT.md")
        w.readme_html = md(readme)
        w.checks_html = md(readme.parent / "CHECKS.md")
        w.quiz = parse_quiz(readme.parent / "QUIZ.md")
        weeks.append(w)
    prs = read_json(ROOT / "site" / "prs.json") or {}
    for w in weeks:
        w.pr = prs.get(str(w.n))
    return weeks


# ---- report renderers (each returns HTML or "") ----------------------------------------------


def table(headers: list[str], rows: list[list[object]]) -> str:
    th = "".join(f"<th>{esc(h)}</th>" for h in headers)
    trs = "".join("<tr>" + "".join(f"<td>{esc(c)}</td>" for c in r) + "</tr>" for r in rows)
    return f'<div class="tbl"><table><thead><tr>{th}</tr></thead><tbody>{trs}</tbody></table></div>'


def report_retrieval() -> str:
    r = read_json(ROOT / "reports" / "retrieval.json")
    if not r:
        return ""
    rows: list[list[object]] = [
        [
            name,
            s["chunks"],
            s["avg_chars"],
            s["precision_at_k"],
            s["recall_at_k"],
            s["mrr"],
            s["hit_rate"],
        ]
        for name, s in r["strategies"].items()
    ]
    return f"<p class='muted'>embedder <code>{esc(r['embedder'])}</code>, k={r['k']}</p>" + table(
        ["strategy", "chunks", "avg chars", "P@k", "R@k", "MRR", "hit"], rows
    )


def report_eval() -> str:
    r = read_json(ROOT / "reports" / "eval.json")
    if not r:
        return ""
    m, t, g = r["metrics"], r["thresholds"], r["gates"]
    keys = [
        ("abstain_rate_unanswerable", "min_abstain"),
        ("answer_rate_answerable", "min_answer"),
        ("hit_rate", "min_hit"),
        ("citation_validity", "min_citation"),
    ]
    rows: list[list[object]] = [
        [k, f"{m[k]:.2f}", f"{t[tk]:.2f}", "PASS" if g[k] else "FAIL"] for k, tk in keys
    ]
    rows.append(["total_cost_usd", f"{m.get('total_cost_usd', 0):.4f}", "", ""])
    return table(["metric", "value", "threshold", "verdict"], rows)


def report_compare() -> str:
    r = read_json(ROOT / "reports" / "compare.json")
    if not r:
        return ""
    rows: list[list[object]] = [
        [
            mode,
            f"{s['correct']}/{s['of']}",
            f"{s['cost_usd']:.5f}",
            s["mean_latency_ms"],
            s["mean_calls"],
        ]
        for mode, s in r.items()
    ]
    return table(["mode", "correct", "cost $", "mean ms", "mean calls"], rows)


def report_attacks() -> str:
    r = read_json(ROOT / "reports" / "attacks.json")
    if not r:
        return ""
    rows: list[list[object]] = [
        [
            row["id"],
            row["name"],
            "SUCCEEDED" if row["attack_succeeded"] else "held",
            row["injection_detected"],
        ]
        for row in r["rows"]
    ]
    verdict = (
        f"<p><b>{r['succeeded']} of {r['attacks']} attacks succeeded</b> "
        f"(guard {esc(r.get('guard_enabled'))})</p>"
    )
    return verdict + table(["id", "attack", "result", "detected"], rows)


def report_traces() -> str:
    r = read_json(ROOT / "reports" / "traces.json")
    if not r:
        return ""
    rows: list[list[object]] = [
        [name, s["count"], s["p50_ms"], s["p95_ms"], f"{s['cost_usd']:.5f}"]
        for name, s in r["steps"].items()
    ]
    errs = ", ".join(f"{k}: {v}" for k, v in (r.get("errors") or {}).items()) or "none"
    return (
        f"<p class='muted'>{r['requests']} requests, ${r['total_cost_usd']:.5f} total; "
        f"failures: {esc(errs)}</p>" + table(["step", "n", "p50 ms", "p95 ms", "cost $"], rows)
    )


def report_degrade() -> str:
    r = read_json(ROOT / "reports" / "degrade.json")
    if not r:
        return ""
    rows: list[list[object]] = [
        [
            mode,
            f"{v['hits']}/{v['of']}",
            v["mean_tokens_in"],
            f"{v['total_cost_usd']:.5f}",
            v["mean_latency_ms"],
        ]
        for mode, v in r.items()
    ]
    return table(["mode", "hits", "mean tokens in", "total $", "mean ms"], rows)


REPORTS = {
    "retrieval": ("Retrieval evaluation", report_retrieval),
    "degrade": ("Degrade and repair", report_degrade),
    "eval": ("Evaluation gate", report_eval),
    "compare": ("Three ways compared", report_compare),
    "attacks": ("Attack set", report_attacks),
    "traces": ("Trace report", report_traces),
}


# ---- page --------------------------------------------------------------------------------------

CSS = """
:root { --bg:#f6f7f5; --fg:#1c2128; --muted:#5b6470; --line:#dbe0e3; --card:#ffffff; --soft:#e8eff5;
        --green:#2e7d4f; --red:#b3261e; --grey:#9a9a9a; --accent:#1f5f8b; --accent-ink:#fff; --code:#eef1f3; }
@media (prefers-color-scheme: dark) {
  :root { --bg:#141719; --fg:#e7eaec; --muted:#9aa4ad; --line:#2c3339; --card:#1c2024; --soft:#22303a;
          --green:#6fcf97; --red:#ff6b61; --grey:#777; --accent:#7db4dc; --accent-ink:#0f1a22; --code:#252b30; }
}
* { box-sizing: border-box; }
body { margin:0; background:var(--bg); color:var(--fg);
       font: 16px/1.55 "IBM Plex Sans", ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif; }
.wrap { max-width: 1120px; margin: 0 auto; padding: 32px 20px 80px; display: grid; grid-template-columns: 210px minmax(0, 1fr); gap: 44px; }
@media (max-width: 880px) { .wrap { grid-template-columns: minmax(0, 1fr); gap: 20px; } }
aside { position: sticky; top: 16px; align-self: start; font-size: 14px; }
@media (max-width: 880px) { aside { position: static; } }
aside .eyebrow { font: 500 12px/1.4 "IBM Plex Mono", ui-monospace, monospace; letter-spacing: .08em; text-transform: uppercase; color: var(--muted); margin: 0 0 10px; }
aside ol { list-style: none; margin: 0; padding: 0; border-left: 2px solid var(--line); }
aside li a { display: block; padding: 5px 12px; color: var(--muted); text-decoration: none; border-left: 2px solid transparent; margin-left: -2px; }
aside li a:hover, aside li a.on { color: var(--fg); border-left-color: var(--accent); }
aside .side { margin-top: 18px; font-size: 13px; color: var(--muted); line-height: 1.5; }
article { min-width: 0; max-width: 780px; }
a { color: var(--accent); }
h1 { font-size: 32px; line-height: 1.15; margin: 0 0 6px; font-weight: 600; }
h2 { font-size: 23px; line-height: 1.25; margin: 44px 0 10px; font-weight: 600; padding-top: 10px; border-top: 1px solid var(--line); }
h2:first-of-type { border-top: none; padding-top: 0; }
h3 { font-size: 13px; text-transform: uppercase; letter-spacing: .04em; color: var(--muted); margin: 0 0 6px; }
p { margin: 0 0 12px; }
.lead { font-size: 17px; color: var(--muted); margin: 0 0 18px; }
.muted { color: var(--muted); font-size: 14px; }
code, pre { font-family: "IBM Plex Mono", ui-monospace, SFMono-Regular, Menlo, monospace; }
code { font-size: .9em; background: var(--code); padding: 1px 5px; border-radius: 4px; }
pre { background: var(--code); padding: 12px 14px; border-radius: 8px; overflow-x: auto; font-size: 13px; line-height: 1.5; }
pre code { background: none; padding: 0; }
.tbl { overflow-x: auto; border: 1px solid var(--line); border-radius: 8px; margin: 8px 0 14px; background: var(--card); }
table { border-collapse: collapse; width: 100%; font-size: 14px; min-width: 480px; }
th, td { text-align: left; vertical-align: top; padding: 7px 10px; border-bottom: 1px solid var(--line); }
th { background: var(--soft); font-weight: 600; white-space: nowrap; }
tr:last-child td { border-bottom: none; }
.doc table { border-collapse: collapse; width: 100%; font-size: 14px; margin: 8px 0 14px; display: block; overflow-x: auto; }
.doc th, .doc td { text-align: left; vertical-align: top; padding: 6px 9px; border-bottom: 1px solid var(--line); }
.doc th { background: var(--soft); }
.doc blockquote { margin: 0 0 12px; padding: 6px 14px; border-left: 3px solid var(--accent); background: var(--soft); border-radius: 0 8px 8px 0; }
.doc h2 { font-size: 17px; margin: 18px 0 6px; border: none; padding: 0; }
.doc h3 { font-size: 15px; text-transform: none; letter-spacing: 0; color: var(--fg); margin: 14px 0 4px; }
.doc p, .doc li { max-width: 72ch; }
.doc ul, .doc ol { padding-left: 22px; }
.here { background: var(--soft); border-left: 3px solid var(--accent); padding: 12px 16px; border-radius: 0 8px 8px 0; margin: 14px 0 6px; }
.here p { margin: 0 0 8px; }
.actions { display: flex; flex-wrap: wrap; gap: 8px; }
.btn { display: inline-block; padding: 7px 12px; border-radius: 8px; border: 1px solid var(--line); background: var(--card); color: var(--fg); text-decoration: none; font-size: 14px; cursor: pointer; font-family: inherit; }
.btn.primary { background: var(--accent); color: var(--accent-ink); border-color: var(--accent); }
.btn:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
.strip { display: grid; grid-template-columns: repeat(11, 1fr); gap: 4px; margin: 12px 0 4px; }
.strip div { height: 10px; border-radius: 3px; background: var(--line); }
.strip div.green { background: var(--green); } .strip div.red { background: var(--red); } .strip div.touched { background: var(--grey); }
.legend { font-size: 13px; color: var(--muted); margin: 0 0 14px; }
.card { background: var(--card); border: 1px solid var(--line); border-radius: 10px; padding: 16px 18px; margin: 0 0 14px; }
.card h2 { font-size: 18px; margin: 0; padding: 0; border: none; display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
.card h2 .gates { margin-left: auto; }
.dot { width: 12px; height: 12px; border-radius: 50%; background: var(--grey); flex: none; }
.dot.green { background: var(--green); } .dot.red { background: var(--red); }
.concept { font-style: italic; color: var(--muted); margin: 6px 0 12px; }
.grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
@media (max-width: 640px) { .grid { grid-template-columns: 1fr; } }
ul.checks { margin: 0; padding-left: 18px; } ul.checks li { margin: 2px 0; }
li.pass::marker { color: var(--green); } li.fail::marker { color: var(--red); }
blockquote.refl { margin: 0; padding: 0 0 0 12px; border-left: 3px solid var(--line); white-space: pre-wrap; font-size: 15px; }
.gates span { display: inline-block; padding: 1px 8px; border-radius: 999px; font-size: 12px; border: 1px solid var(--line); margin: 0 4px 4px 0; font-weight: 400; }
.gates span.pass { border-color: var(--green); color: var(--green); }
.gates span.fail { border-color: var(--red); color: var(--red); }
details { border-top: 1px solid var(--line); padding: 8px 0; }
details summary { cursor: pointer; font-weight: 600; font-size: 14px; }
details[open] summary { margin-bottom: 8px; }
.play { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
@media (max-width: 760px) { .play { grid-template-columns: 1fr; } }
.play label { display: block; font-size: 13px; color: var(--muted); margin: 8px 0 4px; }
.play input[type=text], .play textarea, .play select, #pg-base { width: 100%; padding: 8px 10px; border: 1px solid var(--line); border-radius: 8px; background: var(--bg); color: var(--fg); font: inherit; }
.play textarea { min-height: 70px; }
.play .out { background: var(--code); border-radius: 8px; padding: 10px 12px; font-family: "IBM Plex Mono", ui-monospace, Menlo, monospace; font-size: 12.5px; white-space: pre-wrap; min-height: 60px; overflow-x: auto; margin-top: 8px; }
.status { font-size: 13px; color: var(--muted); }
.quiz .q { padding: 10px 0; border-bottom: 1px dashed var(--line); }
.quiz .q:last-child { border-bottom: none; }
.quiz .qt { font-weight: 600; margin: 0 0 6px; }
.quiz .stretch { font-size: 12px; color: var(--muted); font-weight: 400; margin-left: 6px; }
.quiz label.opt { display: block; padding: 5px 8px; border-radius: 6px; cursor: pointer; }
.quiz label.opt:hover { background: var(--soft); }
.quiz label.opt input { margin-right: 8px; }
.quiz .opt.right { background: rgba(46,125,79,.12); }
.quiz .opt.wrong { background: rgba(179,38,30,.10); }
.quiz .why { font-size: 14px; color: var(--muted); margin: 6px 0 0 8px; border-left: 3px solid var(--line); padding-left: 10px; }
.quiz .why.ok { border-left-color: var(--green); }
.quiz .why.no { border-left-color: var(--red); }
.quiz .qbar { display: flex; gap: 8px; align-items: center; margin-top: 10px; flex-wrap: wrap; }
.qscore { font-weight: 400; font-size: 13px; color: var(--muted); }
pre.mermaid { background: var(--card); border: 1px solid var(--line); text-align: center; overflow-x: auto; }
footer { color: var(--muted); font-size: 13px; margin-top: 40px; border-top: 1px solid var(--line); padding-top: 14px; }
/* level 1: action */
.next { border: 2px solid var(--accent); border-radius: 12px; padding: 16px 18px; margin: 18px 0 10px; background: var(--card); }
.next h2 { border: none; padding: 0; margin: 0 0 6px; font-size: 20px; }
.next .what { margin: 0 0 12px; }
.steps { display: flex; gap: 6px; flex-wrap: wrap; margin: 0 0 12px; }
.steps span { padding: 4px 10px; border-radius: 999px; border: 1px solid var(--line); font-size: 13px; color: var(--muted); }
.steps span.done { border-color: var(--green); color: var(--green); }
.steps span.now { background: var(--accent); color: var(--accent-ink); border-color: var(--accent); font-weight: 600; }
/* stepper */
.stepper { display: grid; grid-template-columns: repeat(7, 1fr); gap: 6px; margin: 16px 0 6px; }
.stepper a { display: block; text-decoration: none; color: var(--muted); font-size: 12px; text-align: center; padding: 8px 4px 6px; border-radius: 8px; border: 1px solid var(--line); background: var(--card); }
.stepper a b { display: block; font-size: 15px; color: var(--fg); }
.stepper a small { display: block; font-size: 10.5px; color: var(--muted); margin-top: 2px; }
.stepper a.done { border-color: var(--green); } .stepper a.done b { color: var(--green); }
.stepper a.now { border-color: var(--accent); border-width: 2px; } .stepper a.now b { color: var(--accent); }
.stepper a.red b { color: var(--red); }
@media (max-width: 640px) { .stepper { grid-template-columns: repeat(4, 1fr); } }
/* the loop */
.loop { display: flex; flex-wrap: wrap; align-items: center; gap: 6px; margin: 10px 0 14px; }
.loop span { padding: 6px 10px; border-radius: 8px; background: var(--soft); font-size: 13.5px; }
.loop span.act { background: var(--accent); color: var(--accent-ink); }
.loop i { color: var(--muted); font-style: normal; }
/* codespace card */
.cs { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
@media (max-width: 720px) { .cs { grid-template-columns: 1fr; } }
.term { background: #16191d; color: #d7dde3; border-radius: 8px; padding: 12px 14px; font-family: "IBM Plex Mono", ui-monospace, Menlo, monospace; font-size: 12.5px; line-height: 1.55; overflow-x: auto; white-space: pre; }
.term .ok { color: #6fcf97; } .term .cmd { color: #8fc1ff; } .term .dim { color: #8a949e; }
ol.todo { padding-left: 22px; margin: 0; } ol.todo li { margin: 6px 0; }
/* week cards */
.card.now { border: 2px solid var(--accent); }
.card.ahead h2 { color: var(--muted); }
.wsteps { list-style: none; padding: 0; margin: 12px 0 0; }
.wsteps > li { display: grid; grid-template-columns: 84px minmax(0, 1fr); gap: 12px; padding: 10px 0; border-top: 1px solid var(--line); }
.wsteps > li .k { font-weight: 600; font-size: 14px; }
.wsteps > li .k small { display: block; font-weight: 400; color: var(--muted); font-size: 12px; }
.wsteps > li.now .k { color: var(--accent); }
.wsteps > li.done .k { color: var(--green); }
.wsteps code.cmd { display: block; padding: 6px 10px; margin: 4px 0; background: var(--code); border-radius: 6px; white-space: pre-wrap; }
.wsteps details { border: none; padding: 4px 0 0; }
.wsteps details summary { font-weight: 500; color: var(--accent); }
summary.wsum { list-style: none; cursor: pointer; display: flex; align-items: center; gap: 10px; font-weight: 600; }
summary.wsum::-webkit-details-marker { display: none; }
summary.wsum .muted { font-weight: 400; }
details.wk { border: 1px solid var(--line); border-radius: 10px; padding: 12px 18px; margin: 0 0 10px; background: var(--card); }
details.wk[open] { padding-bottom: 16px; }
.nextlink { text-align: right; font-size: 14px; margin: 14px 0 0; }
.ref details { border: 1px solid var(--line); border-radius: 10px; padding: 10px 16px; margin: 0 0 10px; background: var(--card); }
.ref details summary { font-size: 16px; }
.play .card:target { border: 2px solid var(--accent); }
aside .prog { list-style: none; margin: 0 0 14px; padding: 0; }
aside .prog li a { display: block; padding: 3px 0; color: var(--muted); text-decoration: none; }
aside .prog li a.done { color: var(--green); } aside .prog li a.now { color: var(--accent); font-weight: 600; }
"""

JS = r"""
(function () {
  // side nav: highlight the section in view
  const links = [...document.querySelectorAll('aside ol a[href^="#"]')];
  const targets = links.map(l => document.getElementById(l.getAttribute('href').slice(1))).filter(Boolean);
  if ('IntersectionObserver' in window && targets.length) {
    const io = new IntersectionObserver(entries => {
      entries.forEach(e => { if (e.isIntersecting) links.forEach(l => l.classList.toggle('on', l.getAttribute('href') === '#' + e.target.id)); });
    }, { rootMargin: '-20% 0px -70% 0px' });
    targets.forEach(t => io.observe(t));
  }

  // ---- playground ------------------------------------------------------------------------
  const base = document.getElementById('pg-base');
  const st = document.getElementById('pg-status');
  const cfg = window.HUB || {};
  try { base.value = localStorage.getItem('hub.base') || cfg.liveUrl || ''; } catch (e) { base.value = cfg.liveUrl || ''; }
  base.addEventListener('change', () => { try { localStorage.setItem('hub.base', base.value.trim()); } catch (e) {} });
  function url(p) { return base.value.trim().replace(/\/$/, '') + p; }
  function out(id, v) { document.getElementById(id).textContent = typeof v === 'string' ? v : JSON.stringify(v, null, 2); }
  async function call(id, p, opts) {
    if (!base.value.trim()) { out(id, 'Set the service URL first (your Space, or a public Codespace port).'); return; }
    out(id, '...');
    const t0 = performance.now();
    try {
      const r = await fetch(url(p), opts);
      const ms = Math.round(performance.now() - t0);
      const rid = r.headers.get('X-Request-Id');
      let body; try { body = await r.json(); } catch (e) { body = await r.text(); }
      out(id, 'HTTP ' + r.status + ' in ' + ms + ' ms' + (rid ? '  request ' + rid : '') + '\n' + JSON.stringify(body, null, 2));
      st.textContent = 'last call: HTTP ' + r.status;
      return body;
    } catch (e) {
      out(id, 'Could not reach ' + url(p) + '\n' + e + '\n\nIf the service is running, check that CORS_ORIGINS allows this page and the port is public.');
    }
  }
  const on = (id, fn) => { const el = document.getElementById(id); if (el) el.onclick = fn; };
  on('pg-health', () => call('pg-health-out', '/health'));
  on('pg-upload', async () => {
    const f = document.getElementById('pg-file').files[0];
    if (!f) { out('pg-upload-out', 'Choose a file first.'); return; }
    const fd = new FormData(); fd.append('file', f);
    const b = await call('pg-upload-out', '/documents', { method: 'POST', body: fd });
    if (b && b.id) document.getElementById('pg-docid').value = b.id;
  });
  on('pg-extract', () => call('pg-extract-out', '/documents/' + document.getElementById('pg-docid').value + '/extract', { method: 'POST' }));
  on('pg-index', () => call('pg-search-out', '/index', { method: 'POST' }));
  on('pg-search', () => call('pg-search-out', '/search?q=' + encodeURIComponent(document.getElementById('pg-q').value) + '&k=3'));
  on('pg-ask', () => call('pg-ask-out', '/ask', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ question: document.getElementById('pg-question').value }) }));
  on('pg-task', () => call('pg-task-out', '/tasks/run', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ question: document.getElementById('pg-tq').value, mode: document.getElementById('pg-mode').value, approved: document.getElementById('pg-approved').checked }) }));
  on('pg-traces', () => call('pg-traces-out', '/traces?limit=10'));

  // ---- diagrams --------------------------------------------------------------------------
  if (window.mermaid) {
    const dark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
    mermaid.initialize({ startOnLoad: false, theme: dark ? 'dark' : 'neutral', securityLevel: 'loose' });
    // render only when a panel is opened, so hidden tabs do not get zero-width diagrams
    const rendered = new WeakSet();
    async function renderIn(root) {
      const nodes = [...root.querySelectorAll('pre.mermaid')].filter(n => !rendered.has(n));
      nodes.forEach(n => rendered.add(n));
      if (nodes.length) { try { await mermaid.run({ nodes }); } catch (e) { console.warn(e); } }
    }
    document.querySelectorAll('details').forEach(d => d.addEventListener('toggle', () => { if (d.open) renderIn(d); }));
    renderIn(document.body);
  }

  // ---- self-test ---------------------------------------------------------------------------
  const quiz = (cfg.quiz || {});
  const KEY = 'hub.quiz';
  function load() { try { return JSON.parse(localStorage.getItem(KEY) || '{}'); } catch (e) { return {}; } }
  function save(state) { try { localStorage.setItem(KEY, JSON.stringify(state)); } catch (e) {} }
  function totals(state) {
    let got = 0, of = 0;
    for (const w in quiz) { of += quiz[w].length; got += (state[w] || {}).score || 0; }
    return { got, of };
  }
  function paintTotals(state) {
    const t = totals(state);
    const el = document.getElementById('qtotal');
    if (el) el.textContent = t.of ? '<br>self-test ' + t.got + '/' + t.of + ' (yours only)' : '';
    if (el) el.innerHTML = el.textContent;
    for (const w in quiz) {
      const sc = document.getElementById('qscore-' + w);
      const st = state[w];
      if (sc) sc.textContent = st && st.done ? '· ' + st.score + '/' + quiz[w].length : '';
    }
  }
  function esc(s) { return String(s).replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c])); }
  function build(w) {
    const host = document.getElementById('quiz-' + w);
    if (!host || host.dataset.built) return;
    host.dataset.built = '1';
    const qs = quiz[w];
    let html = '';
    qs.forEach((q, i) => {
      html += '<div class="q" data-i="' + i + '"><p class="qt">Q' + q.n + '. ' + esc(q.text) + (q.stretch ? '<span class="stretch">stretch: core / pro</span>' : '') + '</p>';
      q.options.forEach((o, j) => {
        html += '<label class="opt" data-j="' + j + '"><input type="radio" name="q' + w + '-' + i + '" value="' + j + '">' + esc(o.text) + '</label>';
      });
      html += '<div class="why" hidden></div></div>';
    });
    html += '<div class="qbar"><button class="btn primary" data-act="check">Check answers</button><button class="btn" data-act="reset">Reset</button><span class="status" data-role="result"></span></div>';
    host.innerHTML = html;
    host.querySelector('[data-act=check]').onclick = () => check(w);
    host.querySelector('[data-act=reset]').onclick = () => { const st = load(); delete st[w]; save(st); host.dataset.built = ''; host.innerHTML = ''; build(w); paintTotals(load()); };
  }
  function check(w) {
    const host = document.getElementById('quiz-' + w);
    const qs = quiz[w];
    let score = 0, answered = 0;
    qs.forEach((q, i) => {
      const box = host.querySelector('.q[data-i="' + i + '"]');
      const picked = box.querySelector('input:checked');
      const why = box.querySelector('.why');
      box.querySelectorAll('label.opt').forEach(l => l.classList.remove('right', 'wrong'));
      if (!picked) { why.hidden = true; return; }
      answered++;
      const j = Number(picked.value);
      const ok = q.options[j].correct;
      if (ok) score++;
      box.querySelectorAll('label.opt').forEach(l => {
        const jj = Number(l.dataset.j);
        if (q.options[jj].correct) l.classList.add('right');
        else if (jj === j) l.classList.add('wrong');
      });
      const optWhy = q.options[j].why ? (ok ? '' : 'Not quite: ' + q.options[j].why + ' ') : '';
      why.textContent = optWhy + (q.why || '');
      why.className = 'why ' + (ok ? 'ok' : 'no');
      why.hidden = false;
    });
    host.querySelector('[data-role=result]').textContent = answered < qs.length
      ? score + ' right of ' + answered + ' answered (' + (qs.length - answered) + ' left)'
      : score + ' of ' + qs.length + ' right';
    const st = load(); st[w] = { score, done: answered === qs.length, at: Date.now() }; save(st);
    paintTotals(st);
  }
  document.querySelectorAll('details.quiz').forEach(d => d.addEventListener('toggle', () => { if (d.open) build(d.dataset.week); }));
  paintTotals(load());
})();
"""


def _gh(repo: str, path: str) -> str:
    return f"https://github.com/{repo}/blob/main/{path}"


def _cmds(cmds: list[str]) -> str:
    return "".join(f'<code class="cmd">{esc(c)}</code>' for c in cmds)


def week_card(w: Week, repo: str, current: bool) -> str:
    gates = "".join(
        f'<span class="{"pass" if ok else "fail"}">{esc(k)}</span>'
        for k, ok in ((w.report or {}).get("gates") or {}).items()
    )
    tests = "".join(
        f'<li class="{"pass" if t["outcome"] == "passed" else "fail"}">'
        f"{esc(t['id'].removeprefix('test_').replace('_', ' '))}</li>"
        for t in w.tests
    )
    step = w.step
    order = ["Read", "Run", "Build", "Check", "Submit"]
    idx = order.index(step)

    def cls(name: str) -> str:
        i = order.index(name)
        if w.done:
            return "done"
        return "done" if i < idx else ("now" if i == idx else "")

    # Read
    read_body = (
        f"<details{' open' if current and step == 'Read' else ''}><summary>Concept, diagrams and reading list</summary>"
        f"<div class='doc'>{w.concept_html}</div></details>"
        if w.concept_html
        else f"<div class='doc'>{w.readme_html}</div>"
    )
    read = (
        f"<li class='{cls('Read')}'><div class='k'>Read<small>~1 h</small></div><div>"
        f"<p>One sentence to be able to say back: <i>{esc(CONCEPTS.get(w.n, ''))}</i> "
        f"Write it in your words in <code>reflections/week-{w.n}.md</code>, Q1.</p>{read_body}</div></li>"
    )
    # Run
    run = (
        f"<li class='{cls('Run')}'><div class='k'>Run<small>~2 h, change nothing</small></div><div>"
        f"{_cmds(WEEK_RUN.get(w.n, []))}"
        f"<details><summary>What to look for, and the reading questions</summary><div class='doc'>{w.readme_html}</div></details>"
        f"</div></li>"
    )
    # Build
    files = "".join(
        f'<li><code>{esc(f)}</code> &middot; <a href="{_gh(repo, f)}">on GitHub</a></li>'
        for f in WEEK_BUILD.get(w.n, [])
    )
    route_note = md(ROOT / "weeks" / str(w.n) / "routes" / f"{ROUTE}.md")
    route_html = (
        f"<details open><summary>Your route: {esc(ROUTE)}</summary><div class='doc'>{route_note}</div>"
        + (
            f"<p class='muted'>Worked example: <code>weeks/{w.n}/routes/worked_example.py</code> "
            f"&middot; <a href='{_gh(repo, f'weeks/{w.n}/routes/worked_example.py')}'>on GitHub</a></p>"
            if ROUTE == "start"
            and (ROOT / "weeks" / str(w.n) / "routes" / "worked_example.py").exists()
            else ""
        )
        + "</details>"
        if route_note
        else ""
    )
    build = (
        f"<li class='{cls('Build')}'><div class='k'>Build<small>~4–5 h</small></div><div>"
        f"<p>{esc(WEEK_BUILD_NOTE.get(w.n, ''))}</p>{route_html}"
        + (f"<ul>{files}</ul>" if files else "")
        + (
            f"<p>Then measure: <code>{esc(WEEK_MEASURE[w.n])}</code> and paste the table into your reflection.</p>"
            if w.n in WEEK_MEASURE
            else ""
        )
        + "</div></li>"
    )
    # Check
    rep_html = ""
    for rep_key in WEEK_REPORTS.get(w.n, []):
        title, fn = REPORTS[rep_key]
        body = fn()
        if body:
            rep_html += f"<details><summary>{title} (last run)</summary>{body}</details>"
    check = (
        f"<li class='{cls('Check')}'><div class='k'>Check<small>as often as you like</small></div><div>"
        f"<code class='cmd'>make check WEEK={w.n}</code>"
        f"<div class='gates'>{gates or '<span>gate not run yet</span>'}</div>"
        + (
            f"<details><summary>This week's checks</summary><ul class='checks'>{tests}</ul>"
            f"<div class='doc'>{w.checks_html}</div></details>"
            if tests or w.checks_html
            else ""
        )
        + rep_html
        + "</div></li>"
    )
    # Submit
    pr_line = (
        f'<a href="{esc(w.pr.get("url", "#"))}">PR #{esc(w.pr.get("number", "?"))}</a> &middot; '
        f"{esc(w.pr.get('state', ''))} &middot; {esc(w.pr.get('review_comments', 0))} mentor comments"
        if w.pr
        else f"No pull request yet. Branch <code>week-{w.n}</code> &rarr; PR to <code>main</code>."
    )
    refl = (
        f"<blockquote class='refl'>{esc(w.reflection_q1)}</blockquote>"
        if w.reflection_q1
        else f"<span class='muted'>reflections/week-{w.n}.md not written yet</span>"
    )
    session = WEEK_SESSION.get(w.n)
    after = (
        f"<p class='muted' style='margin-top:8px'><b>{esc(session)}</b> follows this week: send the PR link a day before.</p>"
        if session
        else "<p class='muted' style='margin-top:8px'>Self-directed week: no session. The gate, the held-out inputs and the self-test are your feedback; this PR is reviewed at the next session.</p>"
    )
    submit = (
        f"<li class='{cls('Submit')}'><div class='k'>Submit<small>{'a day before the session' if session else 'when the gate is green'}</small></div><div>"
        f"<p>{pr_line}</p><h3>Your reflection, Q1</h3>{refl}{after}"
        f"</div></li>"
    )
    quiz = (
        f"<li><div class='k'>Self-test<small>optional</small></div><div>"
        f"<details class='quiz' data-week='{w.n}'><summary>{len(w.quiz)} questions <span class='qscore' id='qscore-{w.n}'></span></summary>"
        f"<div id='quiz-{w.n}'></div></details></div></li>"
        if w.quiz
        else ""
    )
    try_it = (
        f"<li><div class='k'>Try it<small>live</small></div><div>"
        f"<a href='#pg-w{w.n}'>Call this week's endpoint from the playground</a></div></li>"
        if 0 <= w.n <= 5
        else ""
    )
    steps_html = f"<ol class='wsteps'>{read}{run}{build}{check}{submit}{quiz}{try_it}</ol>"
    status = "done" if w.done else ("now" if current else ("red" if w.state == "red" else "ahead"))
    title = f"<span class='dot {w.state}'></span>Week {w.n} &mdash; {esc(w.title)}"
    if current:
        return (
            f"<section class='card now' id='week-{w.n}'><h2>{title}"
            f"<span class='muted'>&middot; this week</span></h2>{steps_html}</section>"
        )
    label = "done" if w.done else ("started" if w.state != "not started" else "ahead")
    return (
        f"<details class='wk {status}' id='week-{w.n}'><summary class='wsum'>{title}"
        f"<span class='muted'>&middot; {label}</span></summary>{steps_html}</details>"
    )


def _split_track() -> dict[str, str]:
    """docs/track.md holds three level-2 sections; return each rendered, keyed by heading."""
    path = ROOT / "docs" / "track.md"
    if not path.exists():
        return {}
    text = re.sub(r"<!--.*?-->", "", path.read_text(encoding="utf-8"), flags=re.S)
    parts: dict[str, str] = {}
    for m in re.finditer(r"^## (.+?)\n(.*?)(?=^## |\Z)", text, re.S | re.M):
        body = MD.render(m.group(2))
        parts[m.group(1).strip()] = _MERMAID.sub(
            lambda mm: f'<pre class="mermaid">{html.unescape(mm.group(1))}</pre>', str(body)
        )
    return parts


def material_links(weeks: list[Week], repo: str) -> str:
    items = []
    for w in weeks:
        base = f"https://github.com/{esc(repo)}/blob/main/weeks/{w.n}"
        parts = [f'<a href="{base}/README.md">exercise</a>']
        if (ROOT / "weeks" / str(w.n) / "CONCEPT.md").exists():
            parts.insert(0, f'<a href="{base}/CONCEPT.md">concept</a>')
        if (ROOT / "weeks" / str(w.n) / "CHECKS.md").exists():
            parts.append(f'<a href="{base}/CHECKS.md">checks</a>')
        if (ROOT / "weeks" / str(w.n) / "QUIZ.md").exists():
            parts.append(f'<a href="{base}/QUIZ.md">quiz</a>')
        items.append(f"<li>Week {w.n}: {' &middot; '.join(parts)}</li>")
    return "".join(items)


def render(weeks: list[Week], route: str, live_url: str, repo: str) -> str:
    gh = f"https://github.com/{esc(repo)}"
    codespace = f"https://codespaces.new/{esc(repo)}?quickstart=1"
    fresh = all(w.report is None for w in weeks)
    current = next((w for w in weeks if not w.done), None)
    done_n = sum(1 for w in weeks if w.done)

    # ---- 1. your next step
    if fresh or current is None and not weeks:
        next_html = (
            "<div class='next'><h2>Step 0: open a Codespace</h2>"
            "<p class='what'>Nothing is installed yet and nothing needs to be. One click builds your machine, "
            "installs everything and runs the first check. Then <code>weeks/0/README.md</code> opens by itself.</p>"
            f"<div class='actions'><a class='btn primary' href='{codespace}'>Open in Codespaces</a>"
            f"<a class='btn' href='#codespace'>What happens next</a></div></div>"
        )
    elif current is None:
        next_html = (
            "<div class='next'><h2>Every week is green</h2><p class='what'>Write the one page that says what it did "
            "for the business, then the final session.</p>"
            "<div class='actions'><a class='btn primary' href='#week-6'>Open Week 6</a></div></div>"
        )
    else:
        w = current
        step = w.step
        chips = "".join(
            f"<span class='{'done' if STEPS.index(st) < STEPS.index(step) else ('now' if st == step else '')}'>{i + 1}. {st}</span>"
            for i, st in enumerate(STEPS)
        )
        what = {
            "Read": f"Read the concept, then write its sentence in your own words in <code>reflections/week-{w.n}.md</code>.",
            "Run": "Run the elaboration scripts and read the files listed. Change nothing yet.",
            "Build": f"Build <code>{esc(', '.join(WEEK_BUILD.get(w.n, [])) or 'the Week 0 tasks')}</code>, then <code>make check WEEK={w.n}</code> until it is green.",
            "Submit": (
                "Your PR is open: send the link to your mentor 24 h before the session."
                if w.pr and not w.merged
                else f"Gate is green. Open the PR <code>week-{w.n} &rarr; main</code> and finish your reflection."
            ),
        }[step]
        primary = {
            "Read": (f"#week-{w.n}", f"Open Week {w.n}"),
            "Run": (f"#week-{w.n}", f"Open Week {w.n}"),
            "Build": (
                (_gh(repo, WEEK_BUILD[w.n][0]), f"Open {WEEK_BUILD[w.n][0].split('/')[-1]}")
                if WEEK_BUILD.get(w.n)
                else (f"#week-{w.n}", f"Open Week {w.n}")
            ),
            "Submit": (
                (esc(w.pr["url"]), f"Open PR #{w.pr.get('number', '')}")
                if w.pr
                else (f"{gh}/compare/main...week-{w.n}?expand=1", "Open a pull request")
            ),
        }[step]
        next_html = (
            f"<div class='next'><h2>Week {w.n}: {esc(w.title)}</h2>"
            f"<div class='steps'>{chips}</div><p class='what'>{what}</p>"
            f"<div class='actions'><a class='btn primary' href='{primary[0]}'>{primary[1]}</a>"
            f"<a class='btn' href='{codespace}'>Open in Codespaces</a></div></div>"
        )

    # ---- stepper
    stepper = ""
    for w in weeks:
        c = "done" if w.done else ("now" if current is w else ("red" if w.state == "red" else ""))
        mark = "&#10003;" if w.done else ("&#9679;" if current is w else "&#9675;")
        tag = (
            f"<small>{esc(WEEK_SESSION[w.n].split(':')[0])}</small>"
            if w.n in WEEK_SESSION
            else "<small>self-directed</small>"
        )
        stepper += f"<a class='{c}' href='#week-{w.n}'><b>{mark}</b>Week {w.n}{tag}</a>"

    # ---- sidebar progress
    prog = "".join(
        f"<li><a class='{'done' if w.done else ('now' if current is w else '')}' href='#week-{w.n}'>"
        f"{'&#10003;' if w.done else ('&#9679;' if current is w else '&#9675;')} Week {w.n}</a></li>"
        for w in weeks
    )

    live_line = (
        f'Live service: <a href="{esc(live_url)}/docs">{esc(live_url)}</a> (<a href="{esc(live_url)}/health">/health</a>)'
        if live_url
        else "No live URL set. Week 6 publishes a runnable image, which needs no account; a clickable URL is optional (Reference &rarr; Start here)."
    )
    track = _split_track()
    area_state: dict[int, str] = {}
    for w in weeks:
        for a in WEEK_AREAS.get(w.n, []):
            area_state[a] = w.state if w.state != "not started" else "touched"
    strip = "".join(
        f'<div class="{area_state.get(a, "")}" title="{a}. {esc(AREAS[a])}"></div>'
        for a in range(1, 12)
    )
    start_html = md(ROOT / "README.md")
    reports_html = (
        "".join(
            f"<h3 style='margin-top:14px'>{title}</h3>{body}"
            for _key, (title, fn) in REPORTS.items()
            if (body := fn())
        )
        or "<p class='muted'>No reports yet. They appear as each week's measurement script runs.</p>"
    )
    quiz_data = {
        str(w.n): [
            {"n": q.n, "text": q.text, "stretch": q.stretch, "why": q.why, "options": q.options}
            for q in w.quiz
        ]
        for w in weeks
        if w.quiz
    }
    cfg = json.dumps({"liveUrl": live_url, "repo": repo, "quiz": quiz_data})
    cards = "".join(week_card(w, repo, current is w) for w in weeks)

    term = (
        "<div class='term'><span class='dim'>== installing uv</span>\n<span class='dim'>== installing the project</span>\n"
        "<span class='dim'>== first check</span>\n  <span class='ok'>PASS</span>  ruff   <span class='ok'>PASS</span>  format   "
        "<span class='ok'>PASS</span>  mypy   <span class='ok'>PASS</span>  tests[fake_a]\n\n"
        "<span class='ok'>Ready.</span> Open weeks/0/README.md and run: make run\n\n"
        "<span class='dim'>$</span> <span class='cmd'>make run</span>\n"
        "INFO:     Uvicorn running on http://0.0.0.0:8000  <span class='dim'>(a port-forward notification appears: open it, add /docs)</span>\n\n"
        "<span class='dim'>$</span> <span class='cmd'>git checkout -b week-1</span>\n"
        "<span class='dim'>$</span> <span class='cmd'>make check WEEK=1</span>\n"
        "  <span class='ok'>PASS</span>  ruff   ...   9 failed   <span class='dim'>(red until you build app/api/extract.py: that is the exercise)</span></div>"
    )

    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>AI Engineering track</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:ital,wght@0,400;0,500;0,600;1,400&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>{CSS}</style>
<script>window.HUB = {cfg};</script>
</head>
<body><div class="wrap">
<aside>
  <p class="eyebrow">Your progress</p>
  <ul class="prog">{prog}</ul>
  <p class="eyebrow">On this page</p>
  <ol>
    <li><a href="#next">Your next step</a></li>
    <li><a href="#loop">How you work</a></li>
    <li><a href="#codespace">Inside your Codespace</a></li>
    <li><a href="#weeks">The six weeks</a></li>
    <li><a href="#playground">Playground</a></li>
    <li><a href="#reference">Reference</a></li>
  </ol>
  <p class="side"><a href="{gh}">{esc(repo)}</a><br>route <b>{esc(route)}</b><br>{done_n} of {len(weeks)} weeks done<span id="qtotal"></span></p>
</aside>

<article>
<h1>AI Engineering track</h1>
<p class="lead">Six weeks. One service that grows into an AI product you can deploy, measure and defend. This page is built from your repository on every merge; nothing on it is typed in by hand.</p>

<div id="next">{next_html}</div>
<div class="stepper">{stepper}</div>
<p class="legend">Done means the week's gate is green and its pull request is merged. Four mentor sessions: Discovery, Direction, Observation, Defence; the other weeks are self-directed. Click a week to open it.</p>

<h2 id="loop">How you work</h2>
<p>The same loop every week. Six words you will see everywhere on this page and in the repo.</p>
<div class="loop">
  <span>Codespace</span><i>&rarr;</i><span>branch <code>week-N</code></span><i>&rarr;</i>
  <span class="act">Read</span><i>&rarr;</i><span class="act">Run</span><i>&rarr;</i><span class="act">Build</span><i>&rarr;</i>
  <span class="act">Check</span><i>&rarr;</i><span class="act">Submit</span><i>&rarr;</i><span>merge</span><i>&rarr;</i><span class="act">Defend</span> <i>at one of the four sessions</i>
</div>
<div class="doc">{track.get("How a week works", "")}</div>
<p class="nextlink">Next: <a href="#codespace">inside your Codespace &rarr;</a></p>

<h2 id="codespace">Inside your Codespace</h2>
<p>One click builds your machine. Here is what is already done when it opens, what you do, and what you should see.</p>
<div class="cs">
  <div class="card"><h3>Already done for you</h3>
    <ul><li>Python 3.12, <code>uv</code>, Docker, Redis</li><li>Every dependency installed (<code>uv sync</code>)</li><li><code>.env</code> created from <code>.env.example</code></li><li>The Week 0 gate run once</li><li><code>weeks/0/README.md</code> opened</li></ul>
    <h3 style="margin-top:12px">You do</h3>
    <ol class="todo">
      <li>Paste one model key: <code>MODEL_API_KEY=...</code> in <code>.env</code> (free Gemini key from <a href="https://aistudio.google.com/apikey">AI Studio</a>), or set the Codespaces secret <code>GEMINI_API_KEY</code>.</li>
      <li><code>make run</code> and open the forwarded port at <code>/docs</code>.</li>
      <li>Each week: <code>git checkout -b week-N</code>, then Read, Run, Build, <code>make check WEEK=N</code>, PR.</li>
      <li>When you stop for the day: <b>Codespaces &rarr; Stop</b> (or set idle timeout to 15 min).</li>
    </ol>
    <div class="actions" style="margin-top:12px"><a class="btn primary" href="{codespace}">Open in Codespaces</a></div>
  </div>
  <div class="card"><h3>What you should see</h3>{term}
    <p class="muted" style="margin-top:8px">If the container opens in <i>recovery mode</i>: <code>pip install uv && uv sync</code>, then Ctrl+Shift+P &rarr; <i>Codespaces: Rebuild Container</i>.</p>
  </div>
</div>
<p class="nextlink">Next: <a href="#weeks">the six weeks &rarr;</a></p>

<h2 id="weeks">The six weeks</h2>
<p>Your current week is open. The others fold to one line until you get there; nothing is locked.</p>
{cards}
<p class="nextlink">Next: <a href="#playground">try your service &rarr;</a></p>

<h2 id="playground">Playground</h2>
<p>Call your running service from here: your Space (set the repository variable <code>LIVE_URL</code>) or a Codespace port you have made public. Only the URL is remembered, in your browser. {live_line}</p>
<label for="pg-base" class="status">Service URL</label>
<input type="text" id="pg-base" placeholder="http://localhost:7860  or  https://your-service.onrender.com">
<p id="pg-status" class="status"></p>
<div class="play">
  <div class="card" id="pg-w0"><h3>Week 0 &middot; health and upload</h3>
    <button class="btn" id="pg-health">GET /health</button>
    <div class="out" id="pg-health-out"></div>
    <label for="pg-file">Upload a .md / .txt / .csv / .pdf</label>
    <input type="file" id="pg-file"> <button class="btn" id="pg-upload">POST /documents</button>
    <div class="out" id="pg-upload-out"></div>
  </div>
  <div class="card" id="pg-w1"><h3>Week 1 &middot; extract</h3>
    <label for="pg-docid">Document id</label>
    <input type="text" id="pg-docid" value="1">
    <button class="btn" id="pg-extract">POST /documents/{{id}}/extract</button>
    <div class="out" id="pg-extract-out"></div>
    <p class="status">Call it twice: the second answer must say <code>cached: true</code>.</p>
  </div>
  <div class="card" id="pg-w2"><h3>Week 2 &middot; index and search</h3>
    <button class="btn" id="pg-index">POST /index</button>
    <label for="pg-q">Query</label>
    <input type="text" id="pg-q" value="mileage rate personal car">
    <button class="btn" id="pg-search">GET /search</button>
    <div class="out" id="pg-search-out"></div>
  </div>
  <div class="card" id="pg-w3"><h3>Week 3 &middot; ask</h3>
    <label for="pg-question">Question</label>
    <textarea id="pg-question">What is the London hotel cap in the Contoso expenses policy?</textarea>
    <button class="btn" id="pg-ask">POST /ask</button>
    <div class="out" id="pg-ask-out"></div>
    <p class="status">Try one the documents cannot answer. A good system declines.</p>
  </div>
  <div class="card" id="pg-w4"><h3>Week 4 &middot; one task, three ways</h3>
    <label for="pg-tq">Question</label>
    <input type="text" id="pg-tq" value="Which invoice has the largest total due, and what is it?">
    <label for="pg-mode">Mode</label>
    <select id="pg-mode"><option value="plain">plain code</option><option value="workflow">workflow</option><option value="agent" selected>agent</option></select>
    <label><input type="checkbox" id="pg-approved"> approve tools that cost money</label>
    <button class="btn" id="pg-task">POST /tasks/run</button>
    <div class="out" id="pg-task-out"></div>
  </div>
  <div class="card" id="pg-w5"><h3>Week 5 &middot; traces</h3>
    <button class="btn" id="pg-traces">GET /traces</button>
    <div class="out" id="pg-traces-out"></div>
    <p class="status">Every call above returned an <code>X-Request-Id</code>; look it up here.</p>
  </div>
</div>

<h2 id="reference">Reference</h2>
<p>Everything else, folded. Open what you need.</p>
<div class="ref">
  <details id="track"><summary>The track: eleven areas, six weeks</summary><div class="doc">{track.get("The track", "")}</div>
    <div class="strip">{strip}</div><p class="legend">The eleven areas as they stand in your repo. Green: that week's gate passed. Red: not yet. Grey: reached, not run.</p></details>
  <details id="sessions"><summary>Sessions and gates: how you are assessed</summary><div class="doc">{track.get("Sessions and gates", "")}</div></details>
  <details id="start"><summary>Start here: commands, model keys, deploying, keeping it free (the README)</summary><div class="doc">{start_html}</div></details>
  <details id="reports"><summary>Reports: every measurement your repo has produced</summary>{reports_html}</details>
  <details id="links"><summary>Links</summary><div class="doc">
    <ul>
      <li><a href="{gh}">Repository</a> &middot; <a href="{gh}/pulls">pull requests</a> &middot; <a href="{gh}/actions">CI runs</a> &middot; <a href="{gh}/tree/main/reflections">reflections</a></li>
      <li><a href="{codespace}">Open in Codespaces</a></li>
      <li>{live_line}</li>
    </ul>
    <h3>Material on GitHub</h3><ul>{material_links(weeks, repo)}</ul>
    <h3>Providers</h3>
    <ul>
      <li><a href="https://aistudio.google.com/apikey">Gemini key (free tier, default)</a></li>
      <li><a href="https://console.groq.com/keys">Groq key (second provider)</a></li>
      <li><a href="https://render.com">Render</a> for an optional clickable URL (the release publishes a runnable image either way)</li>
    </ul>
    <h3>For mentors</h3><p>Runbooks, held-out sets, the rubric and reference solutions live in the private mentor kit, not here.</p>
  </div></details>
</div>

<footer>Built by <code>scripts/build_pages.py</code> on every merge to <code>main</code> from <code>docs/track.md</code>, <code>README.md</code>, <code>weeks/</code>, <code>reports/</code>, <code>reflections/</code> and the pull requests. Nothing here is self-reported.</footer>
</article>
</div>
<script src="https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js"></script>
<script>{JS}</script>
</body></html>
"""


def main() -> int:
    weeks = load_weeks()
    route = ROUTE
    live_url = os.environ.get("LIVE_URL", "").strip().rstrip("/")
    repo = os.environ.get("GITHUB_REPOSITORY", "anilmodest/ai-eng-track")
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(render(weeks, route, live_url, repo), encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)} ({len(weeks)} weeks, {OUT.stat().st_size // 1024} KB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
