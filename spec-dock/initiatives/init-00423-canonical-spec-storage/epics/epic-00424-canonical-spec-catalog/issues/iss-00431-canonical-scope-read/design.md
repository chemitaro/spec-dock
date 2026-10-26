---
種別: 設計書（Issue）
ID: "iss-00431"
タイトル: "Read Scopes From GitHub In Canonical Mode"
関連GitHub: ["#431"]
状態: "draft"
最終更新: "2026-10-26"
依存: ["requirement.md"]
親: ["epic-00424", "init-00423"]
---

# iss-00431 Read Scopes From GitHub In Canonical Mode — 設計

詳細: [Design Guide](../../../../../../docs/authoring/design.md)

## 設計目標

- canonical モードの読むコマンドを、構造のスナップショット（C10）とカタログ（C3）から動かす。`.meta.json` を読まない。
- 従来の部品（`ScopeView`、`read_selection`、`resolve_scope`、`check_scope_expectations`、`list_scopes`、`dependency_listing`、`sync_selection_links`、Artifact のファイル名の解析、worktree の処理）を、変えずに再利用する。そのために、スナップショットから従来と同じ形の `ScopeView` を作る。従来のモジュールは変えない（AC-15）。
- I-5 と I-11 が使う、着手の判定の部品を、純粋な関数として domain に置き、公開の形をこの文書で決める。

## Current / Target

- **Current**（`d5c8cc943`）：版4のリポジトリで、`installation`、`workspace migrate`、`canonical link`、`canonical status`、`canonical check`、`worktree create`（`--expect-current` なし）のほかは、`CANONICAL_NOT_IMPLEMENTED` で止まる。`canonical status` の `structure` は「未対応」。
- **Target**：requirement.md の R-431-01〜12 のコマンドが canonical モードで動く。`CANONICAL_NOT_IMPLEMENTED` が残るのは、I-5 の書くコマンド（`scope create`、`scope import github`、`scope edit`、`scope close`、`scope reopen`、`scope delete`、`dependency add`、`dependency remove`、`artifact create`、`artifact import file`、`work start`、`work finish`）だけである。

## 責務・Interface

### 置き場

| 置き場 | 中身 |
|---|---|
| `domain/canonical_readiness.py`（新） | 着手の判定（公開。I-5、I-11 が使う） |
| `application/canonical_scopes.py`（新） | 読む側の共通の部品：スナップショットの取得、`ScopeView` の組み立て、ディレクトリの対応、表示の辞書、`--expect-current` の確かめ |
| `application/canonical_scope_read.py`（新） | `scope show`、`scope list`、`dependency list`、`dependency check`、`active show`、`active set`、`active clear`、`artifact list`、`artifact show` |
| `application/canonical_branches.py`（新） | `branch show`、`branch create`、`branch switch` |
| `application/canonical_worktrees.py`（I-2 のものに足す） | `worktree list`、`show`、`remove`、`bootstrap`、`create --expect-current`、`workbench copy`、`installation … --expect-current` |
| `application/canonical_workspace.py`（新） | `workspace sync`、`workspace validate`、`workspace doctor`、構造の検査（`canonical status --structure` も使う） |
| `application/canonical_status.py`（I-2 のもの） | `structure` の項目を、`--structure` のときだけ `canonical_workspace` の検査で埋める（1か所の置き換え） |
| `application/canonical_errors.py` | 新しいコード：`CANONICAL_BASE_HAS_SPECS`、`CANONICAL_CATALOG_PROTECTED`、`CANONICAL_WORKBENCH_SHARED` と次の1手 |
| `commands/canonical_dispatch.py` | `CANONICAL_HANDLERS` に上のコマンドを登録する |
| `commands/runtime_dispatch.py` | 版4の `installation … --expect-current` を `CANONICAL_NOT_IMPLEMENTED` から canonical の処理へ |
| `cli/options.py`、`cli/catalog.py` | `dependency check` と `workspace sync` の `--source` の既定（下）、`canonical status --structure` |
| `presentation/command_data.py` | `snapshot` を持つ `ActiveData`、`SyncData`、`DiagnosticData` の canonical 版（従来の型を継ぎ、項目を1つ足す） |

