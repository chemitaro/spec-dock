---
種別: レポート（Issue）
ID: "iss-00532"
関連GitHub: ["#532"]
最終更新: "2026-11-04"
依存: ["requirement.cue", "design.cue", "plan.cue"]
---

# Result Summary

詳細: [Report Guide](../../../docs/authoring/report.md)

ダッシュボードのホームの構造の図（`views/graph.js`）と時間の軸（`views/timeline.js`）を、試作 d2 の見た目と振る舞いで作った。依存の線は試作の `ROUTER` を DOM なしの ES モジュール（`views/graph/router.js`）に移し、配置も DOM なしの関数（`views/graph/layout.js`）で座標を計算する。試作の `edgeAudit` を pytest から node で走らせるテストに持ち込み、代表のデータ（spec-dock の構造のスナップショットと、生成した250件）のすべての表し方の組み合わせで違反0件を確かめた。

## Outcome

### 作ったもの（提供側）

- `src/spec_dock/assets/dashboard/views/graph.js`：構造の図の画面。入れ子と木の切り替え、範囲の絞り込み（`?focus=<ID>`）、依存の線の3つの切り替え（待っている線・すべての線・線なし）、終わったものの切り替え、片付けの候補を畳む（既定は畳む。開いた配下を持つ閉じた親は畳まない）、状態の印での強調（絞り込まない）、段と後に続く数、選んだときの上流・下流の強調（`scopes/<ID>` の API）と「大もと」の札、要点の欄（PC は右、640px 以下は下から）、PC のダブルクリックとスマートフォンの2回目のタップで詳しい画面へ、凡例、変化の印、拡大・縮小・移動、2本指のつまみと `gesturestart`／`gesturechange`／`gestureend` の抑止、操作の帯の下の余白（#527 P-5、P-6）。ブラウザーの確かめ用に `edgeAudit()` を書き出し、`window.specdockEdgeAudit` にも置く。
- `views/graph/router.js`：試作の ROUTER（直交の可視グラフ、曲がりの罰則つき A*、8px の車線への寄せ、箱から10px、角の R=7、交差の切れ目）。試作から足したもの：一方の向きだけを塞ぐ障害物（`lane: "v"`／`"h"`。木の親子の線）、図の端の通り道の `widen`、0.5px 未満のずれの整え、一直線の点の繰り返しの消去（斜めの線分の原因だった）、端どうしが近い線分を同じ束に入れる罰則、出入りの位置の格子（下の「試作からの変更」）。
- `views/graph/layout.js`：見せる Scope、枠と箱、段の列（6列を超えたら折り返し）、推奨順（`rank`）、片付けの候補のまとまり、木の字下げの一覧と親子の線、依存の組。隙間を位置ごとに広げて最大8回引き直す `routeLayout`。
- `views/graph/marks.js`：図だけが使う印（PR、CI、マージできるか、保証の段、段、後に続く数、worktree、変化）とアイコン。状態の5つの記号は骨組みの `core/ui.js` の `STATES`／`stateIcon` をそのまま使う（#531 と共通）。
- `views/timeline.js`、`views/timeline/series.js`：4つの数、種類（Initiative、Epic、Issue）を選べる週ごとの累計の図（点を指すとその週の数）、Scope と PR の最近の動き（日ごと、新しい順、押すと詳しい画面）。
- `views/graph.css`、`views/timeline.css`：試作の CSS を `.gx`／`.tl` の下に閉じ込めて移した。
- `runtime/presentation/dashboard_api.py`：構造の API の項目の追加（下の「契約の変更」）。

### 契約の変更（0.6.0 の移行の注記に要るもの）

構造の API（`specdock.dashboard/v1`。形は契約にしていない）に項目を足しただけで、既存の項目は変えていない。

- `structure` の `scopes[]` と `scopes/<ID>` の `scope`：
  - `blocked_by`：その Scope が宣言した、このリポジトリの Scope の待ち先の ID の配列（番号の順）。
  - `stage`：`{"all": n|null, "open": n|null}`。親の子（親がなければ最上位）の中での段（モデルの `child_stages`）。循環なら `null`、`open` は閉じた Scope で `null`。
  - `rank`：推奨順（`recommended_key`）での全 Scope の中の位置（0始まり）。
  - `assurance`：常に `null`（文字列 `light`／`standard`／`strict`／`critical` の予定）。
  - `branch`：常に `null`（このPCの worktree のブランチ名の予定）。
