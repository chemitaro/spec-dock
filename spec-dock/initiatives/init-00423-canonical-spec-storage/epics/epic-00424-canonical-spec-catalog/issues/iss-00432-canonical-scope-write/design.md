---
種別: 設計書（Issue）
ID: "iss-00432"
タイトル: "Write Scopes To GitHub In Canonical Mode"
関連GitHub: ["#432"]
状態: "draft"
最終更新: "2026-10-29"
依存: ["requirement.md"]
親: ["epic-00424", "init-00423"]
---

# iss-00432 Write Scopes To GitHub In Canonical Mode — 設計

詳細: [Design Guide](../../../../../../docs/authoring/design.md)

## 設計目標

- canonical モードの書くコマンドを、構造は GitHub に、内容はカタログの平らな `<区切り>/<ID>/` に書くようにする。`.meta.json` を読み書きしない。Issue の本文に何も書かない。
- GitHub に書く判断は、必ず `decision` の新しさで確かめ、判断に使う Issue を読み直してから行う。止まる条件（題名の規則と種類の付け替えを含む）は、すべて最初の書き込みの前に確かめる。結果が分からない書き込みは重ねない（R-I4、R-I5）。
- 書いた結果は、書き込みごとにスナップショットに反映する。カタログに書いた変更は、カタログの排他の中で書き、変更の束に残す（C4、C10）。
- 書く側の共通の部品（確かめ、読み直し、書き込みと反映、効果の記録、`partial` の組み立て）を1か所に置き、各コマンドはその上で、下の表の順に書く。
- 従来の部品（選択の記録、選択と在庫の純粋な判定、ブランチの名前の確かめ、テンプレートの置き換え、ファイルとディレクトリの公開、バックアップ、木の削除、Artifact の名前の規則）と、I-14、I-16 の部品は、変えずに呼ぶ。従来のモジュールは変えない（AC-15）。

## Current / Target

- **Current**（`a23d7d175` を取り込んだ後）：版4のリポジトリで、`scope create`（3）、`scope import github`（3）、`scope edit`、`scope close`、`scope reopen`、`scope delete`、`dependency add`、`dependency remove`、`artifact create`、`artifact import file`、`work start`、`work finish` の16個が `CANONICAL_NOT_IMPLEMENTED` で止まる。`scope move` はない。前の担当のコミット（`370fa63d5`）に、書く側の部品と `scope` の書くコマンドの、slug と入れ子の前提の版がある。I-1 の `update_issue` の読み直しは `state_reason` を比べない（前の担当が `body` と一緒に直したが、本文は使わなくなった）。
- **Target**：16個と新しい `scope move` が canonical モードで動き、`CANONICAL_NOT_IMPLEMENTED` で止まるコマンドがなくなる。I-4 から引き継いだ3つの直しが入る。

## 責務・Interface

### 置き場

| 置き場 | 中身 |
|---|---|
| `application/canonical_writes.py`（新） | 書く側の共通の部品（下の「書く側の共通の部品」） |
| `application/canonical_scope_create.py`（新） | `scope create`、`scope import github` |
| `application/canonical_scope_change.py`（新） | `scope edit`、`scope move`、`scope close`、`scope reopen`、`scope delete` |
| `application/canonical_dependency_write.py`（新） | `dependency add`、`dependency remove` |
| `application/canonical_artifact_write.py`（新） | `artifact create`、`artifact import file` |
| `application/canonical_work.py`（新） | `work start`、`work finish` |
| `domain/canonical_scaffold.py`（新） | 純粋な規則：前付けの `タイトル:` と `親:` の行を除く、「詳細:」の相対リンクの深さの書き換え、題名の規則 |
| `infra/canonical_scaffold.py`（新） | テンプレートを、置き換え・前付けの行の除去・リンクの書き換えをしながら、ディレクトリの記述子に写す。区切りのディレクトリを、リンクをたどらずに開くか作る。空になった区切りを消す |
| `application/canonical_catalog.py`（I-2 のもの） | 形式の版の確かめを `require_writable_format(catalog)` として切り出し、`catalog_changes` もそれを使う（振る舞いは同じ） |
| `application/canonical_branches.py`（I-4 のもの） | R-432-13 の再観察 |
| `application/canonical_worktrees.py`（I-4 のもの） | R-432-13 の `--expect-current` とリンク |
| `application/canonical_errors.py` | 新しいコードと次の1手 |
| `infra/github_structure.py`（I-1） | `update_issue` の読み直しで `state_reason` も比べる。本文の引数を持たない（R-432-14） |
| `domain/canonical_structure.py`、`infra/github_snapshot.py`（I-1） | 反映できない変更を飛ばして古いものとして扱う（R-432-14） |
| `commands/canonical_dispatch.py` | `CANONICAL_HANDLERS` に17の書くコマンドを登録する |
| `commands/runtime_dispatch.py` | 版3の `scope move` を `CANONICAL_NOT_MIGRATED` に振り分ける |
| `cli/catalog.py` | `scope move` の葉（`LEAF_PATHS`、`HELP_EFFECTS`、`LEAF_ARGUMENTS`（`--parent` は必須）、`MUTATING_LEAF_PATHS`、`HELP_PRECONDITIONS`、`--help` の節） |
| 配布資産 `docs/reference_cli.md`、`static-inventory.json` | `scope move` の項目と、その digest |

`application/canonical_scopes.py` の組み立て（I-14 の `build_canonical_scopes`）は、そのまま使う。前の担当が切り出した `assemble_canonical_scopes` は、I-14 の同じ関数に置き換えた。

### 書く側の共通の部品（`application/canonical_writes.py`）

