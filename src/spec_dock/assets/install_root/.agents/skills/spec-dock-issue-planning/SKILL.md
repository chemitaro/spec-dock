---
name: spec-dock-issue-planning
description: Actor-based issue requirement, design, and plan authoring workflow spine for spec-dock.
---

# Spec-dock Issue Planning

- Use this skill for issue planning work.
- Typical fit: create or update issue-level requirement/design/plan docs, prepare review readiness, or return unresolved execution gaps to authoring.
- Primary lifecycle / execution workflow: `spec-dock/docs/workflow_issue.md`.
- Spec authoring workflow: `spec-dock/docs/workflow_spec_authoring.md`.
- Clarification workflow for unresolved ambiguity, interview evidence, and source-grounded questions: `spec-dock/docs/workflow_clarification.md`.
- Issue plan phase playbook: `spec-dock/docs/phase_plan_issue.md`.
- Issue plan field semantics and executable step schema: `spec-dock/docs/authoring/issue-plan.md`.
- Decision routing examples and detailed placement guidance: `spec-dock/docs/authoring/decision-routing.md`.

## First-Read Decision Routing Gate

- Before issue-local planning, check whether the target is a decision-only Issue rather than an executable implementation slice.
- If the finding is cross-issue, cross-epic, ADR-worthy, or missing a source of truth, stop issue planning and route it to the smallest owning scope: Epic, Initiative, ADR, or clarification.
- Keep only Issue-local, reversible implementation tradeoffs inside issue planning, and record the adopted decision in the canonical issue artifacts or `report.md`.
- Use `spec-dock/docs/authoring/decision-routing.md` for examples and detailed routing. Do not copy those examples into this skill.

## Mandatory Issue Authoring Workflow

- Follow this actor sequence:
  1. Main orchestrator drafts or updates `requirement.md`.
  2. Main orchestrator obtains a fresh `spec-reviewer` pass for `requirement.md`.
  3. Main orchestrator requests a `system-architect` agent discussion draft for non-trivial design work, then performs handoff review, diff guard, Evidence Adoption Ledger, and canonical `design.md` integration.
  4. Main orchestrator obtains a fresh `spec-reviewer` pass for `design.md`.
  5. Main orchestrator requests an `implementation-planner` agent discussion draft for non-trivial implementation planning, then performs handoff review, diff guard, Evidence Adoption Ledger, and canonical `plan.md` integration.
  6. Main orchestrator obtains a fresh `spec-reviewer` pass for `plan.md`.
  7. Main orchestrator records execution handoff readiness in `report.md`.
- Fresh means the current artifact candidate was reviewed after its latest substantive change and the reviewer returned `review_status: pass`.
- Missing, stale, failed, unavailable, denied, waived, provisional, or any other non-pass reviewer state is not a pass; fix or re-run the gate before promotion or handoff.
- Unresolved requirement / design / plan gaps go back to `workflow_clarification.md` or the relevant prior authoring phase instead of becoming execution assumptions.
- Delegated drafts, research, and discussion artifacts are evidence only until the main orchestrator adopts them into canonical artifacts and records that adoption in `report.md`.
- Do not hand off to issue execution unless `plan.md` is executable under `phase_plan_issue.md` and `authoring/issue-plan.md`; a non-executable plan blocks execution handoff.
- Record Spec Authoring Gate evidence in the issue `report.md`, including reviewer verdicts, fixes, promotion decisions, and execution handoff readiness.

## Delegated Design Draft

- After requirement reviewer pass and before canonical `design.md` promotion, request the `system-architect` agent unless the design is trivial, the role is unavailable, consent is denied, or runtime support is unavailable.
- Pass the current issue scope, `requirement.md`, relevant parent specs, active context, known constraints, and required discussion output path.
- The allowed output is exactly one new flat Markdown evidence file under the target scope `discussions/`.
- The agent must not edit canonical docs, implementation files, tests, config, agent instructions, workflow files, GitHub state, or secrets.
- After the agent returns, the main orchestrator must inspect the diff, reject any forbidden write, review the draft, record adoption / rejection / skip reason in `report.md`, and rewrite adopted evidence into canonical `design.md`.
- The draft, handoff review, or adoption ledger is not a reviewer pass; run a fresh `spec-reviewer` on canonical `design.md` after integration.
- If the agent reports missing, stale, contradictory, or insufficient requirement evidence, return to requirement authoring or clarification instead of absorbing the gap in design.

## Delegated Plan Draft

- After design reviewer pass and before canonical `plan.md` promotion, request the `implementation-planner` agent unless the plan is trivial, the role is unavailable, consent is denied, or runtime support is unavailable.
- Pass the current issue scope, fresh reviewed `requirement.md` and `design.md`, relevant parent specs, active context, known constraints, and required discussion output path.
- The allowed output is exactly one new flat Markdown evidence file under the target scope `discussions/`.
- The agent must not edit canonical docs, implementation files, tests, config, agent instructions, workflow files, GitHub state, or secrets.
- After the agent returns, the main orchestrator must inspect the diff, reject any forbidden write, review the draft, record adoption / rejection / skip reason in `report.md`, and rewrite adopted evidence into canonical `plan.md`.
- The draft, handoff review, or adoption ledger is not a reviewer pass; run a fresh `spec-reviewer` on canonical `plan.md` after integration.
- If the agent reports missing, stale, contradictory, or insufficient design evidence, return to design authoring or clarification instead of absorbing the gap in plan.

## Delegation Fallbacks

- Manual authoring / manual fallback remains valid when a delegated role is unavailable, denied, unsupported, or intentionally skipped for a trivial issue.
- A fallback is not silent success. Record the role, reason, affected phase, manual path, evidence used, reviewer gate to preserve, and risk in `report.md`.
- Fallbacks never weaken reviewer gates, canonical single-writer authority, or execution handoff readiness requirements.

## Discussion Draft Path Compatibility

- Do not require delegated agents to create unsupported discussion kinds. Provide a repo-valid flat Markdown path directly under the target scope `discussions/`.
- If the surrounding runtime or docs use stricter discussion front matter, follow the runtime/docs contract and record any compatibility decision in `report.md`.

## Authority And Routing

- Keep canonical `requirement.md` / `design.md` / `plan.md` / `report.md` main-orchestrator-owned; this skill does not grant delegated canonical write authority.
- `system-architect` and `implementation-planner` are agent roles, not skills. Their role-specific behavior belongs in `.codex/agents/*.toml`; this issue-planning skill owns only the invocation, adoption, fallback, and reviewer-gate workflow.
- `system-architect` and `implementation-planner` drafts are scope-local evidence only. They do not replace main orchestrator integration, fresh `spec-reviewer` pass, phase promotion, implementation readiness, or issue execution handoff.
- In spec authoring mode, do not move from requirement to design, design to plan, or plan to execution until a fresh `spec-reviewer` returns `review_status: pass`; fix findings and re-run a fresh reviewer until pass.
- If planning reveals unresolved requirement / design / plan gaps, return to `workflow_clarification.md` or the relevant authoring phase instead of absorbing the gap in execution.
- Record each `Spec Authoring Gate` in the issue `report.md`, including investigation, user questions/answers, reviewer verdict, fixes, promotion decision, and handoff readiness.
