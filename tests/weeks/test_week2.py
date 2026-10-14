"""Week 2 gate: context is an attention budget, and retrieval is measured, not argued about.

Runs with the lexical `hash` embedder: no model download, deterministic, and it knows nothing
about meaning, which is exactly why the tests only ask it to find words it was given.
"""

import json
import os
import subprocess
import sys
from collections.abc import Iterator
from pathlib import Path

import pytest
from httpx import AsyncClient
from sqlmodel import Session

from app.db.session import get_engine
from app.retrieval.chunkers import by_heading, by_paragraph, by_sentence, chunk, fixed
from app.retrieval.context import select_and_compress
from app.retrieval.hybrid import bm25_scores, reciprocal_rank_fusion
from app.retrieval.metrics import evaluate, precision_at_k, recall_at_k, reciprocal_rank
from app.retrieval.store import Hit
from app.retrieval.versions import version_of
from app.settings import get_settings
from app.tools import TOOLS, ToolContext, call
from app.tools.base import schema
from tests.conftest import upload

pytestmark = pytest.mark.week2

ROOT = Path(__file__).parent.parent.parent
CORPUS = ROOT / "corpus"


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
    # The hand-written pages only: the tests name them, and a generated corpus would only make
    # every test slower. The measurement scripts load the whole corpus.
    for path in sorted(p for p in CORPUS.iterdir() if p.is_file()):
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
    # Which of the two wins depends on the chunker. That it is a coin toss is the whole problem:
    # the version 2 page is returned for a version 3 question, and reads perfectly.
    assert [h for h in hits if h["version"] == "v2"], hits
    assert [h for h in hits if h["version"] == "v3"], hits


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


# ---- hybrid search: app/retrieval/hybrid.py --------------------------------------------------


def test_bm25_scores_only_documents_that_share_a_query_term() -> None:
    docs = [
        "set KESTREL_CONNECT_TIMEOUT to 15 seconds",
        "the timeout is fifteen seconds by default",
        "retries back off exponentially",
    ]
    scores = bm25_scores("KESTREL_CONNECT_TIMEOUT", docs)
    assert len(scores) == 3
    assert scores[0] > 0 and scores[1] == 0 and scores[2] == 0
    assert bm25_scores("nothing matches this", docs) == [0.0, 0.0, 0.0]


def test_bm25_rare_terms_count_for_more() -> None:
    """`timeout` is on every page; `e1104` on one. The page with the rare term must win."""
    docs = ["timeout E1104 out of range", "timeout default", "timeout and retries", "timeout"]
    scores = bm25_scores("timeout e1104", docs)
    assert scores[0] == max(scores) and scores[0] > scores[1]


def test_bm25_a_long_document_does_not_win_by_being_long() -> None:
    short = "connection timeout default fifteen seconds"
    long = short + " " + " ".join(f"filler{i}" for i in range(200))
    scores = bm25_scores("connection timeout", [short, long])
    assert scores[0] > scores[1] > 0


def test_bm25_repeats_count_for_less_each_time() -> None:
    once, four = "timeout setting", "timeout timeout timeout timeout setting"
    scores = bm25_scores("timeout", [once, four, "retries"])
    assert scores[1] > scores[0]
    assert scores[1] < 4 * scores[0]


def test_reciprocal_rank_fusion_merges_by_rank_not_score() -> None:
    fused = reciprocal_rank_fusion([[1, 2, 3], [3, 1, 4]], k=60)
    assert [i for i, _ in fused] == [1, 3, 2, 4]
    assert fused[0][1] == pytest.approx(1 / 61 + 1 / 62)
    assert fused[-1][1] == pytest.approx(1 / 63)
    assert reciprocal_rank_fusion([]) == []


async def test_hybrid_search_keeps_the_version_filter_and_k(api: AsyncClient) -> None:
    await _load_corpus(api)
    await api.post("/index", params={"strategy": "section"})
    params: dict[str, str | int] = {
        "k": 5,
        "strategy": "section",
        "version": "v3",
        "mode": "hybrid",
    }
    for q in ("connection_timeout_seconds", "where is the connection timeout set", "E1104"):
        hits = (await api.get("/search", params={**params, "q": q})).json()
        assert len(hits) == 5, q
        assert not [h for h in hits if h["version"] == "v2"], (q, hits)
        assert len({h["chunk_id"] for h in hits}) == 5, "no chunk twice"


