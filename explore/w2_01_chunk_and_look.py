"""Week 2, elaboration 1: cut one manual page every way and look at where the cuts fall.

    uv run python explore/w2_01_chunk_and_look.py [corpus/file]

No model, no key. Read the output slowly. Find a row of the settings table cut in half. Find a
heading separated from the section it names. Then decide which of those matter for the questions
the desk is asked.
"""

import sys
from pathlib import Path

from app.retrieval.chunkers import STRATEGIES

ROOT = Path(__file__).resolve().parent.parent
DEFAULT = ROOT / "corpus" / "generated" / "howto-v3-configuration.md"


def main() -> None:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT
    text = path.read_text(encoding="utf-8")
    print(f"{path.name}: {len(text)} characters\n")
    for name, fn in STRATEGIES.items():
        pieces = fn(text)
        sizes = [len(p) for p in pieces]
        print(f"=== {name}: {len(pieces)} chunks, {min(sizes)}-{max(sizes)} chars")
        for i, p in enumerate(pieces):
            head = p.replace("\n", " ")[:70]
            tail = p.replace("\n", " ")[-40:]
            print(f"  [{i}] {head!r} ... {tail!r}")
        print()
    print("Which strategy cut a row of the settings table? Which left '## Import file size limit'")
    print("at the end of one chunk and its body in the next? Which kept each heading with its")
    print("body? Now run scripts/retrieval_eval.py and see if it matters.")


if __name__ == "__main__":
    main()
