# Week 3 — Grounding and evaluation, of answers and of paths

Areas 5 and 8. 9 to 10 hours. One of the two decisive weeks. Session 3 (Observation) at the end
of this week. Branch: `week-3`.

> **The one lesson.** Without a test you cannot see, every improvement is a guess.

## The gap it closes

Two habits interviewers probe directly: grounding and abstention, and evaluation. If a system
always produces an answer you cannot trust any of its answers, because a confident wrong one looks
exactly like a confident right one. Without a fixed set of questions run on every change, every
improvement is a guess and every regression is invisible until a customer finds it.

## What you are building

An endpoint that answers **only from the passages retrieved for it**, names the passage each
answer came from, and **declines** when the passages do not hold the answer; and the instruments
that say how often it is right.

```
POST /ask  { "question": "What is the default connection timeout?", "version": "v3" }
  -> { "abstained": false, "answer": "15 seconds, set with KESTREL_CONNECT_TIMEOUT.",
       "citations": [ { "n": 1, "filename": "manual-v3-connection-timeout.md", ... } ], ... }

POST /ask  { "question": "can kestrel send a text message when a run fails" }
  -> { "abstained": true, "reason": "the passages do not contain the answer", ... }
```

## Read (1 hour)

`CONCEPT.md`, then worked examples [B, C, D and E](../../docs/worked-examples.md#example-b-faithfulness-week-3).
Then, answering in `reflections/week-3.md`, Q1b:

1. **`app/api/ask.py`**: there are two abstention gates. Which one costs money, and why is the
   order they run in not negotiable?
2. **`scripts/eval.py`**: why several metrics rather than one "accuracy"? Which would drop first if
   the chunker regressed? Which if the prompt did?
3. **`app/eval/trajectory.py`**: an agent's answer can be right and its path wrong. Name two ways.

## See it (30 minutes, change nothing)

```
uv run python explore/w3_01_ask_without_a_net.py
```

Five questions the documents cannot answer, and five confident inventions. That is the system you
do not want.

## Build (5 to 7 hours)

Core items are needed for the lesson and checked by the gate; stretch items are shown to your
mentor and never block. Log your assistant use as you go in `ai-use/week-3.yml`.

### Core 1: grounded answers that decline (`app/api/ask.py`)

What must hold:

- **The cheap gate first.** If nothing retrieved clears `RELEVANCE_THRESHOLD`, decline with a
  reason and make **no** model call.
- **Answer and cite.** Numbered passages in, an answer, citation numbers and a `grounded` flag out
  (`complete_structured`); every valid citation maps to the real chunk; provider, model, tokens,
  latency and cost recorded.
- **The model's own decline.** `grounded: false`, an empty answer, or no valid citation: decline,
  with no answer and no citations. A citation number outside the passages is dropped.
- **Failures are not declines.** A provider error is a `502 provider_error`, never a decline: a
  decline is a claim about the documents.
- **The version.** A question that comes with a version is searched with it.

### Core 2: your own test set (`eval/my-test-set.jsonl`)

**One hundred questions, written from what a user would ask, not from what the documents say:**
60 straightforward, 20 the documents cannot answer, 20 whose answer depends on the version. Each
answerable row names the document it is answered from and the fact the answer must contain. Three
example rows show the shape.

The natural approach is to read a page and write a question it answers. That produces a set the
system passes trivially, a number that means nothing, and everyone trusts it. Real users ask in
their own words, half-specified, with the wrong terminology. The gate checks the composition and
that your questions do not repeat the documents word for word.

### Core 3: a judge you build and check (`app/eval/judge.py`, `app/llm/prompts/judge_v1.md`)

A judge for **faithfulness**: is every claim in the answer supported by the passages it cited? You
write the prompt (what a claim is, what support is, which biases to resist) and the call. Then you
check it against yourself:

```
uv run python scripts/eval.py --set eval/my-test-set.jsonl      # answers, with what they cited
uv run python scripts/judge_agreement.py --sample 30             # 30 of them to label
# label each one in eval/judge-labels.jsonl: true (faithful) or false
uv run python scripts/judge_agreement.py                         # how often your judge agrees
```

### Core 4: a trajectory set (`eval/trajectories.jsonl`)

Twenty tasks for the agent you build next week: which tools it should call, in which order, with
which arguments, which tools it must not touch, and how it should end. Three examples show the
shape. Include tasks where the version decides the answer, tasks that name a ticket, and tasks
where the right outcome is **not** to act. `scripts/trajectories.py` runs and scores them; until
week 4 every task scores zero, which is the honest number.

### Core 5: the gate (`make evidence WEEK=3`)

The evaluation already blocks a change that drops the score below the floors
(`eval/thresholds-ci.json` in CI). From this week the programme also runs **about 150 hidden
questions and 20 hidden trajectory tasks**, written for your own product, on every pull request,
and blocks a merge that drops the hidden score. You see the totals, never the questions.

| Measurement | Script | What it tells you |
| --- | --- | --- |
| `eval` | `scripts/eval.py --judge --set eval/my-test-set.jsonl` | Your system on your own hundred questions, with your judge |
| `threshold` | `scripts/threshold_curve.py` | Correct declines, wrong declines, inventions and wrong answers at seven thresholds |
| `judge` | `scripts/judge_agreement.py` | How often your judge agrees with your labels, and in which direction it is wrong |
| `trajectories` | `scripts/trajectories.py` | The trajectory command runs (week 4 makes the numbers mean something) |

### Stretch

- **A second marker for your labels**: ask someone else to label ten of the thirty, and report how
  often you agreed with each other. That is the ceiling your judge can reach.
- **Self-consistency**: run the judge twice on the same thirty and report how often it agrees with
  itself.

## Decide

**The relevance threshold**, as a trade between wrong answers and wrong declines, read off the
curve you measured; and **whether to trust your judge**, with its agreement rate and the
disagreements you read. Write `decisions/week-3.md`, quoting the evidence by key (for example
`- threshold.curve[3].invented = 5`).

## What proves it

1. **The gate**: `/ask`'s two gates and its citations, the evaluation blocking a seeded
   regression, your test set's composition, your judge's prompt and verdicts, your labels and
   trajectory tasks, and the threshold and trajectory commands running.
2. **The hidden evaluation**, on what you merge: from this week each measure of its system tier
   must reach 80% of the reference solution's on the same questions; below that goes on your
   mentor's brief, to be explained at the session. Its model tier, on your `model.json` model,
   informs the brief.
3. **The evidence file and the decision record.**

The result: a deliberately bad change demonstrated being blocked by the gate, and **the gap
between your own score and the hidden score, explained**. Session 3 opens with you explaining it.

**Anti-goal: do not write the test questions by reading the documents.**

### If you get stuck

- **Rate-limited?** The evaluation asks every question in one run. Iterate with
  `MODEL_PROVIDER=fake_a EMBED_PROVIDER=hash`, and spend the real provider on `make evidence`.
<!-- route:start -->
- **On `start`?** `routes/worked_example.py` answers a question from a single passage, with the
  `grounded` flag and one citation: the whole shape at `k=1`. Read it beside your stub.
<!-- /route -->
- **Stuck for more than an hour?** That is what the unblock calls are for. Use one.

Your route changes what this week gives you: the page in `routes/` in this folder says how.

## Submit

1. `make check WEEK=3` green, commit, `make evidence WEEK=3`, commit the evidence.
2. `decisions/week-3.md`, `ai-use/week-3.yml`, `reflections/week-3.md` (Q1 to Q5).
3. Open a pull request `week-3 → main` and send the link **24 hours** before the session.

## Session 3: Observation (60 minutes, end of this week)

Watched, not reported. Your mentor reads the brief beforehand.

| Min | What happens |
| --- | --- |
| 0–10 | You explain the gap between your own score and the hidden score, from your numbers |
| 10–35 | Assisted. A question your system gets wrong, served from the hidden pool: you diagnose it with your own assistant while your mentor watches what you accept and what you check |
| 35–55 | Tools closed. You defend your relevance threshold and your judge |
| 55–60 | Week 4's sentence, said back: *agency and model size are both costs* |

## Quizzes: practice here, a short check on BridgePath

`QUIZ.md` in this folder is the practice quiz, with an explanation for every answer. On the hub page
it is interactive, untimed and repeatable, and the score stays in your browser: it never reaches the
repository, your mentor or your route. Use it to find what to re-read.

Your mentor also assigns this week's check on BridgePath. It has different questions, some of them
timed, and you take it once; your mentor sees that score. It asks about what you built and measured
this week, so the work is the preparation.
