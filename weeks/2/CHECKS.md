# Week 2 — What the gate checks

`make check WEEK=2` runs lint, format and strict types, then the week 0 to 2 tests under `fake_a`
and `fake_b`, all with `EMBED_PROVIDER=hash` (no download, deterministic), then the records gate:
`decisions/week-2.md` against `evidence/week-2.json`, and `ai-use/week-2.yml`.

Each test is one sentence that must hold. They check behaviour, not your numbers: your numbers
are in your evidence file.

**Chunking and metrics**

| Test | What must hold |
| --- | --- |
| `fixed_cuts_sentences_in_half` | The fixed strategy ends chunks mid-sentence (the control) |
| `sentence_chunker_never_cuts_mid_sentence` | Sentence chunks end on punctuation |
| `paragraph_chunker_keeps_a_table_row_whole` | A table row survives intact |
| `heading_chunker_keeps_heading_with_its_body` | A section starts with its heading and holds nothing of the next |
| `section_chunker_says_where_each_chunk_sits` | Every section chunk starts with the page title and section, without the front matter |
| `unknown_strategy_is_refused` | A typed error |
| `precision_recall_mrr_on_a_toy_example` | The three metrics are right on a list you can check by hand |
| `evaluate_averages_per_query` | Averages are per query, hit rate included |
| `precision_uses_k_not_the_number_of_hits` | Precision divides by k |

**Search and the version filter (O1)**

| Test | What must hold |
| --- | --- |
| `index_then_search_finds_the_right_document` | The right document comes first; scores are sorted |
| `reindex_replaces_rather_than_duplicates` | Indexing twice gives the same count |
| `search_respects_k_and_strategy` | k limits results; an unindexed strategy returns nothing rather than falling back |
| `unknown_strategy_on_index_is_400` | A typed error |
| `the_version_is_read_from_the_filename` | The version comes from the filename; unknown versions are none |
| `similarity_alone_returns_the_wrong_version` | The control: unfiltered, both versions come back for a version 3 question |
| `a_version_3_question_returns_no_version_2_material` | O1, over five questions |
| `the_filter_runs_before_ranking_not_after` | A filtered search still returns k hits |
| `pages_with_no_version_are_returned_for_every_version` | A page with no version survives a version search |

**Hybrid search**

| Test | What must hold |
| --- | --- |
| `bm25_scores_only_documents_that_share_a_query_term` | No shared term, no score |
| `bm25_rare_terms_count_for_more` | A rare term outweighs a common one |
| `bm25_a_long_document_does_not_win_by_being_long` | Length is normalised |
| `bm25_repeats_count_for_less_each_time` | Term frequency saturates |
| `reciprocal_rank_fusion_merges_by_rank_not_score` | Fusion by rank, with ties in first-seen order |
| `hybrid_search_keeps_the_version_filter_and_k` | Hybrid search returns k distinct hits and none from the wrong version |
| `hybrid_search_finds_an_exact_setting_name` | A setting name is found exactly |
| `unknown_search_mode_is_400` | A typed error |

**The context, and the tool**

| Test | What must hold |
| --- | --- |
| `select_and_compress_keeps_the_passage_that_answers` | The given compressor keeps the passage that answers |
| `select_and_compress_drops_unrelated_passages` | A passage far below the best score is dropped |
| `select_and_compress_trims_inside_a_passage` | A sentence sharing no term with the question is trimmed |
| `select_and_compress_respects_the_budget` | The passages kept fit the character budget |
| `search_docs_is_described_and_needs_a_version` | The tool and its three arguments are described; the version is required |
| `search_docs_refuses_malformed_calls_before_searching` | A missing or unknown version, an empty query or an out-of-range k never reaches the search |
| `search_docs_returns_only_that_versions_pages_with_what_a_citation_needs` | Only that version's pages, each with its file; no results is an answer in words |
| `context_experiment_runs_and_the_wrong_version_costs_accuracy` | The experiment runs its five settings; on the fake model the wrong version's page costs accuracy and burying costs tokens |

The measurements themselves (`make evidence WEEK=2`) are not graded by the gate. They run on your
real model, and your decision record has to match them.
