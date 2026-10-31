---
種別: 設計書（Epic）
ID: "epic-00425"
タイトル: "Switch Spec Documents To CUE And HTML Explanations"
関連GitHub: ["#425"]
状態: "approved"
最終更新: "2026-10-31"
依存: ["requirement.md"]
親: ["init-00423"]
---

# epic-00425 Switch Spec Documents To CUE And HTML Explanations — 設計

詳細: [Design Guide](../../../docs/authoring/design.md)

## 設計目標

- 1つの Scope の `requirement.cue`、`design.cue`、`plan.cue` を、SpecDock が配る型と一緒に1つの CUE の評価にかけ、形の誤りと、つながりの抜けを、インターネットなしで機械的に見つける（R-B）。
- 保証レベルを `requirement.cue` の1か所に置き、型、検査、`scope show`、モデルの選択が、すべてそこを読む（R-C）。
- CUE の文書、説明資料、報告を、同じデザインシステムで HTML に描く。描画の道筋を1本にする（R-E、R-F）。
- 既存の Markdown の Scope は、何も変えずに動き続ける（R-H）。

## Current / Target

| | 今 | この Epic の後 |
|---|---|---|
| 新しい Scope の文書 | `requirement.md`、`design.md`、`plan.md`、`report.md`（`spec-dock/templates/<種類>/` から作る） | `requirement.cue`、`design.cue`、`plan.cue`、`explanation.html`、`report.md` |
| Planning Level | `plan.md` の `## Planning Level` に文章で書く。SpecDock は値を知らない | 保証レベル。`requirement.cue` の `assurance`。`scope create` で必須、`scope show --json` が返す |
| つながりの確かめ | レビュアー（LLM）が読む | `spec-dock scope check` が `cue` で評価する。`work finish` も同じ検査をする |
| 説明資料 | 利用者のスキル（japanese-explanatory-html）で、Scope の外に任意に作る。1ファイル約 345KB（デザインシステムを内蔵） | SpecDock の雛形。Markdown だけを持つ薄い HTML で、デザインシステムは共有のファイルを読む |
| 図の部品 | 説明資料が CDN から読む | SpecDock のパッケージに同梱。ダッシュボードのサーバーが配る。単独で開いたときは CDN |

## 責務・Interface

### 1. 文書の評価の単位（契約 K1）

1つの Scope の CUE の文書は、すべて `package spec` に属し、SpecDock が次のファイルを1つの評価（CUE の instance）にまとめる。

```text
cue export -c --out json -t kind=<種類> \
  <パッケージ>/cue/<型の版>/*.cue      # SpecDock が配る型（R-B1）
  <リポジトリ>/spec-dock/cue/*.cue      # リポジトリが足す型（任意。R-B6）
  <Scope>/requirement.cue <Scope>/design.cue <Scope>/plan.cue
```

- 同じ package のファイルは、ディレクトリが違っても、ファイルを並べて渡せば1つにまとまる（`cue` 0.17.1 で確認。2026-10-31）。そのため、Scope のファイルは `import` を書かない。型は SpecDock が足す。
- Scope の種類（Initiative、Epic、Issue）は、構造の正本である GitHub から取り、タグ `-t kind=` で渡す。種類を CUE に書き写さない（二重管理をしないため）。
- 型の版は、`requirement.cue` の `schema`（例 `"specdock/v1"`）で決める。SpecDock は、まず `requirement.cue` だけを評価して `schema` を読み、その版の型のディレクトリを選ぶ。
- 保証レベルは、`assurance.level` から、型の中の隠した項目 `_rank`（light=0、standard=1、strict=2、critical=3）に変える。レベルで必須の項目を変える型と、つながりの検査は、すべて `_rank` を使う。リポジトリが足す型も、同じ package なので `_rank` を使える（確認済み）。

### 2. 型の骨組み（契約 K2）

型の具体の項目は、I-1 で作り込む。ここでは、Issue をまたいで守る骨組みだけを決める。

