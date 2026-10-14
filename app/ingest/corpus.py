"""The corpus on disk: every document under corpus/, including corpus/generated/.

corpus/ holds the hand-written pages every exercise and test refers to by name. A programme
variant adds corpus/generated/: hundreds more pages of the same product, so the corpus is too big
to send to a model whole, which is what makes retrieval necessary rather than tidy.
"""

from pathlib import Path

CORPUS = Path(__file__).resolve().parent.parent.parent / "corpus"
SUFFIXES = {".md", ".txt", ".csv", ".pdf"}


def corpus_paths(*, generated: bool = True) -> list[Path]:
    """Every corpus file, sorted, hand-written first. `generated=False` for the small core set."""
    top = sorted(p for p in CORPUS.iterdir() if p.is_file() and p.suffix in SUFFIXES)
    if not generated:
        return top
    more = sorted(
        p for p in CORPUS.rglob("*") if p.is_file() and p.suffix in SUFFIXES and p.parent != CORPUS
    )
    return top + more
