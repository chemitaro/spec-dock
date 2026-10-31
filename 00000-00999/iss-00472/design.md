---
種別: 設計書（Issue）
ID: "iss-00472"
タイトル: "Define CUE Spec Schema V1"
関連GitHub: ["#472"]
状態: "draft"
最終更新: "2026-10-31"
依存: ["requirement.md"]
親: ["epic-00425", "init-00423"]
---

# iss-00472 Define CUE Spec Schema V1 — 設計

詳細: [Design Guide](../../../docs/authoring/design.md)

## 設計目標

- Epic の契約 K1、K2、K6 の骨組みの上に、型 `specdock/v1` の具体の項目と規則を作る。
- 必須の項目は最小にし、項目を足す余地を残す。必須を増やすのは、保証レベルの表の行だけにする。
- 形の誤り（`cue` の評価の誤り）と、つながりの指摘（`findings`）を分ける。形の誤りの文は、問題の項目の道筋を名指しし、原因を隠す誤り（循環など）を出さない。
- 雛形は、置き換えの印に値を入れれば、どのレベルでも誤りも指摘もなく通る。指摘は、中身を書き始めてから出る。

## Current / Target

| | 今 | この Issue の後 |
|---|---|---|
| 型 | ない（統括の試作だけ） | パッケージの `spec_dock/cue/v1/*.cue`（`package spec`）。wheel に入る |
| 版の選び方 | ない | `runtime/infra/cue_schemas.py` が、`"specdock/v1"` から `cue/v1/` を返す |
| 雛形の CUE | ない | 3つの種類の `requirement.cue`、`design.cue`、`plan.cue` の中身（置き場は「変更対象」） |
| CI の `cue` | ない | `provider-tests` が、v0.17.1 を checksum で確かめて入れる |
| 型のテスト | ない | 実際の `cue` で評価するテスト。`cue` がなければ失敗 |

## 責務・Interface

### 1. 評価の単位（K1 の具体化）

```text
cue export --out json -t kind=<initiative|epic|issue> \
  <パッケージ>/cue/v1/*.cue \
  [<リポジトリ>/spec-dock/cue/*.cue] \
  <Scope>/requirement.cue <Scope>/design.cue <Scope>/plan.cue
```

- `cue` 0.17.1 の `export` に `-c` はない（`unknown shorthand flag: 'c'`、2026-10-31 に確認）。`export` は、もともと具体的な値だけを出し、具体的でなければ失敗するので、`-c` なしで K1 の意図どおりになる。統括が、Epic の `design.md` の K1 を直した（「決めたこと」の Q1）。
- この Issue は、製品の中で `cue` を呼ぶ部品を作らない（I-2）。テストは、上のとおりに `cue` を呼ぶテスト用の補助（`tests/support/cue.py`）を使う。
- 型のファイルの名前は、Scope のファイルの名前と重ならないようにする（誤りの文の位置で見分けやすくするため）。

### 2. 版の置き場（K6 の具体化）

- `src/spec_dock/cue/v1/` に、次の5つを置く。
  - `base.cue`：`schema`、`kind`、`assurance`、`_rank`、共通の定義（`#Text`、`#Title`）、`findings` の形、版の固定の決まりを書いた冒頭の注。
  - `requirement_type.cue`：要件の文書の項目。
  - `design_type.cue`：設計の文書の項目。
  - `plan_type.cue`：計画の文書の項目、種類ごとの違い、`execution`。
  - `rules.cue`：つながりの規則（`findings`）。
- `src/spec_dock/runtime/infra/cue_schemas.py`（パッケージの資源を読む部品。`static_assets.py` と同じ層）：
  - `schema_directory(schema: object) -> Path | None`：値が `^specdock/v[1-9][0-9]*$` に合い、パッケージにそのディレクトリがあれば、そのディレクトリを返す。ほかは `None`。
  - `shipped_schemas() -> tuple[str, ...]`：パッケージが持つ版の名前を、版の番号の順に返す（I-2 の「SpecDock を上げる」の案内に使う）。
