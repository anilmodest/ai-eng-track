"""The hub's hidden-evaluation card: totals only, from week 2, honest when there is nothing yet."""

from scripts.build_pages import Week, hidden_card, hidden_totals


def test_totals_are_read_from_the_check_summary() -> None:
    assert hidden_totals("answer_accuracy=0.71 attacks_resisted=9/10 n=150") == [
        ("answer accuracy", "0.71"),
        ("attacks resisted", "9/10"),
        ("n", "150"),
    ]


def test_no_card_before_week_two_and_a_plain_note_until_it_has_run() -> None:
    assert hidden_card(Week(n=1, title="x")) == ""
    assert "Not run on this week yet" in hidden_card(Week(n=3, title="x"))


def test_the_card_shows_the_verdict_and_the_totals_and_never_more() -> None:
    w = Week(n=3, title="x")
    w.hidden = {"sha": "abcdef123", "conclusion": "failure", "summary": "answer_accuracy=0.7 n=9"}
    card = hidden_card(w)
    assert "pill red" in card and "abcdef1" in card
    assert "answer accuracy" in card and "0.7" in card
