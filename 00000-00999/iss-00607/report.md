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

## 実装の記録

- 逸脱 codex-symlink-refusal：plan の impl-sol（codex gpt-6.1-sol / medium、dispatch ctx_01b9a40e9a88）が chat-scratch の symlink の拒否で起動できず変更なしで failed を返したので、plan の rationale と統括の了承どおり Claude Opus 5.5 / medium が S-01〜S-02 を担当した。
- 基準（開始のコミット `bf21a961a`）：`make lint` pass。`uv run pytest tests/unit/presentation/test_dashboard_graph_js.py tests/unit/presentation/test_dashboard_graph_range.py tests/unit/presentation/test_dashboard_graph_toolbar.py` 68 passed。
- S-01（Red、`bedd72949`）：test_dashboard_graph_js.py（small・context に deps wait・none の組を足し deps なしと同じを確かめる、restorePrefs の opts が {mode, range} だけ、prefs.js に deps の字がない、node の確かめの組み合わせに deps がない）と test_dashboard_graph_range.py（cases を deps なしにして layout-before.json の deps all の組とだけ比べ、VARIANTS に deps wait・none を足す、これからの線の検査を deps なしの組に書き換える。記録用の `request_before` は開始時の組 `recorded_cases` のまま）。直す前のコードで意図した 6 件が落ちた（6 failed, 50 passed）。fixture は書き換えていない。時系列の series のテストは触っていない。
- S-02（Green、`424ba72eb`）：layout.js（D-01：DEFAULTS と options の注釈から deps、pairs の none・wait の分かれ道を消す）、prefs.js（D-02：VALID・restorePrefs から deps を消し、注釈は deps の字を使わずに直す）、dashboard_graph_check.mjs（組み合わせから deps をなくす。組の数の検査を 6 + 7 × 3 に直す）。節目のテスト：js・range はすべて通過、edgeAudit の違反0（T-04）。toolbar の 3 件（`saves_four_keys[nest|tree]`、`moves_a_saved_version_2_to_version_3`）は graph.js の savePrefs が deps を書く前提の古い期待で落ちる。graph.js と toolbar のテストは S-03 の範囲なので触っていない。`make lint` pass。

## Outcome

## Verification

## Residual Risks / Follow-ups
