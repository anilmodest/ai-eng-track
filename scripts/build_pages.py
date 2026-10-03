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

import csv
import html
import json
import os
import re
from dataclasses import dataclass, field
from datetime import UTC, datetime
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
/* The palette and the restraint come from the platform's own BUILD page, so a fellow moving
   between the two is not changing worlds. Everything here serves one rule: this page answers
   "where am I and what is next", and nothing else. The detail lives one click away. */
:root {
  --ink:#1f2430; --muted:#6b7280; --line:#e7e8f2; --paper:#f5f6fb; --white:#fff;
  --indigo:#7654a2; --indigo-dark:#543874; --indigo-soft:#f3eef8;
  --green:#1a9a55; --green-soft:#e7f6ec; --amber:#c8790a; --amber-soft:#fbf0da;
  --red:#b3261e; --red-soft:#fdecea;
  --radius:14px; --shadow:0 1px 2px rgba(20,20,50,.04), 0 8px 24px rgba(20,20,50,.05);
}
/* Light by default, because the platform the fellow logs into is light and moving between
   the two should not feel like two different products. Dark is a choice, kept in this browser. */
:root[data-theme="dark"] {
  --ink:#e9eaf2; --muted:#9aa1b4; --line:#2b2f3e; --paper:#14161d; --white:#1b1e27;
  --indigo:#a98fd0; --indigo-dark:#c3aee4; --indigo-soft:#241e33;
  --green-soft:#132a1d; --amber-soft:#2d2415; --red-soft:#2d1917;
}
* { box-sizing:border-box; }
body {
  margin:0; background:var(--paper); color:var(--ink);
  font:16px/1.6 Inter,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
  -webkit-font-smoothing:antialiased;
}
.wrap { max-width:860px; margin:0 auto; padding:0 16px 72px; }
a { color:var(--indigo-dark); }
code, pre { font-family:ui-monospace,SFMono-Regular,Consolas,monospace; }

/* top bar */
.bar { background:var(--white); border-bottom:1px solid var(--line); }
.bar .wrap { display:flex; align-items:center; gap:12px; padding:14px 16px; }
.bar .mark { font-family:Georgia,"Times New Roman",serif; font-size:17px; letter-spacing:-.01em; }
.bar .sp { flex:1; }
.bar a { color:var(--muted); text-decoration:none; font-size:14px; }
.bar a:hover { color:var(--ink); }

/* hero */
.kicker { font-size:12px; letter-spacing:.09em; text-transform:uppercase; color:var(--indigo);
  font-weight:600; margin:28px 0 8px; }
h1 { font-family:Georgia,"Times New Roman",serif; font-size:30px; line-height:1.22;
  letter-spacing:-.01em; margin:0 0 10px; font-weight:400; }
.lede { color:var(--muted); margin:0 0 20px; max-width:60ch; }

/* status strip */
.strip { display:flex; flex-wrap:wrap; gap:8px; margin:0 0 26px; }
.chip { display:inline-flex; align-items:center; gap:6px; background:var(--white);
  border:1px solid var(--line); border-radius:999px; padding:5px 12px; font-size:13px;
  color:var(--muted); text-decoration:none; }
.chip b { color:var(--ink); font-weight:600; }
.chip.go { background:var(--indigo-soft); border-color:transparent; color:var(--indigo-dark); }
.dot { width:7px; height:7px; border-radius:50%; background:var(--muted); }
.dot.green { background:var(--green); } .dot.red { background:var(--red); }
.dot.amber { background:var(--amber); }

/* cards */
.card { background:var(--white); border:1px solid var(--line); border-radius:var(--radius);
  box-shadow:var(--shadow); padding:18px 20px; margin:0 0 14px; }
h2 { font-size:15px; margin:34px 0 12px; letter-spacing:.01em; }
h2 .n { color:var(--muted); font-weight:500; margin-right:8px; }

/* the three steps */
.step { display:flex; gap:16px; align-items:flex-start; }
.step-index { flex:none; width:34px; height:34px; border-radius:10px; background:var(--indigo-soft);
  color:var(--indigo-dark); font-size:13px; font-weight:600; display:flex; align-items:center;
  justify-content:center; }
