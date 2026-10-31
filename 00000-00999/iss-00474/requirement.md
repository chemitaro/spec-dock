---
種別: 要件定義書（Issue）
ID: "iss-00474"
関連GitHub: ["#474"]
状態: "approved"
最終更新: "2026-10-31"
---

# iss-00474 Scaffold CUE Scopes With Assurance — 要件定義

詳細: [Requirement Guide](../../../docs/authoring/requirement.md)

## 目的

canonical モード（宣言の版4）の `scope create` と `scope import github` で、保証レベルとその理由を指定して、5つのファイル（`requirement.cue`、`design.cue`、`plan.cue`、`explanation.html`、`report.md`）の一式を持つ CUE の Scope を作れるようにする。指定がないとき、または配布資産が古いときは、GitHub に何も書かずに止まる。

## 背景

- 親：epic-00425（I-3。契約 K4 の持ち主）。Epic の `requirement.md` の R-A5、R-C3、R-H3、AC-01、AC-02、AC-12、AC-18 をこの Issue が受け持つ。
- 前提として、次がマージ済みである（2026-10-31）。
  - I-1（#472）：型 `src/spec_dock/cue/v1/` と、雛形の見本 `tests/fixtures/cue/v1/templates/<種類>/`（置き換えの印 `{{ASSURANCE_LEVEL}}`、`{{ASSURANCE_REASON}}` を含む）。
  - I-2（#473）：`scope check`、`scope show` の `assurance`、`work finish` の検査、`workspace validate`・`doctor` の形式ごとの文書の組。
  - I-4（#475）：配布資産 `spec-dock/design-system/` と、薄い説明資料の雛形 `explanation-skeleton.html`。
- 今の canonical の `scope create` は、`spec-dock/templates/<種類>/` の `.md` の4つを写す。保証レベルを知らない。
- 今の `spec-dock/templates/<種類>/` は、前の版の CLI が使うので、I-7 まで変えない（Epic の design の K4）。

## 観測可能な要件

- **R-01 保証レベルの指定を必須にする**：schema 4 の `scope create <種類>` と `scope import github <種類>` は、`--assurance`（`light`、`standard`、`strict`、`critical` のどれか）と `--assurance-reason`（空白だけでない文）の両方を求める。どちらかがない、または理由が空白だけのとき、GitHub に何も問い合わせず、何も書かずに `ASSURANCE_REQUIRED`（exit 2）で止まる。4つ以外の値は、引数の解析で止まる（`USAGE_ERROR`、exit 2）。`--dry-run` でも同じに止まる。
- **R-02 CUE の一式を作る**：schema 4 の `scope create` は、新しい Scope のディレクトリに、`spec-dock/templates/cue/<種類>/` の5つのファイルを置く。今と同じ規則のリンク（`artifacts/rules.md`、`discussions/rules.md`）も置く。`.md` の要件・設計・計画は置かない。
- **R-03 保証レベルを書き込む**：作った `requirement.cue` の `assurance.level` と `assurance.reason` は、指定した値と理由（前後の空白を除いたもの）である。理由に引用符、改行、タブ、バックスラッシュ、`\(`、制御文字が含まれても、CUE の文字列として正しく、`cue` で読むと元の文に戻る。
- **R-04 `scope import github` の一式**：Scope のディレクトリがないとき、R-02、R-03 と同じ一式を置く。既にディレクトリがあるとき、雛形を足さず、既存のファイルを書き換えず、警告 `ASSURANCE_NOT_WRITTEN` を出す（今の「足りないものだけを足す」動きを守る）。
- **R-05 配布資産が古いときに止まる**：`spec-dock/templates/cue/<種類>/` がない、5つのファイルのどれかがない、または `requirement.cue` に置き換えの印の片方がないとき、`scope create` と（ディレクトリを作る）`scope import github` は、GitHub に何も書かずに `SCOPE_TEMPLATES_OUTDATED`（exit 3）で止まり、次の手順に `spec-dock installation update` を示す。
- **R-06 途中で止まったときの復旧**：`scope create` が GitHub の Issue を作った後に止まったとき、示す `scope import github` の復旧のコマンドは、`--assurance` と `--assurance-reason` を含み、そのまま実行できる（シェルの引用付き）。
- **R-07 schema 3 は今のまま**：schema 3 の `scope create`・`scope import github` は、2つの引数なしで今と同じに動く。2つの引数のどちらかを付けたときは、何も書かずに `CANONICAL_NOT_MIGRATED`（exit 3）で止まる（黙って捨てて `.md` の Scope を作らない）。
- **R-08 作った直後の Scope が検査に通る**：作った直後の CUE の Scope は、`scope check` で、雛形の説明資料の指摘（Initiative と Issue は警告 `EXPLANATION_SKELETON`、Epic は誤り）だけを示す。`scope show --json` は、インターネットなしで、`assurance` の `level`、`reason`、`source: "cue"` を返す。
- **R-09 配布資産**：提供側 `src/spec_dock/assets/spec_dock/templates/cue/{initiative,epic,issue}/` に5つのファイルを置き、`static-inventory.json` に足し、dogfood の写し `spec-dock/templates/cue/` を同じ PR で足す。`explanation.html` は `spec-dock/design-system/explanation-skeleton.html` のバイト一致の写しである。`requirement.cue`、`design.cue`、`plan.cue` は、I-1 の見本を移したものである（見本は消し、I-1 のテストは移した先を読む）。今の `spec-dock/templates/<種類>/` は変えない。
- **R-10 使い方の文書**：`spec-dock help scope create <種類>`、`scope import github <種類>` と、配布資産の `docs/canonical.md` の「エラーと次の1手」、`docs/reference_cli.md`、`docs/cli-redesign-guide.html` の C01〜C06 が、新しい引数とコードを示す。

