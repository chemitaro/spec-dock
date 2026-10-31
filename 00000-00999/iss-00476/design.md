---
種別: 設計書（Issue）
ID: "iss-00476"
関連GitHub: ["#476"]
状態: "approved"
最終更新: "2026-10-31"
依存: ["requirement.md"]
---

# iss-00476 Render CUE Specs As HTML — 設計

詳細: [Design Guide](../../../docs/authoring/design.md)

## 設計目標

- I-2 の評価（K1）を1回だけ通し、その JSON から、副作用のない部品で Markdown と HTML を作る。評価と描画を分け、描画の部品を、`cue` なしでテストできるようにする。
- I-4 の薄い説明資料と同じ形にし、ブラウザーでの描き方を `ds.js` に任せる（描画の道筋を1本にする）。
- 同じ入力から同じ出力を作る。辞書の並びに頼らず、番号の数の順と、決めた節の順で並べる。

## Current / Target

| | 今 | この Issue の後 |
|---|---|---|
| CUE の Scope を人が読む | CUE のファイルを直接読む | `render_scope_html` か `spec-dock scope render <ID>` の HTML を、ブラウザーで読む |
| ダッシュボードの入口 | ない | `render_scope_html(ScopeRenderSource, *, design_system_base, vendor_base)` |
| 公開の葉 | 54 | 55（`scope render`） |

## 責務・Interface

### D-01 入口（`runtime/application/scope_render.py`）

```python
@dataclass(frozen=True)
class ScopeRenderSource:
    scope_id: str          # 例 "iss-00476"
    kind: str              # "initiative" | "epic" | "issue"（GitHub の構造から。K1 の -t kind）
    title: str | None      # GitHub の題名。None なら ID だけを題名にする
    directory: Path        # Scope のディレクトリ（実のパスでもリンクでもよい）
    repository_root: Path  # リポジトリの根（spec-dock/cue/*.cue を読む）
    shown: str | None = None  # 誤りの文に出す Scope の道筋。None なら directory を repository_root からの相対で、相対にできなければ directory の道筋そのもの

@dataclass(frozen=True)
class RenderedScope:
    html: str
    report: ScopeCheckReport   # I-2 の検査の結果
    complete: bool             # 評価が通り、本文まで描いたか
    errors: tuple[Diagnostic, ...]  # ページに載せた誤り（説明資料の検査を除く）

def render_scope(source, *, design_system_base: str, vendor_base: str | None, timeout: float = 30.0) -> RenderedScope
def render_scope_html(source, *, design_system_base: str, vendor_base: str | None, timeout: float = 30.0) -> str
```

- `render_scope` は、`check_scope_documents(directory, kind=, shown=, repository_root=, timeout=)` を呼ぶ（K1。評価のファイルの並べ方は I-2 のまま）。
  - `report.format == "markdown"` なら `CanonicalCommandError(SCOPE_NOT_CUE, exit_code=7)` を投げる。
  - `cue` の問題と型の版の問題は、`check_scope_documents` が投げる `CanonicalCommandError` を、そのまま通す（K3 のコード）。
  - ページに載せる誤りは、`report.errors` から、`SPEC_FINDINGS`（`findings` の節で別に出す）と `EXPLANATION_*`（説明資料の検査。描画の対象外）を除いたものである。
  - `report.evaluation` があれば本文まで描き（`complete=True`）、なければ検査の結果だけを描く（`complete=False`）。
- `render_scope_html` は `render_scope(...).html` を返す。ダッシュボードは、自分が配る URL を `design_system_base`（例 `"/design-system/"`）と `vendor_base`（例 `"/vendor/"`）に渡す。
- `design_system_base` は URL の頭である。末尾に `/` がなければ足して、`ds.css` と `ds.js` を続ける（空の文字列なら、ページからの相対の `ds.css`）。`vendor_base` は、そのまま meta の `content` に入れる（`ds.js` が末尾の `/` を補う）。どちらも HTML の属性として逃がす。
- 公開のコードの定数は、このモジュールに置く：`SCOPE_NOT_CUE`、`SCOPE_RENDER_INCOMPLETE`、`DESIGN_SYSTEM_MISSING`。

### D-02 ページの部品（`runtime/presentation/spec_page.py`）

副作用のない2つの関数を持つ。`cue` もファイルも読まない。

