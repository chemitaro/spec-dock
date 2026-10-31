---
種別: 要件定義書（Issue）
ID: "iss-00477"
関連GitHub: ["#477"]
状態: "approved"
最終更新: "2026-11-01"
---

# iss-00477 Document CUE Authoring And Release — 要件定義

詳細: [Requirement Guide](../../../docs/authoring/requirement.md)

## 目的

エージェントが、配布される `spec-dock` スキルと `docs/authoring/` のガイドだけを頼りに、CUE の要件・設計・計画を書き、`spec-dock scope check` に通し、計画（`plan.cue`）を作業しながら更新できるようにする。I-1〜I-5（#472〜#476）の成果を1つのリポジトリでつないで確かめ、SpecDock 0.4.0 を出す準備をする（epic-00425 の I-6）。

## 背景

- I-1〜I-5 はマージ済みで、CUE の型 `specdock/v1`、`scope check`、`work finish` の検査、`scope show` の `assurance`、`scope create`・`scope import github` の `--assurance`・`--assurance-reason`、`templates/cue/<種類>/`、デザインシステムと薄い説明資料、`scope render` がある。しかし、使い方を通して書いたガイドがなく、`spec-dock` スキルも新しい必須の引数を知らない。今のままでは、スキルに従った `scope create` が `ASSURANCE_REQUIRED` で止まる。
- I-2〜I-5 の報告が、この Issue に次を回した：`docs/canonical.md` の表に、保存を待つ間に開き直された `work finish` の partial（終了コード6）を書く（I-2 のゲートの P3）。`ASSURANCE_*` の行を縛るテストを足す（I-3 のゲートの P3）。`SCOPE_KIND_CHANGED` の復旧の文を直す（I-3）。公開の葉が増えたこと（`scope check`、`scope render`）と新しい必須の引数を、版の文書、スキル、`templates/README.md`、ガイドに書く（I-3、I-5）。
- 版は 0.4.0 にする（利用者の決定、2026-11-01）。版のタグは、マージの後に統括が作る。
- 関係者：CUE の Scope を書くエージェント、説明資料を読む利用者、I-7 で spec-dock に導入する統括。

## 観測可能な要件

- **R-01 CUE の書き方のガイド**：`docs/authoring/cue.md` が、次を1本で説明する。評価の単位（3つのファイル、`package spec`、型を足すのは SpecDock で、Scope のファイルは `import` を書かない）、`schema`、保証レベル（値、選び方、理由、書き換えてよいこと、正本は `requirement.cue` の `assurance` だけ、一段上で決めること）、文書ごとの項目と番号（R、F、D、S、T、切り分けの ID）、保証レベルごとに必須になる項目、つながりの規則の表（8つの規則の名前、内容、出る段階、Epic・Initiative での読み替え）、計画の台帳（`status`、`after`、`dropped`）、`execution`、リポジトリの型（`spec-dock/cue/*.cue`）、`scope check`・`scope show`・`scope render`・`work finish` での使い方と結果のコード、`cue` の入れ方と最低の版。Issue の CUE の見本を載せ、見本は standard で `scope check` の誤りも指摘もなく通る。
- **R-02 説明資料の書き方のガイド**：`docs/authoring/explanation.md` が、置き場（Scope の直下の `explanation.html` の1つ）、薄い形（`ds-source` の1つ、前付けの `title`、`../../../design-system/ds.css` と `ds.js`）、雛形の印と、それを消すこと、説明資料と CUE の正本の関係、検査（ない・雛形のまま・形を壊した、の重さ）、図の部品の読み込み先（CDN と手元）、ブラウザーでの確かめが手元で任意であることを説明する。
- **R-03 既存のガイドの保証レベル**：`overview.md`、`issue-plan.md`、`scope-layering.md` が、CUE の Scope では Planning Level が保証レベル（`requirement.cue` の `assurance`）になったことを書き、新しい2つのガイドへつなぐ。Markdown の Scope では今の Planning Level の書き方（`plan.md` の `## Planning Level`）が残ることを書く。`historical.md` が、過去の「Assurance」（`.assurance.json`、旧 Profile）と新しい保証レベルが別のものだと書く。
- **R-04 雛形の一覧**：`templates/README.md` が、`cue/<種類>/` の5つのファイル、置き換えの印、`scope create` の2つの必須の引数、新しいガイドを示す。今の `.md` の雛形の記述は残す。
- **R-05 スキル**：配布する `spec-dock` スキルが、CUE の Scope と説明資料の扱いを短く示し（`--assurance`・`--assurance-reason` の必須、`scope check`、`scope render`、`work finish` の検査、計画を直接書き換えること）、詳しくは2つのガイドへつなぐ。
- **R-06 canonical.md の表と復旧の文**：`docs/canonical.md` の「エラーと次の1手」が、待つ間に開き直された CUE の Scope の `work finish` の partial（終了コード6）を書く。`SCOPE_KIND_CHANGED` の次の1手（表と、ランタイムの `recovery`・`next_step`）が、作り直した Scope は CUE の Scope になり、Markdown の文書をそのまま移すと `SCOPE_FORMAT_CONFLICT` になることと、正しい手順を示す。
- **R-07 版 0.4.0**：パッケージの版、`uv.lock`、配布資産の `system/spec-dock-version`（提供側と dogfood の写し）が 0.4.0 になる。`docs/migration.md` に「0.4.0 への更新」の節があり、CLI の契約の変更（`scope check`・`scope render` の追加、`scope create`・`scope import github` の `--assurance`・`--assurance-reason` の必須化）、`cue` v0.17.1 以上が CUE の Scope に要ること、`installation update` で配布資産を上げることを書く。ルートの `README.md` を最小限直す（55コマンド、0.4.0 の節へのリンク、`cue` が必須になったこと。統括の許可、2026-11-01）。
- **R-08 つないだ確かめ**：Markdown の Scope と CUE の Scope が並ぶ見本のリポジトリで、`scope create`（CUE）、`scope show`、`scope check`、`scope render`、`workspace validate`、`workspace doctor`、`work start`、`work finish` が、どちらの形式でも正しく動くことを、1つの統合テストで確かめる（Epic の AC-12）。
- **R-09 白紙のエージェントでの試行**：この会話と設計書を知らない新しいエージェント（opus / medium）が、スキルとガイドだけで、テスト用の一時のリポジトリで、CUE の要件・設計・計画を書き、検査に通し、計画を更新できる（Epic の AC-13）。迷った点と、それで直したガイドを `report.md` に書く。

