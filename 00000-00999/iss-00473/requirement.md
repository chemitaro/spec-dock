---
種別: 要件定義書（Issue）
ID: "iss-00473"
タイトル: "Add Scope Check With CUE"
関連GitHub: ["#473"]
状態: "draft"
最終更新: "2026-10-31"
親: ["epic-00425", "init-00423"]
---

# iss-00473 Add Scope Check With CUE — 要件定義

詳細: [Requirement Guide](../../../docs/authoring/requirement.md)

表示名：CUE の Scope を検査するコマンドを足し、`work finish`・`scope show`・`workspace validate`・`doctor` を CUE の Scope に対応させる

## 目的

CUE で書いた Scope の要件・設計・計画と説明資料を、SpecDock が、インターネットなしで機械的に検査できるようにする。

- `spec-dock scope check <ID>` で、1つの Scope の CUE の文書を、I-1 の型（`specdock/v1`）と一緒に評価し、形の誤り、つながりの指摘、説明資料の形を、ファイル、項目、直し方とともに示す。JSON でも出す。
- `work finish` が、誤りの残る CUE の Scope を閉じない。
- `scope show --json` が、保証レベルの値と理由を返す。
- `workspace validate` と `workspace doctor` が、CUE の Scope を、文書の欠落の誤りにしない。

## 背景

- 親の Epic（epic-00425）は、仕様の正本を Markdown から CUE に移す。I-1（iss-00472、PR #480、マージ済み）が型 `src/spec_dock/cue/v1/` と版の置き場を返す部品 `runtime/infra/cue_schemas.py` を作った。I-4（iss-00475、PR #479、マージ済み）が、説明資料のデザインシステムと、雛形 `spec-dock/design-system/explanation-skeleton.html` を作った。
- 製品の中で `cue` を呼ぶ部品は、まだない。型は、テスト（`tests/support/cue.py`）からしか評価されていない。
- 今の `workspace validate`・`doctor` は、すべての Scope に `requirement.md`、`design.md`、`plan.md`、`report.md` を求める。CUE の Scope は、文書の欠落の誤りになる。
- 今の `scope show` は、保証レベルを知らない。統括は、worker のモデルと推論を選ぶ前に、保証レベルを機械的に読めない。
- この Issue は、Epic の契約 K3（検査の結果の形）の持ち主で、K1 の評価の呼び出しを作る。K3 は、I-3、I-5、I-6、epic-00427 が使う。

## 観測可能な要件

番号は、この文書の中だけで使う。

### 検査のコマンド（R-B4、K3）

- **RQ-01 コマンド**：`spec-dock scope check <ID>` を足す。`--json` で `specdock.cli/v2` の封筒を返す。読むだけで、カタログ、GitHub、チェックアウトに何も書かない（GitHub の構造の写しの更新は、ほかの読むコマンドと同じ）。
- **RQ-02 Scope の形式**：`requirement.cue` があれば CUE の Scope、なければ Markdown の Scope と判定する。`requirement.md` と `requirement.cue` の両方があれば、誤り（`SCOPE_FORMAT_CONFLICT`）にする。
- **RQ-03 Markdown の Scope**：成功で終わり、CUE の Scope ではないこと（`format: "markdown"`、`checked: false`）を示す。`cue` を求めない。
- **RQ-04 評価**：CUE の Scope では、`requirement.cue` だけから `schema` を読み、その版の型のディレクトリを選び、契約 K1 のとおりに、型、リポジトリの型（チェックアウトの `spec-dock/cue/*.cue`、あれば）、Scope の3つのファイルを、GitHub の種類のタグ（`-t kind=`）とともに1つの評価にかける。
- **RQ-05 形の誤り**：`cue` の評価の誤りを、1件ずつ、ファイル、行、列、項目の道筋、`cue` の文、直し方に分けて示す（`CUE_INVALID`）。型の中の計算から重ねて出る誤り（隠した項目 `_` から始まる道筋など）は、ほかの誤りがあるときは示さない。`cue` の誤りの文の全体も返す。
- **RQ-06 つながりの指摘**：評価が通れば、`findings` の空でない規則の指摘を、1件ずつ、規則、番号、ファイル、文、直し方とともに示す（`SPEC_FINDINGS`）。指摘は誤りとする。`findings` の全体も返す。
- **RQ-07 保証レベルの置き場**：保証レベルが `requirement.cue` だけからは読めない（ほかのファイルに書いた、など）とき、評価が通っても誤り（`ASSURANCE_UNREADABLE`）にする（R-C2。`scope show` との食い違いを防ぐ）。`schema` も `requirement.cue` だけから読む。
- **RQ-08 説明資料の形**：Epic の design.md の K5 の「薄い説明資料の形」を検査する。
  - `explanation.html` がない（`EXPLANATION_MISSING`）、印 `<!-- spec-dock:explanation-skeleton -->` が残っている（`EXPLANATION_SKELETON`）：Epic では誤り、Initiative と Issue では警告。
  - 形を壊している（`EXPLANATION_INVALID`。常に誤り）：`<script type="text/markdown" id="ds-source">` がちょうど1つでない、その Markdown の先頭に `title` を持つ前付けがない、`../../../design-system/ds.css` を読む `<link rel="stylesheet">` がない、`../../../design-system/ds.js` を読む `<script src>` がない。