### 着手の判定の部品（`domain/canonical_readiness.py`、公開）

```python
ReadinessState = Literal["READY", "BLOCKED", "DOING", "DONE", "UNKNOWN"]
BlockerRole = Literal["self", "ancestor", "prerequisite", "external"]

@dataclass(frozen=True)
class CanonicalBlocker:          # 着手を止めている Issue（従来の dependency_vnext.ReadinessBlocker と別の名前）
    number: int                  # Issue の番号
    scope_id: str | None         # Scope でない Issue（role="external"）は None
    role: BlockerRole            # self=対象、ancestor=祖先、prerequisite=前提の Scope、external=Scope でない依存
    required_state: str          # "open"（self、ancestor）、"completed"（prerequisite）、"closed"（external）
    observed_state: str          # "open"、"completed"、"not-planned"、"unknown"（閉じた理由がほかか無い）
    declared_by: str | None      # prerequisite と external のとき、依存を宣言した Scope の ID

@dataclass(frozen=True)
class UnknownReason:             # 判定できない理由
    number: int                  # 理由のある Issue の番号（対象、祖先、または依存先）
    scope_id: str | None
    code: str                    # スナップショットの異常のコード、または DEPENDENCY_NOT_IN_SNAPSHOT
    message: str

@dataclass(frozen=True)
class ScopeReadiness:
    scope_id: str
    number: int
    state: ReadinessState
    ready: bool                  # DOING を見ない。blockers も unknown も空のときだけ真
    in_progress: bool
    blockers: tuple[CanonicalBlocker, ...]
    unknown: tuple[UnknownReason, ...]

def evaluate_readiness(snapshot: StructureSnapshot, scope_id: str) -> ScopeReadiness   # Scope でなければ LookupError
def evaluate_all(snapshot: StructureSnapshot) -> Mapping[str, ScopeReadiness]          # snapshot.scopes のすべて
```

決め方（統括の判断 Q2）：

1. **鎖**：対象と、`parent` をたどった祖先。親が `issues` にない、ID がない、循環する、種類が合わないときは、その番号の異常（なければ `PARENT_INVALID`）を `unknown` に入れて、たどるのをやめる。
2. **異常**：鎖の各 Scope の `snapshot.anomalies_for(number)` をすべて `unknown` に入れる（`PARENT_FOREIGN_REPOSITORY`、`SUB_ISSUE_FOREIGN_REPOSITORY`、`DEPENDENCY_FOREIGN_REPOSITORY`、印、種類、親子、依存の異常を含む）。
3. **鎖の状態**：対象が閉じていれば `self`、祖先が閉じていれば `ancestor` のブロッカー（`required_state="open"`）。
4. **前提**：鎖の各 Scope の `blocked_by` の番号を、宣言した Scope の順（対象、近い祖先から）にたどり、同じ番号は最初の1回だけ見る。
   - `issues` にあり ID がある：`observe_github_state(state, state_reason)` が `completed` でなければ `prerequisite` のブロッカー（`not-planned` も止める。今の規則）。
   - `issues` にあり ID がない（異常で決まらない）：その番号の異常を `unknown` に入れる（なければ `DEPENDENCY_NOT_IN_SNAPSHOT`）。
   - `external` にある：開いていれば `external` のブロッカー（`required_state="closed"`）。閉じていれば理由を問わず止めない。
   - どちらにもない：`DEPENDENCY_NOT_IN_SNAPSHOT` を `unknown` に入れる。
5. **状態**：閉じていれば `DONE`、`unknown` があれば `UNKNOWN`、`in_progress` なら `DOING`、ブロッカーがあれば `BLOCKED`、ほかは `READY`。`ready` は `not blockers and not unknown`（閉じた対象は `self` のブロッカーを持つので偽）。
6. 配下からの集計は作らない（epic-00427）。`work start` が `DOING` を拒むかは I-5 が決める。

