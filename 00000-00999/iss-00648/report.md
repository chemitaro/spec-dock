---
種別: レポート（Issue）
ID: "iss-00648"
関連GitHub: ["#648"]
最終更新: "2026-11-17"
依存: ["requirement.cue", "design.cue", "plan.cue"]
---

# Result Summary

詳細: [Report Guide](../../../docs/authoring/report.md)

## Outcome

指揮の線を、上の縁から出て上の縁へ入るホップの弧にし、子の端に下向きの矢じりと受けた印の縁を描いた。同じ箱の親子も上の縁の小さな弧（18px、余白と依存の線に合わせて下げる）。点の流れ・波紋・状態・色・帯・軽くした描き方は変えていない。Epic epic-00615 の文書を iss-00646・iss-00648 の決定に合わせた。

## Verification

## レビュー記録

- 仕様のレビュー（spec-reviewer opus / high、standard、2人目なし）：round-1 不合格（P1 2：hop の頂点のはみ出し、Epic に古い決まりが残る。P3 2）→ 直して round-2 **合格**（P0〜P3 すべて0）。結果はこの worktree の `.workbench/spec-review/iss-00648/round-{1,2}.json`・`.check.json`・`review-response.md`（reviewed_sha `92e26aff7`）。
- **合格した文書の sha256**（round-2）：iss-00648/requirement.cue `0eaa489858b3912ea7b1c10eb7acbb1a663936e15067a0c910c42368095a0487`、iss-00648/design.cue `7f624aa028e527e77393b3c03114dcc8f07dc519915a678074d4cc81deaeeb3a`、iss-00648/plan.cue `08edcc3f9c585c18a468611050610051d35a961d6760437afaa12af136c50a30`、iss-00648/explanation.html `862df12fed3328e04d3719d9e50a90bad45bd1337d10fd75cf06dc18fc984c0b`、epic-00615/requirement.cue `e2fffa69623b78b89cde0a508a681e41ba8909379d86aff2a38774ea2854b2b8`、epic-00615/design.cue `51323b73d86669e5148ffe9ed70fe9a38768393e20164838e66c36e295047b2f`。
- **仕様の変更と再レビュー**（S-03 の後の実機で、同じ箱のホップの脚が依存の線を横切り、外接の四角の定義では edgeOverlaps 1。統括の決定 msg_289b1c14b741 A）：R-03・D-03・T-01・Epic D-10 を直し、round-3 **合格**（P0〜P2 0、P3 1。reviewed_sha `489a46348`、`.workbench/spec-review/iss-00648/round-3b.json`）。P3（決定と Epic の文が『中央の半分の弧』を指し、D-03 は頂点の y で判定する）は、数えるものが D-03 と受入で一意に決まるので文書は変えない（実装は D-03 に従う）。
- **今の合格した文書の sha256**（round-3）：iss-00648/requirement.cue `51441f5104f671774a767798044e076fe286212a924d867889e1245ba06df965`、iss-00648/design.cue `9538b0112ebddd2776cef2322d7cf8bba3f489a10764a81380c106fd65914870`、iss-00648/plan.cue `8bacb9831c6a55509f50f92be088e448a22c3aa91f7a0053ea0189286a965a56`、iss-00648/explanation.html `862df12fed3328e04d3719d9e50a90bad45bd1337d10fd75cf06dc18fc984c0b`、epic-00615/requirement.cue `e2fffa69623b78b89cde0a508a681e41ba8909379d86aff2a38774ea2854b2b8`、epic-00615/design.cue `117672e303c6db4f43d6599c6b9ad2e2b47f6a7ea289f93580f47890b331154c`。
- round-1 の間に、タスク担当が `.workbench/iss-00648/` に写しの台本と直す前の写しを足した（レビューの対象の文書は sha256 で固定していて変わっていない）。

## 実装の記録

- 開始のコミット `92e26aff7256a9a32ba6edd5bc7f790ed8e4f149`（origin/main、iss-00646 のマージ後）。
- 仕様化と S-01（Epic の文書の直し）：タスク担当（Claude Opus 5.5 / medium、統括が選んだ値）。