- **RQ-09 結果と終了の状態**：誤りがなければ成功（exit 0。警告だけでもよい）。誤りがあれば失敗（exit 7、`SCOPE_CHECK_FAILED`）で、結果に、すべての誤りと警告を返す。テキストでも、1件ずつ、コード、ファイル、項目、文、直し方を示す。

### `cue` の道具（R-G1）

- **RQ-10 道具の確かめ**：CUE の Scope を評価する前に、`cue` が PATH にあり、版が v0.17.1 以上かを確かめる。ない（`CUE_NOT_FOUND`）、版が古い・読めない（`CUE_VERSION_UNSUPPORTED`）なら、入れ方を示し、何も書かずに止まる（exit 3）。
- **RQ-11 呼び方**：`cue` は、シェルを通さず、引数の並びで、時間の上限（`--timeout`、既定30秒）を付けて呼ぶ。時間切れ（`CUE_TIMEOUT`）、読めない出力（`CUE_FAILED`）では止まる（exit 5）。
- **RQ-12 持っていない型の版**：`schema` が `specdock/v<番号>` の形で、SpecDock がその版を持っていないとき、持っている版を示し、SpecDock を上げるよう示して止まる（`CUE_SCHEMA_UNSUPPORTED`、exit 3）。形の違う値、またはないときは、`schema` の形の誤り（`CUE_INVALID`）にする。

### `work finish`（R-B7）

- **RQ-13 閉じる前の検査**：`work finish` は、閉じる Scope が CUE の Scope なら、GitHub の状態を読み直した後、保存の確かめ、カタログの変更、GitHub への書き込みの前に、`scope check` と同じ検査をする。誤りがあれば、何も書かずに止まり（`SCOPE_CHECK_FAILED`、exit 3）、誤りの一覧と、直した後に実行するコマンドを示す。警告は、結果の警告として示し、止めない。
- **RQ-14 検査しない場合**：Markdown の Scope、ディレクトリがない Scope では、検査しない（今と同じに動く）。子孫は検査し直さない。
- **RQ-15 既に閉じた Scope**：GitHub で既に完了の Scope の `work finish`（選択を外すだけ）では、検査の誤りで止めず、同じ一覧を警告（`SCOPE_CHECK_FAILED`）として示し、選択を外す。
- **RQ-16 dry-run**：`--dry-run` でも同じ検査をし、誤りがあれば同じに止まる。
- **RQ-17 道具の失敗**：CUE の Scope で `cue` がない・古い・時間切れなどのときは、`scope check` と同じコードで、何も書かずに止まる。既に閉じた Scope では、止めずに警告にする。

### `scope show`（R-C6）

- **RQ-18 保証レベル**：`scope show <ID> --json` は、`data.result.assurance` に `level`、`reason`、`source`、`problem` を返す。
  - `source: "cue"`：`requirement.cue` から、4つの値のどれかの `level` と、空白だけでない `reason` を読めた。
  - `source: "unset"`：CUE の Scope ではない（Markdown の Scope、ディレクトリがない）。`level` と `reason` は `null`。
  - `source: "unreadable"`：CUE の Scope だが読めない（`cue` がない・古い、文法の誤り、`assurance` がない、値が4つ以外、理由がない・空白だけ、`requirement.md` もある）。`level` と `reason` は `null`、`problem` に `{code, message}`。
  - `problem` は、`unreadable` のときだけ値を持ち、ほかは `null`。
- **RQ-19 読み方**：`requirement.cue` だけを読み、型を使わない。インターネットを使わない。読めなくても、`scope show` は失敗せず、ほかの情報を今までどおり返す。`scope list` は変えない。

### `workspace validate`・`doctor`（R-H2）

