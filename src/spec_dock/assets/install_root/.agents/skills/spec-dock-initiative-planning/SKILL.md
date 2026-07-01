---
name: spec-dock-initiative-planning
description: Leaf skill for initiative planning tasks in spec-dock.
---

# Spec-dock Initiative Planning

- Use this skill for initiative planning work.
- Typical fit: create/import an initiative, or update initiative-level requirement/design/plan docs.
- Prefer reusing/updating an existing initiative first; create/import only when no existing initiative fits.
- Primary workflow: `spec-dock/docs/workflow_initiative.md`.
- Spec authoring workflow: `spec-dock/docs/workflow_spec_authoring.md`.
- For shared phase authoring method, use:
  - `spec-dock/docs/phase_requirement.md`
  - `spec-dock/docs/phase_design.md`
  - `spec-dock/docs/phase_plan.md`
- Decision routing examples and detailed placement guidance: `spec-dock/docs/authoring/decision-routing.md`.
- First-read gate: keep cross-epic product, investment, success-metric, or operating-model decisions in Initiative planning, but route ADR-worthy decisions to ADR and missing source-of-truth gaps to clarification.
- A user request to use a SpecDock workflow is explicit workflow-scoped authorization to use the SpecDock-defined named sub-agents and reviewers required by that workflow.
- Do not ask for additional per-role or per-phase permission before invoking SpecDock-defined named roles within the active repo/worktree, active SpecDock scope, current session, and documented role responsibility.
- Ask the user only for scope expansion, destructive actions, external publishing, credentialed external mutation, private external systems, or roles outside the SpecDock workflow.
- ユーザーが SpecDock workflow の利用を依頼した場合、その依頼自体を、SpecDock が定義する named sub-agent / reviewer を workflow に従って利用する明示的な許可として扱う。
- active repo/worktree、active SpecDock scope、current session、documented role responsibility の範囲内では、role ごと・phase ごとの追加承認を求めない。
- scope expansion、破壊的操作、外部公開、credential を伴う外部 mutation、private external system、SpecDock workflow 外の role 利用は別途確認する。
- When decomposing work into Epics, do not pass down a decision-only container as execution-ready; pass down only bounded Epic scope or record the remaining Initiative-level decision/follow-up.
- Keep this skill as routing guidance only; use `spec-dock/docs/authoring/decision-routing.md` for examples and detailed routing.
- Keep scope-specific constraints and decisions in `workflow_initiative.md`.
- In spec authoring mode, do not move from requirement to design, design to plan, or plan to Epic decomposition until a fresh `spec-reviewer` returns `review_status: pass`; fix findings and re-run a fresh reviewer until pass.
- Record each `Spec Authoring Gate` in the initiative `report.md`, including investigation, user questions/answers, reviewer verdict, fixes, and promotion decision.
- Fresh reviewer passes required by the workflow are gates and must not be skipped while waiting for extra permission inside the bounded SpecDock workflow scope.
- Do not default to create/import; keep new-initiative rationale in `artifacts/`.
- `spec-dock/docs/reference_github.md`
- `spec-dock/docs/reference_sync.md`
- `spec-dock/docs/reference_naming.md`