```python
def spec_markdown(*, scope_id, kind, title, evaluation: Mapping | None, assurance: Mapping | None,
                  errors: Sequence[Diagnostic]) -> str
def wrap_page(markdown: str, *, title: str, design_system_base: str, vendor_base: str | None) -> str
```

**Markdown の並び**（R-04）。節の見出しは `##`、項目の見出しは `###`。

1. 前付け：`title: <ID> <題名>`、`lead`、`category: CUE の仕様`、`status: 保証レベル <level>`（読めなければ `保証レベル 未確定`）。前付けの値は1行にし、前後の引用符を除く。`ds.js` は `title` を、表紙では Markdown（`mdInline`。生の HTML を通す）として、帯と足元と `document.title` では文字として使うので、どちらの解釈でも同じに見えて、HTML にも強調にもならないように、`title` の中の `\`、`` ` ``、`*`、`_`、`[`、`]`、`<`、`>`、`&`、`~`、`|` を、見た目の近い全角の文字（`＼`、`｀`、`＊`、`＿`、`［`、`］`、`＜`、`＞`、`＆`、`～`、`｜`）に置き換える。題名の正確な文字は、本文の初め（`## 検査の結果` の前）に「題名：<題名>」として、文章でない値の規則で逃がして示す。`lead` と `status` は、SpecDock が作る文と、型が形を決めた値（`schema`、`level`）だけを持つ。
2. `## 検査の結果`：形の誤り（コード、ファイル、項目、文、直し方）を1件ずつ。続けて `findings` の規則の名前の順に、規則ごとに `### <規則の名前>` と、指摘（番号のリンク、文、直し方）を1件ずつ。誤りも指摘もなければ「誤りと指摘はありません。」。
3. `## 保証レベル`：`level` と `reason`（Markdown）。
4. `## 要件`：任意の節（`purpose` 目的、`background` 背景、`includes` 含めるもの、`excludes` 含めないもの、`constraints` 制約、`decisions` 決めたこと、`questions` 未解決のこと）を `###` で。続けて要件を番号の順に `### R-xx <題名>`、文章、`acceptance`（受け入れ）、つながり。
5. `## 失敗・境界条件`：失敗を番号の順に `### F-xx <題名>`、文章、`impact`（影響）、`recovery`（回復）、つながり。
6. `## 設計`：任意の節（`goals`、`current`、`target`、`compatibility`、`risks`）、設計の単位を番号の順に `### D-xx <題名>`、文章、満たすもの。
7. `## 計画`：任意の節（`goal`）、進み具合（手順があるときだけ。状態ごとの数の表）、手順 `### S-xx <題名>`（状態、満たすもの、先にする手順、セッション、文章）、テスト `### T-xx <題名>`（確かめるもの、文章）、切り分け `### <子の ID>`（任せる要件、先にする切り分け、セッション、文章）、`verification`、`rollback`、`exit`、実行の割り当て（セッションとレビューを名前の順に。セッションは作業、モデル、推論、根拠、使う手順。レビューは役割、後にする手順、モデル、推論）。
8. `## その他の項目`：型が知らない一番上の項目と、各項目の知らない項目を、JSON の符号のブロックで（キーの順に並べる）。なければ節を出さない。

各項目の中の任意の項目と、知らない項目（「その他」）も、同じ規則で決まった順に出す。

**番号の並び**：`<頭>-<数>` は、数の大きさの順（同じ数なら文字の順）。セッションとレビューと規則の名前は、文字の順。

**アンカーとリンク**（R-05）：項目の見出しは、Markdown の見出しではなく、HTML の `<h3 id="<番号>">` で書く（`ds.js` は、`id` を持つ見出しの `id` を変えず、目次に入れる）。番号でない `id` の指摘（`rollback`、`execution.reviews.<名前>`、リポジトリの型の規則の `id`）は、リンクにも「ない番号」にもせず、文字として出す。番号の形（`<英字>-<数字>`）で、ページにない `id` だけを「ない番号」とする。`id` は番号そのもの（`R-01`、`F-01`、`D-01`、`S-01`、`T-01`）と、切り分けは `slice-<子の ID>`。番号はキーの正規表現で形が決まっているので、`id` に安全である。リンクは `[R-01](#R-01)`。逆向きの索引（要件 → 設計、手順、テスト、切り分け）は、評価の JSON から Python で作る。存在しない番号は、リンクにせず「`<番号>`（ない番号）」と出す。取り下げた手順も、状態を添えて出す。

