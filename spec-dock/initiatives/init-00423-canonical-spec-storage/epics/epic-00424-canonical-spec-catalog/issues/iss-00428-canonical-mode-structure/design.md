---
種別: 設計書（Issue）
ID: "iss-00428"
タイトル: "Add Canonical Mode And GitHub Structure Snapshot"
関連GitHub: ["#428"]
状態: "draft"
最終更新: "2026-10-26"
依存: ["requirement.md"]
親: ["epic-00424", "init-00423"]
---

# iss-00428 Add Canonical Mode And GitHub Structure Snapshot — 設計

詳細: [Design Guide](../../../../../../docs/authoring/design.md)

この設計書は、Epic の `design.md` の1章、2章、6章の I-1 の行を、実装できる粒度にしたものである。Epic の設計を言い換えず、モジュール、関数、型、エラーのコード、データの形を決める。後の Issue は、この章の「公開の形」をそのまま使う（契約 C1、C2、C10）。変える必要があれば、先に Epic の `design.md` とこの文書を直す。

Epic の記述と、この文書の解釈が違う点は、統括が了承し（2026-10-26）、Epic の文書に反映する。一覧は `plan.md` の「統括の判断」にある。

## 設計目標

- **G-1 従来の経路を変えない**：版3の宣言では、`dispatch()` は、モードを確かめる分岐を1つ通った後、今と同じ従来の処理を、今と同じ順で呼ぶ。従来の処理の関数と、`.meta.json` を読み書きするコードは変えない。
- **G-2 振り分けは1か所**：モードによる振り分けは `dispatch()` だけで行う。canonical の処理は、新しいモジュールの表に登録するだけで足せる。
- **G-3 構造は純粋な規則で組み立てる**：GitHub から読んだ事実から、スナップショット、異常、書き込みの反映を作る処理は、`domain/` の純粋な関数にする。時刻は引数で渡す。
- **G-4 GitHub への要求は1つの部品だけが送る**：状態コード、304、レート制限、再試行、順に送ること、書き込みの間の1秒を、1つの呼び出しの部品に集める。
- **G-5 スナップショットは失敗の原因にならない**：状態の置き場に書けない、読めない、壊れている、排他が取れないときも、コマンドを失敗させない。

## Current / Target

### Current（`origin/main`、2026-10-26）

- `read_workspace_declaration` は、`schema_version` が整数の3でなければ `ValueError("workspace requires known schema 3")` を出し、`dispatch()` が `PRECONDITION_FAILED`（終了コード3）にする。
- `dispatch()` は、`installation`、`workspace validate --ci`、`workspace doctor --raw` を `resolve_context` の前に扱い、ほかのコマンドを `resolve_context` の後の `if`/`elif` の連なりで扱う。`--ci` は作業ツリーの宣言を見ずに、HEAD のコミットの宣言を読む（`direct_validation.py:46`）。`--raw` は、壊れた宣言や知らない版でも診断する（`direct_diagnostics.py:76-81`）。
- GitHub は `GithubIssueGateway`（取得、作成、状態の変更。GET、POST、PATCH だけ、本文は文字列だけ、再試行なし、404 は権限なし）。
- 構造をファイルに保存して使い回すことはしない。
- 配布資産 `spec-dock/workspace.json` は `{"schema_version":3,"writer_protocol":"specdock.worktree-writer/v1"}`（`init_only`）。

### Target

```text
dispatch(namespace, cwd)
  ├ 対応していない OS            → UNSUPPORTED_PLATFORM（今と同じ）
  ├ resolve_context の前の表     → REPOSITORY_INDEPENDENT_HANDLERS（I-1 では空。I-3 が canonical sync --registered、I-7 が canonical check を足す）
  ├ installation *               → 今と同じ（版3と版4を受け付ける）
  ├ workspace validate --ci       ┐ 宣言が版4と読めるときだけ canonical の振り分けへ。
  ├ workspace doctor --raw        ┘ それ以外は今と同じ従来の処理
  └ resolve_context（版3か4。ほかは PRECONDITION_FAILED）
      ├ mode == "canonical" → dispatch_canonical（CANONICAL_HANDLERS。なければ CANONICAL_NOT_IMPLEMENTED）
      ├ "canonical ..." の版3 → CANONICAL_NOT_MIGRATED
      └ mode == "legacy"    → 今と同じ if/elif の連なり（変えない）

構造の読み書き（canonical モードのコマンドと定期の同期が使う。I-1 は部品だけ）
  domain/canonical_structure.py   表し方、ScopeNode、StructureSnapshot、異常、書き込みの反映（純粋）
  infra/github_structure.py       GithubApi（gh api の呼び出し）と GithubStructureClient（GraphQL、条件付きの要求、REST）
  infra/github_snapshot.py        SnapshotStore（置き場、排他、メモリー）と StructureSnapshotService（ensure_fresh、reread、reflect）
  infra/state_root.py             状態の置き場の根
```

## 責務・Interface

### 1. モードの判定（C2。`application/project_context.py`）

```python
WorkspaceMode = Literal["legacy", "canonical"]
LEGACY_WORKSPACE_SCHEMA = 3
CANONICAL_WORKSPACE_SCHEMA = 4

def read_workspace_declaration(path: Path) -> dict[str, object]
def workspace_mode(workspace: Mapping[str, object]) -> WorkspaceMode
def probe_workspace_mode(root: Path) -> WorkspaceMode | None

class ProjectContext(GitContext):
    workspace: dict[str, object]
    @property
    def mode(self) -> WorkspaceMode
    def require_writer(self) -> None   # 今と同じ（版3と版4の両方に当てる）
```

- `read_workspace_declaration` は、`schema_version` が整数（真偽値を除く）の3か4のときだけ宣言の辞書を返す。それ以外は `ValueError("workspace requires known schema 3 or 4")`。`writer_protocol` の確かめは今と同じ。戻り値を辞書のままにするのは、従来の呼び出し元（`start_snapshot.py`、`direct_validation.py`）を変えないためである。モードは `workspace_mode` か `ProjectContext.mode` で得る（Epic の「モードを返す」を、この2つで満たす）。
- `probe_workspace_mode(root)` は、`<root>/spec-dock/workspace.json` を読み、読めて正しい宣言ならモードを、ない、壊れている、知らない版なら `None` を返す。例外を出さない。作業ツリーの宣言を `resolve_context` で確かめない今のコマンド（`workspace validate --ci`、`workspace doctor --raw`）と、`installation` の `--expect-current` の振り分けだけに使う。版4と読めないときは、今の経路をそのまま通す。
- 従来の処理が、別の宣言（基点のコミット、`--ci` の HEAD、同じクローンのほかのworktree）を版4として受け付けるようになる点は、移行していないリポジトリには版4の宣言がないので、AC-15 に当たらない。切り替えの途中（I-10、I-12）にだけ起き、どれも先の確かめで止まる（「risk」）。

### 2. 振り分けの入口（C2。`commands/canonical_dispatch.py`、`commands/runtime_dispatch.py`）

```python
# 型の別名は、後の Issue が実行時にも import できるよう、モジュールの中で定義する
CanonicalHandler = Callable[[argparse.Namespace, ProjectContext], OperationResult[object]]
RepositoryIndependentHandler = Callable[[argparse.Namespace, Path], OperationResult[object] | None]

CANONICAL_HANDLERS: dict[str, CanonicalHandler]                       # キーは LEAF_PATHS の値
REPOSITORY_INDEPENDENT_HANDLERS: dict[str, RepositoryIndependentHandler]

def dispatch_repository_independent(namespace, cwd) -> OperationResult[object] | None
def dispatch_canonical(namespace, context) -> OperationResult[object]
```

