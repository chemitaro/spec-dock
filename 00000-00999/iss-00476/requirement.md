---
種別: 要件定義書（Issue）
ID: "iss-00476"
関連GitHub: ["#476"]
状態: "approved"
最終更新: "2026-10-31"
---

# iss-00476 Render CUE Specs As HTML — 要件定義

詳細: [Requirement Guide](../../../docs/authoring/requirement.md)

## 目的

1つの CUE の Scope の要件・設計・計画（`requirement.cue`、`design.cue`、`plan.cue`）を、人が読める HTML に、その場で描けるようにする。ダッシュボード（epic-00427）のサーバーが、前もってファイルを作らずに呼べる、文書化された入口を持つ。

## 背景

- 親の Epic（epic-00425）の R-F1 と AC-09 を、この Issue が満たす。計画書の「I-5 Render CUE Specs As HTML」の節が材料である。
- I-2（iss-00473、#473）が、K1 の評価の部品（`check_scope_documents`、`k1_files`）を作った。評価が通ると、評価の JSON の全体（`ScopeCheckReport.evaluation`）が得られる。
- I-4（iss-00475、#475）が、デザインシステム（`spec-dock/design-system/` の `ds.css`、`ds.js`）と、薄い説明資料の形（`explanation-skeleton.html`）と、図の部品の読み込み先（`<meta name="ds-vendor-base">`）を作った。
- この Issue は、I-2 の評価の JSON を、決まった並びの Markdown にし、I-4 の薄い説明資料と同じ形の HTML に包む（Epic の設計の責務・Interface 5、契約 K5 の描画の入口）。
- 使う側：ダッシュボード（epic-00427）は Python の関数を、人とエージェントは `spec-dock scope render <ID>` を使う。

## 観測可能な要件

- **R-01 描画の入口（関数）**：`spec_dock.runtime.application.scope_render.render_scope_html(scope, *, design_system_base: str, vendor_base: str | None, timeout: float = 30.0) -> str` が、1つの CUE の Scope の HTML を返す。`scope` は、Scope の ID、種類、題名、Scope のディレクトリ、リポジトリの根を持つ値（`ScopeRenderSource`）である。インターネットを使わず、何も書かない。入口の引数、返り値、止まり方は、関数の docstring と、配布資産の CLI 参照に書く。
- **R-02 描画の入口（コマンド）**：`spec-dock scope render <ID>` が、同じ HTML を標準出力に出す。デザインシステムは、そのチェックアウトの `spec-dock/design-system/` を指す `file:` の URL から、図の部品は CDN から読む（`vendor_base` なし）。`--json` では、共通の封筒（`specdock.cli/v2`）の `data.result.html` に同じ HTML を入れる。読むだけで、何も書かない。
- **R-03 薄い HTML の形**：HTML は、I-4 の薄い説明資料と同じ形を持つ。`<script type="text/markdown" id="ds-source">` がちょうど1つあり、中の Markdown の先頭に `title` を持つ前付けがある。`<design_system_base>ds.css` と `<design_system_base>ds.js` を読む。`vendor_base` があれば `<meta name="ds-vendor-base" content="<vendor_base>">` を持ち、`None` なら持たない。
- **R-04 決まった並び**：Markdown は、次の並びで作る。検査の結果、保証レベル、要件（任意の節、要件、失敗・境界条件）、設計（任意の節、設計の単位）、計画（任意の節、進み具合、手順、テスト、切り分け、実行の割り当て）、その他の項目。番号を持つ項目は、番号の数の順（`R-2` の形は使わないが、`R-100` は `R-99` の後）に並べる。同じ入力からは、いつも同じ HTML ができる。
- **R-05 番号のリンク**：要件と失敗・境界条件ごとに、それを満たす設計、手順、テスト、切り分けを、番号のリンク（ページの中のアンカー）で示す。設計、手順、テスト、切り分けは、自分が指す番号をリンクで示す。存在しない番号は、リンクにせず、ないことを示す。
- **R-06 検査の結果を初めに示す**：ページの初めに、`findings` の規則ごとの指摘（番号、文、直し方）と、形の誤り（`CUE_INVALID` など）を示す。何もなければ、ないことを示す。評価が通らない Scope（形の誤り、両方の形式）は、検査の結果だけのページにする。
- **R-07 手順の状態**：Issue の手順は、それぞれ状態（まだ、作業中、済み、取り下げ）を示す。計画の初めに、状態ごとの数を示す。
- **R-08 文章と逃がし**：文章の項目（型の `#Text`）は Markdown として描く。それ以外の値（題名、番号、状態、モデル、推論、役割、その他の項目）は、HTML と Markdown の特殊な文字を逃がし、文字のまま見せる。Markdown の部分も含めて、どの値も、`<script>` の区切りを壊さない。
- **R-09 Markdown の Scope と、止まり方**：Markdown の Scope では、HTML を作らずに、`SCOPE_NOT_CUE` で止まる。`cue` がない、古い、時間切れ、型の版を持っていないときは、`scope check` と同じコードで止まる（I-2 の契約 K3）。

## スコープ

### 対象

