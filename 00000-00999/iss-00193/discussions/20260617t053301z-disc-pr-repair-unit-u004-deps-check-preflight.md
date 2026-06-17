---
種別: disc
ID: "disc-20260617t053301z-pr-repair-unit-u004-deps-check-preflight"
タイトル: "PR #194 U004 deps check raw preflight repair"
状態: "implemented"
作成者: "codex"
最終更新: "2026-06-17"
親: ["iss-00193"]
関連: ["https://github.com/chemitaro/spec-dock/pull/194", "disc-20260617t041630z-pr-repair-batch"]
authority: "proposed"
derived_from: ["/private/tmp/iss-00193-pr194-snapshot-latest/result.json"]
reflected_to: []
---

# PR #194 U004 deps check raw preflight repair

## Source Finding

- Inventory: I005
- Review comment: 3425775991
- Review thread: PRRT_kwDOQ99OK86KG9x9
- Status: valid / blocking / fix-now

## Objective

Ensure `deps check` does not report readiness when the raw node dependency graph contains structural errors, including empty-container cycles that disappear from the compiled issue dependency map.

## Scope

- Provider runtime source of truth:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/check_deps.py`
- Dogfooding runtime mirror if provider runtime source changes:
  - `spec-dock/scripts/spec_dock_runtime/application/check_deps.py`
- Focused tests:
  - `tests/unit/application/test_check_deps.py`
  - or `tests/cli_runtime/test_deps.py` if the existing CLI fixture is the clearer regression surface

## Constraints

- Preserve existing readiness semantics when raw node validation passes.
- Preserve compatibility with older test ports by using an optional `load_node_dependency_resolutions` lookup if needed.
- Raw structural errors should stop readiness computation before a misleading ready result is returned.
- Do not resolve GitHub review threads manually.

## Required Regression Shape

Create an empty-container raw cycle, for example:

- `epic-00001 -> epic-00002`
- `epic-00002 -> epic-00001`

Expected result: `deps check` returns a failure/non-ready result with raw cycle evidence instead of ready.

## Verification

- Run the focused `deps check` regression.
- Run the existing focused deps or application check suite affected by this change.

## Completion Criteria

- `deps check` shares the same raw node dependency preflight used by validate/sync/mutation where available.
- Existing ready/no-dependency behavior remains green.
- Changed files and test evidence are reported back to the orchestrator.

## Implementation Result

- Status: implemented
- Changed files:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/check_deps.py`
  - `spec-dock/scripts/spec_dock_runtime/application/check_deps.py`
  - `tests/unit/application/test_check_deps.py`
- Evidence:
  - Red: `uv run pytest tests/unit/application/test_check_deps.py -k raw_node_preflight` failed before implementation with `DID NOT RAISE <class 'RuntimeError'>`.
  - Green: `uv run pytest tests/unit/application/test_check_deps.py` -> `8 passed`.
  - Integrated focused bundle after all U003/U004/U005 repairs: `uv run pytest tests/unit/domain/test_deps.py tests/unit/application/test_check_deps.py tests/cli_runtime/test_runtime_delete_s13.py` -> `69 passed`.
- Reviewer result: fresh code-reviewer final pass; no findings.
- Re-observation Result: pending push / PR re-observation.
