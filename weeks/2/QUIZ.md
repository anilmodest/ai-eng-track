# Week 2 — Practice quiz

Practice, untimed and repeatable. Your score stays in this browser on your hub page and never
reaches the repository or your mentor. Use it to find what to re-read; the explanations are the
point, not the score. Your mentor also assigns a short weekly check on BridgePath: different
questions, some of them timed, taken once, and your mentor sees that score.

## Q1. You move from `sentence` chunks to `paragraph` chunks. Recall@5 goes up and precision@5 goes down. Why both?
- [ ] The embedder handles long text worse — the effect shows even with the lexical `hash` embedder, which has no model at all
- [ ] Recall and precision always move together, so one of the numbers is wrong — they usually trade off
- [x] Bigger chunks hold more text each, so the answer lands in the top 5 more often, and each hit brings more unrelated text along
> Why: chunk size is a dial between "find it" and "find only it". That trade-off is why you measure both, across `paragraph`, `heading` and `section`, instead of arguing about the right size.

## Q2. What does the `hash` embedder know about meaning?
- [x] Nothing: it counts words, so two wordings of one question can look unrelated
- [ ] It knows synonyms from a small built-in list of related words that ships with the repository — it has none; every word is hashed to a slot and counted
- [ ] It knows word order, because each word's slot depends on where the word appears in the text — it discards order; only the counts survive
> Why: it hashes each word into one of 512 slots and counts, with no model and no download, so the mechanics are visible and the gate is deterministic. "How long does it wait for the source" shares no word with "connection timeout". Set `EMBED_PROVIDER=fastembed` and that phrasing starts finding the connection-timeout page: that difference is what an embedding model adds.

## Q3. MRR is 0.6 on your best configuration. In plain words?
- [ ] 60 percent of questions found a relevant chunk in the top k — that is hit rate, not MRR
- [ ] The average relevant chunk scored 0.6 cosine similarity — MRR is about rank, not score
- [x] The first relevant chunk usually sits first or second
> Why: MRR averages 1/rank of the first relevant hit, counting 0 when there is none; 0.6 is about 1/1.67. A product manager will accept "usually first or second"; they will not accept "0.6".

## Q4. Your `applicable_versions("v3")` returns `{"v3"}`. The O1 test passes. What breaks?
- [ ] Nothing; that is exactly the requirement — the requirement is the floor, not the whole behaviour
- [x] The FAQ pages, which carry no version, never come back, so version-independent questions find nothing
- [ ] Version 2 pages leak back into version 3 searches — they cannot; that is the one thing this set does prevent
> Why: a page with no version in its filename is stored under `ANY_VERSION` and applies to every version. Dropping it is the quiet failure: no error, no leak, just nothing where there should have been an answer. A filter is defined as much by what it must keep as by what it must exclude, and it runs before ranking, so a filtered search still returns k hits.

## Q5. Which kind of question does keyword search (BM25) rescue that meaning search alone tends to miss?
- [ ] Paraphrases, like "how long does it wait for the source" for the connection-timeout page — that is meaning search's strength, not keyword search's
- [x] Error codes and setting names, such as `E1104` or `KESTREL_CACHE_EXPIRY`, which must match exactly
- [ ] Questions that would otherwise return the wrong version — the version filter runs before both halves; BM25 knows nothing of versions
- [ ] Long questions, because BM25 favours long documents — length is normalised, so a long document does not win by being long
> Why: codes carry little meaning for an embedding, and a support desk is full of them; the tokenizer keeps them whole so BM25 matches them exactly. Reciprocal rank fusion merges the two lists by rank, because a cosine of 0.62 and a BM25 score of 7.3 are not on the same scale but "first" and "fifth" are.

## Q6. Why is `version` a required argument of `search_docs`, limited to the versions that exist, rather than optional?
- [x] Leave it optional and the model will omit it: the version trap is back
- [ ] Required arguments make each tool call cheaper for the model to describe and to send — cost is not the reason; the boundary is
- [ ] The search crashes when no version is given — it does not; it quietly searches the whole corpus, which is the danger
- [ ] So the system prompt never has to mention versions — the prompt may still mention them; the guarantee comes from the schema and the code
> Why: `get_customer` returns the version and `search_docs` is called with it. A call with a missing or unknown version, an empty query or a k out of range fails validation and never reaches the search. The boundary lives in the schema and the code, not in the prompt; every later week repeats that pattern.

## Q7. In the context experiment, the `wrong_version` setting gives the model the other version's page on the same topic. What do you expect to see?
- [ ] The model declines, because the passage does not match the question — the two pages are worded almost identically, so it answers
- [x] Confidently wrong answers that cite the very page they were given
- [ ] About the same accuracy as `right_version`, since the wording is nearly the same — the wording matches, the values differ, and the values are the answer
- [ ] A higher cost than `too_much` — cost follows how much context is sent, and one page is about what `right_version` sends
> Why: the model did not change; the context did, and so did the answers. No model fixes this, because similarity cannot tell the two pages apart: only the version filter choosing the right page does. Your "how much context to send" decision is read off the same table, from `right_version` against `too_much` and `buried`.

## Q8. On this corpus `numpy`, `sqlite_vec` and `qdrant` give near-identical quality numbers. What makes `sqlite_vec` the default here? (stretch: core/pro)
- [ ] It is the fastest of the three at this size — at this size speed does not separate them, and that is worth writing down
- [ ] Hosted vector databases are not allowed in the released image — `qdrant` can run from a local folder; the reason is a property of the store
- [x] The version is its partition key, so a version 3 search never scans version 2 vectors, and it is one file with no service to run
- [ ] FAISS would be better but needs a GPU — FAISS is left out because it has no metadata filtering, not for its hardware
> Why: the interface is the investment, and the property that decided it was filtering before ranking, not throughput. FAISS is absent from `docs/vector-stores.md` because the version constraint would need a second structure kept in step by hand.
