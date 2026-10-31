---
種別: 実装計画書（Issue）
ID: "iss-00475"
関連GitHub: ["#475"]
状態: "draft"
最終更新: "2026-10-31"
依存: ["requirement.md", "design.md"]
---

# iss-00475 Ship Explanation Design System — 実装計画

詳細: [Issue Plan Guide](../../../docs/authoring/issue-plan.md)

## Planning Level

- **選んだ level**：standard（Epic の計画書で決めた値。[standard Completion Guide](../../../docs/authoring/issue-plan-levels/standard.md)）。
- **理由**：読むだけの描画の部品と、新しい配布資産を足すだけで、既存のファイル、CLI の命令、データを変えない。PR を戻せば元に戻る。
- **risk factor**：配布資産の目録と canonical check の規則5（dogfood の写しを忘れると、spec-dock 自身の検査が落ちる）。I-5 と epic-00427 との契約（`meta` の名前と配置）。リポジトリが約 10.5MB 重くなる。
- **再評価の条件**：CLI の命令や出力、既存の配布資産、`templates/` を変える必要が出たら、strict に上げ、統括に聞く。

## 目標

要件定義書の AC-01〜AC-08 を満たす。

## 順序・依存

1. 図の部品の取得と目録（ほかのすべての前提）。
2. 入口 `diagram_vendor.py` とテスト（1 に依存）。
3. デザインシステムの写しと `ds.js` の直し、雛形、目録への登録、dogfood の写し（1 の版に依存）。
4. ブラウザーでの検査の道具（2、3 に依存）。
5. 全体の確かめ、レビュー、最終品質ゲート、PR。

2 と 3 は、並べて進めてよい。依存する他の Issue はない（Epic の計画書）。

## 実装step

各 step は、`tdd` の Red → Green → Refactor で進める。テストの置き場は `tests/unit/infra/`（静的資産、入口）と `tests/integration/`（wheel、`installation init`）。

- **S-01 図の部品**：`.workbench/` の新しい空のディレクトリに、npm の tarball（`@plantuml/core` 1.2026.6、`@highlightjs/cdn-assets` 11.11.1）を取り、integrity を npm の値と照らす。展開だけを行い、中のスクリプトを実行しない。design の 4 のファイルを `src/spec_dock/assets/vendor/` に写し、`manifest.json` を書く。
- **S-02 入口**（AC-04）：Red：一覧と目録の一致、SHA-256、利用許諾、目録にない道筋と `..`、中身を変えた部品、目録の壊れのテスト。Green：`runtime/infra/diagram_vendor.py`。
- **S-03 デザインシステム**（AC-01、AC-03）：Red：5つのファイルが目録にあり、dogfood と一致し、`ds.css` と `vendor/` が元と一致する（元の SHA-256 を固定値で持ち、元があればバイトでも比べる）。`ds.js` の版の定数が部品の目録と一致する。`installation init` で置かれる。Green：写し、`ds.js` の直し（design の 2）、`static_assets.py` の許す場所、`static-inventory.json`、`spec-dock/design-system/` の写し。
- **S-04 雛形**（AC-02）：Red：R-02 の4条件のテスト（HTML を解析する）。Green：`explanation-skeleton.html`（元の `document-skeleton.md` に倣った節と、PlantUML の図1つ）。
- **S-05 wheel**（AC-04）：作った wheel に部品と目録が入るテストを足す（新しいテストとして足し、今のテストは変えない）。
- **S-06 ブラウザーの検査の道具**（AC-05〜AC-07）：`tests/browser/explanation-check.mjs` と、使い方の `tests/browser/README.md`。5つの場面を手元で通し、結果を報告書に書く。

## 検証

- 通常の経路：`uv run pytest`（全体）、`make lint`。
- ブラウザー（手元、外へのネットワークを止める）：`node tests/browser/explanation-check.mjs`（5つの場面）。spec-dock の dogfood の写しを使い、実際の `spec-dock/initiatives/` と `spec-dock/.canonical/` の深さで開く場面を含む。
- negative test：目録にない道筋、`..`、中身を変えた部品、目録の壊れ（pytest）。`meta` も CDN もない、`marked` がない（ブラウザー）。
- 外の依存を使えないときの確かめ：Chrome や Node.js がない環境では、ブラウザーの検査は行えない。そのときは報告書に「未確認」と書き、pytest の静的な検査だけを証拠にする。
- 回帰：今のテストを変えずに通す。`spec-dock/templates/<種類>/` が変わっていないことを `git diff` で確かめる。

## rollback

- PR を戻す。データの移行はない（N/A。新しいファイルを足すだけ）。
- 利用者のリポジトリに入った `spec-dock/design-system/` は、前の版では知らないファイルとして残るだけで、動きに影響しない。

## security / privacy / operability

- 外の部品を同梱するので、取得元の npm の integrity と、各ファイルの SHA-256 を目録に残す。入口は、目録の道筋だけを返し、SHA-256 の食い違いを誤りにする（道筋の横取り、中身の差し替えを防ぐ）。
- PlantUML の図のソースは、ブラウザーの中で描き、外へ送らない（元の動きのまま）。
- 利用許諾（MIT、BSD-3-Clause、marked の MIT）のファイルを同梱する。

## exit / handoff

- 完了の条件：AC-01〜AC-08、レビュー、最終品質ゲートに合格し、マージできる PR がある。`report.md` に、確かめたこと、未確認のこと、残るリスクがある。
- 引き渡し：
  - I-2：説明資料の形の検査は、design の 3 の形を見る。
  - I-3：`spec-dock/design-system/explanation-skeleton.html` を、`templates/cue/<種類>/explanation.html` にバイト一致で写す。
  - I-5 と epic-00427：`meta[name="ds-vendor-base"]` と、その下の配置、`diagram_vendor.py` の入口。
  - 統括：Epic の design.md の K5 に、雛形の置き場と `meta` の契約を追記する（統括が行うと連絡済み）。
- 残るリスク：`@plantuml/core` の版を上げるときの当て直し、`ds.js` の派生の管理（design の risk）。
