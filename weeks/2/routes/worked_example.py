"""Week 2 worked example (start route): a sibling metric and a sibling chunker, in full.

    uv run python weeks/2/routes/worked_example.py

average_precision is a cousin of precision@k and reciprocal rank: same inputs, same shape.
by_lines is a cousin of by_heading: same signature as every chunker in chunkers.py.
"""

from pathlib import Path


def average_precision(relevant: list[bool], k: int) -> float:
    """Mean of precision@i at every relevant rank i <= k. 0 if nothing relevant."""
    hits = 0
    total = 0.0
    for i, flag in enumerate(relevant[:k], start=1):
        if flag:
            hits += 1
            total += hits / i
    return total / hits if hits else 0.0


def by_lines(text: str, min_chars: int = 200) -> list[str]:
    """One chunk per line, merging short lines forward until each chunk has min_chars."""
    chunks: list[str] = []
    current = ""
    for line in text.splitlines():
        if not line.strip():
            continue
        current = f"{current}\n{line}".strip() if current else line.strip()
        if len(current) >= min_chars:
            chunks.append(current)
            current = ""
    if current:
        chunks.append(current)
    return chunks


if __name__ == "__main__":
    flags = [False, True, True, False, True]
    print("average precision @5:", round(average_precision(flags, 5), 3))
    print("  (precision at ranks 2, 3, 5 = 1/2, 2/3, 3/5; their mean = 0.589)")
    text = (
        Path(__file__).resolve().parents[3] / "corpus" / "policy-contoso-expenses.md"
    ).read_text(encoding="utf-8")
    for i, c in enumerate(by_lines(text, 200)):
        print(f"[{i}] {len(c):>4} chars  {c[:60]!r}")
    print("Now: precision_at_k, recall_at_k, reciprocal_rank, evaluate, and by_heading.")
