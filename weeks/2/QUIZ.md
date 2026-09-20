# Week 2 — Quiz

Optional, repeatable, and yours: the score is kept in your own browser on the hub page and
never reaches the repo, the mentor or the route. Use it to find out what you have not understood
yet; then go and read that part again. The explanations are the point, not the score.

## Q1. You move from `sentence` chunks to `paragraph` chunks. Recall@5 goes up and precision@5 goes down. Why both?
- [x] Bigger chunks each hold more of the corpus, so the relevant text lands in the top 5 more often, but each hit carries more irrelevant text with it
- [ ] The embedder is worse at long text — the effect shows even with the lexical embedder
- [ ] Recall and precision always move together — they usually trade off
> Why: chunk size is a dial between "find it" and "find only it". That trade-off is why you measure both instead of arguing about the right size.

## Q2. What does the `hash` embedder know about meaning?
- [ ] It knows synonyms from a small built-in dictionary — it has none
- [x] Nothing: it counts word stems, so "toner price" and "cost of toner" share one word and nothing else
- [ ] It knows word order — it discards it
> Why: it exists so the mechanics are visible without a download and so CI is deterministic. The moment you compare it with `fastembed` on the same queries, you have seen what an embedding model adds.

## Q3. The eval labels a hit as relevant when the chunk contains the expected phrase. What does that get wrong?
- [x] A chunk can contain the phrase and not answer the question, or answer it in other words and be marked irrelevant
- [ ] Nothing; phrase matching is exact — exactness is the problem, not the solution
- [ ] It over-counts chunks from the wrong document — the check also requires the expected document
> Why: labels are a model of relevance, not relevance. Knowing what your evaluation cannot see is part of trusting what it can.

## Q4. MRR is 0.6 on your best strategy. In plain words?
- [ ] 60 percent of queries found a relevant chunk — that is hit rate, not MRR
- [x] On average the first relevant chunk is at about rank 1.7: usually first or second
- [ ] The average relevant chunk scores 0.6 cosine — MRR is about rank, not score
> Why: MRR averages 1/rank of the first relevant hit. 0.6 ≈ 1/1.67. A product manager will accept "usually first or second"; they will not accept "0.6".

## Q5. You buried one fact in 40 paragraphs and a strong model found it at every position. What did you learn?
- [ ] Lost-in-the-middle is a myth — it was measured on other models and sizes; you tested one
- [x] Not at this size with this model; but the cost column moved 10×, so the budget lesson held anyway
- [ ] Context size does not matter — it cost ten times as much for the same answer
> Why: an experiment that does not show the effect is still an experiment. Say what you tried, what you saw, and what you would try next (`--filler 200`). That is the reflex Week 3 turns into an evaluation.

## Q6. `search()` is a numpy cosine scan over every chunk. When do you replace it, and what must stay the same?
- [x] When the scan is slower than the model call it feeds (tens of thousands of chunks); the replacement must keep returning ranked `Hit`s so nothing above it changes
- [ ] Immediately; a vector database is always faster — for a few hundred chunks it is slower and harder to reason about
- [ ] Never; SQLite is enough — it is enough for this corpus, not for every corpus
> Why: the interface is the investment. `Hit` with a score, ordered, is what `/ask` and the agent tools consume. Swap the engine, keep the contract.

## Q7. Hybrid search with reciprocal rank fusion improved hit rate on 4 of 30 queries and hurt none. Should you ship it? (stretch: core/pro)
- [ ] Yes, any improvement is worth it — only if its cost is worth it: two searches per query, more code, more to explain
- [x] Probably, if the latency and complexity cost is small; say the number that decided it either way
- [ ] No, 4 of 30 is noise — it may be; that is why you state the number and the trade-off, not a verdict
> Why: the answer the track wants is not yes or no; it is a decision with a number and a cost beside it. That is the shape of every "should we ship X" question from here to Week 6.
