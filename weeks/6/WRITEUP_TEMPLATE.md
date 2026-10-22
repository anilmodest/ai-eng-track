# What the feature did for the business

<!-- One page. Numbers, not adjectives. This is the document an interviewer will ask you about
     when they say "tell me about the last AI feature you shipped." Copy it to
     reflections/writeup.md and fill it in. -->

## The problem, in one sentence

<!-- Who was doing what by hand, how often, and what it cost them: the desk answering the same
     tickets every day, and the wrong answers when a version 3 customer was given the version 2
     fix. Use the brief's numbers where it has them; where you assume one (tickets a day, minutes
     per ticket), say so, and make the numbers hang together. -->

## What we shipped

<!-- The service, in the reader's terms: "give it a ticket; it finds the customer's version,
     answers from that version's manual with the page it came from, or says plainly that the
     manual does not say; it looks up the customer and the ticket history, drafts a reply a
     person reads before it is sent, and escalates or credits only when a person says yes".
     Link the release (the image tag) and the repo. -->

## What it does now, measured

| Measure | Before | After | Source |
| --- | --- | --- | --- |
| Tickets resolved without a person | | | your trajectory report and evaluation |
| Accuracy on version-dependent questions | | | `scripts/eval.py`, `accuracy_version` on your set |
| Questions correctly declined | | | `scripts/eval.py`, `decline_rate_no_answer` |
| Wrong answers | | | `scripts/eval.py`, answered without the expected fact (1 − `hit_rate`) |
| Approval violations (must be 0) | | | `scripts/trajectories.py`, `unapproved_actions` |
| Cost per ticket | | | `scripts/trace_report.py`, list price |
| Trajectory tasks right, mean steps per task | | | `scripts/trajectories.py`, `correct_rate`, `avg_steps` |
| Attacks that get through | | | `scripts/attack.py` |
| Release tag, and minutes to roll back | | | the release workflow, your rollback |

## What it would do at scale

<!-- N tickets a day (pick N: ten times the desk's volume, say): monthly cost at list price,
     which provider, what breaks first (rate limits? the daily budget? the SQLite file? the numpy
     scan? the people approving actions?), and what you would change before that day. -->

## What we did not ship, and why

<!-- The LangGraph rebuild? Multi-provider fallback? Hybrid search? Streaming? Say what the
     number was that made you leave it out. A decision with a number beats a feature without one. -->

## What went wrong on the way

<!-- The provider retirement. The quota. The injection that got through. Three lines each, and
     what changed because of it. Interviewers trust this section more than the one above. -->

## Versions

<!-- Tag released, commit, prompt versions, model. Straight from /health. -->
