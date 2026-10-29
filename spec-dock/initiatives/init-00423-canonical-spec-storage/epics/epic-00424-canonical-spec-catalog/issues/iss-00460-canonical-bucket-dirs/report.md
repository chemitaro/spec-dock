---
種別: レポート（Issue）
ID: "iss-00460"
タイトル: "Bucket Canonical Catalog By Thousand"
関連GitHub: ["#460"]
最終更新: "2026-10-29"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00424", "init-00423"]
---

# Result Summary

詳細: [Report Guide](../../../../../../docs/authoring/report.md)

## Outcome

canonical のカタログの Scope のディレクトリを、番号の千ごとの区切りの下（`<カタログ>/<区切り>/<ID>/`。例 `00000-00999/iss-00454/`、`100000-100999/iss-100454/`）に置くようにした。区切りの計算は `domain/canonical_layout.py` の1か所にあり、カタログの読み取り、表示のパス、検査がそれを使う。正しい区切りの下にないものは、理由（`root`、`bucket`、`name`、`nested`）と正しい場所（`expected`）付きの `SCOPE_DIRECTORY_MISPLACED` になる。0埋めしない ID の入力（`iss-454`、`iss-000454`）は、すべての canonical の入口で `iss-00454` として通り、出力はいつも0埋めの形である（直す処理は今の共有の選択子の解析のまま。コードの変更はなく、テストで網羅を確かめた）。Epic の要件・設計・計画も、この決まりに直した。

### 実装したこと

- **区切りの計算（C3）**：`domain/canonical_layout.py` に `BUCKET_SIZE`（1000）、`BUCKET_NAME_SHAPE`、`SCOPE_TO_SPEC_DOCK`（`../../..`）、`scope_bucket(number)`、`scope_relative(scope_id)`、`is_bucket_name(name)` を足した。公開の形は `design.md` の「責務・Interface」のとおりで、I-15 向けに作業の初めに push した（`60ea01ccb`）。
- **カタログ**：`infra/catalog_tree.py` の `CatalogTree` が、正しい区切りの下の、区切りの合う `<ID>/` だけを Scope のディレクトリにする（`find` は `<catalog>/<区切り>/<ID>` を直接見て、区切りと ID の実際の名前の完全一致を確かめる）。`misplaced()` は、直下の ID の形の名前（`root`。I-14 の平らな `<ID>/` を含む）、区切りの名前の誤りと区切りの違う ID（`bucket`）、区切りの中の ID でない名前（`name`）、入れ子の残り（`nested`）を返し、名前が ID のものに `expected` を付ける。
- **読む側と検査**：`canonical_scopes.build_views` の `ScopeView.path` を `spec-dock/initiatives/<区切り>/<ID>` にした。`active set` のリンクの先（`../initiatives/<区切り>/<ID>`）と `artifact list/show` のパスは、これと `ScopeDirectory.relative` から作られるので、コードの変更なしに区切りの形になった。`canonical_workspace` の `SCOPE_DIRECTORY_MISSING` の `path`・文・次の1手と、`SCOPE_DIRECTORY_MISPLACED` の `details`（`expected` を足した）・理由ごとの文・次の1手を区切りの形にした。
- **入口の網羅**：`requirement.md` の R-460-04 に列挙した入口（対象、`--parent`、`--scope`、`--from`、`--expect-current`）のすべてに0埋めしない ID を渡すテストを足した。通らない入口はなかった。
- **Epic の文書**（統括の許可）：`requirement.md`（R-A3、R-E1、R-G7、AC-04、AC-09、合意済みの判断）、`design.md`（読み方、用語の「区切り」、Target、2章の表し方と内容の置き場、3章、6章、7章、10章、11章、12章、14章、変更対象、testability、「設計の判断」の最後の行）、`plan.md`（目標、一覧、図と説明、契約 C3 の注記、I-5、I-9、I-11、I-13、I-15 の記述、I-16 の節、rollback）。

### 変えたテスト（すべて canonical モードのもの。AC-460-08、Epic の AC-15）

版3の振る舞いを確かめるテストは1つも変えていない。

- テストの部品：`tests/support/canonical_scopes.py`（`CanonicalWorld.relative` が `<区切り>/<ID>` を返す。引数の形は変えていない）。
- 単体：`tests/unit/infra/test_catalog_tree.py`（区切りの形に書き直した）、`tests/unit/application/test_canonical_catalog.py`（`require_linked` の `tree` が区切りの下を返すこと）。
- CLI：`tests/cli_runtime/test_issue431_dependency_active.py`、`test_issue431_read_only.py`、`test_issue431_scope_read.py`、`test_issue431_workspace.py`、`test_issue455_flat_ids.py`（カタログのパスと期待するパスの値を区切りの形にしただけ。確かめる振る舞いは同じ）。
- 足したテスト：`tests/unit/domain/test_canonical_layout_buckets.py`、`tests/cli_runtime/test_issue460_bucket_dirs.py`。
- I-2、I-3、I-7 のテスト（`test_issue429_*`、`test_issue430_*`、`test_issue434_*`、`test_canonical_check.py`、`test_canonical_git.py`）の `init-00001-plan/` などのパスは、同期・リンク・検査が扱う任意のファイルのパスで、Scope の置き場の規則を確かめていないので、変えていない。

