---
種別: 設計書（Issue）
ID: "iss-00455"
タイトル: "Flatten Canonical Catalog And Drop Slugs"
関連GitHub: ["#455"]
状態: "draft"
最終更新: "2026-10-29"
依存: ["requirement.md"]
親: ["epic-00424", "init-00423"]
---

# iss-00455 Flatten Canonical Catalog And Drop Slugs — 設計

詳細: [Design Guide](../../../../../../docs/authoring/design.md)

## 設計目標

- **D1 ID は種類と番号だけ**：本文を読まず、種類のラベルと番号だけで ID を決める。ID の形は1つの正規表現で決め、解析、カタログの名前、ブランチ名の照合が同じ規則を使う。
- **D2 場所は計算で決まる**：Scope のディレクトリは、いつも `<カタログ>/<ID>`（表示は `spec-dock/initiatives/<ID>`）。探さず、組み立てない。
- **D3 付け替えの判定は1か所**：種類の付け替えの判定（`SCOPE_KIND_CHANGED`）を domain の1つの関数に置き、検査（`workspace validate`、`canonical status --structure`）、読むコマンドの警告、止めるコマンドが同じ結果を使う。I-5 も同じ関数と同じ停止の部品を使う。
- **D4 従来モードを変えない**：従来モードの関数、正規表現、`.meta.json` の処理は変えない（AC-15）。canonical の部品だけを直す。

## Current / Target

| 部分 | Current（`c8b1e338d`） | Target |
|---|---|---|
| ID | 種類のラベルと本文の slug の印。印がないと `id` は null（`SLUG_MARKER_*` の異常） | 種類のラベルと番号だけ。印は読まない |
| ID の形 | `^(init\|epic\|iss)-([0-9]+)$`（`parse_scope_id`） | `^(init\|epic\|iss)-(?:[0-9]{5}\|[1-9][0-9]{5,})$`（`CANONICAL_ID_RE`） |
| スナップショット | 要素に `slug`。GraphQL と REST で `body` を読む | `slug` と本文がない。`version` は1のまま |
| Issue の作成 | `create_issue(title, body, labels)` が本文を送る | `create_issue(title, labels)`。本文を送らない |
| カタログの探し方 | 入れ子をたどり `<ID>-<slug>` の名前で探す。重複は `ScopeDirectoryAmbiguous` | 直下の `<ID>/` を直接見る。重複は起きない（名前が ID そのもの） |
| ディレクトリのない Scope の場所 | 親の場所と `SCOPE_NESTING` と slug で組み立てる | `spec-dock/initiatives/<ID>` |
| 検査 | `SCOPE_DIRECTORY_SLUG_MISMATCH`、`SCOPE_DIRECTORY_DUPLICATE`、入れ子のずれの `SCOPE_DIRECTORY_MISPLACED`、`MISSING`、`ISSUE_MISSING` | `MISSING`、`ISSUE_MISSING`、`KIND_CHANGED`、名前と入れ子の残りの `MISPLACED` |
| 既定のブランチ名 | `<ID>-<slug>` | `<ID>` |
| 種類の付け替え | 判定なし（古い ID は `SCOPE_NOT_FOUND`） | `SCOPE_KIND_CHANGED` で止める・警告する |

## 責務・Interface

ここに書く名前、引数、戻り値、エラーのコードは、I-5、I-11、I-15 が使う公開の形である（契約 C1、C3、C10）。パスは `src/spec_dock/runtime/` から。

### `domain/ids.py`（C1。足すだけ）

```python
CANONICAL_ID_RE: Final = re.compile(r"^(init|epic|iss)-(?:[0-9]{5}|[1-9][0-9]{5,})$")
```

- canonical の ID の形。小文字だけに合う。`format_id`、`ID_RE`、`INPUT_SLUG_KEBAB_RE` などの今の名前は従来モードが使うので変えない。
- I-15 の移行のスクリプトは、この正規表現の文字列を写し、テストで `CANONICAL_ID_RE.pattern` と比べる。

### `domain/canonical_structure.py`（C1、C10）

