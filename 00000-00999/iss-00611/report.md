---
種別: レポート（Issue）
ID: "iss-00611"
関連GitHub: ["#611"]
最終更新: "2026-11-16"
依存: ["requirement.cue", "design.cue", "plan.cue"]
---

# Result Summary

詳細: [Report Guide](../../../docs/authoring/report.md)

## レビュー記録

- 仕様のレビュー round-1（spec-reviewer opus / high）：合格（P0・P1 なし、P2 3・P3 2）。`.workbench/spec-review/iss-00611/round-1.json`（worktree `/Volumes/990p2t/workspace/worktrees/orca/spec-dock/iss-00611`）。P2・P3 はすべて実装の前に反映した（`review-response.md`）。
- round-2（同じレビュアー）：**合格**。P0〜P3 すべて0。結果 `round-2.json`、検査 `round-2.check.json`（valid、status pass、reviewed_sha `2c7427a97`）。
- 合格した文書の sha256：requirement.cue `2988a3ee2b3b33082da4b35fbf1971c7357b55fcb3c10f2fea763c4869aa3db1`、design.cue `8418b5b54c288103497db305c6950c4a67a79d550d301d9435427052d673a29b`、plan.cue `ff2b8a187a89585f3033bd376920f0fb7ca27476b0fcaef08f589eb476763e84`。

## 実装の記録

- 実装担当：Claude Opus 5.5 / medium（plan の impl-sol の rationale どおり、Codex の gpt-6.1-sol が chat-scratch の symlink の拒否で起動できなかったための切り替え。逸脱として記録する）。worktree `/Volumes/990p2t/workspace/worktrees/orca/spec-dock/iss-00611`、branch `chemitaro/iss-00611`。
- 基準（開始のコミット `2c7427a97`）：graph_js・graph_range・graph_toolbar の 73 passed、`make lint` 合格（ruff check・format・mypy）。
- S-01（Red）`12c2841c974c133ce01528405d3f8495240933d3`：`test_dashboard_graph_range.py` に `_parents()`・`_cycle()` と T-01〜T-06・T-09、`test_dashboard_graph_toolbar.py` に T-07（`_only_candidates()`、run `parents`）を足した。直す前のコードで 5 failed / 82 passed。落ちたのは R-01 の `test_next_leaves_out_a_parent_with_nothing_shown_inside[nest|tree]`（70・80・81・110・111 が余計に出る）、focus 80 の `[init-00080-nest|tree]`（81 が余計に出る）、T-07 `test_next_with_only_an_empty_parent_left_says_so`（init-00001 が出る）だけ。前提（候補がちょうど 71・73・82・96）、R-02・R-03・R-05・F-02、focus 70・95、audit は通った。
- S-02（Green）`a51e09159804c7865183d9be0dcabeaa65551639`：`layout.js` の `visibility` の next の分岐だけを `(kids.length ? kids.some(visible) : s.state !== "done" && !cleanup.has(s.id))` にした（全体・いまの分岐は文字どおり変えない）。3つのファイルで 87 passed。iss-00603 の digest と `_next()` の `SHOWN`・`FOCUS` は変えていない。
- S-03 `a51e09159`：`make lint` 合格、`uv run pytest` 3976 passed, 7 skipped（1749.92s）。ログ `.workbench/implement/iss-00611/s03-full.log`。

## 実データの写し（S-04、タスク担当）

- この PC の状態の置き場（`~/.local/state/spec-dock`）を `.workbench/iss-00611/state-{before,after}` に写し、開始のコミット `2c7427a97`（前）と `a51e09159`（後）を `git archive` から wheel にして、別々の隔離した venv に入れた。`spec-dock dashboard serve --offline --tailscale --state-root …` を前 18611・後 18612 で立てた。常駐の 47800 と道具の環境には触れていない。
- headless Chrome（`--disable-features=MacAppCodeSignClone`、CDP `Browser.close` で閉じた）で、保存 `specdock.graph.v3` を `{mode: nest, range: next}` にして、orca-web・spec-dock・housing-lifecycle × 前・後 × 1440・390 × 明・暗の24枚を写した（スクリプト `.workbench/iss-00611/shoot.mjs`、全部の数字 [result.json](artifacts/20261116t135046z--result.json)）。**edgeAudit の違反はすべて0**、押された範囲はどれも「これから」、390 でも横のはみ出しなし。
- ブラウザーのエラー：グラフ由来は0。どの写しにも出た2件は、ページが読む Orca の埋め込み `http://127.0.0.1:8791/embed/agent-marks.js` の CORS の拒否（前・後で同じ。試しのサーバーが別のポートのため。構造の図とは関係しない）。

| リポジトリ | 前（これから） | 後（これから） | 写し |
|---|---|---|---|
| orca-web | 枠1（**init-00002** だけ、中は空） | 0。図の場所に知らせ「これから進める Scope はありません。全体で、終わったものを見られます。」、帯は残る（F-01） | [前 1440 明](artifacts/20261116t135047z--before-orca-web-1440-light.png)、[後 1440 明](artifacts/20261116t135047z-01--after-orca-web-1440-light.png)、[後 390 暗](artifacts/20261116t135047z-02--after-orca-web-390-dark.png) |
| spec-dock | 箱5・枠5（init-00468 が中のない枠） | 箱5・枠4（**init-00468 が消えた**。ほかは同じ） | [前 1440 明](artifacts/20261116t135047z-03--before-spec-dock-1440-light.png)、[後 1440 明](artifacts/20261116t135047z-04--after-spec-dock-1440-light.png)、[後 390 暗](artifacts/20261116t135048z--after-spec-dock-390-dark.png) |
| housing-lifecycle | 箱23・枠26・線11 | 同じ（中のない親がないので変わらない） | [後 1440 暗](artifacts/20261116t135048z-01--after-housing-lifecycle-1440-dark.png)、[後 390 明](artifacts/20261116t135048z-02--after-housing-lifecycle-390-light.png) |

- orca-web の init-00002 は、DOM の `data-id` で、前は 4枚すべてに出て、後は 4枚すべてで出ない（result.json の `init00002`）。
- 試しの URL（本人の確かめ用、確かめまで残す。後のコード）：tailnet `http://100.85.74.8:18612/`（orca-web は `/r/github.com/chemitaro/orca-web/`、spec-dock は `/r/github.com/chemitaro/spec-dock/`）。「これから」を押して確かめる。止め方：`kill $(lsof -tnP -iTCP:18612 -sTCP:LISTEN)`（またはタスク担当・統括に頼む）。前の 18611 は写しの後に止めた。

## Outcome

## Verification

## Residual Risks / Follow-ups