## スコープ

### 対象

- canonical の `scope create`・`scope import github`（`runtime/application/canonical_scope_create.py`）、雛形の写し（`runtime/infra/canonical_scaffold.py`）、引数（`runtime/cli/catalog.py`）、schema 3 の拒否（`runtime/application/direct_scope_publish.py`）。
- 配布資産 `templates/cue/<種類>/` と、その dogfood の写し、`static-inventory.json`。
- 配布資産の文書の、上の R-10 の箇所（と dogfood の写し）。
- 既存のテストのうち、schema 4 の `scope create`・`import` を呼ぶもの（下の「制約・前提」の扱い）、配布資産の数を固定したもの、I-1 の雛形のテストの読む場所。

### 対象外

- 型（`src/spec_dock/cue/`）、検査（`scope check`、`work finish`）、`scope show` の読み取り（I-1、I-2 の持ち物）。
- デザインシステムと説明資料の雛形の中身（I-4 の持ち物。写すだけ）。
- 書き方のガイド、`spec-dock` スキル、`templates/README.md`（I-6）。
- 今の `.md` の雛形 `templates/<種類>/` を外すこと（I-7）。
- schema 3 で CUE の Scope を作ること（iss-00473 の Q6）。
- `scope create` から `cue` を呼ぶこと（下の D の決定）。

## 失敗・境界条件

- **F-01 引数がない、空白だけ**：`ASSURANCE_REQUIRED`（exit 2）。偽の `gh` に要求が1つも届かない。カタログもチェックアウトも変わらない。
- **F-02 4つ以外の値**：引数の解析の `USAGE_ERROR`（exit 2）。
- **F-03 配布資産が古い**：`SCOPE_TEMPLATES_OUTDATED`（exit 3）。偽の `gh` に書き込みの要求が届かない（読み取りは今の事前の確かめのとおり）。
- **F-04 理由が UTF-8 にできない文字を含む**（端末から渡された不正なバイト列）：`ASSURANCE_REQUIRED`（exit 2）。何も書かない。
- **F-05 Issue を作った後の失敗**：今の `SCOPE_PUBLICATION_INCOMPLETE`（partial）。復旧のコマンドに2つの引数を含む（R-06）。
- **F-06 既にディレクトリがある import**：雛形も保証レベルも書かず、警告 `ASSURANCE_NOT_WRITTEN`。
- **F-07 schema 3 で引数を付けた**：`CANONICAL_NOT_MIGRATED`（exit 3）。何も書かない。
- **F-08 理由に置き換えの印やリンクの形の文が含まれる**（例 `{{ASSURANCE_LEVEL}}`、`YYYY-MM-DD`、`](../docs/`）：理由の文は、ほかの置き換えやリンクの付け替えを受けず、そのまま入る。

## 受け入れ条件

各条件は、テストで確かめる（`plan.md` の「検証」）。

