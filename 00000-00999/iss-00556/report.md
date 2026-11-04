---
種別: レポート（Issue）
ID: "iss-00556"
関連GitHub: ["#556"]
最終更新: "2026-11-04"
依存: ["requirement.cue", "design.cue", "plan.cue"]
---

# Result Summary

詳細: [Report Guide](../../../docs/authoring/report.md)

## Outcome

構造の図（ホーム）の既定の表示を、利用者の 2026-11-04 の決定（epic-00427 plan.cue の slice `iss-00556`）に合わせた。提供側の変更だけで、配布資産の文書、`static-inventory.json`、版の番号、`migration.md` は変えていない。

1. **見せる範囲（R-01）**：`views/graph/layout.js` の可視の判定。終わった Scope は、親が終わった子を出す（`showsDone`）ときに出す。`showsDone` は「終わったものも」、絞った Scope、または開いた親（ただし片付けの候補「配下がすべて終わったのに開いたまま」`all_descendants_closed` を除く）。終わった Epic は中身のない畳んだ枠（完了 n/n）になり、その孫は出ない。親も終わったもの、親のない終わったものは出ない。開いた子孫を持つ閉じた親（Epic R-12）は今までどおり残る。絞った Scope 自身は片付けの候補でも畳まない（前は畳まれて図が空になった）。
2. **依存の線（R-02）**：`DEFAULTS.deps` を `"all"` にした。図に出ている箱どうしの終わった依存は薄い線（`is-done`）、待っている依存は今のまま目立つ線。3つの切り替えは残した。
3. **並び（R-03）**：同じ段の中を活動順にした（`byActivity`）。開いた枠（配下の組：作業中を含む → 着手できるを含む → 止められている・不明だけ、同じ組は配下の最後に動いた時刻の新しい順）、開いた箱（推奨順 `rank`）、終わったもの（最近の順）。最上位の「Initiative を先に」はやめた。段は、終わった子を出す枠では `stage.all`（出ている終わった前提が左の段に入り、線が左から右へ向く）、それ以外では `stage.open`。
4. **構造の API の `active_at`（R-04）**：`presentation/dashboard_api.py` の `scope_item` に、作成、Issue の更新、完了、選ばれた PR の作成・マージ・閉じのうち最も新しい時刻を足した（読めない時刻は使わない）。詳しい画面の `scope` にも出る。
5. **保存した見せ方（R-05）**：新しい `views/graph/prefs.js`（DOM のない部品）。保存のキーを `specdock.graph.v2` にし、v1 からは `mode`・`fold`・`legend` だけを引き継ぐ。値は型と範囲を確かめ、合わなければ既定にする。
6. **ボードの終わった列（R-06）**：#531 の実装がすでに完了の時刻の新しい順（同じなら番号の大きい順）なので、コードは変えず、既存のテスト `test_board_columns_follow_lanes_and_rank` で確かめた。

### 判断（統括の了承つき）

- Epic R-15・R-31 の文言（既定は終わったものを隠す、線は待っているものだけ、同じ段は推奨順）は slice と食い違う。統括に知らせ、統括が 2026-11-04 に直した（この Issue では Epic の文書を変えていない）。
- 保存のキーを v2 にして `showDone`・`deps` を新しい既定に戻すこと、`active_at` を API で計算することは、統括が了承した。
- 片付けの候補「配下がすべて終わったのに開いたまま」の親は「開いた親」に数えない。このPCの spec-dock の構造で、この種類の Epic 12件の下に終わった Issue が106件あり、木と畳まない表示で図を埋めたため。統括が了承した。

### 0.6.0 の後の移行の注記の材料（契約の変更）

- 構造の図は、既定で、開いた親の中の終わった Scope と、図に出ている箱どうしの終わった依存の線（薄い線）を出し、活動順に並べる。
- 前に保存した「終わったものも」と依存の線の選択は、一度だけ新しい既定に戻る（ブラウザーの保存のキーが `specdock.graph.v1` から `specdock.graph.v2` に変わる。表し方、片付けの候補を畳むか、凡例は引き継ぐ）。
- 構造の API（`specdock.dashboard/v1`、公開の契約ではない）の各 Scope に `active_at` が足された。既存の項目は変わらない。

