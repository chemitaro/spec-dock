---
種別: 設計書（Issue）
ID: "iss-00460"
タイトル: "Bucket Canonical Catalog By Thousand"
関連GitHub: ["#460"]
状態: "draft"
最終更新: "2026-10-29"
依存: ["requirement.md"]
親: ["epic-00424", "init-00423"]
---

# iss-00460 Bucket Canonical Catalog By Thousand — 設計

詳細: [Design Guide](../../../../../../docs/authoring/design.md)

## 設計目標

- **D1 場所は番号だけで計算する**：区切りは番号だけから1つの純粋な関数で決め、カタログの読み取り、表示のパス、検査、作成（I-5）、移行のスクリプト（I-15 の写し）が同じ規則を使う。探さない。
- **D2 置き場の部品は1か所**：Scope の相対の場所（`<区切り>/<ID>`）を作るのは `domain/canonical_layout.py` の関数だけにし、`infra/catalog_tree.py` と `application/canonical_scopes.py` と `application/canonical_workspace.py` はそれを呼ぶ。
- **D3 入力の正規化は今の1か所のまま**：ID の入力を直すのは、従来モードと共有の選択子の解析（`domain/selectors.py` の `parse_scope_selector`）だけである（すでに直している。変えない）。名前を ID として読む部品は厳密なままにする。
- **D4 従来モードを変えない**：従来モードの関数、正規表現、`.meta.json` の処理、`domain/selectors.py` と `domain/ids.py` の今の名前は変えない（AC-15）。

## Current / Target

| 部分 | Current（`95bbb7a1c`、I-14 の後） | Target |
|---|---|---|
| Scope のディレクトリ | `<カタログ>/<ID>/`（直下） | `<カタログ>/<区切り>/<ID>/`（例 `00000-00999/iss-00454/`） |
| 場所を作るところ | `catalog_tree.py`（`self.catalog / entry.name`）と `canonical_scopes.build_views`（`link / node.id`）と `canonical_workspace`（`"path": scope_id`）が別々に `<ID>` を置く | `canonical_layout.scope_relative(scope_id)` の1か所 |
| 置き場の外れ | 直下の ID の形の名前で ID でないもの（`name`）、`<ID>/` の下の `epics/`・`issues/`（`nested`） | 直下の ID の形の名前（`root`）、区切りの名前の誤りと区切りの違う ID（`bucket`）、区切りの中の ID でない名前（`name`）、`nested`。ID の決まるものは `expected` を持つ |
| ID の入力 | `parse_scope_selector` が `iss-454`、`iss-000454` を `iss-00454` に直す | 同じ（変えない）。すべての canonical の入口が通ることをテストで確かめる |
| 作成時の深さ | Epic の6章が `<カタログ>/<ID>/` からの `../../docs/…` と書く（実装は I-5、未マージ） | `SCOPE_TO_SPEC_DOCK = ../../..`。「詳細:」は `../../../docs/…` |

## 責務・Interface

ここに書く名前、引数、戻り値、例外は、I-5 と I-15 が使う公開の形である（契約 C3）。パスは `src/spec_dock/runtime/` から。

### `domain/canonical_layout.py`（C3。足す）

```python
BUCKET_SIZE: Final = 1000
# 区切りの形をした名前（正しいかは is_bucket_name で決める）。外れの報告に使う。
BUCKET_NAME_SHAPE: Final = re.compile(r"^[0-9]+-[0-9]+$")
# Scope のディレクトリ <catalog>/<bucket>/<ID>/ から spec-dock/ まで（リンク spec-dock/initiatives を通る）。
SCOPE_TO_SPEC_DOCK: Final = PurePosixPath("../../..")

def scope_bucket(number: int) -> str:
    """番号の区切りの名前。number < 1 は ValueError。"""
    # width = max(5, len(str(number))); lower = number - number % 1000; upper = lower + 999
    # return f"{lower:0{width}d}-{upper:0{width}d}"

def scope_relative(scope_id: str) -> PurePosixPath:
    """Scope のディレクトリのカタログからの相対の場所 PurePosixPath(f"{scope_bucket(n)}/{scope_id}")。

    scope_id は CANONICAL_ID_RE にちょうど合う ID（0埋めした形）。ほかは ValueError（入力は先に選択子で直す）。
    """

def is_bucket_name(name: str) -> bool:
    """name が、ある番号の区切りの名前とちょうど同じとき真（"00000-00999"、"100000-100999"）。"""
```

