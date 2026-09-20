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
WEEK_REPORTS = {2: "retrieval", 3: "eval", 4: "compare", 5: "attacks", 6: "traces"}


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
        w = Week(n=n, title=first.lstrip("# ").strip())
        rep = read_json(ROOT / "reports" / f"week-{n}.json")
        if rep:
            w.report = rep
            w.tests = [t for t in rep.get("tests", []) if f"test_week{n}" in t.get("file", "")]
        refl = ROOT / "reflections" / f"week-{n}.md"
        if refl.exists():
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


REPORTS = {
    "retrieval": ("Retrieval evaluation", report_retrieval),
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
"""

JS = r"""
(function () {
  // side nav: highlight the section in view
  const links = [...document.querySelectorAll('aside a[href^="#"]')];
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


def week_card(w: Week, repo: str) -> str:
    gates = ""
    if w.report:
        gates = "".join(
            f'<span class="{"pass" if ok else "fail"}">{esc(k)}</span>'
            for k, ok in (w.report.get("gates") or {}).items()
        )
    tests = "".join(
        f'<li class="{"pass" if t["outcome"] == "passed" else "fail"}">'
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
        refl += (
            "<h3>Concept, in the fellow's words</h3>"
            f"<blockquote class='refl'>{esc(w.reflection_q1)}</blockquote>"
        )
    if w.reflection_q2:
        refl += (
            "<h3 style='margin-top:10px'>What surprised them</h3>"
            f"<blockquote class='refl'>{esc(w.reflection_q2)}</blockquote>"
        )
    no_refl = (
        f"<h3>Reflection</h3><div class='muted'>not written yet: reflections/week-{w.n}.md</div>"
    )
    areas = ", ".join(f"{a} {AREAS[a]}" for a in WEEK_AREAS.get(w.n, []))
    base = f"https://github.com/{repo}/blob/main/weeks/{w.n}"
    panels = ""
    for label, body, fname in (
        ("Concept", w.concept_html, "CONCEPT.md"),
        ("Exercise (README)", w.readme_html, "README.md"),
        ("What the gate checks", w.checks_html, "CHECKS.md"),
    ):
        if body:
            panels += (
                f"<details><summary>{label} <span class='muted'>&middot; "
                f"<a href='{base}/{fname}'>{fname} on GitHub</a></span></summary>"
                f"<div class='doc'>{body}</div></details>"
            )
    rep_key = WEEK_REPORTS.get(w.n)
    if rep_key:
        title, fn = REPORTS[rep_key]
        body = fn()
        if body:
            panels += f"<details open><summary>{title}</summary>{body}</details>"
    if w.quiz:
        panels += (
            f"<details class='quiz' data-week='{w.n}'><summary>Self-test "
            f"<span class='muted'>&middot; {len(w.quiz)} questions, optional, scored only in your browser</span>"
            f" <span class='qscore' id='qscore-{w.n}'></span></summary>"
            f"<div id='quiz-{w.n}'></div></details>"
        )
    checks = (
        f"<h3 style='margin-top:8px'>This week's checks</h3><ul class='checks'>{tests}</ul>"
        if tests
        else ""
    )
    review = f"<h3 style='margin-top:10px'>Review</h3><div>{pr}</div>" if pr else ""
    return f"""
<section class="card" id="week-{w.n}">
  <h2><span class="dot {w.state}"></span>Week {w.n} &mdash; {esc(w.title)}
      <span class="gates">{gates or "<span>gate not run yet</span>"}</span></h2>
  <p class="concept">{esc(CONCEPTS.get(w.n, ""))} <span class="muted">&middot; areas {esc(areas) or "&mdash;"}</span></p>
  <div class="grid">
    <div>{checks or "<h3>This week's checks</h3><div class='muted'>run make check WEEK=" + str(w.n) + " to see them here</div>"}{review}</div>
    <div>{refl or no_refl}</div>
  </div>
  {panels}
</section>"""


def material_links(weeks: list[Week], repo: str) -> str:
    items = []
    for w in weeks:
        base = f"https://github.com/{esc(repo)}/blob/main/weeks/{w.n}"
        parts = [f'<a href="{base}/README.md">exercise</a>']
        if (ROOT / "weeks" / str(w.n) / "CONCEPT.md").exists():
            parts.insert(0, f'<a href="{base}/CONCEPT.md">concept</a>')
        if (ROOT / "weeks" / str(w.n) / "CHECKS.md").exists():
            parts.append(f'<a href="{base}/CHECKS.md">checks</a>')
        items.append(f"<li>Week {w.n}: {' &middot; '.join(parts)}</li>")
    return "".join(items)


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
    gh = f"https://github.com/{esc(repo)}"
    codespace = f"https://codespaces.new/{esc(repo)}?quickstart=1"
    if current is None:
        here = "<p><b>Every released week is green.</b> Time for the write-up and the final session.</p>"
        actions = '<a class="btn primary" href="#week-6">Open Week 6</a>'
    else:
        here = (
            f"<p><b>You are on Week {current.n}: {esc(current.title)}.</b> "
            f"{esc(CONCEPTS.get(current.n, ''))}</p>"
        )
        actions = (
            f'<a class="btn primary" href="#week-{current.n}">Open Week {current.n}</a> '
            f'<a class="btn" href="{codespace}">Open in Codespaces</a>'
        )
    live_line = (
        f'Live service: <a href="{esc(live_url)}/docs">{esc(live_url)}</a> '
        f'(<a href="{esc(live_url)}/health">/health</a>)'
        if live_url
        else "No live service yet. The deploy step in <a href='#start'>Start here</a> gives you one."
    )
    track = _split_track()
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
    cards = "".join(week_card(w, repo) for w in weeks)
    self_test = ' <span id="qtotal"></span>'

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
  <p class="eyebrow">Contents</p>
  <ol>
    <li><a href="#track">1. The track</a></li>
    <li><a href="#how">2. How a week works</a></li>
    <li><a href="#start">3. Start here</a></li>
    <li><a href="#weeks">4. The six weeks</a></li>
    <li><a href="#sessions">5. Sessions and gates</a></li>
    <li><a href="#playground">6. Playground</a></li>
    <li><a href="#reports">7. Reports</a></li>
    <li><a href="#links">8. Links</a></li>
  </ol>
  <p class="side"><a href="{gh}">{esc(repo)}</a><br>route <b>{esc(route)}</b><br>{len(done)} of {len(weeks)} weeks green{self_test}</p>
</aside>

<article>
<h1>AI Engineering track</h1>
<p class="lead">One service that grows, week by week, into an AI product you can deploy, measure and defend. This page is built from your repository on every merge; nothing on it is typed in by hand.</p>
<div class="here">{here}<div class="actions">{actions}</div></div>
<p class="muted">{live_line}</p>

<h2 id="track">1. The track</h2>
<div class="doc">{track.get("The track", "")}</div>
<div class="strip">{strip}</div>
<p class="legend">The eleven areas as they stand in your repo. Green: that week's gate passed. Red: it did not yet. Grey: reached, not run.</p>

<h2 id="how">2. How a week works</h2>
<div class="doc">{track.get("How a week works", "")}</div>

<h2 id="start">3. Start here</h2>
<p class="lead">Three clicks, nothing to install. <a class="btn primary" href="{codespace}">Open in Codespaces</a></p>
<div class="doc">{start_html}</div>

<h2 id="weeks">4. The six weeks</h2>
<p class="lead">One card per week: the gate, your pull request and your own words; then the concept with its diagrams and reading list, the exercise, what the gate checks, the week's measurement, and an optional self-test.</p>
{cards}

<h2 id="sessions">5. Sessions and gates</h2>
<div class="doc">{track.get("Sessions and gates", "")}</div>

<h2 id="playground">6. Playground</h2>
<p class="lead">Call your running service from here: your Space (set the repository variable <code>LIVE_URL</code>) or a Codespace port you have made public. Only the URL is remembered, in your browser.</p>
<label for="pg-base" class="status">Service URL</label>
<input type="text" id="pg-base" placeholder="https://yourname-ai-eng-track.hf.space">
<p id="pg-status" class="status"></p>
<div class="play">
  <div class="card"><h3>Week 0 &middot; health and upload</h3>
    <button class="btn" id="pg-health">GET /health</button>
    <div class="out" id="pg-health-out"></div>
    <label for="pg-file">Upload a .md / .txt / .csv / .pdf</label>
    <input type="file" id="pg-file"> <button class="btn" id="pg-upload">POST /documents</button>
    <div class="out" id="pg-upload-out"></div>
  </div>
  <div class="card"><h3>Week 1 &middot; extract</h3>
    <label for="pg-docid">Document id</label>
    <input type="text" id="pg-docid" value="1">
    <button class="btn" id="pg-extract">POST /documents/{{id}}/extract</button>
    <div class="out" id="pg-extract-out"></div>
    <p class="status">Call it twice: the second answer must say <code>cached: true</code>.</p>
  </div>
  <div class="card"><h3>Week 2 &middot; index and search</h3>
    <button class="btn" id="pg-index">POST /index</button>
    <label for="pg-q">Query</label>
    <input type="text" id="pg-q" value="mileage rate personal car">
    <button class="btn" id="pg-search">GET /search</button>
    <div class="out" id="pg-search-out"></div>
  </div>
  <div class="card"><h3>Week 3 &middot; ask</h3>
    <label for="pg-question">Question</label>
    <textarea id="pg-question">What is the London hotel cap in the Contoso expenses policy?</textarea>
    <button class="btn" id="pg-ask">POST /ask</button>
    <div class="out" id="pg-ask-out"></div>
    <p class="status">Try one the documents cannot answer. A good system declines.</p>
  </div>
  <div class="card"><h3>Week 4 &middot; one task, three ways</h3>
    <label for="pg-tq">Question</label>
    <input type="text" id="pg-tq" value="Which invoice has the largest total due, and what is it?">
    <label for="pg-mode">Mode</label>
    <select id="pg-mode"><option value="plain">plain code</option><option value="workflow">workflow</option><option value="agent" selected>agent</option></select>
    <label><input type="checkbox" id="pg-approved"> approve tools that cost money</label>
    <button class="btn" id="pg-task">POST /tasks/run</button>
    <div class="out" id="pg-task-out"></div>
  </div>
  <div class="card"><h3>Week 5 &middot; traces</h3>
    <button class="btn" id="pg-traces">GET /traces</button>
    <div class="out" id="pg-traces-out"></div>
    <p class="status">Every call above returned an <code>X-Request-Id</code>; look it up here.</p>
  </div>
</div>

<h2 id="reports">7. Reports</h2>
<p class="lead">Every measurement your repo has produced, in one place.</p>
{reports_html}

<h2 id="links">8. Links</h2>
<div class="doc">
  <ul>
    <li><a href="{gh}">Repository</a> &middot; <a href="{gh}/pulls">pull requests</a> &middot; <a href="{gh}/actions">CI runs</a> &middot; <a href="{gh}/tree/main/reflections">reflections</a></li>
    <li><a href="{codespace}">Open in Codespaces</a></li>
    <li>{live_line}</li>
  </ul>
  <h3>Material on GitHub</h3>
  <ul>{material_links(weeks, repo)}</ul>
  <h3>Providers</h3>
  <ul>
    <li><a href="https://aistudio.google.com/apikey">Gemini key (free tier, default)</a></li>
    <li><a href="https://console.groq.com/keys">Groq key (second provider)</a></li>
    <li><a href="https://huggingface.co/new-space">Create a Hugging Face Space</a> for the live URL</li>
  </ul>
  <h3>For mentors</h3>
  <p>Runbooks, held-out sets, the rubric and reference solutions live in the private mentor kit, not here.</p>
</div>

<footer>Built by <code>scripts/build_pages.py</code> on every merge to <code>main</code> from <code>docs/track.md</code>, <code>README.md</code>, <code>weeks/</code>, <code>reports/</code>, <code>reflections/</code> and the pull requests.</footer>
</article>
</div>
<script src="https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js"></script>
<script>{JS}</script>
</body></html>
"""


def main() -> int:
    weeks = load_weeks()
    route_file = ROOT / ".route"
    route = route_file.read_text().strip() if route_file.exists() else "start"
    live_url = os.environ.get("LIVE_URL", "").strip().rstrip("/")
    repo = os.environ.get("GITHUB_REPOSITORY", "anilmodest/ai-eng-track")
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(render(weeks, route, live_url, repo), encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)} ({len(weeks)} weeks, {OUT.stat().st_size // 1024} KB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