## Verification

### 仕様のレビュー（spec-reviewer opus/high）

- round 1：P1 1件（既定で出す終わった Scope の段が未決で、終わった依存の線が左から右にならない）、P2 1件（移行の注記の担当）。段の種類を `showsDone` で切り替える形に直し、注記は PR と統括への報告に書く形にした。
- round 2：合格（P3 1件。文言を直した）。
- round 3（片付けの候補の親の扱いを足した後）：合格（P2 1件：統括の了承が未記録 → 統括が了承し、decisions に書いた）。
- 記録：`.workbench/spec-review/`（packet、round-1〜3 と検証の結果、review-response.md）。

### コードのレビュー（code-reviewer opus/high、標準と仕様の2人、範囲 `ae8c72456..21d192a8d`）

- 標準：合格、指摘0件。
- 仕様：合格、P3 1件（計画 T-05 の2つの分岐、`active_at` がないときと閉じた親の中の `stage.open` のテストがない）。テストを足し（`987e26f21`）、実装をわざと壊すと失敗することを確かめた。
- 記録：`.workbench/code-review/`。

### テスト

- 足したテスト：`tests/unit/presentation/test_dashboard_api_graph.py`（`active_at`）、`tests/unit/presentation/test_dashboard_graph_js.py`（見せる範囲、終わった依存の線、活動順と段、時刻のないもの、片付けの候補の親、保存の版、線の検査）。既存の2つのテスト（既定で終わったものを隠す、絞り込み）の期待を新しい既定に合わせた。
- 線の検査の代表のデータ（spec-dock の固定のスナップショット、種 532・15・18）のすべての表し方で問題0件（既存のテスト。新しい可視の判定と既定で通る）。

### PC のヘッドレスの Chrome（このPCの実際の spec-dock のスナップショット）

- 一時の状態の置き場（`--state-root`、スクラッチパッドの下）に、このPCの `~/.local/state/spec-dock/github/github.com/chemitaro/spec-dock/snapshot.json`（318件。読むだけ）を写し、取得の時刻だけ今に動かして、`uv run spec-dock dashboard serve --port 18556` で開いた。`--disable-features=MacAppCodeSignClone`、`Browser.close` で閉じた。利用者の `~/.local/state/spec-dock/` には書いていない。
- 前の版のキーに `showDone: true`・`deps: "wait"` を保存した状態で開くと、終わったものを隠す既定と「すべての線」で描かれた（v2 は未保存）。
- `window.specdockEdgeAudit()` の違反（boxHits、ownHits、overlaps、diagonal、portShare、trunkOverlaps、failed、missing）：PC の既定（線50本、終わった線58本の要素、待っている線18本の要素）、PC の待っている線、PC の木、390px の既定のすべてで0件。ブラウザーのエラー0件。木の終わった箱は、片付けの候補の親の扱いの前は179件、後は73件。
- 同じ構造で、node の線の検査（16通りの組み合わせと、開いた Epic・Initiative への絞り込み24通り、計40通り）も問題0件、最大463ms。
- 写しと結果：[PC](artifacts/20261104t021615z--pc-graph.png)、[PC 全体](artifacts/20261104t021615z-01--pc-graph-fit.png)、[PC の木・待っている線](artifacts/20261104t021616z--pc-graph-tree-wait.png)、[390px](artifacts/20261104t021616z-01--390-graph.png)、[ブラウザーの結果](artifacts/20261104t021616z-02--result.json)、[node の線の検査](artifacts/20261104t021616z-03--node-audit-real.json)、仕組み：[check.mjs](artifacts/20261104t021617z--check.mjs)、[setup.py](artifacts/20261104t021617z-01--setup.py)。`21d192a8d` の資源で実施（その後の `987e26f21` はテストだけ）。

### 最終品質ゲート

（ゲートの後に書く）

## Residual Risks / Follow-ups

- iPhone の Safari での確かめは、統括が利用者に頼む。
- 活動順は時刻で変わるので、Issue や PR が動くと箱の位置が入れ替わる（構造の `revision` が変わったときだけ）。
- Epic R-15・R-31 の文言の直しは統括が行う。
