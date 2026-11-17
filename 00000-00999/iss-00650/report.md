---
種別: レポート（Issue）
ID: "iss-00650"
関連GitHub: ["#650"]
最終更新: "2026-11-17"
依存: ["requirement.cue", "design.cue", "plan.cue"]
---

# Result Summary

詳細: [Report Guide](../../../docs/authoring/report.md)

## レビュー記録

- 仕様のレビュー（spec-reviewer opus / medium、light、2人目なし）：round-1 **合格**（P0 0、P1 0、P2 0、P3 0）。結果はこの worktree の `.workbench/spec-review/iss-00650/round-1.json` と `round-1.check.json`（reviewed_sha `92e26aff7`、文書は sha256 で固定）。
- **合格した文書の sha256**：requirement.cue `6aba51eeb1fbaa23efacbc9266aac7927bf6dcbeebf1f56c9901ca480faa320d`、design.cue `3bfd13529797a3389360fc8e0ef0411a6b44fd729917c2fbd91510e3275dd519`、plan.cue `06d2f950787f93bad17eae9ad74f75e35596fc5b8ad67acc76c6f6554fdae59d`。
- **範囲の追加（統括、2026-11-17）**：狭い画面の下からの欄（帯の欄、片付けの候補の欄）を指で動かせるようにする（R-03、F-02、D-03、S-03、T-03・T-04）。同じレビュアーで round-2 **合格**（P0 0、P1 0、P2 1、P3 1。reviewed_sha `f7655ea8c`、文書は sha256 で固定）。結果 `.workbench/spec-review/iss-00650/round-2.json` と `round-2.check.json`。
- **今の合格した文書の sha256**（round-2）：requirement.cue `6561b39a410974f1cc8024b2952e906f7dc3039d6b4a07c8838c0cea594372e8`、design.cue `58af6bb3de035380c7f8b9a0da4d23cd07cbe06d3a18845fa11c156b1b32fa6d`、plan.cue `e7f8798e88b244bba3a883849304aa82ac3c2c58ef609c8f7a390c3a4eb796a0`（この後の plan.cue の変更は手順の status だけ）。
- round-2 の P2・P3（止めない）：(P2) 『横断の構造』の片付けの候補の欄の引っぱりと閉じ方に検証がない → 実装で `test_dashboard_allgraph_command_screen.py` の `sheet` の走り（片付けの候補の欄を開いて全面、下へ引いて閉じる）と実機の測りに含めた。(P3) 保証の理由と CP-1 の理由が「1行の変更」のまま（文面の残り。変更は panel.js・panel.css・graph.js・allgraph.js・command_view.js の小さな判定と規則の直し）。

- **最終品質ゲート（2026-11-18、合格）**：キャンペーン iss-00650-r2、合格のコミット `85930f177`（base `92e26aff7`、attempt 01）。レビュー（quality-gate-reviewer opus / medium）P0〜P3 すべて0、網羅は完全。`make lint` exit 0、`uv run pytest` 4239 passed・7 skipped。closure：この worktree の `.workbench/final-quality-gate/iss-00650-r2/closure.md`。記録だけのコミットはない（記録は Git の外）。PR の直前に origin/main を取り込み直す必要はなかった（`92e26aff7` のまま）。

- **PR と CI（2026-11-18）**：PR #659（https://github.com/chemitaro/spec-dock/pull/659）、head `85930f177`。github-pr-checks の見張り：1回目は provider-tests の pending で IDLE_TIMEOUT（exit 4）、`resume_argv` で idle の期限を 3000 秒にして続け、OBSERVED_CI_PASS・merge readiness READY（provider-tests 16分40秒を含む7件すべて pass）。マージは統括。

