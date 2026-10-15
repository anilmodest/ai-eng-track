# Models: the minimum standard, and what you are measured on

Three rules, so that your numbers mean the same thing as everyone else's.

## 1. A floor for building

A model qualifies to build on if it:

- supports JSON output and tool calling through an OpenAI-compatible endpoint, and
- scores at or above the floor on the programme's 30-item qualification set (structured output,
  tool choice, grounded answering), which the programme runs on every candidate free model the
  week before each cohort opens.

The qualifying models are listed in the cohort file your programme sends you, because free tiers
change faster than any document. Choose one of them in week 1 and say which in your decision
record. If none of the free ones suits you, read rule 3.

As of 20 September 2026 the table looked like this; check the cohort file, not this page:

| Provider (`MODEL_PROVIDER`) | Free tier | Role |
| --- | --- | --- |
| `gemini` | Google AI Studio, no card | the default |
| `groq` | free tier | the usual second provider |
| `openrouter`, `cerebras`, `mistral` | free tiers | fallbacks |
| `ollama` | runs on your machine | a local second provider; recommended on pro |

## 2. Say which model you build on: `model.json`

At the root of your repository, `model.json` names it:

```json
{"provider": "groq", "model": "llama-3.1-8b-instant"}
```

`provider` is a `MODEL_PROVIDER` value and `model` the `MODEL_NAME` you use. Set it in week 1 with
your decision, and change it when the decision changes. The gate checks that it is well formed.

## 3. How the hidden evaluation measures you

The programme runs it on each week you merge, in two tiers, and both times it runs the
programme's own reference solution beside your service, on the same questions and the same model.
Your result is a share of the reference's: 0.9 means you got 90% of what the reference got.

- **System tier**: every hidden question and task, with your service on the fake model. No model
  and no quota, so it measures your code (retrieval, declining, version filtering, the approval
  gate, your defences) and is the same for everyone. This is the one with floors.
- **Model tier**: a smaller sample on a real model, the one in your `model.json` when the
  programme has it, the programme's default model otherwise. It shows how your pipeline does on
  a real model; it informs your mentor's brief and has no floor. If a free quota runs out midway,
  the run moves to another model and your mentor sees that it did.

Because the score is a share of the reference's on the same model, a stronger model does not make
your number bigger, and a weaker one does not make it smaller.

## 4. Paid models allowed, never required

You may build with a model you pay for. It does not change how you are measured: the share is
taken on the same model for you and the reference. You are never asked to pay for anything.

## The one frontier run (week 4)

In week 4 your agent runs its trajectory set once on a frontier model, through the programme's
capped key (`MODEL_PROVIDER=programme`; the programme gives you `PROGRAMME_MODEL_BASE_URL` and
`PROGRAMME_MODEL_TOKEN` as Codespaces secrets), so you can measure where a larger model earns its
cost without paying for it.

## When a provider disappears

It has happened to this repository: GitHub Models, the original zero-signup default, was retired
on 30 July 2026. The default moved to Gemini by changing one entry in `app/llm/registry.py` and
two lines in `.env.example`. Nothing in the service changed. That is week 1's argument, and the
reason every model name lives in configuration.