### 読む側の共通の部品（`application/canonical_scopes.py`）

```python
@dataclass(frozen=True)
class CanonicalScopes:
    context: ProjectContext
    fresh: FreshSnapshot                       # ensure_fresh の結果（stale と警告を含む）
    snapshot: StructureSnapshot
    views: tuple[ScopeView, ...]               # 従来の部品にそのまま渡せる
    catalog: LinkedCatalog | None              # require_linked の結果。リンクを求めないコマンドは None
    directories: Mapping[str, ScopeDirectory]  # カタログでちょうど1つ見つかった Scope のディレクトリ
    ambiguous: Mapping[str, tuple[ScopeDirectory, ...]]  # 同じ ID のディレクトリが2つ以上（CatalogTree.duplicates）
    def node(self, scope_id) -> ScopeNode
    def payload(self, view) -> dict[str, object]
    def snapshot_payload(self) -> dict[str, object]   # {"fetched_at", "stale", "repository"}
    def warnings(self) -> tuple[Diagnostic, ...]      # GITHUB_SNAPSHOT_STALE を Diagnostic にしたもの

def load_canonical_scopes(context, *, timeout, link: bool, refresh: bool = False, offline: bool = False,
                          service_factory=default_service) -> CanonicalScopes
def check_canonical_expectation(context, namespace, *, stored=None) -> None   # --expect-current の確かめ
```

- 順序：`link=True` なら先に `require_linked`（ローカルだけ。ネットワークの前）。`link=False` でも、リンクとカタログが正しければディレクトリを読む（`require_linked` の失敗を飲み込み、`catalog=None` にする）。次に `repository_for_checkout(context.root)` で GitHub のリポジトリを求め、`StructureSnapshotService(...).ensure_fresh("display")`（`refresh=True` なら `refresh()`）。`offline=True` のときは、GitHub に何も送らず、状態の置き場の今のスナップショット（`SnapshotStore.load()`）を、`stale=True` と `GITHUB_SNAPSHOT_STALE` の警告で使う。なければ `ValueError("offline mode cannot fetch required GitHub state")`（`PRECONDITION_FAILED`）。`refresh=True` と `offline=True` の組は同じ `ValueError`。状態の置き場は `resolve_state_root()`（`XDG_STATE_HOME`）。`GithubApi` の `cwd` は `context.root`、`timeout` はコマンドの `--timeout`。
- **`ScopeView` の組み立て**（スナップショットの `scopes` ごと）：`id`、`kind`、`title`（GitHub）、`parent_id`（親の番号の Scope の ID。ID がなければ None）、`backend=GithubBackend(number, owner, name)`、`github_ref="gh:<owner>/<name>#<number>"`、`revision=0`、`status=StatusObservation(observe_github_state(state, state_reason), "github", "cache", fetched_at, updated_at, stale)`。
- **ディレクトリの対応**：`CatalogTree.directories()` と `duplicates()` から作る。重複した ID は `directories` に入れず `ambiguous` に入れる（`find` の例外で、関係のない読み取りを止めないため）。ディレクトリそのものが要るとき（`require_directory`）だけ、重複なら `ScopeDirectoryAmbiguous`（`PRECONDITION_FAILED`）、ないなら `FileNotFoundError`（`LOCAL_TARGET_NOT_FOUND`）。
- **`path`**：カタログで見つかったディレクトリは、`<checkout>/spec-dock/initiatives/<カタログの中の相対パス>`（リンクを通した、解決しないパス）。従来の `sync_selection_links` は、`spec-dock/` からの相対パスを使うので、そのまま `../initiatives/…` になる。Artifact の読み取りは、守った開き方（`open_guarded_directory` は各要素を `O_NOFOLLOW` で開く）がリンクを通れないので、実際のカタログのパスで行う（下）。見つからない、またはカタログを読まないときは、GitHub の親子から求めた入れ子の位置（`<init>/epics/<epic>/issues/<iss>`）を同じ形で置き、`payload` の `path` は null、`directory_found` は偽にする。
- **表示の辞書**（`payload`）：従来の `scope_payload` と同じキー（`id`、`kind`、`title`、`parent_id`、`backend`、`github_ref`、`path`、`revision`、`status`）に、`number`、`url`、`state_reason`、`in_progress`、`directory_found` を足す。`revision` は null（`.meta.json` の改訂はない）。`status.source` は `cache`（構造のスナップショット）、`status.observed_at` は取得の時刻。
- **選択**：従来の `read_selection(context, views)` をそのまま使う。選択の記録の `github_ref` とスナップショットの参照が同じなら `selected`、違えば `stale` である。

