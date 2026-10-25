---
種別: 設計書（Issue）
ID: "iss-00429"
タイトル: "Add Canonical Catalog And Link"
関連GitHub: ["#429"]
状態: "draft"
最終更新: "2026-10-26"
依存: ["requirement.md"]
親: ["epic-00424", "init-00423"]
---

# iss-00429 Add Canonical Catalog And Link — 設計

詳細: [Design Guide](../../../../../../docs/authoring/design.md)

この設計書は、Epic の `design.md` の3章（登録と基準を除く）、4章、5章の C5・C6・C11 に関わる部分、9章、6章と12章の I-2 の行を、実装できる粒度にしたものである。Epic の設計を言い換えず、モジュール、関数、型、エラーのコード、データの形を決める。後の Issue（I-3、I-4、I-5、I-7、I-8）は、この章の「公開の形」をそのまま使う（契約 C3、C4、C5、C6、C11）。変える必要があれば、先に Epic の `design.md` とこの文書を直す。

Epic の記述と違う点、Epic で決まっていなかった点は、統括の判断（2026-10-26。`plan.md` の「統括の判断」）に従う。統括が同じ内容を Epic の文書に反映する。

## 設計目標

- **G-1 従来の経路を変えない**：版3の処理、`application/direct_worktrees.py`、`work_start.py`、`.meta.json` を読み書きするコードは変えない。canonical の処理は新しいモジュールに置き、`CANONICAL_HANDLERS` に登録するだけで足す。
- **G-2 書く前にすべて確かめる**：`canonical link` は、止まる条件（場所、リンク、マウント、書き込みの可否、移行していない仕様、git の版、GitHub の有無）を、何かを書く前にすべて確かめる。書いた後の失敗は `partial` で、効果を正しく示す。
- **G-3 規則は純粋な関数に**：場所、正しいリンクの判定、無視の行、git の版、変更の束、canonical の中身、ツールの設定の1行と判定は、`domain/` の純粋な関数にする。ファイルと Git の観察は `infra/`、手順は `application/` に置く。
- **G-4 カタログへの Git は1つの関数から**：カタログに対するすべての Git の呼び出しは、フックと署名を外す1つの関数を通す（C6）。
- **G-5 環境は注入できる**：OS、コンテナの印、git の版は、1つの値として求め、引数で渡す。テストは値を作って渡すか、求める関数を置き換える（C11）。

## Current / Target

### Current（`origin/main` = `41a4c57c0`、2026-10-26）

- I-1 が、`commands/canonical_dispatch.py` の `CANONICAL_HANDLERS`（`workspace migrate` だけ）と `REPOSITORY_INDEPENDENT_HANDLERS`（空）、`application/canonical_errors.py`（`CanonicalCommandError`、`CANONICAL_NOT_LINKED` と `CANONICAL_NOT_LINKED_RECOVERY` を含む）、`infra/state_root.py` を置いた。版4では、`installation` と `workspace migrate` のほかのコマンドが `CANONICAL_NOT_IMPLEMENTED` で止まる。版3の `canonical …` は `CANONICAL_NOT_MIGRATED` で止まる（ただし `canonical` のコマンドは、まだ一覧にない）。
- `cli/catalog.py` の `LEAF_PATHS` は44個。`spec-dock/.gitignore` の配布資産に、無視の3行はない。
- `worktree create` は `application/direct_worktrees.py` の `create_native_worktree` が行い、リンクは作らない。
- カタログ、リンク、変更の束、環境の判定の部品はない。

### Target

```text
cli/catalog.py                    LEAF_PATHS に canonical link、canonical status（46個）
commands/canonical_dispatch.py    CANONICAL_HANDLERS に canonical link、canonical status、worktree create
application/
  canonical_catalog.py            resolve_layout、observe_catalog、require_linked、catalog_changes（C3、C4）
  canonical_link.py               canonical link の手順、link_after_command（C3）
  canonical_status.py             canonical status
  canonical_tools_check.py        ツールの設定の判定（link と status が使う）
  canonical_worktrees.py          canonical モードの worktree create（今の作成の後にリンク）
  canonical_errors.py             I-2 のコードと次の1手を足す
domain/
  canonical_layout.py             場所、ブランチ名、無視の3行、正しいリンクの判定、git の版（C3）
  canonical_content.py            canonical の中身（形式1）（C5）
  canonical_changeset.py          変更の束（版1）（C4）
  canonical_tools.py              ツールの設定の1行と判定（9章）
infra/
  canonical_git.py                C6 の関数と、カタログのための Git の操作
  canonical_files.py              リンクの観察と置き換え、除外のファイル、無視の行の読み取り
  catalog_lock.py                 カタログの排他（C4）
  catalog_runtime.py              .runtime/、変更の束の書き込み、作成の作業場所（C4）
  catalog_tree.py                 名前で Scope のディレクトリを探す（C3）
  runtime_environment.py          OS、コンテナ、git の判定（C11）
presentation/command_data.py      CanonicalStatusData
assets/spec_dock/.gitignore       無視の3行（spec-dock/ からの相対の形）
```

## 責務・Interface

### 1. 場所、無視の行、正しいリンク（C3。`domain/canonical_layout.py`）

定数：

```python
CANONICAL_BRANCH: Final = "spec-dock/canonical"
CANONICAL_REF: Final = "refs/heads/spec-dock/canonical"
CANONICAL_REMOTE: Final = "origin"
CANONICAL_TRACKING_REF: Final = "refs/remotes/origin/spec-dock/canonical"
CATALOG_RELATIVE: Final = PurePosixPath("spec-dock/.canonical")
LINK_RELATIVE: Final = PurePosixPath("spec-dock/initiatives")
MAIN_LINK_TEXT: Final = ".canonical"
CATALOG_LOCK_REASON: Final = "spec-dock canonical catalog"
EXCLUDE_LINES: Final = ("/spec-dock/.canonical/", "/spec-dock/initiatives", "!/spec-dock/initiatives/")  # info/exclude（リポジトリのルートから）
GITIGNORE_LINES: Final = ("/.canonical/", "/initiatives", "!/initiatives/")                           # spec-dock/.gitignore（spec-dock/ から）
MINIMUM_GIT_VERSION: Final = (2, 38, 0)
```

- I-7（`canonical check` の無視の3行の確かめ）と I-8（移行のスクリプトが写す値）は、`GITIGNORE_LINES` と `EXCLUDE_LINES` を使う（I-8 は写した値をこの定数と比べる）。

型と関数：

```python
@dataclass(frozen=True)
class CatalogLayout:
    main_checkout: Path          # 実際のパス
    common_dir: Path             # 実際のパス（<main>/.git）
    checkout: Path               # コマンドを実行したチェックアウトの実際のパス
    @property catalog -> Path            # main_checkout / CATALOG_RELATIVE
    @property is_main -> bool            # checkout == main_checkout
    @property checkouts -> tuple[Path, ...]   # (main,) か (main, checkout)。リンクを置く順
    def link_path(self, checkout: Path) -> Path      # checkout / LINK_RELATIVE
    def link_text(self, checkout: Path) -> str       # main は ".canonical"、ほかは str(catalog)（絶対パス）

LinkKind = Literal["absent", "symlink", "directory", "file", "other"]
LinkState = Literal["absent", "correct", "wrong_link", "occupied"]

@dataclass(frozen=True)
class LinkObservation:
    path: Path; kind: LinkKind; text: str | None; resolved: Path | None; entries: int | None

def link_state(observed: LinkObservation, *, expected_text: str, catalog: Path | None) -> LinkState
def missing_lines(text: str | None, lines: Sequence[str]) -> tuple[str, ...]
def append_lines(text: str | None, lines: Sequence[str]) -> str
def parse_git_version(reported: str) -> tuple[int, int, int] | None
def git_supported(version: tuple[int, int, int] | None) -> bool
```

- **正しいリンク**（`link_state` が `correct`）：`kind == "symlink"`、`text == expected_text`、`resolved` が `catalog`（カタログの実際のパス。カタログがなければ `None` で、`correct` にならない）と同じ。`kind` が `directory`、`file`、`other` なら `occupied`（`entries` はディレクトリの中の、リンクをたどらずに数えたファイルとディレクトリの数）。そのほかのシンボリックリンク（値が違う、先がない）は `wrong_link`。
- `canonical link` が書き直すのは、値（`text`）が期待と違うリンクと、ないリンクだけである。値が同じでカタログがまだないリンクは書き直さず、カタログを作った後に `correct` になる。
- `missing_lines` は、各行の末尾の空白と `\r` を除いて、行が完全に同じかで比べる。`append_lines` は、末尾に改行がなければ足してから、足りない行を足す。3行がすべてないときだけ、前に1行の注記 `# spec-dock canonical catalog and link (added by spec-dock canonical link)` を置く。
- `parse_git_version` は `git version 2.54.0`、`git version 2.39.5 (Apple Git-154)`、`git version 2.38` を受け付ける。読めなければ `None`（`git_supported` は偽）。

### 2. canonical の中身（C5。`domain/canonical_content.py`）

```python
CANONICAL_FORMAT: Final = 1
FORMAT_FILE: Final = ".spec-dock-canonical.json"
RUNTIME_DIRECTORY: Final = ".runtime"
CANONICAL_ROOT_FILES: Final[Mapping[str, bytes]]   # 名前 → 中身（下の3つ）
INITIAL_COMMIT_MESSAGE: Final = "spec-dock: create canonical"

def read_format(payload: bytes | None) -> int | None     # 整数（真偽値を除く）の format。ない、壊れているは None
def format_writable(version: int | None) -> bool          # version が 1 以上 CANONICAL_FORMAT 以下
```

