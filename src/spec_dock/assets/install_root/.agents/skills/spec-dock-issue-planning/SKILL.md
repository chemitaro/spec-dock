---
name: spec-dock-issue-planning
description: Actor-based issue requirement, design, and plan authoring workflow spine for spec-dock.
---

# Spec-dock Issue Planning

Use this skill for issue planning work: create or update issue-level requirement/design/plan docs, prepare review readiness, or return unresolved execution gaps to authoring.

This skill is a fixed kernel. It must not carry state-specific generated Runbook text, full profile procedure sets, or issue-local workflow projections.

## Workflow-Scoped Authorization

- A user request to use a SpecDock workflow is explicit workflow-scoped authorization to use the SpecDock-defined named sub-agents and reviewers required by that workflow.
- Do not ask for additional per-role or per-phase permission before invoking SpecDock-defined named roles within the active repo/worktree, active SpecDock scope, current session, and documented role responsibility.
- Ask the user only for scope expansion, destructive actions, external publishing, credentialed external mutation, private external systems, or roles outside the SpecDock workflow.
- ユーザーが SpecDock workflow の利用を依頼した場合、その依頼自体を、SpecDock が定義する named sub-agent / reviewer を workflow に従って利用する明示的な許可として扱う。
- active repo/worktree、active SpecDock scope、current session、documented role responsibility の範囲内では、role ごと・phase ごとの追加承認を求めない。
- scope expansion、破壊的操作、外部公開、credential を伴う外部 mutation、private external system、SpecDock workflow 外の role 利用は別途確認する。

## First-Read Handoff

- First ask the runtime for current planning guidance:
  - `./spec-dock/scripts/spec-dock guidance issue-planning`
- Treat the command stdout as current guidance only. It is not canonical authority, and must not be edited as source of truth.
- Register the returned `state`, `next_action`, `reason_code`, `authority`, commands, and stop conditions in your task checklist before acting.
- Do not expect or derive authoring phase, implementation step, worker, reviewer, verification, or context packet details from runtime guidance. Use canonical docs and the active artifacts for phase and planning obligations.
- If runtime guidance cannot be generated, is malformed, or contradicts canonical docs, stop and fall back to the canonical docs below instead of guessing the next phase.
- Generated projections such as `spec-dock/.agent/runbooks/current-runbook.*` or `spec-dock/active/current-runbook.*` are ignored human/debug output. Do not read, edit, or manage them as handoff authority.

## Canonical Fallback

- Primary lifecycle / execution workflow: `spec-dock/docs/workflow_issue.md`.
- Spec authoring workflow: `spec-dock/docs/workflow_spec_authoring.md`.
- Clarification workflow for unresolved ambiguity, interview evidence, and source-grounded questions: `spec-dock/docs/workflow_clarification.md`.
- Requirement phase playbook: `spec-dock/docs/phase_requirement.md`.
- Design phase playbook: `spec-dock/docs/phase_design.md`.
- Issue plan phase playbook: `spec-dock/docs/phase_plan_issue.md`.
- Issue plan field semantics and executable step schema: `spec-dock/docs/authoring/issue-plan.md`.
- Decision routing examples and detailed placement guidance: `spec-dock/docs/authoring/decision-routing.md`.

## Issue grade 補足

- Issue の `requirement.md`、`design.md`、`plan.md` を作成または更新する前に、`spec-dock/docs/workflow_spec_authoring.md` の Issue grade matrix を読む。
- `authorized_profile` は runtime template、guidance、obligation authority として扱う。manual escalation は reviewer / specialist / evidence gate を追加で強める判断であり、authority override ではない。
- Lite は automatic default ではない。低リスク根拠が明示される場合だけ Lite を使う。grade、scope、impact、reviewer obligation が unknown / ambiguous の場合は Standard 以上へ倒す。
- Standard では specialist 使用を推奨する。使わない場合は、確認した source、skip reason、残リスクを `report.md` に残す。
- Strict / Critical では specialist 使用を原則必須にする。unavailable、denied、host constraint で使えない場合は、継続前に manual fallback evidence を `report.md` に残す。Critical の fallback は明示承認がない限り通常 blocked のまま扱う。
- 後続作業の stable term として、G2 `draft routing`、G3 `report evidence gate`、G4 `integrated smoke matrix` を維持する。この skill は用語を固定するだけで、routing、report validation、smoke coverage は実装しない。

## Stop Conditions And Authority

- Stop if active context, artifact freshness, reviewer pass evidence, or delegated draft adoption evidence is missing, stale, failed, unavailable, denied, waived, provisional, or contradictory.
- Stop if `authorized_profile` is missing, ambiguous, or inconsistent with the requested obligation.
- Stop if the Issue grade is missing or ambiguous, unless the plan explicitly escalates to Standard or higher and records the reason.
- Stop if `requirement.md`, `design.md`, or `plan.md` is template-only, unresolved, or not reviewer-passed for the current phase.
- Stop if planning reveals unresolved requirement / design / plan gaps; route back to `spec-dock/docs/workflow_clarification.md` or the relevant authoring phase.
- Keep canonical `requirement.md` / `design.md` / `plan.md` / `report.md` main-orchestrator-owned. This skill does not grant delegated canonical write authority.
- `system-architect` and `implementation-planner` are delegated agent roles only; their drafts are scope-local evidence only and do not replace main orchestrator adoption, fresh `spec-reviewer` pass, phase promotion, or execution handoff readiness.
- Delegated drafts, research, discussions, and generated Runbooks are evidence only until adopted into canonical artifacts and recorded in `report.md`.
- Fresh means the current artifact candidate was reviewed after its latest substantive change and fresh `spec-reviewer` returns `review_status: pass`.
- Fresh `spec-reviewer` passes are required gates and must not be skipped while waiting for extra permission inside the bounded SpecDock workflow scope.
- Record Spec Authoring Gate evidence in `report.md` when canonical artifacts are promoted or execution handoff readiness changes.

## Kernel Boundary

- Use the runtime Runbook and canonical docs for phase-specific procedure details; do not copy the full workflow here.
- Keep only durable entrypoint, authority, freshness, fallback, and stop-condition reminders in this skill.