- **RQ-20 形式ごとの必須の文書**：Markdown の Scope は今の4つ（`requirement.md`、`design.md`、`plan.md`、`report.md`）、CUE の Scope は4つ（`requirement.cue`、`design.cue`、`plan.cue`、`report.md`）を求める。形式は `requirement.cue` があるかで決める。両方があれば `SCOPE_FORMAT_CONFLICT` の誤りにする。`explanation.html` は判定しない。`cue` を呼ばない（`cue` がなくても動く）。

### schema 3 のリポジトリ

- **RQ-21 schema 3**：`spec-dock/workspace.json` の `schema_version` が 3 のリポジトリでは、`scope check` は、ほかの canonical のコマンドと同じく `CANONICAL_NOT_MIGRATED` で止まる。schema 3 の `work finish`、`scope show`、`workspace validate`・`doctor` は変えない。

### 既存のものを壊さない（AC-12 の一部）

- **RQ-22 回帰**：今の回帰のテストを変えずに通す。今の `spec-dock/templates/<種類>/` の `.md` の雛形、型 `src/spec_dock/cue/v1/` は変えない。

## スコープ

### 対象

- `cue` を呼ぶ部品（`runtime/infra/`）、検査の部品と `scope check` の処理（`runtime/application/`）、説明資料の形の判定（`runtime/domain/`）。
- `runtime/cli/catalog.py` の `scope check` の葉、ヘルプ、`canonical_dispatch.py` と `runtime_dispatch.py` の振り分け、テキストの出力。
- `canonical_work.py`（`work finish` の検査）、`canonical_scope_read.py`（`scope show` の `assurance`）、`canonical_workspace.py`（形式ごとの必須の文書）。
- 上のテスト（`tests/unit/`、`tests/cli_runtime/`）。CLI の葉の一覧を固定している既存のテストの期待の更新（新しい葉を足すため）。

### 対象外

- 型（`src/spec_dock/cue/v1/`）の変更（I-1 の持ち物。不具合を見つけたら統括に知らせる）。
- `scope create`・`scope import github` の `--assurance`、配布資産の雛形 `templates/cue/`、dogfood の写し（I-3）。
- 説明資料の雛形とデザインシステムの変更（I-4）、CUE の描画と `scope render`（I-5）、ガイドとスキル（I-6）、spec-dock での導入（I-7）。
- `scope list` の保証レベル。
- slices のキーが GitHub の本当の子かの照合（I-2 では行わない。2026-10-31 統括決定 Q5）。
- 説明資料のブラウザーでの描画の検査（I-4 の手元の手順）。
- 利用者の環境への `cue` の導入。

### 親の契約として守る境界

- K1 の評価の単位（ファイルの並べ方、`-t kind`、`schema` による版の選択）。
- K2 の `findings` の形と規則の名前（読むだけ）。
- K5 の「薄い説明資料の形」と雛形の印。
- K6 の版の置き場とリポジトリの型の置き場。
- 今の CLI の共通の契約（`specdock.cli/v2` の封筒、終了の状態、読むコマンドは書かない、canonical モードの規則）。

## 失敗・境界条件

- **`cue` がない、古い、版が読めない**：`scope check` と、CUE の Scope の `work finish` は、入れ方を示して止まる（exit 3）。`scope show` は `assurance.source = "unreadable"`。Markdown の Scope の操作と、`workspace validate`・`doctor` は、`cue` がなくても動く。
- **`cue` が時間切れ、または読めない出力**：`scope check` と `work finish` は止まる（exit 5）。`scope show` は `unreadable`。
- **CUE の文法の誤り**：`scope check` は、ファイルと位置を示す誤り。`scope show` は `unreadable`。`work finish` は止まる。
- **保証レベルがない、4つ以外、理由が空白だけ**：`scope check` は誤り（型の形の誤り、または `ASSURANCE_UNREADABLE`）。`scope show` は `unreadable`。
- **保証レベルを `requirement.cue` 以外に書いた**：`scope check` は `ASSURANCE_UNREADABLE` の誤り。`scope show` は `unreadable`。
- **`schema` がない、形が違う**：`scope check` は `schema` の形の誤り。
- **持っていない型の版**：`scope check` と `work finish` は、SpecDock を上げるよう示して止まる。
- **リポジトリの型の誤り**：`scope check` は、リポジトリの型のファイルの位置を示す誤り。
- **`requirement.md` と `requirement.cue` の両方**：`scope check` と `workspace validate`・`doctor` は誤り。`work finish` は止まる。`scope show` は `unreadable`。
- **CUE の Scope で `design.cue` か `plan.cue` がない**：`scope check` は誤り（`SCOPE_DOCUMENT_MISSING`）。`workspace validate` も文書の欠落の誤り。
- **説明資料がない、雛形のまま**：Epic では誤り、Initiative と Issue では警告。形を壊していれば、どの種類でも誤り。
- **インターネットがない**：`scope check` と `scope show` は、手元の GitHub の構造の写し（古ければ警告 `GITHUB_SNAPSHOT_STALE`）と、カタログだけで動く。`--offline` でも動く。
- **`work finish` で検査が誤り**：何も書かずに止まる。直してから、もう一度 `work finish` を実行する。既に閉じた Scope では、止めずに警告にする。
- **Scope のディレクトリがない**：`scope check` は `LOCAL_TARGET_NOT_FOUND`（exit 4）。`work finish` は検査しない（今のとおり保存して閉じる）。`scope show` は `unset`。

