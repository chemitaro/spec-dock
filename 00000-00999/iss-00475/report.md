---
種別: レポート（Issue）
ID: "iss-00475"
関連GitHub: ["#475"]
最終更新: "2026-10-31"
依存: ["requirement.md", "design.md", "plan.md"]
---

# Result Summary

詳細: [Report Guide](../../../docs/authoring/report.md)

## Outcome

説明資料を、Markdown だけを持つ薄い HTML で書けるようにした。デザインシステムを SpecDock の配布資産として配り、図の部品をパッケージに同梱した。

- **デザインシステム**（R-01、R-03、R-04）：`src/spec_dock/assets/spec_dock/design-system/`（dogfood の写し `spec-dock/design-system/`）に `ds.css`、`ds.js`、`vendor/marked.umd.js`、`vendor/marked.LICENSE.md` を置き、`static-inventory.json` に登録した。`static_assets.py` の許す場所に `spec-dock/design-system/` を足した。`ds.css` と `vendor/` は、利用者のスキル japanese-explanatory-html 1.0.0 とバイト一致（写した時に `shasum` で確かめ、テストは SHA-256 の固定値で縛る）。`ds.js` は4か所だけ直した：版 `1.0.0+specdock.1`、テーマと文字の大きさの先の設定と UD フォントの読み込み、`marked` を `ds.js` と同じ場所の `vendor/` から読む、図の部品を `<meta name="ds-vendor-base">` の手元の場所、CDN の順に試す（`__dsState.vendor` に読み込み元を示す）。
- **雛形**（R-02）：`spec-dock/design-system/explanation-skeleton.html`（約 1.5KB）。`ds-source` が1つで前付けに `title`、`../../../design-system/ds.css` と `ds.js` だけを読み、印 `<!-- spec-dock:explanation-skeleton -->`、PlantUML の図1つ、`sh` のコードの囲み1つを持つ。置き換えの印は持たない。置き場は統括の決定（案A、2026-10-31）による。
- **図の部品**（R-05）：`src/spec_dock/assets/vendor/` に `@plantuml/core` 1.2026.6（`plantuml.js`、`viz-global.js`、`emoji.js`、`openiconic.js`、`LICENSE`）と `@highlightjs/cdn-assets` 11.11.1（`highlight.min.js`、`LICENSE`）。npm の tarball を `.workbench/` の新しい空のディレクトリに取り、integrity を npm の値と照らし、展開だけを行った。`manifest.json` に、取得元、integrity、各ファイルの SHA-256 と内容の型を記録した。利用者のリポジトリには入らない（目録に載せない）。
- **入口**（R-06）：`spec_dock.runtime.infra.diagram_vendor`（`DIAGRAM_VENDOR_META_NAME`、`DiagramVendorFile`、`diagram_vendor_files()`、`read_diagram_vendor_file(path)`、`DiagramVendorError`）。目録にない道筋は `None`、SHA-256 の食い違いと欠けた部品は `DiagramVendorError`。
- **ブラウザー検査の道具**（R-08）：`tests/browser/explanation-check.mjs` と `tests/browser/README.md`。Node の組み込みの WebSocket だけで CDP を使い、外への要求をすべて止める。pytest には入れていない（R-E4）。
- **既存テストの更新**：`tests/integration/test_issue413_assets.py` の、配布資産の数を固定で数える2か所（87→92、88→93）。資産を足すと必ず変わる数で、iss-00436 でも同じ形で更新した前例がある。振る舞いの検査は変えていない。

コミット：`46f3d8dbe`（図の部品と入口）、`1bd72b784`（デザインシステム、雛形、検査の道具）、`7a0a919d0`（レビューの指摘の修正と資産数の更新）、`12dc01d2f`（整形）。

## Verification

- **ブラウザー検査**（AC-05、AC-05b、AC-06、AC-07。`12dc01d2f`、macOS の Google Chrome、headless、外への要求をすべて遮断）：`node tests/browser/explanation-check.mjs` で6場面すべて合格（`VALIDATED`）。
  - `canonical-file`、`initiatives-file`：`file:` で `spec-dock/.canonical/…` と `spec-dock/initiatives/…`（リンク）から開き、図1つを描画、部品は `cdn`（検査の中で同梱の部品を返した）、390px ではみ出しなし。
  - `local-http`：`meta` で `/vendor/` を示し、手元のサーバーから同梱を配る。CDN は遮断。図を描画、部品は PlantUML、highlight.js ともに `local`。
  - `local-fallback`：`meta` が部品のない場所を示すと、CDN に移って描画（`cdn`）。
  - `offline-standalone`：本文は描け、図の位置に読み込めなかった理由が出る。捕まえていない誤りなし。
  - `missing-marked`：`ready` は偽のまま、`__dsState.error` と、`installation update` を示す知らせが出る。
  - dogfood の写し（`--design-system spec-dock/design-system`）でも6場面合格。
  - 否定の確かめ：内蔵形式の Epic の説明資料を、CDN の代わりなしで検査すると `FAILED`（図2つが描けない）になり、道具が素通しでないことを確かめた。
  - 検査の後に Chrome のプロセスが残っていないことを確かめた。
- **pytest と lint**：最終品質ゲートの節を見る。
- **仕様のレビュー**：spec-review（opus / high）第1回 合格（P2 4件を反映）、第2回 合格（P3 2件を反映）。
- **コードのレビュー**：code-review（opus / high、規約と仕様の2人）、どちらも合格。P3 2件（Chrome の起動待ちの時間切れで Chrome が残る、欠けた部品で `OSError` が漏れる）を `7a0a919d0` で直した。

### 最終品質ゲート

（ゲートの結果をここに書く）

## 未確認

- Linux の Chrome での、ブラウザー検査の道具の動き（macOS でだけ確かめた）。
- 実際の main のチェックアウトの `spec-dock/.canonical/` から開いたときの描画（main にはまだデザインシステムがない。同じ深さの見本の木で確かめた）。I-7 で `installation update` した後に確かめられる。
- `emoji.js`、`openiconic.js` を使う図（絵文字、アイコン）の描画。同梱はしたが、検査の見本の図は使っていない。

## Residual Risks / Follow-ups

- **手元のテストの環境**：作業用の worktree では、`spec-dock/initiatives` がカタログへのリンクなので、`tests/unit/infra/test_authoring_kit_assets.py` の `*_guide_link_resolves_from_rendered_node_location`（12件）が、`resolve()` がリンクをたどって落ちる。この Issue の変更とは関係しない（関係するテストと雛形は変えていない）。リンクのない clean な checkout では通る。別の Issue で、テストを直すか、リンクのある環境を想定するかを決める必要がある。
- **並行の Issue との衝突**：`static-inventory.json` と、資産数を固定で数える `test_issue413_assets.py` の2か所は、配布資産を足す I-3 などとも衝突する。後からマージする側が、数を足し直す。
- **派生した `ds.js`**：元のスキルの版を取り込むときは、冒頭の注の4か所を当て直す。
- **`@plantuml/core` の版を上げる**：`manifest.json`、`ds.js` の `PLANTUML_VERSION`、テストの期待の道筋を一緒に変え、ブラウザー検査の6場面を通す。
- **引き渡し**：I-3 は雛形を `templates/cue/<種類>/explanation.html` にバイト一致で写す。I-5 と epic-00427 は `meta[name="ds-vendor-base"]` を出し、`diagram_vendor` の入口で `/…/plantuml/1.2026.6/…` などを配る。統括は Epic の design.md の K5 に、雛形の置き場と `meta` の契約を追記する。
