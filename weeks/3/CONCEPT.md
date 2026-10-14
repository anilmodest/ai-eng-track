# Week 3 — Concept

> **A system that always answers is worse than one that sometimes declines. And nothing ships
> without a number that says how often it does each.**

Read this once (about 20 minutes). Write the sentence in your own words in `reflections/week-3.md`,
Q1, before you touch code.

## Grounding: answer from the passages or not at all

A model will answer any question you put to it. That is the problem. Grounding is the set of
disciplines that make it answer only from what you gave it:

- **Instruct** it to use only the retrieved passages. Necessary; never sufficient.
- **Threshold** retrieval. If nothing scored above a line, do not call the model at all. This
  saves money and, more importantly, removes the chance to invent.
- **Let it decline.** Give the model a structured way to say "the passages do not answer this"
  (`grounded: false`) and treat that as a first-class, expected outcome, not an error.
- **Cite.** Every answer names the passage it came from, so a reader (and a test) can check it.
- **Test abstention.** Deliberately ask questions the corpus cannot answer, and count how often
  the system invents one anyway. Nobody tests this until it embarrasses them.

```mermaid
flowchart TD
  Q[question] --> S[search top k]
  S --> G1{"top score ≥<br/>RELEVANCE_THRESHOLD?"}
  G1 -- no --> A1["abstain<br/>reason: threshold<br/>cost: $0, no model call"]
  G1 -- yes --> M["model reads numbered passages<br/>returns answer, citations, grounded"]
  M --> G2{"grounded and<br/>a valid citation?"}
  G2 -- no --> A2["abstain<br/>reason: passages do not contain the answer<br/>cost: one call"]
  G2 -- yes --> O["answer + citations<br/>each #91;n#93; mapped to a real chunk"]
  style A1 fill:#eef7ef,stroke:#2e7d4f
  style A2 fill:#eef7ef,stroke:#2e7d4f
```


## Evaluation: the thing that separates builders from enthusiasts

Interviewers ask two questions: how do you know it works, and what did it do for the business.
Evaluation is the answer to the first.

- **A test set**, typically 100 to 500 examples, written from what users ask, with the
  expected outcome for each. You write 100 this week. The programme's own 100
  (`eval/golden.jsonl`) is what CI runs on the fake model; yours is what your evidence runs on.
- **Three to five task-specific metrics**, not generic ones. Here: abstention rate on
  unanswerable questions, answer rate on answerable ones, hit rate on the expected fact, and
  citation validity. Not "accuracy". Not "BLEU".
- **A model as judge**, when a string match is not enough. Useful, and biased: it rewards length,
  confidence and plausibility. You build one for **faithfulness** (is every claim supported by the
  passages it cited?) and you do not trust it until you have labelled thirty answers yourself and
  counted how often it agrees with you.
- **In CI, blocking merges.** A versioned golden set and a threshold file. A pull request that
  drops a number below its line does not merge. That is what "we have evals" means.
- **Sampled from live traffic** after release, scored continuously, because the questions people
  actually ask drift away from the ones you wrote.

Four numbers, one grid. Each cell is a different thing going wrong.

| | answered | declined |
| --- | --- | --- |
| **answerable** | hit rate: did it contain the fact? citation validity: did it cite the right file? | answer rate drops → look at retrieval first |
| **unanswerable** | abstention rate drops → look at the prompt and gate 2 | correct |

And the gate in CI, which is what "we have evals" means:

```mermaid
flowchart LR
  PR[pull request] --> CK[make check WEEK=3]
  CK --> EV["scripts/eval.py<br/>golden.jsonl through /ask"]
  EV --> TH{"every metric ≥<br/>thresholds-ci.json?"}
  TH -- yes --> OK[merge allowed]
  TH -- no --> NO["merge blocked<br/>the table says which metric"]
  style NO fill:#fbeeed,stroke:#b3261e
```


## A test you cannot see

Your own test set has a weakness you cannot remove: you wrote it, so your system and your
questions share your blind spots. From this week the programme runs about 150 questions and 20
agent tasks you never see, written for your product, on every pull request, on one reference
model. You see the totals. If your own score is well above the hidden one, your questions are
easier than real users' (worked example E). The gap is the finding; chasing the hidden questions is
not the fix, rewriting your own is.

## Evaluating a path, not just an answer

From next week the system acts: it looks a customer up, searches, drafts, escalates. An answer can
be right for the wrong reasons: it guessed the version instead of looking it up, it searched four
times when once would do, or it reached for a refund nobody asked for. A **trajectory** is the
path, and four numbers describe it: the right tool (first, and in order), the steps it took, what
it cost, and whether anything that needs a person's approval ran without one. You write twenty
tasks this week; the agent you build next week is measured on them, and on twenty hidden ones.

## What this looks like in the service

| Idea | Where it lives | What you do this week |
| --- | --- | --- |
| Threshold and decline | `app/api/ask.py`, `RELEVANCE_THRESHOLD` | Build the two gates |
| Citations | `AskOut.citations` | Map the model's `[n]` to real chunk ids and files |
| Your test set | `eval/my-test-set.jsonl` | Write 100 questions from what users ask |
| Metrics and gate | `scripts/eval.py`, `eval/thresholds.json` | Run it, read it, make CI block on it |
| Judge | `app/eval/judge.py`, `scripts/judge_agreement.py` | Build it, label 30 answers, measure agreement |
| Threshold | `scripts/threshold_curve.py` | Read the threshold off a measured curve |
| Trajectories | `eval/trajectories.jsonl`, `app/eval/trajectory.py` | Write 20 tasks; the agent meets them in week 4 |

## What you should be able to say by Friday

- Your abstention rate on unanswerable questions, and what you did to raise it.
- Why an answer rate of 48 percent with a 100 percent hit rate points at retrieval, not the model.
- Which of your four metrics would move first if someone changed the prompt, and which if someone
  changed the chunker.
- What the judge got wrong when you compared it with your own labels, and in which direction.
- The gap between your own score and the hidden score, and what it says about your questions.

## Read more

Checked September 2026.

- [Hamel Husain: Your AI product needs evals](https://hamel.dev/blog/posts/evals/) — the most practical account of building an evaluation from real failures. Read it before you extend the golden set.
- [Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena](https://arxiv.org/abs/2306.05685) (Zheng et al., 2023) — where the known judge biases (position, verbosity, self-enhancement) were measured. `judge_v1.md` names them because of this paper.
- [Retrieval-Augmented Generation](https://arxiv.org/abs/2005.11401) (Lewis et al., 2020) — again, this time for the grounding argument: why the passages, not the parameters, should carry the facts.
- [Anthropic: Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) — the section on what to put in front of the model applies directly to how `/ask` numbers its passages.