**逃がし**（R-08）：

| 置き場 | 値 | 扱い |
|---|---|---|
| Markdown の地の文、表、リスト | 文章でない値 | 行に分けて各行の前後の空白を除き、1つの空白でつないで1行にし、ASCII の記号をすべてバックスラッシュで逃がす（CommonMark の逃がし。`marked` は `<`、`>`、`&` を文字として出す） |
| HTML の見出し `<h3>` の中 | 番号と題名 | HTML の特殊な文字を実体参照にする（HTML のブロックの中は Markdown にならないため） |
| ブロック | 文章の項目（`#Text`） | そのまま Markdown として置く。リストの中では、続く行を字下げする |
| 符号のブロック | その他の項目 | JSON（`ensure_ascii=False`、`sort_keys=True`、字下げ 2）。文字 `<` を、6文字の逃がし `\u003c`（バックスラッシュ、`u003c`）にする（JSON として同じ値）。囲いは、中の最も長いバッククォートの並びより長くする |

最後に Markdown の全体で、`</script`（大文字小文字を問わない）を `<\/script` に変える（`ds.js` は読むときに戻す）。さらに、Markdown に `<!--` と、`<script` に空白、`/`、`>` のどれかが続く並び（大文字小文字を問わない）の両方があるときだけ、`<!--` を `<!\--` に変える（`<!--` の後に `<script` が来ると、HTML の解析が `</script>` を区切りと見なくなるため。片方だけなら、区切りは壊れない）。このときだけ、文章の項目の HTML のコメントは文字として見え、符号の中の `<!--` は `<!\--` と見える。

**HTML の形**（R-03）：

```html
<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="color-scheme" content="light dark">
<meta name="ds-vendor-base" content="...">        <!-- vendor_base があるときだけ -->
<title>(題名を HTML として逃がしたもの)</title>
<link rel="stylesheet" href="(base)ds.css">
<script type="text/markdown" id="ds-source">
(Markdown)
</script>
<script src="(base)ds.js"></script>
</head>
<body></body>
</html>
```

### D-03 コマンド `scope render <ID>`（`runtime/application/canonical_scope_render.py`）

- `scope check` と同じに Scope を解き（`load_canonical_scopes`、`resolve_canonical_scope`、`check_canonical_scope_expectations`、`require_directory`）、`ScopeRenderSource` を作って `render_scope` を呼ぶ。`design_system_base` は `(<チェックアウトの根>/spec-dock/design-system).as_uri() + "/"`、`vendor_base` は `None`。
- 結果：`FamilyData("scope-render", {scope_id, kind, path, format, complete, valid, errors, design_system_base, vendor_base, html, snapshot})`、終了コード 0。
  - `errors` は `RenderedScope.errors`（ページに載せた誤り。つながりの指摘と説明資料の検査を含まない）。
  - `valid` は、`report.errors` から `EXPLANATION_*` を除いたものが空のとき真（形の誤りも、つながりの指摘もない）。説明資料の検査は、`valid` にも影響しない（`scope check` の `valid` とは、説明資料の扱いだけが違う）。
  - `--json` の封筒は、ほかの葉と同じく共通の秘匿化（`_redact`。トークンや URL の利用者情報を `[redacted]` にする）を通す。`data.result.html` は、その秘匿化の後の値である。テキストの出力と関数の返り値は、秘匿化しない HTML である（描画の結果を、そのまま見せるため）。そのため、秘匿化に当たる文字を含む仕様では、`--json` の `html` だけが、その部分で違う。
- 警告：`complete=False` なら `SCOPE_RENDER_INCOMPLETE`。`<根>/spec-dock/design-system/ds.js` がなければ `DESIGN_SYSTEM_MISSING`（`installation update` の案内）。スコープの読み込みの警告（`scopes.warnings()`）も続ける。
- テキストの出力（`presentation/envelope.py` の `render_text`）：`scope render` で `html` を持つ結果は、標準出力に HTML だけを出す（1行目の `spec-dock: succeeded (...)` を出さない）。警告は今のとおり標準エラーに出す。失敗のときは、今の失敗の出力のままにする。
- schema 3 のリポジトリでは、`scope check` と同じく `CANONICAL_NOT_MIGRATED` で止まる（`runtime_dispatch.py`）。
- catalog：葉 `scope render`（引数 `target`）、効果、前提、`reads`、`does_not`、`json_data`。読むだけの葉として、補完の検査の一覧に入る。