```python
WRITE_CLOCK: GithubClock = SYSTEM_CLOCK          # テストが差し替える（書き込みの間の1秒を待たずに確かめる）
CATALOG_LOCK_TIMEOUT = 10.0

def writing_service(repository, root: Path, timeout: float) -> StructureSnapshotService
    # GithubApi(timeout=timeout, cwd=root, clock=WRITE_CLOCK)、SnapshotStore(resolve_state_root(), repository)

@dataclass
class WriteSession:
    context: ProjectContext
    command: str
    repository: GithubRepository
    service: StructureSnapshotService
    catalog: LinkedCatalog | None
    scopes: CanonicalScopes                       # decision で確かめ、読み直しを反映した後のもの
    effects: list[Effect]
    warnings: list[Diagnostic]
    facts: dict[int, IssueFacts]                  # 読み直した、または書いた結果の Issue

    def resolve(self, selector: str, selection) -> ScopeView      # resolve_canonical_scope（古い ID は SCOPE_KIND_CHANGED）
    def require_kind_unchanged(self, *scope_ids: str) -> None    # scopes.require_kind_unchanged
    def reread(self, numbers: Iterable[int]) -> None
        # 番号ごとに client.get_issue → facts に入れ、UpsertIssue で反映し、scopes を組み直す
    def reread_parent(self, number: int) -> None
        # client.get_parent → SetParent で反映する（親が Scope でなければ親なしとして反映）
    def reread_blockers(self, number: int) -> None
        # client.list_blocked_by → 今の依存に置き換えて反映する（AddBlockedBy と RemoveBlockedBy）
    def write(self, kind: str, target: str, call: Callable[[], T],
              changes: Callable[[T], Sequence[StructureChange]] | None = None) -> T
        # call が成功したら Effect(kind, "succeeded", target) を足し、changes を反映する
        # GithubStructureError なら Effect(kind, "unknown" if uncertain else "failed", target) を足して WriteFailed を出す
    def reflect(self, changes) -> None
        # service.reflect_writes。飛ばした変更があれば GITHUB_SNAPSHOT_STALE の警告を1つ足す
    def ensure_labels(self, names: Sequence[str]) -> None
        # スナップショットのどの Issue にもないラベルだけ label_exists で確かめ、なければ create_label（効果 github.label.create）
    def result(self, status, data, *, effects=None) -> OperationResult[object]
    def incomplete(self, data, error: Exception, *, pending, recovery, code) -> OperationResult[object]
        # 残りの効果を not_attempted で足し、succeeded か unknown があれば partial（6）、なければ failed
        # （終了コードは原因に従う：GITHUB_* は5、CANONICAL_* はそのコードの値、ValueError は3、LookupError は4）

def open_write_session(context, namespace, *, link: bool, level: FreshnessLevel = "decision",
                       refresh: bool = False, service_factory=writing_service) -> WriteSession
def refuse_slug(namespace) -> None               # --slug があれば CANONICAL_NOT_APPLICABLE（scope create、scope import github）
```

- `open_write_session` の順：`--offline` なら `ValueError(OFFLINE_MESSAGE)`（`PRECONDITION_FAILED`）→ `link` なら `require_linked`（ローカルだけ）と `require_writable_format`（`link` でないときも、正しいリンクがあればカタログを読む。I-4 と同じ）→ `repository_for_checkout` → `service.ensure_fresh(level)`（`refresh` なら全体を取り直す。`decision` は失敗すれば元のコードで止まる）→ `build_canonical_scopes`（I-14。`kind_changes` もここで決まる）。どれも書く前なので、失敗は `failed` になる。
- 各コマンドは、`resolve`（I-14 の `resolve_canonical_scope`）と `check_canonical_scope_expectations`（`--expect-current`、`--expect-backend`）で対象を決め、下の表の Issue を `reread` してから、止まる条件をすべて確かめる。`--dry-run` は、ここで `planned` を返す（GitHub に書かない）。
- 書き込みは `write` を通す。1つのコマンドの `GithubApi` は1つなので、書き込みの間の1秒は I-1 の部品が守る。`WriteFailed` を受けたコマンドは `incomplete` で `partial` を返す。書く前に出た `GithubStructureError` は、そのまま dispatch の `github_error_result` が `failed` にする。
- `--yes` の扱いは今と同じ（`scope create`、`scope close`、`scope reopen`、`scope delete` は、`--yes` も TTY もないと止まる。TTY では計画を示して確かめる。`work finish` は `--yes` が必須）。

### 題名の規則（`domain/canonical_scaffold.py`。R-432-16）

```python
TITLE_MAX_LENGTH: Final = 256

def validate_canonical_title(value: str, *, field: str) -> str
    # 前後の空白を除いた値を返す。空、Unicode の分類 Cc（改行、タブなど）を含む、256文字を超える、は ValueError
```

- 文字数は Python の `len`（コードポイントの数）で数える。GitHub の上限（256）と同じ数え方であることは確かめていない（`risk` に書く）。
- 呼ぶところ：`scope create` の `--title`、`scope edit` の `--title`、`scope import github` の GitHub の題名（読み直した値。合わないときの次の1手は「GitHub で題名を直す」）。

### コマンドごとの読み直しと書く順

「読み直す」は `decision` の確かめの後に `GET …/issues/{n}` で読む Issue（R-I4）。効果の名前は、従来と同じものは従来のまま使う。

