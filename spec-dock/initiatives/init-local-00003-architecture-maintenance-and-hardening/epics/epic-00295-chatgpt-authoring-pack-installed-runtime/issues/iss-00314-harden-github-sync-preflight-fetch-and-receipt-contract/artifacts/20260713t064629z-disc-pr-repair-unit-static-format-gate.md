---
種別: disc
ID: "20260713t064629z-disc"
タイトル: "PR Repair Unit U001 Static Format Gate"
状態: "proposed"
作成者: "iwasawayuuta"
最終更新: "2026-07-13"
親: ["iss-00314"]
関連: ["20260713t064556z-pr-repair-batch", "PR #321"]
authority: "proposed"
derived_from: ["R001", "R002"]
reflected_to: ["report.md"]
---

# PR Repair Unit U001 Static Format Gate

- source_batch: `20260713t064556z-pr-repair-batch-pr-repair-batch.md`
- unit_id: U001
- root_cause_family: `static-analysis.format-contract`
- covered_ids: R001, R002
- source_links: Provider CI runs 29229910006 and 29229887985
- failure_class: `check_failure:provider-tests`
- decided_priority: `required-ci`
- merge_blocking: yes
- disposition: `fix-now`

## Validity Analysis

Both required Provider CI runs fail in `Run provider static analysis` because `ruff format --check` reports seven changed Python files. Ruff lint and mypy pass. This is a valid, deterministic branch-local failure.

## Need-To-Fix Decision

Fix now. Required CI cannot pass without canonical formatting.

## Root Cause

The implementation was checked with `ruff check` but not with the repository's separate `ruff format --check` gate.

## Options Considered

- Format the seven CI-reported files only: selected; smallest deterministic repair.
- Format all `src tests`: rejected because it may introduce unrelated churn.
- Change CI or formatter config: rejected as out of scope.

## Recommended Design

Run the repository formatter only on the reported files. If provider files change, apply the identical formatted bytes to required dogfood mirrors using the normal projection/parity contract.

## Implementation Plan

1. Run Ruff formatter on the seven reported files.
2. Verify provider/dogfood mirrors remain byte-identical.
3. Run Ruff format check and Ruff lint over `src tests`.
4. Run focused authoring/preflight tests and mypy.
5. Commit and push the bounded formatting repair.

## Validation Plan

- `uv run ruff format --check src tests`
- `uv run ruff check src tests`
- focused preflight/pack and fetch/writer tests
- `uv run mypy src tests`
- provider/dogfood byte parity
- `git diff --check`

## Out of Scope

Semantic changes, formatter configuration, CI workflow changes, refactors, and non-blocking review work.

## Implementation Result

Ruff formatterをCI報告7ファイルへ限定適用し、対応するprovider/dogfood 3 mirrorをbyte-identicalに同期した。ASTは全7ファイルでHEADと同一で、semantic changeはない。fresh code-reviewerはPASS。

## Commit Evidence

`411510b66abd3dcd137fbed598606065134457e5`。format/lint/mypy、focused 1013 passed / 1 skipped、provider/dogfood parity、diff-checkはpass。

## Re-observation Result

新head push後に実行する。

## Residual Risk / Follow-up

Low. Re-observation must confirm Provider CI passes on the new head;同じfamilyが再発した場合はhuman gateへ移る。