## data / failure

- 書くもの：ない。`cue` は I-2 の部品が子のプロセスとして呼ぶ（3回：`schema`、K1 の評価、`assurance`）。
- 失敗と、扱い：

| 状況 | 関数 | コマンド |
|---|---|---|
| Markdown の Scope | `CanonicalCommandError(SCOPE_NOT_CUE, exit 7)` | 失敗、7。HTML は出さない |
| `cue` がない、古い、時間切れ、失敗、型の版がない | I-2 の `CanonicalCommandError` をそのまま | 失敗、3 または 5 |
| 形の誤り、両方の形式 | 検査の結果だけのページ（`complete=False`） | 成功、0、警告 `SCOPE_RENDER_INCOMPLETE` |
| つながりの指摘 | 本文も描く（`complete=True`、`valid=False`） | 成功、0 |
| デザインシステムがない | 関係しない（URL を受けるだけ） | 成功、0、警告 `DESIGN_SYSTEM_MISSING` |

- 新しいコードは、配布資産の `docs/canonical.md` の「エラーと次の1手」の表に足す。

## 変更対象

- 足す：`src/spec_dock/runtime/application/scope_render.py`、`src/spec_dock/runtime/application/canonical_scope_render.py`、`src/spec_dock/runtime/presentation/spec_page.py`。
- 直す：`runtime/cli/catalog.py`、`runtime/commands/canonical_dispatch.py`、`runtime/commands/runtime_dispatch.py`、`runtime/presentation/envelope.py`。
- 配布資産：`assets/spec_dock/docs/{reference_cli.md,README.md,cli-redesign-guide.html,canonical.md}`、`assets/static-inventory.json`、dogfood の写し `spec-dock/docs/` の同じファイル。
- 葉の数を数えるテスト（54 → 55）。
- 変えない：`scope_check.py`、`cue_tool.py`、デザインシステム、雛形、Markdown の Scope の動き。

## 移行・互換性・rollback

- 足すだけで、今のコマンドの動きは変えない。`render_text` の変更は、`scope render` の成功の結果だけに効く。
- 戻すときは、この PR を戻す。配布資産の CLI 参照の行は、`installation update` で戻る。

## testability

- `spec_page`（`cue` なし）：手で作った評価の JSON で、節の並び、番号の数の順、リンクと逆の索引、ない番号、状態の数、逃がし（`</script>`、`<!--`、`<b>`、`|`、改行）、キーの並びを入れ替えても同じ、`vendor_base` の有無、`design_system_base` の末尾の `/`。
- `scope_render`（本物の `cue`）：`tests/support/cue_scopes.py` の見本の Scope（雛形の見本）で、Issue と Epic の描画、指摘のある Scope、形の誤りの Scope（`complete=False`）、Markdown の Scope（`SCOPE_NOT_CUE`）、2回描いて同じ。I-4 の `inspect_explanation` で、`design_system_base="../../../design-system/"` のときに薄い形の問題がないこと（雛形の印がないので「雛形のまま」にもならない）。
- `cue` の問題：偽の `cue`（I-2 のテストと同じやり方）で、`CUE_NOT_FOUND`、`CUE_VERSION_UNSUPPORTED`。
- コマンド：I-2 の `test_issue473_scope_check.py` と同じ世界で、`scope render` の標準出力、`--json`、終了コード、警告、カタログが変わらないこと。

## risk

- `ds.js` の Markdown の解釈（`marked` の版、指示の書き方）が変わると、描画が変わる。生の HTML の見出しと、普通の Markdown だけを使い、`ds.js` の独自の指示（`:::` など）は使わないことで、影響を小さくする。
- 文章の項目の生の HTML は、`marked` がそのまま出す（説明資料と同じ扱い）。描画は手元とダッシュボードで読むもので、仕様を書くのは利用者とエージェントなので、文章の HTML を消毒しない。`<script>` の区切りを壊すものだけを逃がす。
- 評価を3回の `cue` で行うので、大きな Scope では時間がかかる。`timeout` で上限を設ける（I-2 のまま）。
