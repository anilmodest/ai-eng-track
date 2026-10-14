# Track 3 in ten minutes

Read this first, in week 0. Then read the week 1 concept page, and nothing else yet. The
[glossary](glossary.md) is there for whenever a word stops you; the
[worked examples](worked-examples.md) are for weeks 2 and 3, where the numbers arrive.

## What you are building

One support-desk agent, built in week 0 and changed every week after. It works for a software
product that exists in two supported versions, 2 and 3, whose manuals are almost identical in
wording and different in substance.

Given a ticket, the finished agent finds out which version the customer runs, answers only from
that version's documentation with a citation or declines and hands over to a person, looks up the
customer's own record and ticket history, answers questions about the ticket data with numbers it
did not invent, and proposes the next action, carrying it out only when a person approves. It
proves its own accuracy on questions it never sees, survives an attack hidden in the content it
reads, and ships as a container image anyone can run.

At the end you defend every decision in it twice: once with your AI assistant in hand, once
without it. Both kinds of round now appear in interviews.

## The six weeks on one page

| Wk | What you add | The one lesson | Hours |
| --- | --- | --- | --- |
| 0 | Placement, your repository, two free model keys | Start with a working environment and no excuses. | 5 |
| 1 | The model as a component; the first two tools | A model is an unreliable dependency. Its output must fit a schema and its tools must be described exactly. | 8–10 |
| 2 | Retrieval at real scale, filtered by version | The same model gives a different answer when you give it different context. Choosing the context is the job. | 8–10 |
| 3 | Declining, citations, your test set and the gate | Without a test you cannot see, every improvement is a guess. | 9–10 |
| 4 | Action tools with approval; analysis; MCP | Agency and model size are both costs. Never let the model act without approval. | 9–10 |
| 5 | Tracing, cost per ticket, injection defence, masking | Once the system can act, content it reads can attack it. Remove the capability first. | 8–9 |
| 6 | Release, rollback, write-up, recorded demo | Say what it did for the business, and defend it with or without an assistant. | 8–9 |

Weeks 3 and 4 are the heaviest. The total is 55 to 63 hours. Sessions with your mentor fall at the
end of weeks 0, 1, 3 and 6.

## Your first hours

Week 0, in order. The discovery session sets your route. You make your repository from your
route's template. Open it in Codespaces. Get free keys from two different providers and store both
as Codespaces secrets. Connect your repository to the programme (the link you were sent); the
programme then runs a baseline on your untouched starter.

Then read only two things: this page and `weeks/1/CONCEPT.md`. Nothing else yet.

When unsure what to do next, run `make next`. It names the week you are on, the file to open, and
the first thing that is not working.

## Focus now, and what can wait

| Focus on in week 1 | Safe to ignore until its week |
| --- | --- |
| How a model fails, stalls, costs, varies and changes under you | Chunking, embeddings and retrieval metrics (week 2) |
| Structured output with Pydantic and one repair attempt | Test sets, the judge and faithfulness (week 3) |
| Writing a tool schema a model calls correctly | MCP, approvals, LangGraph and the routing table (week 4) |
| The weekly loop: branch, `make check`, `make evidence`, decision record, pull request | Tracing, injection and personal-data masking (week 5) |
| Filling the AI-use log honestly from day one | Release, rollback and the business write-up (week 6) |

## Foundations, and what becomes clear by building

**Foundations you need from day one:** writing and testing a Python service, proposing a change
through a pull request, reading code you did not write, and checking what a system or an assistant
produced against the source. These are the entry bar; if one is shaky, say so at discovery.

**Ideas that only make sense once built:** why the context window is an attention budget, what a
retrieval metric is really telling you, why a judge must be checked against people, when an agent
beats a workflow, and what blast radius means. Do not try to master these from reading. Read the
concept page, build the week, then reread it.

## How you are judged, in one paragraph

Every pull request gets automated checks against a fake model, and from week 2 a hidden evaluation
on a fixed reference model. You see its totals, never its questions. Each week ends in a one-page
decision record whose numbers must match your evidence file. At sessions the mentor watches you
work with your assistant, then asks you to explain your decisions without it. Using an assistant
is expected and logged. Undisclosed help is the one thing that fails the programme.
