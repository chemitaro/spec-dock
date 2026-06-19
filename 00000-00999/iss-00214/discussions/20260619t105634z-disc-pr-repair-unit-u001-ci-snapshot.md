---
種別: disc
ID: "20260619t105634z-disc"
タイトル: "PR Repair Unit U001 CI Snapshot"
状態: "draft | proposed | archived"
作成者: "iwasawayuuta"
最終更新: "2026-06-19"
親: ["iss-00214"]
関連: []
authority: "proposed"
derived_from: []
reflected_to: []
---

# 20260619t105634z-disc PR Repair Unit U001 CI Snapshot

## source_batch
- `20260619t105436z-pr-repair-batch`

## unit_id
- U001

## covered_ids
- INV-001

## source_links
- PR: https://github.com/chemitaro/spec-dock/pull/216
- GitHub Actions run: `27820892612`
- GitHub Actions job: `82333463397`
- Local failing surface: `tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_initiatives_use_meta_json_dependencies`

## failure_class
- `check_failure:provider-tests`

## risk_class
- `blocking`

## disposition
- `fix-now`

## Validity Analysis
- `Provider CI / provider-tests` failed on the checked-in dogfooding metadata cutover snapshot.
- The observed tree contains `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00158-agent-workflow-pdca-hardening/issues/iss-00214-pr-observation-review-target-state/.meta.json`.
- `_CHECKED_IN_DOGFOODING_META_JSON_PATHS` did not include that path when CI ran.

## Need-To-Fix Decision
- Fix now. The failure is in a required provider CI lane and blocks merge preparation.

## Root Cause
- The issue scaffold/import added checked-in dogfooding metadata for `iss-00214`, but the baseline constants in `tests/unit/infra/test_init_update.py` were not updated.

## Options Considered
- Update only `_CHECKED_IN_DOGFOODING_META_JSON_PATHS`.
- Update both `_CHECKED_IN_DOGFOODING_META_JSON_PATHS` and `_CHECKED_IN_DOGFOODING_DEPENDS_ON_BY_META_PATH`.

## Recommended Design
- Add the `iss-00214.../.meta.json` path to `_CHECKED_IN_DOGFOODING_META_JSON_PATHS`.
- Add the same path to `_CHECKED_IN_DOGFOODING_DEPENDS_ON_BY_META_PATH` with `[]`, because the issue metadata has no `depends_on` entries.

## Implementation Plan
- Patch `tests/unit/infra/test_init_update.py`.
- Run the focused failing test.
- If the focused test passes, update this unit and the repair batch evidence.
- Push the repair and re-observe PR #216 on the new head SHA.

## Validation Plan
- `uv run pytest tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_initiatives_do_not_ship_legacy_deps_json`
- PR latest-head observation after push.

## Implementation Result
- Added the `iss-00214.../.meta.json` path to `_CHECKED_IN_DOGFOODING_META_JSON_PATHS`.
- Added the same path to `_CHECKED_IN_DOGFOODING_DEPENDS_ON_BY_META_PATH` with `[]`.
- Focused test command used the actual local test name: `uv run pytest tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_initiatives_do_not_ship_legacy_deps_json`.
- Focused test result: passed, `1 passed in 0.08s`.

## Commit Evidence
- Pending.

## Re-observation Result
- Pending.

## Residual Risk / Follow-up
- Low. This repair is expected to affect only the checked-in dogfooding baseline test, not runtime behavior.
