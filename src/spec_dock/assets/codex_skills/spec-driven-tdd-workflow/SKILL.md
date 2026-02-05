---
name: spec-driven-tdd-workflow
description: A workflow that drives development from requirements refined into observable behaviors (AC/EC) through requirement definition → design → implementation planning → TDD (Red/Green/Refactor) implementation → reporting. Apply to tasks that execute based on the active issue pointed by `.spec-dock/active/context-pack.md`.
---

# Spec-driven TDD Workflow

- Open `.spec-dock/docs/spec-dock-guide.md` first, and follow it for the rest of the workflow.
- Open `.spec-dock/active/context-pack.md` next. If it doesn't exist, ask the user to run `./.spec-dock/scripts/spec-dock active set --issue iss-xxxx` (or provide the target issue path/ID).
- Create/update the active issue docs (`requirement.md`, `design.md`, `plan.md`, `report.md`) to maintain traceability from requirements → design → plan → implementation.
- Put investigation/interview materials in the active issue `discussions/` directory (prefer Markdown; embed diagrams with PlantUML; organize freely).
- Keep user interviews/questions short and prioritized. For each question, include answer candidates (options) and your recommended choice based on analysis/simulation to reduce cognitive load.
- Implement each step in the active issue `plan.md` as one observable behavior via TDD (Red → Green → Refactor).
- Record commands/results/changes/decisions in the active issue `report.md` per session. Commit only if the repository's workflow allows it.