- 例（AC-460-01）：`scope_bucket(1) == scope_bucket(454) == scope_bucket(999) == "00000-00999"`、`scope_bucket(1000) == "01000-01999"`、`scope_bucket(2114) == "02000-02999"`、`scope_bucket(99999) == "99000-99999"`、`scope_bucket(100000) == scope_bucket(100454) == "100000-100999"`、`scope_bucket(1000000) == "1000000-1000999"`。`scope_relative("iss-00454") == PurePosixPath("00000-00999/iss-00454")`。
- `scope_relative` は、`scope_id` を `domain/canonical_structure.py` の `parse_scope_id` で解き、`scope_id(kind, number) == scope_id` を確かめる（`ISS-00454` や前後の空白も ValueError。名前として使うため）。
- `is_bucket_name`：`BUCKET_NAME_SHAPE` に合い、下端 `lower` が1,000の倍数で、`name == scope_bucket(max(lower, 1))` のとき真。`0-999`、`00000-00998`、`000000-000999`、`01000-01999x` は偽。
- I-15 の移行のスクリプトは、`scope_bucket` の本体（上のコメントの3行）を写して持ち、この Issue のマージの後に、いくつかの番号（1、999、1000、99999、100000、1000000）でパッケージの `scope_bucket` と同じ値を返すことをテストで比べる。`BUCKET_SIZE` の値も比べてよい。
- `SCOPE_TO_SPEC_DOCK`：I-5 の作成は、テンプレートの「詳細:」の `spec-dock/docs/…` へのリンクを `SCOPE_TO_SPEC_DOCK / "docs/…"`（`../../../docs/…`）に、`artifacts/rules.md` と `discussions/rules.md` を `".." / SCOPE_TO_SPEC_DOCK / "docs/rules/…"`（`../../../../docs/rules/…`）に書き換える。

### `infra/catalog_tree.py`（C3）

```python
@dataclass(frozen=True)
class ScopeDirectory:
    scope_id: str
    relative: PurePosixPath        # いつも scope_relative(scope_id)。例 "00000-00999/iss-00454"
    path: Path                     # <catalog>/<bucket>/<ID>

MisplacedReason = Literal["root", "bucket", "name", "nested"]

@dataclass(frozen=True)
class MisplacedDirectory:
    relative: PurePosixPath        # 例 "iss-00454"、"00000-00999/iss-01454"、"00000-00999/epic-00424/issues"
    reason: MisplacedReason
    expected: PurePosixPath | None = None   # 名前が ID と決まるときの正しい場所

class CatalogTree:
    def directories(self) -> tuple[ScopeDirectory, ...]    # 正しい区切りの下の、正しい区切りの <ID>（relative の昇順）
    def find(self, scope_id: str) -> ScopeDirectory | None # <catalog>/<bucket>/<ID> を直接見る。ID でなければ ValueError
    def require(self, scope_id: str) -> ScopeDirectory     # なければ LookupError
    def misplaced(self) -> tuple[MisplacedDirectory, ...]  # 置き場の外れ（relative の昇順）
```