## 受け入れ条件

各 AC の後ろの括弧は、満たす Epic の AC と、この文書の要件の番号。

- **AC-01（Epic AC-02、RQ-18、RQ-19）**：`scope show <ID> --json` が、CUE の Scope では `assurance` に `requirement.cue` の値と理由と `source: "cue"` を返し、Markdown の Scope では `level: null`、`reason: null`、`source: "unset"`、`problem: null` を返す。文法の誤り、`assurance` がない、4つ以外の値、空白だけの理由、`requirement.md` もある、`cue` がない、のそれぞれで `source: "unreadable"` と `problem.code` を返し、コマンドは成功する。`--offline` と、偽の `gh` が GitHub に届かない状態で、同じ結果になる。
- **AC-02（Epic AC-05、RQ-01、RQ-04〜RQ-06、RQ-09）**：`scope check <ID> --json` が、誤りのない CUE の Scope で exit 0、`valid: true`、空の `errors` を返す。形の誤りのある Scope で exit 7、`CUE_INVALID` の各項目に、ファイル（チェックアウトからの道筋。Scope のファイルは `spec-dock/initiatives/<区切り>/<ID>/<名前>`、リポジトリの型は `spec-dock/cue/<名前>`）、行、列、項目の道筋、直し方を返す。つながりの指摘のある Scope で、`SPEC_FINDINGS` の各項目に、規則、番号、ファイル、文、直し方を返す。テキストの出力も、1件ずつ、コード、ファイル、直し方を示す。インターネットなし（`--offline`、偽の `gh` が届かない）でも同じ結果になる。カタログとチェックアウトのファイルが、実行の前後で変わらない。
- **AC-03（Epic AC-07、RQ-04）**：I-1 の見本（`tests/fixtures/cue/v1/samples/`）を CUE の Scope として置き、`scope check` で検査した結果（誤りの項目の道筋、出た規則）が、見本の `expected.json` と一致する。
- **AC-04（Epic AC-08、RQ-04）**：チェックアウトの `spec-dock/cue/*.cue` に置いたリポジトリの型の制約と規則が、`scope check` の結果に加わる。リポジトリの型の誤りは、そのファイルの位置を示す。
- **AC-05（Epic AC-04 の検査のコマンドでの確かめ、RQ-04）**：standard で通る Scope の `assurance.level` を strict に書き換えると、`scope check` が strict で必須の項目の誤りを示し、項目を書き足すと通る。
- **AC-06（RQ-07、RQ-12）**：保証レベルを `design.cue` に書いた Scope が `ASSURANCE_UNREADABLE` の誤りになる。`schema` がない Scope が `schema` の `CUE_INVALID` になる。`schema: "specdock/v9"` の Scope で、`CUE_SCHEMA_UNSUPPORTED` で止まり、持っている版を示す。
- **AC-07（RQ-10、RQ-11、RQ-17）**：偽の `cue` で、ない・古い・版が読めない・時間切れ・読めない出力の各場合に、`scope check` が決まったコード（`CUE_NOT_FOUND`、`CUE_VERSION_UNSUPPORTED`、`CUE_TIMEOUT`、`CUE_FAILED`）と入れ方・次の手順を示して止まり、何も書かない。`cue` を呼ぶ引数が、シェルを通らない並びで、K1 の順番になっている。
- **AC-08（RQ-02、RQ-03）**：Markdown の Scope の `scope check` が、`cue` が PATH になくても、exit 0、`format: "markdown"`、`checked: false` を返す。`requirement.md` と `requirement.cue` の両方がある Scope で、`SCOPE_FORMAT_CONFLICT` の誤りになる。
- **AC-09（Epic AC-16、RQ-13、RQ-16）**：CUE の Scope で、検査に誤りが残っていると、`work finish` が `SCOPE_CHECK_FAILED`（exit 3）で止まり、誤りの一覧と次の手順を示し、カタログの変更集、GitHub への書き込み、選択の解除を何もしない。`--dry-run` でも同じに止まる。誤りを直すと、`work finish` が閉じて選択を外す。説明資料の警告（Issue の雛形のまま）だけなら、警告を示して閉じる。
- **AC-10（Epic AC-16 の後半、AC-12、RQ-14、RQ-22）**：Markdown の Scope の `work finish` が、`cue` が PATH になくても、今と同じに閉じる。既存の `work finish` の回帰のテスト（`tests/cli_runtime/test_issue432_work_finish.py` ほか）が、変えずに通る。
- **AC-11（RQ-15、RQ-17）**：GitHub で既に完了の CUE の Scope に、誤りが残っている、または `cue` がないとき、`work finish` が止まらず、`SCOPE_CHECK_FAILED` などの警告を示して、選択を外す。
- **AC-12（Epic AC-12 の後半、RQ-20）**：Markdown の Scope と CUE の Scope が並ぶカタログで、`workspace validate` と `workspace doctor` が、CUE の Scope を文書の欠落の誤りにしない。CUE の Scope で `plan.cue` がなければ `SCOPE_DOCUMENT_MISSING`（`missing` に `plan.cue`）になる。両方の `requirement` がある Scope は `SCOPE_FORMAT_CONFLICT` になる。どちらも、`cue` が PATH になくても動く。
- **AC-13（Epic AC-17、RQ-08）**：説明資料がない、雛形のまま（印が残る）、の2つが、Epic では誤り、Initiative と Issue では警告になる。Markdown を書く場所がない、2つある、前付けに `title` がない、デザインシステムの CSS を読む指定がない、JS を読む指定がない、のそれぞれが、どの種類でも `EXPLANATION_INVALID` の誤りになる。I-4 の雛形 `spec-dock/design-system/explanation-skeleton.html` は「雛形のまま」だけになり、印を消すと何も出ない。
- **AC-14（RQ-21）**：schema 3 のリポジトリで、`scope check` が `CANONICAL_NOT_MIGRATED` で止まる。
- **AC-15（RQ-01）**：`spec-dock help scope check` と `spec-dock scope check --help` が、読むだけのコマンドであること、`--json` の結果の形、終了の状態を示す。completion に `scope check` が出る。
- **AC-16（Epic AC-15）**：`make lint` と `uv run pytest` が通る。既存のテストの変更は、新しい葉の追加に伴う、CLI の葉の一覧の期待の更新だけである。`src/spec_dock/cue/`、`spec-dock/templates/<種類>/`、`src/spec_dock/assets/spec_dock/templates/` は変えない。

