# Worked examples: reading the numbers

Weeks 2 and 3 are where the learning curve rises: chunking, hit rate, precision, recall, mean
reciprocal rank, faithfulness and decline rate arrive together. Each example below uses one small
case you can check by hand. For every number: what it is, what it means for a user, and what a
change in it would and would not tell you.

The numbers are illustrative. They are not targets: the floors are set by the programme and
reported on your pull request.

## Example A. Retrieval metrics (week 2)

**The case.** A version 3 customer asks: how do I configure the connection timeout? Two pieces in
the corpus are truly relevant: the version 3 environment-variables section, and the version 3
release note saying the old setting is now ignored. With no version filter, the retriever returns
its top five:

| Rank | Piece returned | Relevant? |
| --- | --- | --- |
| 1 | Version 2 configuration file, timeout setting | No, wrong version |
| 2 | Version 3 environment variables | Yes |
| 3 | Version 3 troubleshooting, slow connections | No |
| 4 | Version 3 release note, setting moved | Yes |
| 5 | Version 2 changelog | No |

| Number | Here | What it means for a user |
| --- | --- | --- |
| Precision at 5 | 2 relevant of 5 returned: 0.4 | Three of the five pieces the model reads are noise, one of them actively misleading. |
| Recall at 5 | 2 of the 2 relevant found: 1.0 | Everything needed is somewhere in what the model sees. |
| Hit at 1, hit at 5 | 0 and 1 | The single best match is wrong. A system that sends only the top piece answers from version 2, and the customer's change does nothing. |
| Reciprocal rank | First relevant at rank 2: one divided by 2, 0.5 | Rewards putting the first right piece near the top. |

**Across questions.** Hit rate and MRR are averages over the test set. With four questions whose
first relevant piece sits at ranks 2, 1 and 3, and one where nothing relevant is found, the
reciprocal ranks are 0.5, 1, 0.33 and 0. MRR is their average, about 0.46. Hit rate at 5 is 3 of
4, 0.75.

**After the version filter.** Search only inside version 3. The two relevant pieces now rank first
and second, so precision at 5 rises, hit at 1 becomes 1, and reciprocal rank becomes 1.0. That is
the week 2 fix, measured rather than asserted.

> **What these numbers do not tell you.** They score finding, not answering. Recall of 1.0 with
> precision of 0.4 means the answer is in there, buried in noise that costs tokens and can pull the
> model the wrong way, which is what the week 2 context experiment shows. A higher MRR on the 30
> starter questions says nothing about real users until it holds on the hidden set as well.

## Example B. Faithfulness (week 3)

**The case.** The system answers the same question from the two version 3 pieces with four claims:
set the timeout as an environment variable; the value is in seconds; the old configuration setting
is ignored in version 3; restart the service after changing it. The first three appear in the
retrieved text. The fourth does not.

**The number:** 3 of 4 claims supported, faithfulness 0.75. **For the user:** one instruction in
four came from the model, not your documents. Nobody can check it, yet the citation implies they
can. A rise means fewer invented claims. It does not mean the answer is correct: an answer
faithful to the wrong version's page scores perfectly. That is why version accuracy is measured
alongside it.

## Example C. Decline rate and the threshold (week 3)

Your test set has 100 questions: 20 with no answer in the documents and 80 that can be answered.
The relevance threshold decides how good the best retrieved piece must be before the system
answers. Three settings:

| Threshold | Correct declines, of 20 unanswerable | Wrong declines, of 80 answerable | Invented answers |
| --- | --- | --- | --- |
| 0.3 | 9 | 1 | 11 |
| 0.5 | 15 | 4 | 5 |
| 0.7 | 19 | 13 | 1 |

**For the user:** a low threshold invents answers to questions the manual cannot answer; a high one
turns away people it could have helped. You choose the trade-off and say why in the decision
record: for a support desk where a wrong answer reaches a customer, an invented answer usually
costs more than a hand-over to a person. A higher decline rate on its own is not progress; read it
only together with the wrong declines.

## Example D. Trusting your judge (week 3)

You label 30 answers yourself as faithful or not, then run your judge on the same 30. It agrees on
26: agreement 0.87. **What it tells you:** the judge's faithfulness scores are worth reporting.
**What it does not:** if 25 of your 30 were easy cases, the judge may still fail on the hard ones.
Read the 4 disagreements, not just the total: they show whether your labels or its prompt need
changing.

## Example E. Your score against the hidden score (week 3 onward)

Your own test set scores 0.86. The hidden set, on the same pull request, scores 0.71. The gap is
the finding. It usually means your questions were written from the documents, in the documents'
own words, so your system passes them easily. Real users ask half-specified questions. The fix is
not to chase the hidden questions: rewrite your own set from what a user would ask, and watch
whether the gap narrows. Session 3 opens with you explaining this gap.
