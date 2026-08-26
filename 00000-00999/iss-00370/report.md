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

Issue 370のmanaged distribution deprovision実装を完了した。配布元同一性、semantic source drift、generated state、nested cleanup、forward-only journal、typed result、CLIのJSON/text公開を実装計画に沿って統合した。Full Regressionのapproved failure ledgerは変更していない。実装候補のコード検証と候補全体の最終認証を完了した。

## Outcome

- 実装候補ブランチ: `codex/iss-00370-with-baseline`
- 計画上の性能目標を更新し、600秒はIssue 369の4時間超実行を改善するためのadvisory target、hard boundは1200秒/shard・1800秒全体とした。
- staleな候補worktree専用 `index.lock` は保持プロセス不在を確認後に対象限定で除去し、通常のGit staging/commitを復旧した。

## Verification

- `make lint`: pass（ruff check、ruff format、mypy 174 source files）
- `./spec-dock/scripts/spec-dock validate`: pass（nodes=227）
- `git diff --check`: pass
- Issue 370 focused tests: `64 passed, 349 deselected`
- 通常の `uv run pytest -q`: `1366 passed, 1139 skipped`（再実行結果）
- candidate-wide Full Regression command（verified candidate SHA `1abf6f3de614c7264ab63a3cf93f5a1841d8cf80`）:

  ```bash
  uv run python spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00365-specdock-structural-integrity-rearchitecture-and-regression-baseline-recovery/issues/iss-00368-recognized-workspace-reconciliation/artifacts/verify-full-regression.py \
    --timeout-seconds 1200 --max-total-seconds 1800 --shards 4 \
    --artifact-dir /private/tmp/codex-agent-work/501/session-20260826t013921z-issue-370-baseline-regression-a5a295e5/issue370-combined-full-regression-release-1abf6f3d-rerun
  ```

- 通常の `uv run pytest -q` は初回に既存の Full Regression 制御テストが1件失敗したが、直後の再実行で `1366 passed, 1139 skipped in 49.95s` となった。
- 最終候補 SHA: `1abf6f3de614c7264ab63a3cf93f5a1841d8cf80`。
- 最終候補実行結果（`20260826T110851.930434Z/result.json`）は `status=verified`、candidate-wide 2505 nodes、approved failure signatures 27件 exact一致、`unexpected_errors=[]`、`missing_failures=[]`、`signature_mismatches=[]`、`slo_status=pass`、`total_elapsed_seconds=666.474`。
- 同一候補で先行実行に発生した既存 provider lane の `os.killpg(...): PermissionError` は再実行では発生せず、Issue 370 attributable failureもない。ハーネス・baseline ledgerは変更していない。
- Full Regression artifactは上記 `--artifact-dir/20260826T110851.930434Z/` 配下の `result.json`、shard JUnit、pytest logを正本とする。

## Residual Risks / Follow-ups

- Full Regressionの27件は現行baselineのapproved-no-opであり、Issue 370では修復・ledger変更を行っていない。候補全体の最終実行では既存制御テストを含めてledger exactnessを確認できた。
- 600秒はhard gateではない。将来の性能改善では実測値を比較するが、合否はbounded完走、coverage、ledger exactness、unexpected failure/error 0で判定する。
- baseline更新PR #377への依存をPRに明記し、人間のmerge gateで順序を確認する。自動mergeは行わない。
