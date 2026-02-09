---
name: spec-driven-tdd-workflow
description: A workflow that drives development from requirements refined into observable behaviors (AC/EC) through requirement definition → design → implementation planning → TDD (Red/Green/Refactor) implementation → reporting. Apply to tasks that execute based on the active issue pointed by `spec-dock/active/context-pack.md`.
---

# Spec-driven TDD Workflow

- Open `spec-dock/docs/README.md` first.
- Open `spec-dock/docs/workflow-issue.md` next (Issue workflow). If the task is multi-issue or re-architecture, also consult `spec-dock/docs/workflow-tree.md` and `spec-dock/docs/workflow-adr.md`.
- Check active pointers: run `./spec-dock/scripts/spec-dock active show`.
  - If active is not set, ask the user to run `./spec-dock/scripts/spec-dock active set iss-xxxx` (or provide the GitHub issue number / issue URL).
  - Then open `spec-dock/active/context-pack.md`.
- Read the active Issue specs and keep them as the source of truth:
  - `spec-dock/active/issue/requirement.md` → `spec-dock/active/issue/design.md` → `spec-dock/active/issue/plan.md`
- Also read parent specs as needed (to avoid duplication and respect guardrails):
  - `spec-dock/active/epic/{requirement,design,plan}.md`
  - `spec-dock/active/initiative/{requirement,design,plan}.md`
- If a real trade-off/decision is needed, create an ADR early and keep its Decision **TBD** until the user/reviewer makes the final call:
  - `./spec-dock/scripts/spec-dock new adr --issue iss-xxxx --title "..."` (or `--epic/--initiative`)
- After the user/reviewer decides, update the ADR Decision, set it to `accepted`, and reflect the decision back into the relevant spec files (`design.md` / `plan.md`) with links.
- Put investigation/interview materials in the active issue `discussions/` directory (Markdown; embed diagrams with PlantUML when helpful; do not force a specific UML format).
- Keep interviews/questions short and prioritized. For each question, include answer candidates (options) and your recommended choice based on analysis.
- Implement each step in the active issue `plan.md` as one observable behavior via TDD (Red → Green → Refactor).
- Record commands/results/changes/decisions in `spec-dock/active/issue/report.md` per session. Commit only if explicitly instructed or the repository workflow requires it.
- Use `./spec-dock/scripts/spec-dock sync` (and optionally `--github`) to refresh `spec-dock/.agent/index.json` and `spec-dock/.agent/tree.json` when you need the latest tree view.
