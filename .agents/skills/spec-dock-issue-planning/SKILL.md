---
name: spec-dock-issue-planning
description: Plan an active spec-dock issue by authoring requirement/design/plan and Spec Authoring Gate evidence; no implementation or delivery claims.
---

# Spec-Dock Issue Planning

Use `spec-dock/docs/workflow_issue_planning.md` as the source of truth. This skill is only a concise reminder for Issue authoring and planning.

- Keep the parent orchestrator responsible for user dialogue, canonical `requirement.md` / `design.md` / `plan.md` / `report.md`, Evidence Adoption Ledger, and phase promotion.
- Read active issue context first: `spec-dock/active/context-pack.md`, active issue docs, parent epic / initiative docs, `workflow_spec_authoring.md`, `workflow_issue_planning.md`, `phase_design.md`, `phase_plan_issue.md`, and `authoring/issue-plan.md` as relevant.
- Perform source-grounding before asking the user. Use docs / code / ADR / discussions / primary sources to resolve local uncertainty.
- Use one-question-at-a-time clarification. Important questions require an unanswered `interview` sheet before asking, and the same sheet is completed after the answer.
- Route specialist findings through the orchestrator. Specialists return question candidates, reasons, affected artifacts, and recommended answers; they do not ask the human user directly.
- Use `research` for sources / facts / inference / unverified / terms / edge cases / implications.
- Use `disc` for synthesis, reflection proposal, and ADR candidate triage. It is not the adoption ledger.
- Use ADR sparingly for decisions that are hard to reverse, surprising without context, and involve a real tradeoff.
- Require fresh `spec-reviewer` pass for requirement, design, and plan before the next phase or execution handoff.
- Record Spec Authoring Gate evidence in active issue `report.md`: phase, artifact, reviewer, freshness, state, investigated facts, promotion / completion decision, and notes.

## Forbidden Claims

- Do not edit implementation files, tests, runtime code, package/config files, or GitHub state.
- Do not create PRs, claim merge-prepared, run issue finish, or claim delivery completion.
- Do not claim implementation readiness before fresh reviewer pass and Spec Authoring Gate evidence exist.
- Do not treat grill discussion evidence, delegated drafts, or external support artifacts as substitutes for fresh `spec-reviewer` pass.
- Do not split runtime CLI commands, redesign lifecycle state machines, auto-migrate existing artifacts, or redesign PR / finish lifecycle.

If a planning gap remains, return the smallest next planning action and do not route to execution.
