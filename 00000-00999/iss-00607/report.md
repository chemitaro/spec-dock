---
種別: レポート（Issue）
ID: "iss-00607"
関連GitHub: ["#607"]
最終更新: "2026-11-16"
依存: ["requirement.cue", "design.cue", "plan.cue"]
---

# Result Summary

詳細: [Report Guide](../../../docs/authoring/report.md)

## レビュー記録

- 仕様のレビュー round-1（spec-reviewer opus / high）：**合格**（P0・P1 なし、P2 1・P3 4）。結果 `.workbench/spec-review/iss-00607/round-1.json`、検査 `round-1.check.json`（valid、status pass）（worktree `/Volumes/990p2t/workspace/worktrees/orca/spec-dock/iss-00607`）。
- 合格した文書の sha256：requirement.cue `e2ac949f4c4aa348e505acc934f79b49a82c68d37c87efefeeb97cf32032eaa0`、design.cue `161aecb2e073445a8e648aef2b74ee538682293ee9b34bfbfdc76aa2be2aa5e1`、plan.cue `5f61813b3971eb36261215a1881e45f775f79b12b3c18dc0f872c5b30d5ffe4d`。
- P2・P3 は文書を変えず、実装担当への指示（意味を保つ解釈）で扱う（下の「逸脱と判断」）。

## 逸脱と判断

- 仕様のレビューの P2（T-06 の線の確かめ）：toolbar の harness（`tests/js/dashboard_graph_toolbar.mjs`）を、世界の `.gx-edges` の HTML（または layout の edges）も返すように広げ、版3に deps none を保存した状態で線（is-done を含む）があることを確かめる。テストだけの変更。
- P3（注釈と字の検査）：prefs.js の注釈は `deps` の字を使わずに書く（例 "the old line choice"）。graph.js の字の検査は S-03 で書く。
- P3（これからの線）：`test_dashboard_graph_range.py` の deps none の検査は、deps なしの組（これからで端が done の線がない）に書き換える。
- P3（時系列の series）：`test_weeks_of_the_chosen_kinds_add_up` の all・issue・none は Scope の種類で、deps と関係ないので触らない。

## Outcome

## Verification

## Residual Risks / Follow-ups
