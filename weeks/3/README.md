# Week 3 — Grounding and evaluation

Areas 5 and 8 of the track. About 10 hours including the session. Branch: `week-3`.

## What you are building

An endpoint that answers a support question **only from the passages retrieved for it**, names
the passage each answer came from, and **declines** when the passages do not hold the answer.

```
POST /ask  { "question": "What is the personal car mileage rate?" }
  -> { "abstained": false,
       "answer": "45 pence per mile for a personal car.",
       "citations": [ { "n": 1, "chunk_id": 37, "document_id": 4,
                        "filename": "policy-contoso-expenses.md",
                        "score": 0.71, "text": "..." } ],
       "top_score": 0.71, "tokens_in": 812, "cost_usd": 0.0004 }

POST /ask  { "question": "zxq plimbo vortex kettle" }
  -> { "abstained": true, "reason": "nothing cleared the relevance threshold",
       "citations": [], "cost_usd": 0.0 }
```

Why the support desk cares: a system that always answers is worse than one that sometimes
declines, and the desk will not adopt what it cannot audit. An answer with a citation can be
checked by a human in five seconds. A confident answer with no source has to be trusted.

Two words you will use all week. **Grounding** is the set of disciplines that make the model
answer from the passages rather than from its parameters. **Abstention** is declining on purpose,
as a first-class outcome with a reason attached — not an error, not a timeout, not a shrug.

## The hard part is the measurement

The source document names Retrieval (last week) and Evaluation (this week) as the two areas that
decide most hiring outcomes. Building the gates below is an afternoon. Saying how often they are
right is the thing most candidates cannot do.

So the week's real deliverable is a number. Four numbers, in fact, computed by one command, over a
fixed set of questions with known answers, with a floor under each one. A floor that runs on every
proposed change is the difference between a demo and a system.

This is also the week's interview answer. "How do you know it works?" is a real question, and
"there is a command, here is the table it prints, and this pull request was blocked by it" is a
real answer. "It seemed good when I tried it" is not.

## Run it and watch (1 hour, change nothing)

```
uv run python explore/w3_01_ask_without_a_net.py
```

One unanswerable question, one real passage, three rounds. Watch the model invent a penalty clause
in round A, hedge in round B, and decline in a testable way in round C. Round C is the shape you
are building.

Then run the evaluation on the given service, with the fake model and the lexical embedder:

```
MODEL_PROVIDER=fake_a EMBED_PROVIDER=hash uv run python scripts/eval.py --thresholds eval/thresholds-ci.json
```

Read the table and the "worth a look" list. Every line there is a question you can go and ask.
Both commands need a provider key only for the first: see the main `README.md`, *Model access*.

## Read it (1 hour, change nothing)

Read `CONCEPT.md` in this folder first, then the following in this order, and answer the three
questions in `reflections/week-3.md`, Q1b:

1. **`app/api/ask.py`** — there are two abstention gates. Which one costs money, and why is the
   order they run in not negotiable?
2. **`scripts/eval.py`** — why are there four metrics rather than one "accuracy"? Which one would
   drop first if the chunker regressed? Which if the prompt did?
3. **`eval/thresholds.json`** versus **`eval/thresholds-ci.json`** — why two? What does CI prove,
   and what does it not?

Then open `tests/weeks/test_week3.py`. **It is the specification.** Every test name is one
behaviour, and the table below is the order to make them pass.

## Build it (5 hours)

`app/api/ask.py` is yours. The prompt, the schemas, retrieval and the eval script are given. Run
`make next` any time to see where you are.

Build in this order. Each step is done when the tests named beside it go green.

| # | Build | Done when these pass |
| --- | --- | --- |
| 1 | **Gate 1, the cheap one.** Search, then if the top score is below `RELEVANCE_THRESHOLD`, return `abstained: true` with a reason naming the threshold, and make **no** model call | `abstains_below_threshold_without_calling_the_model` |
| 2 | **Ask and cite.** Number the passages `[1]..[k]`, call the model for an `AskAnswer` (`answer`, `citations`, `grounded`) through `complete_structured`, map each valid `[n]` to the real chunk (id, document, filename, score, text), and record provider, model, tokens, latency and `cost_usd` | `answers_with_citations_that_resolve`, `valid_citations_map_to_real_chunks` |
| 3 | **Gate 2, the model's own decline.** `grounded: false`, an empty answer, or not one valid citation number → `abstained: true`, no answer, no citations, reason `the passages do not contain the answer` | `abstains_when_the_model_says_not_grounded`, `citation_numbers_outside_the_context_are_dropped`, `unanswerable_question_is_declined` |
| 4 | **Failures are not abstentions.** A provider error is a `502 provider_error`. Never a decline, because a decline is a claim about the documents | `provider_failure_is_not_an_abstention` |
| 5 | **The gate runs.** `scripts/eval.py` is given and unchanged; it passes only when the whole route behaves, and fails when a metric is under its floor | `eval_gate_passes_on_ci_thresholds`, `eval_gate_blocks_when_a_threshold_is_not_met` |

