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

Issue 370のmanaged distribution deprovision実装を完了した。配布元同一性、semantic source drift、generated state、nested cleanup、forward-only journal、typed result、CLIのJSON/text公開を実装計画に沿って統合した。Full Regressionのapproved failure ledgerは変更していない。実装候補のコード検証は完了しているが、候補全体の最終認証は既存のFull Regression制御テストの実行環境依存失敗により保留している。

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
- candidate-wide Full Regression command:

  ```bash
  uv run python spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00365-specdock-structural-integrity-rearchitecture-and-regression-baseline-recovery/issues/iss-00368-recognized-workspace-reconciliation/artifacts/verify-full-regression.py \
    --timeout-seconds 1200 --max-total-seconds 1800 --shards 4 \
    --artifact-dir /private/tmp/codex-agent-work/501/session-20260826t013921z-issue-370-baseline-regression-a5a295e5/issue370-combined-full-regression-release-22686055-rerun
  ```

- 通常の `uv run pytest -q` は初回に既存の Full Regression 制御テストが1件失敗したが、直後の再実行で `1366 passed, 1139 skipped in 49.95s` となった。
- 最終候補 SHA: `22686055755145f3d5f88642594709cfe47ef005`。
- 同一 SHA の候補全体 Full Regression 再実行結果（`20260826T102745.887432Z/result.json`）は `status=ledger-mismatch`、candidate-wide 2505 nodes、approved failure signatures 27件は変更なし、`missing_failures=[]`、`signature_mismatches=[]`、`unexpected_errors=[]`、unexpected failureは `tests/unit/test_provider_test_lanes.py::test_full_regression_leader_exit_checks_group_after_pipe_eof` の1件、`slo_status=pass`、`total_elapsed_seconds=674.619`。
- 上記 unexpected failure は `verify-full-regression.py:139` の `os.killpg(...): PermissionError: [Errno 1] Operation not permitted` であり、Issue 370変更箇所外の既存制御テストである。同テスト単体は `1 passed`。ハーネス・baseline ledgerは変更していない。
- Full Regression artifactは上記 `--artifact-dir/20260826T102745.887432Z/` 配下の `result.json`、shard JUnit、pytest logを正本とする。

## Residual Risks / Follow-ups

- Full Regressionの27件は現行baselineのapproved-no-opであり、Issue 370では修復・ledger変更を行っていない。候補全体の認証を阻害している1件は、並列候補実行時の既存プロセスグループ制御テストの環境依存失敗である。
- 600秒はhard gateではない。将来の性能改善では実測値を比較するが、合否はbounded完走、coverage、ledger exactness、unexpected failure/error 0で判定する。
- 現時点では candidate-wide Full Regression が `ledger-mismatch` のため、最終品質ゲートとPR作成は保留する。baseline更新PR #377への依存、および上記制御テストの環境修復または正式な再検証が必要である。自動mergeは行わない。
