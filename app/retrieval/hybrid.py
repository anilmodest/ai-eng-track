"""Week 2: hybrid search. Keyword search (BM25) and meaning search, fused into one ranking.

The exercise is in weeks/2/README.md. Two functions are yours; the store calls them.

Why both. Meaning search (embeddings) finds "how long does it wait for the source" when the page
says "connection timeout". It is weak exactly where a support desk is strong: product codes, error
numbers and setting names, `E1104`, `KESTREL_CONNECT_TIMEOUT`, which carry little meaning and must
match exactly. Keyword search is the opposite. Each misses what the other finds.

    bm25_scores                 one score per document for the query: rare query terms count
                                for more (IDF), repeats of a term count for less each time (k1),
                                and a long document does not win just by being long (b)
    reciprocal_rank_fusion      merge several rankings by rank, not by score: a dense cosine of
                                0.62 and a BM25 score of 7.3 are not on the same scale, but
                                "first" and "fifth" are

The version filter is applied before either ranking (app/retrieval/store.py), so neither side can
bring a version 2 chunk back for a version 3 question.
"""

import re

_TOKEN = re.compile(r"[a-z0-9_]+")


def tokenize(text: str) -> list[str]:
    """Lower-case words, keeping codes whole: `E1104` -> `e1104`, `KESTREL_CONNECT_TIMEOUT` stays
    one token. Given; use it for both the query and the documents."""
    return _TOKEN.findall(text.lower())


def bm25_scores(
    query: str, documents: list[str], *, k1: float = 1.5, b: float = 0.75
) -> list[float]:
    """One BM25 score per document, in the same order. A document sharing no query term scores 0.

    For each query term t, over documents of average length avgdl:
        idf(t)  = ln(1 + (N - n(t) + 0.5) / (n(t) + 0.5))       n(t): documents containing t
        part    = idf(t) * tf * (k1 + 1) / (tf + k1 * (1 - b + b * len(doc) / avgdl))
    and a document's score is the sum of its parts.
    """
    raise NotImplementedError("Week 2: bm25_scores (weeks/2/README.md)")


def reciprocal_rank_fusion(rankings: list[list[int]], *, k: int = 60) -> list[tuple[int, float]]:
    """Merge rankings of ids (best first) into one: (id, score), best first.

    An id's score is the sum, over every ranking it appears in, of 1 / (k + rank), rank from 1. An
    id missing from a ranking gets nothing from it. Ties keep the order the ids were first seen.
    """
    raise NotImplementedError("Week 2: reciprocal_rank_fusion (weeks/2/README.md)")
