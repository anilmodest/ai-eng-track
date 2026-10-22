# Week 1 — Concept

> **A model is an unreliable, expensive, non-deterministic third-party dependency. Treat it like
> one, and give it nothing you have not described exactly.**

Read this once (about 20 minutes). Then write the sentence above in your own words in
`reflections/week-1.md`, Q1, before you touch any code.

## Five ways a model betrays you

Everything in this week's exercise exists because of one of these.

**1. It fails.** Rate limits (HTTP 429), outages (5xx), network drops. Some failures pass if you
try again in a second. Some (a 400: you sent something wrong) never will, and retrying them burns
money and hides your bug. A good client knows the difference.

```mermaid
sequenceDiagram
    participant S as Service (retry.py)
    participant P as Provider
    S->>P: attempt 1
    P-->>S: 429 rate limited (retryable)
    Note over S: wait 0.5 s
    S->>P: attempt 2
    P-->>S: 429 (retryable)
    Note over S: wait 1.0 s
    S->>P: attempt 3
    P-->>S: 200 OK
    Note over S,P: three calls billed, one answer
    S->>P: a different request
    P-->>S: 400 bad request (NOT retryable)
    Note over S: stop at once: retrying our own mistake<br/>costs money and hides the bug
```


**2. It stalls.** A call that usually takes 800 ms sometimes takes 40 s, or never returns. Without a
timeout, one slow call holds a connection, then a worker, then your whole service.

**3. It costs.** Every call bills tokens in and tokens out. A desk taking 2,000 tickets a day, at
five calls a ticket and half a cent a call, spends 50 dollars a day, 18,000 a year. Sending the same
document twice is paying twice for the same answer. Sending a 60-page document when the first page
would do is paying for 59 pages of nothing.

```mermaid
flowchart LR
  A["POST /documents/{id}/extract"] --> K{"extractions row for<br/>doc_id + provider + model + prompt_version?"}
  K -- hit --> C["return it<br/>cached: true, $0"]
  K -- miss --> T[cap to MAX_INPUT_CHARS]
  T --> M["model call<br/>timeout, retry"]
  M --> V{fits DocumentExtract?}
  V -- no --> R["one repair call<br/>with the validation error"]
  R --> V2{fits now?}
  V2 -- no --> E["502 schema_error<br/>never a 500"]
  V -- yes --> W["store row:<br/>tokens, latency, cost"]
  V2 -- yes --> W
  W --> O["return it<br/>cached: false"]
```


**4. It varies.** Ask the same question twice and get two different answers. That is fine for prose
and fatal for data. Free text from a model is not data; it becomes data only after it has passed a
schema. When it does not fit, you ask once more with the error attached, then you fail loudly.

**5. It changes under you.** Providers deprecate models, change defaults, alter pricing. Free tiers
appear and vanish. If the model's name is in your code, a provider change is a code change, a
review, a deploy. If it is in configuration, it is two lines in `.env`.

```mermaid
flowchart LR
  subgraph service [your service: nothing here names a provider]
    E[extract.py] --> C["ModelClient protocol<br/>app/llm/client.py"]
    C --> G["registry.py<br/>reads MODEL_PROVIDER"]
  end
  G -- ".env says gemini" --> P1[(Gemini)]
  G -- ".env says groq" --> P2[(Groq)]
  G -- "tests" --> P3[("fake_a / fake_b")]
  style service fill:#eef3f8,stroke:#1f5f8b
```


This happened to this repo. Its first default provider was GitHub Models, chosen because it needed
no signup. GitHub retired the service on 30 July 2026. The fix was one entry in `registry.py` and
two lines in `.env.example`; not one line of the service changed. That is the whole argument.

## And the sixth: it calls the wrong tool

From this week the model does not only answer. It asks for things: "call `get_customer` with
`C-1004`". That request is **function calling**, and it is nothing more mysterious than structured
output with consequences. The model is shown each tool's name, a description and a JSON schema of
its arguments, and replies with a tool name and arguments in that shape.

Two things follow, and the week is built on both.

