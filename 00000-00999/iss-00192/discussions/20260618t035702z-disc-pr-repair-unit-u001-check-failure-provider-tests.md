---
種別: disc
ID: "20260618t035702z-disc"
タイトル: "PR Repair Unit U001"
状態: "draft | proposed | archived"
作成者: "iwasawayuuta"
最終更新: "2026-06-18"
親: ["iss-00192"]
関連: []
authority: "proposed"
derived_from: []
reflected_to: []
---

# 20260618t035702z-disc PR Repair Unit U001

## source_batch

- `20260618t035621z-pr-repair-batch`

## unit_id

- U001

## covered_ids

- I001
- I002

## source_links

- PR: https://github.com/chemitaro/spec-dock/pull/206
- Observation result: `/private/tmp/spec-dock-pr-206-observation/result.json`
- Failed run: https://github.com/chemitaro/spec-dock/actions/runs/27735228335/job/82050572340
- Duplicate failed run: https://github.com/chemitaro/spec-dock/actions/runs/27735222347/job/82050555742

## failure_class

- `check_failure:provider-tests`

## risk_class

- `blocking`

## disposition

- `fix-now`

## Validity Analysis

- The observation result is for latest head `03b6953ffdfa24835a71cd925f1fc7ec9357be20`.
- Both Provider CI jobs failed in `TestInitUpdate.test_checked_in_dogfooding_initiatives_do_not_ship_legacy_deps_json`.
- The failure is valid because the checked-in `spec-dock/initiatives` tree contains `.meta.json` files that are absent from `_CHECKED_IN_DOGFOODING_META_JSON_PATHS`.
- After updating that tuple, the same test exposed the paired `depends_on` baseline mismatch in `_CHECKED_IN_DOGFOODING_DEPENDS_ON_BY_META_PATH`.

## Need-To-Fix Decision

- Need to fix: yes.
- Reason: `provider-tests` is a required PR check and the PR cannot be merge-prepared while it fails.

## Root Cause

- The dogfooding metadata cutover snapshot in `tests/unit/infra/test_init_update.py` lagged the checked-in `spec-dock/initiatives` tree.
- This issue's main implementation added runtime behavior for `deps-raw.puml`, but the full provider suite also verifies the broader dogfooding metadata snapshot. The stale snapshot was already visible locally as the only remaining broad `tests/unit` failure.

## Options Considered

- Leave as residual risk: rejected because required CI remains red.
- Remove checked-in dogfooding metadata: rejected because it would mutate product dogfooding data outside the repair scope.
- Update snapshot baselines from the current tree: selected because the failing test is explicitly a cutover snapshot guard and this is the smallest repair.

## Recommended Design

- Regenerate `_CHECKED_IN_DOGFOODING_META_JSON_PATHS` from `spec-dock/initiatives/**/*.meta.json`.
- Regenerate `_CHECKED_IN_DOGFOODING_DEPENDS_ON_BY_META_PATH` from the same files' `depends_on` values.
- Do not change runtime implementation, shipped assets, or dogfooding node metadata.

## Implementation Plan

- Update `tests/unit/infra/test_init_update.py` snapshot constants only.
- Run the failing focused test.
- Run broader relevant tests before pushing.

## Validation Plan

- `uv run pytest tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_initiatives_do_not_ship_legacy_deps_json -q`
- `uv run pytest tests/unit/infra/test_init_update.py -q`
- `uv run pytest tests/unit -q`
- Re-observe PR #206 after commit and push.

## Implementation Result

- `_CHECKED_IN_DOGFOODING_META_JSON_PATHS` was updated to 129 current `.meta.json` paths.
- `_CHECKED_IN_DOGFOODING_DEPENDS_ON_BY_META_PATH` was updated from the current `depends_on` values.
- Focused failing test passed locally: `1 passed in 1.21s`.
- `test_init_update.py` passed locally: `439 passed in 259.88s`.
- `tests/unit` passed locally: `680 passed in 233.40s`.
- `./spec-dock/scripts/spec-dock validate` passed: `spec-dock: ok (validate) nodes=129`.
- `git diff --check` passed.

## Commit Evidence

- Pending.

## Re-observation Result

- Pending after commit and push.

## Residual Risk / Follow-up

- The snapshot repair covers dogfooding metadata outside the deps-raw implementation surface. This is acceptable for PR preparation because the failure is a required check and the repair only updates test baselines to checked-in data.