- **消すもの**：`SLUG_MARKER_MISSING`、`SLUG_MARKER_MULTIPLE`、`SLUG_MARKER_INVALID`、`_LINE_BREAK`、`_MARKER_LINE`、`_MARKER_MESSAGES`、`SlugMarker`、`read_slug_marker`、`format_slug_marker`、`append_slug_marker`、`ScopeNode.slug`、`IssueFacts.body`、`INPUT_SLUG_KEBAB_RE` の import。`FACT_ANOMALY_CODES` は `frozenset({KIND_LABEL_MULTIPLE})` になる。
- **変える関数**：
  - `scope_id(kind: ScopeKind, number: int) -> str`：今のまま（`format_id`。5桁で0埋め、超えればそのまま）。
  - `parse_scope_id(value: str) -> tuple[ScopeKind, int]`：`value.strip().lower()` が `CANONICAL_ID_RE` に合い、番号が1以上のときだけ返す。ほかは `ValueError`。
  - `_node_from_facts`：種類が決まれば `id = scope_id(kind, number)`。決まらなければ（`KIND_LABEL_MULTIPLE`）`id` は null。
  - `_node_from_json`：要素の鍵は `number`、`database_id`、`id`、`kind`、`title`、`state`、`state_reason`、`labels`、`assignees`、`in_progress`、`parent`、`sub_issues`、`blocked_by`、`blocking`、`updated_at`、`url` のちょうど16個（`slug` を外す）。`id` は、`kind` があれば `scope_id(kind, number)` と等しく、`kind` が null なら null でなければならない。ほかは `SnapshotFormatError`（読む側は取り直す。I-1 の仕組みのまま）。`SNAPSHOT_VERSION` は1のまま。
- **足すもの**：

```python
SCOPE_KIND_CHANGED: Final = "SCOPE_KIND_CHANGED"

@dataclass(frozen=True)
class KindChange:
    number: int
    current_id: str                 # GitHub の今の ID（例 "epic-00454"）
    directories: tuple[str, ...]    # 同じ番号で別の種類のカタログの直下の名前（昇順。例 ("iss-00454",)）

def kind_changes(snapshot: StructureSnapshot, directory_ids: Iterable[str]) -> Mapping[int, KindChange]:
    """カタログの直下の <ID> の名前と、スナップショットの同じ番号の Scope の種類を比べる。"""

def renamed_scope(snapshot: StructureSnapshot, scope_id: str) -> ScopeNode | None:
    """scope_id がスナップショットになく、同じ番号の Scope が別の ID で決まっているとき、その Scope。"""

def branch_names_scope(branch: str, scope_id: str) -> bool:
    """最後の "/" の後が scope_id か、scope_id + "-" で始まるとき真。"""
```

  - `kind_changes`：`directory_ids` の各名前を `parse_scope_id` で解き（解けない名前は無視）、その番号の要素がスナップショットにあり、`id` が決まっていて（null でない）、名前と違うとき、その番号の `KindChange` を作る。番号ごとに1つで、`directories` に該当する名前をすべて入れる。要素がない番号、`id` が null の番号（`KIND_LABEL_MULTIPLE`）は入れない。
  - `renamed_scope`：古い ID での指定の解決に使う（スナップショットだけで判定し、カタログを見ない。Epic の2章「指定の解決」）。
  - `branch_names_scope`：`scope_id` は `CANONICAL_ID_RE` に合うものを渡す（合わなければ `ValueError`）。I-5 の `work start` と I-11 のダッシュボードが、ブランチ名と ID を照らすところで使う。今のマージ済みのコードには、ブランチ名と ID を照らす処理はない。

### `infra/github_structure.py`（C1 の GitHub の呼び出しの部品）

- `FULL_READ_QUERY` から `body` を外す。`_facts_from_rest` と `_fetched_from_graphql` は本文を読まない。
- `GithubStructureClient.create_issue(*, title: str, labels: Sequence[str]) -> IssueFacts`：送る本文は `{"title": …, "labels": [...]}` だけ（Epic の2章「書く」）。ほかの書き込みと読み直しは今のまま。

### `infra/catalog_tree.py`（C3）

```python
SCOPE_NAME_PREFIX: Final = re.compile(r"^(?:init|epic|iss)-[0-9]")
NESTED_DIRECTORIES: Final = ("epics", "issues")

@dataclass(frozen=True)
class ScopeDirectory:
    scope_id: str
    relative: PurePosixPath        # いつも PurePosixPath(scope_id)
    path: Path                     # <catalog>/<scope_id>

@dataclass(frozen=True)
class MisplacedDirectory:
    relative: PurePosixPath        # 例 "iss-00454-foo"、"epic-00424/issues"
    reason: Literal["name", "nested"]

class CatalogTree:
    def __init__(self, catalog: Path) -> None: ...
    def directories(self) -> tuple[ScopeDirectory, ...]    # 直下の、名前が ID のディレクトリ（名前の昇順）
    def find(self, scope_id: str) -> ScopeDirectory | None # <catalog>/<ID> を直接見る。ID でなければ ValueError
    def require(self, scope_id: str) -> ScopeDirectory     # なければ LookupError
    def misplaced(self) -> tuple[MisplacedDirectory, ...]  # 置き場の外れ（相対パスの昇順）
```

