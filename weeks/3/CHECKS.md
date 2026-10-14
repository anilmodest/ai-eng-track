# Week 3 — What the gate checks

`make check WEEK=3` runs lint, format, strict types, then the week 0 to 3 tests under `fake_a` and
`fake_b` with `EMBED_PROVIDER=hash`, then the evaluation gate (`scripts/eval.py` on the
programme's golden set, the hand-written corpus and `eval/thresholds-ci.json`), then the records
gate.

**`/ask`**

| Test | What must hold |
| --- | --- |
| `answers_with_citations_that_resolve` | An answerable question gets an answer, a citation to the right file and a real chunk, and recorded usage |
| `abstains_below_threshold_without_calling_the_model` | Nothing relevant: declined, with a reason, and no model call |
| `abstains_when_the_model_says_not_grounded` | The model's own `grounded: false` becomes a decline with nothing in it |
| `unanswerable_question_is_declined` | A real-looking question the documents cannot answer is declined |
| `citation_numbers_outside_the_context_are_dropped` | Only citations to passages that were sent survive |
| `valid_citations_map_to_real_chunks` | Every citation resolves to a chunk that was retrieved |
| `provider_failure_is_not_an_abstention` | A provider failure is a typed 502, never a decline |

**The evaluation gate**

| Test | What must hold |
| --- | --- |
| `eval_gate_passes_on_ci_thresholds` | The evaluation passes its floors on the programme's set |
| `eval_gate_blocks_when_a_threshold_is_not_met` | A seeded regression fails it |

**Your instruments**

| Test | What must hold |
| --- | --- |
| `my_test_set_has_100_questions_in_the_required_composition` | 100 distinct questions: 60 straightforward, 20 unanswerable, 20 version-dependent, each answerable one with its document and fact |
| `my_test_set_is_written_from_what_a_user_would_ask` | Not copied from the programme's set, and no more than five repeat a document eight words in a row |
| `the_judge_prompt_is_written` | The prompt is yours, and speaks of claims, faithfulness and what is unsupported |
| `the_judge_grades_faithfulness_from_the_passages` | A supported answer is faithful; one with an invented claim is not, and the claim is named |
| `judge_labels_are_thirty_answers_you_labelled` | Thirty answers with your own true or false, some of each |
| `trajectory_set_has_twenty_well_formed_tasks` | Twenty valid tasks using real tool names, some deciding on the version, some where acting is forbidden |
| `trajectory_scoring_reads_the_path` | The given scorer, on a right and a wrong path |
| `the_trajectory_command_runs` | `scripts/trajectories.py` runs end to end |
| `the_threshold_curve_runs_and_declines_more_as_it_rises` | `scripts/threshold_curve.py` runs, and a higher threshold never declines less |

Two threshold files, on purpose: `eval/thresholds-ci.json` is what CI holds on the fake model and
proves the pipeline; `eval/thresholds.json` is the real bar, met with a real model. Your real
numbers are in `evidence/week-3.json`, and the programme's hidden evaluation is on your pull
request.
