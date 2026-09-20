# Week 5 — Quiz

Optional, repeatable, and yours: the score is kept in your own browser on the hub page and
never reaches the repo, the mentor or the route. Use it to find out what you have not understood
yet; then go and read that part again. The explanations are the point, not the score.

## Q1. Where is model cost attributed in a trace, and why does the root carry a roll-up?
- [x] On the `model.call` span, and added to the root at the same time, so a request's cost is one read and a step's cost is still visible on the step
- [ ] Only on the root; steps are for timing — then you could not say which step spent it
- [ ] Only on the leaf; the root is computed at query time — it could be, but then every dashboard query walks every tree
> Why: `add_usage` writes twice on purpose. Attribution answers "which step"; the roll-up answers "how much" cheaply.

## Q2. A request fails because the provider returned 400. What error kind does the root span carry?
- [ ] `unknown` — that is reserved for unhandled exceptions
- [x] `provider_error`
- [ ] `schema_error` — the model never answered, so there was nothing to validate
> Why: the taxonomy is the dashboard's vocabulary. "12 failures" says nothing; "9 provider_timeout, 3 schema_error" says which provider to call and which prompt to look at.

## Q3. What does `detect_injection` catch, and what will it never catch?
- [x] Known instruction phrasings; not another language, an encoding, a paraphrase, or an instruction that looks like data
- [ ] Every injection, if the pattern list is long enough — no list is long enough for language
- [ ] Nothing useful — it removes most casual attempts cheaply, which is worth having alongside the fence and the output scan
> Why: the pattern filter is one of four defences and the weakest. Knowing what it cannot do is what tells you the others are not optional.

## Q4. `scan_output` flags a figure in the model's key facts that the source never states. What should the service do?
- [ ] Nothing; the model is probably right — a figure that is not in the document did not come from the document
- [x] It depends on who reads the output next: refuse, lower confidence, return the flag, alert. The point is that model output is input to something
- [ ] Always refuse — sometimes right; the flag exists so that the next consumer can decide
> Why: "treat model output as untrusted input to whatever comes next" is the whole security half of the week in one sentence.

## Q5. `DAILY_BUDGET_USD=1.00` and a runaway agent spends it in four minutes. What happens at minute five?
- [x] Every model-backed request returns 429 `budget_exceeded`, visible in the error taxonomy, until the 24-hour window moves on
- [ ] The agent slows down — there is no throttling, only a cap
- [ ] Nothing until the next day's invoice — the budget reads the traces, so it knows now
> Why: blast radius. The budget does not make the loop smarter; it bounds what the loop can cost before a person finds out.

## Q6. With `GUARD_ENABLED=false` the hostile purchase order extracts as a contract. What single change would have stopped that particular attack, and why is it not enough?
- [ ] `detect_injection` alone — the phrase in the document matches, so yes; but a paraphrase would walk past it
- [x] The fence plus preamble alone would stop this one; it is not enough because a model can still be talked out of a rule by data, so the output scan and the limits stay
- [ ] The budget — the budget limits damage; it does not prevent it
> Why: no single defence is sufficient, and the exercise makes you build all four so that you have seen each one fail alone.

## Q7. A peer's attack got through your guard. It was in French. Which defence should have held? (stretch: core/pro)
- [x] The fence and preamble (the model is told fenced text is data regardless of language) and the output scan (a wrong figure is wrong in any language); the pattern list was never going to
- [ ] A French pattern list — and then Spanish, then base64, then zero-width characters; the list never ends
- [ ] Nothing could have — something could; and the question is which, so that you know what you rely on
> Why: the core exercise is to find an attack the filter cannot catch and prove the defence that does. A defence you can name is a defence you can test.