| 名前 | 中身（バイト列） |
|---|---|
| `.spec-dock-canonical.json` | `{"format": 1}` と改行 |
| `.gitignore` | `.runtime/`、`**/.workbench/*`、`!**/.workbench/README.md`、`**/.workbench/README.md/**` の4行（Epic の5章） |
| `README.md` | このブランチが仕様の内容の正本であること、コードのブランチにマージしないこと、編集は各チェックアウトの `spec-dock/initiatives/` から行い、保存と同期は SpecDock の定期の同期が行うことを書いた短い文書（日本語） |

- I-8 の移行のスクリプトは、この3つを写して持ち、テストで `CANONICAL_ROOT_FILES` と比べる。I-3 の同期は `read_format` と `format_writable` で書く前に確かめる。

### 3. 変更の束と排他（C4）

#### 変更の束（`domain/canonical_changeset.py`）

```python
CHANGESET_VERSION: Final = 1
ChangesetOrigin = Literal["command", "finish"]

@dataclass(frozen=True)
class Changeset:
    origin: ChangesetOrigin; command: str; created_at: str        # "YYYY-MM-DDTHH:MM:SSZ"
    paths: tuple[str, ...]; deletions: tuple[str, ...]           # 正規化し、重複を除き、昇順
    version: int = CHANGESET_VERSION
    def to_json(self) -> dict[str, object]
    @classmethod
    def from_json(cls, payload: object) -> Changeset              # 版が1でない、形が違うときは ValueError

def normalize_catalog_path(value: str | PurePosixPath) -> str    # 規則外は ValueError
def changeset_filename(created_at: datetime, token: str) -> str  # "20261025T120000Z-<token>.json"
```

- JSON の形は Epic の4章のとおり（`{"version": 1, "origin": …, "command": …, "created_at": …, "paths": […], "deletions": […]}`）。
- パスは、カタログのルートからの相対の POSIX のパスで、空、絶対、`.`、`..`、`\`、NUL を含むものと、`.runtime` とその下は受け付けない。ディレクトリを書けば、その下をすべて含む（意味づけは I-3）。
- `token` は16桁の小文字の16進数。

#### 排他（`infra/catalog_lock.py`）

```python
class CatalogLockBusy(TimeoutError): ...
class CatalogLock:
    def __init__(self, catalog: Path, *, timeout: float = 10.0)
    def __enter__(self) -> CatalogLock; def __exit__(...)
```

- `start_lock.py` と同じ作り：カタログのディレクトリを `DirectoryIdentity`（読み取りで開く）で開き、`flock(LOCK_EX | LOCK_NB)` を50ミリ秒ごとに `timeout` 秒まで試す。ファイルを作らない。`timeout` は0〜300の有限の値（そのほかは `ValueError`）。`StartLock` とは別のもので、互いに待たない。
- I-3 の同期は `timeout=0` で試し、取れなければそのカタログを飛ばす。

#### `.runtime/` と変更の束の書き込み（`infra/catalog_runtime.py`）

```python
CHANGESETS_RELATIVE: Final = PurePosixPath(".runtime/changesets")
STAGING_RELATIVE: Final = PurePosixPath(".runtime/staging")
def runtime_directory(catalog: Path, relative: PurePosixPath) -> Path    # なければ作る（リンクをたどらない）
def write_changeset(catalog: Path, changeset: Changeset, *, token: str | None = None) -> Path
def staging_directory(catalog: Path) -> Path
```

- `write_changeset` は `<カタログ>/.runtime/changesets/` に、同じディレクトリの一時ファイル `.<名前>.<乱数>.tmp` に書いて `fsync` し、`os.replace` で `changeset_filename(...)` に置き、ディレクトリを `fsync` する。同じ名前があれば、乱数を変えて作り直す（上書きしない）。カタログの排他の中で呼ぶ（呼ぶ側の責任。`catalog_changes` がそうする）。

#### 書く部品（`application/canonical_catalog.py`）

```python
class CatalogChanges:
    catalog: Path
    def add(self, path: str | PurePosixPath) -> None        # 書いたファイルかディレクトリ
    def delete(self, path: str | PurePosixPath) -> None     # 消したファイルかディレクトリ
    def staging(self) -> Path                               # <カタログ>/.runtime/staging/
    written: Path | None                                    # 出たあとに、置いた束のパス

@contextmanager
def catalog_changes(catalog: Path, *, command: str, origin: ChangesetOrigin = "command",
                    timeout: float = 10.0, clock: Callable[[], datetime] | None = None) -> Iterator[CatalogChanges]
```

- 入るときに、`CatalogLock` を取り（取れなければ `CanonicalCommandError(CANONICAL_LOCK_BUSY)`）、`<カタログ>/.spec-dock-canonical.json` を読んで `format_writable` が偽なら `CanonicalCommandError(CANONICAL_FORMAT_UNSUPPORTED)` で、何も書かずに止まる。
- 出るときに（例外でも）、`add` か `delete` があれば、排他の中で変更の束を1つ書き、排他を放す。例外は、そのまま伝える。
- 中ではネットワークを使ってはならない（呼ぶ側の責任。Epic の4章）。I-5 が Scope の作成、移動、削除、Artifact の作成で使い、`work finish` は `origin="finish"` で使う。

### 4. カタログに対する Git の呼び出し（C6。`infra/canonical_git.py`）

```python
HOOKLESS_CONFIG: Final = ("-c", "core.hooksPath=/dev/null", "-c", "commit.gpgSign=false",
                           "-c", "core.fsmonitor=false", "-c", "gc.auto=0", "-c", "maintenance.auto=false")

@dataclass(frozen=True)
class GitOutput: returncode: int; stdout: bytes; stderr: bytes

def run_catalog_git(cwd: Path, *args: str, git: str = "git", read_only: bool = False, mutation: bool = False,
                    timeout: float = 30.0, pathspecs: Sequence[str] | None = None,
                    environment: Mapping[str, str] | None = None, input: bytes | None = None,
                    returncodes: frozenset[int] = frozenset({0})) -> GitOutput
```

- 呼ぶ形：`<git> -C <cwd> <HOOKLESS_CONFIG> [--no-optional-locks] [--literal-pathspecs] <args…> [--pathspec-from-file=<一時ファイル> --pathspec-file-nul]`。Epic の2つの設定に、fsmonitor のフックと、fetch などが誘発する自動の gc とメンテナンス（`git worktree prune` を含む）を止める3つを足す（統括の判断 C5。SpecDock は prune しないため）。
  - `read_only=True` で `--no-optional-locks` を付ける（読むだけのコマンドと観察で使う）。
  - `pathspecs` があれば、`--literal-pathspecs` を付け、パスを NUL で区切った一時ファイル（システムの一時ディレクトリ。終わったら消す）を `--pathspec-from-file` で渡す（`add`、`reset` など、その引数を受け付けるサブコマンドだけで使う。I-3）。
- 環境変数は、今の `sanitized_git_environment()`（`GIT_` で始まるものを除く）に、`GIT_TERMINAL_PROMPT=0` と、`environment`（I-3 の `GIT_INDEX_FILE` など。明示したものだけ）を重ねる。資格情報の入力を端末で待たないためである。
- `returncodes` にない終了コードは、今の `infra/git_process.GitProcessError`（`argv`、`stderr`、`stdout`、`returncode`、時間切れ）として出す。`mutation=True` の時間切れと、シグナルによる終了は `uncertain`。
- この Issue の後、カタログに対する Git は、この関数のほかから呼んではならない（I-3、I-5 も使う）。この Issue が足す操作：

| 関数 | Git | 備考 |
|---|---|---|
| `list_worktrees(main, *, timeout)` | `worktree list --porcelain -z`（読むだけ） | 今の `git_cli` の NUL の解析を使い、`GitWorktreeRecord` を返す |
| `read_gitdir(directory)` | なし（`<dir>/.git` のファイルを読む） | `gitdir: <パス>`（相対なら `<dir>` から）を返す。ファイルでなければ `None` |
| `admin_branch(admin_dir)` | なし（`<admin>/HEAD` を読む） | `ref: refs/heads/<名前>` の名前 |
| `lock_worktree(main, catalog)` | `worktree lock --reason "spec-dock canonical catalog" <カタログ>` | |
| `repair_worktree(main, catalog)` | `worktree repair <カタログ>` | git は、動いていないほかの作業用のworktreeの `.git` も同時に直す（`repair_worktrees`。2026-10-26 に Git 2.54.0 で確認） |
| `add_catalog_worktree(main, catalog, *, mode)` | `mode="track"`：`worktree add --track -b spec-dock/canonical <カタログ> origin/spec-dock/canonical`。`mode="local"`：`worktree add <カタログ> spec-dock/canonical`。`mode="readd"`：`worktree add -f -f <カタログ> spec-dock/canonical` | `readd` は、カタログの場所の登録だけが残っているとき（下の表）だけ使う |
| `remote_canonical(main)` | `ls-remote --exit-code origin refs/heads/spec-dock/canonical` | 0 は `"present"`、2 は `"absent"`、ほかは `GitProcessError` |
| `fetch_covers_canonical(main)` | `config --get-all remote.origin.fetch`（読むだけ） | 取得の対象の左辺（`+` を除く）が `refs/heads/spec-dock/canonical` に当たるか（`*` を1つまで） |
| `add_fetch_branch(main)` | `remote set-branches --add origin spec-dock/canonical` | 浅いクローンなど。重複を除かないので、呼ぶ側が StartLock の中で `fetch_covers_canonical` を確かめ直してから呼ぶ |
| `fetch_canonical(main)` | `fetch --no-tags origin +refs/heads/spec-dock/canonical:refs/remotes/origin/spec-dock/canonical` | I-3 の周期と同じ形 |
| `resolve_commit(main, ref)` | `rev-parse --verify --quiet <ref>^{commit}`（読むだけ） | なければ `None` |
| `tree_has_path(main, rev, path)` | `ls-tree --name-only <rev> -- <path>`（読むだけ、`pathspecs` なし。`--literal-pathspecs`） | |
| `is_initial_commit(main, oid)` | `rev-list --parents -n 1`、`ls-tree -z`、`hash-object --stdin`（読むだけ） | 親がなく、ツリーの中身が `CANONICAL_ROOT_FILES`（モード 100644）とちょうど同じ |
| `create_initial_commit(main)` | `hash-object -w --stdin`、`mktree`、`commit-tree -m "spec-dock: create canonical"` | 参照は作らない。作者は利用者の Git の設定のとおり |
| `push_initial(main, oid)` | `push --porcelain origin <oid>:refs/heads/spec-dock/canonical`（強制しない） | `*` と `=` は `"pushed"`、`!` は `"rejected"`（終了コード1） |
| `reset_branch(main, oid, *, expected)` | `update-ref refs/heads/spec-dock/canonical <oid> <expected>` | 4a の拒否の後だけ。ブランチがまだ `expected`（手元の初期のコミット）のときだけ動かす |
| `catalog_change_summary(catalog)` | `status --porcelain=v2 -z --untracked-files=all` と `ls-files -z --cached --others --exclude-standard`（読むだけ） | 未保存の数と、追跡しているか未保存の、名前が `*.conflict-*` のパス（同期が保存した別名ファイルも示すため） |
| `unpushed(catalog)` | `rev-list --count`、`log --reverse --format=%cI`（`origin/spec-dock/canonical..HEAD`、読むだけ） | 取得の参照がなければ `None` |

### 5. 環境の判定（C11。`infra/runtime_environment.py`）

```python
SystemName = Literal["darwin", "linux"]
CONTAINER_MARKER_FILES: Final = ("/.dockerenv", "/run/.containerenv")
CONTAINER_ENVIRONMENT_KEYS: Final = ("container", "REMOTE_CONTAINERS", "CODESPACES")