- **origin/main の取り込みとやり直し（統括の依頼、2026-11-18）**：PR #658（iss-00648、`106f214e8`）が `command_view.js` と `tests/js/dashboard_{graph,allgraph}_command_screen.mjs` を変えたので、origin/main を merge した（`05bc6c5a8`、衝突なし、force push なし）。キャンペーン iss-00650-r3 で attempt 01 合格：レビュー P0 0・P1 0・P2 1・P3 0（P2 は参考：片付けの候補の欄を全面にしていても、構造の更新や画面の大きさの変化での描き直しで半分に戻る）、`make lint` exit 0、`uv run pytest` 4261 passed・7 skipped。closure：`.workbench/final-quality-gate/iss-00650-r3/closure.md`。CI は `05bc6c5a8` で OBSERVED_CI_PASS・READY。試しの 18650 は取り込んだ後のコードで立て直し、実機の数を測り直した（構造の図 1440：iframe 660 = 本文の内側 660、390：430 = 430、『横断の構造』1440：761 = 761、390：430 = 430、線の検査の違反0、`specdockCmdAudit` 0、エラー0。下からの欄は3つの欄とも 490 → 844 → 490 → 844 → 閉じる、pointercancel 0。`.workbench/iss-00650/measure-merged.jsonl`・`sheet-merged.jsonl`・`shots-merged/`）。

## Outcome

- 原因：帯の欄（`views/graph/command_view.js` の `renderAgentPanel`）の本文 `.pn-body` に `data-tab` がなく、`panel.css` の縦の flex の規則（`.pn-body:is([data-tab="docs"], [data-tab="explanation"], [data-tab="agents"])`）に乗らないため、`.sd-agent` の `flex: 1` が効かず、iframe は `min-height: 240px` のままだった。
- 直し（S-01、`f7655ea8c`）：チャットの枠を出すときだけ、本文を `<div class="pn-body" data-tab="agents">` にした。CSS は足していない。チャットを開けないときは今の `<div class="pn-body">` のまま（余白も同じ）。構造の図と『横断の構造』は同じ関数を呼ぶので、両方が直る。
- テスト（T-01）：`tests/js/dashboard_{graph,allgraph}_command_screen.mjs` の写しに本文の `data-tab` と「チャットを開けません。」を足し、`test_dashboard_graph_command_screen.py` に (1) 帯を押すと `bodyTab == "agents"`、panel.css の規則が PC とシートの2か所で `display: flex; flex-direction: column;` を持つ、(2) 描き直しても `agents` のまま（同じ iframe）、(3) detail のない統括では `data-tab` なしで「チャットを開けません。」（F-01）を、`test_dashboard_allgraph_command_screen.py` に帯を押すと `agents` を足した。Red は直す前の資産で (1)(2) と横断の件が落ちることを確かめた（3 failed）。

## 範囲の追加の実装（S-03、2026-11-17〜18）

- 原因（統括の読みどおりで、もう1つ見つけた）：(1) `panel.js` の pointerdown と、つまみの click が `current`（Scope の欄の中身）があるときだけ働いた。(2) 実機で、帯の欄と片付けの候補の欄を全面の段から下へ引くと、ブラウザーがタッチを取って `pointercancel` になった。全面の段の規則 `.sd-pn[data-snap="full"] .pn-head { display: contents; }` が、ほかの描き手の見出し（`.sd-pn > .pn-head`）にも効いて箱がなくなり、`touch-action: none` が効かなかった。
- 直し（`5bbd17914`・`487702eb7`・`85930f177`）：
  - `panel.js`：下からの欄の判定を「aside が開いている（`.is-open`）」にした（pointerdown、resize、つまみのタップ）。見出しの取っ手は `.pn-top` か `.pn-head`。つまみのタップは「ほかの描き手が aside を持つ」の早い返りより前。`SHEET_GRAB`（Scope の欄と同じつまみのボタン）を export し、`build()`・帯の欄（command_view.js）・片付けの候補の欄（graph.js・allgraph.js）が使う。`hide()` は前の下からの欄の高さが残っていれば（`data-snap` があれば）半分に戻す。
  - `graph.js`・`allgraph.js`：閉じるボタンと同じ処理を `closePanel()` にまとめ、`onClose`（引いて閉じたとき、Scope の欄の閉じる）と閉じるボタンの両方から呼ぶ。帯の欄は `closeAgentPanel()`（`clearAgentPanel` と強調の解除）、片付けの候補は `cleanup = false` と `renderPanel()`。
  - `panel.css`（狭い画面）：`touch-action: none` の範囲に `.sd-pn > .pn-head` を足し、全面の段の `display: contents` を `.pn-top > .pn-head`（Scope の欄の見出し）だけにした。
