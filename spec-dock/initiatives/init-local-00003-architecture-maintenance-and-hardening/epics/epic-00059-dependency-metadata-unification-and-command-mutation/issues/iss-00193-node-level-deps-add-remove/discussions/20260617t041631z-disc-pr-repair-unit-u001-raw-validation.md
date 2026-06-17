---
種別: disc
ID: "disc-20260617t041631z-pr-repair-unit-u001"
タイトル: "PR #194 repair unit U001 raw validation"
状態: "proposed"
作成者: "codex"
最終更新: "2026-06-17"
親: ["iss-00193"]
関連: ["https://github.com/chemitaro/spec-dock/pull/194"]
authority: "proposed"
derived_from: ["20260617t041630z-disc-pr-repair-batch.md"]
reflected_to: []
---

# PR #194 repair unit U001 raw validation

## source_batch
- `20260617t041630z-disc-pr-repair-batch.md`

## unit_id
- U001

## covered_ids
- I001
- I002

## source_links
- PR review comment 3425508533: `domain/deps.py` descendant expansion finding.
- PR review comment 3425508538: `reference_deps.md` validate/sync raw-cycle contract finding.

## failure_class
- `review_feedback:raw-validation`
- `review_feedback:validate-sync-contract`

## risk_class
- blocking

## disposition
- fix-now

## Validity Analysis
- I001 is valid. Current raw node validation checks direct dependency edges but does not include containment edges such as `epic -> child issue`; therefore an empty source container can depend on a target container whose descendant issue depends back on the source container, creating a future compiled cycle when a source child issue is later added.
- I002 is partially valid but should be fixed. The issue requirement primarily requires mutation-time fail-closed behavior, but the updated docs describe raw node graph validity strongly enough that `validate` / `sync` should reject pre-existing raw cycles instead of silently passing them.

## Need-To-Fix Decision
- Fix now. These findings affect the central safety guarantee chosen by the user: block raw dependency states that can become invalid when child issues are added later.

## Root Cause
- `validate_raw_node_dependency_graph` validates dependency edges only.
- `ensure_node_dependency_add_would_be_valid` relies on current issue expansion for compiled validation, so empty source containers produce no issue-level source edges.
- `validate_tree` and `sync_state` load compiled issue dependency maps but do not validate the all-node direct dependency graph.

## Options Considered
- Narrow docs to mutation-only: rejected because it weakens the fail-closed behavior the user explicitly selected.
- Add containment-edge-aware raw validation and call it from validate/sync preflight: selected as the smallest consistent repair.

## Recommended Design
- In `domain/deps.py`, make raw validation also detect dependency cycles through hierarchy containment by adding parent-to-child containment edges to the graph used for raw cycle validation.
- Keep the existing direct-edge self / ancestor / descendant checks.
- In `validate_tree.py`, after loading topology with `ports.deps_topology_reader`, also load all-node direct dependency resolutions when available and call `validate_raw_node_dependency_graph`.
- In `sync_state.py`, during preflight after artifact validation and before compiled dependency validation, call the same raw validation. Respect existing `--force` degradation behavior by routing raw validation failures into `deps_preflight_failed` when forced.
- Mirror provider runtime changes into `spec-dock/scripts/spec_dock_runtime/**`.

## Implementation Plan
1. Add a domain test proving raw validation rejects the future-cycle scenario: issue B under epic E2 has direct dependency to empty epic E1; candidate or raw map also contains `E1 -> E2`; validation must reject.
2. Add CLI/runtime tests proving existing raw cycles are rejected by `validate` and `sync` even when compiled issue expansion is empty.
3. Implement containment-aware raw validation.
4. Wire raw node validation into `validate_tree` and `sync_state` using `load_node_dependency_resolutions`.
5. Sync provider runtime changes to dogfooding mirror runtime files.
6. Run focused and relevant broader tests.

## Validation Plan
- `uv run pytest tests/unit/domain/test_deps.py`
- `uv run pytest tests/cli_runtime/test_deps.py -k "raw_cycle or validate or sync"`
- `uv run pytest tests/cli_runtime/test_deps.py tests/unit/domain/test_deps.py`
- `uv run pytest tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_runtime_mirror_match_provider_assets`
- `./spec-dock/scripts/spec-dock validate`
- `git diff --check`

## Implementation Result
- Implemented containment-edge-aware raw node dependency validation.
- Wired raw node dependency validation into `validate_tree` and `sync_state` preflight.
- Added optional-port compatibility for test doubles / alternate readers that implement only `load_issue_depends_on_map`; real bootstrap readers still run raw node validation via `load_node_dependency_resolutions`.
- Restored validate error priority so structural graph errors such as `issue parent_id mismatch` are reported before raw node validation errors.
- Synced provider runtime changes to dogfooding runtime mirror.
- Added tests for future-cycle-through-target-descendant, `validate` rejection of existing empty-container raw cycle, and `sync` rejection of the same structural error.
- Follow-up unit-suite failure caused by legacy `_StubDepsTopologyReader` was fixed without weakening real-runtime raw validation.

## Commit Evidence
- pending commit

## Re-observation Result
- pending push / re-observation

## Residual Risk / Follow-up
- Low. Local validation passed, including `uv run pytest` -> `1185 passed, 76 skipped`; PR re-observation remains required.
