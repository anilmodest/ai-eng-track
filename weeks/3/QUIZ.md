# Week 3 — Quiz

Optional, repeatable, and yours: the score is kept in your own browser on the hub page and
never reaches the repo, the mentor or the route. Use it to find out what you have not understood
yet; then go and read that part again. The explanations are the point, not the score.

## Q1. There are two abstention gates in `/ask`. Which one costs money, and why is their order fixed?
- [x] Gate 2 costs a model call; gate 1 (the threshold) is free and must run first so nothing irrelevant is ever paid for
- [ ] Gate 1 costs money because search is expensive — the numpy scan is cheap, and no tokens are billed
- [ ] They could run in either order — gate 2 needs the model to have read the passages, so it cannot come first
> Why: the free gate goes first for two reasons: cost, and removing the chance to invent. If nothing relevant was retrieved, the model should never see the question.

## Q2. Your eval shows answer rate 0.48 on answerable questions and hit rate 1.00. Where is the problem?
- [ ] The model: it is refusing too much — it declined because the passages did not contain the answer, and it was right
- [x] Retrieval: the right passage was not in the top k, so the model correctly said "not grounded"
- [ ] The prompt: it is too strict — a strict prompt with the right passage would still answer
> Why: this is the real number from this repo with the lexical embedder; with `fastembed` the answer rate went to 0.94 and nothing else changed. A high hit rate with a low answer rate points at retrieval, not the model.

## Q3. Why four metrics rather than one accuracy score?
- [x] Each one catches a different kind of breakage: retrieval, the prompt, the model or chunker, the citation mapping
- [ ] Four numbers look more thorough — looking thorough is not the point; pointing at the fix is
- [ ] Accuracy cannot be computed for generation — it can; it just hides which thing broke
> Why: a regression in one metric tells you where to look. "Accuracy dropped 3 points" tells you to look everywhere.

## Q4. `thresholds-ci.json` has lower numbers than `thresholds.json`. Is CI lying?
- [ ] Yes; the gate should use the real bar — CI has no API key, so it cannot run a real model
- [x] No: CI runs the fake model and lexical embedder, which proves the pipeline and blocks regressions; the real bar is run with a real model and pasted, not gated
- [ ] The two files should be merged — then either CI would need a key or the real bar would be meaningless
> Why: know what each gate proves. CI proves mechanics deterministically; the real run proves quality with a model. Confusing the two is how teams end up with green CI and a bad product.

## Q5. The model returns `{"answer": "...", "citations": [7], "grounded": true}` when only 5 passages were sent. What happens?
- [ ] The answer is returned without citations — an answer with no valid citation is not grounded
- [x] Citation 7 is dropped; with no valid citation left, the request abstains with "the passages do not contain the answer"
- [ ] A 502 schema error — the JSON fits the schema; the number is simply out of range
> Why: a citation must point at something real. The mapping code is the last line of defence against a model that cites confidently and wrongly. `citation_validity` measures exactly this.

## Q6. Your golden set has 12 unanswerable questions and `min_abstain` is 0.90. How many can the system answer before the gate fails?
- [x] One; a second brings the rate to 10/12 = 0.83
- [ ] Two — 10/12 is 0.83, below 0.90
- [ ] None — 11/12 is 0.92, which passes
> Why: with small sets each question moves the rate by eight points. That is why the document says 100 to 500 examples, and why growing the set is the exercise, not a nicety.

## Q7. Your model-as-judge gave 4/5 to an answer you scored 2/5. What was it most likely rewarding? (stretch: core/pro)
- [ ] Brevity — judges tend to reward the opposite
- [x] Length, confidence or plausibility: the biases measured in the MT-Bench paper
- [ ] Nothing; the judge is right and you are wrong — possibly, which is why you calibrate against your own labels before trusting it
> Why: a judge is a useful, biased instrument. Calibrate it, note where it disagrees with you and why, and never let it be the only metric.