| コマンド | 読み直す | 種類の付け替えを確かめる番号 | 書く順（効果の名前） |
|---|---|---|---|
| `scope create` | 親 | 親とその祖先 | `github.label.create`（ラベルがなければ）→ `github-create`（Issue。題名と種類のラベルだけ）→ `github.sub-issue.add`（親へ。Initiative はなし）→ `scaffold`（排他の中で `<区切り>/<ID>/` を公開し、束を書く） |
| `scope import github` | 対象（さらに `get_parent`、`list_sub_issues`、`list_blocked_by`）と `--parent` | 対象、親とその祖先 | `github.label.create` → `github.issue.label`（種類のラベル）→ `github.sub-issue.add` → `scaffold`。足りないものだけ |
| `scope edit` | 対象 | 対象 | `github.issue.title` |
| `scope move` | 対象と `get_parent`（対象）、新しい親と `get_parent`（新しい親） | 対象、新しい親とその祖先 | `github.sub-issue.add`（`replace_parent: true`。すでにその親なら書かない） |
| `scope close` | 対象 | 対象 | `github.issue.close`（`state`、`state_reason`） |
| `scope reopen` | 対象 | 対象 | `github.issue.reopen`（`state: open`） |
| `scope delete` | 全体を取り直す（`refresh`。生き残る Scope からの依存と子孫を漏れなく見つけるため） | 確かめない（止めない） | `backup` → `selection.clear`（`--clear-active`）→ `scope.delete`（排他の中で各ディレクトリと空になった区切りを消し、束を書く）→ `dependency-edge`（生き残る Scope からの blocked by を外す。`--detach-dependencies`）→ `github.sub-issue.remove`（対象を親から）→ `github.issue.label`（削除する各 Scope の種類のラベルを外す。子孫から） |
| `dependency add`、`remove` | 両端と `list_blocked_by`（`--from`） | 両端 | `dependency-edge`（`POST`／`DELETE …/dependencies/blocked_by`） |
| `artifact create`、`import file` | なし（`display`） | 対象（`@root` は除く） | `artifact`（排他の中で公開し、束を書く） |
| `work start` | 対象と祖先の依存の一覧（`list_blocked_by`。GitHub の画面だけで足した依存は変わったかの確かめで見えないことがあるため）、対象、対象と祖先の Scope でない依存先 | 対象と祖先（`lineage`） | `git.branch.create` → `git.checkout` → `selection.clear`（置き換えのとき）→ `selection.publish` → リンク（`link_after_command` の効果）→ `active.link` → `github.label.create`、`github.issue.label`（作業中）、`github.issue.assignee`（印。失敗は警告だけ） |
| `work finish` | 対象 | 対象 | `catalog.changeset`（`origin: finish`。未保存の変更があるとき）→ 保存の確かめ → `github.issue.close` → `github.issue.label`（作業中を外す。失敗は警告だけ）→ `selection.clear` → `active.link` |

- 書いた結果の反映（`reflect`）：Issue の作成、題名、状態の変更は、返った Issue で `UpsertIssue`。ラベルと担当者は、知っている Issue に、返った値を重ねた `UpsertIssue`。親子は `SetParent`、依存は `AddBlockedBy`（Scope でない相手は `ExternalIssue` を付ける）と `RemoveBlockedBy`。
- 取り込みでは、読み直した親（`get_parent`）、子（`list_sub_issues`）、依存（`list_blocked_by`）も `SetParent` と `AddBlockedBy` で反映する。子は、スナップショットにある Scope だけを `SetParent` にする（Scope でない子は表さないものなので、飛ばしても古いと扱わない）。別のリポジトリの相手は、スナップショットの全体の読み取りと同じく表さない。
- 種類の付け替え：上の表の番号を、`reread` の後に `session.require_kind_unchanged(...)` で確かめる。取り込みの対象は、種類のラベルを足す前なので `kind_changes` に入らない。そこで、`catalog.tree.directories()` の中に、同じ番号で取り込む種類と違う `<ID>` があれば `SCOPE_KIND_CHANGED`（I-14 の `kind_change_error` に `KindChange(番号, 取り込む ID, (同じ番号で違う種類の名前…))`（名前は昇順のタプル）を渡す）とする。

### 各コマンドの止まる条件（書く前）

| コマンド | 止まる条件 |
|---|---|
| `scope create` | `--slug`（`CANONICAL_NOT_APPLICABLE`）。題名の規則。親の解決と種類の規則。親かその祖先が開いていない（親は読み直した値）。親か祖先の種類の付け替え。テンプレートと規則の元のファイルがない。作業場所が同じファイルシステムでない |
| `scope import github` | `--slug`。別のリポジトリ、PR。種類のラベルが別の種類か2つ以上。GitHub の題名が規則に合わない。GitHub の親が `--parent` と違う（次の1手「`--parent` を GitHub の親にして取り込み、その後で必要なら `spec-dock scope move <ID> --parent <親>`、または GitHub で親を直してから取り込む」）。Initiative に親がある。親の種類、親かその祖先が閉じている。同じ番号で別の種類のディレクトリ、親か祖先の付け替え（`SCOPE_KIND_CHANGED`）。区切りの場所がシンボリックリンクかファイル |
| `scope edit` | 題名の規則。対象の付け替え |
| `scope move` | Initiative（親を持たない）。親の種類の規則。対象自身か子孫を親にする。新しい親かその祖先が閉じている。対象か新しい親とその祖先の付け替え |
| `scope close`、`reopen` | 今の `plan_close`、`plan_reopen` の規則（子孫と祖先はスナップショットの親子から求める。対象は読み直した値）。`close --reason completed` は、対象か子孫に `SUB_ISSUE_FOREIGN_REPOSITORY` があるか、子に ID の決まらない Scope（種類のラベルが2つ以上）があれば `PRECONDITION_FAILED`（`DESCENDANT_STATUS_UNKNOWN:`）。対象の付け替え。Epic の「子が付け替えの異常で ID を決められない」は、ID が決まらない子（種類のラベルが2つ以上）と読んだ。付け替えた子（ID は今の種類で決まる）は、`work finish` では止め（保存の確かめの場所が違うため）、`scope close` では今の状態で判定する |
| `scope delete` | 今の規則（`--backup-dir`、`RECURSIVE_REQUIRED`、`CLEAR_ACTIVE_REQUIRED`、`DETACH_DEPENDENCIES_REQUIRED`、選択が観察できない）。バックアップの先が消すディレクトリかカタログか Git のメタデータと重なる |
| `dependency add` | 両端が Scope に決まらない。両端の付け替え。`dependency_violations` が循環か規則の違反を返す（`PRECONDITION_FAILED`。メッセージに違反のコードと相手） |
| `dependency remove` | 両端が Scope に決まらない。両端の付け替え。辺がなく `--missing-ok` がない（`SCOPE_NOT_FOUND`、今と同じ文） |
| `artifact …` | 今の規則（題名、slug、テンプレート、元のファイル、スロット）。Scope のディレクトリがない。対象の付け替え。`@root` はリンクを求めない |
| `work start` | 今の規則（ブランチ、基点、作業ツリー、在庫、選択、`--switch-active`）。基点か既存のブランチの先頭に `spec-dock/initiatives`（`CANONICAL_BASE_HAS_SPECS`）。対象か祖先の付け替え。着手の判定の `ready` が偽（`READINESS_NOT_SATISFIED`）。リンクがないことは止まる条件にしない |
| `work finish` | 今の規則（`--yes`、選択が観察できない、状態が分からない、`not-planned`、子孫が未完了）と `close` の `DESCENDANT_STATUS_UNKNOWN`。対象の付け替え。保留がある（`CANONICAL_SAVE_HELD`）。同期が一時停止（`CANONICAL_SAVE_UNCONFIRMED`） |