- テスト（T-03）：`tests/js/dashboard_{graph,allgraph}_command_screen.mjs` に走りごとの幅と高さ、`--pn-h` からの欄の矩形、欄の上の引っぱり（`sheet`）とつまみのタップ（`grab`）、写しの `snap`・`pnH`・`grab`・`clean` を足した。構造の図で帯の欄・片付けの候補の欄・Scope の欄・PC の幅の4つ、『横断の構造』で帯の欄と片付けの候補の欄（P2 の分）。`test_dashboard_scope_tabs_js.py` に `touch-action` と全面の段の規則の静的な検査。Red は直す前の資産で3件（帯・片付けの候補・横断）と静的な2件が落ちることを確かめた。

## 逸脱と判断

- タスク担当（S-03）：D-03 の 4 は「`hide()` で `applySnap()` を呼ぶ」だが、前に下からの欄を出したとき（`data-snap` があるとき）だけ呼ぶ形にした。下からの欄を出したことのない aside は CSS の既定の高さ（58%）で開き、意味（開いたときの高さが半分）は同じ。`hide()` が配置を読まずに済み、DOM の偽物の小さなテスト（toolbar の偽物の aside には `closest` も `style.setProperty` もない）を変えずに済む。
- タスク担当（S-03）：D-03 の 7 の「足りなければ touch-action の範囲を広げる」に加えて、全面の段の `display: contents` の規則を Scope の欄の見出しだけに絞った（実機の `pointercancel` の原因。共有の規則の範囲を狭めるだけで、帯の欄だけの CSS ではない。Scope の欄の見え方は同じ）。
- タスク担当：S-01 の後に回していた全体のテスト（`.workbench/pytest-s01.log`）と、最初のキャンペーン iss-00650 のテストの組は、統括の範囲の追加で使わなくなったので途中で止めた（重複して同時に走らせないため）。そのキャンペーンのレビューは `f7655ea8c` で合格（P0〜P3 0）だったが閉じていない。新しいキャンペーン iss-00650-r2 で全範囲をやり直す。

- 同じセッションの例外：light で手順が2つ、画面の JS の1行の変更なので、タスク担当（Claude Opus 5.5 / medium、依頼書が画面のコードに指定する値と同じ）が実装した。実装担当は起動していない（plan.cue の execution に記録）。
- `data-tab="agents"` はチャットの枠があるときだけ付ける（依頼書の「チャットを開けません。の表示は変えない」を余白まで保つため。requirement の decisions）。

## Verification

- 節目：`uv run pytest tests/unit/presentation/test_dashboard_graph_command_screen.py tests/unit/presentation/test_dashboard_allgraph_command_screen.py tests/unit/infra/test_dashboard_agents_tab_js.py` 81 passed。`make lint` exit 0。
- 実機（T-02、2026-11-17）：直す前は基準のコミット `92e26aff7` を `git archive` して隔離した venv に入れ（127.0.0.1:18651）、直した後はこの worktree を隔離した venv に editable で入れた（18650、`--tailscale`）。どちらも、この PC の状態の置き場の写しと、試しの `XDG_CONFIG_HOME`（`orca_web.port` 18850）と、常駐の orca-web を GET で読むだけの中継（`relay_orca.py`、18850）。headless Chrome は `--disable-features=MacAppCodeSignClone`、終わりに CDP の `Browser.close`。常駐の 47800・8791 の設定、道具の環境には触れていない。エージェントには何も送っていない。帯の「main のチェックアウト」の統括の印を押して測った（`.workbench/iss-00650/measure.mjs`、`measure.jsonl`）。

