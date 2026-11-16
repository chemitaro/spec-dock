---
種別: レポート（Issue）
ID: "iss-00624"
関連GitHub: ["#624"]
最終更新: "2026-11-17"
依存: ["requirement.cue", "design.cue", "plan.cue"]
---

# Result Summary

詳細: [Report Guide](../../../docs/authoring/report.md)

## レビュー記録

- 仕様のレビュー round-1（spec-reviewer opus / high）：**合格**（P0・P1・P2 0、P3 1：T-01 が F-01 の「外の GIT_CONFIG_* がある条件」を含まない。記録だけ）。結果 `.workbench/spec-review/iss-00624/round-1.json`、検査 `round-1.check.json`（valid、status pass、reviewed_sha `7f7dd2b1d`）。worktree `/Volumes/990p2t/workspace/worktrees/orca/spec-dock/iss-00624`。
- 合格した文書の sha256：requirement.cue `bcd6cc5b0d0089584f69ce592c433ab53bb2adcb03897934fd2de20c238e5f88`、design.cue `0c35fae09e15469807f17b6a6abc39e652cac082dcdd7d4af99cb409051cc5f7`、plan.cue `8a6c6b7e4a8c0f6cbd76777334e26b827e09fd05df8372aa761cb1ec2acf9e24`。

## 原因の調べ（タスク担当、2026-11-17）

- `GIT_TRACE=1` で、fixture と同じ環境の `git commit --allow-empty` が `git maintenance run --auto --quiet --detach` を起こすことを観測（git 2.56.0）。
- commit の返った後 0.5 秒の間に `.git` の中の `*.lock` が見えたのは 40 回中 1 回。`maintenance.auto=false`・`gc.auto=0` を環境で与えると 40 回中 0 回。
- `StartLock` は git を起動せず flock だけで、`.git` に書かない。製品の不具合はない。

## 実装と逸脱

- 逸脱 codex-symlink-refusal：impl-sol（codex gpt-6.1-sol / medium、dispatch ctx_b5b71af20e3b、launch codex / gpt-6.1-sol / medium）は chat-scratch の writable root の symlink で手元のコマンドを起動できず、変更なしで failed を返した。plan の rationale と統括の了承どおり、Claude Opus 5.5 / medium（dispatch ctx_a775632f3f04、launch claude / opus / medium）に切り替えた。
- S-01（Red、`c445cfa6e`）：回帰テスト `test_isolated_git_environment_disables_automatic_maintenance_and_gc` を足した。直す前は `git config --get maintenance.auto` が終了1で落ちた。直す前の環境の `GIT_TRACE=1` の commit は `maintenance run` を3回起こした。
- S-02（Green、`b3135a3a6`）：`_environment()` に `GIT_CONFIG_COUNT=2`（`maintenance.auto=false`、`gc.auto=0`）を足した。ファイルの4件が通る。`_snapshot()` とほかのアサーションは変えていない。
- 基準（開始のコミット `7f7dd2b1d`）：`make lint` 合格。全体の `uv run pytest` は実装担当のバックグラウンドの上限30分で約48%まで（失敗0）で止まり、終わっていない。

## Outcome

- 揺れの原因は、テストの fixture の git が切り離して起こす自動の maintenance（`.git/objects/maintenance.lock`）と、テストの `.git` の走査の競合。製品の不具合ではなく、テストの環境で止めて直した。製品のコードは変えていない。

## Verification

- S-03（実装担当、`b3135a3a6`）：`tests/integration/test_issue413_native_lock.py` を単独で50回続けて走らせ、**50/50 通過**。`make lint` 合格。全体の `uv run pytest` を2回、**どちらも 4011 passed / 7 skipped、失敗0**。
- 最終品質ゲート（quality-gate-reviewer opus / medium、second opinion なし、範囲 `7f7dd2b1d..0c1b66182`、観点 functional-correctness・requirements-closure・test-adequacy）：attempt 01（`0c1b66182`、origin/main の #625 を取り込んだ後）で**合格**。review lane は P0〜P2 0、P3 1（この記録の欠け。ここで反映した）、coverage complete。test lane は `make lint` exit 0、`uv run pytest` exit 0（4014 passed / 7 skipped）。closure `.workbench/final-quality-gate/iss-00624-fqg-1/closure.md`（worktree `/Volumes/990p2t/workspace/worktrees/orca/spec-dock/iss-00624`）。

## Residual Risks / Follow-ups

- 同じ形（fixture の commit の後に `.git` を走査する）で、maintenance を止めていないテストは、`rg` で見た範囲では `tests/unit/application/test_dashboard_scope_details.py` が候補（走査の対象が `.git` かは確かめていない）。この Issue の範囲外。
- git の将来の版で自動の仕事の設定名が変わると、また揺れうる。回帰テストが `maintenance run` の起動を見張る。
