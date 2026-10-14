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

## 2. One reference model for judging

The programme's hidden evaluation always runs your service on the same reference model, with the
programme's key, whatever you built with. So results compare across fellows, and nobody is
measured on a better or worse model than anyone else.

## 3. Paid models allowed, never required

You may build with a model you pay for. It changes nothing about how you are measured, because
measurement is on the reference model. You are never asked to pay for anything.

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
