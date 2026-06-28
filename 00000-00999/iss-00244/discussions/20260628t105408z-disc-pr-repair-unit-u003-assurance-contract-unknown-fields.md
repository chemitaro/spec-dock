---
種別: disc
ID: "20260628t105408z-disc"
タイトル: "PR Repair Unit U003 Assurance Contract Unknown Fields"
状態: "implemented"
作成者: "iwasawayuuta"
最終更新: "2026-06-28"
親: ["iss-00244"]
関連: []
authority: "proposed"
derived_from: []
reflected_to: []
---

# 20260628t105408z-disc PR Repair Unit U003 Assurance Contract Unknown Fields

## source_batch
- `20260628t105306z-pr-repair-batch`

## unit_id
- U003

## covered_ids
- I005

## source_links
- PR #245 review thread: `PRRT_kwDOQ99OK86Myv-f`
- Review comment: `3487750618`
- File: `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/assurance_store.py`

## failure_class
- `review_feedback:assurance-contract-schema`

## risk_class
- `blocking`

## disposition
- `fix-now`

## Validity Analysis
- Valid. A valid `.assurance.json` with unknown root keys can be read, but rewrite through `canonical_json_bytes(contract)` drops those keys.

## Need-To-Fix Decision
- Fix now. Silent field loss in a public contract surface is a merge-blocking data-loss risk.

## Root Cause
- `_contract_from_payload` maps known fields into the dataclass without rejecting extra root keys.

## Options Considered
- Preserve unknown fields through the dataclass and canonical serialization: larger schema change and unclear ownership.
- Reject unknown root fields consistently: smaller and fail-closed, fits strict contract semantics.

## Recommended Design
- Reject unknown root fields with `invalid_schema` diagnostics before constructing `AssuranceContract`.
- Add unit coverage for hidden `.assurance.json` with an extra root key.

## Implementation Plan
- Patch provider and dogfooding `assurance_store.py`.
- Add focused `tests/unit/infra/test_assurance_store.py` coverage.
- Run focused assurance tests.

## Validation Plan
- `uv run pytest tests/unit/infra/test_assurance_store.py tests/unit/application/test_assurance.py tests/cli_runtime/test_assurance.py`
- Final PR re-observation after all repair units.

## Implementation Result
- Provider and dogfooding assurance stores now reject unknown `.assurance.json` root fields during contract parsing.
- Added `test_contract_with_unknown_root_field_is_invalid` to verify an extra root field produces `invalid_schema` with `unknown_root_field:<key>` detail.

## Commit Evidence
- pending until commit.

## Re-observation Result
- pending after push.

## Residual Risk / Follow-up
- Future additive root metadata requires explicit schema support.

## Validation Result
- `uv run pytest tests/cli_runtime/test_workflow.py tests/cli_runtime/test_workflow_context_routing.py tests/unit/infra/test_assurance_store.py tests/unit/infra/test_init_update.py -k 'issue_244_wait_script_does_not_define_required_check_rollup_reader or issue_232_protected_domain or blocker_policy_no_action or status_rollup_failure_is_ignored or status_rollup_running_is_ignored or draft_placeholder_plan or unknown_root_field'` -> 15 passed.
- `uv run pytest tests/cli_runtime/test_workflow.py tests/cli_runtime/test_workflow_context_routing.py tests/unit/infra/test_assurance_store.py tests/unit/application/test_assurance.py tests/cli_runtime/test_assurance.py` -> 43 passed.
- `uv run pytest tests/unit/infra/test_init_update.py` -> 521 passed.
- `make lint` -> passed.
- `git diff --check` -> passed.