### Scope のディレクトリの作成（`scope create`、`scope import github`）

- 置き場：種類と親を問わず `<カタログ>/scope_relative(ID)`（`<区切り>/<ID>`）。作業場所は `<カタログ>/.runtime/staging/`（I-2 の `staging_directory`）で、従来の `publish_directory` で一度に公開する（置き換えない）。
- 区切り：公開の前に、排他の中で `open_bucket(catalog, bucket)`（`infra/canonical_scaffold.py`）で区切りを開く。なければ `mkdir`（作ったときは、束の `paths` に区切りではなく `<区切り>/<ID>` だけを入れる。区切りは Git が保存するのは中身だけなので、束に要らない）。区切りの名前の場所がシンボリックリンクかファイルなら `CanonicalCommandError(CANONICAL_PATH_OCCUPIED)`（終了コード3。次の1手は「示したパスを確かめて退避する」。既存のコードを使う）。`<区切り>/<ID>` がすでにあれば、`publish_directory` が置き換えずに止まる。
- テンプレートは、このチェックアウトの `spec-dock/templates/<種類>/` から、従来の `_replacements` の置き換えで写し、次の2つを行う（`domain/canonical_scaffold.py` の純粋な関数）。
  - 前付け（先頭の `---` から次の `---` まで）の `タイトル:` と `親:` で始まる行を除く（`strip_structure_front_matter`）。見出しの題名は残す。
  - 本文の Markdown のリンクの先のうち、`(../` を繰り返した後に `docs/` が続くもの（従来の入れ子の深さで `spec-dock/docs/…` を指すもの）を、`SCOPE_TO_SPEC_DOCK / "docs/…"`（`../../../docs/…`）に書き換える（`rebase_spec_dock_links`）。ほかのリンクは変えない。
- 規則のリンク：`artifacts/rules.md` と `discussions/rules.md` を、`_create_relative_symlink_at` で、カタログの実際のパスから mainのチェックアウトの `spec-dock/docs/rules/<種類>/artifacts.md` と `discussions.md` への相対のリンクとして置く（`<main>/spec-dock/.canonical/<区切り>/<ID>/artifacts/rules.md` から `../../../../docs/rules/…`。リンク `spec-dock/initiatives` を通しても同じ深さで開く）。`artifacts/rules.md` の組は従来の `_rules_scaffold_specs` から取り、`discussions/rules.md` の組（従来の作成は置かない）は canonical の側で足す（`canonical_rules_links`）。元のファイルがなければ、書く前に止まる（従来の `_precheck_pre_github_create_rules_sources` と同じく `FileNotFoundError`）。移行前の `epics/rules.md` と `issues/rules.md` は置かない。
- 公開の後に、ディレクトリのカタログの中の相対パス（`<区切り>/<ID>`）を、束の `paths` に入れる。

### `scope move`

- 対象（`target`）と新しい親（`--parent`、必須。`LEAF_ARGUMENTS` は `_required("--parent")`）を `resolve` で解く。読み直しの後、`ancestors_for` で、対象自身か子孫を親にしないことを確かめる。すでにその親なら `unchanged`。
- `add_sub_issue(親, child=対象, child_id=対象の id, replace_parent=True)`。反映は `SetParent`。カタログとリンクを求めず、カタログに何も書かない（`open_write_session(link=False)`）。
- 付け替えの後、このチェックアウトの選択（`read_selection`）が対象かその子孫なら、`sync_selection_links` で `spec-dock/active/` を整える（効果 `active.link`。失敗は警告）。ほかのworktreeの選択は、I-4 の `workspace sync` と同じ観察（カタログのworktreeを除く）で見て、対象かその子孫なら警告 `ACTIVE_LINK_NOT_UPDATED`（`details`：`path`、`scope_id`、`next_step`「In <path>, run spec-dock active set <ID>.」）を返す。観察できないときは、警告を足さずに結果を変えない。
- `--help`：Reads「The GitHub structure snapshot checked at decision freshness and the target and new parent Issues and parents read again.」、Writes「The GitHub parent of the Scope (sub-issue with replace_parent); this checkout's spec-dock/active links when it selects the Scope or a descendant.」、Does not「Does not write the catalog, move directories, edit documents, close or reopen Issues, or change selection or branches.」。`HELP_PRECONDITIONS`「A schema-4 checkout; --parent is required and must be the right kind and open, and not the Scope or one of its descendants.」。`HELP_EFFECTS` は Epic の12章の文。
- JSON の `data`：`scope`（今の Scope の出力）、`github_ref`、`changed`、`parent_before`、`parent_after`（ID か null）、`snapshot`。`--dry-run` は `can_apply` と `blockers` を足す。