- `pyproject.toml` の `[tool.setuptools.package-data]` に `"cue/**/*.cue"` を足す。`setup.py` は、パッケージのデータを `pyproject.toml` から読むので変えない（新しく作る wheel と、sdist から作る wheel で確かめる）。
- 版の固定：v1 の見本の評価の結果を、この Issue のテストで固定する（AC-07）。版を出す（I-6 で版を上げる）までに v1 を直すときは、期待の結果を、理由と一緒に変える。出した後は、互換を壊さない足し方だけにし、互換を壊す変更は `cue/v2/` にする（K6）。

### 3. 型の項目の一覧（K2 の具体化）

表の「必須」は、どのレベルでも必須のもの。レベルで変わるものは、次の節の表にある。型にない項目は、どこにでも足せる（各項目の構造と、トップレベルは開いている）。ただし、番号をキーにする構造（`requirements` など）は、番号の形のキーだけを受ける（閉じている）。

共通の定義：

- `#Text`：空白だけでない文字列。Markdown を書いてよい（描画で Markdown として描く。K5）。空白は Python の `str.isspace()` と同じ範囲（全角の空白 U+3000、NBSP などの Unicode の区切りも空白）。RE2 の `\S` は ASCII の空白しか除かないので、`[^\s\p{Z}\x{0B}\x{1C}-\x{1F}\x{85}]` を使う（コードのレビューの指摘。2026-10-31）。
- `#Title`：空白だけでない、1行の文字列（改行を含まない）。空白の範囲は `#Text` と同じ。
- 番号の形：`R-` `F-` `D-` `S-` `T-` の後に2桁以上の数字（`R-01`、`R-123`）。切り分けのキーは `^(epic|iss)-[0-9]{5,}$`（K2）。
- 参照（`satisfies`、`realizes`、`verifies`、`covers`、`after`、`session`）は、ただの文字列で受け、先があるかは `findings` で調べる（K2）。

#### 共通（`base.cue`。値は `requirement.cue` に書く）

| 項目 | 型 | 必須か | 説明 |
|---|---|---|---|
| `schema` | `"specdock/v1"` | 必須 | 型の版。`requirement.cue` に書く（K1） |
| `kind` | `"initiative"` \| `"epic"` \| `"issue"` | タグ | SpecDock が `-t kind=` で渡す。文書に書かない |
| `assurance.level` | `light` \| `standard` \| `strict` \| `critical` | 必須 | 保証レベル（R-C1）。誤りの文を1行にするため、選択肢ではなく正規表現で受ける（受ける値は K2 と同じ） |
| `assurance.reason` | `#Text` | 必須 | レベルを選んだ理由 |
| `_rank` | 0〜3（隠した項目） | 計算 | light=0、standard=1、strict=2、critical=3。`level` が読めないときは 0 にし、`level` の誤りの文だけが出るようにする（下の「data / failure」） |
| `findings` | `{[規則]: [...{id, message, hint?}]}` | 計算 | K2 の形。SpecDock の規則は、`hint` を必ず持つ |

#### 要件（`requirement.cue`）

| 項目 | 型 | 必須か | 説明 |
|---|---|---|---|
| `purpose` | `#Text` | 任意 | 目的 |
| `background` | `#Text` | 任意 | 背景 |
| `includes`、`excludes` | `[...#Text]` | 任意 | 対象、対象外 |
| `requirements` | `{[R-番号]: 要件}` | （空でよい） | 観測できる要件 |
| 要件の `title` | `#Title` | 必須 | 要件の一文 |
| 要件の `text` | `#Text` | 任意 | 詳しい説明 |
| 要件の `acceptance` | `[...#Text]` | レベルの表 | 受け入れの条件（観測できる形） |
| `failures` | `{[F-番号]: 失敗の条件}` | （空でよい） | 失敗・境界の条件（R-B3 の「失敗の条件」） |
| 失敗の条件の `title` | `#Title` | 必須 | 条件と、そのときの振る舞いの一文 |
| 失敗の条件の `text` | `#Text` | 任意 | 詳しい説明 |
| 失敗の条件の `impact` | `#Text` | レベルの表 | 起きたときの影響 |
| 失敗の条件の `recovery` | `#Text` | レベルの表 | 回復のしかた |
| `constraints` | `[...#Text]` | 任意 | 制約・前提 |
| `decisions` | `[...#Text]` | 任意 | 合意した判断 |
| `questions` | `[...#Text]` | 任意 | 未解決事項 |