- `structure` の `timeline.weeks_by_kind`：`{"initiative": [...], "epic": [...], "issue": [...]}`。各要素は `weeks` と同じ `{week_start, created, closed}`。
- `scopes/<ID>` の `downstream_all`：`{direct, indirect}`。閉じたものも含む下流（`downstream_ids(open_only=False)`）。
- 画面の道：構造の図の `?focus=<ID>`（範囲の絞り込み）。

### 作業者の判断

- 配置は CSS の流れに任せず、座標を JS で計算して絶対の位置に置いた（node のテストとブラウザーで同じ矩形を検査するため）。箱の高さは題名2行分で固定。
- 試作からの変更：出入りの位置を、出口は16px の格子、入口はそれから8px ずらした格子に置く（試作は10px の間隔）。寄せで動かない端の線分どうしが重なる違反が実データで出たため。1つの辺の線が多いときは、その箱（枠の見出し、畳んだまとまり）を高くする。
- 隙間は入れ物ごとでなく、入れ物の i 番目の隙間ごとに広げる（入れ物全体で広げると、最上位の間隔が数千px に膨らんだ）。割り当てられない通り道は、その向きの隙間を全体で少し広げる。
- 生成の250件の見本は、実データに合わせて親をまたぐ依存を2%にした（spec-dock の実データでは依存195件のうち194件が同じ親の中）。
- 木では片付けの候補を畳まない（畳む道具は入れ子のときだけ）。
- 統括の判断（2026-11-04）：保証レベルとブランチは `null` の項目だけ（値は統括が後で手当て）。node がないとき、テストは `CI` があれば失敗、なければ理由つきの skip。検索は #531 が作り、`app.js` は触らない。

### 骨組みについての観察（#529 の担当、この Issue では骨組みを変えていない）

- PC では `.mtabs` と知らせの帯が `display:none` になり、`<main>` が格子の高さ auto の行に入って高さ0になる。構造の図と時間の軸は、自分の CSS で `.main[data-view="graph"|"timeline"] { grid-row: 4; }` を指定して避けた。ボードなど #531 の画面も、中身の高さで決まる画面でなければ同じ影響を受ける。
- スナップショットのないリポジトリでは、骨組みの「見た」の `POST` が 409 を返し、ブラウザーの記録に1件のエラーとして出る。

## Verification

