---
種別: 要件定義書（Issue）
ID: "iss-00475"
関連GitHub: ["#475"]
状態: "draft"
最終更新: "2026-10-31"
---

# iss-00475 Ship Explanation Design System — 要件定義

詳細: [Requirement Guide](../../../docs/authoring/requirement.md)

表示名：説明資料のデザインシステムと図の部品を、SpecDock から配る

## 目的

Scope の説明資料（`explanation.html`）を、Markdown だけを持つ薄い HTML で書けるようにする。デザインシステムはリポジトリの共有の場所から読み、どのチェックアウトから開いても同じに描ける。PlantUML の図を描く部品（`@plantuml/core`）と、コードの色付けの部品（highlight.js）を、版を固定して SpecDock のパッケージに同梱し、ダッシュボードのサーバー（epic-00427）が手元から配れるようにする。

## 背景

- 親は epic-00425（仕様の文書を、CUE と HTML の説明資料に分ける）。この Issue は、Epic の計画書の I-4 で、Epic の設計書の契約 K5 のうち、デザインシステムの置き場、薄い説明資料の形、図の部品の読み込み先を持つ（描画の入口は I-5）。
- 今の説明資料は、利用者のスキル japanese-explanatory-html で作る。1ファイルに約 300KB のデザインシステムを内蔵し、図の部品は CDN から読む。Scope ごとに写すと重く、デザインシステムを上げても、各ファイルは古いまま残る。
- 使う側：I-2（`scope check` の説明資料の形の検査）、I-3（新しい Scope の雛形）、I-5（CUE の描画）、epic-00427（ダッシュボードのサーバー）。
- Epic の要件：R-E1（テンプレートとデザインシステムを配る）、R-F2（図の部品を版を固定して同梱する）、R-E4（ブラウザーでの描画の検査は、手元で任意）。

## 観測可能な要件

- **R-01 デザインシステムを配る**：SpecDock の配布資産として、リポジトリの `spec-dock/design-system/` に、`ds.css`、`ds.js`、`vendor/marked.umd.js`、`vendor/marked.LICENSE.md` を置く。`installation init` と `installation update` で入る。中身は、利用者のスキルのデザインシステム（版 1.0.0）の写しで、`ds.js` だけを R-03、R-04 のとおりに直す。
- **R-02 薄い説明資料の雛形**：配布資産 `spec-dock/design-system/explanation-skeleton.html` を置く。雛形は、Epic の設計書の K5 の「薄い説明資料の形」を満たす。
  - `<script type="text/markdown" id="ds-source">` がちょうど1つあり、中の Markdown の先頭に `title` を持つ前付けがある。
  - `../../../design-system/ds.css` と `../../../design-system/ds.js` を読む指定がある。ほかのスタイルやスクリプトを持たない。
  - Markdown に、印 `<!-- spec-dock:explanation-skeleton -->` がある。
  - Scope の種類ごとの置き換えの印を持たない（I-3 が、そのまま `templates/cue/<種類>/explanation.html` に写す）。
- **R-03 `marked` を `ds.js` が読む**：`ds.js` は、自分と同じ場所の `vendor/marked.umd.js` を読み込んでから、Markdown を描く。説明資料は `marked` を読む指定を持たない。
- **R-04 図の部品の読み込み先**：`ds.js` は、PlantUML と highlight.js を、次の順に試して読む。
  1. ページが `<meta name="ds-vendor-base" content="URL">` で示す手元の場所。その下の `plantuml/1.2026.6/` と `highlightjs/11.11.1/`。
  2. CDN（`https://unpkg.com/@plantuml/core@1.2026.6/`、`https://unpkg.com/@highlightjs/cdn-assets@11.11.1/`）。
  `meta` がないとき（ファイルを単独で開いたとき）は、CDN だけを使う。どこから読んだかを、ページの状態（`window.__dsState`）に示す。
- **R-05 図の部品を同梱する**：Python のパッケージの中に、`@plantuml/core` 1.2026.6 の `plantuml.js`、`viz-global.js`、`emoji.js`、`openiconic.js`、highlight.js（`@highlightjs/cdn-assets`）11.11.1 の `highlight.min.js` と、それぞれの利用許諾のファイルを置く。リポジトリの `spec-dock/` には置かない。各ファイルの SHA-256 と、取得元の npm の integrity を、目録（manifest）に記録する。
- **R-06 図の部品の入口**：パッケージの中の図の部品を、手元から配るための Python の入口を持つ。入口は、R-04 の配置（`plantuml/1.2026.6/plantuml.js` など）の相対の道筋で、ファイルの一覧（道筋、内容の型、SHA-256）と、1つのファイルの中身を返す。目録にない道筋は返さない。中身が目録の SHA-256 と違えば、誤りにする。
- **R-07 どこから開いても描ける**：雛形を Scope の場所に置いた説明資料は、`spec-dock/initiatives/<区切り>/<ID>/` からも、main のチェックアウトの `spec-dock/.canonical/<区切り>/<ID>/` からも、同じに描ける。
- **R-08 ブラウザーでの検査の手順**：手元で任意に実行できる、ブラウザーでの描画の検査の道具と手順を持つ。検査は、外へのネットワークを止めて行い、次を確かめる。
  - Markdown が描かれ、デザインシステムが準備を終える。JavaScript の捕まえていない誤りがない。
  - Markdown の `plantuml` の図の数と、描かれた SVG の数が一致し、誤りの図がない。
  - スマートフォンの幅（390px）で、ページが横にはみ出さない。

## スコープ

### 対象

