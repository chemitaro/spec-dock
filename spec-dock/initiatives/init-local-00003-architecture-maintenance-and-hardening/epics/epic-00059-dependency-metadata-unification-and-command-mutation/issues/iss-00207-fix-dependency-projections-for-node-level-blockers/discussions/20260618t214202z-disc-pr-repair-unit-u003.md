---
種別: disc
ID: "20260618t214202z-disc"
タイトル: "PR Repair Unit U003"
状態: "draft | proposed | archived"
作成者: "iwasawayuuta"
最終更新: "2026-06-18"
親: ["iss-00207"]
関連: []
authority: "proposed"
derived_from: []
reflected_to: []
---

# 20260618t214202z-disc PR Repair Unit U003

## source_batch

- `20260618t194321z-pr-repair-batch`

## unit_id

- U003

## covered_ids

- I006: Preserve local high-level open state for empty initiative / epic dependencies

## source_links

- PR: https://github.com/chemitaro/spec-dock/pull/208
- Observation head SHA: `473a50910aed8d2fc419a52ca157ca12dc4ac57b`
- I006 thread: `PRRT_kwDOQ99OK86Krei6`
- I006 comment: `3438957583`

## failure_class

- `review_feedback:local-high-level-open-state`

## risk_class

- blocking

## disposition

- fix-now

## Validity Analysis

The finding is valid. `resolve_issue_statuses` resolves non-GitHub-linked initiative / epic nodes as `effective_status="open"` with `source="local"`, but `resolve_high_level_status_context()` previously accepted only GitHub and cache snapshots before trying descendant aggregation. Empty high-level nodes have no descendants, so local open state fell through to `unknown/none`.

## Need-To-Fix Decision

Fix now. The behavior is inside the issue scope because `deps check`, `deps-issues`, and `deps-raw` must distinguish known local open blockers from truly unknown high-level status.

## Root Cause

The high-level status resolver treated local high-level status as a fallback only through descendant aggregation. Empty local containers cannot be aggregated, so their already-known local open status was lost.

## Options Considered

- Leave as follow-up: rejected because the repair is small and directly affects blocker reason accuracy.
- Accept any local status before descendant aggregation: rejected because it could mask done descendant aggregate behavior.
- Use local high-level status only after GitHub/cache and descendant aggregation fail: selected.

## Recommended Design

- Preserve the existing GitHub and cache precedence.
- Preserve descendant aggregate precedence for non-empty local containers.
- If no prior resolver produced a state and the high-level node status is `source="local"` with normalized `open` or `done`, use that local status.
- Keep GitHub-linked unresolved empty high-level nodes as `unknown/none`.

## Implementation Result

- Implemented.
- `resolve_high_level_status_context()` now uses local high-level status as the final known-state fallback.
- Added / updated regressions:
  - local empty high-level dependency becomes `empty_open` with `state_source="local"`;
  - GitHub-linked empty high-level dependency without cache remains `empty_unknown` with `state_source="none"`;
  - descendant aggregate still overrides local default open when child issue state is known.
- Provider runtime changes were mirrored into `spec-dock/scripts/spec_dock_runtime/...`.

## Commit Evidence

- pending commit after parent integration.
- Parent verification before commit:
  - `uv run pytest tests/unit/application/test_check_deps.py -k "local_empty_high_level_dependency_preserves_open_status or github_linked_empty_high_level_dependency_without_cache_fails_unknown or local_high_level_default_open_does_not_mask_done_descendant_aggregate"` -> 3 passed
  - `uv run pytest tests/unit/application/test_check_deps.py` -> 14 passed
  - `uv run pytest tests/cli_runtime/test_deps.py -k "deps_check or node or empty_high_level or closed_epic_context"` -> 31 passed, 8 skipped, 69 deselected
  - `./spec-dock/scripts/spec-dock validate` -> `spec-dock: ok (validate) nodes=130`
  - `git diff --check` -> pass
  - `diff -u src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/check_deps.py spec-dock/scripts/spec_dock_runtime/application/check_deps.py` -> no diff

## Step Review

- `code-reviewer` `review_status=pass`; no findings.

## Re-observation Result

- pending after commit and push.

## Residual Risk / Follow-up

- pending re-observation.

## Ledger Note

- No material implementation decisions beyond the approved plan.
