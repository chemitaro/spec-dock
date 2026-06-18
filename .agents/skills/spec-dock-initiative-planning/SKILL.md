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
- When decomposing work into Epics, do not pass down a decision-only container as execution-ready; pass down only bounded Epic scope or record the remaining Initiative-level decision/follow-up.
- Keep this skill as routing guidance only; use `spec-dock/docs/authoring/decision-routing.md` for examples and detailed routing.
- Keep scope-specific constraints and decisions in `workflow_initiative.md`.
- In spec authoring mode, do not move from requirement to design, design to plan, or plan to Epic decomposition until a fresh `spec-reviewer` returns `review_status: pass`; fix findings and re-run a fresh reviewer until pass.
- Record each `Spec Authoring Gate` in the initiative `report.md`, including investigation, user questions/answers, reviewer verdict, fixes, and promotion decision.
- Do not default to create/import; keep new-initiative rationale in `discussions/`.
- `spec-dock/docs/reference_github.md`
- `spec-dock/docs/reference_sync.md`
- `spec-dock/docs/reference_naming.md`
