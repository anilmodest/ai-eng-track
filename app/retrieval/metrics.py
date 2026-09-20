"""Retrieval metrics. Measured separately from generation: a wrong answer usually starts here.

Each query has a list of relevance flags in rank order (True = the hit at that rank was relevant)
and the total number of relevant chunks that exist for it in the corpus.
"""

from dataclasses import dataclass


def precision_at_k(relevant: list[bool], k: int) -> float:
    """Of the first k hits, what fraction were relevant?"""
    raise NotImplementedError("Week 2: build me (weeks/2/README.md)")


def recall_at_k(relevant: list[bool], total_relevant: int, k: int) -> float:
    """Of everything relevant in the corpus, what fraction did the first k hits find?"""
    raise NotImplementedError("Week 2: build me (weeks/2/README.md)")


def reciprocal_rank(relevant: list[bool]) -> float:
    """1 / rank of the first relevant hit; 0 if none."""
    raise NotImplementedError("Week 2: build me (weeks/2/README.md)")


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
    raise NotImplementedError("Week 2: build me (weeks/2/README.md)")
