---
種別: 設計書（Issue）
ID: "iss-00475"
関連GitHub: ["#475"]
状態: "draft"
最終更新: "2026-10-31"
依存: ["requirement.md"]
---

# iss-00475 Ship Explanation Design System — 設計

詳細: [Design Guide](../../../docs/authoring/design.md)

## 設計目標

- 説明資料は、Markdown と、共有のデザインシステムを読む2行だけを持つ。デザインシステムを上げても、Scope のファイルは変わらない（R-01〜R-03）。
- 図の部品の読み込み先を、ページが示す手元の場所、CDN の順の1本の道筋にする。ダッシュボードのサーバーも、単独のファイルも、同じ `ds.js` で描く（R-04）。
- 図の部品は、パッケージにだけ置き、目録の SHA-256 で中身を縛る。配る側は、目録にあるファイルだけを返す（R-05、R-06）。
- ブラウザーでの検査は、外へのネットワークを止め、決まった見本の木で、場面ごとに再現できる（R-08）。

## Current / Target

| | 今 | この Issue の後 |
|---|---|---|
| デザインシステム | 利用者のスキルの `assets/design-system/`。説明資料に内蔵 | 配布資産 `spec-dock/design-system/`（`ds.css`、`ds.js`、`vendor/marked.*`）。説明資料は相対の道筋で読む |
| `marked` | 説明資料に内蔵 | `ds.js` が `vendor/marked.umd.js` を読む |
| 図の部品 | CDN（unpkg）だけ | `meta[name="ds-vendor-base"]` の手元の場所、CDN の順。部品はパッケージ `spec_dock/assets/vendor/` に同梱 |
| 雛形 | スキルの `explanatory-document.html`（約 300KB） | 配布資産 `spec-dock/design-system/explanation-skeleton.html`（数 KB） |
| ブラウザーの検査 | スキルの検査の道具（内蔵の形だけを受ける） | `tests/browser/explanation-check.mjs`（薄い形。手元で任意） |

## 責務・Interface

### 1. 配布資産のファイル

提供側 `src/spec_dock/assets/spec_dock/design-system/` と、利用側 `spec-dock/design-system/`（`installation` が置く。dogfood の写しは同じ PR で写す）。

| 道筋（`spec-dock/design-system/` から） | 中身 |
|---|---|
| `ds.css` | スキルの `ds.css` とバイト一致 |
| `ds.js` | スキルの `ds.js` を、下の「`ds.js` の直し」のとおりに直したもの |
| `vendor/marked.umd.js` | スキルのものとバイト一致 |
| `vendor/marked.LICENSE.md` | スキルのものとバイト一致 |
| `explanation-skeleton.html` | 薄い説明資料の雛形（下の 3） |

- `static-inventory.json` に5つを足す（`mode` 420、`init_only` 偽、`known_old_sha256` は空）。道筋は並びの順を守る。
- `runtime/infra/static_assets.py` の、配布資産として許す場所に `spec-dock/design-system/` を足す。ほかの場所は変えない。
- canonical check の規則5は、既定のブランチに、この5つが今の版または既知の古い版であることを求める。dogfood の写しを同じ PR で入れるので、spec-dock 自身の検査は通る。

### 2. `ds.js` の直し

元の動き（Markdown の描き方、部品、図の検査、拡大表示）は変えない。直すのは、内蔵を前提にした4か所だけである。