```cue
package spec

schema!: "specdock/v1"
kind:    "initiative" | "epic" | "issue" @tag(kind)
assurance: {
	level!:  "light" | "standard" | "strict" | "critical"
	reason!: string & !=""
}

// 番号を持つ項目は、番号をキーにした構造で持つ（順番は order や after で表す）
requirements: [=~"^R-[0-9]{2,}$"]: {...}   // requirement.cue
design:       [=~"^D-[0-9]{2,}$"]: {satisfies!: [...string], ...}   // design.cue
steps:        [=~"^S-[0-9]{2,}$"]: {realizes!: [...string], status: *"todo" | "doing" | "done" | "dropped", after?: [...string], session?: string, ...}   // plan.cue
tests:        [=~"^T-[0-9]{2,}$"]: {verifies!: [...string], ...}   // plan.cue
execution?: {sessions?: [string]: {...}, reviews?: [string]: {after?: string, ...}}   // plan.cue（R-D3）

findings: [rule=string]: [...{id: string, message: string, hint?: string}]
```

- **番号はキー**：要件、設計、手順、テストは、番号をキーにした構造にする。番号の重複は、CUE の構造で起こり得ない（同じキーは1つにまとまる）。2つの定義が食い違えば、CUE の衝突として誤りになる。
- **形の誤りと、つながりの指摘を分ける**：
  - 形の誤り（必須の項目がない、値の形が違う）は、CUE の制約で表し、`cue` の評価の誤りとして出る。
  - つながりの指摘（存在しない番号への参照、要件を満たす手順がない、など）は、型が計算する `findings` に、規則ごとの一覧として出す。存在しない番号を CUE の選択肢の制約にすると、誤りの文が選択肢の数だけ並び、読めない（試作で確認）。そのため、参照の先は文字列として受け、`findings` で調べる。
  - `findings` は規則の名前をキーにするので、リポジトリが足す型も、規則を足せる（確認済み）。
- **レベルの表（R-B3）**：各規則は、`if _rank >= <段階> { findings: "<規則>": [...] }` の形で書く。表の1行が、型の1つの規則に当たる。

  | 規則の名前 | 内容 | 出す段階 |
  |---|---|---|
  | `unknown-reference` | 存在しない番号への参照 | 0（light） |
  | `requirement-without-step` | 要件を満たす手順がない | 0 |
  | `requirement-without-design` | 要件を満たす設計がない | 1（standard） |
  | `requirement-without-test` | 要件を確かめるテストがない | 1 |
  | `orphan-step` | どの要件にも結び付かない手順 | 2（strict） |
  | `failure-without-test` | 失敗の条件に、確かめるテストがない | 2 |
  | `rollback-missing` | 戻し方がない | 3（critical） |
  | `execution-reference` | 手順が存在しないセッションを指す、レビューが存在しない手順を指す | 0（`execution` があるときだけ。R-D4） |

- **種類ごとの違い**：Epic と Initiative の計画は、手順とテストの代わりに、子の Scope への切り分け `slices: [=~"^(epic|iss)-[0-9]{5,}$"]: {covers!: [...string], ...}`（子の ID と、その子に任せる要件）を持つ。子の保証レベルは書かない（R-C4）。種類ごとの必須の項目は、`if kind == "epic" {...}` で切り替える。規則は、R-B3 の表の後の注のとおりに読み替える。Epic と Initiative では、`requirement-without-step`、`requirement-without-test`、`failure-without-test` は、`slices` の `covers` に入っていれば満たす。`orphan-step` は、`covers` が空の切り分けに当てはめる。`requirement-without-design` は、Issue と同じに当てはめる。
- **文章の項目**：説明の文章を持つ項目は、Markdown を書いてよい。描画のときに、Markdown として描く（契約 K5）。

### 3. 検査のコマンド（契約 K3、R-B4、R-B7、R-E4）