## 制約・前提

- Linux と macOS、Python 3.10 以上。
- テストと手元の確かめの `cue` は v0.17.1。この worktree の無視される場所（`.workbench/bin/`）に入れ、利用者の環境には入れない。
- テストは外のネットワークを使わない。GitHub は偽の `gh` で置き換える。`cue` の失敗は偽の `cue` で起こす。
- 本物の GitHub に試しの Issue を作らない。本物のカタログに CUE の Scope を作らない。
- Epic の目的、Issue の分け方、契約 K1〜K6 は変えない。
- 文書の正本は、この Scope の Markdown（Epic の `requirement.md` の対象外）。

## 合意済みの判断

2026-10-31 に、統括が確かめた（詳細と理由は `design.md` の「決めたこと」）。

- Q1 `cue` の最低の版は v0.17.1。
- Q2 誤りのコードと終了の状態（RQ-05〜RQ-13 のとおり）。
- Q3 `scope show` の `assurance` の形（RQ-18）。`scope list` には足さない。
- Q4 `schema` と `assurance` は `requirement.cue` だけから読み、読めなければ誤り（RQ-07）。
- Q5 slices のキーが本当の子かは、I-2 では調べない。
- Q6 schema 3 の `scope check` は `CANONICAL_NOT_MIGRATED`（RQ-21）。
- Q7 `work finish` の検査（RQ-13〜RQ-17）。既に閉じた Scope では止めずに警告（統括の変更）。
- Q8 リポジトリの型は、チェックアウトの作業ツリーの `spec-dock/cue/*.cue` を読む。

## 未解決事項

ない。