@dataclass(frozen=True)
class GitInstallation:
    path: str | None                      # PATH で見つかった git の絶対パス
    version: tuple[int, int, int] | None
    reported: str | None                  # git --version の1行目
    @property supported -> bool           # git_supported(version)

@dataclass(frozen=True)
class RuntimeEnvironment:
    system: SystemName
    container_markers: tuple[str, ...]    # 見つかった印（ファイルのパスか環境変数の名前）
    git: GitInstallation
    environ: Mapping[str, str]
    @property container -> bool           # 印が1つ以上
    @property codex_sandbox -> bool       # "CODEX_SANDBOX" in environ
    @property claude_code -> bool         # "CLAUDECODE" in environ
    @property home -> Path | None         # environ["HOME"]（絶対パスのときだけ）

def detect_runtime_environment(environ: Mapping[str, str] | None = None, *, root: Path = Path("/"),
                               runner: Callable[..., subprocess.CompletedProcess[bytes]] = subprocess.run,
                               timeout: float = 10.0) -> RuntimeEnvironment
```

- `system` は `sys.platform`（`dispatch()` が linux と darwin のほかを先に止める）。印のファイルは `root` の下で確かめる（テストは一時ディレクトリを渡す）。git は `shutil.which("git", path=environ["PATH"])` で探し、`[path, "--version"]` を `GIT_` を除いた環境で実行する（見つからない、失敗した、読めないときは `version=None`）。
- **注入の仕方**：手順の関数（`link_checkout`、`observe_catalog`、`require_linked`、`link_after_command` など）は `environment` を引数で受け取る。コマンドの処理は、`runtime_environment.detect_runtime_environment()` をモジュールの属性として呼ぶので、CLI のテストは `monkeypatch.setattr(runtime_environment, "detect_runtime_environment", …)` で置き換えられる。
- I-3 は、`RuntimeEnvironment` に既定値のある項目（systemd のユーザー、linger）を足し、この関数に判定を足す。

### 6. カタログの観察（`application/canonical_catalog.py`）

```python
def resolve_layout(context: GitContext) -> CatalogLayout     # CANONICAL_UNSUPPORTED_LAYOUT

CatalogState = Literal["ready", "repair", "readd", "absent", "occupied", "elsewhere", "foreign"]
# occupied には、カタログが別のブランチにいる場合（off_branch）も入る

@dataclass(frozen=True)
class CatalogObservation:
    layout: CatalogLayout
    state: CatalogState
    registered: GitWorktreeRecord | None          # spec-dock/canonical の登録（あればちょうど1つ）
    locked: bool
    moved: bool                                   # 登録のパスがこのプロセスから見えない（mainの移動）
    gitdir: Path | None                           # <カタログ>/.git の gitdir
    entries: int | None                           # occupied のときの数
    links: tuple[LinkView, ...]                   # LinkView(checkout, observed, state, expected)
    exclude_missing: tuple[str, ...]              # info/exclude に足りない行
    gitignore_missing: tuple[str, ...]            # このチェックアウトの spec-dock/.gitignore に足りない行
    detail: str | None                            # 止まる理由の説明（パスを含む）
    registered_exists: bool | None                # elsewhere のとき、登録のパスが存在するか
    off_branch: str | None                        # カタログが spec-dock/canonical 以外にいるとき、その名前
    def link_for(self, checkout: Path) -> LinkView

def observe_catalog(layout: CatalogLayout, environment: RuntimeEnvironment, *, timeout: float) -> CatalogObservation
```

- **mainのチェックアウト**（`resolve_layout`）：`context.common_dir` の名前が `.git` で、`(親 / ".git")` の実際のパスが `context.common_dir` と同じなら、親がmainのチェックアウトである。そうでなければ `CANONICAL_UNSUPPORTED_LAYOUT`。`--path-format=absolute --git-common-dir` の値は `resolve_context` が求めた `common_dir`（実際のパス）と同じものを使う。
- `observe_catalog` は読むだけである（Git は `read_only=True`、ネットワークなし、書き込みなし）。カタログの状態は次の表で決める（上から順に当てる）。

| カタログの場所 | Git の登録 | 状態 | `canonical link` がすること |
|---|---|---|---|
| ない（`lstat` が ENOENT。権限の失敗は「ない」にしない） | `spec-dock/canonical` の登録がない | `absent` | 作る（下の「作るとき」） |
| ない | 登録がちょうど1つで、カタログの場所を指す（同じ実際の親ディレクトリの同じ名前。`git clean -ffdx` の後） | `readd` | `git worktree add -f -f <カタログ> spec-dock/canonical`、lock（prune と unlock は使わない。統括の判断 B1） |
| ない | 登録が、ほかのパス（存在するかどうかによらない） | `elsewhere` | 止まる（`CANONICAL_PATH_OCCUPIED`） |
| ファイル、シンボリックリンク、`.git` ファイルのないディレクトリ、gitdir の名前の管理ディレクトリ（HEAD のあるもの）が今の共通ディレクトリにない | — | `occupied` | 止まる（`CANONICAL_PATH_OCCUPIED`）。中身を消さない |
| `.git` の gitdir の先が存在し、今の管理ディレクトリと別の実体（別のリポジトリのworktree） | — | `occupied` | 止まる |
| 管理ディレクトリの HEAD が `spec-dock/canonical` でない（別のブランチ、detached） | — | `occupied`（`off_branch`） | 止まる。次の1手は `git -C <カタログ> switch spec-dock/canonical` |
| 管理ディレクトリはあるが、`spec-dock/canonical` がほかのパスの登録でもチェックアウトされている | — | `elsewhere` | 止まる |
| 登録のパスと gitdir の先が、どちらも存在し、カタログと管理ディレクトリと同じ実体（`samefile`。文字列は別名でもよい） | — | `ready` | lock されていなければ lock |
| 登録のパスが存在し、カタログと別の実体 | — | `occupied` | 止まる（別のディレクトリの登録かもしれないため。統括の判断 C7） |
| 登録のパスか gitdir の先が、このプロセスから見えない | — | コンテナの印があれば `foreign`、なければ `repair`（登録のパスが見えなければ `moved`） | `foreign` は止まる。`repair` は `git worktree repair <カタログ>`、lock されていなければ lock。`moved` なら警告 `CANONICAL_MAIN_MOVED` |

  - パスは、文字列ではなく実体（デバイスと inode）で比べる。`repair` は、記録されたパスが見えないときだけ行う。別名のパスでマウントした環境（記録が同じ実体の別名を指す）で `repair` すると、git がホストの全worktreeの `.git` を別名のパスに書き換えるためである（統括の判断 C7）。
  - `elsewhere` の次の1手（`elsewhere_next_step`）は、登録のパスが存在すれば「そのworktreeで別のブランチへ切り替える（`git -C <パス> switch <ブランチ>`）。SpecDock はそのworktreeに触れない」、存在しなければ「示した登録を確かめ、lock されていれば `git worktree unlock <パス>`、続けて `git worktree remove <パス>` を実行し、もう一度 `spec-dock canonical link`」とする（2026-10-26 に Git 2.54.0 で、消えた登録が unlock と remove で外れることを確かめた）。SpecDock は `git worktree prune` を実行しない（クローン全体の、選べない消去になるため。統括の判断 B1）。
- **マウントしたチェックアウト**（`foreign`。R-C8）：コンテナの印があり、カタログのディレクトリがあり、その `.git` の gitdir の先か、登録のパスが、このプロセスから見て存在しないとき。`repair` を行うと、ホストの記録（ほかのworktreeの `.git` を含む）をコンテナのパスに書き換えるためである。カタログのディレクトリがないときは、`foreign` にしない（コンテナの中でクローンしたリポジトリの `git clean -ffdx` の後を `readd` で直すため。登録のパスが違えば `elsewhere` で止まる）。

```python
@dataclass(frozen=True)
class LinkedCatalog:
    layout: CatalogLayout
    catalog: Path            # カタログの実際のパス
    tree: CatalogTree        # 7章