- `spec-dock scope check iss-00532`：誤り 0、警告 0。
- 仕様のレビュー（spec-reviewer opus/high）：1回目 fail（P1 1件：既定の畳みが開いた配下を持つ閉じた親まで畳む。P2 4件、P3 2件）→ 直して2回目 pass（P0・P1 なし、P3 1件。直した）。`.workbench/spec-review/iss-00532/`。
- コードのレビュー（code-reviewer opus/high、standards と spec の2人、`26daeb90f`）：両方 pass。P2 2件（離れた後の応答が古い強調を残す、読めないスナップショットで「まだ Scope がありません」と出る）と P3 1件（CSS の3つの規則が `.gx` の外に漏れる）をすべて直した（`9953a7040`）。`.workbench/code-review/iss-00532/`。
- テスト：`tests/unit/presentation/test_dashboard_api_graph.py`（API の項目6件）、`tests/unit/presentation/test_dashboard_graph_js.py`（node：代表のデータの線の検査、250件が1秒以内、配置、3つの線の切り替え、時間の軸の集計。10件）、`tests/js/dashboard_graph_check.mjs`、`tests/support/dashboard_graph.py`、`tests/fixtures/issue532/spec-dock-snapshot.json`（2026-11-04 の spec-dock の構造のスナップショット、版1）。
- 線の検査（node）：spec-dock と250件の見本のそれぞれで、表し方の16通り（入れ子・木 × 終わったもの × 線 × 畳む）と、開いた Epic・Initiative への絞り込みのすべてで、ほかの箱への当たり、自分の箱への当たり、車線の重なり、斜め、出入りの衝突、親子の線に沿う重なり、経路の失敗が0件。
- PC のヘッドレスの Chrome（CDP、`--disable-features=MacAppCodeSignClone`、`Browser.close` で終了）。サーバーは一時の状態の置き場（`XDG_STATE_HOME` をスクラッチの下）で立て、利用者の `~/.local/state/spec-dock/` は使っていない。仕組みと結果：[check.mjs](artifacts/20261103t201203z--check.mjs)、[cdp.mjs](artifacts/20261103t201203z-01--cdp.mjs)、[setup.py](artifacts/20261103t201203z-02--setup.py)、[結果](artifacts/20261103t201203z-03--result.json)。最終のコード（`9953a7040`）での結果：
  - PC（1440×900）と 390px、明るい・暗いの4通りで、2つの画面の `scrollWidth` が幅以内、JS のエラー0件（R-12）。写し：[PC 明るい](artifacts/20261103t201204z--pc-light-graph.png)、[PC 暗い](artifacts/20261103t201204z-01--pc-dark-graph.png)、[390px 明るい](artifacts/20261103t201204z-02--390-light-graph.png)、[390px 暗い](artifacts/20261103t201204z-03--390-dark-graph.png)、[時間の軸 PC](artifacts/20261103t201206z--pc-light-timeline.png)、[時間の軸 390px 暗い](artifacts/20261103t201206z-01--390-dark-timeline.png)。
  - DOM の矩形に対する `edgeAudit`：4通りのホームと、spec-dock・250件の見本の8通り（入れ子・木 × 終わったもの × 待っている線・すべての線）の20回すべてで0件、配置と DOM のずれ0px（R-02）。
  - 状態の印「着手できる」で、その5件だけが目立ち、ほかは残ったまま淡くなる。もう一度押すと戻る（R-06）。
  - 止められている iss-00534 を押すと、その箱だけに3px の縁、直接の線5本が太く、間接3本が細く、関係のない箱8件（ホームの Issue の箱15件のうち）が淡く、大もとの札が4件（iss-00530〜00533）、右に要点（理由「#530・#531・#532・#533 を待つ」）。その後に状態の印を押すと選択が外れ、印の見え方だけになる（R-07）。[写し](artifacts/20261103t201204z-04--pc-select.png)。
  - Epic に絞ると `?focus=epic-00080`、道筋と「全体へ戻る」が出て、戻ると全体に戻る（R-06）。[写し](artifacts/20261103t201205z-02--pc-focus.png)。
  - 木：枠0、箱39（終わったものを隠し、開いた配下を持つ閉じた親を残す）、畳む道具は出ない（R-01、R-04）。[写し](artifacts/20261103t201205z--pc-tree.png)。
  - 終わったものも・すべての線：線130本のうち終わった依存122本が破線（4px 3px）。線なしで0本（R-03）。[写し](artifacts/20261103t201205z-01--pc-done-all.png)。
  - 片付けの候補のまとまりを押すと、要点の欄に候補の一覧と理由が出る（R-04）。凡例が開く（R-09）。[写し](artifacts/20261103t201205z-03--pc-legend.png)。
  - PC のダブルクリックで `/r/…/scopes/iss-00407` へ移る。Enter で選び、Esc で外れる。Ctrl とホイールで図だけが拡大し、`visualViewport.scale` は 1 のまま。
  - 390px：1回目のタップで選んで要点が下から出て（画面は移らない。選んだ箱は要点の上へ動く）、同じ箱の2回目のタップで詳しい画面へ移る。2本指のつまみを模した入力で図の倍率だけが 74% → 200% になり、`visualViewport.scale` は 1 のまま。`gesturestart` と `gesturechange` が `preventDefault` され、図の領域の `touch-action` は `none`。1本指のドラッグで動く（R-08）。[写し](artifacts/20261103t201205z-04--390-tap1.png)。
  - 開いたとき、「全体」の後、絞り込みの後に、どの箱の上端も操作の帯の下端より下（P-6）。
  - 変化の印：見た後に状態が変わった iss-00004 と新しい iss-00005 に印が付き、上の帯の数が2件（R-10）。[写し](artifacts/20261103t201205z-05--pc-changes.png)。
  - 時間の軸：作られた308、終わった270、開いている38。点を指すとその週の数。Issue を外すと累計が34／11 になる。最近の動きに Scope と PR（#900〜#904 の見本）が新しい順に並び、押すと詳しい画面へ移る（R-11）。
  - 速さ：250件の見本で、開いてから線が出るまで約110ms、終わったものも出す描き直しが約40ms（R-13）。
  - スナップショットのないリポジトリでは、2つの画面とも「構造のスナップショットがないか読めないため…」と出て、知らせの帯に `SNAPSHOT_MISSING` が出る（F-01）。
