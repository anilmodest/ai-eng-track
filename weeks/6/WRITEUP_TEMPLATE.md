# What the feature did for the business

<!-- One page. Numbers, not adjectives. This is the document an interviewer will ask you about
     when they say "tell me about the last AI feature you shipped." Copy it to
     reflections/writeup.md and fill it in. -->

## The problem, in one sentence

<!-- Who was doing what by hand, how often, and what it cost them. Invent a plausible owner for
     this corpus if you have to, but make the numbers hang together. -->

## What we shipped

<!-- The service, in the reader's terms: "upload a document, get the key facts and a
     classification in about two seconds; ask a question and get an answer with the passage it
     came from, or a clear 'the documents do not say'". Link the live URL and the repo. -->

## What it does now, measured

| Measure | Before | After | Source |
| --- | --- | --- | --- |
| Time to classify one document | | | your trace report |
| Cost per document | | | your trace report, list price |
| Questions answered correctly | | | `scripts/eval.py`, hit rate |
| Questions correctly declined | | | `scripts/eval.py`, abstention rate |
| Attacks that get through | | | `scripts/attack.py` |

## What it would do at scale

<!-- 10,000 documents a day: monthly cost at list price, which provider, what breaks first
     (rate limits? the SQLite file? the numpy scan?), and what you would change before that day. -->

## What we did not ship, and why

<!-- The agent? Multi-provider fallback? Hybrid search? Say what the number was that made you
     leave it out. A decision with a number beats a feature without one. -->

## What went wrong on the way

<!-- The provider retirement. The quota. The injection that got through. Three lines each, and
     what changed because of it. Interviewers trust this section more than the one above. -->

## Versions

<!-- Tag deployed, commit, prompt versions, model. Straight from /health. -->