| 画面 | 大きさ | 前：iframe の高さ / 本文の内側 | 後：iframe の高さ / 本文の内側 | 後の本文の余白 |
|---|---|---|---|---|
| 構造の図 | 1440×900 | 240 / 745 | 761 / 761 | 4px 10px 10px（タブと同じ） |
| 構造の図 | 390×844 | 240 / 406 | 430 / 430 | 2px 4px 4px（タブと同じ） |
| 横断の構造 | 1440×900 | 240 / 745 | 761 / 761 | 4px 10px 10px |
| 横断の構造 | 390×844 | 240 / 406 | 430 / 430 | 2px 4px 4px |

  - 本文の内側は「本文の高さ − 上下の余白」。後はどれも差 0px（受入の差 2px 以内）。縁取り 1px solid、角丸 8px はエージェントのタブと同じ（scope_tabs.css）。
  - 線の検査：構造の図の `specdockEdgeAudit` の違反（boxHits・ownHits・overlaps・diagonal・portShare・trunkOverlaps・frameExits・failed・missing・markOverflow）は前後とも 0、『横断の構造』は7つのリポジトリのどれも 0。`specdockCmdAudit` の `boxOverlaps`・`edgeOverlaps`・`heads` 0、`spotDrift` 0.4〜0.5（前後で同じ）。横のスクロールなし。ダッシュボードのエラー0。
  - 横断の構造 1440 の後の1回で、iframe の中の orca-web の資産（`/embed/send-*.js`）の読み込みが試しの中継で `ERR_CONNECTION_RESET` になった（中継の一時の切れ。ダッシュボードの資産ではなく、ほかの7回は0）。横断の構造 390 の後の1回目は、押した帯の印が画面の外（別のエージェント）で欄が開かず、撮り直した。
  - 写し：`.workbench/iss-00650/shots/{one,all}-{before,after}-{1440,390}.png`。後は送る欄が欄の下に付き、会話の枠が見出しの下から欄の下まで広がる。
- 本人が見る試しの URL：tailnet の 18650 の `/r/github.com/chemitaro/spec-dock/graph`（構造の図）と `/graph`（横断の構造）。止め方：`.workbench/iss-00650/state/dashboard/server.json` の pid（または `pkill -f "port 18650 --state-root"`）と、`relay_orca.py` の2つ（127.0.0.1 と tailnet の 18850）。直す前のサーバー（18651、127.0.0.1 だけ）も比べのために残す。

- 実機（T-04、2026-11-18、後は `85930f177` の資産）：390×844 の Chrome（モバイルの見立て、タッチの見立て）で、CDP の `Input.dispatchTouchEvent` で、開く → つまみのタップ → もう一度のタップ → 見出しを 300px 上へ引く → 見出しを下の端まで引く、を3つの欄で行った（`.workbench/iss-00650/sheet.mjs`、`sheet.jsonl`、写し `shots-sheet/`）。欄の高さ（px）と `data-snap`、`pointercancel` の数：

| 欄 | 前（`92e26aff7`） | 後 |
|---|---|---|
| Scope の欄 | 開く 490 half → タップ 844 full → タップ 490 half → 上へ 844 full → 下へ 閉じる（cancel 0） | 同じ |
| 帯の欄 | 開く 490 → タップ 490（変わらず）→ タップ 490 → 上へ 490（cancel 1）→ 下へ 490、開いたまま（cancel 2） | 開く 490 → タップ 844 full → タップ 490 half → 上へ 844 full → 下へ 閉じる（cancel 0。印の aria-pressed と線の強調も0になる） |
| 片付けの候補の欄 | 帯の欄と同じく動かない | Scope の欄と同じ |

  - 全面の段の帯の欄は、見出しの行（印、`claude · main のチェックアウト`、閉じる）が上に1行で残り、チャットが下まで広がる（`shots-sheet/band-after-up.png`）。

## Residual Risks / Follow-ups

- なし。