.step h3 { margin:2px 0 4px; font-size:16px; font-weight:600; }
.step p { margin:0 0 8px; color:var(--muted); font-size:14px; }
.step .status { font-size:13px; color:var(--muted); }

/* the week list: one row per week, nothing more */
.weeks { background:var(--white); border:1px solid var(--line); border-radius:var(--radius);
  box-shadow:var(--shadow); overflow:hidden; }
.wk { display:flex; align-items:center; gap:14px; padding:14px 18px; border-top:1px solid var(--line);
  text-decoration:none; color:inherit; }
.wk:first-child { border-top:0; }
.wk:hover { background:var(--indigo-soft); }
.wk .num { flex:none; width:28px; height:28px; border-radius:8px; background:var(--paper);
  border:1px solid var(--line); font-size:13px; color:var(--muted); display:flex;
  align-items:center; justify-content:center; }
.wk .body { flex:1; min-width:0; }
.wk .t { font-weight:600; font-size:15px; }
.wk .h { color:var(--muted); font-size:13px; white-space:nowrap; overflow:hidden;
  text-overflow:ellipsis; }
.wk .go { flex:none; color:var(--indigo); font-size:18px; }
.pill { flex:none; font-size:12px; padding:3px 9px; border-radius:999px; background:var(--paper);
  color:var(--muted); border:1px solid var(--line); }
.pill.green { background:var(--green-soft); color:var(--green); border-color:transparent; }
.pill.red { background:var(--red-soft); color:var(--red); border-color:transparent; }
.pill.amber { background:var(--amber-soft); color:var(--amber); border-color:transparent; }
.wk.current { background:var(--indigo-soft); }

/* next step */
.next { border-left:3px solid var(--indigo); }
.next h3 { margin:0 0 6px; font-size:16px; font-weight:600; }
.next p { margin:0 0 10px; color:var(--muted); font-size:14px; }

pre { background:var(--paper); border:1px solid var(--line); border-radius:10px; padding:12px 14px;
  overflow:auto; font-size:13px; margin:0 0 10px; }
code { font-size:.92em; }
:not(pre) > code { background:var(--paper); border:1px solid var(--line); border-radius:5px;
  padding:1px 5px; }

.btn { display:inline-block; border:1px solid var(--line); background:var(--white); color:var(--ink);
  border-radius:9px; padding:7px 14px; font-size:14px; text-decoration:none; cursor:pointer; }