## スコープ

### 対象

- 配布資産の文書：`docs/authoring/{cue,explanation,overview,issue-plan,scope-layering,historical}.md`、`docs/canonical.md`、`docs/migration.md`、`templates/README.md`、`system/spec-dock-version`、`static-inventory.json`、配布する `spec-dock` スキル。dogfood の写し（`spec-dock/` の下、ルートの `.agents/skills/spec-dock/SKILL.md`）を同じ PR で写す。
- ランタイム：`canonical_errors.py` の `SCOPE_KIND_CHANGED_RECOVERY` の文だけ。
- `pyproject.toml` の版、`uv.lock`、ルートの `README.md`（上の最小限）。
- テスト：文書をランタイムと型に縛るテスト、つないだ統合テスト、表の行のテスト。

### 対象外

- CUE の型、検査、作成、描画の振る舞いの変更（I-1〜I-5 の持ち物）。
- 今の `spec-dock/templates/<種類>/` の `.md` の雛形の変更と撤去（I-7）。
- 版のタグの作成と、利用者の環境への導入（統括、I-7）。
- spec-dock の本物のカタログでの CUE の Scope の作成（I-7）。
- 利用者のスキルと手順（`coordinate` など）、policy の書き換え。
- ルートの `README.md` の、上の最小限より先の直し。

### 親の契約として守る境界

- Epic の目的、Issue の分け方、K1〜K6 を変えない。ガイドは K1〜K6 を言い換えずに説明する。

## 失敗・境界条件

- **F-01 ガイドと実物がずれる**：規則の名前、結果のコード、雛形の印、デザインシステムの道筋が、型やランタイムと違う。テストが、ガイドの記述を型とランタイムの定数に照らして落ちる。
- **F-02 ガイドの見本が検査に通らない**：`cue.md` の見本を写したエージェントが誤りを受ける。テストが、見本を本物の `cue` で検査し、誤りか指摘があれば落ちる。
- **F-03 Markdown の Scope の回帰**：既存のガイドの直しで、Markdown の Scope の書き方の節が消える、または既存のテストが落ちる。既存の見出しと語を残し、既存のテストは、統括が許した変更（新しいガイドへのリンクを、リンクの集合の期待に足すこと）と、資産を足すと必ず変わる資産の数だけを変える。
- **F-04 dogfood の写しのずれ**：提供側と写しのバイトが違う、または目録の `sha256` が違う。既存の写しと目録のテストが落ちる。
- **F-05 版の食い違い**：パッケージの版と `spec-dock-version` が違うと、`canonical check` と配布の確かめが食い違う。テストが3つの版の一致を確かめる。
- **F-06 復旧の文の誤り**：`SCOPE_KIND_CHANGED` の文に従うと `SCOPE_FORMAT_CONFLICT` になる。テストが、文が CUE の作り直しと `SCOPE_FORMAT_CONFLICT` を名指すことを確かめる。