### `scope delete` の書き方

- 消すもの：対象と（`--recursive` のとき）子孫の ID のそれぞれについて、`catalog.tree.find(ID)` と、その番号の `kind_changes` の古い名前（`scope_relative(名前)`）のうち、今あるもの。ないものは計画から外す（やり直しでは、残っているものだけになる）。
- バックアップは従来の部品（`copy_tree_at`、`tree_digest`、`verify_backup_root`）で、それぞれを `<backup-dir>/<区切り>/<名前>` に写し、digest で確かめる。選択を外すときは、選択の記録も写す（従来と同じ）。
- 順序は、バックアップ → 選択を外す → ディレクトリを消す → GitHub の書き込み、とする（統括の判断の「バックアップが先」を、やり直せる順にさらに進めたもの）。GitHub の書き込みを最後にするのは、種類のラベルを外すと Issue が Scope でなくなり、同じコマンドで対象を決められなくなるためである。途中で止まっても、対象はまだ Scope なので、同じ `scope delete` をもう一度実行すれば、ないディレクトリを飛ばし、残りの GitHub の書き込みを行う（外す書き込みは、相手がなければ読み直しで確かめて成功とする。I-1 の部品）。
- ディレクトリは、カタログの排他の中で、写した後の中身が変わっていないことを確かめてから、従来の `remove_tree`（観察した項目だけを消す）で1つずつ消し、束の `deletions` に入れる。消した後に区切りが空なら `rmdir` で消す（空でなければ何もしない。`remove_empty_bucket`）。`origin: command` の束の削除は、同期が保留しない（I-3）。
- 種類のラベルを外すと、その Issue は Scope でなくなる（スナップショットでは `external` になる）。Issue は閉じない。

### `work start`（`application/canonical_work.start_work`）

- 従来の `work_start.start_work` の流れを、canonical の部品で写す。従来の純粋な部品（`plan_start`、`plan_selection`、`check_inventory`、`check_branch_occupancy`、`_verify_inventory`、`_check_private_state`、`_resolve_bound_context`）はそのまま呼ぶ。
- 置き換えるもの：
  - 対象と在庫：`.meta.json` の代わりに、`decision` のスナップショットの `views`。他のworktreeの選択の観察は、I-4 の `workspace sync` と同じく、カタログのworktreeを除き、`read_selection(other, views)` で行い、従来の `WorktreeSelection` の形で返す。
  - 既定のブランチ名：`target.id`（`<ID>`）。`--branch` の既存のブランチはそのまま使う。従来の `work start` はブランチ名と ID を照らさない（名前の形だけを確かめる）ので、I-14 の `branch_names_scope` は使わず、移行前の `<ID>-<名前>` を含む任意の名前を今と同じく受け付ける。
  - 基点の照合：`read_candidate` と `verify_candidate`（`.meta.json`）の代わりに、I-4 の `refuse_specs_at(context, tip)`（`CANONICAL_BASE_HAS_SPECS`）。チェックアウトの後も、HEAD が固定した先頭であることで同じコミットを確かめる。
  - 種類の付け替え：`scopes.require_kind_unchanged(*scopes.lineage(target.id))`（I-14）。
  - 着手の判定：`evaluate_readiness`。`ready`（ブロッカーも判定できない理由もない）が真のときだけ進み、`plan_start` には `ReadinessResult(target, ready=True, blockers=(), stale=False)` を渡す。`ready` が真で状態が `DOING` なら警告 `SCOPE_IN_PROGRESS`（`details`：`scope_id`、`number`、`assignees`、`labeled_at: null`、`next_step`）。`ready` が偽なら、状態を問わず（作業中の印があっても）`READINESS_NOT_SATISFIED`（`details`：`state`、`blockers`、`unknown`）。
  - Git の書き込みの失敗の後の再観察：従来の `_mutate_git` の判定のうち、`verify_candidate` を `refuse_specs_at` に替えた写し。
- 順序：書く前の確かめ（`StartLock` の外。GitHub の確かめと読み直しを含む。リンクは求めない）→ `StartLock` の中で、従来と同じ確かめ、ブランチの作成、チェックアウト、選択の記録 → `StartLock` を放す → `link_after_command(context.root)` → リンクが正しければ、カタログを読み直した `views` で `sync_selection_links`（正しくなければ飛ばし、警告 `ACTIVE_LINK_NOT_UPDATED`）→ 作業中の印。
- 選択の記録が `unchanged` のときも、リンクと作業中の印を整える。どれかが書けば結果は `succeeded`、何も書かなければ `unchanged`。
- 作業中の印：`ensure_labels(["spec-dock:in-progress"])`、`add_labels`、`current_login` と `add_assignees`。どれかが失敗したら、残りを行わずに、警告 `CANONICAL_PROGRESS_MARK_FAILED`（次の1手「GitHub で対象の Issue に `spec-dock:in-progress` と担当者を付ける。付けなくても作業は進められる」）を返す。成功した書き込みだけを効果に入れ（`succeeded` の結果に `unknown` を入れないため）、失敗した書き込みの種類と状態（`failed`、`unknown`）は警告の `details.writes` に入れる。

### `work finish`（`application/canonical_work.finish_work`）