- S-02（impl-claude：Claude Opus 5.5 / medium。計画では impl-sol だったが、Codex が chat-scratch の symlink の拒否で何も変えずに止まったので、計画の rationale と統括の了承のとおり引き継いだ）：コミット `e823115b2`（題を直す前は `074191092`）。
  - 基準（開始のコミット `92e26aff7`、`.workbench/implement/iss-00648/start.md`）：`make lint` 合格、S-02 の節目のテスト 51 passed。全体の `uv run pytest` は30分かかるので基準では省き、S-04 で行う。
  - 変えたもの：`views/graph/command.js`（`HOP`・`hop`・上の縁の端 `fixedEnd`・`sameHop`・線の `mark` と `peak`・`top`・引数 `ceiling`。`faceOf`・`DOWN`・`SIDES` の下と左右・`contains`・`center`・`boxArc`・`frameArc`・`bandArc`・`CHORD`・`ARC_D`・`ARC_MIN`・`FRAME_ARC_D` と `roomOf` の下・右を消した）、`views/allgraph/command.js`（`crossModel` が `ceiling: 4`）、`tests/js/dashboard_graph_command.mjs`（`hop` の依頼と `HOP` の定数）、`tests/unit/presentation/test_dashboard_{graph,allgraph}_command.py`。描き方のファイルは変えていない。
  - Red：新しいテストを開始のコミットの `command.js` 2つで走らせて 22 failed・3 errors（`hop` がない）（`.workbench/implement/iss-00648/s02-red.log`）。Green：`uv run pytest tests/unit/presentation/test_dashboard_graph_command.py tests/unit/presentation/test_dashboard_allgraph_command.py` 60 passed（`s02-green.log`）。`make lint` 合格（`s02-lint.log`）。CP-1 の『S-02 の節目のテストの合格』はこれで確かめた。
  - 直した今の期待：下の端（帯の項目の下の縁・箱の下の縁・枠の見出しの印の下・枠の内側の下の縁・F-04 の箱の下の縁）→ 上の縁。`stubs`（箱の中の短い線）→ 空。`boxArc`（下・右の縁の外、16px、弦 40、右へ逃げる・依存の線から逃げる）・`frameArc`（見出しの下 12px）・`bandArc`（上 16px）→ `sameHop`（上の縁、18px、弦 12、余白 − 3 へ下げ下限 8、`crowded`）。曲線の制御点（`k = min(140, max(24, 0.45·L))`、両端の向き）→ `hop`（頂点がちょうど H 上）。`top` の `-32` → ホップの頂点を含む `-78`（`five`）。同じ枠の上の縁へ入る3本のずらし（前は2本 ±5、内側の下の縁の1本は別）→ 3本 −10・0・+10。『Epic の統括の線が枠の上の縁より上に出ない』→『枠の上の縁から出て Issue の上の縁へ入るホップ』。`boundsOf` の弧の下の縁の制限 → 上の縁の制限（16/10 → 18/10）。依存の線から右へ逃げるテスト → `edgeOverlaps` に数えるテスト。
  - 足したテスト：木の枠の箱（`tframe`）、縦に重なる印（12 に離す）、上の余白 14px（11、`crowded` 1、`boxOverlaps` 0）・6px（8、重なり1）、依存の線の水平な区間（`edgeOverlaps` 1）、子が上・同じ高さ・下、`hop` の直の計算（同じ高さ、差 700px、dx 0 の横のふくらみ、`ceiling` と `HOP.low`）、線の `mark`、`top`、横断の構造の『ほかの場所』から 500px 以上下の箱（頂点 4）。

- S-03（impl-claude）：コミット `2f7934ab0`（題を直す前は `489a46348`）。
  - 変えたもの：`views/graph/command_motion.js`（`ARROW`・`arrowPath`・`markRect`・`bandMarkHtml`、`endsHtml` は `cl-dot` の代わりに `cl-arrow` と、箱・枠の印の `cl-in` を描き、SVG の四角は矢じりと縁を含む）、`views/graph/command_view.js`（`layersHtml` が帯の子の縁を波紋と同じ `.gx-band-cr` に入れる、`paintCmdSel` が `.gx-band-cr .cl` も塗る）、`views/graph.css`（`.cl-arrow`・`.cl-in`・done の .35、`.cl-dot` の規則を消す、層の説明の注釈）。
  - Red：S-02 のコミットの上で新しいテストが 13 failed（`.workbench/implement/iss-00648/s03-red.log`）。Green：S-03 の節目のコマンド `uv run pytest tests/unit/presentation/ tests/unit/infra/test_dashboard_orca_marks_js.py tests/unit/infra/test_dashboard_orca_views_js.py tests/unit/infra/test_dashboard_screens_js.py tests/unit/infra/test_dashboard_allgraph_route.py` 394 passed（`s03-green.log`）。`make lint` 合格（`s03-lint.log`）。
  - 直した今の期待：端の層の `cl-dot`（中心が `to`、半径 2.5）→ `cl-arrow`（先が `to`）。端の層の SVG の四角（点の半径を含む）→ 矢じりの3点を含む。構造の図の最初の表示・『収める』の『帯の上 −32』→ 描いた線の頂点の最も高い所 − 6 と −32 の小さい方（D-05 の `top`。S-02 の後にこの3件が落ちていた：`s02-s03set.log`）。横断の構造の画面で、帯から出る線の始めの y（項目の下の縁 → 上の縁）と、子の端（`cl-dot` の中心が箱の下の縁 → 矢じりの先が箱の上の縁）。線ごとの SVG の層の候補に `.gx-band-cr` を足した。
  - 足したテスト：`arrowPath`（先・底・幅 7）、`markRect`（2px 外）、`endsHtml`（矢じり1つ・点なし・箱の印の縁・帯の子は縁なし・stubs が空の flow は止めた絵1枚）、`bandMarkHtml`（帯の子だけ）、CSS（`--sd-cmd`、1.5px、done .35、`.cl-dot` の規則なし、減らす設定に規則なし、薄めの規則）、構造の図と横断の構造の画面（箱・枠の子は `cl-in`＋`cl-arrow`、帯の子は `cl-arrow` と `.gx-band-cr` の縁、選びで `is-cmd-hl`・`is-cmd-off`）。
  - static-inventory.json：dashboard の資産は載っていないので直すものはない。凡例（`lg-cmd`）は範囲外で変えていない。

