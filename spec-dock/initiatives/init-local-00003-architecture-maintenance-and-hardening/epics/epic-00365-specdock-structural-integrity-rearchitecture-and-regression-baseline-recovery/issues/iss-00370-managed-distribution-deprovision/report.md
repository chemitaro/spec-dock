---
種別: レポート（Issue）
ID: "iss-00370"
タイトル: "Managed Distribution Deprovision"
関連GitHub: ["#370"]
最終更新: "2026-08-26"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00365", "init-local-00003"]
---

# Result Summary

Issue 370のmanaged distribution deprovision実装を完了した。配布元同一性、semantic source drift、generated state、nested cleanup、forward-only journal、typed result、CLIのJSON/text公開を実装計画に沿って統合した。Full Regressionのapproved failure ledgerは変更していない。

## Outcome

- 実装候補ブランチ: `codex/iss-00370-with-baseline`
- 計画上の性能目標を更新し、600秒はIssue 369の4時間超実行を改善するためのadvisory target、hard boundは1200秒/shard・1800秒全体とした。
- staleな候補worktree専用 `index.lock` は保持プロセス不在を確認後に対象限定で除去し、通常のGit staging/commitを復旧した。

## Verification

- `make lint`: pass（ruff check、ruff format、mypy 174 source files）
- `./spec-dock/scripts/spec-dock validate`: pass（nodes=227）
- `git diff --check`: pass
- Issue 370 focused tests: `59 passed, 20 skipped, 2421 deselected`
- 通常の `uv run pytest -q`: `1361 passed, 1139 skipped`
- candidate-wide Full Regression command:

  ```bash
  uv run python spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00365-specdock-structural-integrity-rearchitecture-and-regression-baseline-recovery/issues/iss-00368-recognized-workspace-reconciliation/artifacts/verify-full-regression.py \
    --timeout-seconds 1200 --max-total-seconds 1800 --shards 4 \
    --artifact-dir /private/tmp/codex-agent-work/501/session-20260826t013921z-issue-370-baseline-regression-a5a295e5/issue370-combined-full-regression-release
  ```

- final candidate run result (`20260826T065404.405997Z/result.json`): `status=verified`、candidate-wide 2500 nodes、approved failure signatures 27件 exact一致、unexpected failure/error 0、missing/signature mismatch 0、`slo_status=pass`。`total_elapsed_seconds=654.352`で、600秒超過はadvisory follow-upとして扱う。
- Full Regression artifactは上記 `--artifact-dir/20260826T065404.405997Z/` 配下の `result.json`、shard JUnit、pytest logを正本とする。

## Residual Risks / Follow-ups

- Full Regressionの27件は現行baselineのapproved-no-opであり、Issue 370では修復・ledger変更を行っていない。
- 600秒はhard gateではない。将来の性能改善では実測値を比較するが、合否はbounded完走、coverage、ledger exactness、unexpected failure/error 0で判定する。
- PRはbaseline更新PR #377への依存を明記し、人間のmerge gateで順序を確認する。自動mergeは行わない。