async def test_hybrid_search_finds_an_exact_setting_name(api: AsyncClient) -> None:
    await _load_corpus(api)
    await api.post("/index", params={"strategy": "section"})
    hits = (
        await api.get(
            "/search",
            params={"q": "KESTREL_RETRY_POLICY", "k": 3, "strategy": "section", "mode": "hybrid"},
        )
    ).json()
    assert "KESTREL_RETRY_POLICY" in hits[0]["text"]


async def test_unknown_search_mode_is_400(api: AsyncClient) -> None:
    r = await api.get("/search", params={"q": "timeout", "mode": "magic"})
    assert r.status_code == 400


def test_section_chunker_says_where_each_chunk_sits() -> None:
    text = (CORPUS / "manual-v3-connection-timeout.md").read_text(encoding="utf-8")
    chunks = chunk(text, "section")
    assert chunks and all(c.startswith("Connection timeout (Kestrel v3)") for c in chunks)
    assert any("> Limits" in c for c in chunks)
    assert not any(c.startswith("---") or "product: Kestrel" in c for c in chunks)


# ---- search_docs: the agent's second tool (app/tools/search.py) ------------------------------


def test_search_docs_is_described_and_needs_a_version() -> None:
    s = schema(TOOLS["search_docs"])
    assert "TODO" not in s["description"] and len(s["description"].split()) >= 12
    props = s["parameters"]["properties"]
    assert set(props) == {"query", "version", "k"}
    for name, prop in props.items():
        assert len(str(prop.get("description", "")).split()) >= 4, f"describe {name}"
    assert "version" in s["parameters"].get("required", []), "no version is the version trap"


@pytest.fixture
def search_ctx(env: None, monkeypatch: pytest.MonkeyPatch) -> Iterator[ToolContext]:
    monkeypatch.setenv("CHUNK_STRATEGY", "section")
    get_settings.cache_clear()
    with Session(get_engine()) as session:
        yield ToolContext(session=session, settings=get_settings())


async def test_search_docs_refuses_malformed_calls_before_searching(
    search_ctx: ToolContext,
) -> None:
    for args in (
        {"query": "timeout", "version": "v4"},
        {"query": "timeout"},
        {"query": "", "version": "v3"},
        {"query": "timeout", "version": "v3", "k": 500},
        {"query": "timeout", "version": "v3", "k": 0},
    ):
        out = await call(search_ctx, "search_docs", args)
        assert out.startswith("error:"), (args, out)
    assert search_ctx.calls == []


async def test_search_docs_returns_only_that_versions_pages_with_what_a_citation_needs(
    api: AsyncClient, search_ctx: ToolContext
) -> None:
    await _load_corpus(api)
    await api.post("/index", params={"strategy": "section"})
    out = await call(
        search_ctx, "search_docs", {"query": "default connection timeout", "version": "v3", "k": 3}
    )
    assert "manual-v3-connection-timeout.md" in out
    assert "manual-v2-" not in out
    assert "KESTREL_CONNECT_TIMEOUT" in out or "15 seconds" in out
    nothing = await call(
        search_ctx, "search_docs", {"query": "zebra crossing", "version": "v2", "k": 3}
    )
    assert not nothing.startswith("error"), nothing


# ---- the context experiment ------------------------------------------------------------------


def test_context_experiment_runs_and_the_wrong_version_costs_accuracy() -> None:
    env = {**os.environ, "MODEL_PROVIDER": os.environ.get("MODEL_PROVIDER") or "fake_a"}
    r = subprocess.run(
        [sys.executable, "scripts/context_experiment.py", "--limit", "6"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert r.returncode == 0, r.stdout + r.stderr
    report = json.loads((ROOT / "reports" / "context.json").read_text())
    settings = report["settings"]
    assert set(settings) == {"none", "wrong_version", "right_version", "too_much", "buried"}
    assert settings["right_version"]["accuracy"] > settings["wrong_version"]["accuracy"]
    assert settings["none"]["decline_rate"] == 1.0
    assert (
        settings["buried"]["tokens_in_per_question"]
        > settings["right_version"]["tokens_in_per_question"]
    )