- 提供側の配布資産 `src/spec_dock/assets/spec_dock/design-system/`（R-01、R-02）と、`assets/static-inventory.json` への登録、配布資産として許す場所の追加（`runtime/infra/static_assets.py`）。
- dogfood の写し `spec-dock/design-system/`（同じ PR で写す）。
- パッケージの中の図の部品と目録（R-05）、その入口（R-06）。
- ブラウザーでの検査の道具と手順（R-08）。
- テスト。

### 対象外

- `templates/cue/<種類>/` の雛形の置き場と、`explanation.html` の写し（I-3。K4 の持ち主）。
- `scope check` の説明資料の形の検査（I-2）。この Issue の雛形は、その検査が求める形を満たすだけである。
- CUE の描画（`render_scope_html`、`scope render`）と、`meta` を出す側（I-5）。
- ダッシュボードのサーバー（epic-00427）。
- 書き方のガイドとスキル（I-6）。
- 利用者のスキル japanese-explanatory-html の変更。利用者のスキルの検査の道具で、薄い説明資料を検査できるようにすること。
- 今の `spec-dock/templates/<種類>/` の `.md` の雛形の変更（I-7）。

### 親の契約として守る境界

- Epic の設計書の K5（デザインシステムの置き場は `spec-dock/design-system/`、薄い説明資料の3つの形、図の部品はパッケージにだけ同梱、読み込み先は手元の場所、CDN の順）。
- 雛形の置き場の決定（2026-10-31、統括）：I-4 は `spec-dock/design-system/explanation-skeleton.html` を置き、`templates/cue/` には触れない。

## 失敗・境界条件

- **外へのネットワークがない、`meta` がある**：手元の場所から読み、図を描ける。
- **外へのネットワークがない、`meta` がない（ファイルを単独で開いた）**：本文は描ける。図とコードの色付けだけが描けない。図の位置に、読み込めなかった理由を示す（今のデザインシステムの動き）。
- **`meta` が示す場所に部品がない、または読めない**：CDN を試す。両方とも読めなければ、図の位置に理由を示す。
- **`vendor/marked.umd.js` を読めない**：本文を描けないので、ページに、読み込めなかったことと、`installation update` を示す。`window.__dsState` に誤りを示し、`ready` にしない。
- **デザインシステムがリポジトリにない（配布資産を上げていない）**：ブラウザーは `ds.css` と `ds.js` を読めず、Markdown がそのまま残る。SpecDock はこれを検査しない（I-2 の範囲外。`installation show` で見つかる）。
- **パッケージの図の部品が壊れている**：R-06 の入口は、SHA-256 の食い違いを誤りにし、中身を返さない。
- **目録にない道筋、`..` を含む道筋を求められた**：R-06 の入口は、何も返さない。

## 受け入れ条件

- **AC-01（R-01）**：新しい空のリポジトリに `installation init` を行うと、`spec-dock/design-system/` に R-01 の4つのファイルと雛形ができ、`ds.css` と `vendor/` の2つは利用者のスキルのデザインシステムとバイト一致する。dogfood の写しが、提供側とバイト一致する。
- **AC-02（R-02）**：雛形が、R-02 の4つの条件を満たす（テストで確かめる）。
- **AC-03（R-04、R-05）**：`ds.js` の図の部品の版（PlantUML と highlight.js）が、同梱した部品の目録の版と一致する。
- **AC-04（R-05、R-06）**：入口が返す一覧が目録と一致し、各ファイルの SHA-256 が目録と一致する。利用許諾のファイルが含まれる。目録にない道筋と `..` を含む道筋には何も返さず、中身を変えた部品は誤りになる。作った wheel に、図の部品が含まれる。
- **AC-05（R-04、R-08。Epic の AC-10）**：同梱した部品を手元の HTTP のサーバーから配り、`meta` で示した説明資料を、外へのネットワークを止めたブラウザーで開くと、PlantUML の図が描け、部品は手元の場所から読まれる。
- **AC-06（R-02、R-07、R-08。Epic の AC-11）**：雛形を Scope の場所に置いた説明資料が、`spec-dock/initiatives/` からも `spec-dock/.canonical/` からも、ブラウザーでの描画の検査（R-08）に通る。390px の幅で、横にはみ出さない。ファイルを単独で開いたときに CDN から読む部品は、検査の中で、CDN の代わりに同梱の部品を返して確かめる。
- **AC-07（失敗）**：外へのネットワークを止め、`meta` も CDN の代わりもないとき、本文は描け、図の位置に読み込めなかった理由が出る。`vendor/marked.umd.js` がないとき、ページに理由が出て、`__dsState.ready` が偽のままである。
- **AC-08（Epic の AC-12、AC-15）**：今の回帰のテストを変えずに、`make lint` と `uv run pytest` が通る。今の `spec-dock/templates/<種類>/` の `.md` の雛形は変わらない。

## 制約・前提

- デザインシステムの元（`~/.agents/skills/japanese-explanatory-html/assets/design-system/`）は、読んで写すだけにし、変えない。
- 図の部品は、npm から版を固定して取り、取得物の integrity を npm の値と照らす。取得物の中のスクリプトを実行しない。
- テストは外のネットワークを使わない。ブラウザーの検査も、外へのネットワークを止めて行う。Chrome を直接起動するときは `--disable-features=MacAppCodeSignClone` を付け、CDP の `Browser.close` で閉じる。
- ブラウザーの検査は、手元で任意（R-E4）であり、CI では行わない。Chrome と Node.js を前提にするため、`uv run pytest` には入れない。
- 図の部品（約 10.5MB）は、パッケージにだけ置き、利用者のリポジトリには写さない（Epic の設計書 K5）。
- Python 3.10 以上、Linux と macOS。