def require_linked(context: ProjectContext, *, environment: RuntimeEnvironment | None = None,
                   timeout: float = 30.0) -> LinkedCatalog
```

- 仕様を使う canonical モードのコマンド（I-4、I-5）が、最初に呼ぶ。git の版が足りなければ `CANONICAL_GIT_TOO_OLD`（観察が `worktree list -z` を使うため。統括の判断 C3）、構成が違えば `CANONICAL_UNSUPPORTED_LAYOUT`、`foreign` なら `CANONICAL_FOREIGN_CHECKOUT`、カタログが `ready`（lock の有無は問わない）でないか、このチェックアウトのリンクが `correct` でなければ `CANONICAL_NOT_LINKED`（`recovery` は I-1 の `CANONICAL_NOT_LINKED_RECOVERY`）を `CanonicalCommandError` で出す。何も書かない。
- `environment` を省くと `detect_runtime_environment()` を使う。

```python
def inside_catalog(project: str | None, cwd: Path, *, timeout: float) -> Path | None
def inside_catalog_error(catalog: Path) -> CanonicalCommandError     # CANONICAL_INSIDE_CATALOG
```

- **カタログの中から実行したとき**（統括の判断 C1）：`dispatch()` の `resolve_context` が `ValueError`（宣言がない、壊れている）で止まったときだけ、`inside_catalog` で、解決したworktreeが `spec-dock/canonical` をチェックアウトし、ルートに `.spec-dock-canonical.json` があるかを読むだけで確かめる。そうなら `CANONICAL_INSIDE_CATALOG`（終了コード3、次の1手 `Run the command from the checkout root, or add --project <checkout>.`）で止まる。そうでなければ、元の `PRECONDITION_FAILED` のまま止まる。版3のリポジトリにはカタログがないので、従来モードの振る舞いは変わらない（ふつうの経路に Git の呼び出しを足さない）。

### 7. 名前で Scope のディレクトリを探す（C3。`infra/catalog_tree.py`）

```python
@dataclass(frozen=True)
class ScopeDirectory:
    scope_id: str
    relative: PurePosixPath      # カタログのルートから
    path: Path                   # カタログの実際のパスの下の絶対パス

class ScopeDirectoryAmbiguous(ValueError):     # dispatch で PRECONDITION_FAILED（見つからないのではなく、値の誤り）
    scope_id: str; matches: tuple[ScopeDirectory, ...]

class CatalogTree:
    def __init__(self, catalog: Path)
    catalog: Path
    def directories(self) -> tuple[ScopeDirectory, ...]        # 名前の規則に合うすべて（relative の昇順）
    def find(self, scope_id: str) -> ScopeDirectory | None     # 2つ以上なら ScopeDirectoryAmbiguous
    def require(self, scope_id: str) -> ScopeDirectory         # なければ LookupError（dispatch で SCOPE_NOT_FOUND）
    def duplicates(self) -> Mapping[str, tuple[ScopeDirectory, ...]]
```

- 名前の規則：`^(init|epic|iss)-[0-9]{5,}-[a-z0-9]+(?:-[a-z0-9]+)*$`。`find` の `scope_id` は、I-1 の `parse_scope_id` が受け付ける ID で、`scope_id(kind, number)` で5桁にそろえてから探す（`iss-429` も `iss-00429` として探す）。ディレクトリの名前が `<scope_id>-` で始まり、残りが slug の規則に合うものを探す。
- カタログのルートから、`os.scandir` で、シンボリックリンクをたどらずにすべてのディレクトリを1回だけたどり、結果を持つ（同じ実体の中で使い回す）。`.` で始まる名前のディレクトリ（`.runtime`、`.workbench`、`.git` など）の中は探さない。Scope のディレクトリの中も、さらに探す（Epic は Initiative の下にある）。
- `git ls-files` は使わない（未保存の新しい Scope も見つけるため）。リンクを通さずにカタログの実際のパスを使う。正しいリンクのときだけ使うことは、`require_linked` が保証する。

### 8. `spec-dock canonical link`（`application/canonical_link.py`）

```python
def run_canonical_link(namespace: argparse.Namespace, context: ProjectContext) -> OperationResult[object]  # CANONICAL_HANDLERS
def link_checkout(context: ProjectContext, environment: RuntimeEnvironment, *, command: str,
                  timeout: float, dry_run: bool) -> OperationResult[object]