- 書く前：`--yes`、`require_linked`、`decision` の確かめと対象の読み直し、対象と子孫の付け替え（`require_kind_unchanged(対象, *子孫)`）、今の状態の規則と `DESCENDANT_STATUS_UNKNOWN`、選択の観察（従来と同じ `clear_handle` の決め方）。確かめる場所は、対象と子孫（スナップショットの親子）のそれぞれの `scope_relative(ID)` で、ディレクトリがなくても確かめを飛ばさない。`state.json` を読み、どれかの場所の下の保留（`holds_under`）があれば `CANONICAL_SAVE_HELD`（3）、`paused` なら `CANONICAL_SAVE_UNCONFIRMED`（3）。`state.json` が読めなければ `CANONICAL_SAVE_UNCONFIRMED`（3、`next_step` は `spec-dock canonical status`）。
- 保存の確かめ（`confirm_saved`。時計、待ち、間隔は注入できる。既定は180秒、2秒）：
  1. カタログの排他の中で `run_catalog_git(catalog, "status", "--porcelain=v1", "-z", "--untracked-files=all", read_only=True, pathspecs=[<場所>…])`（C6 の渡し方）。変更があれば、`catalog_changes(origin="finish")` の束（`paths` は今ある場所、消えた場所は `deletions`）を書き、束のファイル名を覚える。
  2. 待ち始めの時刻（秒に切り捨て）を記録し、`request_sync_now(resolve_state_root())`。
  3. `read_catalog_state` を間隔ごとに読み、条件（requirement.md の R-432-12 の4）をすべて満たせば終わる。毎回、上の読むだけの `status` で場所の未保存の変更がないことと、`rev-parse HEAD`（読むだけ）が `state.json` の `head` と同じことも確かめる。周期の新しさは、`last_cycle.started_at` が待ち始めの時刻（秒に切り捨て）以上であることで求める（`state.json` の時刻は秒の精度なので、頼んだ周期が同じ秒の中で終わっても数えられるようにする。同じ秒に始まった前の周期を数えても、保存の保証は、束を書いたときの `consumed_changesets`、毎回の未保存の変更がないことと HEAD の一致と `remote_contains_head` が受け持つ）。待ち始めの時刻は、同期の側と同じ実際の時刻で取る。時間切れの判定と待ちの間隔だけを注入できるようにする（`canonical_work.SAVE_CLOCK`。テストは、時間切れを確かめるときだけ、待ちのたびに進む時計に替える）。保留が現れたら `CANONICAL_SAVE_HELD`、`paused` になったら `CANONICAL_SAVE_UNCONFIRMED` で、待たずに止まる。
  4. 時間切れは `CANONICAL_SAVE_UNCONFIRMED`。束を書いていれば `partial`（6。`catalog.changeset` が `succeeded`、`github.issue.close` と以後が `not_attempted`）、書いていなければ `failed`（3）。`recovery` は `spec-dock canonical status`。
- 確かめた後：`ensure_fresh(decision)` と対象の読み直しをもう一度行い、状態の規則を確かめ直す。止まるときは、束を書いていれば `partial`（6、`recovery` に `spec-dock work finish <ID> --yes`）、書いていなければ `failed`。続けて、対象が `completed` でなければ `update_issue(state="closed", state_reason="completed")`。作業中のラベルがあれば `remove_label`（失敗は警告 `CANONICAL_PROGRESS_MARK_FAILED`）。選択を外し、今と同じく `spec-dock/active/` を戻す。結果の形は従来の `FinishData`。

### I-4 から引き継ぐ直し

- **ブランチ**（`canonical_branches.py`）：
  - 作成の Git の失敗：同じクローンとworktreeであることを確かめてから参照を読み直す。あれば `created`、先頭が固定した基点と同じなら `succeeded`、違えば `unknown`、なく結果が確かなら `failed`、ほかは `unknown`。選択も確かめる。読み直しの例外は飲み込み、`unknown` のままにする（従来と同じ）。
  - 切り替えの Git の失敗：目的のブランチと先頭にいれば `succeeded`（さらに、きれいさと選択を確かめ、失敗すれば `verification_error`）、元のブランチと先頭にいて結果が確かで、きれいなら `failed`、ほかは `unknown`。読み直しの例外は `details.verification_error` に入れる。
  - 切り替えの成功の後に、作業ツリーがきれいであること（`status --porcelain`）を確かめる。`unchanged` のときも同じ。
- **`--expect-current`**（統括の判断 Q3）：
  - `worktree remove`、`worktree bootstrap`：従来の外側の関数が行う確かめ（`require_writer`、`--expect-backend`、選択の記録の状態と物理の同一性、`--yes`、`--offline`、対象の解決）と、`DirectoryIdentity` を出るときの `OSError` を `partial` か `failed` に直す包みを写した上で、canonical で取り込んだ記録で `check_canonical_expectation(…, stored=記録)` を行い、同じ記録で従来の `_remove_captured_worktree`、`_bootstrap_captured_target` を `DirectoryIdentity` の中で呼ぶ。従来の内側の処理は、書く前に記録が取り込んだものと同じであることを確かめるので、確かめと書き込みの間に選択が変わると止まる。
  - `worktree create --expect-current`、版4の `installation … --expect-current`：記録を取り込んで確かめ、従来の処理を呼ぶ直前に記録を読み直し、同じでなければ `PRECONDITION_FAILED`（「direct selection changed after --expect-current was checked」）で止まる。従来の処理は自分で取り込み直すので、読み直しと従来の取り込みの間の狭い窓が残る（`report.md` に書く）。
- **`worktree remove` とリンク**（統括の判断 Q4）：従来と同じ `git ls-files --others --ignored --exclude-standard --directory -z` で、対象の無視されたものを数える。`--discard-ignored` がなく、無視されたものが `spec-dock/initiatives` の1つだけで、それが正しいリンク（I-2 の判定）なら、従来の内側の処理に `discard_ignored=True` を渡す。渡すときは `replace_namespace(namespace, discard_ignored=True)` で置き換える（従来の内側の処理は `namespace.discard_ignored` を読むため）。ほかのものがあれば、今と同じく `ignored worktree content requires --discard-ignored and explicit confirmation` で止まる。選択を持つworktreeには、無視された `spec-dock/active/` と `spec-dock/.agent/` もあるので、今と同じく `--discard-ignored` が要る。

### C1 と C10 の追加（R-432-14）