- Scope のディレクトリは、カタログの直下の、隠しでない、シンボリックリンクでない実際のディレクトリで、名前が `parse_scope_id` で解け、`scope_id(*parse_scope_id(name)) == name` のもの（名前を小文字にしない）。
- `find()` は `<catalog>/<ID>` を `lstat` で確かめ、さらにカタログの直下の実際の名前に ID とちょうど同じ名前があることを確かめる。大文字と小文字を区別しないファイルシステム（macOS の既定）で `ISS-00454/` が `iss-00454` として開けても、Scope のディレクトリにしない（`directories()` と同じ答えにする）。
- `misplaced()`：(1) 直下の、`SCOPE_NAME_PREFIX`（大文字と小文字を区別しない）に合うのに Scope のディレクトリでないディレクトリ（`reason="name"`。`ISS-00454` を含む）。(2) 直下の Scope のディレクトリのすぐ下の `epics/`、`issues/`（`reason="nested"`）。それより深くは調べない。
- **消すもの**：`SCOPE_DIRECTORY_NAME`、`ScopeDirectoryAmbiguous`、`duplicates`、`_walk`、`INPUT_SLUG_KEBAB_RE` の import。
- `git ls-files` は使わない（未保存の新しい Scope も見える）。リンクが正しいカタログ（`require_linked`）にだけ使う。

### `application/canonical_errors.py`

- `SCOPE_KIND_CHANGED_RECOVERY: Final`：「Restore the GitHub kind label. If the new kind is intended, create the Scope again with that kind (spec-dock scope create), move the old directory's contents into the new <ID>/, then run spec-dock scope delete <current ID>.」

### `application/canonical_scopes.py`（読む側の共通の部品）

- **消すもの**：`SCOPE_NESTING`、`CanonicalScopes.ambiguous`、`build_views` の引数 `directories` と入れ子の組み立て。
- `build_views(root, repository, fresh, snapshot)`：各 Scope の `ScopeView.path` は `root / LINK_RELATIVE / <ID>`（ディレクトリの有無によらない）。外に出す JSON の `path` は、I-4 のとおり、ディレクトリがあるときだけこの値で、なければ null。
- `CanonicalScopes` のフィールド（この順の frozen dataclass）：`context`、`repository`、`fresh`、`snapshot`、`views`、`catalog: LinkedCatalog | None`、`directories: Mapping[str, ScopeDirectory]`（スナップショットの Scope のうち、直下に `<ID>/` があるもの）、`kind_changes: Mapping[int, KindChange]`（カタログが見えないときは空）。
- 組み立ては1か所 `build_canonical_scopes` に置き、`load_canonical_scopes`（`display`）も、I-5 が `decision` の新しさで作るときも、これを呼ぶ。

```python
def build_canonical_scopes(
    context: ProjectContext, repository: GithubRepository, fresh: FreshSnapshot, catalog: LinkedCatalog | None
) -> CanonicalScopes   # views、directories、kind_changes（kind_changes(snapshot, catalog.tree.directories() の名前)）を作る
```

- `CanonicalScopes` に足すメソッド：

```python
def require_directory(self, scope_id: str) -> Path              # なければ FileNotFoundError（LOCAL_TARGET_NOT_FOUND）
def lineage(self, scope_id: str) -> tuple[str, ...]             # 自分と GitHub の親をたどった祖先の ID（近い順）。壊れた鎖でも失敗しない
def require_kind_unchanged(self, *scope_ids: str) -> None       # 付け替えがあれば CanonicalCommandError
def kind_change_warnings(self) -> tuple[Diagnostic, ...]        # 付け替えごとに1件の SCOPE_KIND_CHANGED の警告
def snapshot_warnings(self) -> tuple[Diagnostic, ...]           # GITHUB_SNAPSHOT_STALE だけ（今の warnings() の中身）
def warnings(self) -> tuple[Diagnostic, ...]                    # snapshot_warnings() + kind_change_warnings()
```