- S-02 の続き（仕様の変更 R-03・D-03・T-01、round-3 合格。タスク担当の依頼 msg_7027cb394ce9）：コミット `9d2afa266`（作った時は `78a7afd47`）。
  - round-3 の sha256（requirement `51441f51…`、design `9538b011…`、plan `8bacb983…`、Epic design `117672e3…`）が report.md の値と一致することを確かめてから始めた。走っていた全体の `uv run pytest`（9% まで）は止めた。
  - 変えたもの：`sameHop` の高さを、上限 u から HOP.low へ 1 ずつ下げ、頂点（`self.y1 − d`）と、弧の幅の中央の半分に x が重なる依存の線の横の区間の y との差がどれも 3 以上になる最初の値にする。なければ u で `edgeOverlaps++`。ふくらみの四角での依存の線の判定（`overlapsRoute`）は消した。
  - 直した期待：`routeAbove`（縁の 7px 上の区間で `edgeOverlaps` 1）→ 5つの例 `run10`・`run15`（18 のまま、0）、`run16`（13、0）、`runLegs`（脚の位置だけの区間、18、0）、`runNone`（9・14・18px 上、18 のまま、1）。
  - Red：S-03 のコミットの `command.js` で新しい例のうち 4 failed（`runNone` は前の判定でも 1 で通る）（`.workbench/implement/iss-00648/s02b-red.log`）。Green：S-02 の節目のテスト 64 passed（`s02b-green.log`）、`make lint` 合格。
- コミットの題の直し（タスク担当の依頼）：自動生成の題が『コマンド線』『依存線の終点』だったので、push 前に非対話の rebase（reword）で『指揮の線…』に直した。直す前の HEAD `78a7afd47`、直した後の HEAD `9d2afa266`、`git diff 78a7afd47 9d2afa266` は空（内容は同じ）。作者・コミッターは chemitaro のまま。
- S-04（impl-claude）：HEAD `9d2afa266` で S-02 の節目のテスト 64 passed（`s04-s02set.log`）、S-03 の節目のテスト 398 passed（`s04-s03set.log`）、`make lint` 合格（`s04-lint.log`）。全体の `uv run pytest`：4255 passed、7 skipped、32分45秒、exit 0（`s04-full.log`、HEAD `9d2afa266`）。直したテストの期待は、端・道・弧・端の層・`top` の変更によるものだけ。static-inventory.json に dashboard の資産はなく、直すものはない。既存の失敗はない。

## 逸脱と判断

- 観察（仕様どおり、変えていない）：横断の構造の『ほかの場所』の帯の同じ項目のホップは、帯の上の縁 y 24 と `ceiling` 4 から `room` 20、高さ min(18, 20 − 3) = 17 になり、`crowded` に 1 数える（テストの場面 `deep`。`boxOverlaps`・`edgeOverlaps` は 0）。実データで『ほかの場所』の中の親子があると、`specdockCmdAudit()` の `crowded` が 1 以上になる。
- S-02 の担当の交代：計画では impl-sol（Codex gpt-6.1-sol / medium、dispatch `ctx_17c1d5a4151a`）だったが、Codex が chat-scratch の symlink の拒否（symlinked writable roots are not supported）で何も変えずに止まった。計画の rationale と統括の了承のとおり worker-stop し、impl-claude（Claude Opus 5.5 / medium、dispatch `ctx_aec9f6b0309e`、provider claude / model opus）が S-02〜S-04 を1つのセッションで行う。CP-1 の S-02 の節目のテストの確かめは、実装担当が S-02 の後に行い、記録する。


## 実機の確かめ（S-05、2026-11-17、`9d2afa266`）