.btn.primary { background:var(--indigo); border-color:var(--indigo); color:#fff; }
.btn:hover { border-color:var(--indigo); }

.links { display:grid; grid-template-columns:repeat(auto-fill,minmax(230px,1fr)); gap:8px; }
.links a { display:block; background:var(--white); border:1px solid var(--line); border-radius:10px;
  padding:10px 13px; text-decoration:none; color:var(--ink); font-size:14px; }
.links a span { display:block; color:var(--muted); font-size:12px; }
.links a:hover { border-color:var(--indigo); }

.fineprint { color:var(--muted); font-size:13px; margin:28px 0 0; }

.meter { height:6px; background:var(--line); border-radius:99px; overflow:hidden; margin:0 0 22px; }
.meter i { display:block; height:100%; background:var(--indigo); border-radius:99px;
  transition:width .3s; }

.tog { background:none; border:0; color:var(--muted); font-size:15px; cursor:pointer; padding:0;
  line-height:1; }
.tog:hover { color:var(--ink); }

.checks .sum { display:flex; align-items:center; gap:10px; font-size:14px; margin:0; }
.checks details { border-top:1px solid var(--line); margin-top:12px; padding-top:10px; }
.checks summary { font-size:14px; font-weight:500; }
.checks ul { list-style:none; margin:8px 0 4px; padding:0; }
.checks li { padding:6px 0; border-top:1px solid var(--line); font-size:13px;
  display:flex; gap:10px; align-items:baseline; }
.checks li:first-child { border-top:0; }
.checks li .f { color:var(--muted); font-size:12px; margin-left:auto; white-space:nowrap; }
.checks li b { font-family:ui-monospace,SFMono-Regular,Consolas,monospace; font-weight:500; }
.checks li.fail b { color:var(--red); }
.checks li.pass b { color:var(--ink); }

.todo { background:var(--indigo-soft); border-color:transparent; }
.todo h3 { margin:0 0 4px; font-size:15px; }
.todo p { margin:0 0 10px; font-size:14px; color:var(--indigo-dark); }
.todo pre { background:var(--white); }
.caveat { color:var(--amber); font-size:12px; }

/* week detail pages */
.back { display:inline-block; margin:22px 0 0; color:var(--muted); font-size:14px;
  text-decoration:none; }
.back:hover { color:var(--ink); }
.prose { background:var(--white); border:1px solid var(--line); border-radius:var(--radius);
  box-shadow:var(--shadow); padding:4px 22px 18px; }
.prose h2 { font-size:17px; margin:26px 0 10px; }
.prose h3 { font-size:15px; margin:20px 0 8px; }
.prose table { border-collapse:collapse; width:100%; font-size:14px; margin:0 0 14px; }
.prose th { text-align:left; border-bottom:1px solid var(--line); padding:7px 9px;
  background:var(--paper); }
.prose td { border-bottom:1px solid var(--line); padding:7px 9px; vertical-align:top; }
.tbl { overflow-x:auto; }
.tbl table { border-collapse:collapse; width:100%; font-size:14px; }
.tbl th { text-align:left; border-bottom:1px solid var(--line); padding:7px 9px;
  background:var(--paper); }
.tbl td { border-bottom:1px solid var(--line); padding:7px 9px; }
details { border-top:1px solid var(--line); padding:12px 0 2px; }
details summary { cursor:pointer; font-weight:600; font-size:15px; }
.mermaid { background:var(--white); text-align:center; }
.quiz .q { border-top:1px solid var(--line); padding:12px 0; }
.quiz .opt { display:block; padding:5px 0; cursor:pointer; font-size:14px; }
.quiz .why { color:var(--muted); font-size:13px; margin:6px 0 0; display:none; }
.quiz .q.answered .why { display:block; }
.quiz .opt.right { color:var(--green); } .quiz .opt.wrong { color:var(--red); }
@media (max-width:600px) {
  h1 { font-size:25px; }
  .wk .h { display:none; }
  .wrap { padding-bottom:48px; }
}
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
    const dark = document.documentElement.dataset.theme === 'dark';
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
    if (el) {
      const any = t.of && Object.keys(state).length;
      el.hidden = !any;
      el.textContent = any ? 'self-test ' + t.got + '/' + t.of + ' (yours only)' : '';
    }
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


def _pill(w: "Week") -> str:
    """One word for where this week stands. The mentor's verdict is not ours to give."""
    if w.state == "green" and w.merged:
        return '<span class="pill green">merged</span>'
    if w.pr:
        return '<span class="pill amber">submitted</span>'
    if w.state == "green":
        return '<span class="pill green">checks pass</span>'
    if w.state == "red":
        return '<span class="pill red">checks fail</span>'
    return '<span class="pill">not started</span>'


def headline(w: "Week") -> str:
    """One short sentence of evidence. Enough to decide whether to open the week."""
    if w.report:
        bits = []
        # This week's own checks, not the running total for every week up to it: the number here
        # has to be the number the week page lists, or one of them is a lie.
        if w.tests:
            passed = len([t for t in w.tests if t.get("outcome") == "passed"])
            failed = len(w.tests) - passed
            bits.append(
                f"{passed} of {len(w.tests)} checks pass" if failed else f"all {passed} checks pass"
            )
        elif w.report.get("passed") is not None:
            bits.append(f"{w.report['passed']} checks pass")
        extra = WEEK_HEADLINE.get(w.n)
        if extra:
            value = extra()
            if value:
                bits.append(value)
        if bits:
            return " · ".join(bits)
    return WEEK_PROMPT.get(w.n, "not started yet")


def _num(path: str, *keys: str) -> Any:
    data = read_json(ROOT / "reports" / path)
    for key in keys:
        if not isinstance(data, dict):
            return None
        data = data.get(key)
    return data


def _h_retrieval() -> str:
    data = read_json(ROOT / "reports" / "retrieval.json")
    if not isinstance(data, dict) or not data.get("strategies"):
        return ""
    return f"{len(data['strategies'])} chunking strategies compared"


def _h_eval() -> str:
    value = _num("eval.json", "metrics", "citation_validity")
    mode = _num("eval.json", "provider_mode")
    if value is None:
        return ""
    note = " (fake model)" if mode == "fake" else ""
    return f"citations {float(value):.0%} valid{note}"


def _h_compare() -> str:
    data = read_json(ROOT / "reports" / "compare.json")
    return "three approaches compared" if isinstance(data, dict) and data else ""


def _h_attacks() -> str:
    data = read_json(ROOT / "reports" / "attacks.json")
    if not isinstance(data, dict) or "attacks" not in data:
        return ""
    return f"{data['attacks'] - data.get('succeeded', 0)} of {data['attacks']} attacks blocked"


def _h_versions() -> str:
    data = read_json(ROOT / "reports" / "versions.json")
    if not isinstance(data, dict) or not data.get("rows"):
        return ""
    leaks = sum(len(r.get("filtered_leaks", [])) for r in data["rows"])
    return "no wrong-version material" if leaks == 0 else f"{leaks} wrong-version passages"


WEEK_HEADLINE: dict[int, Any] = {
    2: lambda: _h_retrieval() or _h_versions(),
    3: _h_eval,
    4: _h_compare,
    5: _h_attacks,
}

WEEK_PROMPT: dict[int, str] = {
    0: "open a Codespace and run the first check",
    1: "the model layer: retries, caching, cost, a provider swap",
    2: "chunking, the version filter, and numbers to choose by",
    3: "citations, declining, and a gate that blocks regressions",
    4: "tools, scopes, and plain code against an agent",
    5: "tracing, cost per step, and a document that attacks you",
    6: "publish it, break it, roll it back, write it up",
}


def _pretty(test_id: str) -> str:
    return test_id.removeprefix("test_").replace("_", " ")


def checks_card(w: "Week") -> str:
    """What the gate actually ran. The counts everywhere else open into this.

    A fellow reading "19 fail" needs the names, not the number: the names say which part of the
    week is not built yet, and they are the same names as in the test file they are working
    against. A count alone is a verdict; the list is a map.
    """
    if not w.tests:
        return (
            '<div class="card checks" id="checks"><p class="sum">'
            f"No checks have run for this week yet &middot; <code>make check WEEK={w.n}</code>"
            "</p></div>"
        )
    failed = [t for t in w.tests if t.get("outcome") != "passed"]
    passed = [t for t in w.tests if t.get("outcome") == "passed"]

    def items(rows: list[dict[str, str]], kind: str) -> str:
        return "".join(
            f'<li class="{kind}"><b>{esc(_pretty(t.get("id", "")))}</b>'
            f'<span class="f">{esc(Path(t.get("file", "")).name)}</span></li>'
            for t in rows
        )

    head = (
        f"{len(passed)} of {len(w.tests)} checks pass"
        if failed
        else f"all {len(passed)} checks pass"
    )
    body = ""
    if failed:
        body += (
            f"<details open><summary>The {len(failed)} that do not</summary>"
            f"<ul>{items(failed, 'fail')}</ul>"
            '<p class="fineprint">Red is the normal state of a week you have not built yet. '
            "Each name is a test in the file beside it.</p></details>"
        )
    if passed:
        body += (
            f"<details><summary>The {len(passed)} that do</summary>"
            f"<ul>{items(passed, 'pass')}</ul></details>"
        )
    return (
        f'<div class="card checks" id="checks">'
        f'<p class="sum">{_pill(w)} <span>{esc(head)}</span></p>{body}</div>'
    )


def week_row(w: "Week", current: bool) -> str:
    return (
        f'<a class="wk{" current" if current else ""}" href="week-{w.n}.html">'
        f'<span class="num">{w.n}</span>'
        f'<span class="body"><span class="t">{esc(w.title)}</span><br>'
        f'<span class="h">{esc(headline(w))}</span></span>'
        f"{_pill(w)}"
        f'<span class="go">&rsaquo;</span></a>'
    )


def render_week(w: "Week", weeks: list["Week"], repo: str) -> str:
    """One week, in full. This is what a details link lands on."""
    parts = [
        '<a class="back" href="index.html">&lsaquo; All weeks</a>',
        f'<p class="kicker">Week {w.n}</p>',
        f"<h1>{esc(w.title)}</h1>",
        f'<div class="strip"><a class="chip" href="#checks">{esc(headline(w))} &rsaquo;</a>'
        f'<a class="chip" href="{_gh(repo, f"weeks/{w.n}/README.md")}">On GitHub</a></div>',
    ]
    if not w.done:
        verb = {
            "Read": "Start by reading the concept, then run what is already there.",
            "Build": "Build this week's exercise, then run the gate.",
            "Submit": "Fill in your reflection, then open the pull request.",
        }[w.step]
        parts.append(
            f'<div class="card todo"><h3>Do this next</h3><p>{esc(verb)}</p>'
            f"<pre>make check WEEK={w.n}</pre></div>"
        )
    parts.append(checks_card(w))

    if w.pr:
        state = str(w.pr.get("state", "")).lower()
        parts.append(
            f'<div class="card"><h3 style="margin:0 0 6px">Your pull request</h3>'
            f'<p style="margin:0;color:var(--muted);font-size:14px">'
            f'<a href="{esc(w.pr.get("url", "#"))}">#{esc(w.pr.get("number", ""))} '
            f"{esc(w.pr.get('title', ''))}</a> &middot; {esc(state)}</p></div>"
        )

    if w.reflection_q1 or w.reflection_q2:
        parts.append(
            '<div class="card"><h3 style="margin:0 0 8px">In your own words</h3>'
            f'<div class="prose" style="box-shadow:none;border:0;padding:0">'
            f"{MD.render(w.reflection_q1)}{MD.render(w.reflection_q2)}</div></div>"
        )

    measured = []
    for name in WEEK_REPORTS.get(w.n, []):
        if name not in REPORTS:
            continue
        label, renderer = REPORTS[name]
        body = renderer()
        if body:
            measured.append(f"<h3>{esc(label)}</h3>{body}")
    if measured:
        parts.append(
            f'<h2><span class="n">Measured</span>this week</h2>'
            f'<div class="card">{"".join(measured)}</div>'
        )

    if w.readme_html:
        parts.append(
            f'<h2><span class="n">Do</span>the week</h2><div class="prose">{w.readme_html}</div>'
        )
    if w.concept_html:
        parts.append(
            '<h2><span class="n">Read</span>the concept</h2>'
            '<div class="card"><details><summary>The idea behind this week</summary>'
            '<div class="prose" style="box-shadow:none;border:0;padding:0">'
            f"{w.concept_html}</div></details></div>"
        )
    if w.checks_html:
        parts.append(
            '<h2><span class="n">Gate</span>what is verified</h2>'
            f'<div class="card"><details><summary>What <code>make check WEEK={w.n}</code> runs'
            '</summary><div class="prose" style="box-shadow:none;border:0;padding:0">'
            f"{w.checks_html}</div></details></div>"
        )
    if w.quiz:
        parts.append(f'<h2><span class="n">Optional</span>self-test</h2>{quiz_html(w)}')

    nav = []
    if w.n > 0:
        nav.append(f'<a class="btn" href="week-{w.n - 1}.html">&lsaquo; Week {w.n - 1}</a>')
    if w.n < max(x.n for x in weeks):
        nav.append(f'<a class="btn" href="week-{w.n + 1}.html">Week {w.n + 1} &rsaquo;</a>')
    parts.append(f'<p style="margin:28px 0 0;display:flex;gap:8px">{"".join(nav)}</p>')

    return "".join(parts)


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


def page(title: str, body: str, cfg: dict[str, Any] | None = None) -> str:
    """The shell. One stylesheet, one script, no framework, nothing to install."""
    config = json.dumps(cfg or {})
    return f"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap"
      rel="stylesheet">
<style>{CSS}</style>
<script>
  /* Before first paint, so a chosen dark theme never flashes light. */
  try {{ var t = localStorage.getItem('hub.theme');
         if (t) document.documentElement.dataset.theme = t; }} catch (e) {{}}
</script>
</head><body>
<div class="bar"><div class="wrap">
  <span class="mark">AI Engineering</span>
  <span class="sp"></span>
  <a href="index.html">Weeks</a>
  <a href="playground.html">Playground</a>
  <a href="progress.csv">Export</a>
  <button class="tog" id="theme" title="Light or dark">&#9680;</button>
</div></div>
<div class="wrap">{body}</div>
<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
<script>
  document.getElementById('theme').onclick = function () {{
    var dark = document.documentElement.dataset.theme === 'dark';
    document.documentElement.dataset.theme = dark ? 'light' : 'dark';
    try {{ localStorage.setItem('hub.theme', dark ? 'light' : 'dark'); }} catch (e) {{}}
  }};
</script>
<script>const cfg = {config};</script>
<script>{JS}</script>
</body></html>
"""


def quiz_html(w: Week) -> str:
    return (
        f'<div class="card quiz" id="quiz-{w.n}"></div>'
        '<p class="fineprint">Scored in your browser only. It never reaches the repository, '
        "your mentor or your route.</p>"
    )


def quiz_cfg(weeks: list[Week]) -> dict[str, Any]:
    return {
        "quiz": {
            str(w.n): [
                {
                    "n": q.n,
                    "text": q.text,
                    "stretch": q.stretch,
                    "options": q.options,
                    "why": q.why,
                }
                for q in w.quiz
            ]
            for w in weeks
            if w.quiz
        }
    }


def next_step(weeks: list[Week], repo: str) -> str:
    """The one thing to do now. Everything else on this page is reference."""
    current = next((w for w in weeks if not w.done), None)
    if current is None:
        return (
            '<div class="card next"><h3>Every week is green</h3>'
            "<p>Write the page that says what it did for the business, then book the defence.</p>"
            f'<a class="btn primary" href="week-{weeks[-1].n}.html">Week {weeks[-1].n}</a></div>'
        )
    if current.n == 0 and current.report is None:
        return (
            '<div class="card next"><h3>Open a Codespace</h3>'
            "<p>Nothing to install. About 90 seconds, then week 0 opens by itself.</p>"
            f'<a class="btn primary" href="https://codespaces.new/{esc(repo)}?quickstart=1">'
            "Open in GitHub Codespaces</a></div>"
        )
    verb, cmds = {
        "Read": (
            "Read the concept, then run what is already there",
            WEEK_RUN.get(current.n, [f"make check WEEK={current.n}"]),
        ),
        "Build": (
            "Build this week's exercise, then run the gate",
            [f"make check WEEK={current.n}"],
        ),
        "Submit": (
            "Fill in your reflection, then open the pull request",
            [
                f"git add -A && git commit -m 'week {current.n}'",
                f"git push -u origin week-{current.n}",
                "gh pr create --fill --base main",
            ],
        ),
    }[current.step]
    return (
        f'<div class="card next"><h3>Week {current.n}: {esc(current.title)}</h3>'
        f"<p>{esc(verb)}.</p>"
        f"<pre>{esc(chr(10).join(cmds))}</pre>"
        f'<a class="btn primary" href="week-{current.n}.html">Open week {current.n}</a></div>'
    )


def render_index(weeks: list[Week], route: str, live_url: str, repo: str) -> str:
    done = [w for w in weeks if w.done]
    milestones = [w for w in weeks if w.n > 0]
    current = next((w for w in weeks if not w.done), None)

    chips = [
        f'<span class="chip">route <b>{esc(route)}</b></span>',
        f'<span class="chip"><span class="dot'
        f'{" green" if len(done) == len(weeks) else ""}"></span>'
        f"<b>{len(done)}</b> of {len(weeks)} weeks complete</span>",
    ]
    if live_url:
        chips.append(f'<a class="chip go" href="{esc(live_url)}">Live service</a>')
    chips.append('<span class="chip" id="qtotal" hidden></span>')

    steps = [
        (
            "01",
            "Getting ready",
            "Open the workspace, read the client's brief, and prove the foundations.",
            "week-0.html",
            "Week 0 " + ("complete" if weeks[0].done else "not finished"),
        ),
        (
            "02",
            "The six weeks",
            "One service, improved every week, with a gate you run as often as you like.",
            f"week-{(current or milestones[0]).n}.html",
            f"{len([w for w in milestones if w.done])} of {len(milestones)} milestones complete",
        ),
        (
            "03",
            "Your evidence",
            "Measurements, a published build, and one page on what it did for the business.",
            f"week-{milestones[-1].n}.html",
            "Ready at week 6",
        ),
    ]
    step_html = "".join(
        f'<div class="card step"><span class="step-index">{n}</span><div>'
        f"<h3>{esc(title)}</h3><p>{esc(blurb)}</p>"
        f'<p class="status">{esc(status)} &middot; <a href="{href}">Open</a></p>'
        "</div></div>"
        for n, title, blurb, href, status in steps
    )

    rows = "".join(week_row(w, current is not None and w.n == current.n) for w in weeks)

    links = [
        ("The brief", "what the client asked for", _gh(repo, "weeks/0/BRIEF.md")),
        ("What it must do", "the twelve requirements", _gh(repo, "weeks/0/REQUIREMENTS.md")),
        ("Your role and the rules", "including AI tools", _gh(repo, "RULES.md")),
        ("How the track works", "routes, sessions, gates", _gh(repo, "docs/track.md")),
        ("Where the vectors live", "choosing a store", _gh(repo, "docs/vector-stores.md")),
        ("The repository", "everything above, as files", f"https://github.com/{esc(repo)}"),
    ]
    link_html = "".join(
        f'<a href="{href}">{esc(t)}<span>{esc(sub)}</span></a>' for t, sub, href in links
    )

    pct = round(100 * len(done) / len(weeks))
    body = f"""
<p class="kicker">Discover &rarr; Build &middot; AI Engineering</p>
<h1>One service, six weeks, numbers you can defend.</h1>
<p class="lede">A support desk answers the same documentation questions every day, from a manual
that exists in two versions worded almost identically. You build the assistant that answers from
the right one, shows where the answer came from, and says when it does not know.</p>
<div class="strip">{"".join(chips)}</div>
<div class="meter"><i style="width:{pct}%"></i></div>
{next_step(weeks, repo)}
<h2><span class="n">How</span>you get there</h2>
{step_html}
<h2><span class="n">Weeks</span>where you are</h2>
<div class="weeks">{rows}</div>
<h2><span class="n">Reference</span>when you need it</h2>
<div class="links">{link_html}</div>
<p class="fineprint">Nothing on this page is typed by hand: it is built from the repository on
every merge. Numbers measured against the test model and the lexical embedder prove the pipeline
holds, not that answers are good &mdash; each week says which it ran.
<a href="progress.csv">progress.csv</a> &middot; <a href="progress.json">progress.json</a></p>
"""
    return page("AI Engineering — your build", body, quiz_cfg(weeks))


PLAYGROUND = """
<a class="back" href="index.html">&lsaquo; Back</a>
<p class="kicker">Playground</p>
<h1>Call your running service.</h1>
<p class="lede">Point this at your Codespace's forwarded port (make it public first) or at a
published build. Nothing is stored here; every call goes straight to the address you give.</p>
<div class="card">
  <p><label>Base address<br><input id="pg-base" style="width:100%;max-width:460px;padding:8px"
     placeholder="http://127.0.0.1:8000"></label></p>
  <p class="status" id="pg-status"></p>
</div>
<div class="card"><h3>Upload and extract</h3>
  <p><input type="file" id="pg-file"> <button class="btn" id="pg-upload">Upload</button>
     <input id="pg-docid" placeholder="document id" style="width:110px;padding:6px">
     <button class="btn" id="pg-extract">Extract</button></p>
  <pre id="pg-extract-out">&nbsp;</pre></div>
<div class="card"><h3>Index and search</h3>
  <p><button class="btn" id="pg-index">Index</button>
     <input id="pg-q" placeholder="connection timeout" style="padding:6px">
     <button class="btn" id="pg-search">Search</button></p>
  <pre id="pg-search-out">&nbsp;</pre></div>
<div class="card"><h3>Ask</h3>
  <p><input id="pg-question" style="width:100%;max-width:460px;padding:8px"
     placeholder="How do I configure the connection timeout?">
     <button class="btn primary" id="pg-ask">Ask</button></p>
  <pre id="pg-ask-out">&nbsp;</pre></div>
<div class="card"><h3>Run a task three ways</h3>
  <p><input id="pg-tq" style="width:100%;max-width:420px;padding:8px" placeholder="a task">
     <select id="pg-mode" style="padding:7px"><option>plain</option><option>workflow</option>
     <option>agent</option></select>
     <label style="font-size:14px"><input type="checkbox" id="pg-approved"> approved</label>
     <button class="btn" id="pg-task">Run</button></p>
  <pre id="pg-task-out">&nbsp;</pre></div>
<div class="card"><h3>Traces</h3>
  <p><button class="btn" id="pg-traces">Last ten requests</button></p>
  <pre id="pg-traces-out">&nbsp;</pre></div>
"""


def export_rows(weeks: list[Week], route: str, repo: str, hub: str) -> list[dict[str, str]]:
    """The narrow export: one row per week, status and a link. Nothing the platform must parse.

    Deliberately not here: the measurements. They differ week by week, they go stale the moment
    they are copied, and a number shown without the run that produced it is worse than no number.
    `details_url` always shows the current evidence, with its own caveats attached.

    Also deliberately not here: completion. Open and submitted are facts we can see. Complete,
    needs clarification and incomplete are the mentor's words, recorded where the mentor works.
    """
    now = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    repo_url = f"https://github.com/{repo}"
    out = []
    for w in weeks:
        checks = {"green": "pass", "red": "fail"}.get(w.state, "not run")
        out.append(
            {
                "repo_url": repo_url,
                "route": route,
                "week": str(w.n),
                "title": w.title,
                "status": "submitted" if w.pr else "open",
                "checks": checks,
                "headline": headline(w),
                "details_url": f"{hub}/week-{w.n}.html",
                "updated_at": now,
            }
        )
    return out


def write_export(rows: list[dict[str, str]], out_dir: Path, hub: str) -> None:
    columns = [
        "repo_url",
        "route",
        "week",
        "title",
        "status",
        "checks",
        "headline",
        "details_url",
        "updated_at",
    ]
    with (out_dir / "progress.csv").open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)
    (out_dir / "progress.json").write_text(
        json.dumps(
            {
                "schema": "talentraft.progress/1",
                "repo_url": rows[0]["repo_url"] if rows else "",
                "route": rows[0]["route"] if rows else "",
                "hub_url": hub,
                "updated_at": rows[0]["updated_at"] if rows else "",
                "weeks": [
                    {
                        k: r[k]
                        for k in ("week", "title", "status", "checks", "headline", "details_url")
                    }
                    for r in rows
                ],
            },
            indent=2,
        ),
        encoding="utf-8",
    )


def main() -> int:
    weeks = load_weeks()
    route = ROUTE
    live_url = os.environ.get("LIVE_URL", "").strip().rstrip("/")
    repo = os.environ.get("GITHUB_REPOSITORY", "anilmodest/ai-eng-track")
    owner, _, name = repo.partition("/")
    hub = os.environ.get("HUB_URL", "").strip().rstrip("/") or f"https://{owner}.github.io/{name}"

    out_dir = OUT.parent
    out_dir.mkdir(exist_ok=True)
    OUT.write_text(render_index(weeks, route, live_url, repo), encoding="utf-8")
    for w in weeks:
        (out_dir / f"week-{w.n}.html").write_text(
            page(f"Week {w.n} — {w.title}", render_week(w, weeks, repo), quiz_cfg([w])),
            encoding="utf-8",
        )
    (out_dir / "playground.html").write_text(page("Playground", PLAYGROUND), encoding="utf-8")
    write_export(export_rows(weeks, route, repo, hub), out_dir, hub)

    size = OUT.stat().st_size // 1024
    print(f"wrote site/index.html ({size} KB), {len(weeks)} week pages, playground, progress.*")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