- `lineage`：祖先の付け替えは、検証した祖先の鎖（`ancestors_for`）を壊す（例：親の Epic が Initiative になると、鎖の種類の規則に合わず `PRECONDITION_FAILED` になる）。付け替えを先に示すために、スナップショットの `parent` をたどる、検証しない鎖を使う。`active set` と、I-5 の `work start`（対象か祖先）が `require_kind_unchanged(*scopes.lineage(target.id))` で使う。

- 関数として足すもの：

```python
def kind_change_error(change: KindChange, *, requested: str | None = None) -> CanonicalCommandError
def refuse_old_ids(scopes: CanonicalScopes, *targets: str | None) -> None
def resolve_canonical_scope(
    context: ProjectContext, scopes: CanonicalScopes, target: str, *, selection: SelectionObservation | None = None
) -> ScopeView
def check_canonical_scope_expectations(
    context: ProjectContext, scopes: CanonicalScopes, selection: SelectionObservation | None, *,
    target: ScopeView | None, expected_current: str | None, expected_backend: str | None,
) -> None
```

  - `SCOPE_KIND_CHANGED` の `details` は、エラー、findings、警告のどれでも同じ形：`{"scope_id": 今の ID, "number", "current_id": 今の ID, "directories": [古い名前…], "requested"(古い ID で指定したエラーだけ), "next_step": SCOPE_KIND_CHANGED_RECOVERY}`。`scope_id` は、ほかの異常の `details.scope_id` と同じく、今の Scope を指す。
  - `kind_change_error`：コード `SCOPE_KIND_CHANGED`、終了コード3、`recovery=(SCOPE_KIND_CHANGED_RECOVERY,)`、`details` は上の形。
  - `refuse_old_ids`：各 `target` を、従来と共有の今の選択子の解析 `parse_scope_selector`（`domain/selectors.py`。変えない）で解く。ID の選択子（ローカルの ID でないもの）で、正規化した ID（`iss-454` は `iss-00454`）に `renamed_scope` が Scope を返すとき、`kind_change_error`（`requested` は正規化した ID、`directories` はカタログで見つかった同じ番号の古い名前。カタログが見えなければ空）を上げる。解けない選択子と、`@current` などの選択の役と `gh:` の参照は、何もしない（今の解決がそのまま答える）。
  - `resolve_canonical_scope`：`refuse_old_ids(scopes, target)` の後に、今の `resolve_scope` に渡す。
  - `check_canonical_scope_expectations`：`refuse_old_ids(scopes, expected_current)` の後に、今の `check_scope_expectations`（`application/scope_expectations.py`。変えない）に `scopes.views` を渡す。canonical の処理の `--expect-current` は、すべてこれか `check_canonical_expectation` を通す（`scope show/list`、`dependency list/check`、`active show`、`artifact list/show`、`branch …`、`workspace validate/sync/doctor`）。
  - `require_kind_unchanged`：渡した ID のどれかの番号が `kind_changes` にあれば、最初のものの `kind_change_error` を上げる。
  - `check_canonical_expectation(context, namespace, *, stored=None, refuse_kind_changed=False) -> tuple[Diagnostic, ...]`（`worktree …` と `installation … --expect-current` が使う）：`--expect-current` の解決に `resolve_canonical_scope` を使う。`refuse_kind_changed` なら、選ぶ Scope に `require_kind_unchanged` を当てる。戻り値は `kind_change_warnings()`（`--expect-current` がなければ空）。
- 警告の合成：読むコマンド（R-455-06 の警告にするもの）は `warnings()` を返す。`workspace validate`、`workspace doctor`、`canonical status --structure` は、付け替えを findings か項目の異常として示すので、`snapshot_warnings()` だけを使い、同じ異常を警告に重ねない。

### `application/canonical_workspace.py`

- **消すもの**：`SCOPE_DIRECTORY_SLUG_MISMATCH`、`SCOPE_DIRECTORY_DUPLICATE`、`misplaced_scopes`、`StructureReport.misplaced`。`SCOPE_NESTING` の import。
- 足すもの：

