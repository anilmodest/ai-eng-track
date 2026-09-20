# Week 2 — What the gate checks

`make check WEEK=2` runs lint, format, strict types, then Weeks 0–2 tests under `fake_a` and
`fake_b`, all with `EMBED_PROVIDER=hash` (no download, deterministic).

| Test | Expects |
| --- | --- |
| `fixed_cuts_sentences_in_half` | the fixed strategy produces chunks that end mid-sentence |
| `sentence_chunker_never_cuts_mid_sentence` | every chunk but the last ends on punctuation; the clause-number weakness is present and known |
| `paragraph_chunker_keeps_a_table_row_whole` | an invoice table row survives intact |
| `heading_chunker_keeps_heading_with_its_body` | the Mileage section starts with its heading and holds nothing from the next section |
| `unknown_strategy_is_refused` | `ValueError` |
| `precision_recall_mrr_on_a_toy_example` | P@5 = 0.4, R@5 = 0.5, RR = 0.5 for a known list |
| `evaluate_averages_per_query` | averages over queries, including hit rate |
| `index_then_search_finds_the_right_document` | the expenses policy is the top hit for a mileage query; scores are sorted |
| `reindex_replaces_rather_than_duplicates` | indexing twice yields the same count |
| `search_respects_k_and_strategy` | `k` limits results; an un-indexed strategy returns nothing rather than falling back |
| `unknown_strategy_on_index_is_400` | typed error |

`scripts/retrieval_eval.py` is **not** part of the gate: it is evidence for the session, and its
numbers depend on the embedder you ran it with. Paste its table into your reflection.
