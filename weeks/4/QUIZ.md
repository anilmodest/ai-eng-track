# Week 4 — Quiz

Optional, repeatable, and yours: the score is kept in your own browser on the hub page and
never reaches the repo, the mentor or the route. Use it to find out what you have not understood
yet; then go and read that part again. The explanations are the point, not the score.

## Q1. Why does `extract_document` need approval and `search_documents` does not?
- [x] One spends money on every call; a loop that calls it twenty times is a bill, and least agency says a tool that can spend is a tool an attacker can spend with
- [ ] Extraction is slower — speed is not the reason; cost and consequence are
- [ ] Search is read-only and extraction writes to the database — it writes a cache row; the money is the point
> Why: the human checkpoint sits on the actions that cost money or cannot be undone. Everything else the agent may do freely.

## Q2. The model calls a tool that does not exist. What does a good loop do?
- [ ] Raise an exception and end the request with a 500 — the loop must not crash on the model's mistake
- [x] Return an error message as the tool result so the model can read it and choose again
- [ ] Silently pick the closest tool name — guessing on the model's behalf is how wrong actions happen
> Why: `run_tool` turns unknown tools and invalid arguments into text. The model reads "error: unknown tool" and recovers; the service never sees an exception.

## Q3. The workflow makes N+1 calls for N invoices. The agent answered the same question in 2 calls. So the agent is cheaper?
- [ ] Yes, on every question — its cost varies per run and per question
- [x] On that question; the workflow's cost is fixed and predictable, which is a property worth paying for
- [ ] No, agents are always more expensive — not always; they are less predictable
> Why: cost per correct answer is the number to compare, and predictability is a cost too. The comparison table exists so the decision has both.

## Q4. `AGENT_MAX_STEPS=8` and the agent is on step 8 without calling `finish`. What is the result?
- [x] `status: max_steps`, no answer, and every step recorded with its tokens
- [ ] It keeps going until it finishes — that is the failure mode the wall exists to stop
- [ ] It returns the last tool result as the answer — a tool result is not an answer; the caller must know the loop ran out
> Why: a loop with no wall runs until the budget is gone. The wall makes "it did not finish" a visible outcome, with the transcript to explain why.

## Q5. Through MCP, a `reader` token calls `extract_document`. What comes back?
- [ ] The extraction; MCP clients are trusted — MCP is a transport, not a permission system
- [x] `denied: token 'reader' may not call extract_document; allowed: [...]` and the server stays up
- [ ] A rate-limit error — scope is checked before the limiter
> Why: `check_scope` runs before anything touches a tool. Least agency: a reader reads.

## Q6. Which of these is the best reason to choose the workflow over the agent for the six invoice questions?
- [ ] The agent got fewer right — true in our run, but partly because the provider's quota ran out
- [x] The workflow's steps are known in advance, so its cost and behaviour are predictable, and it scored the same as plain code
- [ ] Agents are not production-ready — some are; the question is whether this problem needs one
> Why: prefer the simplest thing that works. The agent's flexibility is worth its unpredictability only when the questions are ones nobody wrote steps for.

## Q7. Name a way past your own MCP scopes that the tests do not cover. (stretch: core/pro)
- [x] Any concrete one: a second token in `MCP_TOKENS`, a tool that calls another tool, an argument the schema does not bound, `MCP_APPROVED` read from the environment
- [ ] There is none; the tests cover scopes and rate limits — they cover what they cover
- [ ] Only a network attacker could — the boundary is inside the process; the caller is already past the network
> Why: the exercise is to look. A permission boundary you have not tried to cross is a diagram, not a boundary.