#### 設計（`design.cue`）

| 項目 | 型 | 必須か | 説明 |
|---|---|---|---|
| `goals` | `[...#Text]` | 任意 | 設計目標 |
| `current`、`target` | `#Text` | 任意 | 今と、この Scope の後 |
| `design` | `{[D-番号]: 設計}` | （空でよい） | 責務、interface、data などの単位 |
| 設計の `title` | `#Title` | 必須 | 設計の一文 |
| 設計の `text` | `#Text` | 任意 | 詳しい説明 |
| 設計の `satisfies` | `[...string]` | 必須（空の並びでよい） | 満たす要件・失敗の条件の番号（K2） |
| `compatibility` | `#Text` | 任意 | 移行、互換性 |
| `risks` | `[...#Text]` | 任意 | リスク |

#### 計画（`plan.cue`）

| 項目 | 型 | 必須か | 種類 | 説明 |
|---|---|---|---|---|
| `goal` | `#Text` | 任意 | すべて | 目標 |
| `steps` | `{[S-番号]: 手順}` | （空でよい） | Issue だけ | 実装の手順（作業の台帳。R-D1） |
| 手順の `title` | `#Title` | 必須 | | 手順の一文 |
| 手順の `text` | `#Text` | 任意 | | 詳しい説明 |
| 手順の `realizes` | `[...string]` | 必須（空の並びでよい） | | 満たす要件・失敗の条件の番号（K2） |
| 手順の `status` | `todo` \| `doing` \| `done` \| `dropped` | 既定 `todo` | | 状態（K2） |
| 手順の `after` | `[...string]` | 任意 | | 先に済ませる手順の番号（K2）。並びは番号の順 |
| 手順の `session` | `string` | 任意 | | 行うセッションの名前（R-D3） |
| `tests` | `{[T-番号]: テスト}` | （空でよい） | Issue だけ | テスト |
| テストの `title` | `#Title` | 必須 | | 何を確かめるかの一文 |
| テストの `text` | `#Text` | 任意 | | 確かめ方 |
| テストの `verifies` | `[...string]` | 必須（空の並びでよい） | | 確かめる要件・失敗の条件の番号（K2） |
| `slices` | `{[子の ID]: 切り分け}` | （空でよい） | Epic、Initiative だけ | 子の Scope への切り分け（K2）。子の保証レベルは書かない（R-C4） |
| 切り分けの `covers` | `[...string]` | 必須（空の並びでよい） | | 子に任せる要件・失敗の条件の番号（K2） |
| 切り分けの `text` | `#Text` | 任意 | | 子に任せることの説明（題名は GitHub が正本なので持たない） |
| 切り分けの `after` | `[...string]` | 任意 | | 先に済ませる切り分け（子の ID） |
| 切り分けの `session` | `string` | 任意 | | 行うセッションの名前 |
| `verification` | `#Text` | 任意 | すべて | 検証のしかた |
| `rollback` | `#Text` | レベルの表 | すべて | 戻し方 |
| `exit` | `#Text` | 任意 | すべて | 終わりの条件、引き渡し |
| `execution` | 下の表 | 任意 | すべて | 実行の割り当て（R-D3） |

`execution`（R-D3、R-D4。値の意味は持たない）：

| 項目 | 型 | 必須か | 説明 |
|---|---|---|---|
| `execution.sessions.<名前>.task` | `#Text` | 任意 | 何をするか |
| `execution.sessions.<名前>.model` | `string`（どんな文字列でもよい） | 任意 | モデル |
| `execution.sessions.<名前>.effort` | `string`（どんな文字列でもよい） | 任意 | 推論 |
| `execution.sessions.<名前>.rationale` | `#Text` | 任意 | 選んだ根拠 |
| `execution.reviews.<名前>.role` | `string` | 任意 | 役割 |
| `execution.reviews.<名前>.after` | `string` | 任意 | どの手順（Epic と Initiative では切り分け）の後か（K2） |
| `execution.reviews.<名前>.model`、`.effort` | `string`（どんな文字列でもよい） | 任意 | モデル、推論 |

