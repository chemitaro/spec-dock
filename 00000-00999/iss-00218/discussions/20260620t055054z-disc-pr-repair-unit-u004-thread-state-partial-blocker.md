---
種別: disc
ID: "20260620t055054z-disc"
タイトル: "PR Repair Unit U004"
状態: "draft | proposed | archived"
作成者: "iwasawayuuta"
最終更新: "2026-06-20"
親: ["iss-00218"]
関連: []
authority: "proposed"
derived_from: []
reflected_to: []
---

# 20260620t055054z-disc PR Repair Unit U004

## Repair Unit Metadata

- source_batch: 20260620t051224z-pr-repair-batch
- unit_id: U004
- covered_ids: I004
- source_links:
  - https://github.com/chemitaro/spec-dock/pull/220#discussion_r3445541880
- failure_class: review_feedback:partial-thread-collection-blocker
- risk_class: blocking
- disposition: fix-now

## Validity Analysis

Valid. `gh_graphql_threads()` emits `thread_state_partial` with `severity=blocking` when review thread pagination is incomplete. The downstream `blocking_collection_failure` predicate currently filters blocking limitations by a narrow code set and omits `thread_state_partial`. Because `no_findings_completion_promotes` only checks `not blocking_collection_failure`, a no-findings issue comment can still promote to a pass when review threads may be incomplete.

## Need-To-Fix Decision

Need to fix now. Partial review thread collection means unresolved review feedback may be missing. A no-findings issue-comment pass is only safe when thread collection did not report a blocking limitation.

## Root Cause

The code treats `severity=blocking` as metadata for output, but the no-findings promotion gate re-encodes a separate allow-list of blocking limitation codes. The allow-list drifted when `thread_state_partial` was added.

## Options Considered

- Option A: Add `thread_state_partial` to the existing code allow-list.
  - Pros: smallest diff.
  - Cons: future blocking limitation codes can drift again.
- Option B: Treat any limitation with `severity=blocking` as a promotion blocker.
  - Pros: aligns with the semantics of severity and prevents future allow-list drift.
  - Cons: any future blocking limitation, even if not thread-specific, blocks no-findings pass.

## Recommended Design

Use Option B. A decision-facing no-findings pass should not be promoted while any blocking limitation is present. This is simpler than preserving a code allow-list and matches the collector contract.

## Implementation Plan

1. Change `blocking_collection_failure` to check `item.get("severity") == "blocking"` for all limitations.
2. Mirror the provider-side script into `.agents`.
3. Add a focused regression where GraphQL reviewThreads pagination returns `hasNextPage=true` without an `endCursor`, producing `thread_state_partial`.
4. Assert no-findings does not promote and the blocking limitation is surfaced.
5. Run issue 218 focused tests and the full `tests/unit/infra/test_init_update.py` parity lane.

## Validation Plan

- `uv run pytest tests/unit/infra/test_init_update.py -k 'issue_218'`
- `uv run pytest tests/unit/infra/test_init_update.py`

## Implementation Result

- Implemented `blocking_collection_failure` as a severity-based blocker: any limitation with `severity=blocking` blocks no-findings promotion.
- Mirrored the provider-side `pr_review_snapshot.py` into the checked-in `.agents` copy.
- Added a regression where GraphQL thread pagination returns `hasNextPage=true` without `endCursor`, producing `thread_state_partial`.
- Verified no-findings does not promote when `thread_state_partial` is present.

## Commit Evidence

Pending commit and push.

## Re-observation Result

Pending latest-head re-observation.

## Residual Risk / Follow-up

Validation completed before commit:

- `uv run pytest tests/unit/infra/test_init_update.py -k 'issue_218'`: 23 passed.
- `uv run pytest tests/unit/infra/test_init_update.py`: 464 passed.

If a future limitation is marked `blocking` but intentionally should not block no-findings promotion, that future limitation should not use `severity=blocking`; otherwise this gate should block by default.

## 推奨反映先 (必須)
- `requirement.md`:
  - ...
- `design.md`:
  - ...
- `plan.md`:
  - ...
- `ADR`:
  - ...
- `report.md` Evidence Adoption Ledger:
  - ...

## 未採用 / deferred 理由 (必須)
- 未採用:
  - ...
- deferred:
  - ...

## 次アクション (必須)
- `requirement.md` / `design.md` / `plan.md` / `adr` へ反映する内容:
  - ...
- 追加で作る discussion docs:
  - ...
