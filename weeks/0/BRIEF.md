# The brief

This is how the work arrives. Read it as a client wrote it, because one did.

## The client

A software company with its product on a third major version. Versions 2 and 3 are both supported
and both in active use by customers.

## The problem

The support desk handles the same kinds of ticket every day. Most are answerable from the manual,
but the answer depends on which version the customer runs, and that has to be looked up. Some
need a look at the customer's own history: has this happened to them before, how many tickets like
this came in this month. And some end in an action: a drafted reply, an escalation to engineering,
or a goodwill credit.

Three things make this harder than it sounds.

The documentation for version 2 and version 3 is almost identical in wording and different in
substance, so an answer from the wrong version is worse than no answer at all. A meaningful share
of questions are not covered by the documentation, so a system that always answers will
confidently invent things. And a system that acts on its own can do real damage: a credit costs
money, an escalation pages an engineer, and a wrong reply goes to a customer.

## What they want

An agent that takes a ticket, finds out which version the customer runs, answers only from that
version's documentation with a citation or declines, pulls the facts it needs from the customer's
record and the ticket history, and proposes the next action, carrying it out only when a person
approves it.

They need to know how often it is right, how often it wrongly declines, how often it wrongly
answers, how often it picks the wrong tool or acts without approval, and what it costs per ticket.
They need those numbers produced automatically rather than claimed, on questions the builder has
never seen.

## The constraint they set

The desk will not adopt anything they cannot audit. Every answer has to be traceable to a source,
every measurement has to be reproducible, every action has to be approved and recorded, no
customer's personal data may leave the service unmasked, and any change that makes the system
worse has to be caught before it reaches a customer.

## The example the whole build turns on

A user asks: **how do I configure the connection timeout?**

In version 2 the setting is a value in a configuration file. In version 3 it moved to an
environment variable, and the old setting is now silently ignored. The two documentation pages are
nearly identical in wording.

A system matching on similarity alone finds the version 2 page, because the words match almost
perfectly, and answers with total confidence. The user follows the instructions and nothing
happens. And the agent cannot know which page is right until it has called the tool that says
which version this customer runs. That is the first reason the system is an agent rather than a
pipeline.

Open `corpus/manual-v2-connection-timeout.md` and `corpus/manual-v3-connection-timeout.md` now and
read them side by side. Everything in the next six weeks is downstream of that pair.

## Why this brief and not a simpler one

Every candidate now has a document question-answering project, and having one signals nothing. The
version constraint is what turns a common project into a discriminating one, and the desk's data
and actions are what turn it into an agent that has to be trusted:

| | |
| --- | --- |
| Retrieval becomes genuinely hard | Matching on similarity alone returns the wrong version. Filtering on metadata is the fix, and that is a skill rather than a trick |
| Declining becomes necessary | Some questions are genuinely not covered, so abstention can be measured instead of discussed |
| Tool use has an obvious purpose | The agent has to look up which version a customer runs and what their tickets say. There are tools that read, a tool that analyses, and tools that act |
| Analysis is unavoidable | "How many version 3 customers hit this timeout this month?" cannot be answered from documents. The agent asks the ticket data through a read-only, allowlisted query, and every number it states is checked against the count |
| Agency has a real cost | A credit spends money, an escalation pages an engineer, a reply reaches a customer. Approval and limits are requirements, not extras |
| The attack surface is real | A documentation page carrying hidden instructions is a risk for a system whose job is reading documents. So is a ticket a customer wrote, which reaches the model through a tool: that is the attack that matters once the agent can act |
| The business metric is obvious | Tickets resolved without a person, at a cost per ticket, with no action nobody approved. A hiring manager understands that sentence immediately |

## One hard constraint on the corpus

It must **fail** a no-retrieval baseline. Before any retrieval is built, you ask the test questions
with no documents attached and record the score. If the model already answers correctly from its
own training, retrieval is doing no work and every measurement afterwards is meaningless.

`uv run python scripts/baseline.py` does this, and week 2 asks you to run it. It is also what
proves to you that the work has a point.

The product in `corpus/` is invented, and so is every setting name, default and unit in it. That
is why.

## What ships with the repository

- The manual and its neighbours, about 400 documents in `corpus/`: manual, troubleshooting and
  how-to pages for both versions, known issues, release notes, API pages and upgrade guides. Too
  much to send with every question, which is the point of week 2.
- The business documents the same desk also gets asked about (contracts, invoices, letters, a
  policy), which carry no version.
- The desk's own data in `support/`: its customers, each on version 2 or 3, and 300 tickets with
  their history, loaded into the database at start and read only through the agent's tools.
- Thirty starter questions in `eval/starter-questions.jsonl`, so week 2 has something to measure
  against before you write a test set of your own in week 3.

When the programme connects your repository it gives you your own product: the same structure,
size and traps, under a different company and product name, so your portfolio is your own work.

## What you are expected to produce

The sixteen output requirements in `weeks/0/REQUIREMENTS.md`. Each one is demonstrable, and each
is checked automatically, by the programme's hidden evaluation, or at the final session. Read them
now; they are the specification you are being measured against, and nothing in them is a surprise
later.