- `spec-dock scope check <ID> [--json]` を足す。Scope の種類と、CUE の Scope か Markdown の Scope かを見分け、CUE の Scope なら次を行う。読むだけのコマンドで、何も書かない。
  1. `cue` があり、版が足りるか（R-G1）。
  2. `requirement.cue` だけを評価して、`schema` を読む。
  3. 契約 K1 のとおりに評価し、`cue` の誤りを、ファイル、位置、項目の道筋に分けて示す。
  4. `findings` を読み、規則ごとに、番号、文、直し方を示す。
  5. `explanation.html` の形を検査する（契約 K5 の「薄い説明資料の形」。ない、または雛形のままなら、Epic では誤り、ほかは警告。形を壊していれば誤り）。
- 結果の JSON は、今の CLI の共通の封筒（`specdock.cli/v2`）に従う。誤りは `CUE_INVALID`、`SPEC_FINDINGS`、`EXPLANATION_INVALID` などの番号で示す（名前は I-2 で決める）。
- Markdown の Scope では、「CUE の Scope ではない」と示して、成功で終わる（R-H1）。両方があれば、誤りで止まる。
- `work finish` は、閉じる前（保存の確かめより前、何かを書く前）に、閉じる Scope だけを、同じ検査にかける（子孫は、今の `work finish` のとおり、既に閉じていなければ止まるので、検査し直さない）。誤りがあれば、何も書かずに止まり、誤りと、直した後のコマンドを示す（R-B7）。
- `workspace validate` と `workspace doctor`（`canonical_workspace.py` の `REQUIRED_DOCUMENTS`）は、Scope の形式ごとに必須のファイルの組を変える。Markdown の Scope は今の4つ（`requirement.md`、`design.md`、`plan.md`、`report.md`）、CUE の Scope は4つ（`requirement.cue`、`design.cue`、`plan.cue`、`report.md`）。`explanation.html` は、ここでは判定せず、`scope check` と `work finish` だけが判定する（判定を1か所にそろえるため）。`requirement.md` と `requirement.cue` の両方がある Scope は誤りにする。形式は、`requirement.cue` があるかで決める。CUE の評価は行わない（`cue` がなくても動く）。
- `scope show <ID> --json` は、`assurance`（`level`、`reason`、`source`）を返す。`source` は `cue`、`unset`（Markdown の Scope）、`unreadable`（読めない）のどれかである（R-C6）。読むのは `requirement.cue` だけで、型は使わない。

### 4. 作るときの一式と、保証レベル（契約 K4、R-A5、R-C3）

- `scope create <種類>` と `scope import github` に、`--assurance <値>` と `--assurance-reason <文>` を足し、必須にする。どちらかがなければ、GitHub にも何も書かずに止まる（引数の段階で止める）。
- 雛形は、新しい場所 `spec-dock/templates/cue/<種類>/` に置き、新しい CLI はそこだけから作る。今の `spec-dock/templates/<種類>/` の `.md` の雛形は、前の版の CLI のために、I-7 まで残す（I-7 の後は、前の版の CLI は雛形がないので、GitHub に書く前に止まる。安全な側の止まり方である）（前の版の CLI は、雛形のディレクトリのファイルをすべて写すので、同じ場所に CUE の雛形を置くと、置き換えられない印の残る Scope ができる）。`templates/cue/<種類>/` がないとき（新しい版の CLI と、上げていない配布資産）、新しい CLI は、GitHub に何も書かずに止まり、`installation update` を示す（R-H3）。雛形の CUE には、`{{ASSURANCE_LEVEL}}` と `{{ASSURANCE_REASON}}` の置き換えの印を置く。理由の文は、CUE の文字列として正しくなるように、置き換えの前に CUE の文字列の書き方に変える（引用符や改行）。
- 今の `scope import github` が、既にディレクトリがある Scope を補うときは、雛形を足さず、保証レベルも書かない（今の「足りないものだけを足す」動きを守る）。
- 説明資料の雛形 `explanation.html` は、Markdown を書く場所と、共有のデザインシステムを読み込む数行だけを持つ（下の契約 K5）。