1. **版**：`VERSION` を `"1.0.0+specdock.1"` にする（元の 1.0.0 から派生したことを示す）。冒頭の注に、元と直した点を書く。
2. **先に行う設定（元の `ds-preflight`）**：テーマと文字の大きさの設定を、`ds.js` の読み込みの直後に行う（説明資料は `ds.js` を `<head>` で同期に読むので、描く前に効く）。UD フォント（Google Fonts）の `<link>` も、`ds.js` が `<head>` に足す。読めない環境では、端末の標準のゴシック体になる（元と同じ）。
3. **`marked`**：読み込みの時に `document.currentScript.src` を覚え、起動の前に、その場所からの `vendor/marked.umd.js` を `<script>` で読む。`window.marked` が既にあれば読まない。読めなければ、`<body>` に `role="alert"` の知らせ（読めなかったファイルと `spec-dock installation update`）を出し、`__dsState.error` に理由を入れ、`ready` を偽のままにする。
4. **図の部品の読み込み先**：

   ```js
   const PLANTUML_VERSION = "1.2026.6";
   const HLJS_VERSION = "11.11.1";
   const VENDOR = {
     plantuml: { local: `plantuml/${PLANTUML_VERSION}/`, cdn: `https://unpkg.com/@plantuml/core@${PLANTUML_VERSION}/` },
     hljs:     { local: `highlightjs/${HLJS_VERSION}/`,  cdn: `https://unpkg.com/@highlightjs/cdn-assets@${HLJS_VERSION}/` },
   };
   ```

   - `meta` を読む時：部品を読み込む時（起動の後、`DOMContentLoaded` の後）に読む。そのため `meta` は `<head>` のどこに置いてもよい（I-5 には、`ds.js` の `<script>` より前に置くよう勧める）。
   - 候補の並び：`<meta name="ds-vendor-base" content="URL">` があれば、`content` を文書の URL から解決し、末尾に `/` を足した場所の下の `local`、その次に `cdn`。`meta` がなければ `cdn` だけ。
   - PlantUML は、候補ごとに `viz-global.js` を読み、`plantuml.js` を `import()` する。失敗したら次の候補へ進む。すべて失敗したら、各候補の理由をまとめた誤りにする（図の位置に出る。元の動き）。
   - highlight.js は、候補ごとに `highlight.min.js` を読む。すべて失敗したら、元と同じく色なしで表示する。
   - 読めた候補を `__dsState.vendor = { plantuml: "local" | "cdn" | null, hljs: ... }` に示す。

`meta` の名前 `ds-vendor-base` と、その下の配置（`plantuml/<版>/`、`highlightjs/<版>/`）が、I-5 と epic-00427 との契約である（K5 の「図の部品の読み込み先」。2026-10-31、統括が了承）。

### 3. 薄い説明資料の雛形

```html
<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="color-scheme" content="light dark">
<title>説明資料</title>
<link rel="stylesheet" href="../../../design-system/ds.css">
<!-- 説明資料の本文（Markdown）。編集するのはこのブロックだけです。 -->
<script type="text/markdown" id="ds-source">
---
title: …
---
<!-- spec-dock:explanation-skeleton -->
…（元の document-skeleton.md に倣った節。PlantUML の図を1つと、言語を付けたコードの囲みを1つ含む）
</script>
<script src="../../../design-system/ds.js"></script>
</head>
<body></body>
</html>
```

- K5 の3つの形（`ds-source` がちょうど1つで前付けに `title`、`ds.css` と `ds.js` の相対の指定、雛形の印）を満たす。ほかの `<style>`、`<script>`、外部の読み込みを持たない。
- Scope の種類ごとの置き換えの印を持たない。I-3 は、この雛形を `templates/cue/<種類>/explanation.html` にバイト一致で写す。
- **置き場の決定（2026-10-31、統括）**：雛形は `spec-dock/design-system/explanation-skeleton.html` に置き、`templates/cue/` には触れない。理由：`templates/cue/` の持ち主は I-3（K4）である。I-4 が `templates/cue/<種類>/` に先にファイルを置くと、「`templates/cue/<種類>/` がなければ止まる」という I-3 の判定が、半端な配布資産で誤って通る。雛形はデザインシステムと同じ版で動くので、同じ場所で管理する。
- 相対の道筋 `../../../design-system/` は、`spec-dock/initiatives/<区切り>/<ID>/` と `spec-dock/.canonical/<区切り>/<ID>/` のどちらからも `spec-dock/design-system/` に届く（ブラウザーは URL の `..` を字面で解くので、`initiatives` がリンクでも同じ）。

### 4. パッケージの図の部品と、その入口

置き場：`src/spec_dock/assets/vendor/`（`assets/**/*` で wheel に入る。`static-inventory.json` には載せないので、利用者のリポジトリには入らない）。

```text
assets/vendor/
  manifest.json
  plantuml/1.2026.6/{plantuml.js, viz-global.js, emoji.js, openiconic.js, LICENSE}
  highlightjs/11.11.1/{highlight.min.js, LICENSE}
