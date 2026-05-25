---
種別: ディスカッション
ID: "20260524t000000z-02-disc-fallback-implementation-planner-plan-draft"
タイトル: "S02 fallback implementation-planner plan draft"
状態: "draft"
作成者: "spec-dock-implementation-planner"
親: ["iss-00125", "epic-00112", "init-local-00003"]
authority: "proposed"
source_revision: "608a7e994e37e2ee2d095eb96f6700ebe1f62e1b"
---

# S02 fallback implementation-planner plan draft

## Plan Summary

`iss-00125` は S01 により prerequisite closure / explicit fallback、active scope、validate/sync baseline、Permission Profile 状態、S02 Task Manifest Lock が記録済みです。S02 は `pilot_target_issue_id: none` のため、write-scoped canonical `design.md` / `plan.md` authoring ではなく、issue-local `discussions/` への fallback draft evidence として完了させます。

この proposal は implementation-planner の S02 fallback plan draft evidence です。canonical `plan.md`、`report.md`、provider source、tests、config、GitHub state は編集しません。`HEAD` は Task Manifest Lock の source hash `608a7e994e37e2ee2d095eb96f6700ebe1f62e1b` と一致します。

## Requirement / Design Traceability

- AC-001 / EC-001 / EC-003: S01 の Task Manifest Lock により、Permission/Profile/host behavior が canonical write verification を許可しないため S02 は proposal-only fallback として実行する。
- AC-002: S02 では system-architect と implementation-planner の draft evidence を `authority: proposed` として記録し、promotion / reviewer-pass / implementation-readiness を claim しない。
- AC-003 / EC-001: S03 で fallback discussion draft が context-pack / lifecycle authoritative input にならないこと、または canonical write verification が disabled/fallback であることを記録する。
- AC-004 / EC-002: v0 `iss-00113`-`iss-00118` と prerequisite v1 `iss-00120`-`iss-00124` の plans/reports は書き換えず、provider defect は follow-up/amendment disposition とする。
- Parent Epic E-AC-010-E-AC-012: `iss-00125` の additive rollout/fallback evidence、provider-first parity/no-provider-change evidence、requirement authority prerequisite/fallback evidence で閉じる。

## Milestones

- M1: S02 fallback draft evidence を揃える。system-architect design fallback draft と implementation-planner plan fallback draft を locked discussions path に保存し、`report.md` へ no-promotion evidence として統合する。
- M2: S03 で lifecycle/context-pack fallback を検証し、fallback draft が canonical authority として扱われないことを記録する。
- M3: S03 で provider defect の有無を disposition する。defect があれば provider source を直接直さず、owning issue amendment または follow-up として記録する。
- M4: S90 で docs impact を no-op/follow-up/update に分類し、spec-reviewer gate を通す。
- M5: S99 で qa-reviewer、issue-wide code-reviewer、final spec-reviewer、validate/sync、final report/commit/PR delivery evidence を閉じる。
- M6: Epic G10 で `iss-00120`-`iss-00125` 全体の `baseRefOid...HEAD` 差分を deep-consultant と spec-reviewer が確認する。

## Dependency-Derived Execution Order

1. S01 reviewer gate を先に通す。S01 が pending reviewer のままなら S02 fallback draft は統合 evidence にはできても step closure pass にはしない。
2. S02 は canonical write を試さず、locked discussion paths に fallback draft evidence を保存する。
3. S02 の `tc-003` は system-architect draft、`tc-004` は implementation-planner draft で別々に closure evidence を残す。
4. S03 は S02 evidence 後に実行し、fallback draft が active/context-pack/lifecycle authoritative input にならないことを確認する。
5. Provider defect が出た場合は S03/S90 で follow-up/amendment disposition を先に閉じ、silent fix はしない。
6. S90 docs impact を閉じてから S99 final quality gate に進む。
7. S99 issue-local closure 後、Epic PR #119 更新前に G10 epic-wide pre-PR gate を実行する。

## Issue / Step Slicing

- S02 / `tc-004`: implementation-planner fallback plan draft evidence
  - allowed output: locked discussion draft proposal only.
  - required record: draft path, source hash, source artifacts read, `authority: proposed`, no final authority claimed.
  - stop condition: source hash mismatch, active issue mismatch, path lock change, or request to edit canonical artifacts.
- S03 / `tc-005`: lifecycle/context-pack fallback verification
  - evidence: `active show`, `validate`, relevant active/context-pack inspection, and report statement that fallback discussion drafts are not canonical authority.
- S03 / `tc-006`: provider defect disposition
  - evidence: git diff scope and defect ledger/no-defect statement.
  - rule: provider/source/runtime/test defects become follow-up/amendment, not pilot-local silent implementation.
- S90 / `tc-090`: docs impact
  - evidence: `validate`, `rg` for Task Manifest Lock/fallback fields, spec-reviewer docs/spec alignment.
- S99 / `tc-099`: final quality
  - evidence: all closure rows pass or approved-no-op, final QA/code/spec reviewers pass, validate/sync pass, final report ledger complete, final commit and delivery/PR gates recorded by orchestrator.

## Test Strategy Mapping

