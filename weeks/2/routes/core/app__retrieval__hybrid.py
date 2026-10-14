"""Week 2: hybrid search. Keyword search (BM25) and meaning search, fused into one ranking.

Both functions are written. Read them as a reviewer before you run anything: do they compute
what the docstrings say?
"""

import math
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
    terms = set(tokenize(query))
    docs = [tokenize(d) for d in documents]
    n = len(docs)
    if not n or not terms:
        return [0.0] * n
    avgdl = sum(len(d) for d in docs) / n or 1.0
    df = {t: sum(1 for d in docs if t in d) for t in terms}
    idf = {t: math.log((n - df[t] + 0.5) / (df[t] + 0.5)) for t in terms}
    scores = []
    for d in docs:
        counts: dict[str, int] = {}
        for tok in d:
            if tok in terms:
                counts[tok] = counts.get(tok, 0) + 1
        norm = k1 * (1 - b + b * len(d) / avgdl)
        scores.append(sum(idf[t] * tf * (k1 + 1) / (tf + norm) for t, tf in counts.items()))
    return scores


def reciprocal_rank_fusion(rankings: list[list[int]], *, k: int = 60) -> list[tuple[int, float]]:
    """Merge rankings of ids (best first) into one: (id, score), best first.

    An id's score is the sum, over every ranking it appears in, of 1 / (k + rank), rank from 1. An
    id missing from a ranking gets nothing from it. Ties keep the order the ids were first seen.
    """
    scores: dict[int, float] = {}
    for ranking in rankings:
        for rank, item in enumerate(ranking):
            scores[item] = scores.get(item, 0.0) + 1.0 / (k + rank)
    return sorted(scores.items(), key=lambda kv: -kv[1])
