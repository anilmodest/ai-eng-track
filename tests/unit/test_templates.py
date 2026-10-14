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
        others = {p for p in pages if p != f"{route}.md"}
        if route == "start":
            others = {p for p in others if not p.startswith("worked_example")}
        assert not others, (route, others)
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
    given = "Tracing is given and working on your route"
    stub = "On your route `app/trace.py` is signatures only"
    assert given in week5["start"] and stub not in week5["start"]
    assert stub in week5["core"] and given not in week5["core"]
    assert stub in week5["pro"] and "worked_example.py" not in week5["pro"]
    assert "worked_example.py" in week5["start"]


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


def test_every_core_fault_file_keeps_every_name_the_service_uses() -> None:
    """A core file replaces a whole file. If the source gained a function since the fault was
    planted, the core template would not even import: every top-level name must still be there."""
    import ast

    def names(path: Path) -> set[str]:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        out = set()
        for node in tree.body:
            if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef):
                out.add(node.name)
            elif isinstance(node, ast.Assign):
                out |= {t.id for t in node.targets if isinstance(t, ast.Name)}
        return {n for n in out if not n.startswith("_")}

    for faulty in sorted(ROOT.glob("weeks/*/routes/core/*.py")):
        source = ROOT / faulty.name.replace("__", "/")
        missing = names(source) - names(faulty)
        assert not missing, f"{faulty.name} lacks {sorted(missing)} from {source.relative_to(ROOT)}"