- **AC-01**（Epic AC-01）：schema 4 で、3つの種類それぞれについて、保証レベルと理由を指定した `scope create` が、直下に5つのファイルを作り、`requirement.cue` に指定した値と理由がある。`.md` の要件・設計・計画はない。
- **AC-02**（Epic AC-01 の後半、F-01）：2つの引数のどちらかがない、または理由が空白だけ（全角の空白を含む）の `scope create` と `scope import github` が、`ASSURANCE_REQUIRED`（exit 2）で止まり、偽の `gh` に要求が1つも届かず、カタログが変わらない。`--dry-run` でも同じ。4つ以外の値は `USAGE_ERROR`（exit 2）。
- **AC-03**（R-03、F-04、F-08）：引用符、改行、タブ、バックスラッシュ、`\(`、制御文字、置き換えの印、リンクの形を含む理由が、作った `requirement.cue` を本物の `cue` で読むと、元の理由（前後の空白を除いたもの）に戻る。UTF-8 にできない理由は `ASSURANCE_REQUIRED`。
- **AC-04**（Epic AC-02、R-08）：作った直後の Scope で、`scope check --json` の誤りと警告が、説明資料の雛形の指摘だけ（Issue・Initiative は警告、Epic は誤り）であり、`scope show --json --offline` が `assurance = {level, reason, source: "cue", problem: null}` を返す。
- **AC-05**（R-04、F-06）：ディレクトリがない Issue の `scope import github` が AC-01 と同じ一式を作る。既にディレクトリがある Scope の `scope import github` は、ファイルを足さず、書き換えず、警告 `ASSURANCE_NOT_WRITTEN` を出す。
- **AC-06**（Epic AC-18 の前半、R-05、F-03）：`templates/cue/<種類>/` がないチェックアウト、ファイルが1つ欠けたチェックアウト、印が欠けたチェックアウトで、`scope create` と `scope import github` が `SCOPE_TEMPLATES_OUTDATED`（exit 3）で止まり、`recovery` に `spec-dock installation update` を含み、GitHub に書き込みの要求が届かない。
- **AC-07**（Epic AC-18 の後半）：新しい配布資産でも、`templates/<種類>/` の中身（前の版の CLI がすべてを写す場所）は、今の `.md` の4つのままで、`templates/cue/` はその外にある。schema 3 の `scope create`（今も `templates/<種類>/` を写す）が、新しい配布資産で、今と同じ `.md` の Scope を作る。
- **AC-08**（R-06、F-05）：Issue を作った後に止まった `scope create` の `recovery` の `scope import github` のコマンドが、2つの引数を含み、それをそのまま実行すると Scope ができる。
- **AC-09**（R-07、F-07）：schema 3 で2つの引数を付けた `scope create` と `scope import github` が `CANONICAL_NOT_MIGRATED` で止まり、何も書かない。付けなければ、今の schema 3 の回帰のテストが変更なしで通る。
- **AC-10**（R-09）：配布資産の `templates/cue/<種類>/` の5つのファイルが、`static-inventory.json` にあり、dogfood の写しとバイト一致する。`explanation.html` は `design-system/explanation-skeleton.html` とバイト一致する。作った Scope の `explanation.html` も、雛形とバイト一致する。`installation init` が、新しい15のファイルを置く。
- **AC-11**（R-10）：`help scope create issue` と `help scope import github issue` が、2つの引数を示す。`canonical.md` の表に `ASSURANCE_REQUIRED`、`SCOPE_TEMPLATES_OUTDATED`、`ASSURANCE_NOT_WRITTEN` の行がある（既存の表の検査のテストが通る）。
- **AC-12**（Epic AC-12、AC-15）：`make lint` と `uv run pytest`（`cue` を PATH に置いて）が通る。既存のテストの変更は、下の「制約・前提」の範囲に限る。

## 制約・前提

- **既存のテストの扱い**（2026-10-31、統括の決定。Epic の plan.md の I-3）：schema 4 の `scope create`・`import` を呼ぶ既存のテストは、2つの引数を足すことと、作られるファイルの期待を CUE の一式に変えることだけを変えてよい。ほかの確かめ（GitHub への書き込みの順、題名、種類、親、復旧、エラーの形など）は弱めない。変えたテストと理由を、`report.md` と PR の本文に書く。ほかに、配布資産の数を固定したテスト（I-4 の前例のとおり）、I-1 の雛形のテストの読む場所、葉の数でなく説明の文を固定したテストの更新を、変更として認める。
- Markdown の Scope（既存の Scope の `show`、`finish`、`validate`、`doctor`、schema 3 の作成）の回帰は、変えずに通す。
- 提供側 `src/spec_dock/` を先に変え、dogfood の写しは同じ PR で写す。仕様（`spec-dock/initiatives/`）は Git で扱わない。
- テストは外のネットワークを使わない。GitHub は偽の `gh`。`cue` は、この worktree の無視されている場所に入れた v0.17.1 を PATH に置く。
- 本物の GitHub とカタログに、試しの Issue や CUE の Scope を作らない。
- 判断（2026-10-31、統括が推奨どおりに決定。理由は `design.md` の「決めたこと」）：Q1 schema 3 の扱い、Q2 既にディレクトリがある import、Q3 復旧のコマンド、Q4 エラーのコード、Q5 `cue` を呼ばない、Q6 `report.md` の雛形。
