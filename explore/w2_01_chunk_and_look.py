"""Week 2, elaboration 1: cut one document four ways and look at where the cuts fall.

    uv run python explore/w2_01_chunk_and_look.py [corpus/file]

No model, no key. Read the output slowly. Find a table row cut in half. Find a clause number
separated from its clause. Then decide which of those matter for the questions people will ask.
"""

import sys
from pathlib import Path

from app.retrieval.chunkers import STRATEGIES

ROOT = Path(__file__).resolve().parent.parent
DEFAULT = ROOT / "corpus" / "contract-fabrikam-tailspin.txt"


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
    print("Which strategy cut a table row? Which separated '3. Fees.' from the fee? Which kept the")
    print("heading with its body? Now run scripts/retrieval_eval.py and see if it matters.")


if __name__ == "__main__":
    main()