- 区切りのディレクトリは、カタログの直下の、隠しでない、シンボリックリンクでない実際のディレクトリで、名前が `is_bucket_name` に合うもの。Scope のディレクトリは、区切りのディレクトリの直下の、隠しでない、シンボリックリンクでない実際のディレクトリで、名前が ID とちょうど同じで（I-14 の `_scope_name`）、`scope_bucket(番号) == 区切りの名前` のもの。
- `find()`：今の I-14 と同じく、入力を `scope_id(*parse_scope_id(…))` で ID にし（`" ISS-00454 "` は `iss-00454`、`iss-454` は ValueError。I-14 のまま）、`<catalog>/<scope_relative(ID)>` を `lstat` で確かめ、区切りのディレクトリが実際のディレクトリで、その中の実際の名前に ID とちょうど同じ名前があることを確かめる（大文字と小文字を区別しないファイルシステムで `ISS-00454/` を開かないため）。
- `misplaced()`：
  1. カタログの直下（隠し、シンボリックリンク、ファイルは除く）：
     - `is_bucket_name` に合う → 区切りとして中を調べる（下の2）。
     - I-14 の `SCOPE_NAME_PREFIX`（大文字と小文字を区別しない）に合う → `root`。名前が ID（`_scope_name`）なら `expected = scope_relative(名前)`。
     - `BUCKET_NAME_SHAPE` に合う（区切りの名前の誤り） → `bucket`、`expected = None`。
     - ほか（`notes` など）は調べない。
  2. 区切りのディレクトリの直下（隠し、シンボリックリンク、ファイルは除く）：
     - 名前が ID で、区切りが合う → Scope のディレクトリ。そのすぐ下の `epics/`、`issues/` が実際のディレクトリなら `nested`（I-14 のまま）。
     - 名前が ID で、区切りが違う → `bucket`、`expected = scope_relative(名前)`。
     - `SCOPE_NAME_PREFIX` に合う（ID でない） → `name`。
     - ほかは調べない。
- 消すもの：なし（`SCOPE_NAME_PREFIX`、`NESTED_DIRECTORIES` は残す）。`git ls-files` は使わない（I-14 のまま）。

### `application/canonical_scopes.py`

- `build_views`：各 Scope の `ScopeView.path` を `root / LINK_RELATIVE / scope_relative(node.id)` にする（ディレクトリの有無によらない）。外に出す JSON の `path` は、I-14 のとおり、ディレクトリがあるときだけこの値で、なければ null。
- モジュールと関数の説明の `<catalog>/<ID>`、`initiatives/<ID>` を区切りの形に直す。ほかの公開の形（`CanonicalScopes`、`build_canonical_scopes`、`require_directory`、`lineage`、`require_kind_unchanged`、`warnings` など）は変えない。
- `active set` のリンクの先は、今の `active_links` が `ScopeView.path` の `spec-dock/` からの相対で作るので、`../initiatives/<区切り>/<ID>` になる（コードの変更はない。テストで確かめる）。`artifact list/show` は `ScopeDirectory.relative` から表示のパスを作るので、`spec-dock/initiatives/<区切り>/<ID>/artifacts/…` になる。

### `application/canonical_workspace.py`

- `SCOPE_DIRECTORY_MISSING`：メッセージ `f"{scope_id} has no directory {scope_relative(scope_id)}/ in the catalog"`、`details.path = scope_relative(scope_id).as_posix()`。`DIRECTORY_MISSING_NEXT_STEP` の `spec-dock/initiatives/{scope_id}/` を `spec-dock/initiatives/{path}/` にする。
- `SCOPE_ISSUE_MISSING`：`details.path` は `ScopeDirectory.relative`（`<区切り>/<ID>`）。文は今のまま。
- `SCOPE_DIRECTORY_MISPLACED`：`details = {"path", "reason", "expected": str | None, "next_step": MISPLACED_NEXT_STEP}`。メッセージは理由ごとに次のとおり。
  - `root`：`f"{path} is at the catalog root; Scope directories live under their number's bucket"`
  - `bucket`：`f"{path} is not a bucket of its numbers"`（区切りの名前の誤り）、`f"{path} is in another number's bucket"`（区切りの違う ID）
  - `name`：`f"{path} is not a Scope directory <ID>/ in its bucket"`
  - `nested`：今のまま。
- `MISPLACED_NEXT_STEP = "Move the Scope contents it holds into spec-dock/initiatives/<bucket>/<ID>/ for each ID (the bucket is the ID number's thousand range, e.g. 00000-00999/iss-00454) and delete the emptied directory."`（区切りの名前の誤りのディレクトリは中に複数の `<ID>/` を持ちうるので、「それぞれの ID」の文にする）
- 並び、`DirectoryReport`、`inspect_canonical_structure`、`structure_item` の形は I-14 のまま。

