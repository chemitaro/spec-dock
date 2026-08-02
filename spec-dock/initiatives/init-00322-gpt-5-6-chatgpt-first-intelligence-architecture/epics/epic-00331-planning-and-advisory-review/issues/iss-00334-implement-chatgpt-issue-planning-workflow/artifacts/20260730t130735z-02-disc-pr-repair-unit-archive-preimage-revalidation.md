---
種別: disc
ID: "20260730t130735z-02-disc"
タイトル: "PR Repair Unit U003 Archive Preimage Revalidation"
状態: "proposed"
作成者: "iwasawayuuta"
最終更新: "2026-07-30"
親: ["iss-00334"]
関連: []
authority: "adopted"
derived_from:
  - "20260730t115808z-pr-repair-batch-pr-351-repair-batch.md R003/F003/S002"
  - "20260730t130735z-01-pr-351-s002-p1-repair-chatgpt-consultation.md"
  - "20260730t134843z-pr-351-s003-race-closure-chatgpt-consultation.md"
  - "20260730t141210z-pr-351-s004-backed-up-recovery-chatgpt-followup.md"
  - "20260730t143143z-pr-351-s005-atomic-stage-state-validation-chatgpt-followup.md"
  - "20260730t145257z-pr-351-s006-no-transaction-state-chatgpt-followup.md"
reflected_to:
  - "bounded dev-coder handoff U003"
---

# U003 Archive Preimage Revalidation

## Contract

- source_batch: `20260730t115808z-pr-repair-batch-pr-351-repair-batch.md`
- unit_id: `U003`
- root_cause_family: `issue-planning-apply.archive-preimage-revalidation`
- covered_ids: `R003`
- source_links: PR Review `4818771681`, comment `3682683856`
- failure_class: `review_feedback:archive-preimage-revalidation`
- decided_priority: `P1`
- merge_blocking: `yes`
- disposition: `fix-now`

## Validity Analysis

Archive mode bypasses the existing git-bound stale comparison. Canonical targets and companion can drift after application preflight; later transaction snapshots may be accepted as rollback baselines and overwritten without matching the Human-bound operation preimage.

## Need-To-Fix Decision

Fix in this PR. A stale concurrent edit or create must be preserved and rejected before managed mutation.

## Root Cause

Archive transaction-boundary snapshots are not compared to the operation's exact preimage evidence. Companion snapshot timing additionally leaves a creation/change window.

## Options Considered

- run only the git-bound stale helper: rejected because companion existence/content and rollback snapshot binding remain uncovered.
- accept fresh snapshot as baseline or detect after write: rejected because it loses Human/Review binding or concurrent bytes.
- add schema fields: rejected; expected canonical evidence exists and optional companion state is derivable from `expected_head`.
- compare all relevant preimages at one mutation boundary: adopted.

## Recommended Design

- verify `pre_apply_document_bytes` correspond to `pre_apply_target_blob_oids` during operation creation without changing serialization/schema.
- derive expected companion presence/blob/bytes from `expected_head`, distinguishing absence from Git failure.
- snapshot canonical targets and companion together after prerequisite state snapshots and before any managed write or transaction backup.
- compare existence, bytes, and blob OIDs to operation evidence.
- on mismatch, return existing `stale/apply_target_changed`; do not write, backup, restore, validate, sync, commit, or push.
- persist only already-matched snapshots as rollback authority.
- keep git-bound behavior and operation ID/schema unchanged.

## Implementation Plan

1. Add Red tests for post-preflight canonical edit, absent companion create, tracked companion change, exact tracked companion no-op, and incoherent operation evidence.
2. Modify only provider apply infra plus focused unit/integration tests.
3. Do not edit dogfood projection directly; Main performs official update after U002/U003 integration.
4. Reuse existing closed result/reason and helper patterns; no public contract expansion.

## Validation Plan

- `uv run pytest tests/unit/infra/test_issue_planning_apply.py`
- explicit permission integration: `uv run pytest --run-full-regression tests/integration/test_issue_planning_apply.py`
- existing archive/git-bound happy, rollback, recovery, and publication paths
- provider/dogfood byte parity after Main update
- full verification in S002 integration

## Out of Scope

- repository-wide locking and post-snapshot multiwriter serialization
- operation schema/version or Human decision changes
- Candidate, review, Prompt, Oracle, browser, wrapper, local Oracle configuration
- F004

## Implementation Result

- `after_operation_recorded`直後、`mutation_started`／`MUTATING`／最初のmanaged writeより前にbranch、HEAD、canonical三文書、companionをcaptured `FileSnapshot`へ再照合する。
- existence、bytes、mode、non-regular／symlink／read failureを含む不一致は既存`stale/apply_target_changed`へ閉じる。
- drift時はbackupをrestoreせずdiscardし、directory sync後にstateを`OPERATION_RECORDED`へ戻す。cleanup失敗は`recovery_required/restore_mismatch`。
- surviving `BACKED_UP` recoveryはdiscard-onlyであり、concurrent bytesをpreimageへ戻さない。`MUTATING`以降の既存rollback semanticsは維持する。
- S004で`BACKED_UP` recoveryはdurable backup snapshotとcurrent targetsを比較し、actual driftだけを`stale/apply_target_changed`、no driftを既存`rolled_back/planning_commit_failed`へ分類する。どちらもrestoreしない。
- S005でdurable stateをclosed vocabularyへ制限し、transaction recoveryは`BACKED_UP`または`MUTATING`／`VALIDATED`／`SYNCED`／`STAGED`だけを許可する。unknown／invalid combinationはdestructive helper前に`recovery_required/restore_mismatch`へ閉じ、evidenceを保持する。
- S006でcommit／transaction／no-transaction routeをattempt記録前に分類し、transaction不在で新しい実行を開始できるstateを`OPERATION_RECORDED`／`ROLLED_BACK`だけに限定する。invalid state／orphan publicationはevidenceを書き換えず停止する。
- exact restore成功後はtransaction absenceとoperation-directory durabilityを確認し、stateを`ROLLED_BACK`へatomic writeしてからだけ`rolled_back`を返す。
- public schema、operation ID、status／reason contractは変更していない。

## Verification Result

- exact hook canonical edit／absent companion create、`BACKED_UP` drift／no-drift、unknown／known-invalid durable stateをRed→Greenで検証した。
- apply unit: `19 passed`
- explicit full-regression apply integration: `60 passed`
- targeted Ruff check／format: PASS
- `git diff --check`: PASS

## Commit Evidence

Pending.

## Re-observation Result

Pending.

## Residual Risk / Follow-up

- 最終再比較後からmanaged writeまでの一般的な外部multiwriter raceは残る。repository-wide lock／CASは今回のdefect-only scope外である。
- sequential multi-file snapshotsはOS-atomic repository snapshotではなく、accepted boundary後はsingle-writer前提を維持する。
