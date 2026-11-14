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

## 直した後の写し（S-08、タスク担当）

コミット 1005646d3 から作った隔離の venv（`.workbench/iss-00587/venv-after`、ポート 18588、同じ状態の置き場の写し）で、`.workbench/iss-00587/shoot.mjs`（headless Chrome、CDP）で撮り、同じスクリプトで測った（`plan-after.json`、`plan-after-390.json`）。写しは `.workbench/iss-00587/shots/after/`。

| 場面 | 測り | 写し |
|---|---|---|
| 構造の図 1440、epic-00573 | 欄 left 796・幅 634、タブ 説明資料・概要・依存・配下・文書・Artifact・人のタスク、選ばれたタブ explanation、iframe src `/r/github.com/chemitaro/spec-dock/files/epic-00573/explanation.html`、sandbox `allow-scripts allow-popups`、上の帯のボタンで欄と重なるもの 0、依存のタブへ切り替えて URL 不変、「詳しい画面」で `/r/…/scopes/epic-00573?tab=deps` | `graph-1440-explain.png`、`graph-1440-deps.png`、`graph-1440.png`（詳しい画面） |
| 構造の図 1000、iss-00587 | 欄 幅 440、説明資料が最初、帯と重なるもの 0 | `graph-1000.png` |
| 構造の図 1000、epic-00471（雛形） | 最初のタブ summary、iframe なし | `graph-1000-skel.png` |
| ボード 1440、iss-00587 | 札を押して URL 不変（/board）、欄 幅 634、列の右端 762 < 欄の左端 796、説明資料が最初、概要へ切り替え | `board-1440-explain.png`、`board-1440.png` |
| ボード 1000、iss-00407（説明資料なし） | 最初のタブ summary、列の右端 516 < 欄の左端 550 | `board-1000.png` |
| 詳しい画面 1440、epic-00573（tab なし） | 選ばれたタブ「説明資料」 | `scope-1440.png` |
| 構造の図 390、iss-00587 | 通常の段 top 354・高さ 490（844×0.58） | `graph-390-half.png` |
| ボード 390、iss-00587 のスワイプ | 通常 490 → 見出しを上へ払う → 全体 top 0・高さ 844・説明資料の枠 652px → 下へ払う → 通常 → 下へ → 最小 120 → 上へ → 通常 → 説明資料の枠の上で上へ 200px 引きずる → 通常のまま（動かない）→ 下へ → 最小 → さらに下へ → 閉じた（選びが外れる） | `board-390-half.png`、`board-390-full.png`、`board-390-peek.png`、`board-390-closed.png` |

直す前（`shots/before/`）との違い：欄の幅 372 → 634（1440）、ボードで札を押すと詳しい画面へ移っていた → 同じページで欄が開く、欄に説明資料とタブがなかった → 説明資料が最初のタブで埋め込まれる、スマホのシートは動かなかった → 3段に動く。

気づき（後の提案）：スマホの印だけの下の帯で、「新しいタブで開く」と「GitHub」が同じ外部リンクの印になる（名前は aria-label と title にある）。通常の段でも下の帯が印だけになる（設計は全体の段だけを決めていた。読みの邪魔はない）。

## 実装の記録

詳細: [Report Guide](../../../docs/authoring/report.md)

## Outcome

## Verification

## Residual Risks / Follow-ups