種類ごとの違い（RQ-06）：Epic と Initiative の `steps` と `tests`、Issue の `slices` に項目を書くと、`error()` で直し方を示す形の誤りになる（例「Epic と Initiative の plan.cue には steps を書かない。子の Scope への切り分けは slices に書く」）。構造そのものは、どの種類でも空の構造として出る（読む側が、ないことを気にしなくてよいように）。

### 4. 保証レベルごとの必須の項目（R-B2）

形の誤りとして求める項目。上の一覧の「必須」は、どのレベルでも必須で、ここには再掲しない。

| 項目 | light | standard | strict | critical |
|---|---|---|---|---|
| 要件の `acceptance`（1つ以上） | 任意 | 必須 | 必須 | 必須 |
| 失敗の条件の `impact` | 任意 | 任意 | 必須 | 必須 |
| 失敗の条件の `recovery` | 任意 | 任意 | 必須 | 必須 |
| 計画の `rollback` | 任意 | 任意 | 任意 | 必須（形の誤りではなく、`findings` の `rollback-missing`。手順か切り分けが1つ以上あるとき） |

- 理由：standard の完成基準は「acceptance と主要な error path を確認できる」、strict は「失敗時の影響、forward recovery が説明されている」（`docs/authoring/issue-plan-levels/`）。どちらも、番号の項目に付けるので、空の雛形は、どのレベルでも通る（RQ-14）。
- critical の追加は、K2 の `rollback-missing` だけにする（最小から始める。I-7 で足りなければ、互換を壊さない足し方か、v2 で足す）。

### 5. つながりの規則（K2 の規則の表の具体化）

作業の単位を、Issue では手順（`steps`）、Epic と Initiative では切り分け（`slices`）とする。手順の「生きている」ものは、`status` が `dropped` 以外のもの。参照の先の集まりは、要件と失敗の条件の番号（R と F）。

| 規則 | 段階 | Issue | Epic、Initiative |
|---|---|---|---|
| `unknown-reference` | 0 | `design.*.satisfies`、`steps.*.realizes`、`tests.*.verifies` が R と F にない。`steps.*.after` が手順にない | `design.*.satisfies`、`slices.*.covers` が R と F にない。`slices.*.after` が切り分けにない |
| `requirement-without-step` | 0 | 要件が、生きている手順の `realizes` にない | 要件が、どの `covers` にもない |
| `requirement-without-design` | 1 | 要件が、どの `satisfies` にもない | 同じ |
| `requirement-without-test` | 1 | 要件が、どの `verifies` にもない | 要件が、どの `covers` にもない |
| `orphan-step` | 2 | 生きている手順の `realizes` が空 | 切り分けの `covers` が空 |
| `failure-without-test` | 2 | 失敗の条件が、どの `verifies` にもない | 失敗の条件が、どの `covers` にもない |
| `rollback-missing` | 3 | 手順が1つ以上あり、`rollback` がない | 切り分けが1つ以上あり、`rollback` がない |
| `execution-reference` | 0 | 手順の `session` が `execution.sessions` にない。レビューの `after` が手順にない | 切り分けの `session` が `execution.sessions` にない。レビューの `after` が切り分けにない |

- 出す段階以上のレベルでは、規則の一覧が、違反がなくても空の並びとして出る（どの規則で調べたかが分かる）。段階より低いレベルでは、その規則の名前が出ない。`execution-reference` は、`execution` があるか、`session` を書いた作業の単位があるときに出る（「決めたこと」の Q4）。
- Epic と Initiative で要件がどの `covers` にもないと、`requirement-without-step`（段階0）と `requirement-without-test`（段階1）の両方に出る（R-B3 の注の読み替えのとおり）。
- 取り下げた手順（`dropped`）は、要件を満たすものとして数えず、`orphan-step` の対象にもしない。参照（`realizes`、`after`、`session`）は、取り下げた手順も調べる（「決めたこと」の Q3）。
- 指摘の形（RQ-11）：
  - `id`：問題のある項目の番号（`R-01`、`F-01`、`D-01`、`S-01`、`T-01`、子の ID）。レビューは `execution.reviews.<名前>`、`rollback-missing` は `rollback`。番号の頭で、どのファイルの項目かが分かる（R、F は `requirement.cue`、D は `design.cue`、ほかは `plan.cue`）。
  - `message`：何が問題か。参照の先と、項目の道筋を含める（例「design."D-01".satisfies の "R-09" は、requirements と failures にない番号です」）。
  - `hint`：直すファイルと項目（例「requirement.cue に "R-09" を足すか、design.cue の design."D-01".satisfies から外す」）。
  - 文は日本語にする（「決めたこと」の Q6）。
  - 一覧は `id` の順に並べる（同じ入力から同じ結果。I-5 の決まった並びの助けにもなる）。