```python
@dataclass(frozen=True)
class DirectoryReport:
    errors: tuple[Diagnostic, ...]     # SCOPE_DIRECTORY_MISSING、SCOPE_ISSUE_MISSING、SCOPE_KIND_CHANGED
    warnings: tuple[Diagnostic, ...]   # SCOPE_DIRECTORY_MISPLACED

def directory_anomalies(scopes: CanonicalScopes) -> DirectoryReport
```

  - 規則（Epic の2章「内容の置き場」）：
    - `SCOPE_KIND_CHANGED`：`scopes.kind_changes` の番号ごとに1件。`details` は上の共通の形。
    - `SCOPE_DIRECTORY_MISSING`：Scope（`snapshot.scopes`）の `<ID>/` がなく、その番号が `kind_changes` にない。`details={"scope_id", "path": "<ID>", "next_step": "Create spec-dock/initiatives/<ID>/ with the Scope documents, or put back the directory that was moved or renamed."}`。
    - `SCOPE_ISSUE_MISSING`：直下の `<ID>/` の番号の要素がスナップショットにない（要素があり、`id` が null のとき（`KIND_LABEL_MULTIPLE`）と、`kind_changes` にあるときは出さない）。`details={"scope_id", "path", "next_step": "Check GitHub Issue #<n> and its spec-dock kind label; if the Scope is gone, move the directory's contents out of the catalog and delete it."}`。
    - `SCOPE_DIRECTORY_MISPLACED`：`tree.misplaced()` ごとに1件。`details={"path", "reason", "next_step": "Move its contents into <catalog>/<ID>/ and delete the emptied directory."}`。
  - 次の1手の文：Epic と I-4 の設計は、`MISSING` と `ISSUE_MISSING` の次の1手を決めていない。`structure` の項目は「最初の異常の次の1手」を示す（Epic の3章、約束5）ので、この Issue で上の文を決める（どちらも、示した状態を元に戻すか片付けるだけで、新しいコマンドを案内しない）。
  - 並び：errors は `KIND_CHANGED`（番号順）、`MISSING`（番号順）、`ISSUE_MISSING`（名前順）、warnings は `MISPLACED`（パス順）。
- `inspect_canonical_structure(scopes, *, timeout) -> StructureReport(errors, warnings)`：スナップショットの異常、`directory_anomalies`、必要な文書（ディレクトリがある Scope だけ）、`.meta.json`、別名ファイル、Scope でない Issue への依存。
- `structure_item(...)`：項目は `{"status": "ok"|"problem", "next_step": 最初の異常（errors を先に、上の並び）の next_step か null, "snapshot": …, "anomalies": [{"code", "severity": "error"|"warning", "message", "details"}]}`。警告には各異常を `{"item": "structure", …details}` で入れる。取れないときの `unavailable` の形は今のまま。I-4 の `misplaced` の鍵は `anomalies` に置き換える（根拠：Epic の `plan.md` の I-14 の「担当する設計」に「3章の `canonical status` の `structure`」がある。Epic の3章の「項目の担当」の文は `structure` を I-4 としたままなので、I-9 で文書をそろえるときに直すよう、報告書で統括に伝える）。

### `application/canonical_branches.py`

- 対象は `resolve_canonical_scope` で決める。既定の名前は `target.id`。`branch create` と `branch switch` は、名前を決める前に `scopes.require_kind_unchanged(target.id)`（`--dry-run` でも止まる）。`branch show` は `scopes.warnings()` を返す。
- モジュールの説明から slug の印を外す。

### `application/canonical_scope_read.py`、`application/canonical_worktrees.py`

- `resolve_scope` の代わりに `resolve_canonical_scope` を使う（`scope show`、`scope list --parent`、`dependency list/check`、`active set/clear --from`、`artifact list/show`、`--expect-current`）。
- `active set`：対象と祖先に `require_kind_unchanged` を当ててから、ディレクトリを確かめる。
- `artifact list/show`：ディレクトリは `scopes.require_directory(target.id)` の実際のパス（`<catalog>/<ID>`）、表示は `spec-dock/initiatives/<ID>`。
- `worktree create`：`check_canonical_expectation(..., refuse_kind_changed=True)`。`worktree list/show`：`--expect-current` があればその戻り値を、なければ、構造（`display`、リンクを求めない）を読めたときだけ `kind_change_warnings()` を、結果の `warnings` に足す。読めないとき（`CanonicalCommandError`、`GithubStructureError`、`GitProcessError`、`ValueError`、`OSError`）は警告を足さず、結果を変えない。`worktree remove/bootstrap`、`installation … --expect-current` は、Epic の2章の表にないので、付け替えで止めも警告もしない（今のまま。古い ID の `--expect-current` だけは `SCOPE_KIND_CHANGED`）。

