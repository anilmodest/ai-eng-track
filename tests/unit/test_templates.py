"""The route templates: each holds its own route and nothing of the other two.

Source-only: this file is never shipped in a template (scripts/templates.py SOURCE_ONLY).
"""

import json
from pathlib import Path

import pytest

from scripts.templates import MARK, ROOT, ROUTES, SOURCE_ONLY, build, strip_marked


@pytest.fixture(scope="module")
def templates(tmp_path_factory: pytest.TempPathFactory) -> dict[str, Path]:
    out = tmp_path_factory.mktemp("templates")
    return {route: _built(out, route) for route in ROUTES}


def _built(out: Path, route: str) -> Path:
    build(ROOT, route, out / route)
    return out / route


def test_each_template_holds_only_its_own_route_pages(templates: dict[str, Path]) -> None:
    for route, tree in templates.items():
        pages = sorted(p.name for p in tree.glob("weeks/*/routes/*"))
        assert pages, route
        allowed = {f"{route}.md"} | ({"worked_example.py"} if route == "start" else set())
        assert set(pages) <= allowed, (route, set(pages) - allowed)
        assert not list(tree.glob("weeks/*/routes/core")), route


def test_core_gets_the_planted_faults_and_the_others_the_stubs(
    templates: dict[str, Path],
) -> None:
    for faulty in ROOT.glob("weeks/*/routes/core/*"):
        rel = faulty.name.replace("__", "/")
        planted = faulty.read_bytes().replace(b"\r\n", b"\n")
        assert (templates["core"] / rel).read_bytes() == planted, rel
        assert (templates["start"] / rel).read_bytes() != planted, rel


def test_pro_helpers_are_signatures_only(templates: dict[str, Path]) -> None:
    for rel in ("app/llm/retry.py", "app/llm/structured.py", "app/llm/cost.py", "app/trace.py"):
        assert MARK in (templates["pro"] / rel).read_text(encoding="utf-8"), rel
        assert MARK not in (templates["start"] / rel).read_text(encoding="utf-8"), rel
    assert MARK in (templates["core"] / "app/trace.py").read_text(encoding="utf-8")


def test_nothing_source_only_is_shipped(templates: dict[str, Path]) -> None:
    for route, tree in templates.items():
        for rel in SOURCE_ONLY:
            assert not (tree / rel).exists(), (route, rel)
        makefile = (tree / "Makefile").read_text(encoding="utf-8")
        assert "templates:" not in makefile and "source-only" not in makefile, route
        assert "route:" not in makefile, route


def test_no_marker_survives_and_the_right_text_does(templates: dict[str, Path]) -> None:
    for tree in templates.values():
        for md in tree.rglob("*.md"):
            text = md.read_text(encoding="utf-8")
            assert "<!-- route:" not in text and "<!-- source-only" not in text, md
    week5 = {r: (templates[r] / "weeks/5/README.md").read_text(encoding="utf-8") for r in ROUTES}
    assert "On start, tracing is given" in week5["start"]
    assert "On start, tracing is given" not in week5["core"]
    assert "On core, the guard is implemented" in week5["core"]
    assert "On pro, both files" in week5["pro"] and "On core" not in week5["pro"]


def test_template_json_lists_route_dependent_files_per_week(templates: dict[str, Path]) -> None:
    for route, tree in templates.items():
        meta = json.loads((tree / ".template.json").read_text(encoding="utf-8"))
        assert meta["route"] == route == (tree / ".route").read_text().strip()
        week_files = meta["week_files"]
        assert "app/api/extract.py" in week_files["1"]
        assert "app/trace.py" in week_files["5"]
        assert f"weeks/3/routes/{route}.md" in week_files["3"]
        for files in week_files.values():
            for rel in files:
                assert (tree / rel).exists(), (route, rel)


def test_strip_marked() -> None:
    text = (
        "a\n<!-- route:core,pro -->\nB\n<!-- /route -->\n"
        "c\n# source-only:begin\nx\n# source-only:end\n"
    )
    assert strip_marked(text, "start") == "a\nc\n"
    assert strip_marked(text, "pro") == "a\nB\nc\n"
