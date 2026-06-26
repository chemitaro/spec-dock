# epic-00224 stdout guidance handoff 再手動テストサマリー

## 総合判定

- 判定: 合格
- 理由:
  - `guidance issue-planning` / `guidance issue-execution` が標準出力で現在の案内を返すことを、dogfooding mirror と fresh trial repo の両方で確認した。
  - `workflow next` は primary command / fallback alias として残っておらず、invalid choice として拒否された。
  - runbook projection は `authority: non-canonical` の human-facing projection として生成され、symlink による projection write failure でも guidance stdout は非ブロックで返った。
  - context packet write failure は focused regression で fail closed のまま維持されることを確認した。
  - 前回修正した routing の退行は focused regression と trial repo guidance の両方で見つからなかった。

## 環境

- メイン checkout: `/Users/iwasawayuuta/.codex/worktrees/dbca/spec-dock`
- ブランチ: `iss-00238-stdout-runbook-handoff-instead-of-generated-workflow-files`
- テスト対象 commit: `3d0a2bb893189c70cbbd037106e501522794bdc3`
- Trial repo: `manual-tests/epic-00224-dynamic-workflow-resource-allocation/retest-20260626-guidance-handoff/workspaces/trial-local-repo`
- 実施日: 2026-06-26 JST
- 外部 GitHub mutation: なし

## 結果数

- PASS: 13
- PASS with note: 1
- FAIL: 0
- BLOCKED: 0
- SKIPPED: 0
- 合計: 14

## 主要な確認結果

- active issue なしの `guidance issue-execution` は `state=no-active` / `next_action=issue-start-required` を返した。
- `workflow --help` は `status` のみを表示し、`workflow next issue-execution` は invalid choice で失敗した。
- issue planning / execution skill は `guidance issue-planning` / `guidance issue-execution` を実行する指示に更新されていた。
- fresh trial repo でも installed runtime に `guidance` command が含まれた。
- 実運用風の hierarchy を作成し、実装可能な runtime issue で `dev-coder` / `medium` / `unit_tests` が guidance stdout に表示された。
- stale projection は再実行時に現在の active issue で更新され、古い `iss-99999` / `stale-next-action` は採用されなかった。
- symlinked runbook projection では projection が `written: false` になり、エラーは `Projection Errors` に表示された一方、guidance stdout 自体は exit 0 で返った。
- context packet failure、routing regression、workflow/wrapper regression の focused pytest はすべて成功した。

## 補足

- `issue start iss-09004` と `active set --id iss-09004` は、未準備 issue に対する lifecycle guard により blocked になった。これは今回の guidance handoff の不具合ではなく、trial repo で scaffold issue を active にする前提が不足していたためである。
- 手動テストでは `active set --force --no-checkout` を使って scaffold状態の guidance を確認した。

## 外部 GitHub Repository 要否

- 新規 GitHub repository は不要だった。
- `--github-issue <n>` と fake `gh` により、production GitHub state を変更せず hierarchy 作成と guidance 確認を実施できた。

## 残リスク

- 今回の手動テストは `guidance` handoff と前回修正分の退行確認に絞っているため、Epic 00224 の初回手動テストで扱った PR observation fake-gh matrix 全量は再実施していない。
- trial repo 内には手動テスト用の dirty state と pycache が残っているが、メイン checkout の通常 `git status` には影響しない。
- `manual-tests/` は ignore 対象なので、このサマリーを PR に含めるには明示的な force add が必要である。

## 証跡

- テスト計画: `manual-tests/epic-00224-dynamic-workflow-resource-allocation/retest-20260626-guidance-handoff/test-plan.md`
- 実施記録: `manual-tests/epic-00224-dynamic-workflow-resource-allocation/retest-20260626-guidance-handoff/execution-log.md`
- サマリー: `manual-tests/epic-00224-dynamic-workflow-resource-allocation/retest-20260626-guidance-handoff/summary-report.md`
- 証跡ディレクトリ: `manual-tests/epic-00224-dynamic-workflow-resource-allocation/retest-20260626-guidance-handoff/evidence/`
