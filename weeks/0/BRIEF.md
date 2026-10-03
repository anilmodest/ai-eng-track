# The brief

This is how the work arrives. Read it as a client wrote it, because one did.

## The client

A software company with its product on a third major version. Versions 2 and 3 are both supported
and both in active use by customers.

## The problem

The support desk answers the same documentation questions every day. Most of them are answerable
from the manual. Two things make this harder than it sounds.

The documentation for version 2 and version 3 is almost identical in wording and different in
substance, so an answer from the wrong version is worse than no answer at all. And a meaningful
share of incoming questions are not covered by the documentation, so a system that always answers
will confidently invent things.

## What they want

A service that takes a customer question and the version they are running, and returns an answer
drawn only from the documentation for that version, with a citation, or declines to answer.

They need to know how often it is right, how often it wrongly declines, how often it wrongly
answers, and what it costs per question — and they need those numbers produced automatically
rather than claimed.

## The constraint they set

The desk will not adopt anything they cannot audit. Every answer has to be traceable to a source,
every measurement has to be reproducible, and any change that makes the system worse has to be
caught before it reaches a customer.

## The example the whole build turns on

A user asks: **how do I configure the connection timeout?**

In version 2 the setting is a value in a configuration file. In version 3 it moved to an
environment variable, and the old setting is now silently ignored. The two documentation pages are
nearly identical in wording.

A system matching on similarity alone finds the version 2 page, because the words match almost
perfectly, and answers with total confidence. The user follows the instructions and nothing
happens.

Open `corpus/manual-v2-connection-timeout.md` and `corpus/manual-v3-connection-timeout.md` now and
read them side by side. Everything in the next six weeks is downstream of that pair.

## Why this brief and not a simpler one

Every candidate now has a document question-answering project, and having one signals nothing. The
version constraint is what turns a common project into a discriminating one, because it makes five
things real that are otherwise exercises:

| | |
| --- | --- |
| Retrieval becomes genuinely hard | Matching on similarity alone returns the wrong version. Filtering on metadata is the fix, and that is a skill rather than a trick |
| Declining becomes necessary | Some questions are genuinely not covered, so abstention can be measured instead of discussed |
| Tool use has an obvious purpose | The system needs to look up which version a given customer is running, which is a real reason to call a real system |
| The attack surface is real | A documentation page carrying hidden instructions is a genuine risk for a system whose entire job is reading documents |
| The business metric is obvious | Support questions deflected, at a cost per question. A hiring manager understands that sentence immediately |

## One hard constraint on the corpus

It must **fail** a no-retrieval baseline. Before any retrieval is built, you ask the test questions
with no documents attached and record the score. If the model already answers correctly from its
own training, retrieval is doing no work and every measurement afterwards is meaningless.

`uv run python scripts/baseline.py` does this, and week 2 asks you to run it. It is also what
proves to you that the work has a point.

The product in `corpus/` is invented, and so is every setting name, default and unit in it. That
is why.

## What ships with the repository

- The manual, as a fixed snapshot: six topics, each written for version 2 and version 3.
- The business documents the same desk also gets asked about, which carry no version.
- Thirty starter questions in `eval/starter-questions.jsonl`, so week 2 has something to measure
  against before you write a test set of your own in week 3.

## What you are expected to produce

The twelve output requirements in `weeks/0/REQUIREMENTS.md`. Each one is demonstrable, and each is
checked either automatically or at the final session. Read them now; they are the specification
you are being measured against, and nothing in them is a surprise later.
