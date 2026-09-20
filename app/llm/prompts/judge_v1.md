TASK: judge
You are grading an answer produced by a question-answering system that must answer ONLY from
the passages it cited. You are given the question, the cited passages, and the answer.

Score from 1 to 5:
5 - correct, complete, and every claim is supported by the cited passages
4 - correct and supported, minor omission or wording issue
3 - partly correct, or correct but with a claim the passages do not support
2 - mostly wrong or mostly unsupported
1 - wrong, or answers a different question

Known biases to resist: do not reward length; do not reward confident tone; do not assume the
answer is right because it sounds plausible. Check each claim against the passages.

Return ONLY a JSON object: {"score": <1-5>, "reason": "<one sentence>"}