### `application/canonical_status.py`

- `_structure_item` の説明と、モジュールの説明の「入れ子のずれ」を、2章の4つの異常に直す。形は `structure_item` に従う。

### 消す名前の一覧（AC-455-07 の検索の対象）

`SLUG_MARKER_MISSING`、`SLUG_MARKER_MULTIPLE`、`SLUG_MARKER_INVALID`、`SlugMarker`、`read_slug_marker`、`format_slug_marker`、`append_slug_marker`、`_MARKER_LINE`、`_MARKER_MESSAGES`、`SCOPE_DIRECTORY_NAME`、`ScopeDirectoryAmbiguous`、`duplicates`、`SCOPE_NESTING`、`misplaced_scopes`、`SCOPE_DIRECTORY_SLUG_MISMATCH`、`SCOPE_DIRECTORY_DUPLICATE`、`ambiguous`。`ScopeNode` と `IssueFacts` の `slug` と `body` の項目、`FULL_READ_QUERY` の `body`、`create_issue` の `body` 引数。

### 変えないもの

- `domain/canonical_content.py` の `CANONICAL_FORMAT`（1のまま。まだ作られたカタログがない）。
- I-3（同期）と I-7（`canonical check`）の本体。読んで、slug と入れ子を使っていないことを確かめた。
- 従来モードの処理（`application/direct_*`、`work_start.py`、`branch_operations.py`、`infra/scope_*`、`domain/ids.py` の今の名前）と、canonical の処理も使う従来の共有の部品（`domain/selectors.py` の `parse_scope_selector`、`application/scope_expectations.py` の `check_scope_expectations`、`application/worktree_observation.py` の `resolve_scope` と `ancestors_for`）。canonical の側は、これらを包む関数を足すだけにする。

## data / failure

- **スナップショットの形**：版1の要素の鍵の集合から `slug` を外す。利用者の状態の置き場にまだファイルはない（0.3.0 の前）ので、版は上げない。古い形のファイルは `SnapshotFormatError` で取り直しになる（`ensure_fresh` の「版が違う・壊れた」と同じ扱い）。取り直せないときは、ファイルがないときと同じ失敗のコードで止まる。
- **カタログ**：形式の版は1のまま。この Issue はカタログに書かない（読むだけ）。
- **失敗のコード**：

| コード | 終了コード | 出る場所 | 次の1手 |
|---|---|---|---|
| `SCOPE_KIND_CHANGED` | 3（止めるもの、古い ID の指定）／—（findings、項目の異常、警告） | `branch create/switch`、`active set`、`worktree create --expect-current`、すべてのコマンドの古い ID の指定と `--expect-current`／`workspace validate`、`canonical status --structure`、読むコマンド | `SCOPE_KIND_CHANGED_RECOVERY` |
| `SCOPE_DIRECTORY_MISSING`、`SCOPE_ISSUE_MISSING` | —（findings、項目の異常） | `workspace validate`、`workspace doctor`、`canonical status --structure` | この Issue で決めた文（`directory_anomalies` の規則） |
| `SCOPE_DIRECTORY_MISPLACED` | —（警告、項目の異常） | 同上 | 中身を `<カタログ>/<ID>/` に移し、空のディレクトリを消す |
| `LOCAL_TARGET_NOT_FOUND` | 4 | `active set`、`artifact list/show` で `<ID>/` がない | 今のまま |

- 消すコード：`SLUG_MARKER_MISSING`、`SLUG_MARKER_MULTIPLE`、`SLUG_MARKER_INVALID`、`SCOPE_DIRECTORY_SLUG_MISMATCH`、`SCOPE_DIRECTORY_DUPLICATE`。`ScopeDirectoryAmbiguous` による `PRECONDITION_FAILED` もなくなる。

## 変更対象

