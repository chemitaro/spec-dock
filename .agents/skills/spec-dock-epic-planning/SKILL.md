---
name: spec-dock-epic-planning
description: Leaf skill for creating or updating Epic-level requirement, design, plan, Issue handoff evidence, and reviewer-gated planning artifacts in SpecDock.
---

# Spec-Dock Epic Planning

Use this skill for Epic planning: create/import an Epic, update Epic `requirement.md` / `design.md` / `plan.md`, preserve planning evidence, or prepare downstream Issue handoff. Prefer reusing an existing Epic; create/import only when no current Epic fits.

This skill is an operational kernel. Keep detailed policy in docs and keep global invariants in `spec-dock-hub`.

Contract anchor: create/import an epic when no existing Epic fits; capture scope-specific constraints and decisions before Issue handoff; record Spec Authoring Gate evidence after fresh `spec-reviewer` pass.

ChatGPT authoring relationship: `spec-dock-chatgpt-authoring` may provide Epic planning evidence, ZIP/tree output, Issue draft artifacts, candidate reports, or handoff indexes. Those outputs are evidence-only; Epic planning still owns Issue slicing, Evidence Adoption Ledger entries, and human approval before Issue node creation. Canonical Issue docs remain Issue planning outputs.

## Read First

- Current state: `./spec-dock/scripts/spec-dock active show`, active Initiative/Epic docs, existing sibling Epics, `artifacts/`, legacy `discussions/` when present, related code/tests/templates/ADRs, and relevant user attachments.
- Workflows and phase playbooks:
  - `spec-dock/docs/workflow_epic.md`
  - `spec-dock/docs/workflow_spec_authoring.md`
  - `spec-dock/docs/phase_requirement.md`
  - `spec-dock/docs/phase_design.md`
  - `spec-dock/docs/phase_plan.md`
  - `spec-dock/docs/phase_plan_epic.md`
- Routing references:
  - `spec-dock/docs/authoring/decision-routing.md`
  - `spec-dock/docs/authoring/scope-layering.md`
  - `spec-dock/docs/reference_github.md`
  - `spec-dock/docs/reference_sync.md`
  - `spec-dock/docs/reference_naming.md`
  - Command syntax: `./spec-dock/scripts/spec-dock new --help`, `workflow_epic.md`, and `reference_naming.md` are the authority. Do not hand-build artifact paths; use `new artifact` stdout `path=...`.

## Operating Spine

1. Establish parent Initiative and Epic fit.
   - If active scope is missing or ambiguous, inspect local state first; ask the user one blocking question only if local sources cannot determine placement.
   - Keep new-Epic rationale in scope-local `artifacts/`.
2. Build source-grounded understanding before authoring.
   - Preserve raw research separately from synthesized decisions.
   - If the target Epic does not exist yet and the parent Initiative is known, create only attachment inventory and fit analysis under the parent Initiative `artifacts/`; after Epic creation, adopt the relevant research into Epic `artifacts/` and record the move/adoption in `report.md`.
   - If both target Epic and parent Initiative are unknown, do not create durable repo artifacts yet; keep only session-local inventory in the host/session temp area outside canonical docs, resolve parent scope, then create scope-local artifacts.
   - Do not ask the user about facts or constraints available from repo docs, artifacts, code, tests, templates, ADRs, or attachment contents.
3. Route decisions before writing.
   - Epic owns cross-Issue scope, backbone design, Issue slicing, Issue dependency, and handoff package decisions.
   - Route cross-Epic operating/product decisions to Initiative.
   - Route durable decision records to ADR.
   - Route missing source-of-truth or user-intent blockers to `spec-dock-clarification`.
4. Author phases in order: requirement -> design -> plan -> Issue handoff.
   - Each phase needs a fresh `spec-reviewer` `review_status: pass` before the next phase starts. In Codex, use the `spec-reviewer` sub-agent role; in other hosts, use the equivalent reviewer mechanism. Treat unavailable or denied reviewer access as a blocked gate rather than a pass.
   - Record investigation, questions/answers, reviewer verdict, fixes, adoption decisions, and promotion decision in Epic `report.md`.
5. Use specialists as evidence producers, not authorities.
   - For non-trivial planning, a `system-architect` draft may be useful, but it is optional.
   - If delegation is skipped, unavailable, denied, or unsupported, record the skip/fallback reason and continue only if reviewer gates remain intact.
   - Adopt specialist output only through `report.md` Evidence Adoption Ledger and canonical-doc integration by the main orchestrator.
   - Bounded depth=2 delegation only: Depth=3 / grandchild delegation is forbidden.
   - Leaf-only evidence producers must not edit canonical artifacts; final fresh reviewer pass remains independent.
6. Prepare Issue handoff without finalizing Issue execution docs.
   - Create executable Issue slices only; do not create decision-only Issues as execution-ready work.
   - Epic planning may create Issue-local `artifacts/` evidence such as `draft-design`, `draft-plan`, and a path index.
   - ChatGPT / Oracle ZIP/tree output may be staged as Issue draft evidence, but it is not canonical adoption and is not execution-ready.
   - Canonical Issue `design.md` / `plan.md` remain Issue planning outputs; do not finalize them during Epic planning.

## Stop Conditions

- Parent Initiative / active scope cannot be determined from local sources.
- Existing Epic fit is unresolved and creating a new Epic would duplicate or fragment work.
- A decision belongs to Initiative, ADR, or clarification rather than Epic.
- Requirement / design / plan candidate changed after review and lacks a fresh `spec-reviewer` pass.
- Specialist output has not been adopted into canonical docs and `report.md`.
- ChatGPT / Oracle ZIP/tree output or Issue draft artifacts have not been reviewed and adopted or rejected in `report.md`.
- Issue node creation lacks explicit human approval.
- Issue handoff would require execution-ready claims for template-only, draft-only, or unreviewed Issue docs.
