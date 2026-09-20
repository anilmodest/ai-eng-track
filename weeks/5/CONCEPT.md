# Week 5 — Concept

> **You cannot fix what you cannot see. And the defining vulnerability of this work is an
> instruction hidden in the data, which does not look like a bug during normal testing.**

Read this once (about 20 minutes). Write the sentence in your own words in `reflections/week-5.md`,
Q1, before you touch code.

## Observability: trace every step, attribute every cent

A request to an AI feature is several steps: retrieve, call the model (maybe twice), run a tool,
call again. When it is slow, or wrong, or expensive, the question is *which step*. So:

- **Trace every step.** A request is a tree of spans; each has a duration, tokens, cost and,
  when it failed, a kind. The request id goes back to the caller so a complaint can be looked up.
- **Attribute latency and cost to the step that caused it.** "This request cost 0.4 cents" is a
  fact. "The repair call cost 0.3 of it" is something you can act on.
- **An error taxonomy, not one bucket.** `provider_timeout` and `schema_error` need different
  fixes. A dashboard that says "12 failures" says nothing; one that says "9 timeouts, 3 schema"
  says which provider to call and which prompt to look at.
- **A dashboard a non-engineer can read.** Cost per query is now a standard interview question,
  and the person asking it will not read a span tree.

## Security: the model reads instructions in the data

Prompt injection is not a prompt problem; it is a data problem. Any text the model reads (an
uploaded file, a retrieved passage, a web page, a tool result) can contain instructions, and the
model cannot reliably tell the difference between your instruction and one in the data. It
arrives through retrieval as easily as through a user, and it looks like a normal document.

The disciplines, none sufficient alone:

- **Treat data as data.** Fence untrusted text, label it, and tell the model that instructions
  never come from inside the fence. Cheap, and it removes most casual injections.
- **Filter input, and know what filtering cannot catch.** Known patterns can be stripped. New
  phrasings, other languages and encoded text walk straight past a pattern list.
- **Treat model output as untrusted input to whatever comes next.** A figure the model reports
  that the source document never contains did not come from the document. Check.
- **Least agency.** The minimum permission the task actually needs. A tool that can spend money
  or delete data is a tool an attacker can spend or delete with.
- **Kill switches and blast radius.** One setting that stops every model call, and a budget that
  caps how far a runaway loop, or an attacker, can get before someone notices.

## What this looks like in the service

| Idea | Where it lives | What you do this week |
| --- | --- | --- |
| Spans and cost attribution | `app/trace.py`, `GET /traces` | Read it; use it to answer questions about your own service |
| Error taxonomy | `ErrorKind` in `app/trace.py` | Map every failure to a kind |
| Dashboard | `scripts/trace_report.py` | Run it; explain it to someone who does not code |
| Guard | `app/guard.py` | Get attacked; build the four defences |
| Attack set | `eval/attacks.jsonl`, `scripts/attack.py` | Attack a peer; add what worked to the set |
| Limits | `KILL_SWITCH`, `DAILY_BUDGET_USD` | Flip them; watch the service refuse |

## What you should be able to say by Friday

- The cost of one `/ask` request, step by step, from a trace.
- Which error kind your service produced most this week, and what you changed because of it.
- The attack that got through your peer's service, and the one that got through yours.
- What your input filter cannot catch, and what you rely on instead for that case.
