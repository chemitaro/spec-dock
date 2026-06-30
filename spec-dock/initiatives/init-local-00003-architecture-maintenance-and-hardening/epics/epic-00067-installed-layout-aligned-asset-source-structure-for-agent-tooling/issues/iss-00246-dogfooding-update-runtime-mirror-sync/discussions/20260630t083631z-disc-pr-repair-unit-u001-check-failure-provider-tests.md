---
種別: disc
ID: "20260630t083631z-disc"
タイトル: "PR Repair Unit U001"
状態: "proposed"
作成者: "iwasawayuuta"
最終更新: "2026-06-30"
親: ["iss-00246"]
関連: []
authority: "proposed"
derived_from: []
reflected_to: []
---

# 20260630t083631z-disc PR Repair Unit U001

## source_batch

- `20260630t083605z-pr-repair-batch`

## unit_id

- U001

## covered_ids

- INV-001

## source_links

- PR: https://github.com/chemitaro/spec-dock/pull/249
- Observation result: `/private/tmp/spec-dock-pr-249-observation-1/result.json`
- CI job: https://github.com/chemitaro/spec-dock/actions/runs/28431280075/job/84246330373

## failure_class

- `check_failure:provider-tests`

## risk_class

- blocking

## disposition

- fix-now

## Validity Analysis

The failure is valid. PR observation reported `overall_status=failed`,
`recommended_next_action=fix_ci`, and the GitHub Actions log shows `make lint`
failing in `ruff format check` for `tests/unit/infra/test_init_update.py`.

## Need-To-Fix Decision

Fix now. `provider-tests` is a required CI surface for this repository and the
failure is deterministic.

## Root Cause

Issue 246 test additions were correct behaviorally, but the final file shape did
not match `ruff format` output. The failure is formatting-only; no production
runtime behavior failed in CI evidence.

## Options Considered

- Run `ruff format` on `tests/unit/infra/test_init_update.py`.
- Manually apply the exact formatting changes shown in the CI log.

## Recommended Design

Apply a single-file formatting repair with no logic changes. Keep the repair
commit scoped to `tests/unit/infra/test_init_update.py` plus this PR repair
evidence.

## Implementation Plan

1. Format `tests/unit/infra/test_init_update.py`.
2. Run the single-file format check.
3. Run focused Issue 246 tests if practical.
4. Commit, push, and re-observe the latest head SHA.

## Validation Plan

- `uv run ruff format --check tests/unit/infra/test_init_update.py`
- Focused Issue 246 regression tests:
  - `test_update_refreshes_stale_runtime_mirror_and_preserves_user_data`
  - `test_issue_246_isolated_wheel_update_refreshes_stale_runtime_file`
  - `test_checked_in_dogfooding_runtime_mirror_match_provider_assets`

## Implementation Result

- Applied formatting-only changes to `tests/unit/infra/test_init_update.py`.
- No production code, PR body, or non-repair issue docs were changed by the repair worker.
- Parent recorded this repair result in `report.md` and in the PR repair batch.

## Commit Evidence

- Pending commit after repair evidence integration.

## Re-observation Result

- Pending.

## Residual Risk / Follow-up

- Latest-head CI/review re-observation is still required after commit and push.
