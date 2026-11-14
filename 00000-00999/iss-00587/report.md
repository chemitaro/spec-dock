---
種別: レポート（Issue）
ID: "iss-00587"
関連GitHub: ["#587"]
最終更新: "2026-11-14"
依存: ["requirement.cue", "design.cue", "plan.cue"]
---

# Result Summary

## レビュー記録

- round-1（spec-reviewer opus / high）：不合格（P1 1・P2 4）。`.workbench/spec-review/iss-00587/round-1.json`、検査 `round-1.check.json`。対応 `review-response.md`（iframe を外さない差分の入れ替え、scope_tabs.css、ボードの revision と F-02、docState、全体の段の詰め方）。
- round-2（同じレビュアー）：**合格**。P0・P1・P2 なし、P3 1（D-05 の移す規則の一覧に parts.css にある .sd-lane と .sd-note が入っている。parts.css の範囲に .sd-pn を足すので影響なし。記録だけ）。`round-2.json`、検査 `round-2.check.json`（valid、status pass）。
- 合格した文書の sha256：requirement.cue `a7d5a626e18c45026f074e840c43387743a857fe0ba0234c97737bbb3fdd1a7c`、design.cue `baf6ed354161713d52c1ab217740a85518214c32cb640aad8dace98610efa05c`、plan.cue `25828cfebd7d59fc5a90be0aa813e10d84bedd396be37598c88d580ddd85b132`。
- 結果の場所：worktree `/Volumes/990p2t/workspace/worktrees/orca/spec-dock/iss-00587` の `.workbench/spec-review/iss-00587/`。
- CP-1（code-reviewer opus / medium の2人、axis standards と spec、範囲 `928460f48..5b1a7ca65`、S-01〜S-04）：**合格**。どちらも P0・P1 なし、P2 1件ずつ（欄の概要の「前回からの変化」が基準なしの api.scope で図の印と食い違う、欄の見出しが古い詳しい JSON で構造の新しい状態を上書きする）。結果 `.workbench/code-review/iss-00587/cp1-standards-round-1.json`・`cp1-spec-round-1.json`、検査 `*.check.json`（valid、status pass）。P2 の2件は、今回の共通化で入った食い違いなので、タスク担当の判断で S-05 の中で直すよう実装担当に送った。
- 注：plan.cue は合格の後、手順の status だけを書き換えている（中身は合格のまま）。

## 直す前の写し

開始のコミット 928460f48 から作った隔離の venv（`.workbench/iss-00587/venv-before`、ポート 18587、状態の置き場の写し `.workbench/iss-00587/state`）で撮った。`.workbench/iss-00587/shots/before/`：

- `graph-1440.png`：epic-00573 を選んだ欄（幅 372px、状態・道筋・種類・保証・段・配下の進み具合だけ）。上の帯の道具の右端（「待っている」）が欄の下に隠れる。
- `graph-1000.png`、`graph-390.png`：iss-00587 を選んだ欄。390 では下から高さ 432px のシートで、取っ手はあるが動かない。
- `board-1440.png`：札を押すと詳しい画面（/r/…/scopes/iss-00587）へ移る（欄はない）。
- `scope-1440.png`：詳しい画面（概要のタブ）。

## 実装の記録

詳細: [Report Guide](../../../docs/authoring/report.md)

## Outcome

## Verification

## Residual Risks / Follow-ups