**The description is a prompt.** It is the only thing the model knows about the tool. "Gets data"
leaves the model guessing which of two tools a request needs, and it guesses wrong about half the
time. "Look up one of this desk's customers by id and get back which version and plan they are on"
does not. A tool's description has to say when to call it and what comes back, in the words a
request will use.

**Arguments are validated before anything runs.** A model will one day send `"1001"`, `"c1001"`,
an empty string or `"C-1001; DROP TABLE"`. The schema's constraints reject them before the tool
runs, and the model gets back a sentence it can act on, not a stack trace. The same goes for a
refusal: a customer on another desk is a boundary, answered in words, not an exception.

```mermaid
flowchart LR
  M["model: {tool, args}"] --> V{"args fit<br/>the schema?"}
  V -- no --> E["error: invalid arguments ...<br/>(the tool never runs)"]
  V -- yes --> A{"writes or<br/>spends?"}
  A -- "yes, no approval" --> N["needs approval<br/>(week 4)"]
  A -- no --> T["the tool runs"] --> R["text the model can read:<br/>a record, or refused: why"]
```

You measure both on a real model: how often it calls the right tool with valid arguments, with a
first-draft description and with yours (`scripts/tool_drill.py`), and how often plain "reply in
JSON" breaks the schema compared with schema-enforced output (`scripts/schema_drill.py`).

## What this looks like in the service

| Betrayal | Where the defence lives | What you do this week |
| --- | --- | --- |
| Fails | `app/llm/retry.py` | Retry 429 and 5xx with backoff; never retry 400 |
| Stalls | `app/llm/retry.py`, `MODEL_TIMEOUT_S` | Every attempt gets its own timeout |
| Costs | `app/llm/cost.py`, the `extractions` table | Record tokens and cost per call; never pay twice |
| Varies | `app/llm/structured.py`, `DocumentExtract` | Validate against a schema; repair once; typed error |
| Changes | `app/llm/registry.py`, `.env` | Provider and model are configuration |
| Calls the wrong tool | `app/tools/`, the argument models | Describe each tool exactly; validate before running; refuse in words |

## What you should be able to say by Friday

- Why a 400 is not retried and a 429 is.
- What "idempotent" means for this endpoint, and what key decides it.
- What one extraction costs on each of your two providers, and which one you would pick for a desk
  taking 2,000 tickets a day.
- Why `git diff main` shows no provider-specific code after you switched providers.
- How often plain "reply in JSON" broke the schema on your model, and how often schema-enforced
  output did: the number, not the rule.
- Which wrong tool calls your descriptions fixed, and which your constraints fixed.

Now run the three scripts in `explore/` (see `README.md`, "See it").

## Read more

Checked September 2026. Read the first two; the rest when the exercise makes you curious.

- [AWS Architecture Blog: Exponential Backoff and Jitter](https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/) — why the waits grow, and why adding randomness stops every client retrying at the same instant. The idea behind `retry.py`.
- [Stripe API: idempotent requests](https://docs.stripe.com/api/idempotent_requests) — the clearest production statement of "the same request must not be paid for twice", from a company that handles money.
- [Gemini API: structured output](https://ai.google.dev/gemini-api/docs/structured-output) and [OpenAI: structured outputs](https://platform.openai.com/docs/guides/structured-outputs) — what providers offer natively. This repo validates with Pydantic instead so it works on every provider; read these to see what you would gain and lose by switching.
- [OpenAI: function calling](https://platform.openai.com/docs/guides/function-calling) and [Anthropic: tool use](https://docs.anthropic.com/en/docs/build-with-claude/tool-use/overview) — how providers present tools to a model, and what their advice on descriptions is. Read the parts on writing descriptions.
- [Pydantic documentation](https://docs.pydantic.dev/latest/) — the schema is the contract; this is the tool that enforces it.
- [Gemini API: rate limits](https://ai.google.dev/gemini-api/docs/rate-limits) — the numbers behind "it fails". Check them before you plan a batch job.
- [3Blue1Brown: But what is a GPT?](https://www.youtube.com/watch?v=wjZofJX0v4M) (video, 27 min) — why the same prompt gives different answers: the model samples.