### 6. リポジトリの型（K6、R-B6）

- リポジトリの型は、`package spec` の `.cue` で、SpecDock の型のファイルと Scope のファイルの間に並べる（K1）。
- 使ってよいもの：公開の項目（上の一覧）と `_rank`（読むだけ。書くと、`assurance.level` と違う値は誤りになる）。トップレベルの `if _rank >= <段階> {...}` も使える（`_rank` が読めないときの既定 0 のため、循環の誤りにならない）。規則を足すときは、`findings: "<名前>": [...]` に足す。名前は、SpecDock の規則と重ねない（重ねると、一覧が衝突して評価が誤りになる）。
- SpecDock の型の中の計算に使う隠した項目は、`_specdock` の下にまとめる。リポジトリの型は、これを使わない（版の中で、名前を変えることがある）。

### 7. 雛形の中身（K4 の中身）

- 3つの種類ごとに、`requirement.cue`、`design.cue`、`plan.cue` を作る。中身：
  - `package spec`、型の版（`requirement.cue` だけに `schema: "specdock/v1"`）。
  - `assurance: {level: "{{ASSURANCE_LEVEL}}", reason: "{{ASSURANCE_REASON}}"}`（`requirement.cue`）。印は、CUE の二重引用符の文字列の中に置く。置き換える側（I-3）は、理由を、二重引用符の文字列の中身の書き方に変えてから入れる（`\` を `\\`、`"` を `\"`、改行を `\n`、ほかの制御文字を `\u` の形に）。`\(`（CUE の文字列の埋め込み）も、`\` を変えることで、文字のまま入る。
  - 番号の構造（`requirements: {}` など）と、書き方の例の注（書き換える項目と、レベルで必須になる項目）。例は注にして、値を置かない（値を置くと、雛形のままで指摘が出るため）。
- 置き場は、テストの見本の置き場 `tests/fixtures/cue/v1/templates/<種類>/`（「決めたこと」の Q2）。I-3 が配布資産 `templates/cue/<種類>/` に移す。

## data / failure

- この Issue は、ファイルを書く製品の処理を作らない。型は、評価の入力を読むだけである。
- 保証レベルが読めないとき：`_rank: *{light: 0, ...}[assurance.level] | 0`。既定の 0 がないと、トップレベルの `if _rank >= ...` が「cycle with field: _rank」という誤りの文を出し、`level` がないことを隠す（2026-10-31 に、`cue` 0.17.1 で確かめた）。既定があっても、`level` がない・値が違うことは、`assurance.level` の誤りとして評価を失敗させる。
- `_rank` の書き換えを防ぐ：既定の選択肢があると、文書が `_rank: 0` と書けば 0 が選ばれ、レベルを変えずに検査が弱まる。隠した照合の項目 `_specdock: rank: {light: 0, ...}[assurance.level] & _rank` を置き、`level` と違う値は衝突の誤りにする（`level` が読めないときは、この項目は具体的にならず、ほかの誤りの文を増やさない。2026-10-31 に確かめた）。
- 状態の値の誤り：`status: *"todo" | (string & =~"^(todo|doing|done|dropped)$")` で、誤りの文を2行にする（選択肢で書くと4行）。
- 種類のタグがないとき：種類で切り替える条件は、`kind` を直接読まず、`_specdock: issue: *(kind == "issue") | true` を読む。タグがないと、比べた結果が読めないので既定に落ち、トップレベルの `if` が循環や「unresolved disjunction」の誤りを出さず、`kind: incomplete value ...` の誤りだけが出る（2026-10-31 に確かめた）。3つ以外の値のときも、`kind` の衝突の誤りが出る（ほかの誤りが続くことはある）。
- 種類に合わない構造に書いたとき：規則の計算は、その種類の構造だけを読む（`_specdock.ownSteps`、`ownTests`、`ownSlices`。ほかの種類の構造は空として読む）。そのため、Epic に `steps` を書いた誤りは、`steps."S-01"` の1つの誤りの文だけになり、規則の計算から同じ誤りが重ねて出ない（2026-10-31 に確かめた）。
- リポジトリの型との衝突：CUE の衝突の誤りで、両方のファイルの位置が出る。
- `cue` がないとき（テスト）：`tests/support/cue.py` が、入れ方（`GOBIN="$PWD/.workbench/bin" go install cuelang.org/go/cmd/cue@v0.17.1` と PATH）を示して `pytest.fail` する。飛ばさない。

