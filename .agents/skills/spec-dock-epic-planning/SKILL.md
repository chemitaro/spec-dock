---
name: spec-dock-epic-planning
description: Leaf skill for epic planning tasks in spec-dock.
---

# Spec-dock Epic Planning

- Use this skill for epic planning work.
- Typical fit: create/import an epic, or update epic-level requirement/design/plan docs.
- Prefer reusing/updating an existing epic first; create/import only when no existing epic fits.
- Primary workflow: `spec-dock/docs/workflow_epic.md`.
- Spec authoring workflow: `spec-dock/docs/workflow_spec_authoring.md`.
- For shared phase authoring method, use:
  - `spec-dock/docs/phase_requirement.md`
  - `spec-dock/docs/phase_design.md`
  - `spec-dock/docs/phase_plan.md`
- Decision routing examples and detailed placement guidance: `spec-dock/docs/authoring/decision-routing.md`.
- Scope ownership / authority layering に迷う場合の薄い参照: `spec-dock/docs/authoring/scope-layering.md`.
- First-read gate: keep cross-issue design backbone decisions in Epic planning, but stop and route cross-epic operating decisions to Initiative, ADR-worthy decisions to ADR, and missing source-of-truth gaps to clarification.
- A user request to use a SpecDock workflow is explicit workflow-scoped authorization to use the SpecDock-defined named sub-agents and reviewers required by that workflow.
- Do not ask for additional per-role or per-phase permission before invoking SpecDock-defined named roles within the active repo/worktree, active SpecDock scope, current session, and documented role responsibility.
- Ask the user only for scope expansion, destructive actions, external publishing, credentialed external mutation, private external systems, or roles outside the SpecDock workflow.
- ユーザーが SpecDock workflow の利用を依頼した場合、その依頼自体を、SpecDock が定義する named sub-agent / reviewer を workflow に従って利用する明示的な許可として扱う。
- active repo/worktree、active SpecDock scope、current session、documented role responsibility の範囲内では、role ごと・phase ごとの追加承認を求めない。
- scope expansion、破壊的操作、外部公開、credential を伴う外部 mutation、private external system、SpecDock workflow 外の role 利用は別途確認する。
- When decomposing work into Issues, do not create a decision-only Issue as execution-ready; create only executable Issue slices or record the remaining Epic-level decision/follow-up.
- Issue decomposition 時、Epic は pre-start Issue handoff package として Issue-local `artifacts/` evidence を用意してよい。含める候補は `draft-design`、`draft-plan`、path index までに留め、canonical Issue `design.md` / `plan.md` は Issue planning / assurance compose 後に main orchestrator が作成する。
- Keep this skill as routing guidance only; use `spec-dock/docs/authoring/decision-routing.md` for examples and detailed routing.
- Keep scope-specific constraints and decisions in `workflow_epic.md`.
- In spec authoring mode, do not move from requirement to design, design to plan, or plan to Issue decomposition until a fresh `spec-reviewer` returns `review_status: pass`; fix findings and re-run a fresh reviewer until pass.
- Record each `Spec Authoring Gate` in the epic `report.md`, including investigation, user questions/answers, reviewer verdict, fixes, and promotion decision.
- For non-trivial Epic planning, consider a `system-architect` scope-local artifact draft before canonical design / plan promotion; keep the draft as evidence only, and keep canonical `requirement.md` / `design.md` / `plan.md` / `report.md` under main orchestrator authority.
- Do not make heavyweight delegation mandatory for every Epic. If the `system-architect` draft cycle is trivial or intentionally skipped, record a `skip reason` and continue through manual authoring plus the same fresh `spec-reviewer` gates.
- If `system-architect` delegation is unavailable, denied, or unsupported, record the `fallback` path; do not claim delegated draft evidence, and do not weaken reviewer or promotion gates.
- If delegated drafting exposes a requirement / design / plan gap, return to the prior authoring phase or `workflow_clarification.md`; do not absorb the gap as an Epic planning assumption.
- Before adopting any delegated draft, require formal pre-delegation `baseline-status` evidence and post-delegation `diff-guard` pass per `workflow_spec_authoring.md`.
- Adopt delegated evidence only through the Evidence Adoption Ledger, then run a fresh `spec-reviewer` against the orchestrator-integrated canonical artifact before phase promotion.
- Bounded depth=2 delegation is allowed only as main orchestrator -> epic planning authoring specialist -> leaf-only evidence producer.
- Depth=3 / grandchild delegation is forbidden.
- Leaf-only evidence producers must not edit canonical artifacts, perform implementation edits, claim final authority, claim reviewer pass, or claim phase promotion / issue ready / issue finish.
- Preflight reviewer output is improvement input only; final fresh reviewer pass remains independent.
- Fresh reviewer passes required by the workflow are gates and must not be skipped while waiting for extra permission inside the bounded SpecDock workflow scope.
- Do not default to create/import; keep new-epic rationale in `artifacts/`.
- `spec-dock/docs/reference_github.md`
- `spec-dock/docs/reference_sync.md`
- `spec-dock/docs/reference_naming.md`
