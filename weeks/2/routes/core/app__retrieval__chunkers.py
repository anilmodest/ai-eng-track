"""Four ways to cut a document into pieces. Which one is right is a measurement, not an opinion.

Every strategy returns a list of strings. Chunks should be small enough that a retrieved chunk is
mostly about one thing, and whole enough that a table row or a sentence is not cut in half.
"""

import re
from collections.abc import Callable

_SENTENCE_END = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9\"'(\[|#*-])")


def fixed(text: str, size: int = 500, overlap: int = 50) -> list[str]:
    """Cut every `size` characters with `overlap`. Fast, simple; cuts sentences and tables."""
    text = text.strip()
    if not text:
        return []
    step = max(1, size - overlap)
    return [
        text[i : i + size].strip() for i in range(0, len(text), step) if text[i : i + size].strip()
    ]


def by_sentence(text: str, target: int = 400) -> list[str]:
    """Accumulate whole sentences until about `target` characters. Never cuts mid-sentence."""
    sentences = [s.strip() for s in _SENTENCE_END.split(text.strip()) if s.strip()]
    chunks: list[str] = []
    current = ""
    for s in sentences:
        if current and len(current) + 1 + len(s) > target:
            chunks.append(current)
            current = s
        else:
            current = f"{current} {s}".strip()
    if current:
        chunks.append(current)
    return chunks


def by_paragraph(text: str, max_chars: int = 800) -> list[str]:
    """Split on blank lines; merge small paragraphs; split a huge one by sentence."""
    paras = [p.strip() for p in re.split(r"\n\s*\n", text.strip()) if p.strip()]
    chunks: list[str] = []
    current = ""
    for p in paras:
        if len(p) > max_chars:
            if current:
                chunks.append(current)
                current = ""
            chunks.extend(by_sentence(p, target=max_chars))
            continue
        if current and len(current) + 2 + len(p) > max_chars:
            chunks.append(current)
            current = p
        else:
            current = f"{current}\n\n{p}".strip()
    if current:
        chunks.append(current)
    return chunks


def by_heading(text: str, max_chars: int = 1200) -> list[str]:
    """One chunk per markdown section, heading kept with its body; oversized sections fall back
    to paragraphs, each still prefixed with the heading so it keeps its context.

    A document with no headings behaves like by_paragraph.
    """
    lines = text.strip().splitlines()
    sections: list[tuple[str, list[str]]] = []
    heading = ""
    body: list[str] = []
    for line in lines:
        if re.match(r"^#{1,6}\s+\S", line):
            if heading or body:
                sections.append((heading, body))
            heading, body = line.strip(), []
        else:
            body.append(line)
    if heading or body:
        sections.append((heading, body))

    chunks: list[str] = []
    for heading, body in sections:
        section_text = "\n".join(body).strip()
        if not section_text and not heading:
            continue
        if not section_text:
            chunks.append(heading)
            continue
        whole = section_text
        if len(whole) <= max_chars:
            chunks.append(whole)
        else:
            for part in by_paragraph(section_text, max_chars=max_chars - len(heading) - 1):
                chunks.append(f"{heading}\n{part}".strip() if heading else part)
    return chunks


STRATEGIES: dict[str, Callable[[str], list[str]]] = {
    "fixed": fixed,
    "sentence": by_sentence,
    "paragraph": by_paragraph,
    "heading": by_heading,
}


def chunk(text: str, strategy: str) -> list[str]:
    try:
        fn = STRATEGIES[strategy]
    except KeyError as e:
        raise ValueError(f"unknown chunk strategy {strategy!r}; known: {sorted(STRATEGIES)}") from e
    return fn(text)