## 受け入れ条件

- **AC-01**（R-01、F-01、F-02）：`cue.md` が、v1 の型の8つの規則の名前をすべて、型の規則と同じ段階で示し、`scope check` の結果のコード（`CUE_INVALID`、`SPEC_FINDINGS`、`ASSURANCE_UNREADABLE`、`SCOPE_FORMAT_CONFLICT`、`SCOPE_DOCUMENT_MISSING`、`EXPLANATION_*`、`CUE_*`、`SCOPE_CHECK_FAILED`）を示す。見本の3つのファイルを写した Issue が、standard で `scope check` の誤りも警告もなく通る（説明資料は書き換えたものを置く）。テストで確かめる。
- **AC-02**（R-02、F-01）：`explanation.md` が、雛形の印と、デザインシステムの2つの道筋を、検査の部品の定数と同じ文字で示し、3つの検査の重さ（Epic で誤り、ほかで警告、形を壊すと誤り）を示す。テストで確かめる。
- **AC-03**（R-03、F-03）：`overview.md`、`issue-plan.md`、`scope-layering.md` が「保証レベル」と2つのガイドへのリンクを持ち、Markdown の Scope では Planning Level が残ることを書く。`historical.md` が `.assurance.json` と保証レベルの区別を書く。既存の authoring のテストが、リンクの集合の期待の追加だけで通る。
- **AC-04**（R-04）：`templates/README.md` が、3つの種類の `cue/<種類>/` の5つのファイル、`{{ASSURANCE_LEVEL}}`、`{{ASSURANCE_REASON}}`、`--assurance`、`--assurance-reason` を示し、2つのガイドへつなぐ。テストで確かめる。
- **AC-05**（R-05）：スキルが `--assurance`、`--assurance-reason`、`scope check`、`scope render`、`plan.cue`、2つのガイドの道筋を含み、提供側とルートの写しがバイト一致する。テストで確かめる。
- **AC-06**（R-06、F-06）：`canonical.md` の `SCOPE_CHECK_FAILED` の行が終了コード6（partial）を示す。`ASSURANCE_REQUIRED`、`ASSURANCE_NOT_WRITTEN`、`SCOPE_TEMPLATES_OUTDATED` を含む、CUE の Scope の部品（作成、検査、描画、`cue` の呼び出し）の公開のコードが、表か `cue.md` のコードの表にあり、次の1手を持つ。`SCOPE_KIND_CHANGED` の表の行とランタイムの文が `SCOPE_FORMAT_CONFLICT` と `--assurance` を含む。テストで確かめる。
- **AC-07**（R-07、F-05）：`pyproject.toml`、`uv.lock`、提供側と写しの `spec-dock-version` が 0.4.0 で一致し、`migration.md` の「0.4.0 への更新」が4つの契約の変更と `cue` v0.17.1 を示す。ルートの `README.md` が55コマンドと0.4.0 の節へのリンクを示す。テストで確かめる。
- **AC-08**（R-08、Epic の AC-12）：統合テストが、1つのリポジトリで、Markdown の Scope と、`scope create` で作った CUE の Scope について、`scope show` の `assurance.source`（`unset`、`cue`）、`scope check`（Markdown は検査しない成功、CUE は誤りなし）、`scope render`（CUE は HTML、Markdown は `SCOPE_NOT_CUE`）、`workspace validate`・`workspace doctor`（文書の欠落の誤りなし）、`work start`、誤りの残る CUE の Scope の `work finish` の停止と直した後の完了、Markdown の Scope の `work finish` の完了を確かめる。
- **AC-09**（R-09、Epic の AC-13）：白紙のエージェントの試行の結果（使ったもの、書いた文書、検査の結果、計画の更新、迷った点、直したガイド）が `report.md` にある。
- **AC-10**（F-03、F-04、Epic の AC-12、AC-15）：`make lint` と `uv run pytest`（`cue` v0.17.1 を PATH に通す）が通る。既存のテストの変更は、F-03 に書いたものだけで、`report.md` と PR に書く。

## 制約・前提

- テストは外のネットワークを使わない。GitHub は偽の `gh` で置き換える。白紙のエージェントの試行も、本物のカタログと GitHub を使わない。
- `cue` は、この worktree の無視されている `.workbench/bin` に v0.17.1 を入れて使う。
- 仕様は Git で扱わない。コードと配布資産だけをコミットする。
- 既存のテストの変更は、統括の許可（2026-11-01：リンクの集合の期待に新しいガイドへのリンクを足すこと）の範囲と、資産を足すと必ず変わる資産の数（I-3、I-4 の前例）に限る。