- `GithubStructureClient.update_issue(number, *, title=None, state=None, state_reason=None)`。`confirmed()` は、送った `title`、`state`、`state_reason` をすべて比べる。前の担当が足した `body` の引数と `_lines` は外す（I-14 が `IssueFacts.body` を外したため、使い道がない）。
- `domain/canonical_structure.apply_changes_lenient(snapshot, changes, *, at, command) -> tuple[StructureSnapshot, tuple[StructureChange, ...]]`：当てられない変更（`SetParent` の子か、`None` でない親がない、`AddBlockedBy` の対象がないか、相手が Scope でも `external` 付きでもない、`RemoveBlockedBy` の対象がない）を飛ばし、残りを `apply_changes` と同じに当てる。`apply_changes` は変えない（`dependency_violations` が使う）。
- `SnapshotStore.reflect` は `apply_changes_lenient` を使い、飛ばした変更があれば、同じ排他の中で `probe.json` を `checked_at: null`、`etags: {}` に書き換える（次の `ensure_fresh` は、どの段階でも確かめで「変化あり」になり、全体を取り直す。形式は同じ版1）。`StructureSnapshotService.reflect_writes(changes, command) -> Reflection(snapshot, skipped)` を足す。`reflect` と `reread` の公開の形は変えない。

### エラーのコード（12章の既存のコードと、新しいもの）

| コード | 終了コード | 次の1手 |
|---|---|---|
| `CANONICAL_NOT_APPLICABLE` | 3 | `scope create`、`scope import github` の `--slug`：「ID とディレクトリ名は Issue の番号から決まる。`--slug` を外す」 |
| `CANONICAL_TITLE_IGNORED`（新、警告） | — | `details`：`given`（渡された値）、`github_title`、`next_step`「題名を変えるなら `spec-dock scope edit <ID> --title …`」（統括の判断 2026-10-29） |
| `SCOPE_KIND_CHANGED` | 3 | I-14 の `SCOPE_KIND_CHANGED_RECOVERY` |
| `CANONICAL_PATH_OCCUPIED` | 3 | 区切りの場所のシンボリックリンクかファイルを確かめて退避する（既存のコード） |
| `CANONICAL_SAVE_HELD` | 3（待つ間に現れ、束を書いた後は `partial` の6。Epic の12章は3だけを挙げる。同じ結果の規則による） | 保留の種類ごとの解き方（I-3 の `SAVE_HELD_NEXT_STEPS`） |
| `PRECONDITION_FAILED`（メッセージが `DESCENDANT_STATUS_UNKNOWN:` で始まる。新しい結果のコードは作らない。従来の `RECURSIVE_REQUIRED` などと同じ形） | 3 | 別のリポジトリの子か、異常のある子を、GitHub で確かめて直す（`workspace validate`） |
| `ACTIVE_LINK_NOT_UPDATED` | 警告 | そのworktreeで `spec-dock active set <ID>`（今あるコード） |
| `CANONICAL_SAVE_UNCONFIRMED` | 6（束を書いた後）、3（書いていない。Epic の12章は6だけを挙げるが、効果のない結果は `failed` という結果の規則に従う） | `spec-dock canonical status` |
| `CANONICAL_BASE_HAS_SPECS` | 3 | 切り替えの後のコミットを基点にする（I-4 の定数） |
| `READINESS_NOT_SATISFIED` | 3 | 今と同じ（ブロッカーと理由を `details` に） |
| `SCOPE_IN_PROGRESS`（新、警告） | — | 別のPCで作業中でないか利用者に確かめる。古い印なら `spec-dock work finish` か GitHub でラベルを外す |
| `CANONICAL_PROGRESS_MARK_FAILED`（新、警告） | — | GitHub で印を付ける（外す）。付けなくても作業は進められる |
| `SCOPE_PUBLICATION_INCOMPLETE` | 6 | `spec-dock scope import github <種類> <番号> [--parent <親>] --title <題名>`（今と同じコード） |
| `SCOPE_DELETE_INCOMPLETE` | 6 | バックアップと今の状態を確かめてから、同じ `scope delete` を新しい `--backup-dir` で（今と同じコード） |
| `GITHUB_*` | 今と同じ | 今と同じ（作成の結果が分からないときは `scope import github`） |
| `GITHUB_SNAPSHOT_STALE` | 警告 | 次の表示か定期の同期で新しくなる |

前の担当の設計にあった `SCOPE_MOVE_INCOMPLETE` は、`scope move` がディレクトリを移さなくなったので使わない。

## data / failure

- 書くもの：GitHub の Issue（作成、題名、状態、ラベル、担当者、親子、依存。本文は書かない）、カタログの作業ツリー（`<区切り>/<ID>/`、区切り、Artifact）と `.runtime/`（束、作成の作業場所）、状態の置き場の `snapshot.json` と `probe.json`、選択の記録と `spec-dock/active/`（今と同じ）、Git の参照と作業ツリー（`work start`）、`--backup-dir`（`scope delete`）。カタログでコミットしない。`.git` に書くのは `work start` の今と同じ参照とチェックアウトだけ。
- 読むもの：構造のスナップショット（`decision`、Artifact は `display`）、GitHub の読み直し、カタログ（`<区切り>/<ID>` を直接）、`state.json`（`work finish`）、テンプレートと規則の元のファイル。
- 失敗：requirement.md の「失敗・境界条件」の表のとおり。書いた後の失敗は、効果を `succeeded`、`unknown`、`not_attempted` で示した `partial`（6）と、続きから整う次の1手。自動で巻き戻さない（GitHub の書き込みも、カタログの書き込みも）。

## 変更対象

