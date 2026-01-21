---
name: spec-driven-tdd-workflow
description: A workflow that drives development from requirements refined into observable behaviors (AC/EC) through requirement definition → design → implementation planning → TDD (Red/Green/Refactor) implementation → reporting → commit. Apply to tasks that execute based on `.specdoc/current/*.md`.
---

# Spec-driven TDD Workflow

- Open `.specdoc/docs/planning-guide.md` first, and follow it for the rest of the workflow.
- Create/update `.specdoc/current/requirement.md`, `.specdoc/current/design.md`, `.specdoc/current/plan.md`, and `.specdoc/current/report.md` to maintain traceability from requirements → design → plan → implementation.
- Keep user interviews/questions short and prioritized. For each question, include answer candidates (options) and your recommended choice based on analysis/simulation to reduce cognitive load.
- Implement each step in `.specdoc/current/plan.md` as one observable behavior via TDD (Red → Green → Refactor).
- Record commands/results/changes/decisions in `.specdoc/current/report.md` per session, and `git commit` at the end of the phase.
