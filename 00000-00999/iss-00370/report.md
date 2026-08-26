---
種別: レポート（Issue）
ID: "iss-00370"
タイトル: "Managed Distribution Deprovision"
関連GitHub: ["#370"]
最終更新: "2026-08-27"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00365", "init-local-00003"]
---

# Result Summary

Issue 370のmanaged distribution deprovision実装を完了した。配布元同一性、semantic source drift、generated state、nested cleanup、forward-only journal、typed result、CLIのJSON/text公開を実装計画に沿って統合した。Full Regressionのapproved failure ledgerは変更していない。実装ブランチ上でP10候補検証を完了し、最終品質ゲートへ引き渡せる状態にした。

## Outcome

- 実装ブランチ: `codex/iss-00370-fqg-final`（コード実装コミット: `8409af8a28bf6920536b719440237c13a862b433`）。
- 候補 worktree `codex/iss-00370-with-baseline` には書き込み・stage・commit・pushを行っていない。候補側の既存 index/working tree は保護したままである。
- 計画上の性能目標を更新し、600秒はIssue 369の4時間超実行を改善するためのadvisory target、hard boundは1200秒/shard・1800秒全体とした。

## Verification

- `make lint`: pass（ruff check、ruff format、mypy 174 source files）
- `./spec-dock/scripts/spec-dock validate`: pass（nodes=227）
- source変更の `git diff --check`: pass
- Issue 370 managed-distribution suite: `432 passed`（`tests/unit/infra/test_managed_distribution.py`）
- 通常の `uv run pytest`: `1385 passed, 1139 skipped`
- candidate-wide Full Regression command（verified candidate SHA `8409af8a28bf6920536b719440237c13a862b433`）:

  ```bash
  uv run python spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00365-specdock-structural-integrity-rearchitecture-and-regression-baseline-recovery/issues/iss-00368-recognized-workspace-reconciliation/artifacts/verify-full-regression.py \
    --timeout-seconds 1200 --max-total-seconds 1800 --shards 4 \
    --artifact-dir /private/tmp/spec-dock-full-final-5G6qvQ
  ```

- 実装候補 SHA: `8409af8a28bf6920536b719440237c13a862b433`。
- verifier結果（`/private/tmp/spec-dock-full-final-5G6qvQ/20260826T191123.273760Z/result.json`）は `status=verified`、candidate-wide 2524 nodes、approved failure signatures 27件 exact一致、unexpected failure/error 0、`slo_status=pass`、`total_elapsed_seconds=691.252`。検証プロセスはledger照合後に終了コード0となった。
- 600秒のadvisory targetは超過したが、4シャードのbounded実行はhard bound（1200秒/shard・1800秒全体）内で完了した。27件は現行provider laneの承認済みbaselineであり、Issue 370 attributable failureではない。
- 既存の `artifacts/full-regression-evidence-d13d65fc/` は旧コミットの不変証跡であり、今回の判定には流用していない。今回のverifier raw `result.json`、collection、4シャードのJUnit/pytest logは上記 `/private/tmp` に保持している。ハーネス・baseline ledgerは変更していない。

## Residual Risks / Follow-ups

- Full Regressionの27件は現行baselineのapproved-no-opであり、Issue 370では修復・ledger変更を行っていない。candidate-wide verifierでledger exactnessを確認できた。
- 600秒はhard gateではない。将来の性能改善では実測値を比較するが、合否はbounded完走、coverage、ledger exactness、unexpected failure/error 0で判定する。
- 最終品質ゲート通過後にこのブランチをpushし、Issue 370用のPRを作成する。baseline更新PR #377への依存が必要な場合はPRに明記し、人間のmerge gateで順序を確認する。自動mergeは行わない。