- 試しのサーバー：直す前は基準のコミット `92e26aff7` を `git archive` して隔離した venv（`.workbench/iss-00648/venv-before`、ポート 18649、ローカルだけ）。直した後はこの worktree を editable で隔離した venv（`.workbench/iss-00648/venv`、18648、`--tailscale`）。どちらも同じ状態の置き場の写し（GitHub の写しは常駐の状態から読むだけで写した）と、常駐の orca-web を GET で読むだけの中継（`relay_orca.py`、18848）。headless Chrome（9648）は `--disable-features=MacAppCodeSignClone`。常駐の 47800・8791 の設定、道具の環境には触れていない。
- 場面（実データ）：帯の統括 → iss-00648 の箱のタスク担当、iss-00648 の箱のタスク担当 → 実装担当（同じ箱）。統括に頼んだ試しのエージェント（haiku、待ちだけ）：iss-00646 の箱の親子（同じ箱）、統括 → orca-web の main の子（リポジトリをまたぐ。横断の構造では『ほかの場所』の帯から spec-dock の帯へ）。撮った後、統括が止める。
- 写し（`.workbench/iss-00648/shots/{before,after}/`、各 `*-view.png` と `*-crop.png`、`log.jsonl`・`log-cross.jsonl`）：構造の図と横断の構造 × 1440・390 × 明・暗 × 全体・いま・これから（各 24 枚の組、前と後）。試しのエージェントを入れた全体は `shots/extra/`。
  - 前：帯の統括の線は帯の項目の下の縁から下へ U 字に垂れ、箱の下の縁へ入る。同じ箱の親子は箱の下の縁の外の弧。子の端は小さな点。
  - 後：帯の項目の上の縁から上へ跳ね、箱の上の縁へ上から入る（帯の項目と間の箱の後ろを通る）。同じ箱の親子は上の縁の小さな弧（実データで 18px。頂点は上を走る依存の線から 3px 以上離れる）。子の端に下向きの矢じり、受けた印は指揮の色の縁で囲まれる。明・暗とも見える。横断の構造の『ほかの場所』からの線は天井（y 4）の内で跳ねる。
  - 11px に下がる例：実データでは出せない（worktree のある iss-00646・iss-00648 の箱は Epic の枠の1行目で上に箱がない。上に箱がある Issue はどれも閉じていて worktree がない）。統括の了承（msg_5ea853a95490）のとおり、node のテスト（T-01：上の余白 14px で 11px、`crowded` 1、`boxOverlaps` 0）で確かめた。実データの箱の上の余白は 16〜18px（依存の線の道で広がる）。
- 検査（前と後の 48 組の写しのすべて）：`specdockEdgeAudit()` の違反 0、`specdockCmdAudit()` の `boxOverlaps`・`edgeOverlaps`・`heads`・`spotMissing` 0、`crowded` 0、ブラウザーのエラー 0。`spotDrift` は 0.4〜0.5（直す前も同じ 0.4〜0.5 が出る。印の幅の測りの揺れで、この Issue の変更とは関係しない。R-05 の受入の『≤ 0.4』は、直す前と同じ値の揺れで 0.5 になる組がある）。
- 測り（iss-00646 の台本 `perf-measure.mjs`、1440×900、deviceScaleFactor 2、読み込みの15秒後から10秒の TaskDuration。前と後を交互に3回ずつ、`perf-ab.txt`）：

| 画面 | 前・動きあり | 後・動きあり | 前・減らす設定 | 後・減らす設定 |
|---|---|---|---|---|
| 横断の構造（`/graph`） | 0.06・0.01・0.01（中央 0.01） | 0.01・0.02・0.01（中央 0.01） | 0.02・0.02・0.02 | 0.02・0.03・0.05 |
| spec-dock の構造の図 | 0.01・0.01・0.01 | 0.01・0.01・0.01 | 0.01・0.01・0.01 | 0.01・0.01・0.01 |

  受入（横断 0.11 秒以下、単体 0.07 秒以下／10秒）を満たし、重さは戻っていない。
- 本人が見る試しの URL：tailnet の 18648 の `/graph`（横断の構造）と `/r/github.com/chemitaro/spec-dock/graph`。止め方：`.workbench/iss-00648/state/dashboard/server.json` の pid（または `pkill -f "port 18648 --state-root"`）、直す前の `pkill -f "port 18649 --state-root"`、中継 `pkill -f "relay_orca.py .* 18848"`（127.0.0.1 と tailnet の2つ）、Chrome は CDP の `Browser.close`（ポート 9648）。

## Residual Risks / Follow-ups

- 箱の上の余白が狭い所（同じ箱の弧が 8〜17px に下がる）は、実データの写しでは確かめていない（node のテストだけ）。
- 帯から下の箱への線は、帯の項目と間の箱の後ろを通る（統括の確認済み）。本人の確かめを受ける。
- `spotDrift` が 0.5 になる組がある（直す前と同じ揺れ）。
