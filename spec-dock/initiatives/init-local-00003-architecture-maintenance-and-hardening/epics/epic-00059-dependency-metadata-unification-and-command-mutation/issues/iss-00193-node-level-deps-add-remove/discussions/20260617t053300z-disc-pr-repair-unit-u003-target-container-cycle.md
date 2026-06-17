---
種別: disc
ID: "disc-20260617t053300z-pr-repair-unit-u003-target-container-cycle"
タイトル: "PR #194 U003 target container raw cycle repair"
状態: "implemented"
作成者: "codex"
最終更新: "2026-06-17"
親: ["iss-00193"]
関連: ["https://github.com/chemitaro/spec-dock/pull/194", "disc-20260617t041630z-pr-repair-batch"]
authority: "proposed"
derived_from: ["/private/tmp/iss-00193-pr194-snapshot-latest/result.json"]
reflected_to: []
---

# PR #194 U003 target container raw cycle repair

## Source Finding

- Inventory: I004
- Review comment: 3425775988
- Review thread: PRRT_kwDOQ99OK86KG9x6
- Status: valid / blocking / fix-now

## Objective

Make raw node-level dependency validation reject a candidate where the target is a descendant of a container that already depends back on the source container, because that state can become an issue-level cycle when the source container later gains child issues.

## Scope

- Provider runtime source of truth:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/deps.py`
- Dogfooding runtime mirror if provider runtime source changes:
  - `spec-dock/scripts/spec_dock_runtime/domain/deps.py`
- Focused tests:
  - `tests/unit/domain/test_deps.py`
  - or another existing focused deps test file if local pattern is stronger

## Constraints

- Preserve existing public error code mapping in mutation paths unless tests show an existing contract requires otherwise.
- Do not change docs/help in this unit.
- Do not resolve GitHub review threads manually.
- Keep changes minimal and local to raw validation plus tests.

## Required Regression Shape

Create a graph equivalent to:

- `init-00001` is an empty or future source container.
- `init-00002` contains `iss-00002`.
- Existing raw edge: `init-00002 -> init-00001`.
- Candidate raw edge: `init-00001 -> iss-00002`.

Expected result: raw validation rejects the candidate before saving because it would allow a future compiled cycle after `init-00001` gains an issue.

## Verification

- Run the focused domain test for the new regression.
- If provider/dogfood mirrors both change, confirm they stay equivalent for the edited function.

## Completion Criteria

- The review example is rejected.
- Existing S01/S02 regressions remain green.
- Changed files and test evidence are reported back to the orchestrator.

## Implementation Result

- Status: implemented
- Changed files:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/deps.py`
  - `spec-dock/scripts/spec_dock_runtime/domain/deps.py`
  - `tests/unit/domain/test_deps.py`
- Evidence:
  - Red: `uv run pytest tests/unit/domain/test_deps.py -k target_container_future_cycle` failed before implementation with `DID NOT RAISE <class 'RuntimeError'>`.
  - Green: `uv run pytest tests/unit/domain/test_deps.py` -> `8 passed`.
  - Integrated focused bundle after all U003/U004/U005 repairs: `uv run pytest tests/unit/domain/test_deps.py tests/unit/application/test_check_deps.py tests/cli_runtime/test_runtime_delete_s13.py` -> `69 passed`.
- Reviewer result: fresh code-reviewer final pass; no findings.
- Re-observation Result: pending push / PR re-observation.
