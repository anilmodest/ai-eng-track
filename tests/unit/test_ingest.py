import pytest

from app.ingest import UnsupportedType, parse


def test_markdown_passes_through() -> None:
    assert parse("a.md", b"# Title\n\nbody") == "# Title\n\nbody"


def test_csv_becomes_labelled_rows() -> None:
    out = parse("a.csv", b"name,amount\nAlice,10\nBob,20\n")
    assert out.splitlines() == [
        "name | amount",
        "name: Alice | amount: 10",
        "name: Bob | amount: 20",
    ]


def test_unknown_suffix_is_refused() -> None:
    with pytest.raises(UnsupportedType):
        parse("a.docx", b"...")