- 変えるコード：`domain/ids.py`（足すだけ）、`domain/canonical_structure.py`、`infra/github_structure.py`、`infra/catalog_tree.py`、`application/canonical_errors.py`、`application/canonical_scopes.py`、`application/canonical_workspace.py`、`application/canonical_status.py`、`application/canonical_branches.py`、`application/canonical_scope_read.py`、`application/canonical_worktrees.py`。
- 変えるテスト（すべて canonical モードのもの）：`tests/unit/domain/test_canonical_structure.py`、`tests/unit/infra/test_github_structure.py`、`tests/unit/infra/test_github_snapshot.py`、`tests/unit/domain/test_canonical_readiness.py`、`tests/unit/infra/test_catalog_tree.py`、`tests/support/fake_github.py`、`tests/support/canonical_scopes.py`、`tests/integration/github/test_fake_github.py`、`tests/cli_runtime/test_issue431_*.py`、`test_issue430_canonical_status.py`、`test_issue430_canonical_sync.py`、`test_issue429_canonical_link.py`、`tests/unit/infra/test_migration_contract_copies.py`（slug の印の比べ合わせだけを外す）。足すテスト：`tests/cli_runtime/test_issue455_flat_ids.py`（付け替えと平らな置き場のコマンドの確かめ）。
- テストの部品の新しい形：`FakeGithub.scope(kind, *, title=None, number=None, parent=None, state="open", state_reason=None, labels=(), body="Scope body.")`（本文に印を付けない。題名の既定は `"Scope <番号>"`）。`FakeGithub` で変えるのは `scope()` だけで、`POST …/issues` の本文の受け取り、保存、記録は変えない（I-15 までは、移行のスクリプトが本文の印を送り、I-8 の移行のテスト（`tests/integration/migration/`、`tests/support/migration_repo.py`）がそれを確かめるため。それらのテストは変えずに通す）。`CanonicalWorld.scope(kind, number, title=None, *, parent=None, directory=True, documents=…)`、`CanonicalWorld.directory(kind, number, *, documents=…) -> Path`（`<catalog>/<ID>`）、`CanonicalWorld.relative(kind, number) -> Path`（`<ID>`）。`_NESTING` を消す。

## 移行・互換性・rollback

- 移行：N/A。canonical モードはまだどのリポジトリでも使われておらず（spec-dock も版3）、利用者の状態の置き場にスナップショットも、作られたカタログもない。古い形のスナップショットがあっても取り直しになる。
- 互換性：版3のリポジトリは、canonical の処理を通らないので変わらない（AC-15）。I-5、I-11 の未マージのブランチは、テストの部品の引数（`slug`）と消した名前に合わせ直す必要がある（その担当が `origin/main` を取り込むときに行う）。
- rollback：PR を `git revert` すれば戻る。利用者の運用への影響はない。

## testability

- 単体：`CANONICAL_ID_RE` と `parse_scope_id` の境界（4桁、5桁、6桁、先頭の0、番号0、接尾辞）、`_node_from_facts` が本文によらず ID を決めること、スナップショットの往復と古い形（`slug` の鍵、`id` と `kind` の食い違い）の拒否、`kind_changes`（古い名前が2つ、新しい名前もある、種類が決まらない番号）と `renamed_scope` と `branch_names_scope`、`CatalogTree` の直下だけの判定と `misplaced`（隠し、リンク、ファイル、大文字）、`FULL_READ_QUERY` に `body` がないことと `create_issue` の送る本文。
- CLI（偽の `gh`、一時の bare の origin、一時の `XDG_STATE_HOME`、`tests/conftest.py` の偽物の中）：平らな置き場での `scope show/list`、`active set`、`artifact list`、`workspace validate`、`canonical status --structure`、`branch create` の既定の名前、付け替えのときの停止と警告と古い ID の解決、読むだけのコマンドがリポジトリとカタログに書かないこと（I-4 の確かめを平らな置き場で通す）。
- 偽の `gh` の記録：GraphQL の問い合わせの文に `body` がないこと、`POST …/issues` の本文に `body` がないこと。
- 回帰：版3のテスト（`tests/` の canonical でないもの）を変えずに全体を通す。

## risk

| リスク | 軽減 |
|---|---|
| 共有のテストの部品（`fake.scope`、`CanonicalWorld`）の形が変わり、I-5、I-11 のブランチが取り込みで壊れる | 新しい形を、この設計書の「変更対象」に書く。題名の既定を決めた値にし、引数の名前を `title` にそろえる |
| 消した名前を未マージのブランチが使っている | 消した名前の一覧をこの設計書と報告書に書く。I-5、I-11 は I-14 の後に再開する（Epic の計画） |
| 付け替えの判定が場所によってずれる | 判定を `kind_changes` と `renamed_scope` の2つの関数だけにし、検査、警告、停止がそれを使う |
| 従来モードを変えてしまう | `domain/ids.py` は足すだけにし、従来の関数を触らない。版3のテストを変えずに全体を通す |
