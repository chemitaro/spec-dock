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
- source変更の `git diff --check`: pass（raw verifier log/XMLは実行時空白を保持）
- Issue 370 focused tests: `66 passed, 349 deselected`
- 通常の `uv run pytest -q`: `1368 passed, 1139 skipped`
- candidate-wide Full Regression command（verified candidate SHA `d13d65fc76a30f212e88e925026fd35b3448e8ac`）:

  ```bash
  uv run python spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00365-specdock-structural-integrity-rearchitecture-and-regression-baseline-recovery/issues/iss-00368-recognized-workspace-reconciliation/artifacts/verify-full-regression.py \
    --timeout-seconds 1200 --max-total-seconds 1800 --shards 4 \
    --artifact-dir /private/tmp/codex-agent-work/501/session-20260826t013921z-issue-370-baseline-regression-a5a295e5/issue370-combined-full-regression-release-d13d65fc-rerun2
  ```

- 最終実装候補 SHA: `d13d65fc76a30f212e88e925026fd35b3448e8ac`。
- 最終候補実行結果（`20260826T131033.536208Z/result.json`）は `status=verified`、candidate-wide 2507 nodes、approved failure signatures 27件 exact一致、`unexpected_errors=[]`、`missing_failures=[]`、`signature_mismatches=[]`、`slo_status=pass`、`total_elapsed_seconds=625.085`。
- 先行実行は未追跡の証跡ディレクトリを候補wheelが検出したため `ledger-mismatch` となった。証跡を退避したclean worktreeで再実行し、上記verified結果を得た。既存provider laneの承認済みfailure以外にIssue 370 attributable failureはない。
- Full Regressionのraw `result.json`、2507件のcollection inventory、4シャードのJUnit/pytest logは、`artifacts/full-regression-evidence-d13d65fc/` にtracked copyとして公開している。ハーネス・baseline ledgerは変更していない。

## Residual Risks / Follow-ups

- Full Regressionの27件は現行baselineのapproved-no-opであり、Issue 370では修復・ledger変更を行っていない。候補全体の最終実行では既存制御テストを含めてledger exactnessを確認できた。
- 600秒はhard gateではない。将来の性能改善では実測値を比較するが、合否はbounded完走、coverage、ledger exactness、unexpected failure/error 0で判定する。
- baseline更新PR #377への依存をPRに明記し、人間のmerge gateで順序を確認する。自動mergeは行わない。
