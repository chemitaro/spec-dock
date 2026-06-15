---
種別: disc
ID: "20260616t024410z-disc-pr-repair-unit-u001-provider-tests-snapshot-drift"
タイトル: "PR repair unit U001: provider-tests snapshot drift"
状態: "proposed"
作成者: "iwasawayuuta"
最終更新: "2026-06-16"
親: ["iss-00186"]
関連: ["#189"]
authority: "proposed"
derived_from: ["20260616t024310z-disc-pr-repair-batch.md"]
reflected_to: []
---

# PR repair unit U001: provider-tests snapshot drift

## source_batch

- `20260616t024310z-disc-pr-repair-batch.md`

## unit_id

- U001

## covered_ids

- I001

## source_links

- PR: https://github.com/chemitaro/spec-dock/pull/189
- Failed run: https://github.com/chemitaro/spec-dock/actions/runs/27564309099/job/81484125715
- Observation result: `/private/tmp/iss-00186-pr-observation/result.json`

## failure_class

- check_failure:provider-tests

## risk_class

- blocking

## disposition

- fix-now

## Validity Analysis

The failure is valid. PR event `provider-tests` failed on `TestInitUpdate.test_checked_in_dogfooding_initiatives_do_not_ship_legacy_deps_json` because the merge-commit test state includes one additional `.meta.json` path from `origin/main`: `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00158-agent-workflow-pdca-hardening/issues/iss-00187-actions-pr-observation-ci-state/.meta.json`.

## Need-To-Fix Decision

Fix now. The merge-prepared predicate requires no check failure remains, and waiving provider CI would hide a snapshot baseline drift.

## Root Cause

`origin/main` advanced after this branch's snapshot baseline was updated. The push workflow passed against the branch head alone, while the PR workflow tested the merge state with base `main` and saw the new `iss-00187` dogfooding issue metadata.

## Options Considered

- Rerun CI only: rejected because the assertion mismatch is deterministic while base remains ahead.
- Merge or rebase `origin/main` into the branch and update snapshot baselines: selected.
- Waive the failing check: rejected because this is provider CI and merge-prepared cannot be claimed with a live failure.

## Recommended Design

Bring the branch up to date with `origin/main` and update only the dogfooding snapshot baseline fields that are required for the new checked-in `iss-00187` metadata to pass. Avoid unrelated refactors or workflow wording changes.

## Implementation Plan

1. Confirm clean worktree and current branch.
2. Merge `origin/main` into `iss-00186-harden-issue-execution-step-gates` without changing issue implementation commits.
3. Inspect `iss-00187` `.meta.json` and `tests/unit/infra/test_init_update.py` snapshot baseline.
4. Update the checked-in dogfooding `.meta.json` path baseline and `depends_on` baseline only if the merge does not already provide the correct expectation.
5. Run `uv run pytest tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_initiatives_do_not_ship_legacy_deps_json`.
6. Run `./spec-dock/scripts/spec-dock validate`.
7. Return changed files, verification output, and `No material implementation decisions beyond the approved repair unit.` or a Ledger Note.

## Validation Plan

- `uv run pytest tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_initiatives_do_not_ship_legacy_deps_json`
- `./spec-dock/scripts/spec-dock validate`
- Post-repair PR re-observation for latest head SHA.

## Implementation Result

- Implemented in worktree before commit:
  - Merged `origin/main` into the branch with `git merge --no-commit --no-ff origin/main` so `iss-00187` comes from the base history instead of PR-unique copied files.
  - Added `iss-00187-actions-pr-observation-ci-state/.meta.json` to `_CHECKED_IN_DOGFOODING_META_JSON_PATHS`.
  - Added the same `.meta.json` path with `[]` to `_CHECKED_IN_DOGFOODING_DEPENDS_ON_BY_META_PATH`.
  - Verified `git diff --name-status origin/main...HEAD` no longer reports `iss-00187` files as PR-unique diff.
  - `code-reviewer` (`019ecc68-b04b-7fe2-a35d-7bb129570879`) returned `review_status: pass` with no blocking findings.

## Commit Evidence

- pending until orchestrator commit.

## Re-observation Result

- pending

## Residual Risk / Follow-up

- Snapshot can drift again if `main` gains another dogfooding node before merge.