- S02 fallback: inspect-only evidence. Verify the saved discussion draft exists at the locked path and contains `status: draft`, `authority: proposed`, source hash, rejected canonical-write scope, blockers, and no promotion claim.
- S03 lifecycle: run `./spec-dock/scripts/spec-dock active show` and `./spec-dock/scripts/spec-dock validate`; inspect `spec-dock/active/context-pack.md` and report that fallback discussion drafts did not become active authoritative design/plan input.
- S03 provider defect: run `git diff --name-status` or equivalent scope check after S02/S03. If provider/runtime/test/config paths changed, stop for amendment unless explicitly authorized by a reviewed plan update.
- S90 docs: run `./spec-dock/scripts/spec-dock validate` and `rg -n 'Task Manifest Lock|pilot_target_issue_id|design_draft_path|plan_draft_path|stale-if|fallback' .../iss-00125-*/report.md`.
- S99: run final validate/sync and required reviewers. Treat any reviewer unavailable/denied/waived/provisional as incomplete, not pass.

## Review Gates

- S01 gate: fresh spec-reviewer pass is required before S01 is closed.
- S02 gate: fresh spec-reviewer reviews fallback delegated draft provenance and no-promotion claims; delegated draft itself is not reviewer approval.
- S03 gate: code-reviewer only if runtime/provider diff appears; otherwise spec-reviewer/QA evidence can confirm fallback/no-op scope.
- S90 gate: fresh spec-reviewer docs/spec alignment pass.
- S99 gates: qa-reviewer pass, issue-wide code-reviewer pass, final spec-reviewer pass.
- G10 gate: fresh deep-consultant and fresh spec-reviewer review the whole Epic delta before PR #119 update/push.

## Rollback / Compatibility

- Rollback is to keep write-scoped delegated authoring disabled for this pilot and continue v0 discussions/manual integration workflow.
- Compatibility requires preserving completed v0 issue plans/reports and prerequisite v1 issue plans/reports as historical evidence.
- Fallback draft evidence is review/planning input only. It must not enable implementation start, issue ready, issue finish, phase completion, or `authority: approved`.
- If host/Permission Profile evidence becomes fail-open, divergent, unavailable, or unverified, delegated canonical writes remain disabled and S02 evidence is retained only as proposal/fallback evidence.

## Docs Impact

S90 should classify docs impact as one of:

- `no-op`: current docs already describe proposal-only fallback, task manifest, Permission Profile fail-closed behavior, and manual path preservation.
- `follow-up`: provider docs/runtime behavior need durable change but are outside this pilot's no-provider-source scope.
- `amendment required`: completing `iss-00125` requires changing allowed paths, closure mapping, authority model, or fallback condition.

For the current S02 lock, expected docs impact is likely `no-op` or `follow-up`, not direct provider docs editing.

## Final Quality Gate

Before `iss-00125` can be reported complete, the orchestrator must have:

- S01 through S03, S90, and S99 closure rows closed in `Step Contract Closure`, `Test Contract Closure`, and `Closure Coverage`.
- Delegated Draft Evidence for both system-architect design fallback and implementation-planner plan fallback.
- No open decision ledger entries.
- No unauthorized changes to v0 issue reports/plans, prerequisite v1 issue reports/plans, provider source, runtime, tests, config, or GitHub state.
- `validate` and `sync` evidence recorded.
- final QA/code/spec reviewer pass evidence.
- PR Delivery Gate and Merge Preparation Gate evidence if moving toward issue finish.
- post-final-commit clean evidence recorded externally by the orchestrator.

## Plan Blockers

- none.

## Integration Notes for Main Orchestrator

Save this proposal as the locked S02 fallback plan draft path and integrate only the evidence summary into `report.md`; do not promote this draft to canonical `plan.md`. S02 `tc-004` can reference this draft as produced once saved. S02 as a whole still needs the paired system-architect fallback design draft for `tc-003`.

## Delegated Draft Evidence

```yaml
role: spec-dock-implementation-planner
phase: plan
scope: iss-00125
source_artifacts_read:
  - spec-dock/active/context-pack.md
  - spec-dock/active/issue/requirement.md
  - spec-dock/active/issue/design.md
  - spec-dock/active/issue/plan.md
  - spec-dock/active/issue/report.md
  - spec-dock/active/epic/requirement.md
  - spec-dock/active/epic/design.md
  - spec-dock/active/epic/plan.md
  - spec-dock/active/epic/report.md
  - .agents/skills/spec-dock-implementation-planner/SKILL.md
  - spec-dock/docs/workflow_issue.md
  - spec-dock/docs/authoring/issue-plan.md
  - spec-dock/docs/workflow_spec_authoring.md
  - spec-dock/docs/phase_plan.md
draft_artifact_path: spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/issues/iss-00125-authority-aware-delegated-authoring-dogfooding-pilot/discussions/20260524t000000z-02-disc-fallback-implementation-planner-plan-draft.md
draft_status: produced
authority: proposed
integration_notes: S02 fallback discussion draft only; closes tc-004 evidence after orchestrator saves artifact and records no-promotion/no-canonical-write statement. Does not close tc-003, S02 reviewer gate, S03, S90, S99, or G10.
rejected_portions: canonical plan.md write, report.md edit, provider/runtime/test/config edit, GitHub mutation, phase promotion, reviewer-pass claim, implementation-readiness claim
blockers: none
permission_profile_task_manifest_verification_result: Task Manifest Lock says pilot_target_issue_id none; no safe canonical pilot target; write-scoped canonical authoring disabled; source hash 608a7e994e37e2ee2d095eb96f6700ebe1f62e1b verified as current HEAD; existing report.md dirty state was not edited by this role.
previous_phase_artifacts_edited: none
final_authority_claimed: no
```
