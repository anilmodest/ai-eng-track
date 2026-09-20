"""Retrieval metrics. Measured separately from generation: a wrong answer usually starts here.

Each query has a list of relevance flags in rank order (True = the hit at that rank was relevant)
and the total number of relevant chunks that exist for it in the corpus.
"""

from dataclasses import dataclass


def precision_at_k(relevant: list[bool], k: int) -> float:
    """Of the first k hits, what fraction were relevant?"""
    top = relevant[:k]
    return sum(top) / len(top) if top else 0.0


def recall_at_k(relevant: list[bool], total_relevant: int, k: int) -> float:
    """Of everything relevant in the corpus, what fraction did the first k hits find?"""
    if total_relevant <= 0:
        return 0.0
    return min(1.0, sum(relevant[:k]) / total_relevant)


def reciprocal_rank(relevant: list[bool]) -> float:
    """1 / rank of the first relevant hit; 0 if none."""
    for i, flag in enumerate(relevant, start=1):
        if flag:
            return float(i)
    return 0.0


@dataclass(frozen=True)
class RetrievalScores:
    queries: int
    k: int
    precision_at_k: float
    recall_at_k: float
    mrr: float
    hit_rate: float  # fraction of queries with at least one relevant hit in the top k


def evaluate(per_query: list[tuple[list[bool], int]], k: int) -> RetrievalScores:
    """Average the per-query metrics.

    `per_query` = [(relevance flags in rank order, total_relevant)].
    """
    n = len(per_query)
    if n == 0:
        return RetrievalScores(0, k, 0.0, 0.0, 0.0, 0.0)
    p = sum(precision_at_k(f, k) for f, _ in per_query) / n
    r = sum(recall_at_k(f, t, k) for f, t in per_query) / n
    m = sum(reciprocal_rank(f[:k]) for f, _ in per_query) / n
    h = sum(sum(f[:k]) for f, _ in per_query) / n
    return RetrievalScores(n, k, round(p, 4), round(r, 4), round(m, 4), round(h, 4))
