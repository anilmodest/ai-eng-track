"""Week 2 gate: context is an attention budget, and retrieval is measured, not argued about.

Runs with the lexical `hash` embedder: no model download, deterministic, and it knows nothing
about meaning, which is exactly why the tests only ask it to find words it was given.
"""

from pathlib import Path

import pytest
from httpx import AsyncClient

from app.retrieval.chunkers import by_heading, by_paragraph, by_sentence, chunk, fixed
from app.retrieval.context import select_and_compress
from app.retrieval.metrics import evaluate, precision_at_k, recall_at_k, reciprocal_rank
from app.retrieval.store import Hit
from app.retrieval.versions import version_of
from tests.conftest import upload

pytestmark = pytest.mark.week2

CORPUS = Path(__file__).parent.parent.parent / "corpus"


# ---- chunkers ------------------------------------------------------------------------------


def test_fixed_cuts_sentences_in_half() -> None:
    text = "The quick brown fox jumps over the lazy dog. " * 40
    pieces = fixed(text, size=100, overlap=10)
    assert len(pieces) > 5
    assert any(not p.rstrip().endswith(".") for p in pieces)


def test_sentence_chunker_never_cuts_mid_sentence() -> None:
    text = (CORPUS / "contract-fabrikam-tailspin.txt").read_text(encoding="utf-8")
    pieces = by_sentence(text, target=300)
    assert len(pieces) >= 4
    for p in pieces[:-1]:  # the last chunk ends wherever the document ends
        assert p.rstrip()[-1] in ".!?:", p[-60:]
    # Honest weakness, on purpose: a numbered clause heading is split from its body.
    assert any(p.rstrip().endswith("Fees.") for p in pieces)


def test_paragraph_chunker_keeps_a_table_row_whole() -> None:
    text = (CORPUS / "invoice-northwind-0042.md").read_text(encoding="utf-8")
    pieces = by_paragraph(text, max_chars=400)
    row = "| Data pipeline consulting, August 2026 | 24 h | 175.00 USD | 4,200.00 USD |"
    assert any(row in p for p in pieces)


def test_heading_chunker_keeps_heading_with_its_body() -> None:
    text = (CORPUS / "policy-contoso-expenses.md").read_text(encoding="utf-8")
    pieces = by_heading(text)
    mileage = next(p for p in pieces if "45 pence per mile" in p)
    assert mileage.startswith("## Mileage")
    assert "Hotel nightly caps" not in mileage


def test_unknown_strategy_is_refused() -> None:
    with pytest.raises(ValueError):
        chunk("x", "magic")


# ---- metrics -------------------------------------------------------------------------------


def test_precision_recall_mrr_on_a_toy_example() -> None:
    flags = [False, True, False, True, False]
    assert precision_at_k(flags, 5) == pytest.approx(0.4)
    assert recall_at_k(flags, total_relevant=4, k=5) == pytest.approx(0.5)
    assert reciprocal_rank(flags) == pytest.approx(0.5)
    assert reciprocal_rank([False, False]) == 0.0


def test_evaluate_averages_per_query() -> None:
    # Query 1 has two relevant hits in the top 2: hit rate counts the query once, not twice.
    scores = evaluate([([True, True], 2), ([False, False], 2)], k=2)
    assert scores.queries == 2
    assert scores.precision_at_k == pytest.approx(0.5)
    assert scores.recall_at_k == pytest.approx(0.5)
    assert scores.mrr == pytest.approx(0.5)
    assert scores.hit_rate == pytest.approx(0.5)


def test_precision_uses_k_not_the_number_of_hits() -> None:
    # Three hits returned for k=5, one relevant: precision@5 is 1/5, not 1/3.
    assert precision_at_k([False, True, False], 5) == pytest.approx(0.2)


# ---- index and search through the API ------------------------------------------------------


async def _load_corpus(api: AsyncClient) -> None:
    for path in sorted(CORPUS.iterdir()):
        r = await api.post("/documents", files={"file": (path.name, path.read_bytes())})
        assert r.status_code == 201, r.text


async def test_index_then_search_finds_the_right_document(api: AsyncClient) -> None:
    await _load_corpus(api)
    r = await api.post("/index", params={"strategy": "paragraph"})
    assert r.status_code == 200 and r.json()["chunks"] > 10
    r = await api.get(
        "/search", params={"q": "mileage rate personal car pence", "k": 3, "strategy": "paragraph"}
    )
    hits = r.json()
    assert hits[0]["filename"] == "policy-contoso-expenses.md"
    assert "45 pence" in hits[0]["text"]
    assert hits[0]["score"] >= hits[1]["score"] >= hits[2]["score"]


async def test_reindex_replaces_rather_than_duplicates(api: AsyncClient) -> None:
    await upload(api, "invoice.md")
    first = (await api.post("/index", params={"strategy": "sentence"})).json()["chunks"]
    second = (await api.post("/index", params={"strategy": "sentence"})).json()["chunks"]
    assert first == second > 0


async def test_search_respects_k_and_strategy(api: AsyncClient) -> None:
    await _load_corpus(api)
    await api.post("/index", params={"strategy": "fixed"})
    r = await api.get("/search", params={"q": "toner cartridge", "k": 2, "strategy": "fixed"})
    assert len(r.json()) == 2
    r = await api.get("/search", params={"q": "toner cartridge", "k": 2, "strategy": "heading"})
    assert r.json() == []  # nothing indexed under that strategy yet: no silent fallback