### コマンドごとの処理

| コマンド | リンク | 処理 |
|---|---|---|
| `scope show` | 要 | `resolve_scope` → `check_scope_expectations` → `FamilyData("scope", {scope, github_ref, changed: False, snapshot})` |
| `scope list` | 要 | `list_scopes`（`--kind`、`--parent`、`--state`）→ `FamilyData("scope-list", {items, unknown_filtered_count: 0, snapshot})` |
| `dependency list` | 不要 | `dependency_listing(views, raw, id)`。`--view` は従来どおり文字の出力だけを絞る（`external` は JSON だけに出る）。`raw` は各 Scope の `blocked_by` のうち ID のある Scope の番号の ID。`FamilyData("dependency", {scope_id, declared, effective, external, ready: None, blockers: (), changed: False, snapshot})`。`external` は対象と祖先の Scope でない依存（`number`、`title`、`state`、`declared_by`） |
| `dependency check` | 不要 | 明示の `--source local` は `CANONICAL_NOT_APPLICABLE`。`--source github --offline` は `PRECONDITION_FAILED`。`--source github` は `refresh=True`。`evaluate_readiness` の結果を、`ready`、`blockers`（`READINESS_BLOCKED` と `READINESS_UNKNOWN` の `Diagnostic`）、`readiness`（状態と2つの一覧）で返す。`READINESS_BLOCKED` の `details` は、従来の `scope_id`、`required_state`、`observed_state`、`source`（`cache` か `github`）、`stale` に、`number`、`role`、`declared_by` を足す。`READINESS_UNKNOWN` は `number`、`scope_id`、`code`。結果は今と同じく `succeeded`（判定の結果で失敗にしない） |
| `active show` | 要 | `read_selection` → `CanonicalActiveData(selection, ancestors, scope, snapshot)`。`scope` は選んだ Scope の `payload`（選択がなければ null） |
| `active set` | 要 | 従来の `set_direct` と同じ判定。同じ選択なら、対象と祖先のすべてのディレクトリを `require_directory` で確かめてから、`sync_selection_links(context, views, id)` でリンクだけを直す（ぶら下がるリンクを作らない）。違えば `WORK_START_REQUIRED` |
| `active clear` | 要 | 従来の `clear_direct` と同じ手順を、canonical の Scope で行う（`--from`、`--all`、`--yes`、`--dry-run`、効果の扱い、空になったときの `system/active-none` へのリンク） |
| `artifact list`、`show` | 要（`@root` は不要） | 対象の Scope を決め、`require_directory`。カタログの実際のパス（`LinkedCatalog.catalog / relative / "artifacts"`）を、従来と同じ検査（守った開き方、スロットの台帳、通常のファイルで `st_nlink == 1`、開いた前後の同じ実体）と同じ domain の解析（`parse_existing_artifact_filename`、`scan_artifact_slot_ledger`、`can_create_artifact_type`）で読み、場所を `spec-dock/initiatives/<相対パス>/artifacts/<名前>` で示す。返す形は従来と同じ（`artifact-list` の `scope_id`、`items`、`artifact` の項目）に `snapshot` を足す。`@root` は従来の `query_artifact` をそのまま使う |
| `branch show`、`create`、`switch` | 不要 | 既定の名前 `<ID>-<slug>`（スナップショットの slug）。`create` と `switch` は、従来の `branch_operations` の部品（選択の記録の取得と確かめ、切り替え先の確かめ、`_data`）と同じ手順で、`read_candidate` の代わりに対象のコミットの `spec-dock/initiatives` を `git ls-tree` で確かめる（統括の判断 Q3） |
| `worktree list`、`show` | 不要 | `--expect-current` を canonical で確かめた後、従来の処理（`expect_current=None`）。各行に `catalog`（真偽）を足す |
| `worktree remove` | 不要 | 対象がカタログ（`spec-dock/canonical` をチェックアウトし、ルートに `.spec-dock-canonical.json`）なら `CANONICAL_CATALOG_PROTECTED`。ほかは canonical の確かめの後、従来の処理 |
| `worktree bootstrap` | 不要 | 対象がカタログなら `CANONICAL_CATALOG_PROTECTED`（カタログの中で `make init` を動かさない）。ほかは canonical の確かめの後、従来の処理 |
| `worktree create --expect-current` | 不要 | canonical の確かめの後、I-2 の `create_worktree_and_link`（`expect_current=None`） |
| `installation show/update/uninstall --expect-current`（版4） | 不要 | 対象のworktreeの `ProjectContext` で canonical の確かめの後、従来の `install_static_assets`（`expect_current=None`） |
| `workbench copy` | — | `CANONICAL_WORKBENCH_SHARED`（3） |
| `workspace sync` | 不要 | 明示の `--source local` は `CANONICAL_NOT_APPLICABLE`。`--source github` は `refresh=True`。同じクローンのworktree（カタログを除く）ごとに `resolve_context` と `WorkTargetStore` を読み、`read_selection(other, views)` で観察する。宣言が版3のworktreeも、記録の形式が同じなので同じく観察する。読めないworktreeは従来と同じく `unavailable` の行。従来と同じ重複の検査。`--allow-invalid` は従来と同じく結果を変えない。`CanonicalSyncData`（`SyncData` に `snapshot` を足す）。`source` は `snapshot` か `github` |
| `workspace validate` | 要 | `--ci` は `CANONICAL_NOT_APPLICABLE`（次の1手 `spec-dock canonical check`）。下の検査 |
| `workspace doctor` | 不要（正しければ読む） | 検査の誤りと、選択の確かめ（従来と同じ `DIRECT_SELECTION_UNVERIFIED`）を `findings` に、検査の警告と `canonical status` の警告を `warnings` に、`canonical status` の12の項目を `data.canonical` に入れる（`CanonicalDiagnosticData`）。GitHub の確かめ（`--github-*`）と `--legacy` は従来の部品を使う。`--raw` は、版4では宣言が読めるので、付けないときと同じ。リンクやカタログが正しくないときは、カタログを使う検査を飛ばし、`CANONICAL_NOT_LINKED`（など `require_linked` のコード）を `findings` に入れる |
| `canonical status --structure` | 要（なければ項目に示す） | `display` で確かめ、検査のうち入れ子のずれだけを `structure` に示す。項目の形：付けないとき `{"status": "not_checked", "next_step": null}`。付けたとき `{"status": "ok"|"problem", "next_step", "snapshot": {fetched_at, stale, repository}, "misplaced": [{scope_id, path, expected, next_step}]}`。確かめられないとき `{"status": "unavailable", "code", "next_step", "message"}` |

