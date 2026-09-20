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
| `precision_uses_k_not_the_number_of_hits` | P@5 with three hits returned is 1/5, not 1/3 |
| `select_and_compress_keeps_the_passage_that_answers` | the passage with the fact survives |
| `select_and_compress_drops_unrelated_passages` | a passage far below the best score is dropped |
| `select_and_compress_respects_the_budget` | total characters never exceed the budget |
| `select_and_compress_trims_inside_a_passage` | sentences sharing no term with the question go |

`scripts/retrieval_eval.py` and `scripts/degrade_repair.py` are **not** part of the gate: it is evidence for the session, and its
numbers depend on the embedder you ran it with. Paste its table into your reflection.