def elsewhere_next_step(registered: Path | None, *, exists: bool) -> str
def link_occupied_next_step(path: Path) -> str
def main_not_migrated_warning(layout: CatalogLayout) -> Diagnostic
```

- **I-3 の差し込み口**：I-3 は、`link_checkout` と `link_after_command` に既定値のある引数 `schedule: bool = True` を足し（呼ぶ側は変わらない）、手順6と7を、手順4.4（最後の確かめ）の前に足す。`--no-schedule` は `schedule=False` にする。I-2 は、使わない引数を置かない。

手順（番号は Epic の3章のまま。手順6、7は I-3 が手順5と8のあいだに足す）：

1. **前提**：`environment.git.supported` でなければ `CANONICAL_GIT_TOO_OLD`（`details` に見つかった git のパスと版）。`resolve_layout`。宣言の版4は `dispatch()` が保証する（版3は I-1 のとおり `CANONICAL_NOT_MIGRATED`）。git の版を先に確かめるのは、後の Git の呼び出し（`worktree list -z` など）が古い Git で動かないためである。
2. **先に確かめる**（書く前にすべて。ここで止まれば `failed`、効果なし）：
   1. `observe_catalog`。`foreign` は `CANONICAL_FOREIGN_CHECKOUT`、`occupied` と `elsewhere` は `CANONICAL_PATH_OCCUPIED`（`details.path`、`details.entries` か `details.registered_path`）。
   2. リンクを置くチェックアウトのリンクのどれかが `occupied` なら `CANONICAL_LINK_OCCUPIED`（`details.path` と `details.entries`）。作業用のworktreeから実行し、mainのチェックアウトの宣言が版4でない（`probe_workspace_mode(main) != "canonical"`）ときは、mainのリンクを置かず、mainのリンクの状態では止まらない（統括の判断 C6）。
   3. 書き込みの場所に、このプロセスが書けるか（`os.access(<場所、なければ存在する最も近い親>, W_OK)`）。**ネットワークを使う前に**確かめる（統括の判断 C8）。カタログを作るときの場所は、作り方によらず `<共通ディレクトリ>`、`<共通ディレクトリ>/worktrees`、`<main>/spec-dock` である。ほかに、lock と repair は管理ディレクトリ（repair はカタログも）、除外は `<共通ディレクトリ>/info`、リンクは各 `<チェックアウト>/spec-dock`。カタログと除外がそろっていてリンクを置くだけなら、`<チェックアウト>/spec-dock` だけである。書けない場所があれば `CANONICAL_SANDBOX_DENIED`（`details.paths`。次の1手は、`CODEX_SANDBOX` があれば「サンドボックスの外で同じコマンド」、なければ「示したパスの権限を確かめる。サンドボックスの中なら普通の端末で」）。
   4. `absent` なら、作り方を決める（下の「作るとき」）。ここで `ls-remote` を行う（読むだけのネットワーク。接続の失敗は `GITHUB_UNAVAILABLE`、終了コード5）。新しいリポジトリで、既定のブランチのツリーに `spec-dock/initiatives` があれば `CANONICAL_NOT_MIGRATED`。作り方が決まったら、3をもう一度確かめる（場所は3の範囲に入る）。
   5. `--dry-run` なら、ここで、行う予定を `planned` の効果で返す（何もしないなら効果なしの `planned`）。
3. **ネットワークの手順**（排他の外）：作るときだけ。初期のコミットの push（`canonical.remote.create`。拒否は `unchanged`）、取り込み（`git.fetch`。明示の refspec なので、取得の対象の設定によらず `origin/spec-dock/canonical` ができる）。
4. **書く手順**（クローンの `StartLock` の中。既定の5秒で取れなければ `START_LOCK_BUSY`、終了コード3。統括の判断 A10）。ネットワークの手順も、書くカタログ、除外、リンクの手順もないときは、StartLock を取らない（何もしない実行を、ほかの `work start` で止めないため）。StartLock の中で、もう一度 `observe_catalog` をして（ネットワークなし）、2.1 と 2.2 を確かめ直し、次を行う。
   1. カタログ：表の「`canonical link` がすること」。`absent` では、取得の対象に `spec-dock/canonical` がなければ `git.remote.set-branches`（確かめ直してから1行だけ足す）、4a の拒否の後なら `git.branch.reset`、続けて `git.worktree.add`、`git.worktree.lock`。何もしなければ `canonical.catalog` を `unchanged`。
   2. 除外：`info/exclude` に足りない行を足す（`git.info.exclude`）。`info/` がなければ作る。一時ファイルに書いてから `rename` し、もとの権限を保つ。
   3. リンク：リンクを置くチェックアウトの順に、値が期待と違うか、ないリンクを置く（`canonical.link`、対象はリンクのパス）。ないときは `os.symlink`（置き換えない）。違う先のリンクは、同じディレクトリに一時の名前でリンクを作り、置き換える前にその場所がまだシンボリックリンクであることを確かめてから `os.rename` で置き換える（`ln -s` を重ねない）。すべて `spec-dock` のディレクトリを `O_NOFOLLOW` で開いた記述子に対して行う。
   4. 最後に、カタログとリンクを観察し直し、カタログが `ready` でないか、置いたリンクが `correct` でなければ `CANONICAL_NOT_LINKED` の失敗として扱う。
   - 書くときに `PermissionError`、または Git の「Operation not permitted」「Permission denied」で拒否されたら（`os.access` が許しても拒否する Linux の Landlock など）、`CANONICAL_SANDBOX_DENIED`（次の1手は権限の確かめと普通の端末）とする。
8. **ツールの設定**（10章）と、警告：`CANONICAL_TOOL_SETTING_MISSING`、`CANONICAL_TOOL_SETTING_UNKNOWN`、このチェックアウトの `spec-dock/.gitignore` に無視の3行が足りなければ `CANONICAL_IGNORE_RULES_MISSING`（次の1手は `spec-dock installation update`）、`moved` なら `CANONICAL_MAIN_MOVED`、4b なら `CANONICAL_REMOTE_MISSING`、mainのリンクを置かなかったら `CANONICAL_MAIN_NOT_MIGRATED`、カタログの形式が書けなければ `CANONICAL_FORMAT_UNSUPPORTED`（警告。カタログは作る。形式のファイルがないか読めないときの次の1手は「canonical のルートの `.spec-dock-canonical.json` を確かめる」）。

**作るとき**（`absent`。統括の判断 A3、A4）：

| GitHub（`ls-remote`） | ローカルのブランチ | すること |
|---|---|---|
| ある | — | `fetch`。StartLock の中で、取得の対象に入っていなければ `set-branches --add`。ローカルのブランチがなければ `add --track -b`、あれば `add`（ローカル） |
| ない | 中身が初期のコミットだけ（`is_initial_commit`。どう生じたかは問わない。統括の判断 C2） | 4a：そのコミットを push。`fetch`。push できたら `add`（ローカル）。拒否されたら（別のPCが先に作った）、ローカルのブランチを、元の値（手元の初期のコミット）を確かめてから `origin/spec-dock/canonical` に付け替えて（`update-ref`）、`add`（ローカル）。取得の対象は「ある」の行と同じに足す |
| ない | 中身のあるブランチ | 4b：push しない。`add`（ローカル）。警告 `CANONICAL_REMOTE_MISSING`（GitHub の削除の扱いは I-3 の基準と一時停止） |
| ない | ない | 既定のブランチ（`refs/remotes/origin/HEAD`、なければmainのチェックアウトの HEAD）のツリーに `spec-dock/initiatives` があれば、書く前に `CANONICAL_NOT_MIGRATED`（GitHub に canonical がなく、既定のブランチに仕様があること。次の1手は移行の手順書）。なければ、新しいリポジトリとして、初期のコミットを作って push し、`fetch` する。push が拒否されたら（`unchanged`）、GitHub のものを使う。どちらも、StartLock の中で取得の対象を確かめて足してから `add --track -b`（`--single-branch` のクローンでも追跡を設定できるように） |

- 初期のコミットは、`CANONICAL_ROOT_FILES` だけを持つ、親のないコミットで、参照を作らずに push する（push が拒否されても、手元に捨てるブランチを残さない）。push に失敗した後のもう一度の実行は、新しいリポジトリの経路で整う。
- **結果**：すべての効果が `unchanged` なら `unchanged`、そうでなければ `succeeded`（終了コード0）。2の後に失敗したら、それまでの効果を `succeeded`（時間切れなどで分からなければ `unknown`）、失敗した手順を `failed`、残りを `not_attempted` とし、`succeeded` か `unknown` があれば `partial`（終了コード6）、なければ `failed`（Git は `GIT_FAILED`、ネットワークは `GITHUB_UNAVAILABLE`、ファイルは `LOCAL_IO_FAILED`、拒否は `CANONICAL_SANDBOX_DENIED`、StartLock は `START_LOCK_BUSY`）で返す。`recovery` は、ふつうは「もう一度 `spec-dock canonical link` を実行すれば続きから整う」。
- **`data`**（`FamilyData("canonical-link", …)`）：`main_checkout`、`checkout`、`catalog`、`catalog_state`（観察の状態）、`source`（`remote`、`local`、`new`、`null`）、`links`（`[{checkout, path, expected, state}]`。最後の状態）、`exclude`（`{path, added}`）、`changed`。

### 9. SpecDock のほかのコマンドから（C3。`link_after_command`、`application/canonical_worktrees.py`）

```python
@dataclass(frozen=True)
class LinkFollowUp:
    effects: tuple[Effect, ...]        # succeeded / unchanged / planned の効果だけ
    warnings: tuple[Diagnostic, ...]   # 失敗、ツールの設定などの警告（details.next_step）
    link: dict[str, object]            # {"path": …, "state": …}（呼ぶ側の data に入れてよい）

def link_after_command(checkout: Path, *, environment: RuntimeEnvironment | None = None,
                       timeout: float = 30.0, dry_run: bool = False) -> LinkFollowUp
```

- `checkout` について `resolve_context` をして、`link_checkout` と同じ手順を行う。**呼ぶ側は StartLock を持ってはならない**（この関数が StartLock を取るため。呼ぶ側が持っていると、5秒待って `START_LOCK_BUSY` になり、リンクは置かれない）。canonical の `work start`（I-5）は、選択を記録して StartLock を放した後に呼ぶ（統括の判断 A1）。
- 失敗は、呼ぶ側の結果を変えずに返す：`link_checkout` が `failed` か `partial` を返したとき、または `CanonicalCommandError`、`GitProcessError`、`OSError`、`ValueError`、`RuntimeError` を出したとき（宣言がない、構成が違う、など）は、そのコード（`START_LOCK_BUSY` を含む）を警告のコードにした `Diagnostic`（`details.next_step` に、その失敗の次の1手。どれも `spec-dock canonical link` を含む。`details.effects` にすべての効果）を返す。`effects` には、`succeeded`、`unchanged`（`dry_run` では `planned`）の効果だけを入れる（呼ぶ側の `succeeded` の結果を壊さないため）。対象のチェックアウトの宣言が版4でなければ、何もせずに警告 `CANONICAL_CHECKOUT_NOT_MIGRATED` を返す（止まるコードの `CANONICAL_NOT_MIGRATED` を警告に使い回さない。統括の判断 C6 の考え方）。チェックアウトがなく `dry_run` なら、`canonical.link` の `planned` の効果だけを返す。
- **canonical モードの `worktree create`**（`create_worktree_and_link`。`CANONICAL_HANDLERS["worktree create"]`）：
  1. `--expect-current` があれば、`CANONICAL_NOT_IMPLEMENTED` で止まる（従来の確かめは `.meta.json` を読むため。選択の解決は I-4。統括の判断 A2）。
  2. 今の `direct_worktrees.create_native_worktree(namespace, context)` をそのまま呼ぶ。
  3. 結果が `succeeded` か `planned` なら、作ったworktreeについて `link_after_command(..., dry_run=namespace.dry_run)` を呼び、効果と警告を結果の末尾に足し、`data.result.canonical_link` に `link` を入れる。`failed` と `partial` は、そのまま返す。

### 10. ツールの設定（9章。`domain/canonical_tools.py`）

```python
CODEX_CONFIG_FILE: Final = "~/.codex/config.toml"
CODEX_SECTION: Final = "[sandbox_workspace_write]"
CLAUDE_USER_SETTINGS_FILE: Final = "~/.claude/settings.json"

def codex_setting_line(catalog: Path) -> str          # 'writable_roots = ["<catalog>"]'
def claude_setting_line(catalog: Path) -> str         # '{ "permissions": { "additionalDirectories": ["<catalog>"] } }'
def claude_allows(payloads: Sequence[tuple[Path, object]], catalog: Path, *, home: Path | None,
                  resolve: Callable[[Path], Path] = lambda path: path) -> bool | None
```

- 1行のパスは JSON の文字列として書く（`json.dumps(str(catalog))`。TOML の基本の文字列とも同じ表し方）。
- `claude_allows`：読んだ設定（ファイルのパスと JSON の値）ごとに、`permissions.additionalDirectories` の各要素（`~` で始まれば `home` で展開し、相対なら設定のファイルのプロジェクトのルート（`.claude` の親）から求め、`resolve` で実際のパスにする。呼ぶ側は `os.path.realpath` を渡す）が、カタログか、その親なら真。どの設定にもなければ偽。JSON として読めない、または `permissions` か `additionalDirectories` の形が違う設定があり、ほかに真がなければ `None`（判定できない）。設定のファイルが1つもなければ偽。
- 判定（`application/canonical_tools_check.py` の `tool_findings(layout, environment) -> (tools の項目, 警告)`。`canonical link` と `canonical status` が使う）：
  - Codex：作業用のworktreeで `environment.codex_sandbox` のとき、`os.access(<カタログ>, W_OK)` が偽なら、`CANONICAL_TOOL_SETTING_MISSING`（`details.tool = "codex"`、`file`、`section`、`line`）。
  - Claude Code：作業用のworktree（`not layout.is_main`）のとき、`~/.claude/settings.json`、`<チェックアウト>/.claude/settings.json`、`<チェックアウト>/.claude/settings.local.json` を読むだけ読み（ないファイルは飛ばす）、`claude_allows` が偽なら `CANONICAL_TOOL_SETTING_MISSING`（`details.tool = "claude_code"`、`file`、`line`）、`None` なら `CANONICAL_TOOL_SETTING_UNKNOWN`（`details.sources`）。`environment.claude_code`（`CLAUDECODE`）は、`tools` の項目に示すだけで、判定の要否を変えない（作業用のworktreeでは、いつも確かめる。統括の判断 C4）。
  - mainのチェックアウトでは、どちらも示さない。
- 警告の `message` には、次の1手（ファイル、節、1行）をそのまま書く（文字の出力でも見えるようにするため）。

### 11. `spec-dock canonical status`（`application/canonical_status.py`）

```python
def run_canonical_status(namespace: argparse.Namespace, context: ProjectContext) -> OperationResult[object]