- `REPOSITORY_INDEPENDENT_HANDLERS` は、`resolve_context` より前に呼ぶ表である。リポジトリによらないコマンド（`canonical sync --registered`。I-3）と、宣言を自分で調べるコマンド（`canonical check`。I-7）を登録する（統括の判断 B、2026-10-26）。ハンドラーは名前空間と `cwd` を受け、自分でリポジトリと宣言を確かめる。`canonical check` は、1章の「`canonical` グループは版3で `CANONICAL_NOT_MIGRATED`」の例外で、版3の宣言を `CANONICAL_CHECK_FAILED`（終了コード7）の1件として返す（I-7 の受け入れ）。
- `dispatch_repository_independent` は、表にそのコマンドがあればそれを呼ぶ。ハンドラーが `None` を返したとき（例：`canonical sync` の `--registered` がないとき）は、通常の経路（`resolve_context` の後）へ進む。I-1 では表は空である。
- `dispatch_canonical` は、`CANONICAL_HANDLERS` にそのコマンドがあればそれを呼び、なければ `CANONICAL_NOT_IMPLEMENTED` を返す。I-1 で登録するのは `workspace migrate`（拒否）だけである。後の Issue は、表に1行足し、処理を新しいモジュールに置く。
- `runtime_dispatch.dispatch` の変更は次の5か所だけである。
  1. `try` の最初に `dispatch_repository_independent` を呼ぶ。
  2. `installation *` で、対象のworktreeの宣言が版4（`probe_workspace_mode(target.root) == "canonical"`）で、`--expect-current` があるときだけ、`CANONICAL_NOT_IMPLEMENTED` で止める。それ以外は今と同じく `install_static_assets` を呼ぶ。
  3. `workspace validate --ci` と `workspace doctor --raw` で、`probe_workspace_mode(git.root) == "canonical"` のときだけ `dispatch_canonical(namespace, resolve_context(...))` を呼ぶ。
  4. `resolve_context` の直後に、`context.mode == "canonical"` なら `dispatch_canonical`、`command.startswith("canonical ")` なら `CANONICAL_NOT_MIGRATED` とし、今の連なりの最初の `if` を `elif` にする。
  5. 例外の対応に、`CanonicalCommandError` と `GithubStructureError` を、`LookupError` より前に足す（従来の処理はこれらを出さない）。
- 版4の `installation show`、`update`、`uninstall` に `--expect-current` を付けた組み合わせの canonical の処理（選択と Scope の解決）は、I-4 の担当である（統括の判断、2026-10-26）。I-4 は、ほかのコマンドの `--expect-current` と同じ部品で解決し、上の2の止め方を外す。

### 3. エラーと次の1手（C8 の一部。`application/canonical_errors.py`）

```python
class CanonicalCommandError(Exception):
    code: str; message: str; exit_code: int; recovery: tuple[str, ...]; details: dict[str, object]

def canonical_failure(command, code, message, exit_code, recovery, details=None) -> OperationResult[DiagnosticData]
def github_error_result(command: str, error: GithubStructureError) -> OperationResult[object]
```

- canonical の処理は、書く前に止まるとき `CanonicalCommandError` を出してよい。`dispatch()` が `failed` の結果（`recovery` は `RecoveryInstructions`）にする。
- `CanonicalCommandError` の終了コードは、書く前の失敗の値（1、2、3、4、5、7）だけを受け付ける（6 は効果を持つ `partial` なので、処理が自分で結果を組み立てる）。
- コードの文字列と次の1手は、このモジュールの定数に1か所で置く（`workspace migrate` の次の1手は `MIGRATE_NOT_APPLICABLE_RECOVERY`）。`CANONICAL_NOT_LINKED` と、その次の1手 `spec-dock canonical link`（`CANONICAL_NOT_LINKED_RECOVERY`）は I-1 が置き、I-2 はそれを使う（同じコードを二重に定義しない。統括の判断 A5）。
- 構造の異常（スナップショットの `anomalies`）を Epic の12章の `GITHUB_STRUCTURE_INVALID`（終了コード7）に写すのは、対象の Scope とその祖先に異常があるときに止まる、構造を読むコマンド（I-4、I-5）である。この Issue は、異常の一覧（`StructureSnapshot.anomalies_for`）とコードだけを提供する。
- `github_error_result` は、確かな失敗（`uncertain` が偽）を `failed`（終了コード5）に、結果が分からない書き込みを `partial`（終了コード6、効果 `github.write` を `unknown`）にする。後の Issue の処理は、効果の一覧を自分で組み立てるのが原則で、これは取りこぼしたときの受け皿である。
- I-1 が使うコードと次の1手：

| コード | 終了コード | `recovery` |
|---|---|---|
| `CANONICAL_NOT_IMPLEMENTED` | 3 | `Wait for SpecDock 0.3.0, which completes canonical mode for this command; this repository declares workspace schema 4.` |
| `CANONICAL_NOT_MIGRATED` | 3 | `This repository is not migrated (workspace schema 3); follow scripts/migrate-to-canonical/README.md in SpecDock 0.3.0 to migrate it.` |
| `CANONICAL_NOT_APPLICABLE`（`workspace migrate`） | 3 | `No writer-protocol migration applies to a schema-4 workspace; nothing needs to be done.` |
| `CANONICAL_NOT_LINKED`（I-1 は `installation init` の警告にだけ使う） | 3 | `spec-dock canonical link` |
| `GITHUB_RATE_LIMITED` | 5 | `Run the same command after <時刻>.` |
| `GITHUB_UNAVAILABLE` | 5 | `Check the network connection and run gh auth status, then run the same command.` |
| `GITHUB_ACCESS_DENIED`、`GITHUB_REQUEST_REJECTED`、`GITHUB_RESPONSE_INVALID` | 5 | 対象の Issue と `gh auth status` を確かめる |
| `GITHUB_EFFECT_UNKNOWN`、`GITHUB_CREATE_IDENTITY_UNKNOWN` | 6 | GitHub の対象を確かめてから新しい操作をする（作成なら `scope import github`） |

### 4. `installation`（`application/direct_installation.py`、配布資産）

- 配布資産 `src/spec_dock/assets/spec_dock/workspace.json` を `{"schema_version":4,"writer_protocol":"specdock.worktree-writer/v1"}` にし、`static-inventory.json` の `sha256` を更新する。版3の内容の SHA-256 は `known_old_sha256` に入れ、版3のリポジトリの `installation show` が `known-old`（今の分類の名前）を示すようにする。`init_only` のままなので、`installation update` は版3の宣言を変えない。
- `installation init` の結果（`planned` と `succeeded`）の `warnings` に、`CANONICAL_NOT_LINKED`（`Run spec-dock canonical link to create or link this clone's canonical catalog.`、`details.next_step = "spec-dock canonical link"`）を入れる。
- `installation show` は宣言を `inspect_json_file` で読むだけなので、今も版4を示せる。`update` と `uninstall` は `resolve_context` と `require_writer` を通るので、`read_workspace_declaration` が版4を受け付ければ、コードを変えずに版4で動く（版4で `writer_protocol` が古い値なら、今と同じく止まる）。`HELP_PRECONDITIONS` の「schema-3」を「schema-3 or schema-4」に、`installation init` の効果を「schema-4 workspace declaration」に直す。
- **版3のリポジトリで目に見える違い**（統括の判断 C、2026-10-26）：版3の `installation show` は、宣言を `current` ではなく `known-old` と示す。配布資産の値の変化として受け入れた。ほかの版3の結果は変えない。変更の前と後で、版3の `workspace validate`、`workspace validate --ci`、`workspace doctor`、`installation update`（宣言を書き換えないこと）の結果が同じであることを、テストで確かめる（testability）。

### 5. 構造の表し方と規則（C1。`domain/canonical_structure.py`）

定数：

```python
KIND_LABELS = {"initiative": "spec-dock:initiative", "epic": "spec-dock:epic", "issue": "spec-dock:issue"}
IN_PROGRESS_LABEL = "spec-dock:in-progress"
LABEL_DEFINITIONS = (   # LabelDefinition(name, color, description)
    ("spec-dock:initiative", "5319e7", "SpecDock Initiative scope"),
    ("spec-dock:epic", "1d76db", "SpecDock Epic scope"),
    ("spec-dock:issue", "0e8a16", "SpecDock Issue scope"),
    ("spec-dock:in-progress", "fbca04", "SpecDock work in progress"),
)
ID_PREFIXES = {"initiative": "init", "epic": "epic", "issue": "iss"}
PARENT_KINDS = {"initiative": None, "epic": "initiative", "issue": "epic"}
SNAPSHOT_VERSION = 1
```