### `workspace validate` の検査（Epic の6章）

| 検査 | コード | 区分 |
|---|---|---|
| 種類と階層の規則、親子の異常、別のリポジトリの親子・依存 | スナップショットの異常のコード（`KIND_LABEL_MULTIPLE`、`PARENT_MISSING`、`PARENT_INVALID`、`PARENT_FOREIGN_REPOSITORY`、`SUB_ISSUE_FOREIGN_REPOSITORY`、`DEPENDENCY_FOREIGN_REPOSITORY`） | 誤り |
| 本文の印と slug | `SLUG_MARKER_MISSING`、`SLUG_MARKER_MULTIPLE`、`SLUG_MARKER_INVALID`。ディレクトリ名の slug と印の slug が違えば `SCOPE_DIRECTORY_SLUG_MISMATCH` | 誤り |
| 依存の循環、不正な依存 | `DEPENDENCY_CYCLE`、`DEPENDENCY_INVALID` | 誤り |
| ID の重複 | `SCOPE_DIRECTORY_DUPLICATE`（同じ ID のディレクトリが2つ以上） | 誤り |
| ディレクトリがちょうど1つ | `SCOPE_DIRECTORY_MISSING` | 誤り |
| 入れ子と GitHub の親子のずれ | `SCOPE_DIRECTORY_MISPLACED`（`details`：`scope_id`、`path`、`expected`、`next_step: "spec-dock scope move <ID>"`） | 警告 |
| Issue のないディレクトリ | `SCOPE_ISSUE_MISSING`（ディレクトリの ID がスナップショットの Scope にない） | 誤り |
| 必要な文書 | `SCOPE_DOCUMENT_MISSING`（`requirement.md`、`design.md`、`plan.md`、`report.md` のどれかがない） | 誤り |
| `.meta.json` | `SCOPE_METADATA_PRESENT`（カタログの中に `.meta.json` がある。`.runtime/`、`.workbench/` などの `.` で始まるディレクトリの下は見ない） | 誤り |
| 別名ファイル | `CANONICAL_CONFLICT_COPY`（I-2 の `catalog_change_summary` の別名ファイル） | 警告 |
| Scope でない Issue への依存 | `DEPENDENCY_NOT_SCOPE`（Scope の `blocked_by` が `external` にある） | 警告 |