@dataclass(frozen=True)
class CanonicalStatusData:        # presentation/command_data.py
    catalog: dict[str, object]; link: dict[str, object]; exclude: dict[str, object]; access: dict[str, object]
    tools: dict[str, object]; sync: dict[str, object]; changes: dict[str, object]; format: dict[str, object]
    git: dict[str, object]; snapshot: dict[str, object]; dashboard: dict[str, object]; structure: dict[str, object]
    kind: str = "canonical-status"
```

- どの項目も `status`（`ok`、`problem`、`unknown`、`not_implemented`）と `next_step`（問題のときの次の1手。なければ `null`）を持つ。

| 項目 | I-2 の中身 |
|---|---|
| `catalog` | `path`、`state`（観察の状態）、`exists`、`branch`、`head`、`locked`、`registered_path`、`registration_matches`。`ready` で lock されていれば `ok` |
| `link` | `links`（`[{checkout, path, expected, actual, state, entries}]`）。すべて `correct` なら `ok`。作業用のworktreeから見て、mainの宣言が版4でなければ、mainのリンクは `CANONICAL_MAIN_NOT_MIGRATED` の問題とする |
| `exclude` | `info_exclude`（`{path, missing}`）、`gitignore`（このチェックアウトの `spec-dock/.gitignore` の `{path, missing}`） |
| `access` | `readable`、`writable`（`os.access(<カタログ>, R_OK \| X_OK)`、`W_OK`）。カタログがなければ `unknown` |
| `tools` | `codex`（`{sandbox, writable, needed, file, section, line}`）、`claude_code`（`{session, needed, configured, sources, file, line}`） |
| `format` | `version`、`supported_max`（1）、`writable` |
| `git` | `path`、`version`、`supported`、`minimum`（`2.38.0`）。今の `PATH` の git。登録簿の git は I-3 |
| `changes` | `unsaved`、`conflict_files`、`unpushed`、`oldest_unpushed_at`。`holds` と `blocking` は `not_implemented`（I-3）。別名ファイルがあれば `next_step` に「中身を元のファイルに統合してから別名ファイルを消す」（警告にはしない。同期の項目の警告は I-3）。未pushが10分を超えたときの警告（R-C6）は、`state.json` の `unpushed_since` を使う I-3 が足す |
| `sync`、`snapshot` | `{"status": "not_implemented", "next_step": null, "owner": "iss-00430"}`。I-3 が置き換える関数 `sync_item(layout, environment)`、`snapshot_item(layout, environment)` が返す |
| `dashboard` | `{"status": "not_implemented", "next_step": null, "owner": "iss-00438"}` |
| `structure` | `{"status": "not_implemented", "next_step": null, "owner": "iss-00431"}`（`--structure` の引数は I-4 が足す） |

- 問題（`catalog`、`link`、`exclude`、`access`、`tools`、`format`、`git` の `problem`）ごとに、`warnings` に1件の `Diagnostic`（`details.item`、`details.next_step`）を入れる。結果は `succeeded`（終了コード0）。mainのチェックアウトが見つからない構成だけ `CANONICAL_UNSUPPORTED_LAYOUT`（`failed`、終了コード3）。
- 問題のコードと次の1手：

| 問題 | コード | 次の1手 |
|---|---|---|
| カタログがない、`readd`、`repair`、lock されていない、リンクがない、違う先 | `CANONICAL_NOT_LINKED` | `spec-dock canonical link` |
| カタログの場所がふさがっている、別のブランチ、`elsewhere` | `CANONICAL_PATH_OCCUPIED` | 6章の観察の表のとおり |
| リンクの場所に実体がある | `CANONICAL_LINK_OCCUPIED` | 示したパスの中身を確かめて退避してから `spec-dock canonical link`（移行前のコミットなら、元のブランチに戻ってから） |
| mainの宣言が版4でない（作業用のworktreeから） | `CANONICAL_MAIN_NOT_MIGRATED` | mainで移行後のコミットをチェックアウトしてから `spec-dock canonical link` |
| `foreign` | `CANONICAL_FOREIGN_CHECKOUT` | 13章の次の1手 |
| `info/exclude` に行が足りない | `CANONICAL_IGNORE_RULES_MISSING` | `spec-dock canonical link` |
| `spec-dock/.gitignore` に行が足りない | `CANONICAL_IGNORE_RULES_MISSING` | `spec-dock installation update` |
| 読めない、書けない（サンドボックスの外） | `OS_ACCESS_DENIED` | カタログの権限を確かめる |
| ツールの設定 | `CANONICAL_TOOL_SETTING_MISSING`、`CANONICAL_TOOL_SETTING_UNKNOWN` | 10章の1行 |
| 形式 | `CANONICAL_FORMAT_UNSUPPORTED` | 形式が新しければ SpecDock を更新する。形式のファイルがないか読めなければ、canonical のルートを確かめる |
| git が古い、ない | `CANONICAL_GIT_TOO_OLD` | Git 2.38 以上を入れ、`spec-dock canonical link` |

- 読むだけ：リポジトリ、カタログ、`.git`、GitHub、状態の置き場に何も書かない。リモートに問い合わせない（`ls-remote` も `fetch` もしない）。Git は `read_only=True`。git が古くて Git の観察ができないときは、該当の項目を `unknown` にして続ける。

### 12. コマンドの一覧と出力（`cli/catalog.py`、`cli/options.py`、`presentation/`）

- `LEAF_PATHS` の `workspace migrate` の後に、`canonical link`、`canonical status` を足す（46個）。引数は、どちらも共通の引数だけ（`--no-schedule` は I-3、`--structure` は I-4 が足す）。`canonical link` を `MUTATING_LEAF_PATHS` に入れる（`--dry-run` と `--yes` を受け付ける。確認は求めない）。
- `HELP_EFFECTS`：
  - `canonical link`：`Find or create this clone's catalog, lock it, add the ignore rules and link the main checkout and this checkout.`（I-3 が Epic の12章の文に直す）
  - `canonical status`：`Read catalog, link, ignore rules, access and tool settings; no changes.`
- `HELP_PRECONDITIONS`、`_READS_BY_ROOT["canonical"]`、`_DOES_NOT_BY_ROOT["canonical"]`、`_JSON_DATA_BY_ROOT["canonical"]` と、`_help_spec` の2つのコマンドの個別の文、`cli/options.py` の `_recovery_help`（`canonical link` は「もう一度 `spec-dock canonical link` を実行すれば続きから整う」）を書く。
- `presentation/command_data.py` に `CanonicalStatusData` を足し、`render_text` は `FamilyData` と同じく JSON の形で示す。
- 配布資産の `docs/reference_cli.md` に `C45 canonical link`、`C46 canonical status` の行を足し、全体の数を46にする。`docs/README.md` と、リポジトリの `README.md` の「44」を「46」にする。

### 13. エラーと警告のコード（C8 の一部。`application/canonical_errors.py` に足す）