### 5. 描画と、デザインシステム（契約 K5、R-E1、R-F1、R-F2）

- **デザインシステム**：今の japanese-explanatory-html のデザインシステム（`ds.css`、`ds.js`、`marked`）を、SpecDock の配布資産として、リポジトリの `spec-dock/design-system/` に置く。利用者のスキルから写して、SpecDock が持つ。
- **薄い説明資料の形**：Scope の `explanation.html` は、次の3つだけを持つ。検査（K3）は、この形を確かめる。
  - `<script type="text/markdown" id="ds-source">` がちょうど1つあり、中の Markdown の先頭に `title` を持つ前付けがある。
  - `../../../design-system/ds.css` と `../../../design-system/ds.js` を読む指定がある（`marked` は `ds.js` が読む）。
  - 雛形の Markdown には、印 `<!-- spec-dock:explanation-skeleton -->` を置く。この印が残っていれば「雛形のまま」と判定する。書き換えた人は、印を消す。
- **雛形の置き場**（2026-10-31、I-4 の確認で決定）：説明資料の雛形は、I-4 が配布資産 `spec-dock/design-system/explanation-skeleton.html` として、デザインシステムと同じ版で置く。I-3 は、これを `templates/cue/<種類>/explanation.html` に写し、中身のバイト一致をテストで確かめる。`templates/cue/` は K4 の持ち物（I-3）なので、I-4 は触れない。
- **図の部品の読み込み先**（同上）：ページの `<meta name="ds-vendor-base" content="<URL>">` で示す。その下の道筋は `plantuml/<版>/` と `highlightjs/<版>/` に固定する（初めの版は `@plantuml/core` 1.2026.6、highlight.js 11.11.1）。
- **相対の道筋**：説明資料は、`../../../design-system/` からデザインシステムを読む。カタログは、どのPCでも main のチェックアウトの `spec-dock/.canonical/` にあり、`spec-dock/initiatives/` から開いても同じ深さなので、この相対の道筋は、どちらから開いても `spec-dock/design-system/` に届く。1つの Scope に約 300KB のデザインシステムを写さずに済み、デザインシステムを上げても、Scope のファイルは変わらない。
- **図の部品**：`@plantuml/core`（約 10.6MB）と highlight.js は、版を固定して Python のパッケージにだけ同梱し、リポジトリには置かない。`ds.js` は、部品の読み込み先を、ページが示す手元の場所（ダッシュボードのサーバー）、CDN の順に試す。ファイルを単独で開いたときは、CDN から読む。
- **CUE の描画**：SpecDock の Python の部品が、契約 K1 で評価した JSON を、決まった並びの Markdown に変え、同じデザインシステムの薄い HTML に包む。要件ごとに、それを満たす設計、手順、テストを、番号のリンクで結ぶ。`findings` も、ページの初めに示す。入口は、Python の関数（`render_scope_html(<Scope>, *, design_system_base: str, vendor_base: str | None) -> str`）と、確かめ用の `spec-dock scope render <ID>`（標準出力に HTML）の2つにする。`design_system_base` はデザインシステムを読む URL の頭、`vendor_base` は図の部品を読む URL の頭（`None` なら CDN）である。ダッシュボードのサーバー（epic-00427）は、自分が配る URL を渡す。`scope render` の既定は、そのチェックアウトの `spec-dock/design-system/` を指す `file:` の URL と、`vendor_base` なし（CDN）である。
- 報告と ADR の Markdown も、同じ薄い HTML に包めば描ける（epic-00427 が使う）。

### 6. 型の版と、リポジトリの型（契約 K6、R-B5、R-B6）