## 変更対象

- 足すもの：
  - `src/spec_dock/cue/v1/{base,requirement_type,design_type,plan_type,rules}.cue`
  - `src/spec_dock/runtime/infra/cue_schemas.py`
  - `pyproject.toml`（パッケージのデータ）
  - `.github/workflows/provider-ci.yml`（`provider-tests` のジョブに、`cue` の導入の手順を1つ）
  - 雛形の CUE（9つ。`tests/fixtures/cue/v1/templates/<種類>/`）
  - テスト：`tests/support/cue.py`（K1 の並べ方の評価、CUE の文字列の書き方、固定した版と checksum。ワークフローと同じ値を持つ）、`tests/unit/cue/`（共通の項目、形の誤り、レベル、規則と指摘の形、`execution`、項目を足せること、リポジトリの型、雛形、見本の固定、`cue` がないときの失敗）、`tests/unit/infra/test_cue_schemas.py`、`tests/integration/test_cue_schema_wheel.py`（ビルドの入力だけを一時ディレクトリに写してビルドする。手元の残りの `*.egg-info/SOURCES.txt` が、パッケージのデータの設定にないファイルを wheel に入れてしまうため）、`tests/integration/test_provider_ci_cue.py`、見本 `tests/fixtures/cue/v1/samples/<名前>/`（3つのファイルと `expected.json`）
- 変えないもの：既存のテストのファイル、`spec-dock/templates/<種類>/` の `.md` の雛形、`static-inventory.json`、dogfood の写し（`spec-dock/` の下。この Issue は配布資産を変えない）、ランタイムの既存のコマンド、`setup.py`。

## 移行・互換性・rollback

- 既存の Scope と CLI の動きは変わらない（新しいファイルを足すだけで、どこからも呼ばない。I-2 から使う）。
- wheel に `spec_dock/cue/` が増える。配布資産（利用者のリポジトリに写すもの）は増えない。
- CI の `provider-tests` が、`cue` の取得に GitHub の Releases を使う。取得できないと、テストのジョブが失敗する（偽の成功にしない）。
- 戻すときは、この PR を戻す。型を使う Scope は、I-7 まで本物のカタログにないので、移行は要らない。

## testability

| 受け入れ | 観測点と方法 |
|---|---|
| AC-01 | 種類ごとの「すべての規則を満たす見本」に、規則ごとの1つの違反を足し、4つのレベルで評価する。出た規則の名前の集まりと、空でない一覧の集まりを、表から計算した期待と比べる |
| AC-02 | standard で通る見本で、`level` を変えて評価し、誤りの文の項目の道筋を確かめる。項目を足して通ることを確かめる |
| AC-03 | `execution` の参照の誤りの見本と、さまざまな `model`・`effort` の値の見本 |
| AC-04 | テストの中で作るリポジトリの型（`_rank` の条件で `execution` を必須にし、規則を1つ足す） |
| AC-05 | 雛形の印を、テストの中の CUE の文字列の書き方に変える関数で置き換え、評価する。理由が、元の文字列のまま出ることも確かめる |
| AC-06 | 失敗・境界条件の見本ごとに、終了の状態、項目の道筋、`cycle` がないことを確かめる |
| AC-07 | `tests/fixtures/cue/v1/samples/<名前>/` の見本と、期待の結果 `expected.json` |
| AC-08 | `uv build` で wheel と sdist を作り、sdist から wheel を作り、中身を比べる。`cue_schemas` の関数のテスト |
| AC-09 | ワークフローの文面のテスト（手順の順番、版、2つの checksum、`sha256sum -c`、`GITHUB_PATH`）。PATH を空にして、補助が失敗することを確かめる |
| AC-11 | 各項目と、トップレベル、`assurance`、`execution` に、型にない項目を足した見本。番号の構造に形の違うキーを足した見本 |
| AC-12 | AC-01 の違反の見本で出たすべての指摘の `id`、`message`、`hint` と、`hint` のファイルの名前、一覧の並び |
| AC-10 | `make lint`、`uv run pytest`（PATH に `.workbench/bin` を足す）。`git diff --stat origin/main -- tests/` が、足したファイルだけであること |

