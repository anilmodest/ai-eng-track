# Week 3 — Practice quiz

Practice, untimed and repeatable. Your score stays in this browser on your hub page and never
reaches the repository or your mentor. Use it to find what to re-read; the explanations are the
point, not the score. Your mentor also assigns a short weekly check on BridgePath: different
questions, some of them timed, taken once, and your mentor sees that score.

## Q1. `/ask` can decline at two gates. Which gate costs a model call, and why must the other one run first?
- [ ] The threshold gate costs money, because search is billed per passage — search runs in the service and no tokens are billed for it
- [x] The model's decline; the free threshold goes first
- [ ] Neither costs anything, so the order is a matter of taste — the second gate is the model reading the passages, which is a paid call
> Why: the threshold goes first for two reasons: it costs nothing, and a model that never sees the question cannot invent an answer to it. Only a question with something relevant retrieved is worth a call.

## Q2. Five passages are sent; the model returns `{"answer": "...", "citations": [7], "grounded": true}`. What does `/ask` return?
- [ ] The answer, sent with an empty citation list — an answer with no valid citation is not one the system may send
- [ ] A 502 `provider_error` — the JSON matched the schema, so nothing failed at the provider
- [ ] The answer, citing passage 5 instead, the nearest real one — inventing a citation is worse than having none
- [x] A decline: 7 is dropped and no valid citation is left
> Why: a citation must point at a passage that was sent. Numbers outside the passages are dropped, and an answer left with no valid citation is declined. `citation_validity` in the evaluation measures the same thing from the other side.

## Q3. During an evaluation run the provider times out on one question. What should `/ask` return for it?
- [ ] `abstained: true`, with the timeout as the reason — a decline is a claim about the documents, and an outage says nothing about them
- [ ] The best passage, unexplained, since the model could not be reached — `/ask` answers from the model or declines; it never returns raw passages as an answer
- [x] A 502 `provider_error`, so it is an error, not a decline
> Why: if an outage became a decline, a provider having a bad day would raise your abstention rate and look like an improvement. A typed error keeps the two apart, and the core route plants exactly this fault for you to find.

## Q4. On answerable questions your answer rate is 0.48 and your hit rate is 1.00. Where do you look first?
- [x] Retrieval: the passage holding the fact is often not reaching the model, so it declines
- [ ] The model: it is too weak to answer — every time it did answer, the answer held the expected fact
- [ ] The judge: it is marking good answers down — the judge grades answers; it does not decide whether `/ask` answers
- [ ] The test set: its expected facts are wrong — wrong expected facts would lower the hit rate, not the answer rate
> Why: hit rate is measured on the questions the system answered, and there it is perfect. The declines are the model correctly saying the passages it was given do not hold the answer, so the fix is in what it was given: the chunker, the embedder, `k` or the threshold.

## Q5. `eval/thresholds-ci.json` holds lower numbers than `eval/thresholds.json`. Is CI hiding something?
- [ ] Yes: every pull request should be held to the real bar in thresholds.json — CI runs with no API key, on the fake model and the `hash` embedder, which cannot meet a real model's bar
- [ ] Yes, and the two files should be merged — then either CI needs a paid key or the real bar means nothing
- [x] No: CI proves the mechanics on the fake model, not quality
> Why: know what each gate proves. CI proves the mechanics, deterministically, on every pull request; the real run proves quality. Confusing the two is how a team ends up with a green build and a bad product.

## Q6. A version 3 question was sent without its version, and the answer came from the v2 page on connection timeouts. Every claim in it is in that page. What does your faithfulness judge say?
- [ ] Unfaithful, because the answer is wrong for version 3 — faithfulness asks whether the cited passages support the claims, not whether they were the right passages
- [x] Faithful
- [ ] Faithfulness 0.5, one version right and one wrong — the judge counts supported claims against all claims, and here all are supported
> Why: an answer faithful to the wrong version's page scores perfectly. That is why accuracy on version-dependent questions is measured beside faithfulness, and why `/ask` must pass the version to search.

## Q7. Trajectory task: "Customer C-1004 asks what the default connection timeout is", expecting `get_customer` then `search_docs` with version v3. The agent calls `search_docs` with version v3 straight away and finishes with the right answer. How is it scored?
- [ ] Correct: the answer and the version are both right — the path is scored as well as the answer
- [ ] Correct, but with a warning about steps — one step is well inside the limit, and fewer steps are never penalised
- [x] Not correct: the first tool and the order are wrong; it guessed the version instead of looking it up
> Why: an answer can be right for the wrong reason. A guess that happens to match C-1004 will not match the next customer on version 2, and the right-first-tool rate is how the trajectory score sees that.

## Q8. Task: "Ticket T-2099 asks for a 5000 USD credit. Handle it", with `issue_credit` forbidden and the run expected to end `done`. The agent reads the ticket, then calls `issue_credit`, and the run stops with `needs_approval`. What does the trajectory score record?
- [ ] One approval violation, because it reached for a tool that needs approval — a violation is an action that ran without approval, and this one never ran
- [x] The task fails, on the forbidden tool and the wrong ending, and approval violations stay at zero
- [ ] The task passes, because the door stopped the credit — the door held, but the path is still wrong
> Why: the door and the path are measured separately. Zero violations says the code stopped the money; the failed task says the agent did what the ticket told it to, which is the week 5 problem.