| コード | 種類 | 終了コード | 出す場面 | `recovery` / `details.next_step` |
|---|---|---|---|---|
| `CANONICAL_UNSUPPORTED_LAYOUT` | エラー | 3 | mainのチェックアウトがない構成 | `Use a clone whose main checkout holds the .git directory; bare and separate-git-dir layouts are not supported.` |
| `CANONICAL_GIT_TOO_OLD` | エラー | 3 | git が 2.38 より前か、ない | `Install Git 2.38 or later, then run spec-dock canonical link again.` |
| `CANONICAL_FOREIGN_CHECKOUT` | エラー | 3 | マウントしたチェックアウト | `Saving and syncing run on the host; in this container only read and write the spec files, or clone the repository inside the container and run spec-dock canonical link.` |
| `CANONICAL_PATH_OCCUPIED` | エラー | 3 | カタログの場所、`elsewhere` | 状況ごとの文（6章）。どれも SpecDock は消さないと書く |
| `CANONICAL_LINK_OCCUPIED` | エラー | 3 | リンクの場所に実体 | `Inspect <path> and move its contents aside, then run spec-dock canonical link; SpecDock does not delete it. After checking out a pre-migration commit, switch back first.` |
| `CANONICAL_SANDBOX_DENIED` | エラー | 3（書いた後の拒否は `partial` の6） | 書く場所に書けない、書くときに拒否された | `CODEX_SANDBOX` があれば `Run the same command outside the sandbox (in a normal terminal).`、なければ `Check the permissions of the listed paths; inside a sandbox, run the same command in a normal terminal.` |
| `CANONICAL_LOCK_BUSY` | エラー | 3 | カタログの排他（`catalog_changes`） | `Wait a moment, then run the same command again.` |
| `CANONICAL_FORMAT_UNSUPPORTED` | エラー（`catalog_changes`）、警告（`canonical link`、`canonical status`） | 3 | 形式が1より大きいか、読めない | 新しい形式：`Update SpecDock; this catalog uses a canonical format it cannot write.`。ない、読めない：`Check that the root of the spec-dock/canonical branch has a valid .spec-dock-canonical.json; SpecDock writes only a catalog that declares format 1.` |
| `CANONICAL_INSIDE_CATALOG` | エラー | 3 | カタログのworktreeの中から実行した（統括の判断 C1） | `Run the command from the checkout root, or add --project <checkout>.` |
| `CANONICAL_NOT_MIGRATED` | エラー | 3 | 新しいリポジトリで、既定のブランチに仕様がある（I-1 のコードを使う） | I-1 の `NOT_MIGRATED_RECOVERY` |
| `CANONICAL_NOT_LINKED` | エラー（`require_linked`）、問題（`canonical status`） | 3 | リンクかカタログが正しくない | I-1 の `CANONICAL_NOT_LINKED_RECOVERY`（`spec-dock canonical link`） |
| `START_LOCK_BUSY` | エラー（`canonical link`）、警告（`link_after_command`） | 3 | クローンの StartLock が取れない | `Wait a moment, then run spec-dock canonical link again.` |
| `CANONICAL_TOOL_SETTING_MISSING` | 警告 | — | ツールの1行が足りない | 10章の1行（ファイル、節、行） |
| `CANONICAL_TOOL_SETTING_UNKNOWN` | 警告 | — | Claude Code の設定を判定できない | `Check that <file> lists the catalog in permissions.additionalDirectories.` |
| `CANONICAL_IGNORE_RULES_MISSING` | 警告、問題 | — | 無視の3行が足りない | `info/exclude`：`spec-dock canonical link`、`.gitignore`：`spec-dock installation update` |
| `CANONICAL_MAIN_MOVED` | 警告 | — | mainの移動を `repair` で直した | `Git may also have reconnected the linked worktrees; run spec-dock canonical link in each linked worktree (for a worktree that also moved, first run git worktree repair <path> in the main checkout).` |
| `CANONICAL_MAIN_NOT_MIGRATED` | 警告、問題 | — | 作業用のworktreeから実行し、mainの宣言が版4でない（統括の判断 C6） | `Check out a migrated commit (workspace schema 4) in the main checkout, then run spec-dock canonical link there.` |
| `CANONICAL_CHECKOUT_NOT_MIGRATED` | 警告 | — | `link_after_command` の対象のworktreeの宣言が版4でない | `Base the worktree on a commit that declares workspace schema 4, then run spec-dock canonical link in it.` |
| `CANONICAL_REMOTE_MISSING` | 警告 | — | 4b | `Check whether the GitHub branch spec-dock/canonical was deleted; if it was, sync stops (I-3); follow spec-dock canonical status.` |
| `OS_ACCESS_DENIED` | 問題（`canonical status`） | — | カタログを読めない、書けない | `Check the permissions of <catalog>.` |

- I-1 の `CanonicalCommandError` と `canonical_failure` を使う。新しいコードの定数と次の1手は、このモジュールに1か所で置く。

## data / failure

### データの境界

| データ | 置き場 | 書くもの | 読むもの |
|---|---|---|---|
| カタログ | `<main>/spec-dock/.canonical`（canonical のworktree、lock 済み） | `canonical link`（作成、repair、lock） | すべて |
| リンク | `<チェックアウト>/spec-dock/initiatives` | `canonical link`、`link_after_command` | すべて（`require_linked` が確かめる） |
| 除外 | `<共通ディレクトリ>/info/exclude` | `canonical link` | Git、`canonical status` |
| 無視（配布資産） | `spec-dock/.gitignore` | `installation init`、`update` | Git、`canonical status` |
| 変更の束 | `<カタログ>/.runtime/changesets/` | `catalog_changes`（I-5） | I-3 の同期 |
| 作成の作業場所 | `<カタログ>/.runtime/staging/` | I-5 | I-5 |
| canonical の形式 | `<カタログ>/.spec-dock-canonical.json` | 初期のコミット、I-8 | `catalog_changes`、`canonical status`、I-3 |

### 失敗の扱い

| 出来事 | 扱い |
|---|---|
| 版3の `canonical link`、`canonical status` | `CANONICAL_NOT_MIGRATED`（I-1 の振り分け） |
| 書く前の確かめで止まる | `failed`（終了コード3。接続は5）。効果なし |
| 書いた後の失敗 | `partial`（6）、効果ごとの状態、`recovery` に `spec-dock canonical link` |
| GitHub に問い合わせられない（作るとき） | 書く前に `GITHUB_UNAVAILABLE`（5） |
| fetch、push の失敗（ネットワークの手順） | それまでに効果があれば `partial`、なければ `failed`（`GITHUB_UNAVAILABLE`、5） |
| StartLock が取れない | `START_LOCK_BUSY`（3）。ネットワークの手順の効果があれば `partial` |
| `link_after_command` の失敗 | 呼ぶ側の結果を変えず、警告と次の1手 |
| `canonical status` の観察の Git の失敗 | 該当の項目を `unknown` にして続ける |

## 変更対象

| 置き場 | 変更 |
|---|---|
| `src/spec_dock/runtime/domain/canonical_layout.py`、`canonical_content.py`、`canonical_changeset.py`、`canonical_tools.py`（新） | 1、2、3、10章の純粋な規則 |
| `src/spec_dock/runtime/infra/canonical_git.py`、`canonical_files.py`、`catalog_lock.py`、`catalog_runtime.py`、`catalog_tree.py`、`runtime_environment.py`（新） | 3〜7章 |
| `src/spec_dock/runtime/application/canonical_catalog.py`、`canonical_link.py`、`canonical_status.py`、`canonical_tools_check.py`、`canonical_worktrees.py`（新） | 3、6、8、9、10、11章 |
| `src/spec_dock/runtime/commands/runtime_dispatch.py` | `resolve_context` の `ValueError` のときだけ `inside_catalog` を確かめる（6章、統括の判断 C1） |
| `src/spec_dock/runtime/application/canonical_errors.py` | 13章のコードと次の1手 |
| `src/spec_dock/runtime/commands/canonical_dispatch.py` | 3つの登録 |
| `src/spec_dock/runtime/cli/catalog.py`、`cli/options.py` | 12章 |
| `src/spec_dock/runtime/presentation/command_data.py`、`envelope.py` | `CanonicalStatusData` と文字の出力 |
| `src/spec_dock/assets/spec_dock/.gitignore`、`docs/reference_cli.md`、`docs/README.md`、`static-inventory.json` | 無視の3行、2つのコマンドの行と数、`sha256` と `known_old_sha256`（変更の前の中身を足す） |
| `README.md` | コマンドの数（46） |
| `tests/`（新と、許された変更） | testability |

変えないもの：従来の処理（`application/direct_worktrees.py`、`work_start.py`、`direct_*.py`、`scope_query.py`、`start_snapshot.py` など）、`.meta.json` を読み書きするコード、`infra/start_lock.py`、`infra/git_process.py`、`infra/git_cli.py`、I-1 の部品の公開の形、テンプレート、利用側の `spec-dock/` の配布資産（I-9、I-10）。

## 移行・互換性・rollback

- **版3のリポジトリ**：`canonical link` と `canonical status` は、I-1 の振り分けで `CANONICAL_NOT_MIGRATED` になる。`worktree create` は今の処理のまま（`CANONICAL_HANDLERS` は版4でだけ使う）。配布資産の `.gitignore` の3行は、実体の `spec-dock/initiatives/` の中の新しいファイルを無視しない（Epic の3章、確認済み）ので、`installation update` で入れても従来モードは壊れない。版3の利用側の `.gitignore` は、`known_old_sha256` に前の中身があるので、`installation show` で `known-old`、`installation update` で新しい中身になる。
- **版4のリポジトリ**：この Issue の後、`canonical link`、`canonical status`、`worktree create`、`installation`、`workspace migrate` のほかは、まだ `CANONICAL_NOT_IMPLEMENTED` で止まる。版4のリポジトリは、I-10 まで本物には存在しない。
- **rollback**：PRを `git revert` すれば戻る。版3のリポジトリでは、カタログもリンクも作られない。テストのカタログは一時ディレクトリにある。後の Issue（I-3、I-4、I-5）がマージされた後は、部品を使っているので、forward recovery（この部品を直す PR）にする。

## testability

### テストの置き場

| 置き場 | 中身 |
|---|---|
| `tests/unit/domain/test_canonical_layout.py`、`test_canonical_content.py`、`test_canonical_changeset.py`、`test_canonical_tools.py` | 純粋な規則 |
| `tests/unit/infra/test_canonical_git.py` | C6 の関数（引数の形、環境、`--no-optional-locks`、`pathspecs`、終了コード、時間切れ）、各操作。フック（必ず失敗する `post-checkout`、`pre-push`）と `commit.gpgSign=true` |
| `tests/unit/infra/test_catalog_lock.py`、`test_catalog_runtime.py`、`test_catalog_tree.py`、`test_runtime_environment.py`、`test_canonical_files.py` | 排他（別のプロセスで持つ）、変更の束の原子的な書き込み、名前で探す、環境の判定（印、git の版の注入）、リンクと除外 |
| `tests/unit/application/test_canonical_catalog.py` | `resolve_layout`、`observe_catalog` の状態の表、`require_linked`、`catalog_changes` |
| `tests/cli_runtime/test_issue429_canonical_link.py` | AC-429-01〜05、07〜13、16、18〜20 の CLI のテスト |
| `tests/cli_runtime/test_issue429_canonical_status.py` | AC-429-02、05、06、13 の `canonical status` |
| `tests/integration/test_issue429_ignore_rules.py` | AC-429-04 の無視の3行 |
| `tests/support/canonical_repo.py`（新） | 一時の bare のリポジトリと、版4の宣言を持つクローンを作る部品（後の Issue も使う） |

