---
種別: disc
ID: "20260619t113206z-disc"
タイトル: "PR Repair Unit U001"
状態: "proposed"
作成者: "iwasawayuuta"
最終更新: "2026-06-19"
親: ["iss-00211"]
関連: []
authority: "proposed"
derived_from: []
reflected_to: []
---

# 20260619t113206z-disc PR Repair Unit U001

## source_batch
- `20260619t113109z-pr-repair-batch-pr-repair-batch.md`

## unit_id
- U001

## covered_ids
- I001

## source_links
- PR: https://github.com/chemitaro/spec-dock/pull/217
- Provider CI run: https://github.com/chemitaro/spec-dock/actions/runs/27822529397
- Failed job: https://github.com/chemitaro/spec-dock/actions/runs/27822529397/job/82338831912

## failure_class
- `check_failure:provider-tests`

## risk_class
- `blocking`

## disposition
- `fix-now`

## Validity Analysis
- The failure is valid. `provider-tests` failed on the PR merge ref for head `881ef59eb1e1f95b9bfdf5a61eb9f7d25dabbb13`.
- The failed test is `TestInitUpdate.test_checked_in_dogfooding_initiatives_do_not_ship_legacy_deps_json`.
- The assertion reports one extra checked-in `.meta.json` path from base `main`: `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00158-agent-workflow-pdca-hardening/issues/iss-00214-pr-observation-review-target-state/.meta.json`.

## Need-To-Fix Decision
- `need_to_fix: yes`
- Required Provider CI cannot remain failed for merge-prepared status.
- This is not review feedback and not an optional check waiver candidate.

## Root Cause
- The Issue 211 branch was cut before base `main` added Issue 214 scaffold metadata.
- GitHub Actions tests the PR merge ref, so the merge ref includes Issue 214 files from `main` while this branch's test snapshot in `tests/unit/infra/test_init_update.py` has not been reconciled with that base advancement.

## Options Considered
- Option A: rerun Provider CI only.
  - Rejected because the snapshot mismatch is deterministic on the merge ref.
- Option B: ignore as base failure.
  - Rejected because the PR merge-prepared predicate requires no required check failures.
- Option C: merge or otherwise reconcile `origin/main`, update the checked-in dogfooding snapshot, run focused verification, commit, push, and re-observe.
  - Selected as the smallest repair consistent with the failed test.

## Recommended Design
- Reconcile the branch with `origin/main`.
- Preserve Issue 211 changes.
- Update only the checked-in dogfooding meta snapshot required by the failing test unless merge reconciliation naturally brings in Issue 214 scaffold files.

## Implementation Plan
1. Ensure working tree contains only repair batch/unit artifacts before reconciliation.
2. Merge or otherwise reconcile `origin/main` into `iss-00211-epic-execution-coordinator-skill`.
3. If `tests/unit/infra/test_init_update.py` still lacks the Issue 214 `.meta.json` entry, add it in the sorted `_CHECKED_IN_DOGFOODING_META_JSON_PATHS` tuple.
4. Run the focused failing test: `uv run pytest tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_initiatives_do_not_ship_legacy_deps_json`.
5. Run `git diff --check`.
6. Commit and push the repair.
7. Re-run PR observation for the new latest head SHA.

## Validation Plan
- Focused failing test must pass.
- `git diff --check` must pass.
- PR re-observation must match the new latest head SHA and report no required check failure.

## Implementation Result
- Merged `origin/main` into `iss-00211-epic-execution-coordinator-skill`, bringing in the Issue 214 scaffold from base `main`.
- Added the Issue 214 `.meta.json` path to `_CHECKED_IN_DOGFOODING_META_JSON_PATHS`.
- Added the same path with an empty dependency list to `_CHECKED_IN_DOGFOODING_DEPENDS_ON_BY_META_PATH`.
- Focused failing test passed: `uv run pytest tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_initiatives_do_not_ship_legacy_deps_json` -> `1 passed`.
- `git diff --check` passed.

## Commit Evidence
- pending repair commit

## Re-observation Result
- pending after repair commit push

## Residual Risk / Follow-up
- If `main` advances again with additional dogfooding scaffold metadata before merge, the same snapshot reconciliation pattern may be needed again.