- `runtime/application/scope_render.py`（入口）、`runtime/presentation/spec_page.py`（評価の JSON から Markdown と HTML を作る、副作用のない部品）。
- `scope render` の CLI の葉（catalog、dispatch、テキストの出力）。
- 配布資産の CLI 参照（`docs/reference_cli.md`、`docs/README.md`、`docs/cli-redesign-guide.html`、`docs/canonical.md` のエラーの表）と、その dogfood の写し、`static-inventory.json`。
- テスト（`tests/unit/presentation/`、`tests/unit/application/`、`tests/cli_runtime/`）。

### 対象外

- ダッシュボードのサーバーそのもの、報告と ADR の描画（epic-00427）。
- 説明資料（`explanation.html`）の描画と検査（I-2、I-4 の持ち物）。描画のページには、説明資料の検査の結果を載せない。
- デザインシステムと `ds.js` の変更（I-4 の持ち物）。
- `scope render` に、出力先のファイルや、読み込み先を変える引数を足すこと。読み込み先を変えるのは、関数の入口だけである。
- ブラウザーでの描画の自動の検査（ブラウザーの検査は、手元で任意。Epic の R-E4）。

### 親の契約として守る境界

- K1：評価は、I-2 の `check_scope_documents` を使う。ファイルの並べ方を、自分で作り直さない。
- K3：止まるときのコード、`assurance` の読み方は、I-2 のとおりにする。
- K5：薄い説明資料の形と、`ds-vendor-base` の意味は、I-4 のとおりにする。

## 失敗・境界条件

- **F-01 Markdown の Scope**：`SCOPE_NOT_CUE`（終了コード 7）で止まる。何も出さない。
- **F-02 `cue` の問題**：`CUE_NOT_FOUND`、`CUE_VERSION_UNSUPPORTED`（3）、`CUE_TIMEOUT`、`CUE_FAILED`（5）、`CUE_SCHEMA_UNSUPPORTED`（3）で止まる。
- **F-03 評価が通らない**：形の誤り、両方の形式の Scope では、検査の結果だけのページを出す。コマンドは成功で終わり、警告 `SCOPE_RENDER_INCOMPLETE` を出す。
- **F-04 つながりの指摘がある**：ページの初めに示し、ほかの部分は普通に描く。コマンドは成功で終わる。
- **F-05 デザインシステムがない**：`scope render` で、そのチェックアウトに `spec-dock/design-system/ds.js` がないときは、HTML を出したうえで、警告 `DESIGN_SYSTEM_MISSING` と `installation update` の案内を出す。
- **F-06 危ない文字**：題名などに `<`、`&`、`|`、`*`、改行、`</script>`、`<!--` を含んでも、ページの形を壊さず、文字として見える。

## 受け入れ条件

- **AC-01**（R-01、R-03、Epic AC-09）：見本の CUE の Issue、Epic を `render_scope_html` に渡すと、ネットワークなしで、R-03 の形の HTML が返る。`vendor_base` を渡すと `ds-vendor-base` の meta があり、`None` ならない。
- **AC-02**（R-02）：`spec-dock scope render <ID>` が、標準出力に HTML だけを出し、終了コード 0 で終わる。`--json` の `data.result.html` が同じ HTML である。カタログもチェックアウトも変わらない。
- **AC-03**（R-04）：同じ Scope を2回描くと、同じ HTML になる。評価の JSON のキーの並びを入れ替えても、Markdown は同じになる。番号は数の順に並ぶ。
- **AC-04**（R-05）：要件の節に、それを満たす設計、手順、テストへのリンクがあり、設計、手順、テストの節に、要件へのリンクがある。存在しない番号はリンクにならない。Epic では、切り分けへのリンクになる。
- **AC-05**（R-06、F-03、F-04）：つながりの指摘のある Scope では、ページの初めに規則、番号、文、直し方が出る。形の誤りの Scope では、誤りだけのページになり、`scope render` は成功と警告 `SCOPE_RENDER_INCOMPLETE` を返す。
- **AC-06**（R-07）：手順の状態と、状態ごとの数が出る。
- **AC-07**（R-08、F-06）：文章の項目の Markdown は、そのまま Markdown として入る。文章でない値の HTML と Markdown の特殊な文字は逃がされる。どの値に `</script>` や `<!--` を入れても、`ds-source` の中に `</script` も `<!--` も現れない。
- **AC-08**（R-09、F-01、F-02）：Markdown の Scope では `SCOPE_NOT_CUE`（7）で止まる。偽の `cue` で、ない、古いときに `scope check` と同じコードで止まる。
- **AC-09**（F-05）：デザインシステムのないチェックアウトで、警告 `DESIGN_SYSTEM_MISSING` が出る。
- **AC-10**（Epic AC-12、AC-15）：今の回帰テストを変えずに、`make lint` と `uv run pytest` が通る（葉の数の検査と、CLI 参照の一覧の検査は、葉が1つ増えたことに合わせる）。

## 制約・前提

- Python 3.10 以上、Linux と macOS。テストは、外のネットワークを使わない。`cue` を要するテストは、`cue` がないときに飛ばさず、失敗にする（I-1 の方針）。
- `cue` は v0.17.1 を、この worktree の無視されている場所に入れて使う。
- 今の `.md` の雛形と、Markdown の Scope の動きは変えない。
- `scope render` は、公開の葉が1つ増える CLI の契約の変更である（54 から 55）。
