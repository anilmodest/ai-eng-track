"""What the hub needs from GitHub, not the repo: your pull requests and the hidden score.

    uv run python scripts/hub_data.py          # writes site/prs.json and site/hidden.json

Run by the pages workflow and by `make hub`. It uses the GitHub CLI (`gh`), which Codespaces and
Actions both have and are already signed in to. Without it, both files are written empty and the
hub says so: nothing else depends on them.

site/prs.json     {"<week>": {"number", "url", "state", "title", "head_sha", "review_comments"}}
site/hidden.json  {"<week>": {"sha", "conclusion", "summary", "at"}}

The hidden evaluation is run by the programme, not by you, on every pull request from week 2: a
check called `hidden-eval` on your commit. Its summary holds totals only, for example
`answer_accuracy=0.71 version_accuracy=0.93 n=150`. You never see its questions.
"""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
HIDDEN_CHECK = "hidden-eval"


def gh_json(*args: str) -> Any:
    """`gh <args>` parsed as JSON, or None if gh is missing, signed out, or the call fails."""
    if shutil.which("gh") is None:
        return None
    r = subprocess.run(["gh", *args], cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
    if r.returncode != 0 or not r.stdout.strip():
        return None
    try:
        return json.loads(r.stdout)
    except json.JSONDecodeError:
        return None


def this_repo() -> str | None:
    env = os.environ.get("GITHUB_REPOSITORY", "").strip()
    if env:
        return env
    view = gh_json("repo", "view", "--json", "nameWithOwner")
    return view.get("nameWithOwner") if isinstance(view, dict) else None


def weeks() -> list[int]:
    return sorted(int(p.parent.name) for p in ROOT.glob("weeks/*/README.md"))


def pull_request(repo: str, week: int) -> dict[str, Any] | None:
    found = gh_json(
        "pr",
        "list",
        "--repo",
        repo,
        "--state",
        "all",
        "--head",
        f"week-{week}",
        "--limit",
        "1",
        "--json",
        "number,url,state,title,headRefOid",
    )
    if not found:
        return None
    pr: dict[str, Any] = found[0]
    comments = gh_json("api", f"repos/{repo}/pulls/{pr['number']}/comments")
    return {
        "number": pr["number"],
        "url": pr["url"],
        "state": pr["state"],
        "title": pr["title"],
        "head_sha": pr["headRefOid"],
        "review_comments": len(comments) if isinstance(comments, list) else 0,
    }


def hidden_result(repo: str, sha: str) -> dict[str, Any] | None:
    runs = gh_json("api", f"repos/{repo}/commits/{sha}/check-runs?check_name={HIDDEN_CHECK}")
    if not isinstance(runs, dict) or not runs.get("check_runs"):
        return None
    run = runs["check_runs"][0]  # newest first
    return {
        "sha": sha,
        "conclusion": run.get("conclusion") or run.get("status"),
        "summary": (run.get("output") or {}).get("summary") or "",
        "at": run.get("completed_at") or run.get("started_at") or "",
    }


def main() -> int:
    SITE.mkdir(exist_ok=True)
    prs: dict[str, Any] = {}
    hidden: dict[str, Any] = {}
    repo = this_repo()
    if repo is None:
        print("hub_data: no GitHub CLI session; pull requests and hidden scores left out")
    else:
        for week in weeks():
            pr = pull_request(repo, week)
            if pr is None:
                continue
            prs[str(week)] = pr
            result = hidden_result(repo, pr["head_sha"])
            if result is not None:
                hidden[str(week)] = result
        print(f"hub_data: {repo}: {len(prs)} pull requests, {len(hidden)} hidden results")
    (SITE / "prs.json").write_text(json.dumps(prs, indent=2), encoding="utf-8")
    (SITE / "hidden.json").write_text(json.dumps(hidden, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