関数：

```python
def read_slug_marker(body: str | None) -> SlugMarker            # SlugMarker(slug: str | None, anomaly: str | None)
def format_slug_marker(slug: str) -> str                         # "<!-- spec-dock:slug=<slug> -->"
def append_slug_marker(body: str, slug: str) -> str              # 末尾に置く。印がすでにあれば ValueError
def kind_from_labels(labels: Iterable[str]) -> tuple[ScopeKind | None, str | None]
def scope_id(kind: ScopeKind, number: int) -> str                # format_id(ID_PREFIXES[kind], number)
def parse_scope_id(value: str) -> tuple[ScopeKind, int]          # local ID と知らない接頭辞は ValueError
def format_timestamp(value: datetime) -> str                     # "YYYY-MM-DDTHH:MM:SSZ"（UTC）
def parse_timestamp(value: str) -> datetime
```

- **印**（統括の判断 A3）：本文を `re.split(r"\r?\n")` で行に分け、各行の行末の空白を除き、`^<!-- spec-dock:slug=(.*) -->$` に合う行を数える。0行なら `SLUG_MARKER_MISSING`、2行以上なら `SLUG_MARKER_MULTIPLE`（正しい印と規則外の印が1行ずつのときも）、1行で値が `^[a-z0-9]+(?:-[a-z0-9]+)*$` に合わなければ `SLUG_MARKER_INVALID`。Epic の2章の正規表現は規則外の値の行を数えないので、規則外の slug を見つけられない。I-8 はこの規則を写す。行頭に空白がある行は印として数えない。`append_slug_marker` は、本文の末尾の改行を除き、空でなければ空行を1つはさみ、印と改行を足す。
- **種類**：ラベルのうち `KIND_LABELS` の値を数える。0なら Scope でない（`(None, None)`）。2つ以上なら `KIND_LABEL_MULTIPLE`。
- **ID**：`id` は、種類と slug がどちらも決まったときだけ作る。決まらないときは `id` と `slug` を `None` にする（Epic の2章）。

型：

```python
@dataclass(frozen=True)
class ScopeNode:      # snapshot.json の issues の1要素と同じ項目
    number: int; database_id: int; id: str | None; kind: ScopeKind | None; slug: str | None
    title: str; state: Literal["open", "closed"]; state_reason: str | None
    labels: tuple[str, ...]; assignees: tuple[str, ...]; in_progress: bool
    parent: int | None; sub_issues: tuple[int, ...]; blocked_by: tuple[int, ...]; blocking: tuple[int, ...]
    updated_at: str; url: str

@dataclass(frozen=True)
class ExternalIssue: number: int; title: str; state: Literal["open", "closed"]
@dataclass(frozen=True)
class StructureAnomaly: number: int; code: str; message: str
@dataclass(frozen=True)
class LocalWrite: at: str; command: str; numbers: tuple[int, ...]

@dataclass(frozen=True)
class StructureSnapshot:
    repository: str                        # "github.com/<owner>/<repo>"（小文字）
    fetched_at: str; fetch_started_at: str
    issues: Mapping[int, ScopeNode]        # 種類のラベルを持つすべての Issue（異常のものを含む）
    external: Mapping[int, ExternalIssue]
    anomalies: tuple[StructureAnomaly, ...]
    local_writes: tuple[LocalWrite, ...]
    @property scopes -> tuple[ScopeNode, ...]          # id が決まったもの（番号の昇順）
    def find(self, scope_id: str) -> ScopeNode | None  # id で探す
    def anomalies_for(self, number: int) -> tuple[StructureAnomaly, ...]
    def to_json(self) -> dict[str, object]
    @classmethod
    def from_json(cls, payload: object) -> StructureSnapshot   # 版が1でない、形が違うときは SnapshotFormatError
```

- 項目の出どころ：

| 項目 | GraphQL | REST（Issue の取得、作成、更新） |
|---|---|---|
| `number` | `number` | `number` |
| `database_id` | `databaseId` | `id` |
| `title`、`body` | `title`、`body` | `title`、`body` |
| `state`、`state_reason` | `state`、`stateReason`（小文字にする） | `state`、`state_reason` |
| `labels`、`assignees` | `labels.nodes[].name`、`assignees.nodes[].login` | `labels[].name`、`assignees[].login` |
| `updated_at` | `updatedAt` | `updated_at` |
| `url` | `url` | `html_url`（REST の `url` は API の URL なので使わない） |
| 関係の `repository` | `repository.nameWithOwner` | `repository_url` の `repos/` の後 |

- `labels` と `assignees` は、REST と GraphQL で並びが違わないよう、名前の昇順にそろえる。`sub_issues` は GitHub の並び、`blocked_by` と `blocking` は番号の昇順。`state` と `state_reason` は REST の値（小文字。GraphQL の `COMPLETED` は `completed`、`NOT_PLANNED` は `not_planned`）。`in_progress` は `IN_PROGRESS_LABEL` があるかどうか。
- `to_json` は、Epic の2章の `snapshot.json` の版1の形を、キーを番号の昇順にそろえて返す。本文は持たない。

読み取りの入力と組み立て：

```python
@dataclass(frozen=True)
class IssueFacts:      # 1つの Issue の事実（GraphQL か REST）
    number: int; database_id: int; title: str; body: str | None; state: str; state_reason: str | None
    labels: tuple[str, ...]; assignees: tuple[str, ...]; updated_at: str; url: str
@dataclass(frozen=True)
class RelatedIssue:    # 親、子、依存先。repository は "<owner>/<repo>"（小文字）
    number: int; repository: str; title: str | None = None; state: str | None = None
@dataclass(frozen=True)
class FetchedIssue:
    facts: IssueFacts; parent: RelatedIssue | None; sub_issues: tuple[RelatedIssue, ...]; blocked_by: tuple[RelatedIssue, ...]

def build_snapshot(repository: str, issues: Iterable[FetchedIssue], *, fetched_at: str, fetch_started_at: str) -> StructureSnapshot
```

- **異常のコード**（`StructureAnomaly.code`。1つの Issue に複数あってよい）：

| コード | 判定 | 種類 |
|---|---|---|
| `KIND_LABEL_MULTIPLE` | 種類のラベルが2つ以上 | 要素 |
| `SLUG_MARKER_MISSING`、`SLUG_MARKER_MULTIPLE`、`SLUG_MARKER_INVALID` | 印の規則（上） | 要素 |
| `PARENT_FOREIGN_REPOSITORY` | 親が別のリポジトリの Issue（`parent` は `None` にする） | 要素 |
| `SUB_ISSUE_FOREIGN_REPOSITORY` | 子に別のリポジトリの Issue がある（`sub_issues` には入れない） | 要素 |
| `DEPENDENCY_FOREIGN_REPOSITORY` | 依存先に別のリポジトリの Issue がある（`blocked_by` にも `external` にも入れない） | 要素 |
| `PARENT_MISSING` | Epic か Issue に親がない（`PARENT_FOREIGN_REPOSITORY` のときは出さない） | 構造 |
| `PARENT_INVALID` | Initiative に親がある。親が Scope でない、異常で `id` がない、親の種類が規則（Epic の親は Initiative、Issue の親は Epic）に合わない | 構造 |
| `DEPENDENCY_INVALID` | 自分自身、祖先、子孫への依存 | 構造 |
| `DEPENDENCY_CYCLE` | 継いだ依存を含めた循環。循環に入る Issue ごとに1つ | 構造 |

  「要素」の異常は、その Issue の事実だけで決まり、要素と一緒に持ち運ぶ（書き込みの反映と取り直しの重ね合わせで使う）。「構造」の異常は、`issues` の全体から、組み立てるたびに求め直す。