### 一時のリポジトリ（`tests/support/canonical_repo.py`）

```python
remote = bare_remote(tmp_path / "remote.git", files={...}, gitignore=True, declaration={...})
                                                    # main に版4の宣言（と配布資産の spec-dock/.gitignore）のコミット
main = clone(remote, tmp_path / "main", *clone_options)    # user.name と user.email をローカルの設定に置く
linked = add_worktree(main, tmp_path / "linked", "feature")
env = environment(git_version=(2, 54, 0), container=False, environ=None)   # environ=None は今の os.environ
home = isolate_user_state(monkeypatch, tmp_path)           # HOME と XDG_STATE_HOME を一時に、ツールの印を消す
git(root, *args)                                            # GIT_ を除いた環境で git を呼ぶ
```

- `HOME` と `XDG_STATE_HOME` は、いつも一時ディレクトリにする（`isolate_user_state`）。`CODEX_SANDBOX`、`CLAUDECODE`、コンテナの環境変数は消してから、要るテストだけ設定する。
- 環境の判定は、`monkeypatch.setattr(runtime_environment, "detect_runtime_environment", lambda *a, **k: environment)` で注入する（実際の git の版は使わない）。
- 「書けない場所」は、ディレクトリの権限を 555 にして作る（終わったら戻す）。root で動くと `os.access` が真になるので、その場合はテストを飛ばす。

### 従来モードの回帰で変えるテスト（Epic の testability の許された区分）

| テスト | 変えること | 区分 |
|---|---|---|
| `tests/cli_runtime/test_cli_vnext_contract.py::test_vnext_catalog_matches_approved_44_leaf_design` | 数を46に、一覧に2つを足す（名前も合わせる） | コマンドの数と一覧 |
| `tests/cli_runtime/test_issue413_contract.py::test_every_public_leaf_help_describes_the_v2_envelope_without_project_access` | 数を46に | コマンドの数 |
| `tests/integration/test_cli_docs_vnext.py::test_command_reference_covers_all_public_leaves` | 数を46に | コマンドの数（文書） |
| `tests/cli_runtime/test_help_completion_vnext.py`（補完のテスト） | 数を46に（読むだけのコマンドの集合に `canonical status` を足す） | コマンドの数と一覧 |
| `tests/cli_runtime/test_issue428_canonical_mode.py::test_every_command_without_a_canonical_handler_stops_without_writing` | `_leaf_arguments` に2つのコマンドを足す（`CANONICAL_HANDLERS` にあるので飛ばされる） | canonical モードのテスト（版3の振る舞いではない） |

- このほかに、版3の振る舞いを確かめる既存のテストは変えない。最終の品質の関門で `git diff origin/main -- tests/` を一覧にし、報告書に書く。
- 配布資産の値（`static-inventory.json` の `sha256`）を直接確かめるテストはない（2026-10-26 に確かめた）。

### 受け入れ条件との対応

| AC | 確かめ方 |
|---|---|
| AC-429-01 | `test_issue429_canonical_link.py`：bare のリポジトリ、2つのクローン、`git worktree add`、`worktree create` |
| AC-429-02 | `git clean -ffdx`、`mv` による移動（`.git/worktrees/` の名前の一覧が同じ）、実体の `spec-dock/initiatives` を持つコミットへの checkout と戻り |
| AC-429-03 | ツリーの要約（`tree_digest`）。書いた後の失敗は、リンクを置く部品を失敗させる注入 |
| AC-429-04 | `git status --porcelain --ignored` と `git check-ignore`（info/exclude と、配布資産の `.gitignore` を置いた版3のリポジトリ） |
| AC-429-05 | `CODEX_SANDBOX` と権限 555 |
| AC-429-06 | `.git` とカタログとチェックアウトの `tree_digest` が前後で同じ |
| AC-429-07、08 | 環境の注入。`.git/worktrees/` の `tree_digest` |
| AC-429-09 | 2回目の結果と効果。`--dry-run` の前後の `tree_digest` |
| AC-429-10 | bare のリポジトリの参照、コミットの親とツリー。同時の作成は、先のクローンが push した後に、後のクローンの `ls-remote` の答えを「ない」と注入して再現する（後の push は、本物の bare のリポジトリが拒否する）。4a は push の失敗を注入した1回目の後の2回目、4b は bare のリポジトリからブランチを消した後 |
| AC-429-11 | `git clone --single-branch` |
| AC-429-12 | 必ず失敗する `post-checkout`、`pre-push`（`core.hooksPath` をテストのフックのディレクトリに）、`commit.gpgSign=true` |
| AC-429-13 | 一時の `HOME` の `~/.claude/settings.json`、`<worktree>/.claude/settings.local.json`、壊れた JSON |
| AC-429-14 | `test_catalog_tree.py`、`test_canonical_catalog.py`、`test_catalog_lock.py`（`multiprocessing` か `subprocess` で別のプロセス） |
| AC-429-15 | 全体のテスト（許された変更のほかは変えない） |
| AC-429-16 | `worktree create --expect-current`、リンクの失敗と `START_LOCK_BUSY` の注入 |
| AC-429-18 | mainを版3の宣言と実体の `spec-dock/initiatives` のコミットにして、作業用のworktreeから `canonical link`。mainの `spec-dock/initiatives` の `tree_digest` が同じで、mainの `scope list`（従来モード）が動く |
| AC-429-19 | カタログの中へ `chdir` して `canonical status` と `scope list`。宣言のないふつうのリポジトリでは `PRECONDITION_FAILED` |
| AC-429-20 | 管理ディレクトリの `gitdir` と、カタログの `.git` を、同じ実体のシンボリックリンクの別名のパスに書き換える |
| AC-429-17 | `make lint`、`uv run pytest` |

### 実機の確かめ（報告書に書く）

- macOS：外付けのボリュームの一時のリポジトリ（scratchpad の下）と、同じ場所の一時の bare のリポジトリで、`canonical link`（新しいリポジトリ、2つ目のクローン、作業用のworktree）、`canonical status`。
- Codex のサンドボックス：`codex sandbox -P :workspace -C <チェックアウト> -- spec-dock canonical status` などで、`CODEX_SANDBOX` と書き込みの可否の判定、`CANONICAL_SANDBOX_DENIED`、リンクだけのときに通ること、カタログへの `flock` が内と外で効くこと。動かなければ「未確認」。`~/.codex/config.toml` は変えない（一時の `CODEX_HOME` と `-c` の上書きだけを使う）。
- Claude Code：一時の `HOME` か一時の設定のファイル（`--settings`）で、作業用のworktreeから、1行がなければリンク経由の読み書きが拒否され、あれば通ること。利用者の `~/.claude/settings.json` は変えない。確かめられなければ「未確認」。
- Linux（OrbStack の Ubuntu 24.04 の仮想マシン、Git 2.43）：リンク、カタログの排他（`flock`）、書き込みの可否の判定。この Issue のテストを仮想マシンの中でも動かす（`worktree add -f -f` と `repair` の Git 2.43 での動き）。Git 2.38 は手元にないので未確認とする。
- Docker：コンテナに一時のリポジトリを、ホストと**別のパス**にマウントして、`CANONICAL_FOREIGN_CHECKOUT` で止まり、ホスト側の `.git/worktrees/` が変わらないこと。資格情報を写さず、作った仮想マシン、コンテナ、イメージは消す。使えなければ「未確認」。

## risk

| リスク | 影響 | 軽減 |
|---|---|---|
| リンクの置き換えで、実体のファイルやディレクトリを消す | 大 | 実体は止まる。置き換えは、その場所がシンボリックリンクであることを確かめてから `rename`。`os.symlink` は置き換えない。テストでツリーの要約を比べる |
| `git worktree prune` や `-f` で、ほかのworktreeの登録やチェックアウトを壊す | 大 | prune を使わない。`-f -f` は、登録がちょうど1つでカタログの場所のときだけ（統括の判断 B1）。ほかの prunable な登録が残るテスト |
| マウントしたコンテナから、ホストの Git の記録を書き換える | 大 | コンテナの印があり、登録が見えなければ、`repair` の前に止まる |
| 新しいリポジトリの判定の誤りで、移行していない仕様を空の canonical で隠す | 大 | GitHub にもローカルにも canonical がなく、既定のブランチに仕様があれば止まる |
| GitHub の canonical の削除を、空の canonical で上書きする | 大 | 中身のあるローカルのブランチがあれば push しない（4b） |
| 従来モードの経路が変わる | 大 | 従来の関数を変えず、`CANONICAL_HANDLERS` に足すだけ。全体のテスト |
| 同じクローンの同時の `canonical link` | 中 | 書く手順を StartLock の中で、観察し直してから行う |
| `os.access` がサンドボックスの拒否と一致しない | 中 | Codex の seatbelt では一致を確かめた（調査の記録）。Linux の Landlock は実機で確かめ、できなければ未確認とする |
| Claude Code の設定の判定が当たらない | 低 | 判定できないことを示す。文書（I-9）に手順を書く |
| 後の Issue が契約の不足を見つける | 中 | 公開の形をこの文書に書き、I-3、I-4、I-5 の使い方を `plan.md` の handoff に書く |