- 入れ子の期待：Initiative は `<ID>-<slug>`（カタログの直下）、Epic は `<親のディレクトリ>/epics/<ID>-<slug>`、Issue は `<親のディレクトリ>/issues/<ID>-<slug>`。親のディレクトリは、実際に見つかった親の場所を使う（親がずれていても、子は親の下にあれば正しい）。親のディレクトリが見つからないときは、子のずれを判定しない。
- 結果は従来と同じ `FamilyData("validation", {valid, findings, snapshot_source: "github-snapshot", snapshot_oid: None, node_count, snapshot})`。誤りがあれば `failed`（終了コード7、`WORKSPACE_VALIDATION_FAILED`）。`--require-nodes` は従来と同じ。

### `--source` の既定（統括の判断 Q1）

- `dependency check` と `workspace sync` の `--source` のパーサーの既定を None にし、`parse_vnext` の中（解析の直後）で、`source_explicit = source is not None`、`source = source or "local"` とする。dispatch では戻さない（従来の JSON の `source` と、既存のテストの `parse_vnext(...).source == "local"` を保つため）。canonical の処理は `getattr(namespace, "source_explicit", False)` で読む（テストが直接作る Namespace にはないため）。従来モードの処理は今と同じ値 `local` を受け取る。canonical モードは、`source_explicit` が真で `local` のときだけ止まる。

### エラーのコード（12章の既存のコード）

| コード | 終了コード | 次の1手 |
|---|---|---|
| `CANONICAL_BASE_HAS_SPECS` | 3 | 切り替えの後のコミットを基点にする（I-5 の `work start` も使う） |
| `CANONICAL_CATALOG_PROTECTED` | 3 | 取り外すなら `spec-dock canonical remove` |
| `CANONICAL_WORKBENCH_SHARED` | 3 | 何もしなくてよい（どのworktreeからも見える） |
| `CANONICAL_NOT_APPLICABLE` | 3 | `workspace validate --ci` は `spec-dock canonical check`、`--source local` は `--source` を外すか `--source github` |
| `GITHUB_SNAPSHOT_STALE` | 警告 | 表示は取得の時刻の時点のもの。つながったら、次の表示か定期の同期で新しくなる |

## data / failure