- **別のリポジトリの Issue**（統括の判断、2026-10-26）：親、子、依存先のうち別のリポジトリのものは、`parent`、`sub_issues`、`blocked_by`、`blocking`、`external` のどれにも入れず、上の `*_FOREIGN_REPOSITORY` の異常（メッセージに `<owner>/<repo>#<番号>`）として記録する。子の異常 `SUB_ISSUE_FOREIGN_REPOSITORY` は、親の側から見た同じ扱いで、完了の判定（子孫が完了しているか）で別のリポジトリの子を見落とさないために足した。これらの異常を持つ Scope を、読む側（I-4 の着手の判定、I-11 のダッシュボード）は「着手できる」にしない（ダッシュボードでは UNKNOWN）。`SetParent` で親を付け直すと、子の `PARENT_FOREIGN_REPOSITORY` は消える。
- **循環**：祖先の鎖に異常のない Scope を節にし、`id` を持つ依存先への辺から、`DEPENDENCY_INVALID` の辺を除き、今の `domain/dependency_vnext.validate_dependency_graph` で確かめる（節は `id` と `parent_id` だけを持つ小さな値で、型は `cast` で合わせる）。`ValueError` なら、`dependency_listing` の `effective` の辺と親から子への辺の強連結成分を求め、2つ以上の節を持つ成分の各 Issue に `DEPENDENCY_CYCLE` を付ける。
- `id` のない依存先（異常の Scope）への辺は、循環の確かめに入れない。`blocked_by` には残る。そのような依存を持つ Scope を、着手の判定（I-4）とダッシュボード（I-11）は「着手できる」にしない（統括の判断 A4）。
- `blocked_by` の辺のうち `DEPENDENCY_INVALID` のものも、GitHub にあるので `blocked_by` と `blocking` に残す。
- **`external`**：Scope でない（種類のラベルのない）同じリポジトリの依存先を、`number`、`title`、`state` で持つ。どの `blocked_by` からも参照されなくなったものは消す。

書き込みの反映：

```python
@dataclass(frozen=True)
class UpsertIssue: facts: IssueFacts                                   # 作成、題名、状態、ラベル、担当者の変更、読み直し
@dataclass(frozen=True)
class SetParent: child: int; parent: int | None                        # 親子を付ける、付け替える、外す
@dataclass(frozen=True)
class AddBlockedBy: number: int; blocker: int; external: ExternalIssue | None = None
@dataclass(frozen=True)
class RemoveBlockedBy: number: int; blocker: int
StructureChange = UpsertIssue | SetParent | AddBlockedBy | RemoveBlockedBy

def apply_changes(snapshot, changes, *, at: str, command: str) -> StructureSnapshot
def merge_refresh(current: StructureSnapshot | None, fresh: StructureSnapshot) -> StructureSnapshot
def element_anomalies(snapshot: StructureSnapshot, number: int) -> tuple[StructureAnomaly, ...]
def dependency_violations(snapshot: StructureSnapshot, number: int, blocker: int) -> tuple[StructureAnomaly, ...]
```

- `UpsertIssue` は、事実から要素の項目（題名、状態、ラベル、担当者、slug、id、作業中）と、事実から決まる異常（種類と印）を作り直し、親子、依存、関係から決まる異常（`*_FOREIGN_REPOSITORY`）は今の値を残す。
  - 種類のラベルのある事実で、新しい番号なら、親子と依存が空の要素を足す（親子と依存は、続けて `SetParent` と `AddBlockedBy` で反映する）。
  - 種類のラベルのない事実（Scope でない Issue の読み直しや、種類のラベルを外した後）は、`issues` に足さない。`issues` にあれば除く。`external` には、その番号の題名と状態を入れるが、どの `blocked_by` からも参照されていなければ、組み立ての最後に消える。そのため、`work start` が Scope でない依存先を読み直すと、`external` の題名と状態だけが新しくなる。
- `SetParent` は、子の `parent` を変え、前の親の `sub_issues` から除き、新しい親の `sub_issues` の末尾に足す。子の `PARENT_FOREIGN_REPOSITORY` を消す。
- `AddBlockedBy` は `blocked_by` に足し（番号の昇順）、相手が Scope でなければ `external` に `ExternalIssue` を入れる。`RemoveBlockedBy` は外す。
- `apply_changes` は、変更を順に当て、`blocking`、`external`、構造の異常を求め直し、`LocalWrite(at, command, 変えた番号の昇順)` を `local_writes` の末尾に足す。変えた番号には、`SetParent` の前の親と新しい親、依存の両端を含める（取り直しの重ね合わせで、関係の両端を同じ側から取るため）。
- `dependency_violations` は、`AddBlockedBy(number, blocker)` を当てた仮のスナップショットで、新しく出る `DEPENDENCY_INVALID` と `DEPENDENCY_CYCLE` を返す。`dependency add`（I-5）が、書く前に循環と規則の違反を確かめるのに使う。
- `merge_refresh` は、取り直したスナップショット `fresh` に、`current.local_writes` のうち `at >= fresh.fetch_started_at` のものを重ねる。それらの番号の要素、要素の異常、`external` の要素は、書き込みを反映した後の `current` の値を使い（`current` にない番号は `fresh` から除く）、`local_writes` はそれらだけを残し、`blocking`、`external`、構造の異常を求め直す。これが Epic の「書き込みの変更を重ねる」の具体である。秒の単位の時刻なので、同じ秒の書き込みも残す（`>=`）。

### 6. GitHub の呼び出しの部品（C1。`infra/github_structure.py`）

```python
@dataclass(frozen=True)
class GithubRepository:
    owner: str; name: str; host: str = "github.com"     # 小文字、[a-z0-9_.-]、"." と ".." を除く
    @property slug -> "owner/name"; @property key -> "github.com/owner/name"
    @classmethod parse(cls, value: str) -> GithubRepository   # "owner/name" か "github.com/owner/name"

class GithubStructureError(RuntimeError):
    code: str; message: str; uncertain: bool; status: int | None; retry_at: str | None; endpoint: str | None
    @property exit_code -> 6 if uncertain else 5

class GithubClock(Protocol):
    def monotonic(self) -> float
    def sleep(self, seconds: float) -> None
    def now(self) -> datetime        # UTC
SYSTEM_CLOCK: GithubClock

@dataclass(frozen=True)
class GithubResponse: status: int; headers: Mapping[str, str]; body: object | None   # ヘッダーの名前は小文字

class GithubApi:
    def __init__(self, *, runner=subprocess.run, clock: GithubClock = SYSTEM_CLOCK, timeout: float = 30.0, cwd: Path | None = None)
    def request(self, method, endpoint, *, payload=None, ok=frozenset({200}), headers=None, write=None) -> GithubResponse
    clock: GithubClock

def repository_for_checkout(root: Path, *, timeout: float) -> GithubRepository   # origin の URL から（github_remote を使う）
```

- `gh api --hostname github.com --include --method <M> <endpoint>` で呼ぶ。エンドポイントの中のラベルの名前（`labels=` の値と、`labels/{name}` の部分）は、`urllib.parse.quote(name, safe="")` で符号化する（`spec-dock:epic` は `spec-dock%3Aepic`）。本文があれば `--input -` で標準入力から JSON（数値と配列を含む）を送る。ヘッダーは `-H "<名前>: <値>"`。GraphQL は `--method POST graphql --input -` に `{"query": …, "variables": …}` を送る。
- 応答は、`\r\n` を `\n` にそろえ、最初の空行で状態行とヘッダーと本文に分ける。**状態コードは状態行だけで決め、`gh` の終了コードは使わない**（304 の `gh` は終了コード1を返すため）。状態行がない応答は、読み取りなら `GITHUB_UNAVAILABLE`、書き込みなら結果が不明（`GITHUB_EFFECT_UNKNOWN`）。
- `ok` に入る状態コードは正常な答えとして返す（例：親の取得は `{200, 404}`、確かめは `{200, 304}`）。それ以外は次のように扱う。