- 型は、パッケージの `cue/v1/`、`cue/v2/` … に版ごとに置く。版の中身は、出した後は変えない（直すときは、互換を壊さない足し方だけにする）。互換を壊す変更は、新しい版にする。
- SpecDock は、持っているすべての版を配る。持っていない版の `schema` を読んだら、SpecDock を上げるよう示して止まる。
- 前の版の Scope を新しい版に上げる道具は、この Epic では作らない（必要になったら足す）。
- リポジトリの型は、リポジトリの `spec-dock/cue/*.cue`（既定のブランチに置く、リポジトリの決まり）に置く。SpecDock は、あれば評価に加える。リポジトリの型は、`package spec` で、SpecDock の型を変えずに制約と規則を足す。

## data / failure

- **書くもの**：`scope create` と `scope import github` が、雛形の5つのファイルを、今と同じカタログの1つの変更として書く。`scope check`、`scope show`、`scope render` は、何も書かない。`work finish` は、検査で止まったときは何も書かない。
- **`cue` を呼ぶ**：`cue` は、子のプロセスとして、引数の並びで呼ぶ（シェルを通さない）。時間の上限を設ける。`cue` の誤りの文は、そのまま利用者に見せる部分と、ファイル・位置に分けた部分の両方を返す。
- **`cue` がない、古い**：CUE を扱うコマンドは、入れ方を示して止まる。`scope show` は、`assurance` を `unreadable` にし、ほかの情報は返す。`cue` の最低の版は I-2 で決める（試作は 0.17.1）。
- **文法の誤り**：`scope check` は誤りを示す。`scope show` は `assurance.source = unreadable` を返す。`work finish` は止まる。
- **両方がある Scope**：`requirement.md` と `requirement.cue` の両方があれば、`scope check` と `work finish` は止まる。`scope show` は `unreadable` を返す。
- **リポジトリの型の誤り**：どの Scope の検査も、リポジトリの型のファイルの位置を示して止まる。

## 変更対象

- **提供側**（`src/spec_dock/`）
  - `assets/spec_dock/templates/cue/{initiative,epic,issue}/`：CUE の雛形、`explanation.html`、`report.md`（新しい配布資産）。今の `templates/{initiative,epic,issue}/` は I-7 で外す。
  - `assets/spec_dock/design-system/`：デザインシステム（新しい配布資産）。`assets/static-inventory.json` に足す。
  - パッケージの `cue/v1/`：型。パッケージの図の部品（配布資産ではなく、パッケージの中のファイル）。
  - `runtime/application/`：`canonical_scope_create.py`（必須の引数、置き換え）、`canonical_scope_read.py`（`assurance`）、`canonical_work.py`（`work finish` の検査）、`canonical_workspace.py`（形式ごとの必須のファイル）、新しい検査と描画の部品。
  - `runtime/infra/`：`cue` を呼ぶ部品。
  - `runtime/cli/`：`scope check`、`scope render`、`--assurance`、`--assurance-reason`。
  - `assets/spec_dock/docs/authoring/`：CUE の書き方、説明資料の書き方、Issue Plan Guide と overview の Planning Level の記述を保証レベルに直す。
  - `assets/install_root/.agents/skills/spec-dock/SKILL.md`：短い整理とガイドへのリンク。
- **変えないもの**：Markdown の Scope の読み書き、今の CLI の共通の契約、カタログの保存と同期、GitHub の構造の扱い、`canonical check`（既定のブランチの検査）。カタログに新しい共有のファイルは置かない（デザインシステムはリポジトリの側に置く）。

## 移行・互換性・rollback

