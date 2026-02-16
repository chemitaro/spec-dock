---
name: spec-driven-tdd-workflow
description: A workflow that drives development from requirements refined into observable behaviors (AC/EC) through requirement definition → design → implementation planning → TDD (Red/Green/Refactor) implementation → reporting. Apply to tasks that execute based on the active issue pointed by `spec-dock/active/context-pack.md`.
---

# Spec-driven TDD Workflow

## First time onboarding (recommended)

- Open `spec-dock/docs/README.md` and `spec-dock/docs/guide.md` first.
- Open `spec-dock/docs/workflow_issue.md` next (Issue workflow). If the task spans multiple layers (initiative/epic) or requires design decisions, also consult `spec-dock/docs/workflow_initiative.md`, `spec-dock/docs/workflow_epic.md`, and `spec-dock/docs/workflow_adr.md`.

## Each session

- Safety notes (before running commands):
  - `./spec-dock/scripts/spec-dock active set ...` may checkout branches for GitHub-linked nodes (requires a clean working tree).
  - For `new/import {initiative,epic,issue}`, `--title` must be ASCII (alphanumerics + single spaces) and `--slug` must be kebab-case; if validation fails, ask the user to provide a compliant title/slug (put non-ASCII context in requirement/design instead).
  - `./spec-dock/scripts/spec-dock new ...` creates GitHub Issues by default (use `--no-github` to opt out).
- Check active pointers: run `./spec-dock/scripts/spec-dock active show`.
  - If active is not set, ask the user to run `./spec-dock/scripts/spec-dock active set <id|#num|url>`.
    - Examples: `./spec-dock/scripts/spec-dock active set iss-00123` / `./spec-dock/scripts/spec-dock active set 123` / `./spec-dock/scripts/spec-dock active set https://github.com/<owner>/<repo>/issues/123`
  - Then open `spec-dock/active/context-pack.md`.
- Read the active Issue specs and keep them as the source of truth:
  - `spec-dock/active/issue/requirement.md` → `spec-dock/active/issue/design.md` → `spec-dock/active/issue/plan.md`
- Also read parent specs as needed (to avoid duplication and respect guardrails):
  - `spec-dock/active/epic/{requirement,design,plan}.md`
  - `spec-dock/active/initiative/{requirement,design,plan}.md`
- If a real trade-off/decision is needed, create an ADR early and keep its Decision **TBD** until the user/reviewer makes the final call:
  - Prefer scope-local wrappers (single title arg):
    - `spec-dock/active/issue/adrs/new-adr "..."`
    - `spec-dock/active/epic/adrs/new-adr "..."`
    - `spec-dock/active/initiative/adrs/new-adr "..."`
  - Fallback (direct runtime command): `./spec-dock/scripts/spec-dock new adr --issue iss-00123 --title "..."` (or `--epic/--initiative`)
- After the user/reviewer decides, update the ADR Decision, set it to `accepted`, and reflect the decision back into the relevant spec files (`design.md` / `plan.md`) with links.
- Put investigation/interview materials in the active issue `artifacts/` directory (Markdown; embed diagrams with PlantUML when helpful; do not force a specific UML format). If `discussions/` exists in older nodes, treat it as legacy read-only context.
- Keep interviews/questions short and prioritized. For each question, include answer candidates (options) and your recommended choice based on analysis.
- Implement each step in the active issue `plan.md` as one observable behavior via TDD (Red → Green → Refactor).
- Record commands/results/changes/decisions in `spec-dock/active/issue/report.md` per session. Commit only if explicitly instructed or the repository workflow requires it.
- Use `./spec-dock/scripts/spec-dock sync` (and optionally `--github`) to refresh `spec-dock/.agent/index.json` and `spec-dock/.agent/tree.json` when you need the latest tree view.