Gate 1 first is not a preference. It is the gate that saves money, and it is the only part of the
week you can test without a model at all — zero calls is the assertion.

The **relevance threshold** is `RELEVANCE_THRESHOLD` in `.env`, the retrieval score under which
nothing is considered worth answering from. The repo default is `0.30`. It is a product decision
disguised as a float: raise it and you decline more, lower it and you invent more.

`make check WEEK=3` as often as you like. Red is the week's work, not a problem.

### If you get stuck

- **Rate-limited mid-exercise?** The free tiers are small, and the eval asks every golden question
  in one run. Iterate with `MODEL_PROVIDER=fake_a EMBED_PROVIDER=hash` and spend the real provider
  only on the runs you are going to paste.
- **A test is failing and the message is not obvious?** Open the test. It is short, and it says
  exactly what it expected.
- **On `start`?** `routes/worked_example.py` answers a question from a single passage, with the
  `grounded` flag and one citation: the whole shape at `k=1`. Read it beside your stub rather than
  instead of it.
- **Stuck for more than an hour?** That is what the two unblock calls are for. Use one.

Your route changes what this week gives you: read `routes/start.md`, `routes/core.md` or
`routes/pro.md` in this folder. The hub shows which one is yours.

## Measure it and block a bad change (1 hour 30 minutes)

This is the point of the week, not the tidy-up after it.

```
uv run python scripts/eval.py                          # real model, real bar (thresholds.json)
EMBED_PROVIDER=fastembed uv run python scripts/eval.py # real embeddings too
```

Four task-specific metrics, each a different thing going wrong:

| Metric | Reads as |
| --- | --- |
| `abstain_rate_unanswerable` | of the questions the corpus cannot answer, how many did you decline? |
| `answer_rate_answerable` | of the questions it can answer, how many did you answer? |
| `hit_rate` | of the answerable questions you answered, how many held the expected fact? |
| `citation_validity` | of the answers, how many cited a chunk from the expected document? |

`hit_rate` and `citation_validity` together are what people mean by **faithfulness**: the answer
says what the cited passage says, and the citation points where it claims to. **Citation validity**
on its own is the weaker, mechanical half — the `[n]` resolves to a real chunk from the right file.

Paste both tables into your reflection. If `answer_rate_answerable` is low while `hit_rate` is
high, you have seen the Week 2 lesson from the other side: fix retrieval, not the prompt.

Then grow the **golden set** — `eval/golden.jsonl`, the fixed list of questions with their expected
outcomes that every run is scored against. Add at least 20 questions you would actually ask of
these documents, with expected facts, and at least 5 more that cannot be answered. Run again. The
numbers will move, and that is the exercise: a metric over a set you wrote yourself is a metric you
understand.

Finally, prove the **regression gate** — the eval running on every proposed change and failing the
change when a number drops below its floor.

```
make check WEEK=3     # already runs scripts/eval.py against the CI thresholds
```

Open a pull request that deliberately breaks citations (return `[]`) and watch CI go red. Revert
it. That red run is the evidence; link it in your reflection. A gate nobody has seen fire is not
known to work.

## Submit (30 minutes)

- `reflections/week-3.md`: Q1 (the concept in your words), Q1b (the three reading questions),
  Q2 (what surprised you), Q3 (what you would change), Q4 (what you contributed and how you
  checked it), Q5 (help you used), both eval tables, the red CI run, and the golden set additions.
- Open a pull request `week-3 → main`. CI runs the gate, including the eval. Fix anything red.
- Send the link to your mentor **24 hours** before the session, not at the start of it.

## Session 3: Observation (60 minutes, end of this week)

Not a progress report. Your mentor watches you work, on a task you have not seen, for most of the
hour, and says very little. The point is to see how you think, check and recover, not what you
built. Have the service running and your evaluation ready to run.

| Min | What happens |
| --- | --- |
| 0–5 | Your mentor states the task (grounding or evaluation shaped; you will not have seen it) |
| 5–45 | You work. Aloud. Your mentor watches: where you look first, what you run, how you check |
| 45–55 | Your mentor asks three questions about what they saw, and reviews the Week 2 and 3 PRs |
| 55–60 | Week 4's sentence: *prefer the simplest thing that works* |

**Pass line:** CI green including the eval gate, the red run linked, and from your own numbers,
where a wrong answer would have come from.

## Optional: self-test

`QUIZ.md` in this folder, with an explanation for every answer. On the hub page it is interactive.
The score stays in your browser: it never reaches the repository, your mentor or your route. Use
it to find what to re-read, not to measure yourself.