| 応答 | 読み取り（GET と GraphQL） | 書き込み |
|---|---|---|
| レート制限（403 か 429 で、`retry-after`、`x-ratelimit-remaining: 0`、本文に `rate limit`。GraphQL の `errors[].type == "RATE_LIMITED"` も） | 待ち = `retry-after` 秒、なければ（`x-ratelimit-remaining: 0` のときだけ）`x-ratelimit-reset` までの秒、どちらもなければ60秒（GitHub の文書の手順）。待ちが60秒以下なら待って再試行（3回まで）。60秒を超えるか、3回を超えたら `GITHUB_RATE_LIMITED`（`retry_at` に時刻） | 再試行せず `GITHUB_RATE_LIMITED`（効果なし） |
| 500番台 | 1秒、2秒、4秒の間をおいて3回まで再試行し、続けば `GITHUB_UNAVAILABLE` | 結果が不明（`uncertain`） |
| 401、403、404（`ok` にないとき） | `GITHUB_ACCESS_DENIED` | 同じ |
| 400、410、422 | `GITHUB_REQUEST_REJECTED` | 同じ |
| `gh` がない、起動できない | `GITHUB_UNAVAILABLE` | 同じ（送っていない） |
| 時間切れ、そのほかの OS の失敗 | `GITHUB_UNAVAILABLE` | 結果が不明 |
| 本文が JSON でない、形が違う | `GITHUB_RESPONSE_INVALID` | 結果が不明（2xx の書き込みでも本文が読めなければ、読み直しで確かめる） |

- `gh` の入出力は UTF-8 で読み書きする（`encoding="utf-8"`。利用者のロケールに依らず日本語の題名を扱うため）。
- 呼び出しは同期で1つずつ行う（スレッドを使わない）。`GithubApi` の1つの実体を、1つのコマンドの中で使い回す。
- 書き込みの前に、前の書き込みが終わってからの経過（`clock.monotonic()`）が1秒より短ければ、足りない分だけ `clock.sleep` で待つ。
- `GithubStructureClient.graphql` は読み取りの問い合わせだけを送る（読み取りとして再試行するので、`mutation` は `ValueError` で拒む）。`errors` があれば、レート制限なら上の扱い、`NOT_FOUND` なら `GITHUB_ACCESS_DENIED`、それ以外は `GITHUB_REQUEST_REJECTED`。`rateLimit.cost` は `GithubStructureClient.last_graphql_cost` に残す（I-3 がログに書く）。

```python
class GithubStructureClient:
    def __init__(self, repository: GithubRepository, api: GithubApi)
    last_graphql_cost: int | None                                         # 最後の全体の読み取りの rateLimit.cost の合計
    # 読み取り
    def fetch_structure(self) -> tuple[FetchedIssue, ...]
    def graphql(self, query: str, variables: Mapping[str, object]) -> dict[str, object]
    def probe(self, etags: Mapping[str, str | None]) -> ProbeResult       # ProbeResult(changed, etags, statuses)
    def get_issue(self, number: int) -> IssueFacts
    def get_parent(self, number: int) -> RelatedIssue | None              # 404 は None
    def list_sub_issues(self, number: int) -> tuple[RelatedIssue, ...]
    def list_blocked_by(self, number: int) -> tuple[RelatedIssue, ...]
    def list_labels(self, number: int) -> tuple[str, ...]
    def label_exists(self, name: str) -> bool                             # 404 は False
    def current_login(self) -> str
    # 書き込み
    def create_issue(self, *, title: str, body: str, labels: Sequence[str]) -> IssueFacts
    def update_issue(self, number: int, *, title=None, state=None, state_reason=None) -> IssueFacts
    def add_sub_issue(self, parent: int, *, child: int, child_id: int, replace_parent: bool = False) -> None
    def remove_sub_issue(self, parent: int, *, child: int, child_id: int) -> None
    def add_blocked_by(self, number: int, *, blocker: int, blocker_id: int) -> None
    def remove_blocked_by(self, number: int, *, blocker: int, blocker_id: int) -> None
    def create_label(self, definition: LabelDefinition) -> None           # 422 の already_exists は成功
    def add_labels(self, number: int, labels: Sequence[str]) -> tuple[str, ...]
    def remove_label(self, number: int, name: str) -> None                # 404 は、読み直してラベルがなければ成功
    def add_assignees(self, number: int, logins: Sequence[str]) -> None
```

- **全体の読み取り**：Epic の2章の問い合わせを、次の3点だけ変えて使う（統括の判断、2026-10-26。`snapshot.json` の版1の形は変えない）。
  1. `blockedBy` の要素の `labels(first: 20)` を外す。外さないと、1ページの費用が104点になる（2026-10-26 に、本物の GitHub で読むだけの問い合わせで測った。外すと4点）。依存先が Scope かどうかは、`issues`（開いたものも閉じたものも含む）にあるかで決める。Scope でないものは `external` に題名と状態を入れる。
  2. `parent`、`subIssues`、`blockedBy` の要素に `repository { nameWithOwner }` を足す。sub-issue と blocked by は別のリポジトリの Issue を指せるので、番号だけでは取り違える。費用は変わらない。別のリポジトリのものの扱いは5章。
  3. `labels(first: 20)` に `totalCount` を足し、20を超える Issue だけ、REST の `GET …/issues/{n}/labels?per_page=100` で読み直す（種類のラベルを見落とさないため）。
  - `subIssues.totalCount` か `blockedBy.totalCount` が、返った要素の数より多い Issue だけ、REST の一覧（`per_page=100` と `page`）で残りを読む。これらの読み直しも、1つずつ順に送る。
  - 使う問い合わせ（`$after` でページ送り）：

    ```graphql
    query($owner: String!, $name: String!, $after: String) {
      rateLimit { cost remaining resetAt }
      repository(owner: $owner, name: $name) {
        issues(first: 100, after: $after, states: [OPEN, CLOSED],
               labels: ["spec-dock:initiative", "spec-dock:epic", "spec-dock:issue"]) {
          pageInfo { hasNextPage endCursor }
          nodes {
            number databaseId title body state stateReason updatedAt url
            labels(first: 20) { totalCount nodes { name } }
            assignees(first: 10) { nodes { login } }
            parent { number repository { nameWithOwner } }
            subIssues(first: 100) { totalCount nodes { number repository { nameWithOwner } } }
            blockedBy(first: 100) { totalCount nodes { number title state repository { nameWithOwner } } }
          }
        }
      }
    }
    ```
- **確かめ**：`GET /repos/{o}/{r}/issues?labels=<種類のラベル>&state=all&sort=updated&direction=desc&per_page=1` を、ラベルごとに、記録した `ETag` があれば `If-None-Match` を付けて送る（`ok={200, 304}`）。1つでも 200 なら `changed`。応答の `ETag` を新しい値として返す（304 で `ETag` がなければ前の値）。
- `sub_issue_id`、`issue_id`、`DELETE …/blocked_by/{id}` には、引数の `child_id`、`blocker_id`（Issue の id）を使う。番号の引数は、結果を確かめる読み直しにだけ使う。
- **結果の確かめ**：結果が不明な書き込み（2xx でも本文が読めないものを含む）は、すぐに読み直す。外す操作の404は、読み直して関係がなければ成功とする（`remove_sub_issue` は、子の Issue が読めることを先に確かめる。読めなければ `GITHUB_ACCESS_DENIED`）。題名と状態は `GET issue`、親子は `GET …/parent`、依存は `GET …/blocked_by`、ラベルと担当者は `GET issue` で確かめ、望んだ状態なら成功として返す。違う、または読めなければ `GITHUB_EFFECT_UNKNOWN`（`uncertain`）。作成は確かめられないので `GITHUB_CREATE_IDENTITY_UNKNOWN`（`uncertain`）。
- その Issue 自身を返す操作（`get_issue`、`create_issue`、`update_issue`）の応答は、PRの Issue（`pull_request` がある）と、`repository_url` が別のリポジトリのものを拒む（`GITHUB_RESPONSE_INVALID`）。関係の読み取り（`get_parent`、`list_sub_issues`、`list_blocked_by`、全体の読み取りの続き）は、別のリポジトリの Issue を拒まず、`RelatedIssue.repository` に入れて返す（扱いは5章の「別のリポジトリの Issue」）。