- 足すもの、変えるものは「置き場」の表のとおり。
- 変えないもの：従来の `application/direct_*.py`、`scope_*.py`、`work_start.py`、`start_*.py`、`branch_operations.py`、`worktree_observation.py`、`active_links.py`、`github_scope_scaffold.py`、`scope_scaffold.py`、`infra/template_scaffolder.py` と、その下の `.meta.json` の読み書き。従来と共有の引数の解析（`cli/catalog.py` の今の葉の引数。`scope move` の葉を足すだけ）。C2、C3、C4、C6、C9 と I-4、I-14、I-16 の部品の公開の形。テンプレートの配布資産。

## 移行・互換性・rollback

- 版3のリポジトリは、`dispatch()` の振り分けで従来の処理だけを通るので、振る舞いは変わらない。新しい `scope move` は、版3では `CANONICAL_NOT_MIGRATED` で止まる（`--parent` がなければ、その前に使い方の誤り）。コマンドの数と一覧の変化は、許された区分のテストの直しで受ける。
- 版4のリポジトリは、spec-dock を含めて I-10 までないので、利用者の運用への影響はない。
- rollback：PR を `git revert` する。データの移行はない。

## testability

- **単体**：`apply_changes_lenient` と `SnapshotStore.reflect` の飛ばしと古い扱い、`update_issue` の読み直しの `state_reason`（偽の実行器）、前付けの行の除去とリンクの書き換え、題名の規則、区切りを開く・作る・空なら消す、保存の確かめの判定（`state.json` を直接作る）。
- **CLI**（`tests/cli_runtime/test_issue432_*.py`）：I-4 の `tests/support/canonical_scopes.py`（一時の bare とクローン、`canonical link`、`origin` の付け替え、偽の `gh`、一時の `XDG_STATE_HOME`。`CanonicalWorld.directory`/`relative` は `<区切り>/<ID>`）を使う。書き込みの間の1秒は `canonical_writes.WRITE_CLOCK` を記録する時計に替えて、待ちを記録で確かめる。書く順、本文、id は偽の `gh` の記録で、束は `<カタログ>/.runtime/changesets/` の JSON で確かめる。別の区切りの子孫は、番号を1000以上にした偽の Issue で作る。
- **`work finish`**：`origin` を一時の bare のリポジトリのままにし、構造のリポジトリ（`repository_for_checkout`）だけをテストで固定する。`canonical link`（`--no-schedule` なし）の後、`tests/conftest.py` の偽のスケジューラーの `on_kick` が、その場で `canonical sync` の1周期を動かす。時間切れは、注入した時計と待ちで確かめる。もう1つのクローンからの push で、取り込んだだけの場合を確かめる。
- **安全**：テストは `tests/conftest.py` の2段の防ぎ（偽のスケジューラーと、`launchctl`、`systemctl`、`loginctl` の偽物）の中で書き、本物の `gh` に届かないよう、偽の `gh` を `PATH` の先頭に置き、`GH_TOKEN` などを外す（`isolate_user_state`）。
- **従来モード**：版3の作り物で、`scope move` が `CANONICAL_NOT_MIGRATED` で止まることと、ほかの書くコマンドの振る舞いのテストと従来の題名の規則のテストが変更なしで通ることを確かめる。
- **実機**：strict だが、Epic の計画は実機の確かめを I-2、I-3、I-9、I-10 に置く。この Issue では、wheel を入れた一時の venv から、一時ディレクトリの bare とクローンと偽の `gh` で、`scope create`（日本語の題名）→ `scope show` → `work start` → 仕様の編集 → `canonical sync` → `work finish` の流れを外の console で動かす（本物の GitHub、利用者の状態の置き場、定期の実行を使わない。`work finish` の待ちは、別の端末で `canonical sync` を動かして満たす）。

## risk

- **作成の後の失敗**：Issue だけができて、ディレクトリがない。`partial` と `scope import github` の案内で、重ねて作らずに完了できる（AC-432-04）。
- **結果が分からない書き込み**：同じ書き込みを重ねない。読み直しで送った値をすべて比べる。分からなければ `partial` で、GitHub を確かめてからの次の1手を示す。
- **スナップショットの古さ**：書く前に `decision` で確かめ、判断に使う Issue と関係を読み直す（`scope delete` は全体を取り直す）。反映できない変更は、古いものとして扱って次に取り直す。読み直さない Issue（`work start` の前提の Scope、閉じるときの子孫、依存の追加の循環の確かめに使うほかの辺）は、`decision` の5分の新しさで判断する（Epic の決めたとおり）。
- **古いことの印の上書き**：反映できない変更の印（`probe.json` の `checked_at: null`）は、同じときに別のプロセスが確かめの記録を書くと消えうる。そのときは、30分ごとの取り直しまで古いことがある。飛ばす変更は、別のリポジトリの相手などに限られ、まれである。
- **題名の長さの数え方**：256文字をコードポイントで数える。GitHub が別の数え方（UTF-16 など）で数えると、絵文字などを多く含む題名で、GitHub が拒むことがある（そのときは書き込みの失敗として `failed` になり、Issue はできない）。
- **従来の部品の写し**：`work start` と Artifact の公開は、従来の流れの写しを持つ（従来のモジュールを変えないため）。canonical の経路のテストで、従来と同じ効果と止まり方を確かめる。I-13 の撤去で一本にする。
- **`work finish` の待ち**：最大180秒、端末を止める。定期の実行が動いていないと時間切れになり、`canonical status` を示す。
- **`--expect-current` の残る窓**：`worktree create` と `installation` は、従来の処理の取り込みの直前に読み直すが、狭い窓が残る（統括の判断 Q3）。
- **`worktree remove` の窓**：無視されたものがリンクだけと確かめてから `git worktree remove` までに作られた無視されたファイルは消える（従来の `--discard-ignored` と同じ種類の窓。統括の判断 Q4）。
- **I-11 との衝突**：`cli/catalog.py`、`commands/canonical_dispatch.py`、コマンドの一覧のテスト。`origin/main` のマージで取り込む。