- 書いてよいのは、状態の置き場の `snapshot.json` と `probe.json` だけ（読むだけのコマンド）。`active set`、`active clear` は今と同じく `spec-dock/active/` と選択の記録だけ、`branch create`、`switch` は参照と作業ツリーだけ、`worktree remove`、`bootstrap` は今と同じ対象だけを書く。
- カタログに対する Git の呼び出し（別名ファイル）は、I-2 の `run_catalog_git(read_only=True)`（`--no-optional-locks`）を使う。
- 失敗の扱いは requirement.md の「失敗・境界条件」の表のとおり。GitHub の失敗は `GithubStructureError` を投げ、dispatch の `github_error_result` が終了コードを決める。

## 変更対象

- 足すもの、変えるものは「置き場」の表のとおり。
- 変えないもの：従来の `application/direct_*.py`、`scope_query.py`、`worktree_observation.py`、`active_links.py`、`branch_operations.py`、`artifact_query.py`、`start_snapshot.py` と、その下の `.meta.json` の読み書き。C1、C2、C3、C10 の公開の形。配布資産。
- I-1 から引き継ぐ直し：`infra/github_structure.py` の `_rate_limit_wait(...) or 60.0` を `is None` の比較にする。テストの直しと追加（R-431-12）。

## 移行・互換性・rollback

- 版3のリポジトリは、`dispatch()` の振り分けで従来の処理だけを通るので、振る舞いは変わらない。`--source` の既定の変更は、解析の後に同じ値に戻すので、従来の値、`--help`、JSON は変わらない（テストで確かめる）。
- 版4のリポジトリは、spec-dock を含めて I-10 までないので、利用者の運用への影響はない。
- rollback：PR を `git revert` する。データの移行はない。

## testability

- **単体**：`domain/canonical_readiness.py` は、`StructureSnapshot` を直接作って、状態ごとと理由ごとに確かめる。`canonical_scopes` の組み立ては、作ったスナップショットと一時のカタログで確かめる。
- **CLI**（`tests/cli_runtime/test_issue431_*.py`）：I-2 の部品（`tests/support/canonical_repo.py` の bare と clone、`canonical link`）でカタログとリンクを作り、カタログに Scope のディレクトリを置く。リンクの後に `origin` の URL を `https://github.com/<owner>/<repo>.git` に変える（読むコマンドはリモートに触れない）。偽の `gh` を `PATH` に置き（`install_fake_gh`）、`XDG_STATE_HOME` を一時ディレクトリにする（`isolate_user_state`）。要求の数は、偽の `gh` の記録で確かめる。304 の確かめを起こすには、`probe.json` の `checked_at` を60秒より前に書き換える。
- **読むだけ**：`tree_digest`（カタログ、`.git`）と `git status --porcelain` の前後の比較、偽の `gh` の書き込みの要求が0件。
- **従来モード**：版3の作り物で、`dependency check` と `workspace sync` の `--source` を付けない／付けた実行の `namespace.source` と JSON が今と同じこと、`--help` の文が同じことを確かめる。
- **実機**：standard の Issue で、Epic の計画は実機の確かめを I-2、I-3、I-9、I-10 に置く。この Issue では、macOS の一時ディレクトリで、wheel を入れた一時の venv から、偽の `gh` を使って主なコマンドを動かす（本物の GitHub と利用者の状態の置き場を使わない）。

## risk

- **従来の部品の再利用**：従来の部品が、将来 `.meta.json` の前提を足すと、canonical の処理が壊れる。テストで canonical の経路を通すことで気づける。I-13 の撤去で、従来の部品を canonical の部品に寄せる。
- **`ScopeView.path` の意味**：canonical ではリンクを通した解決しないパスである。`resolve()` するとカタログの実際のパスになり、`spec-dock/` からの相対パスが求まらない。従来の部品のうち、パスを `resolve` するもの（`load_scope_views`）と、守った開き方でパスを開くもの（`list_artifacts`、`show_artifact`）は canonical では使わない。
- **I-3 との衝突**：`canonical_status.py` の `sync_item`、`snapshot_item` は I-3 が置き換える。この Issue は `structure` の1か所と `status_of` の引数だけを変える。
- **スナップショットの古さ**：`display` は最大30分古い構造を示しうる（Epic の設計どおり）。`dependency check --source github` と `workspace sync --source github` で取り直せる。