### ID の入力（変えるコードはない）

- canonical モードの ID の入口は、すべて `resolve_canonical_scope`、`check_canonical_scope_expectations`、`check_canonical_expectation`、`refuse_old_ids`（I-14）を通り、そこで `parse_scope_selector` が `iss-454`、`ISS-454`、`iss-000454` を `iss-00454` に直す。`gh:OWNER/REPO#N` と `@current` などの役は今のまま。
- この Issue は、それぞれの入口に0埋めしない ID を渡すテストを足し、通っていない入口がないことを確かめる（AC-460-04）。通っていない入口が見つかったときは、その入口で `parse_scope_selector` を使うように直す（新しい正規化の関数は作らない）。
- I-5 が足す ID の入口（`--parent`、`dependency add/remove` の両端など）も、同じく `parse_scope_selector`（または `resolve_canonical_scope`）を通す。I-5 の設計への引き渡しとして `report.md` に書く。
- 区切りのディレクトリそのものの扱い（I-5 への引き渡し。Epic の `plan.md` の I-5 の「変わる」にも書いた）：作成では、区切りがなければ実際のディレクトリとして作る。区切りの名前の場所にシンボリックリンクかファイルがあれば、書く前に止まる（読む側は、それを区切りとして扱わない）。削除で空になった区切りは消す（Git は空のディレクトリを保存しないので、残しても他のクローンにはなく、検査の異常にもならないが、手元とそろえるため）。
- 名前を ID として読む部品（`parse_scope_id`、`CatalogTree`、`kind_changes`、`branch_names_scope`、`scope_relative`）は、I-14 のとおり厳密な形だけを受け付ける。

## data / failure

- **カタログ**：形式の版（`CANONICAL_FORMAT`）は1のまま。まだ作られたカタログがない（I-10 の前）ので、版を上げず、平らな置き場からの移しも作らない。I-14 の平らな `<ID>/` が残っていたら、`SCOPE_DIRECTORY_MISPLACED`（`root`、`expected` 付き）として示し、移すのは利用者（またはエージェント）である。
- **スナップショット**：変えない（場所を持たない）。
- **失敗のコード**：新しいコードはない。

| コード | 終了コード | 出る場所 | 次の1手 |
|---|---|---|---|
| `SCOPE_DIRECTORY_MISSING` | —（findings、項目の異常） | `workspace validate`、`workspace doctor`、`canonical status --structure` | `spec-dock/initiatives/<区切り>/<ID>/` を作るか、移したディレクトリを戻す |
| `SCOPE_DIRECTORY_MISPLACED` | —（警告、項目の異常） | 同上 | `MISPLACED_NEXT_STEP` |
| `LOCAL_TARGET_NOT_FOUND` | 4 | `active set`、`artifact list/show` で `<区切り>/<ID>/` がない | 今のまま |

- 内部の誤り：`scope_bucket` に0以下、`scope_relative` に ID でない値を渡すと `ValueError`。コマンドの入口は、それより前に選択子の解析で使い方の誤りとして止めるので、利用者には出ない。

## 変更対象

- 変えるコード：`domain/canonical_layout.py`（足すだけ）、`infra/catalog_tree.py`、`application/canonical_scopes.py`、`application/canonical_workspace.py`、`application/canonical_status.py`（説明の文だけ）。`SCOPE_KIND_CHANGED_RECOVERY`（`application/canonical_errors.py`）の「新しい `<ID>/`」は、`scope create` が新しい番号の `<区切り>/<ID>/` を作り、そこへ移すという意味なので、区切りがあっても正しく、文を変えない。
- 変えるテスト（すべて canonical モードのもの）：`tests/support/canonical_scopes.py`（`CanonicalWorld.relative(kind, number)` が `<区切り>/<ID>` を返す。`directory` はそこに作る）、`tests/unit/infra/test_catalog_tree.py`、置き場のパスを直書きしている `tests/cli_runtime/test_issue431_*.py`、`test_issue455_flat_ids.py`、`test_issue430_canonical_status.py`、`tests/unit/application/test_canonical_catalog.py` など（実装の後に検索して確かめ、`report.md` に一覧で書く）。
- 足すテスト：`tests/unit/domain/test_canonical_layout_buckets.py`（区切りの計算、相対の場所、`is_bucket_name`、深さの定数）、`tests/cli_runtime/test_issue460_bucket_dirs.py`（区切りの置き場、外れ、0埋めしない入力、深さの実際のリンク）。
- 変えない：`domain/selectors.py`、`domain/ids.py`、`domain/canonical_structure.py`（C1。`KindChange.directories` は名前のまま）、スナップショット（C10）、I-3 と I-7 の本体、テンプレートの配布資産、従来モードの処理とテスト。
- Epic の文書：`requirement.md`（R-A3、R-G7、AC-04、AC-09、合意済みの判断。統括の許可）、`design.md`（用語、Target、2章、3章、6章、7章、10章、11章、12章、14章、変更対象、testability、「設計の判断」）、`plan.md`（目標、一覧、順序の図と説明、I-5、I-11、I-13、I-15 の置き場の記述、I-16 の節、rollback）。