```

- `emoji.js` と `openiconic.js` は、`plantuml.js` が、絵文字とアイコンの図のときに同じ場所から読む。そのため一緒に置く。
- `manifest.json`：

  ```json
  {
    "schema_version": "specdock.diagram-vendor/v1",
    "packages": [
      {"name": "@plantuml/core", "version": "1.2026.6", "license": "MIT", "directory": "plantuml/1.2026.6",
       "npm_tarball": "https://registry.npmjs.org/@plantuml/core/-/core-1.2026.6.tgz", "npm_integrity": "sha512-…"}
    ],
    "files": [{"path": "plantuml/1.2026.6/plantuml.js", "content_type": "text/javascript; charset=utf-8", "sha256": "…"}]
  }
  ```

- 入口 `spec_dock/runtime/infra/diagram_vendor.py`（パッケージの資源を読む部品なので infra に置く）：

  ```python
  DIAGRAM_VENDOR_META_NAME = "ds-vendor-base"

  @dataclass(frozen=True)
  class DiagramVendorFile:
      path: str          # "plantuml/1.2026.6/plantuml.js"（vendor_base の下の相対の道筋）
      content_type: str
      sha256: str

  class DiagramVendorError(ValueError): ...

  def diagram_vendor_files() -> tuple[DiagramVendorFile, ...]: ...
  def read_diagram_vendor_file(path: str) -> bytes | None: ...
  ```

  - `diagram_vendor_files()` は、目録を読み、形（版、道筋の安全、並び、重複）を確かめて返す。目録が壊れていれば `DiagramVendorError`。
  - `read_diagram_vendor_file(path)` は、目録にある道筋だけを読む。目録にない道筋（`..`、絶対、空、`\` を含むものを含む）は `None`。中身の SHA-256 が目録と違えば `DiagramVendorError`。
  - ダッシュボードのサーバーは、自分の URL の頭（例 `/vendor/`）の下に、`path` をそのまま対応させ、`content_type` で返す。ページには、`<meta name="ds-vendor-base" content="/vendor/">` を出す（I-5 の `render_scope_html(vendor_base=…)`）。

### 5. ブラウザーでの検査の道具

`tests/browser/explanation-check.mjs`（Node.js 22 以上の組み込みの `WebSocket` と `fetch` だけを使い、依存を足さない）。pytest には入れない（R-E4、手元で任意）。

- Chrome を、新しい一時のプロファイル、`--headless=new`、`--remote-debugging-port=0`、`--disable-features=MacAppCodeSignClone`、`--host-resolver-rules="MAP * ~NOTFOUND, EXCLUDE 127.0.0.1"` で起動し、CDP の `Browser.close` で閉じる。
- CDP の `Fetch` で、すべての要求を止める。`file:` と `http://127.0.0.1:<道具のサーバー>` だけを通す。場面が許すときだけ、`ds.js` の CDN の URL（固定の版）への要求に、同梱の部品を `Access-Control-Allow-Origin: *` を付けて返す。それ以外は失敗させ、記録する。
- 見本の木を一時のディレクトリに作る：`repo/spec-dock/design-system/`（提供側の写し）、`repo/spec-dock/.canonical/00000-00999/iss-00001/explanation.html`（雛形）、`repo/spec-dock/initiatives` → `.canonical` のリンク。
- 場面：

  | 場面 | 開き方 | 部品 | 期待 |
  |---|---|---|---|
  | `canonical-file` | `file:` で `.canonical/…` | CDN の代わりに同梱を返す | 合格、`vendor.plantuml = "cdn"`、`vendor.hljs = "cdn"` |
  | `initiatives-file` | `file:` で `initiatives/…` | 同上 | 合格 |
  | `local-http` | 道具のサーバーで、`meta`（`content="/vendor/"`）を `ds.js` の前に足した写し | `/vendor/` から同梱を配る。CDN は止める | 合格、`vendor.plantuml = "local"`、`vendor.hljs = "local"` |
| `local-fallback` | 道具のサーバーで、部品のない場所を示す `meta` を足した写し | CDN の代わりに同梱を返す | 合格、`vendor.plantuml = "cdn"` |
  | `offline-standalone` | `file:` で `.canonical/…` | すべて止める | 本文は準備を終え、図は誤り1つ、捕まえていない誤りなし |
  | `missing-marked` | `vendor/marked.umd.js` を消した木 | すべて止める | `ready` が偽、知らせが出る |