## Verification

### 受け入れ条件

| AC | 確かめたテスト | 結果 |
|---|---|---|
| AC-460-01 | `test_canonical_layout_buckets.py`（9つの例、0と負の数、種類によらないこと、`scope_relative` の例と ID でない値、`is_bucket_name` の12通り） | 通過 |
| AC-460-02 | `test_issue460_bucket_dirs.py`（`scope show/list` の `path`、`active set` のリンク、`artifact list` のパス、平らな残りを場所にしないこと）、直した `test_issue431_*` | 通過 |
| AC-460-03 | `test_catalog_tree.py`（4つの理由と `expected`、隠し・リンク・ファイルの無視、大文字）、`test_issue460_bucket_dirs.py`（`workspace validate` と `canonical status --structure` の外れ、`MISSING` の `path`、同じ区切りの中の付け替えが1件） | 通過 |
| AC-460-04 | `test_issue460_bucket_dirs.py`（読む入口23通りの parametrize と、`active set`、`active clear --from`、`branch create`、`branch switch`、`worktree create --expect-current`）。名前の照合（`00000-00999/iss-7/` は Scope のディレクトリでない）。`iss-000454` も同じ | 通過 |
| AC-460-05 | `test_canonical_layout_buckets.py`（`SCOPE_TO_SPEC_DOCK` の正規化）、`test_issue460_bucket_dirs.py`（mainのチェックアウトと作業用のworktreeで、Markdown のリンクとシンボリックリンクが `spec-dock/docs/…` を開く）。`git diff 95bbb7a1c..HEAD -- src/spec_dock/assets` は空（テンプレートは変えていない） | 通過 |
| AC-460-06 | Epic の3文書を「直下」「`<カタログ>/<ID>/`」「`initiatives/<ID>`」で検索した。残るのは、区切りそのものの説明（用語の「区切り」の行、R-A3 と合意済みの判断の理由、内容の置き場の `root` の説明）、移行前の置き場（11章の平らにする写しの元のパス）、`plan.md` の I-14 の節のマージの時点の記録（節の初めにそう書いた）、I-16 の節の受け入れの文だけである | 通過 |
| AC-460-07 | `test_canonical_layout_buckets.py`、`test_catalog_tree.py` が `design.md` の公開の形（`scope_bucket`、`scope_relative`、`is_bucket_name`、`SCOPE_TO_SPEC_DOCK`、`MisplacedDirectory.expected`）を直接使う | 通過 |
| AC-460-08 | 下の「最終品質ゲート」の `make lint` と `uv run pytest` の全体。変えたテストは上の一覧のとおりすべて canonical モードのもの | 通過 |

- 場所の組み立ての取り残し：`grep -rnE "/ ?(node|view|target|scope)\.id\b|/ ?scope_id\b|catalog ?/ ?f?\"" src/spec_dock/runtime/application/canonical_* src/spec_dock/runtime/infra/catalog_tree.py src/spec_dock/runtime/infra/canonical_* src/spec_dock/runtime/domain/canonical_*` の結果は、`catalog_tree.py` の `bucket / scope_id`（区切りを `scope_relative` から求めた後）と、`canonical_hold.py` の `.runtime/accepted.json` だけで、`<ID>` をカタログに直接つなぐ箇所は残っていない。
- 実装の途中の確かめ：canonical の範囲（`tests/cli_runtime/test_issue429*`〜`test_issue455*`、`tests/unit/application/test_canonical*`、`tests/unit/infra`、`tests/unit/domain`、`tests/integration/github`）で、テストを直した後に 1426 件が通った（直す前に走らせた回の12件の失敗は、どれも直したテストで、直した後に通った）。`make lint` は通った。

### 独立したレビュー

- 文書（統括の手順4。`061c1be04` の時点の文書）：この会話を知らない新しいサブエージェント1つ（opus/high）。P0/P1 は0件、P2 が5件、P3 が8件。`analyze-review-findings` で分析し、すべて根拠ありと判断した。直したこと：作り直しの次の1手の理由（新しい番号の区切りになる）、I-15 のマージを I-16 の後にすること（Epic の `plan.md`）、AC-460-04 の入口の列挙、I-5 への区切りのディレクトリの扱いの引き渡し（作る、シンボリックリンクかファイルなら止まる、空になったら消す）、C3 の持ち主の書き方、理由の数、区切りの名前の誤りにも合う次の1手の文、「最大1,000件」の限定、深さの確かめ方、検索の語、12章の参照先、R-A3 の見出し。依存の記録（I-15 と I-9 から I-16 へ）は、ほかの Issue のメタデータなので、統括に引き渡した（下）。
- 実装（`95bbb7a1c..7660bf4ae`）：`code-review` の Standards と Spec の新しいサブエージェント2つ（opus/high）。結果は契約の検証（`validate-review.py`）で有効、どちらも `pass`。Standards は指摘0件。Spec は P2 が1件（この `report.md` がまだ空で、AC-460-08 の変えたテストの一覧と引き渡しの記録がない）。この節と上の一覧を書いて直した。

