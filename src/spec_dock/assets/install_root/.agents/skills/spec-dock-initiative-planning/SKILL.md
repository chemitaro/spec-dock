---
name: spec-dock-initiative-planning
description: Leaf skill for creating or updating Initiative-level requirement, design, plan, Epic decomposition, and reviewer-gated planning artifacts in SpecDock.
---

# Spec-Dock Initiative Planning

Use this skill for Initiative planning: create/import an Initiative, update Initiative `requirement.md` / `design.md` / `plan.md`, or prepare bounded Epic decomposition. Prefer reusing an existing Initiative; create/import only when no current Initiative fits.

This skill is an operational kernel. Keep detailed policy in docs and keep global invariants in `spec-dock-hub`.

Contract anchor: create/import an initiative when no existing Initiative fits; capture scope-specific constraints and decisions before Epic decomposition; record Spec Authoring Gate evidence after fresh `spec-reviewer` pass.

ChatGPT-first primary route: for non-trivial Initiative planning, use `spec-dock-chatgpt-authoring` as the primary evidence-production route before canonical authoring. If ChatGPT/browser/backend capacity is busy, wait and retry; if automation is unhealthy, recover or restart the browser/backend and retry. Do not switch to manual planning for queued tabs, retryable timeouts, stale sync, or fixable prompt/backend setup.

Manual backup route: use `spec-dock-initiative-planning-manual` only after hard / unrecoverable ChatGPT route failure and explicit human approval. Record the failure class, recovery attempts, approval evidence, and manual-route decision in Initiative `report.md`.

ChatGPT authoring relationship: `spec-dock-chatgpt-authoring` may provide Initiative decomposition evidence, candidate Epic summaries, or comparison artifacts. Those outputs are evidence-only; Initiative planning still owns canonical Initiative docs, Evidence Adoption Ledger entries, fresh `spec-reviewer` pass, and human approval before Epic node creation.

## Read First

- Current state: `./spec-dock/scripts/spec-dock active show`, existing Initiatives/Epics, active docs, `artifacts/`, legacy `discussions/` when present, related code/tests/templates/ADRs, and relevant user attachments.
- Workflows and phase playbooks:
  - `spec-dock/docs/workflow_initiative.md`
  - `spec-dock/docs/workflow_spec_authoring.md`
  - `spec-dock/docs/phase_requirement.md`
  - `spec-dock/docs/phase_design.md`
  - `spec-dock/docs/phase_plan.md`
  - `spec-dock/docs/phase_plan_initiative.md`
- Routing references:
  - `spec-dock/docs/authoring/decision-routing.md`
  - `spec-dock/docs/authoring/scope-layering.md`
  - `spec-dock/docs/reference_github.md`
  - `spec-dock/docs/reference_sync.md`
  - `spec-dock/docs/reference_naming.md`

## Operating Spine

1. Establish Initiative fit.
   - Inspect existing Initiatives before creating/importing.
   - Keep new-Initiative rationale in `artifacts/`.
2. Build source-grounded understanding before authoring.
   - Answer what local sources can answer; ask the user only for blocking intent gaps.
   - Use Japanese-first prose while preserving exact paths, commands, identifiers, role names, and SpecDock fixed terms.
   - For non-trivial scope, prepare a ChatGPT-first evidence request with repo/branch or local-context evidence and an explicit ZIP/tree output contract when useful.
   - Adopt only source-grounded claims through `report.md`; rewrite canonical docs locally and obtain fresh reviewer pass after integration.
3. Route decisions before writing.
   - Initiative owns cross-Epic product, investment, success metric, operating model, and roadmap boundary decisions.
   - Route ADR-worthy decisions to ADR.
   - Route missing source-of-truth or user-intent blockers to `spec-dock-clarification`.
4. Author phases in order: requirement -> design -> plan -> Epic decomposition.
   - Each phase needs a fresh `spec-reviewer` `review_status: pass` before the next phase starts.
   - Record investigation, questions/answers, reviewer verdict, fixes, adoption decisions, and promotion decision in Initiative `report.md`.
5. Decompose only bounded Epic scope.
   - Do not pass down decision-only containers as execution-ready Epics.
   - Keep remaining Initiative-level decisions or follow-ups at Initiative scope.

## Stop Conditions

- Existing Initiative fit is unresolved and creating a new Initiative would duplicate or fragment work.
- A decision belongs to ADR or clarification rather than Initiative.
- Requirement / design / plan candidate changed after review and lacks a fresh `spec-reviewer` pass.
- ChatGPT / Oracle decomposition evidence has not been adopted or rejected in `report.md`.
- ChatGPT-first route has a retryable, recoverable, waiting, or setup failure and manual backup has not been explicitly approved by the user.
- Epic candidate creation lacks explicit human approval.
- Epic decomposition would pass unresolved Initiative decisions downstream as ready work.