async def test_unknown_strategy_on_index_is_400(api: AsyncClient) -> None:
    r = await api.post("/index", params={"strategy": "magic"})
    assert r.status_code == 400


# ---- the version filter: output requirement O1 ---------------------------------------------
#
# The manual exists twice over, worded almost identically. Similarity alone cannot tell the two
# apart, so these tests are the contract: a question asked about one version may not be answered
# out of another version's page.


def test_the_version_is_read_from_the_filename() -> None:
    assert version_of("manual-v3-connection-timeout.md") == "v3"
    assert version_of("manual-v2-retries.md") == "v2"
    assert version_of("policy-contoso-expenses.md") is None
    assert version_of("manual-v9-nothing.md") is None  # not a version we know about


async def test_similarity_alone_returns_the_wrong_version(api: AsyncClient) -> None:
    """The control. Without the filter the version 2 page wins, and the answer reads perfectly."""
    await _load_corpus(api)
    await api.post("/index", params={"strategy": "heading"})
    hits = (
        await api.get(
            "/search",
            params={"q": "what is the default connection timeout", "k": 3, "strategy": "heading"},
        )
    ).json()
    assert hits[0]["filename"] == "manual-v2-connection-timeout.md"
    assert hits[0]["score"] > hits[1]["score"]
    assert hits[1]["filename"] == "manual-v3-connection-timeout.md"


async def test_a_version_3_question_returns_no_version_2_material(api: AsyncClient) -> None:
    """O1. The requirement the whole retrieval week exists to meet."""
    await _load_corpus(api)
    await api.post("/index", params={"strategy": "heading"})
    for question in (
        "what is the default connection timeout",
        "where is the connection timeout set",
        "how long are logs kept",
        "how do I authenticate to the API",
        "how are schedules written",
    ):
        hits = (
            await api.get(
                "/search",
                params={"q": question, "k": 5, "strategy": "heading", "version": "v3"},
            )
        ).json()
        assert hits, question
        assert not [h for h in hits if h["version"] == "v2"], (question, hits)
        assert not [h for h in hits if "-v2-" in h["filename"]], (question, hits)


async def test_the_filter_runs_before_ranking_not_after(api: AsyncClient) -> None:
    """Filtering afterwards would leave fewer than k hits. Losing recall quietly is still losing."""
    await _load_corpus(api)
    await api.post("/index", params={"strategy": "heading"})
    params: dict[str, str | int] = {"q": "connection timeout", "k": 5, "strategy": "heading"}
    unfiltered = (await api.get("/search", params=params)).json()
    filtered = (await api.get("/search", params={**params, "version": "v3"})).json()
    assert len(filtered) == len(unfiltered) == 5


async def test_pages_with_no_version_are_returned_for_every_version(api: AsyncClient) -> None:
    """A page that applies to all versions must not be filtered out by a version search."""
    await _load_corpus(api)
    await api.post("/index", params={"strategy": "paragraph"})
    hits = (
        await api.get(
            "/search",
            params={
                "q": "mileage rate personal car pence",
                "k": 3,
                "strategy": "paragraph",
                "version": "v3",
            },
        )
    ).json()
    assert hits[0]["filename"] == "policy-contoso-expenses.md"
    assert hits[0]["version"] is None


# ---- context engineering: select and compress ----------------------------------------------


def _hit(i: int, text: str, score: float) -> Hit:
    return Hit(chunk_id=i, document_id=i, filename=f"doc{i}.md", ordinal=0, text=text, score=score)


MILEAGE = (
    "## Mileage\nPersonal car: 45 pence per mile for the first 10,000 miles in the tax year, "
    "then 25 pence. Electric cars: the same rate. Parking and tolls at cost."
)
HOTELS = "Hotel nightly caps: London 180 GBP, other UK cities 130 GBP. Breakfast is claimable."
FLEET = "The fleet grew from 412 to 438 vehicles in the half. Electric vehicles rose from 31 to 57."


def test_select_and_compress_keeps_the_passage_that_answers() -> None:
    hits = [_hit(1, MILEAGE, 0.62), _hit(2, HOTELS, 0.31), _hit(3, FLEET, 0.12)]
    out = select_and_compress("What is the mileage rate for a personal car?", hits, 1200)
    assert out and "45 pence per mile" in out[0]


def test_select_and_compress_drops_unrelated_passages() -> None:
    hits = [_hit(1, MILEAGE, 0.62), _hit(2, HOTELS, 0.31), _hit(3, FLEET, 0.12)]
    out = select_and_compress("What is the mileage rate for a personal car?", hits, 5000)
    assert not any("fleet grew" in p for p in out), "a passage far below the best score was kept"


def test_select_and_compress_respects_the_budget() -> None:
    hits = [_hit(i, MILEAGE + " " + HOTELS, 0.5) for i in range(1, 9)]
    out = select_and_compress("What is the mileage rate for a personal car?", hits, 300)
    assert sum(len(p) for p in out) <= 300


def test_select_and_compress_trims_inside_a_passage() -> None:
    hits = [_hit(1, MILEAGE, 0.6)]
    out = select_and_compress("What is the mileage rate for a personal car?", hits, 1200)
    assert "45 pence per mile" in out[0]
    assert "Parking and tolls" not in out[0], "a sentence sharing no term with the question stayed"