- 合格の判定（`canonical-file`、`initiatives-file`、`local-http`、`local-fallback`、`--file`）：`__dsState.ready` と `__plantumlDocumentState.completed` が真、捕まえていない誤りがない、`.ds-unknown` がない、Markdown の `plantuml` の囲みの数と、`expected`、`rendered`、図ごとに1つの SVG の数が一致し、`errors` が空、390px の幅で `scrollWidth <= innerWidth`。
- `--file <道筋>` で、手元の任意の説明資料を同じ判定にかけられる（`--cdn-from-package` で CDN の代わりに同梱を返す）。結果は、場面ごとの JSON と、最後の行 `VALIDATED` または `FAILED`。

## data / failure

- 書くもの：`installation init/update` が `spec-dock/design-system/` に5つのファイルを置く（今の静的資産の仕組みのまま）。入口と検査の道具は、パッケージとリポジトリに何も書かない（検査の道具は一時のディレクトリだけに書き、終わりに消す）。
- 失敗の扱いは、要件定義書の「失敗・境界条件」のとおり。`ds.js` の失敗は、ページの中の知らせと `__dsState` で示し、捕まえていない誤りにしない。

## 変更対象

- 足す：`src/spec_dock/assets/spec_dock/design-system/`（5つ）、`src/spec_dock/assets/vendor/`、`src/spec_dock/runtime/infra/diagram_vendor.py`、`spec-dock/design-system/`（写し）、`tests/browser/explanation-check.mjs`、テスト。
- 直す：`src/spec_dock/assets/static-inventory.json`、`src/spec_dock/runtime/infra/static_assets.py`（許す場所）。
- 変えない：`spec-dock/templates/` の雛形、`templates/cue/`、CLI の命令と出力、canonical check の規則、利用者のスキル。

## 移行・互換性・rollback

- 新しい配布資産を足すだけで、既存のファイルを変えない。前の版の CLI は、`spec-dock/design-system/` を知らない。canonical check の規則5は、提供側の目録にある資産だけを見るので、前の版の CLI で検査しても、この資産は対象にならない。
- 利用者のリポジトリへは、`installation update` で入る（R-J1、I-7 で spec-dock に入れる）。dogfood の写しは、同じ PR で入れる。
- 戻すときは、PR を戻す。利用者のリポジトリに入った5つは、前の版では知らないファイルとして残るだけで、動きに影響しない。
- データの移行：N/A（新しいファイルを足すだけ）。

## testability

- pytest（ネットワークなし）：
  - 静的資産：5つが目録にあり、提供側と dogfood の写しがバイト一致し、`ds.css` と `vendor/` の SHA-256 が、写した時の元（スキルの版 1.0.0）の値（テストに固定値で書く）と一致する。利用者の PC のスキルは読まない（hermetic に保つ。元との一致は、写した時に一度確かめ、報告書に残す）。`installation init` で5つが置かれる。
  - 雛形の形（R-02 の4条件）を、HTML を解析して確かめる。
  - `ds.js`：`PLANTUML_VERSION`、`HLJS_VERSION` が目録の版と一致し、`ds-vendor-base`、`vendor/marked.umd.js` を参照する。
  - 入口：一覧と目録の一致、SHA-256、利用許諾、目録にない道筋、`..`、中身を変えた部品（資源の読み取りを差し替えて確かめる）。
  - wheel：今の wheel のテストと同じく、作った wheel に `spec_dock/assets/vendor/manifest.json` と部品があることを確かめる。
- ブラウザー（手元で任意）：`node tests/browser/explanation-check.mjs` の6つの場面（AC-05、AC-05b、AC-06、AC-07）。結果を報告書に残す。

## risk

- **スキルの元が CI にない、別に進む**：`~/.agents/skills/...` は、利用者の PC にだけあり、別に更新される。テストは写した時の SHA-256 の固定値と比べ、元を読まない（SpecDock の側を正とする。Epic の設計書の risk）。
- **`@plantuml/core` が新しく、`emoji.js` などの読み方が版で変わる**：版を固定し、上げるときは検査の道具の6つの場面を通す。
- **リポジトリが約 10.5MB 重くなる**：Epic の設計書で受け入れ済み。利用者のリポジトリには入らない。
- **CDP の `Fetch` が `file:` の要求を扱わない**：`file:` は止めずに通すので、判定に影響しない。外への要求は、`host-resolver-rules` でも止める（二重）。
- **`ds.js` の派生が元から離れる**：直した4か所を冒頭の注に書き、元の版を上げるときは、その4か所を当て直す。