## 移行・互換性・rollback

- 移行：N/A。canonical モードはまだどのリポジトリでも使われていない（spec-dock も版3）。作られたカタログがないので、平らな置き場からの移しは要らない。
- 互換性：版3のリポジトリは canonical の処理を通らないので変わらない（AC-15）。I-5、I-11 の未マージのブランチは、`origin/main` を取り込むときに、テストの部品の `CanonicalWorld.relative` の値（`<区切り>/<ID>`）と、カタログに直接 `<ID>` を作っているテストを合わせる必要がある。I-15 は、この Issue の `scope_bucket` を写す。
- rollback：PR を `git revert` すれば戻る。利用者の運用への影響はない。I-5、I-11、I-15 が取り込んだ後は、revert せずに直す PR を出す。

## testability

- 単体：`scope_bucket` の9つの例と0・負の数、種類によらないこと、`scope_relative` の例と ID でない値、`is_bucket_name` の真偽、`SCOPE_TO_SPEC_DOCK` の正規化（`LINK_RELATIVE / scope_relative(id) / SCOPE_TO_SPEC_DOCK` が `spec-dock`）、`CatalogTree` の区切りの下だけの判定と `misplaced` の4つの理由と `expected`（隠し、リンク、ファイル、大文字、区切りの違う ID、区切りの名前の誤り、I-14 の平らな残り）。
- CLI（偽の `gh`、一時の bare の origin、一時の `XDG_STATE_HOME`、`tests/conftest.py` の偽物の中）：区切りの置き場での `scope show/list` の `path`、`active set` のリンクの先、`artifact list` のパス、平らな残りを場所にしないこと、`workspace validate` と `canonical status --structure` の異常、0埋めしない入力の各入口（`requirement.md` の R-460-04 の列挙を parametrize する）、深さのリンク（Markdown のリンクは字面で畳んでそのチェックアウトの `spec-dock/docs/…`、シンボリックリンクはカタログの実際の場所から mainの `spec-dock/docs/…`）。
- 回帰：版3のテスト（`tests/` の canonical でないもの）を変えずに全体を通す。I-14 の付け替えのテスト（`test_issue455_flat_ids.py`）を区切りの置き場で通す。

## risk

| リスク | 軽減 |
|---|---|
| I-15 の写しの区切りの計算が食い違い、移行で場所がずれる | 計算を3行の純粋な関数にし、例をこの設計書に書く。I-15 はマージの後にパッケージの関数と比べるテストを足す |
| 置き場の文字列を別々に作る箇所が残り、場所が食い違う | 場所を作るのを `scope_relative` だけにし、`<ID>` を直接つなぐ箇所の検索を報告書に書く |
| 0埋めしない入力が通らない入口が残る | 入口ごとの CLI のテストを足す。新しい正規化の関数は作らず、今の1か所に通す |
| I-5、I-11 のブランチがテストの部品の変更で壊れる | テストの部品の形（引数）は変えず、`relative` の値だけを変える。変更点を報告書に書く |
| 従来モードを変えてしまう | 変えるファイルを canonical のものに限り、版3のテストを変えずに全体を通す |