### 最終品質ゲート（Claude だけのゲート。ChatGPT のゲートは利用者の設定で無効）

- **対象**：通常の push で GitHub に送った `e60f069f1f885fd1837e86b37e2e546a19433332`（`origin/main` = `95bbb7a1c` からの全差分 `origin/main...HEAD`）。作業ツリーはきれいな状態で固定した。
- **静的解析**：`make lint`（ruff check、ruff format --check、mypy）→ 終了コード0（3つとも pass）。
- **全体のテスト**：`uv run pytest -q -p no:cacheprovider` → 終了コード0、3057 passed、8 skipped（909秒）。実行の前後で HEAD が同じ SHA であることを確かめた。
- **独立したレビュー**：この作業に関わっていない新しいサブエージェント2つ（`code-review` の Standards と Spec、opus/high。範囲 `95bbb7a1c..e60f069f1`）。結果は契約の検証（`validate-review.py`）で有効、どちらも `pass`、P0/P1/P2 は0件。
  - Standards：指摘0件。
  - Spec：P3 が1件（この `report.md` の AC-460-04 の行が、入口の parametrize を「24通り」と書いていたが、実際は23通り）。止める指摘ではない。この節を書くコミットで23通りに直した。
- **結果**：合格。止める指摘がなく、lint と全体のテストが同じ SHA で通った。この節を書いたコミットは、ゲートの対象の上の、`report.md` だけの変更である。

### 未確認

- 実機の確かめ（Codex のサンドボックス、Linux の実機）：この Issue は場所の計算と読み取りの部品だけを変え、定期の実行や OS の仕組みに触れないので、行っていない（未確認）。CI の `ubuntu-latest` の結果は PR の検査で確かめる。
- 本物のカタログでの確かめ：まだ作られたカタログがない（I-10 の前）ので、一時のカタログと偽の `gh` だけで確かめた（未確認）。

## Residual Risks / Follow-ups

- **統括に頼むこと**：依存の記録 `iss-00456`（I-15）→ `iss-00460` と `iss-00436`（I-9）→ `iss-00460` を `spec-dock dependency add` で足す（Epic の `plan.md` の表と説明には書いた。ほかの Issue のメタデータなので、この Issue では書いていない）。
- **I-5 への引き渡し**：作成、削除、`work finish` の保存の確認、`holds_under` の接頭辞は `scope_relative(ID)` を使う。作成時の「詳細:」のリンクは `SCOPE_TO_SPEC_DOCK / "docs/…"`（`../../../docs/…`）、`artifacts/rules.md` と `discussions/rules.md` は `../../../../docs/rules/…`。区切りのディレクトリは、なければ実際のディレクトリとして作り、その場所にシンボリックリンクかファイルがあれば書く前に止まり、削除で空になったら消す。新しい ID の入口（`--parent`、`dependency add/remove` の両端など）は `parse_scope_selector`（または `resolve_canonical_scope`）を通す。`KindChange.directories` は名前（ID）のままで、場所は `scope_relative(名前)` で求める。止まっている作業の、カタログに直接 `<ID>` を作るテストは、`CanonicalWorld.directory`/`relative` を使うか、区切りを足す必要がある。
- **I-11 への引き渡し**：ダッシュボードはディレクトリの場所を使わないので、変わるものはない（テストの部品の取り込みだけ）。
- **I-15 への引き渡し**：`scope_bucket` の本体（`width = max(5, len(str(n)))`、`lower = n - n % 1000`、`f"{lower:0{width}d}-{lower + 999:0{width}d}"`）を写し、この Issue のマージの後に、パッケージの関数と比べるテストを足す。平らにする写しの写し先は `<区切り>/<ID>/`、深さは `SCOPE_TO_SPEC_DOCK`。
- **I-9 への引き渡し**：規則の節、使い方の文書、`reference_cli.md`、`help` に、`spec-dock/initiatives/<区切り>/<ID>/`、場所は `scope show <ID> --json` の `path` で確かめること、ID の入力は0埋めしなくてよいことを書く（Epic の `plan.md` の I-9 の節に足した）。
- **I-14 の平らな置き場の残り**：まだ作られたカタログがないので、自動の移しは作っていない。残っていれば `SCOPE_DIRECTORY_MISPLACED`（`root`、`expected` 付き）で示す。
