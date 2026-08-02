---
種別: disc
ID: "20260730t130735z-disc"
タイトル: "PR Repair Unit U002 Candidate Output Directory TOCTOU"
状態: "proposed"
作成者: "iwasawayuuta"
最終更新: "2026-07-30"
親: ["iss-00334"]
関連: []
authority: "adopted"
derived_from:
  - "20260730t115808z-pr-repair-batch-pr-351-repair-batch.md R002/F002/S002"
  - "20260730t130735z-01-pr-351-s002-p1-repair-chatgpt-consultation.md"
  - "20260730t134843z-pr-351-s003-race-closure-chatgpt-consultation.md"
  - "20260730t143143z-pr-351-s005-atomic-stage-state-validation-chatgpt-followup.md"
reflected_to:
  - "bounded dev-coder handoff U002"
---

# U002 Candidate Output Directory TOCTOU

## Contract

- source_batch: `20260730t115808z-pr-repair-batch-pr-351-repair-batch.md`
- unit_id: `U002`
- root_cause_family: `issue-planning-candidate.output-directory-toctou`
- covered_ids: `R002`
- source_links: PR Review `4818771681`, comment `3682683838`
- failure_class: `review_feedback:output-directory-toctou`
- decided_priority: `P1`
- merge_blocking: `yes`
- disposition: `fix-now`

## Validity Analysis

`build_and_publish_candidate()` validates a directory identity but later uses its pathname for staging, publication, and cleanup. Renaming the validated directory and replacing the pathname can cause a write before the later revalidation. This violates the external-output and repository-mutation safety boundary.

## Need-To-Fix Decision

Fix in this PR. Repeated pathname checks cannot prevent the last-check-to-write race.

## Root Cause

Publication authority is a mutable pathname rather than the validated directory object.

## Options Considered

- additional pathname revalidation: rejected.
- global directory lock: rejected as broader lifecycle machinery.
- long-lived descriptor through Oracle transport: rejected as unnecessary ownership expansion.
- reopen at publication entry, verify identity, then use descriptor-relative operations: adopted.

## Recommended Design

- keep `OutputDirectoryGuard` and application API unchanged.
- at publisher entry, safely open the output directory and require its `fstat` identity to match the guard before any write.
- create the private stage directory and ZIP file with `dir_fd`, no-follow, and exclusive creation.
- construct/fsync/read exact ZIP bytes through the opened file; review through the existing byte-snapshot helper.
- publish no-replace using descriptor-relative Darwin/Linux primitives.
- cleanup only known private staged entries relative to captured descriptors; do not use pathname recursive deletion.
- preserve Candidate bytes/schema/identity, collision mapping, and unsupported-platform fail-closed behavior.

## Implementation Plan

1. Add deterministic Red tests for pre-capture path replacement, post-capture replacement, collision entries, and failure cleanup isolation.
2. Modify only provider candidate infra plus focused tests.
3. Do not edit dogfood projection directly; Main performs official update after U002/U003 integration.
4. Keep public call signatures unless a private helper split is required for fd-backed ZIP creation.

## Validation Plan

- `uv run pytest tests/unit/infra/test_issue_planning_candidate.py`
- deterministic ZIP bytes and collision regression
- Darwin/Linux error mapping through current platform-aware tests
- provider/dogfood byte parity after Main update
- full verification in S002 integration

## Out of Scope

- Oracle, Prompt, browser, wrapper, local Oracle configuration
- Candidate control schema/content
- apply/review/Human-decision behavior
- global locking or lifecycle redesign
- F004

## Implementation Result

- S005でprivate stage directoryを廃止し、validated output descriptor直下のrandom hidden staged ZIPを`openat(O_CREAT|O_EXCL|O_NOFOLLOW)`でatomic create/openする。成功fdがownershipの起点である。
- staged ZIPはopen descriptor、`st_dev`、`st_ino`へbindし、write／fsync／read／review／identity derivationをdescriptor／captured bytesだけで行う。
- publish直前にrandom staged filenameとopen descriptorが同じregular fileを示すことを再確認し、source／destination parentの双方にvalidated output descriptorを使ってno-replace publishする。
- failure cleanupはsame-objectの場合だけrandom staged nameを`unlink`する。renamed owned file／replacementは探索・削除しない。
- public schema、deterministic ZIP bytes、Candidate identity、no-replace publication、Darwin／Linux platform contractは変更していない。

## Verification Result

- S005 exact atomic-stage/replacement/collision tests: `4 passed`
- full candidate infra module: `29 passed`
- targeted Ruff check／format: PASS
- targeted mypy: PASS
- `git diff --check`: PASS

## Commit Evidence

Pending.

## Re-observation Result

Pending.

## Residual Risk / Follow-up

- final identity checkと`rename`／`unlink` syscallの間の極小raceは、今回採用したthreat modelでは許容する。observed replacementは常にfail closedし、第三者entryを削除しない。
- renamed owned staged fileは安全のため探索・削除せず、一時stateとして残り得る。