## risk

- **型が硬すぎる・緩すぎる**：必須は表の行だけにし、項目を足せるようにした。I-7 の実際の Issue で直す。出した後は互換を壊せないので、I-6 までに I-2〜I-5 で使って見直す。
- **トップレベルが開いているので、項目の名前の書き間違い（`requirments`）を見つけない**：R-B1 の柔らかさを優先した。番号の構造は閉じているので、番号の書き間違いは見つける。I-7 で問題になれば、v2 で閉じるか、規則を足す。
- **`cue` の版の違いで、誤りの文が変わる**：テストは、誤りの文の全体ではなく、項目の道筋と、`cycle` がないことだけを確かめる。
- **作業の単位の順番の循環（`after` が輪になる）を見つけない**：CUE で推移的な閉包を計算すると重く、v1 では扱わない。描画（I-5）とダッシュボードは、輪があっても止まらないようにする（引き渡し）。
- **子の ID が、本当にその親の子かを調べない**：型は GitHub の構造を知らない。I-2 の検査で比べるかは I-2 で決める（引き渡し）。
- **`schema` と `assurance` を、`requirement.cue` 以外のファイルに書いても、型は気づかない**：CUE は、ファイルの区別なく1つにまとめるため。I-2 の `scope show` は `requirement.cue` だけを読むので、I-2 で、別のファイルにあれば知らせるかを決める（引き渡し）。

## 決めたこと

統括に確かめ、2026-10-31 に、すべて推奨のとおりに決まった（Q1、Q4 は、統括が Epic の `design.md` も直した）。

- **Q1（K1 の直し）**：`cue export -c` は 0.17.1 で失敗するので、K1 を `cue export --out json -t kind=<種類> ...` にした（`export` は、もともと具体的な値を求めるので、意味は同じ）。
- **Q2（雛形の置き場）**：I-1 の雛形の CUE は、テストの見本として `tests/fixtures/cue/v1/templates/<種類>/` に置く。I-3 が、配布資産の `src/spec_dock/assets/spec_dock/templates/cue/<種類>/` に移し、`static-inventory.json` と dogfood の写しも I-3 が足す（K4 の持ち主が配布資産を変える。一式がそろう前に、I-3 の「`templates/cue/<種類>/` がなければ止まる」の判定が満たされないように）。
- **Q3（取り下げた手順）**：`dropped` の手順は、要件を満たす手順として数えない。
- **Q4（`execution-reference` の出る条件）**：`execution` があるときに加えて、`execution` がなくても、`session` を書いた作業の単位があれば出す（書き忘れの見落としを防ぐ）。
- **Q5（種類ごとの違い）**：Epic と Initiative の `steps`・`tests`、Issue の `slices` は、直し方を示す形の誤りにする（読み替えの規則が、どちらを数えるかで迷わないため）。
- **Q6（指摘の文の言葉）**：`findings` の `message` と `hint` は日本語にする（仕様の文書とガイドに合わせる）。
- **Q7（`rollback-missing` の出る条件）**：手順か切り分けが1つ以上あるときだけ出す（作った直後の critical の Scope が、指摘なしで通る。I-3 の受け入れ「作った直後は説明資料の警告だけ」と合う）。
- **Q8（項目の一覧と、レベルの表）**：3と4の節のとおり。
