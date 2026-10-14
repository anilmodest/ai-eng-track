# Route templates (programme team only)

This file is never shipped to a fellow. It says how this source repository becomes the three
templates fellows create their repositories from, and what to set up once.

## How it works

```
ai-eng-track (this repo, the only place the material is edited)
   │  push to main
   ▼
publish-templates.yml ── scripts/templates.py build --route R ──► week 0 check on a copy
   │
   ├──► <owner>/ai-eng-track-start   (template repository)
   ├──► <owner>/ai-eng-track-core
   └──► <owner>/ai-eng-track-pro
```

A fellow is sent one link: their route's template. They click **Use this template**, create a
**public** repository in their own account, then **Connect repo** (the programme's GitHub App,
installed on that one repository). Their repository holds their route and nothing of the other
two: no `weeks/N/routes/core/` folder of planted faults, no worked examples unless they are on
start, no command to switch route.

What differs by route is listed per week in the template's `.template.json` (`week_files`). If the
route is corrected at session 2, the programme's App opens one pull request on the fellow's
repository that replaces exactly those files for the weeks still ahead, from the new route's
template. Work already done is not touched.

## Marking text for one route, or for this repo only

In Markdown:

```
<!-- route:start -->
Only the start template keeps this (markers removed).
<!-- /route -->
<!-- route:core,pro -->
Core and pro keep this.
<!-- /route -->
<!-- source-only -->
No template keeps this.
<!-- /source-only -->
```

In Python, YAML and Makefiles, lines between `# source-only:begin` and `# source-only:end` are
removed. Whole files that never ship are listed in `SOURCE_ONLY` in `scripts/templates.py`.

Build them locally to look: `make templates` writes `build/templates/start|core|pro`.
`tests/unit/test_templates.py` checks that each template holds only its own route.

## One-time setup (on your account now, the platform organisation later)

1. Create three **public** repositories: `ai-eng-track-start`, `ai-eng-track-core`,
   `ai-eng-track-pro`, each with a README so they are not empty.
2. In each: **Settings → General → Template repository** on, and **Settings → Secrets and
   variables → Actions → Variables** → `IS_TEMPLATE` = `true` (stops the release workflow running
   on the template itself; the variable is not copied to repositories made from it).
3. Create a fine-grained personal access token limited to those three repositories with
   **Contents: read and write**. In this repository add it as the Actions secret
   `TEMPLATES_TOKEN`.
4. Optional variables in this repository: `PROGRAMME_OWNER` (default: this repository's owner) and
   `TEMPLATE_PREFIX` (default `ai-eng-track`).
5. Run **Actions → publish templates → Run workflow** once, and check each template repository.

When the programme moves to the platform organisation: transfer the four repositories, set
`PROGRAMME_OWNER` to the organisation, and replace the token with one the organisation issues.
Fellows' repositories are not affected.