- 手元だけの追加の検査（ほかの実リポジトリの構造。私的なデータなのでテストには入れていない）：housing-lifecycle、input-devices、taikyohiyou_project を含む171通りのうち167通りで0件。残る4通りは下の「残る課題」。
- `make lint` と `uv run pytest`（全体）：最終品質ゲートの節を見る。

## Final Quality Gate

- 合格のコミット：`e23291cf4844af72eae6d8b1f7b8768d4ffc3dda`（作業ツリーは clean）。記録は `.workbench/final-quality-gate/iss-00532-g1/`（`campaign.json`、`closure.md`、`attempts/01〜03/`）。
- 試行：01（`9953a7040`）レビュー pass。#531 のマージで全体のテストを止めて取り込み直した。02（`6aa34f2ec`、#531 の取り込み。`dashboard_api.py` の `rank` の競合を両方の意図を残して解いた）レビュー pass。#533 のマージでテストを止めて取り込み直した。03（`e23291cf4`、#533 の取り込み。競合なし）で両方の道が合格。
- レビューの側：quality-gate-reviewer（opus/high、1人）。観点は functional-correctness、requirements-closure、test-adequacy。pass（P0 0、P1 0、P2 0、P3 2、網羅は完全）。
- テストの側：`make lint` 終了コード0（ruff check、ruff format check、mypy すべて pass）、`uv run pytest` 終了コード0（3464 passed、7 skipped、25分11秒。node の線の検査10件を含む）。どちらも同じコミット。
- P3（情報。直していない）：(1) 入れ子で畳む既定のまま、片付けの候補（配下がすべて終わった Epic）に絞ると、その Epic 自体がまとまりに畳まれ、枠も配下も出ない。(2) node の線の検査の絞り込みの組み合わせは、閉じていない Epic と Initiative だけ（D-07 の「各 Epic」より狭い）。
- マージの後のブラウザーの確かめ：`6aa34f2ec`（#531 の取り込み後）で全項目をやり直して同じ結果（[結果](artifacts/20261103t203009z--result-after-merge.json)）。#533 の取り込みは画面と構造の API に触れていない（差分は撤去したファイルだけ）ので、ブラウザーの確かめはやり直していない。

## Pull Request

- PR #543（https://github.com/chemitaro/spec-dock/pull/543）、head `e23291cf4844af72eae6d8b1f7b8768d4ffc3dda`（`Refs #532`、`Refs #427`）。CI は観測できた範囲（Actions と Commit Status）で PASS：Provider CI、SpecDock check、Commit identity。GitHub のマージの可否は READY（2026-11-03T21:38:04Z の観測）。マージと `work finish` は統括が行う。

## Residual Risks / Follow-ups

- iPhone の Safari の実機での表示、2本指のつまみ、2回目のタップは確かめていない（#534 で利用者に頼む）。PC の Safari も未実施。
- 手元だけの検査で、終わったものとすべての線を同時に出す既定でない組み合わせの4通り（housing-lifecycle の入れ子1通り、taikyohiyou_project の入れ子1通り・木2通り）に、車線の重なりが1〜8件残った（8回の引き直しで隙間が収まらない）。この2つのリポジトリでも、既定の表示と、どちらか一方だけを出した表示は0件。taikyohiyou_project で線284本を出すと配置と経路に約2.4秒かかる（R-13 の3秒以内）。
- 保証レベルとブランチの印は、統括が API に値を入れるまで出ない。
- 骨組みの格子で `<main>` が高さ0になる件と、スナップショットのないリポジトリでの「見た」の 409（上の「骨組みについての観察」）は、骨組みの担当で扱う。
- 試作の残った課題のうち「親をまたぐ依存で左右の並びが崩れるときは、矢印の向きでしか分からない」はそのまま。
- 最終品質ゲートの P3 の2件（上の節）。(1) は、絞った Scope を畳みから外す小さな直しで済む見込み。
- 状態の印や PR の印などの部品は、#531 の `views/_shared/parts.js` と一部が重なる（状態の記号は両方とも `core/ui.js` の `STATES`／`stateIcon`）。重なりの整理は統括の判断で後に行う。