### 7. 構造のスナップショット（C10。`infra/github_snapshot.py`、`infra/state_root.py`）

```python
def resolve_state_root(environ: Mapping[str, str] | None = None, *, override: Path | None = None) -> Path   # infra/state_root.py
    # override（I-3 の --state-root の値。絶対パスでなければ ValueError）があればそれを、なければ
    # ${XDG_STATE_HOME:-$HOME/.local/state}/spec-dock。XDG_STATE_HOME が絶対パスでなければ使わない

FreshnessLevel = Literal["display", "decision", "cycle"]
PROBE_INTERVAL = timedelta(seconds=60)
MAX_AGE = {"display": timedelta(minutes=30), "decision": timedelta(minutes=5), "cycle": timedelta(minutes=30)}

@dataclass(frozen=True)
class ProbeRecord:
    checked_at: str | None; etags: Mapping[str, str | None]; last_error: Mapping[str, str] | None
    def to_json(self) -> dict[str, object]; @classmethod from_json(cls, payload) -> ProbeRecord

class SnapshotStore:
    def __init__(self, state_root: Path, repository: GithubRepository, *, lock_timeout: float = 10.0)
    directory: Path                                   # <根>/github/<host>/<owner>/<repo>
    def load(self) -> tuple[StructureSnapshot | None, ProbeRecord | None]       # 例外を出さない
    def commit_refresh(self, fresh: StructureSnapshot, probe: ProbeRecord) -> StructureSnapshot
    def save_probe(self, probe: ProbeRecord) -> None                    # 排他の中の記録の checked_at が新しければ書かない
    def record_probe_error(self, error: Mapping[str, str]) -> None     # 排他の中の記録に last_error だけを重ねる
    def reflect(self, changes, *, command: str, at: str) -> StructureSnapshot | None
    persisted: bool                                   # 最後の書き込みがファイルに届いたか

@dataclass(frozen=True)
class SnapshotWarning: code: str; message: str; details: Mapping[str, object]

@dataclass(frozen=True)
class FreshSnapshot:
    snapshot: StructureSnapshot | None   # cycle で一度も取れていないときだけ None
    stale: bool
    probe: Literal["unchanged", "changed", "skipped", "failed"]
    refreshed: bool
    warning: SnapshotWarning | None      # display の GITHUB_SNAPSHOT_STALE
    graphql_cost: int | None             # 取り直したときの rateLimit.cost（I-3 がログに書く）
    def require(self) -> StructureSnapshot   # snapshot がなければ GITHUB_UNAVAILABLE
    def payload(self) -> dict[str, object]   # {"fetched_at": …, "stale": …}（12章の data.snapshot）

class StructureSnapshotService:
    def __init__(self, repository: GithubRepository, *, store: SnapshotStore, client: GithubStructureClient, clock: GithubClock)
    def ensure_fresh(self, level: FreshnessLevel) -> FreshSnapshot
    def refresh(self) -> FreshSnapshot                                    # --source github：確かめを待たずに取り直す
    def reread(self, numbers: Iterable[int], *, command: str) -> StructureSnapshot   # decision の読み直し
    def reflect(self, changes: Sequence[StructureChange], *, command: str) -> StructureSnapshot | None

def ensure_fresh(repository: GithubRepository, level: FreshnessLevel, *, state_root: Path | None = None,
                 api: GithubApi | None = None) -> FreshSnapshot              # 既定の部品で組み立てる入口
```

- **状態の置き場の根**（統括の判断 A6）：根の求め方の持ち主は I-1 で、登録簿、`state.json`、`--state-root` は I-3 のままである。`canonical link` が求めて定期の実行の引数に書いた値を `override` に渡すと、同じ根になる（テストで確かめる）。
- **置き場**：`SnapshotStore.directory` に `snapshot.json` と `probe.json`。足りないディレクトリを作るとき、最後の `<repo>` のディレクトリは `0o700` にする（途中のディレクトリと、すでにある状態の置き場の根は、利用者の umask と今の権限のまま）。2つのファイルは `0o600` で作る（題名と担当者のログイン名を持つため）。
- **書き方**：ディレクトリを読み取りで開いて `flock(LOCK_EX)` を取り（`LOCK_NB` を50ミリ秒ごとに試し、`lock_timeout` 秒まで。`lock_timeout` は0〜300秒の有限の値）、その中で、今のファイルを読み直して変更を1回だけ当て、ファイルの中身と変わったものだけを、同じディレクトリの一時ファイル `.<名前>.<乱数>.tmp` に書いて `fsync` し、`os.replace` で置き、ディレクトリを `fsync` する。304 だけの確かめでは `probe.json` だけを書き、`snapshot.json` は置き換えない。読むときは排他を取らない。
- **読み方**：`snapshot.json` と `probe.json` を読み、`from_json` が失敗したもの（壊れている、版が違う）は「ない」とする。
- **メモリー**：書き込み（ディレクトリの作成、排他、一時ファイル、`rename`）が `OSError` で失敗したら（排他が `lock_timeout` 秒で取れないときを含む）、そのプロセスの中の表（`directory` をキーにする）に、書こうとした値を置き、`persisted` を偽にする。ファイルに書けたら、表のその要素を消す（メモリーの値がファイルより新しければ、そのときにファイルへ書く）。2つ目のファイルの書き込みで失敗したときは、排他の中で計算した値をそのままメモリーに置く（変更を2回当てない）。`load` は、ファイルとメモリーのうち `fetched_at` が新しい方を返し、同じならメモリーを返す（メモリーは書けなかった後にだけあり、`reflect` は `fetched_at` を変えないため）。`probe.json` は `checked_at` で同じように選ぶ。`clear_memory()` はテスト用である。
- **取り直しの書き込み**：`commit_refresh` は、排他の中のスナップショットの `fetch_started_at` が、書こうとする取り直しのものより新しければ、何も書かずに今のものを返す（並んで走った古い取り直しが、新しいものと `ETag` を戻さないため）。
- **`ensure_fresh(level)` と `refresh()`**（時刻は `clock.now()`）：`load()` で今のスナップショットと確かめの記録を得てから、次の表で決める。「確かめ」は種類のラベルごとの3回の条件付きの要求、「取り直し」は GraphQL の全体の読み取り（とその続きの REST）である。取り直すときは、`ETag` を得るため、いつも先に確かめる。

| 段階 | 状況 | 送る要求 | `probe.json` に残すもの | 結果 |
|---|---|---|---|---|
| `display` | 最後の確かめから60秒以内で、`fetched_at` から30分以内 | なし | 変えない | `probe="skipped"` |
| `display`、`cycle` | 確かめが要り（`display` は60秒を超えた、`cycle` はいつも）、304が3つで、30分以内 | 確かめだけ | `checked_at` を進める。`ETag` は同じ | `probe="unchanged"` |
| `decision` | いつも確かめる。304が3つで、5分以内 | 確かめだけ | 同じ | `probe="unchanged"` |
| どれも | 200 が1つでもある（変化あり） | 確かめと取り直し | 取り直しが成功したら、新しい `ETag`、`checked_at`、`last_error=null` | `probe="changed"`、`refreshed=True` |
| どれも | スナップショットがない、版が違う、壊れている、`MAX_AGE[level]`（30分、5分、30分）を超えた | 確かめと取り直し | 同じ | `probe` は確かめの結果、`refreshed=True` |
| `refresh()` | いつも（`--source github`） | 確かめと取り直し | 同じ | `refreshed=True` |
| どれも | 確かめか取り直しで GitHub の失敗 | 失敗したところまで | `ETag` と `checked_at` は変えず、`last_error`（`code`、`message`、`at`）だけ | 下の「失敗」 |

  - 境は「超えた」で判定する（60秒ちょうど、30分ちょうど、5分ちょうどは、まだ超えていない）。
  - 取り直しは、始めた時刻を `fetch_started_at`、終えた時刻を `fetched_at` とし、`build_snapshot` で作り、`commit_refresh` で書く（`merge_refresh` で書き込みの反映を重ねる）。
  - 組み立てで GitHub の値が規則外（知らない状態、同じ番号が2回など）とわかったときは、`GITHUB_RESPONSE_INVALID` の失敗として下の「失敗」と同じに扱う（`reread` も同じ）。
  - 失敗の記録は `record_probe_error` で、排他の中の最新の `ETag` と `checked_at` を残し、`last_error` だけを書く（並んで走った別のプロセスの記録を巻き戻さない）。
  - **失敗**：`display` でスナップショットがあれば、`stale=True`、`probe="failed"`、警告 `GITHUB_SNAPSHOT_STALE`（`details.fetched_at` と `details.cause`）で返す（レート制限も同じ。統括の判断 A2）。`display` でスナップショットがないとき、`decision`、`refresh()` は、元の `GithubStructureError` をそのまま出す（コードは、つながらないなら `GITHUB_UNAVAILABLE`、制限なら `GITHUB_RATE_LIMITED`、権限なら `GITHUB_ACCESS_DENIED` など。統括の判断 A7）。`cycle` は例外を出さず、`stale=True`、`probe="failed"` で返す（スナップショットがなければ `snapshot=None`）。