- 既存の Markdown の Scope は移さない。SpecDock は、ファイルの拡張子で CUE の Scope と Markdown の Scope を見分ける（R-H1、R-H2）。
- `scope create` と `scope import github` の新しい必須の引数は、配られる CLI の契約の変更である。呼んでいるスクリプトやスキル（`spec-dock` スキル、利用者の `coordinate` などの手順）は、引数を足す必要がある。版を上げるときの文書に書く。
- 配布資産を変える PR は、dogfood の写し（`spec-dock/` の下）も同じ PR で更新する。spec-dock の検査のワークフロー（`canonical check` の規則5）と、写しの一致のテスト（`tests/unit/infra/test_authoring_kit_assets.py`）が、それを求めるためである。新しい雛形は `templates/cue/` にあるので、写しを先に入れても、前の版の CLI の動きは変わらない。
- 配布資産（雛形、デザインシステム、ガイド、スキル）は、`installation update` で入る。spec-dock リポジトリで、承認された導入の手順として行う（R-J1）。ほかのリポジトリは、利用者の判断で行う。
- 戻すときは、前の版の SpecDock を入れ直し、配布資産を戻す。それまでに作った CUE の Scope のファイルは、カタログに残る。前の版は CUE の Scope を知らないので、それらの Scope に `work start` などはできるが、検査はされない。戻すかどうかは利用者が決める。

## testability

- 型（I-1）：R-B3 の表の各行について、違反する文書と違反しない文書の組を、4つのレベルのすべてで評価するテスト（AC-03）。保証レベルを書き換えたときの必須の項目の変化（AC-04）。`execution` のつながり（AC-06）。版の固定（v1 の型で書いた見本の Scope が、後の変更の後も同じ結果になる。AC-07）。
- 検査のコマンド（I-2）：`cue` を実際に呼ぶ統合テストと、`cue` がない、古い、時間切れの場合の偽の `cue`。`work finish` の止まり方（AC-16）。インターネットを使わないこと（AC-05）。
- 作るとき（I-3）：必須の引数、置き換え、引用符や改行を含む理由、GitHub に書く前に止まること（AC-01、AC-02）。
- 描画（I-4、I-5）：手元から部品を配ったときに、ネットワークを止めたブラウザーで図が描けること（AC-10）。雛形の説明資料のブラウザーでの検査（AC-11）。CUE の描画の結果（AC-09）。
- 共存：Markdown と CUE の Scope が並ぶ見本のリポジトリでの回帰と、`workspace validate`・`doctor`（AC-12）。前の版の CLI の雛形の読み方が、新しい配布資産で変わらないこと、新しい CLI が古い配布資産で止まること（AC-18）。
- 説明資料の検査（I-2）：雛形のまま、ない、形を壊した、の3つ（AC-17）。
- ガイド（I-6）：白紙のエージェントでの試行（AC-13）。
- `cue` を CI で使うため、I-1 で、Provider CI に `cue` の導入の手順を足す。版を固定し、取得したファイルの checksum を確かめる。`cue` を要するテストは、`cue` がないときに飛ばさず、失敗にする（受け入れの証拠を CI で確かめるため）。

## risk

- **型が硬すぎる、または緩すぎる**：使ってみるまで分からない。必須の項目は最小から始め、実際の Issue（R-J1）で直す。型の版で、前の文書を壊さない。
- **`cue` の誤りの文が分かりにくい**：つながりは `findings` に分け、形の誤りだけを `cue` の文で示す。誤りの文に、直し方のヒントを足す。
- **`@plantuml/core` が新しい**：版を固定し、上げるときは描画のテストを通す。CDN の予備を残す。
- **デザインシステムを利用者のスキルから写す**：2つが別々に進む。SpecDock の側を正とし、スキルの側の変更を取り込むときは、SpecDock のテストで確かめる。利用者のスキルは、SpecDock の薄い説明資料を直接扱えない（スキルの検査は、デザインシステムを内蔵したファイルを求める）。SpecDock のガイドで、書き方と検査のコマンドを示す。
- **保証レベルを読む利用者の policy**：今は Planning Level の名前で書かれている。利用者が直すまで、名前がずれる。ガイドに、Planning Level が保証レベルになったことを書く。
- **過去の「Assurance」と名前が重なる**：過去の `.assurance.json` と別のものだと、ガイドで区別する。