- **`reread(numbers)`**：番号ごとに `get_issue` を読み、`UpsertIssue` の変更として `reflect(command=f"{command} (reread)")` する。読み直しの結果がスナップショットと同じでも記録する（判断に使った値を、並んで走る取り直しから守るため）。Scope でない Issue を読み直すと、`external` の題名と状態だけが新しくなる（5章）。読めなければ、元の `GithubStructureError` を出す。
- **`reflect(changes)`**：排他の中で今のスナップショットに `apply_changes` を当てて書く。スナップショットがなければ何もせず `None` を返す（書く判断の前に `ensure_fresh("decision")` があるので、ふつうは起きない）。
- **書いてよいもの**：表示だけのコマンドがこの部品を使っても、書くのは `snapshot.json`、`probe.json`、そのディレクトリ、その一時ファイルだけである。

## data / failure

### `snapshot.json`（版1）

Epic の `design.md` 2章の形のとおり。`anomalies` は `{"number", "code", "message"}`、`local_writes` は `{"at", "command", "numbers"}`。キーの並びは番号の昇順、`anomalies` は `(number, code)` の昇順。

### `probe.json`（版1）

```json
{"version": 1, "checked_at": "2026-10-26T12:00:00Z",
 "etags": {"spec-dock:initiative": "W/\"…\"", "spec-dock:epic": "W/\"…\"", "spec-dock:issue": null},
 "last_error": {"code": "GITHUB_UNAVAILABLE", "message": "…", "at": "2026-10-26T12:01:00Z"}}
```

### 失敗の扱い

| 出来事 | 扱い |
|---|---|
| 宣言が版5、真偽値、文字列、壊れている | `PRECONDITION_FAILED`（今と同じ。文言だけ「schema 3 or 4」に変わる） |
| 版4で、canonical の処理がないコマンド | `CANONICAL_NOT_IMPLEMENTED`（3）。何も読まず、何も書かない |
| 版4の `workspace migrate` | `CANONICAL_NOT_APPLICABLE`（3）。宣言を読むだけ |
| 版3の `canonical …` | `CANONICAL_NOT_MIGRATED`（3） |
| GitHub の失敗 | 6章の表。`ensure_fresh` は7章の手順7 |
| 状態の置き場の失敗 | 書けなければメモリー、読めなければ「ない」。コマンドは失敗しない |
| 取り直しの途中の書き込みの反映 | `merge_refresh` が残す |

## 変更対象

| 置き場 | 変更 |
|---|---|
| `src/spec_dock/runtime/application/project_context.py` | 版3と4の受け付け、`WorkspaceMode`、`workspace_mode`、`probe_workspace_mode`、`ProjectContext.mode` |
| `src/spec_dock/runtime/commands/runtime_dispatch.py` | 2章の5か所 |
| `src/spec_dock/runtime/commands/canonical_dispatch.py`（新） | 振り分けの表と入口 |
| `src/spec_dock/runtime/application/canonical_errors.py`（新） | `CanonicalCommandError`、結果の組み立て、I-1 のコード |
| `src/spec_dock/runtime/application/canonical_refusals.py`（新） | `workspace migrate` の拒否（I-4 が拒否を足す置き場） |
| `src/spec_dock/runtime/application/direct_installation.py` | `installation init` の警告 |
| `src/spec_dock/runtime/cli/catalog.py` | `installation` の `HELP_EFFECTS` と `HELP_PRECONDITIONS` の文言 |
| `src/spec_dock/runtime/domain/canonical_structure.py`（新） | 5章 |
| `src/spec_dock/runtime/infra/github_structure.py`（新） | 6章 |
| `src/spec_dock/runtime/infra/github_snapshot.py`（新）、`infra/state_root.py`（新） | 7章 |
| `src/spec_dock/assets/spec_dock/workspace.json`、`src/spec_dock/assets/static-inventory.json` | 版4と、ハッシュ |
| `tests/support/`（新）、`tests/unit/{domain,infra,commands}/`、`tests/cli_runtime/` | 偽の GitHub と、この Issue のテスト |

変えないもの：従来の処理の関数（`application/direct_installation.py` を除く `application/direct_*.py`、`scope_query.py`、`start_snapshot.py`、`work_start.py` など）、`.meta.json` を読み書きするコード、`infra/github_lifecycle.py`、`domain/dependency_vnext.py`、テンプレート、利用側の `spec-dock/` の配布資産（I-9 で更新する）。

## 移行・互換性・rollback

- **版3のリポジトリ**：`dispatch()` は、`resolve_context` の後に `mode == "legacy"` の枝で今の連なりをそのまま通る。`workspace validate --ci` と `--raw` は、宣言が版4と読めないかぎり今の経路を通る。`installation show` は、版3の宣言を `known-old` と示す（配布資産が版4になったため。`init_only` なので `update` は書き換えない）。
- **版4のリポジトリ**：この Issue の後も、`installation` と `workspace migrate` 以外は `CANONICAL_NOT_IMPLEMENTED` で止まる。版4のリポジトリは、I-10 まで本物には存在しない（`installation init` で新しく作ったものだけ）。
- **0.2.4 との組み合わせ**：0.2.4 は版4の宣言を読むと止まる（今のコード）。
- **rollback**：PRを `git revert` すれば戻る。状態の置き場のファイルは、版3のリポジトリでは作られない。テストで作ったものは一時ディレクトリにある。

## testability

### 偽の GitHub（`tests/support/fake_github.py`。後の Issue も使う）

```python
fake = FakeGithub("example/repo")                         # 番号と id は別の値（id = 1_000_000 + 番号 × 7）
init = fake.scope("initiative", slug="plan", title="計画")  # 種類のラベルと印を持つ Issue を足す
epic = fake.scope("epic", slug="core", parent=init.number)
other = fake.add_issue(title="外の Issue")                  # Scope でない Issue
fake.block(epic.number, by=other.number)                    # blocked by
fake.add_foreign_issue("other/repo", 5)                     # 別のリポジトリの Issue（親、子、依存先に使う）
fake.inject(status=403, headers={"retry-after": "5"}, body={"message": "secondary rate limit"}, method="GET")
api = GithubApi(runner=fake, clock=fake.clock)              # 同じ実体が実行器と時計になる
...
fake.requests            # [FakeRequest(method, endpoint, payload, headers, status, at, when)]
fake.metered_requests()  # 主のレート制限を消費する要求（304 以外）
fake.writes()            # 書き込みの要求
fake.graphql_requests()  # GraphQL の要求
handle = install_fake_gh(tmp_path, monkeypatch, fake)       # PATH の先頭に gh を置く（CLI のテスト用）
handle.load()            # 実行ファイルが書き戻したモデルと要求の記録を読む
```

- 偽物は、Epic の `design.md` 2章の REST の操作と GraphQL の問い合わせ（問い合わせの文字列の `labels: [...]` を OR で絞り、`first` と `after` でページ送り）に答える。`relation_limit`（既定100）と `label_limit`（既定20）を小さくすると、`totalCount` の超過と REST での残りの読み取りを試せる。
- 条件付きの要求は、一覧の本文の SHA-256 から `ETag`（`W/"…"`）を作り、`If-None-Match` と同じなら、本物の `gh` と同じく、終了コード1と状態行 `HTTP/2.0 304 Not Modified` を返す。
- `sub_issue_id` と `issue_id` は id として探し、番号を送ると404を返す。
- `fake.clock` は `GithubClock` で、`sleep` は待たずに時刻を進める。要求の時刻（`at`）を記録するので、書き込みの間を確かめられる。`inject(..., timeout=True)` は、実行器の中で `subprocess.TimeoutExpired` を出す。
- 状態の置き場は、テストでいつも `tmp_path` に置く（`resolve_state_root({"XDG_STATE_HOME": …})` か `SnapshotStore(tmp_path, …)`）。`monkeypatch.setenv("XDG_STATE_HOME", …)` は CLI のテストで使う。
- `relation_updates_timestamp`（既定は偽）は、親子と依存の変更で Issue の `updated_at` が変わるかを選ぶ。本物の動きは未確認（Epic の「未確認の事項」）なので、既定は見落とす側にして、30分ごとの取り直しを試せるようにする。

### 従来モードの回帰で変えるテスト（統括の判断、2026-10-26）

`installation init` が版4の宣言を書くことに伴い、次の4件だけを変える。どれも確かめる中身（`assert`）は変えないか、「配布資産の値」の許された変更である。変えた行と理由は `report.md` に一覧で書く。

| テスト | 変えること |
|---|---|
| `tests/cli_runtime/test_issue413_work_start.py::test_start_accepts_the_standard_rule_documents_created_by_scope_import` | `installation init` の直後に、宣言を版3に戻す準備の行を足す |
| `tests/integration/test_issue413_assets.py::test_init_places_only_static_assets_and_a_new_declaration_in_the_explicit_worktree` | 宣言の値を版4に。init の直後の `workspace validate` を、版4が canonical に送られ `CANONICAL_NOT_IMPLEMENTED` で止まる確かめにする |
| `tests/integration/test_issue413_assets.py::test_init_in_a_linked_worktree_does_not_install_into_main_or_shared_git` | `installation show` が示す宣言の版を4に |
| `tests/integration/test_issue413_wheel.py::test_fresh_wheel_contains_one_normal_runtime_and_context_free_utilities` | wheel の資産と init の宣言の値を版4に。`verify_issue415_console` の init の直後に、宣言を版3に戻す準備の行を足す |

### 受け入れ条件との対応

| AC | 確かめ方（テストの置き場） |
|---|---|
| AC-428-01 | 今のテストの全体（`uv run pytest`）。許された変更（上の4件と、Epic の testability の3つの区分）のほかは変えない。`git diff origin/main -- tests/` で変えたテストを一覧にする |
| AC-428-02 | 版4の一時のリポジトリで、`installation` と `workspace migrate` を除く全コマンド（`workspace validate --ci`、`workspace doctor --raw` を含む）が `CANONICAL_NOT_IMPLEMENTED` と `recovery` を返し、作業ツリーと `.git` が変わらない。版5、真偽値、文字列、知らない `writer_protocol` の版4で `PRECONDITION_FAILED`（`tests/cli_runtime/test_issue428_canonical_mode.py`） |
| AC-428-03 | 版4の `workspace migrate`（`--dry-run` と適用）で `CANONICAL_NOT_APPLICABLE`、宣言のバイト列が同じ（同上） |
| AC-428-04 | 振り分けの単体テスト（名前空間を直接作る）。版3で `canonical status` の経路が `CANONICAL_NOT_MIGRATED`。表に登録した偽のハンドラーが、`resolve_context` を呼ぶ前に呼ばれ、`None` なら通常の経路へ進む（`tests/unit/commands/test_canonical_dispatch.py`） |
| AC-428-05 | `installation init` の宣言と警告。版4の `installation show`、`update`（`--dry-run` と適用）、`uninstall`（適用）、古い `writer_protocol` の版4の `update` の停止、版4の `--expect-current` の `CANONICAL_NOT_IMPLEMENTED`（`tests/cli_runtime/test_issue428_canonical_mode.py`） |
| AC-428-06 | `build_snapshot` の単体テスト（`tests/unit/domain/test_canonical_structure.py`）と、偽の GitHub の上の `fetch_structure`（`tests/unit/infra/test_github_structure.py`） |
| AC-428-07 | 時計を注入した `ensure_fresh` の表のテスト（59/60/61秒、5分と30分の前後）（`tests/unit/infra/test_github_snapshot.py`） |
| AC-428-08 | 偽の GitHub の要求の記録（同上） |
| AC-428-09 | 取り直しの途中に `reflect` を挟むテスト。書けない状態の置き場（権限 555）と、排他が取れないとき（同上） |
| AC-428-10 | 偽の GitHub が受けた本文（`tests/unit/infra/test_github_structure.py`） |
| AC-428-11 | 偽の GitHub の404、403 と `retry-after`、時計の記録（同上） |
| AC-428-12 | `make lint`、`uv run pytest` |
| AC-428-13 | `inject(..., apply=True)` と時間切れで、読み直しによる確かめと `GITHUB_EFFECT_UNKNOWN`、`GITHUB_CREATE_IDENTITY_UNKNOWN`（`tests/unit/infra/test_github_structure.py`） |
| AC-428-14 | 500番台の再試行、60秒を超える待ち、GraphQL の `errors`（同上） |
| AC-428-15 | ページ送り、関係とラベルの超過（同上）。壊れたファイルと違う版、古い取り直し、メモリーとファイルの同じ時刻（`tests/unit/infra/test_github_snapshot.py`） |
| AC-428-16 | 変更の前のコード（`be4810244`）で版3の作り物に対して記録した出力（`tests/fixtures/issue428/legacy-outputs.json`）と、今のコードの出力を比べる（`tests/cli_runtime/test_issue428_legacy_outputs.py`）。最終の品質の関門の SHA で `.github/scripts/specdock-ci-validate.sh <worktree> <worktree> <HEAD>` を実行する |

## risk

| リスク | 影響 | 軽減 |
|---|---|---|
| 振り分けの変更で、版3のコマンドの経路が変わる | 大 | 連なりの最初の `if` を `elif` にするだけにし、`mode == "legacy"` で今の連なりに入る。今のテストの全体を通す |
| `read_workspace_declaration` が版4を受け付けると、従来の処理が別の宣言（基点、HEAD、ほかのworktree）を版4として読む | 中 | 移行していないリポジトリには版4がない。切り替えの途中だけの出来事で、従来の処理はその後の `.meta.json` の確かめで止まる。`--ci` と `--raw` は宣言を見て振り分ける |
| `installation init` が版4を書くので、`init` で版3の作り物を作る今のテストが従来の処理に届かない | 中 | 統括の判断（案A）で、4件のテストに、宣言を版3に戻す準備の行だけを足す（testability）。確かめる中身が変わっていないことを最終のレビューで見る |
| GraphQL の費用 | 中 | 依存先の要素のラベルを外して、1ページ4点にする（実測。統括の了承） |
| 別のリポジトリの親や依存先を取り違える | 中 | `repository { nameWithOwner }` を読み、どこにも入れずに異常にする（統括の了承） |
| 取り直しが書き込みの反映を消す | 中 | 排他の中で `merge_refresh` を当てる。テストで、取り直しの途中に反映を挟む |
| 状態の置き場の不具合でコマンドが止まる | 中 | 失敗をメモリーと「ない」に変える。権限のないディレクトリのテスト |
| 偽の GitHub が本物と違う | 中 | 304 の `gh` の終了コード、状態行、id と番号の違いを、調査の記録の実測に合わせる。本物の GitHub で、読むだけの問い合わせを確かめる（報告書） |
