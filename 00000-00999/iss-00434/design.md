---
種別: 設計書（Issue）
ID: "iss-00434"
タイトル: "Add Default Branch Spec Check And Workflow"
関連GitHub: ["#434"]
状態: "draft"
最終更新: "2026-10-26"
依存: ["requirement.md"]
親: ["epic-00424", "init-00423"]
---

# iss-00434 Add Default Branch Spec Check And Workflow — 設計

詳細: [Design Guide](../../../docs/authoring/design.md)

この設計書は、Epic の `design.md` の8章（既定のブランチの検査）、1章の版3の止まり方の例外、12章の `canonical check` と `CANONICAL_CHECK_FAILED` の行を、実装できる粒度にしたものである。Epic の設計を言い換えず、モジュール、関数、データの形、失敗のコード、次の1手を決める。後の Issue（I-8、I-9、I-10、I-12、I-13）は、「C7 の公開の形」をそのまま使う。変える必要があれば、先に Epic の `design.md` とこの文書を直す。

## 設計目標

- **G-1 コミットのツリーだけを見る**：`canonical check` は、指定したコミットのツリーとその blob だけを読む。作業ツリー、インデックス、カタログ、状態の置き場、ネットワーク、GitHub を読まず、何も書かない。CI のチェックアウト（浅いクローン、PR のマージのコミット）でそのまま動く。
- **G-2 すべての問題を並べる**：最初の問題で止まらず、6つの調べることをすべて行い、問題を1件ずつ、パスと次の1手を付けて返す。宣言の版3も、その1件である（Epic の `design.md` 1章の例外）。
- **G-3 判定は今の規則を使う**：配布資産の照合は `installation show` の分類（`current`、`known-old`、`missing`、`unknown`、`unsafe`）を、同じ1つの関数で行う。宣言の受け付けは `project_context` の版と `writer_protocol` の規則を使う。
- **G-4 版はファイル1つで決まる**：検査のワークフローが入れる SpecDock の版は、配布資産の版のファイルだけで決まる。版を上げてもワークフローは変えない（R-F2）。
- **G-5 従来モードと今のCIを変えない**：従来の処理、`.meta.json` のコード、`specdock-ci-validate.sh`、`ci.yml` を変えない。

## Current / Target

### Current（`origin/main` の `41a4c57c0`、2026-10-26）

- I-1 が、`commands/canonical_dispatch.py` に `resolve_context` より前に呼ぶ表 `REPOSITORY_INDEPENDENT_HANDLERS`（空）と、`canonical …` を版3で `CANONICAL_NOT_MIGRATED` にする経路を置いた。`canonical` グループのコマンドは、まだ `cli/catalog.py` の `LEAF_PATHS`（44個）にない。
- 配布資産の分類は、`application/direct_installation.py` の `installation show` の中に書かれている（作業ツリーのファイルの SHA-256 を、`static-inventory.json` の `sha256` と `known_old_sha256` に照らす）。
- 版のファイルと、検査のワークフローの見本はない。`pyproject.toml` の版は 0.2.4 で、版のタグはない。
- spec-dock の CI は、`ci.yml` が `.github/scripts/specdock-ci-validate.sh` で、ソースから作った wheel の `workspace validate --ci` を実行する。
- 配布資産 `spec-dock/.gitignore` には、まだ無視の3行がない（I-2 が足す。契約 C3）。

### Target

```text
spec-dock canonical check [--commit REV]
  dispatch() ─ REPOSITORY_INDEPENDENT_HANDLERS["canonical check"] → check_canonical_commit(namespace, cwd)
    resolve_git_context（宣言を読まない）→ resolve_commit(REV) → list_commit_tree(oid)
    → evaluate_commit_tree(entries, read_blob, assets, running_version)   ← 6つの調べること
    → OperationResult（通過 0 / CANONICAL_CHECK_FAILED 7、警告は版の違い）

配布資産（C7）
  spec-dock/system/spec-dock-version          "0.2.4\n"（pyproject.toml の版と同じ）
  spec-dock/docs/ci/spec-dock-check.yml       検査のワークフローの見本（I-8 の cut が .github/workflows/ に写す）

spec-dock のリポジトリ（C7）
  .github/scripts/specdock-ci-check.sh        ソースの wheel で canonical check（I-10 のワークフローが呼ぶ）
  .github/scripts/release-tag-decision.py     版のタグの判定（パッケージを読み込まない）
  .github/workflows/release-tag.yml           main への push で、判定がタグを返したときだけタグを作る
```

## 責務・Interface

### 1. コマンドの一覧と引数（`cli/catalog.py`）

- `LEAF_PATHS` に `"canonical check"` を足す（44 → 45。置き場は `installation uninstall` の後、`help` の前）。`MUTATING_LEAF_PATHS` には入れない（読むだけ）。
- 引数：`--commit REV`（既定 `HEAD`）。共通の引数は今と同じ（`--project`、`--json`、`--timeout` など）。`--yes` は読むだけのコマンドなので受け付けない（今の規則）。`--dry-run` は受け付け、今の読むだけのコマンドの規則（`_render_result` が、終了コード0の結果を `planned` にし、`can_apply` と `blockers` を足す）に従う。何も書かない。
- `HELP_EFFECTS["canonical check"]`：Epic の12章の文 `Check that a commit of the code tree holds no specs and has intact SpecDock files; for CI.`。
- `HELP_PRECONDITIONS["canonical check"]`：Git のチェックアウトと、そのコミット（既定 `HEAD`）が要ること。カタログ、ネットワーク、GitHub のトークン、作業ツリーのモードは要らないこと。問題があれば終了コード7で、各パスと次の1手を返すこと。
- `--help` の節（Target、Reads、Writes、Does not、JSON）は、`canonical check` 用の文を `_help_spec` に足す。`canonical` のグループの既定の文（`_READS_BY_ROOT` など）も足す（I-2、I-3 が同じグループのコマンドを足すときに、自分の文で上書きしてよい）。

### 2. 振り分け（契約 C2 を使う。`commands/canonical_dispatch.py`）

- `REPOSITORY_INDEPENDENT_HANDLERS["canonical check"] = check_canonical_commit` を登録する。ハンドラーは `None` を返さない（いつも結果を返す）。
- `runtime_dispatch.dispatch` は変えない。表に登録すれば、`resolve_context` の前に呼ばれ、例外は今の `except` の連なり（`CanonicalCommandError`、`GitProcessError`、`ValueError` など）で結果になる。
- このため、作業ツリーの宣言が版3、版4、ない、壊れているのどれでも、`CANONICAL_NOT_MIGRATED`、`CANONICAL_NOT_IMPLEMENTED`、`PRECONDITION_FAILED`（宣言による）にならず、コミットのツリーで判定する。

### 3. コミットのツリーの読み取り（`infra/commit_tree.py`、新）

```python
TreeEntryKind = Literal["regular", "symlink", "gitlink", "other"]

@dataclass(frozen=True)
class TreeEntry:
    path: str          # リポジトリのルートからの相対パス（UTF-8 で読めないバイトは backslashreplace）
    kind: TreeEntryKind
    object_id: str

def resolve_commit(root: Path, revision: str, *, timeout: float) -> str | None
def list_commit_tree(root: Path, commit: str, *, timeout: float) -> tuple[TreeEntry, ...]
def read_blob(root: Path, object_id: str, *, timeout: float) -> bytes
```

- `resolve_commit` は `git rev-parse --verify --quiet --end-of-options <REV>^{commit}` で、見つからなければ `None` を返す。`rev-parse --verify` は、知らない名前、あいまいな短い名前、コミットでないもの（`HEAD^{tree}` など。このときは標準エラーに1行出る）を終了コード1で返すので、終了コード1はすべて `None` とする。ほかの失敗（壊れたリポジトリなど）は `GitProcessError` のまま出す。
- `list_commit_tree` は `git ls-tree -r --full-tree -z <commit>` を読む（Epic の8章）。`-r` なのでツリーは並ばず、blob とgitlink だけが並ぶ。種類は、モード `100644`/`100755` と `blob` が `regular`、`120000` が `symlink`、`160000` と `commit` が `gitlink`、それ以外が `other`。
- `read_blob` は `git cat-file blob <id>`。どれも `infra/git_process.run_git` を使い、`.git` に書かない（`ls-tree`、`cat-file`、`rev-parse` はインデックスも lock も取らない）。

### 4. 配布資産の分類（`infra/static_assets.py`）

```python
StaticClassification = Literal["missing", "current", "known-old", "unknown", "unsafe"]

def classify_static_digest(asset: StaticAsset, digest: str | None) -> StaticClassification
```

- `installation show` の中の分類の式を、この関数に移して、`installation show` からも呼ぶ（振る舞いは同じ。`unsafe` は呼び出し元が決める）。`canonical check` も同じ関数を使う（G-3）。

### 5. 検査（`application/canonical_check.py`、新）

```python
# application/canonical_errors.py（I-1 の「コードと次の1手は1か所に置く」に従い、コマンドの終わり方のコードはここ）
CANONICAL_CHECK_FAILED: Final = "CANONICAL_CHECK_FAILED"

# application/canonical_check.py
# C7 の値（I-8 が写し、そのテストでこの定数と比べる）
CI_VERSION_FILE: Final = "spec-dock/system/spec-dock-version"
WORKFLOW_SAMPLE: Final = "spec-dock/docs/ci/spec-dock-check.yml"
WORKFLOW_DESTINATION: Final = ".github/workflows/spec-dock-check.yml"
WORKFLOW_BRANCH_LINE: Final = "branches: [main]"

# Epic の design.md 3章「無視の設定」の3行（spec-dock/ からの相対の形）。C3 の値で、持ち主は I-2。
# I-2 と I-7 のうち、後から main に入る側が、この定数を C3 の定数に置き換える。
SPEC_DOCK_IGNORE_LINES: Final = ("/.canonical/", "/initiatives", "!/initiatives/")

@dataclass(frozen=True)
class CheckOutcome:
    failures: tuple[Diagnostic, ...]
    warnings: tuple[Diagnostic, ...]
    version_file: str | None

def evaluate_commit_tree(entries: Sequence[TreeEntry], read: Callable[[TreeEntry], bytes], *,
                         assets: Sequence[StaticAsset], running_version: str) -> CheckOutcome
def check_canonical_commit(namespace: argparse.Namespace, cwd: Path) -> OperationResult[object]
```

- `evaluate_commit_tree` は、ツリーの一覧と blob の読み手を受け取る、Git に触れない関数である（単体テストで、作り物のツリーで確かめる）。
- `CI_VERSION_FILE` は、`src/spec_dock/asset_layout.py` の `VERSION_FILE`（`spec-dock/spec-dock.version`。退けた engine pin のパスで、`static-inventory.json` の `retired` にある）とは別のものである。取り違えないよう、名前を変えてある。
- 失敗の1件ずつのコード（下の表）は、`data.result.failures[]` の中のコードで、コマンドの終わり方のコードではないので、`canonical_check.py` に置く。I-9 が Epic の12章の表と照らすのは `CANONICAL_CHECK_FAILED` で、失敗の1件ずつのコードは、この設計書の表と照らす。
- `check_canonical_commit` は、`--expect-current` か `--expect-backend` があれば `CanonicalCommandError("PRECONDITION_FAILED", …, recovery=("Run spec-dock canonical check without --expect-current and --expect-backend; it reads a commit tree, not a selection.",))`。`resolve_git_context(namespace.project, cwd)` で Git のルートを求め（宣言は読まない）、`resolve_commit` が `None` なら `CanonicalCommandError("PRECONDITION_FAILED", …, exit_code=3, recovery=("Pass an existing commit with --commit REV, or commit first; canonical check reads a commit tree.",))`。その後、一覧を読み、`evaluate_commit_tree` に `package_static_assets()` と `spec_dock.__version__` を渡す。

#### 調べることと、失敗のコード（`data.result.failures[]` の各要素の `code`）

各要素は `Diagnostic(code, message, details)` で、`details` に必ず `path`（リポジトリのルートからの相対パス）と `next_step`（次の1手の1文）を持つ。1つのパスは、最初に当たった調べることだけで報告する（1→2→3の順）。並びは、調べることの順で、1〜3はツリーの並び（パスの順）、5は配布資産の照合（`static-inventory.json` の並び。パスの順）の後に、無視の3行の1件である。

| 調べること | コード | パス | `details` のほかの項目 | 次の1手（`next_step`） |
|---|---|---|---|---|
| 1 | `SPEC_PATH_TRACKED` | `spec-dock/initiatives` そのものか、その下の各パス | `entry`（`regular`、`symlink`、`gitlink`、`other`） | `Remove the spec paths from this branch with git rm -r --cached -- spec-dock/initiatives, then commit; specs belong on the spec-dock/canonical branch.` |
| 2 | `CATALOG_PATH_TRACKED` | `spec-dock/.canonical` そのものか、その下の各パス | `entry` | `Remove the catalog paths from this branch with git rm -r --cached -- spec-dock/.canonical, then commit; spec-dock canonical link restores the ignore rules.` |
| 3 | `SCOPE_METADATA_TRACKED` | `spec-dock/` の下の、名前が `.meta.json` の各パス（1と2を除く） | `entry` | `Remove the tracked .meta.json files from this branch with git rm --cached, then commit; canonical mode keeps Scope structure in GitHub Issues.` |
| 4 | `WORKSPACE_NOT_MIGRATED` | `spec-dock/workspace.json` | `schema_version: 3` | I-1 の `NOT_MIGRATED_RECOVERY`（`This repository is not migrated (workspace schema 3); follow scripts/migrate-to-canonical/README.md in SpecDock 0.3.0 to migrate it.`） |
| 4 | `WORKSPACE_DECLARATION_INVALID` | `spec-dock/workspace.json` | `reason`：`missing`、`not-regular`、`invalid-json`、`unknown-schema`、`unknown-writer-protocol` | `unknown-schema` で整数の版が4より大きいとき：`Install the SpecDock version named by spec-dock/system/spec-dock-version; this SpecDock knows workspace schema 3 and 4.`。ほか：`Commit spec-dock/workspace.json as {"schema_version": 4, "writer_protocol": "specdock.worktree-writer/v1"}.` |
| 5 | `STATIC_ASSET_INVALID` | 配布資産のパス（`init_only` を除く） | `classification`：`missing`、`unknown`、`unsafe` | `Run spec-dock installation update --target <checkout> --backup-dir <new external directory> --yes and commit the static files; a modified file needs a manual merge.` |
| 5 | `IGNORE_RULES_MISSING` | `spec-dock/.gitignore` | `missing_lines`（足りない行）、`misordered`（`!/initiatives/` が最後の `/initiatives` より前か） | `Add these lines to spec-dock/.gitignore in this order, then commit: /.canonical/, /initiatives, !/initiatives/.` |

- **調べること4**：宣言の blob を `json.loads` で読む（UTF-8 でない、JSON でない、深すぎる入れ子で `RecursionError` になる、はどれも `invalid-json`）。`project_context.workspace_mode` と同じ規則で版を判定し（整数の3か4。真偽値を除く）、`writer_protocol` が `project_context` の既知の2つの値（`specdock.worktree-writer/v1`、`specdock.writer/v1`）のどれかであることを求める（「既知」は `read_workspace_declaration` と同じ範囲）。版3は `WORKSPACE_NOT_MIGRATED` の1件だけを返す（`writer_protocol` は見ない）。
- **調べること5（資産）**：`package_static_assets()` のうち `init_only` でないものを、パスで一覧に照らす。ない → `missing`、`regular` でない → `unsafe`、`regular` なら blob の SHA-256 を `classify_static_digest` で分類し、`current` と `known-old` は通す。`init_only`（`spec-dock/workspace.json`）は、利用者が持つ中身なので照合せず、調べること4で確かめる。消えた資産（`retired`）があっても失敗にしない（`installation update` が外すもので、壊れた資産ではない）。
- **調べること5（無視の3行）**：`spec-dock/.gitignore` が `regular` のときだけ調べる（ない、または `regular` でないときは、資産の失敗だけを返す）。各行の末尾の空白（`\r` を含む）を除いて、`SPEC_DOCK_IGNORE_LINES` の各行と同じ行があるかを見る。あわせて、`!/initiatives/` の最後の行が、`/initiatives` の最後の行より後にあることを求める（Git は後の規則が勝つので、逆だと実体のディレクトリの中の新しいファイルを無視してしまう。Epic の3章の性質を守るため）。
- **調べること5と6の重なり**：版のファイルも `init_only` でない配布資産なので、調べること5で照合する。中身が既知（このパッケージの版か、`known_old_sha256` の古い版）なら5は通り、動いている版と違えば6の警告だけになる。知らない中身なら、5の失敗と6の警告の両方になる。CI では、ワークフローが版のファイルの版を入れるので、6の警告は出ない（手元の別の版の SpecDock で実行したときに出る）。
- **調べること6**：版のファイルが `regular` のとき、中身を UTF-8 で読み、前後の空白を除いた文字列が `spec_dock.__version__` と違えば、警告 `SPEC_DOCK_VERSION_MISMATCH`（`details`：`path`、`expected`（動いている版）、`actual`（読めなければ `null`）、`next_step`：`Run the SpecDock version named by spec-dock/system/spec-dock-version, or run spec-dock installation update and commit to record this version.`）を返す。版のファイルがない、または `regular` でないときは、調べること5の失敗だけで、警告は出さない。

#### 結果

- 通過：`OperationResult("canonical check", "succeeded", FamilyData("canonical-check", result), 0, warnings=…)`。
- 失敗：`status="failed"`、終了コード7、`error=Diagnostic("CANONICAL_CHECK_FAILED", "<件数> problems in commit <短い SHA>; each failure names its path and next step", {"failure_count": <件数>, "commit": <SHA>})`、`recovery=RecoveryInstructions(失敗の next_step を、出てきた順に重ねずに並べたもの)`。効果はない（`effects=[]`）。
- `data.result`（`kind` は `canonical-check`）：

| キー | 中身 |
|---|---|
| `commit` | 調べたコミットの完全な SHA |
| `revision` | 指定した名前（既定 `HEAD`） |
| `valid` | 失敗が0件か |
| `failures` | 上の失敗の一覧（`code`、`message`、`details`） |
| `entry_count` | ツリーの一覧の件数 |
| `package_version` | 動いている SpecDock の版 |
| `version_file` | 版のファイルの中身（前後の空白を除く。ない、読めないときは `null`） |

### 6. 出力（`presentation/envelope.py`）

- JSON は今の v2 の封筒のまま（上の `data`）。
- 文字の出力は、`render_text` に `canonical check` の枝を足し、1行目の後に `commit=<SHA> valid=<true|false> failures=<件数>` と、失敗ごとに `failure [<コード>] path="<パス>" next_step="<次の1手>"`、警告ごとに `warning [<コード>] path="<パス>" next_step="<次の1手>"` を出す（数千件でも1件1行。今の stderr の `warning [code] message` には次の1手が出ないため、R-H2 のために stdout にも出す）。エラーと `recovery` は今の stderr の形。ほかのコマンドの出力は変えない。

### 7. C7 の公開の形（I-8、I-9、I-10、I-12、I-13 が使う）

#### 版のファイル

- 配布資産の元：`src/spec_dock/assets/spec_dock/system/spec-dock-version`。利用側：`spec-dock/system/spec-dock-version`（定数 `CI_VERSION_FILE`）。
- 中身：`pyproject.toml` の `[project].version` の文字列と、改行1つ（例 `0.2.4\n`）。先頭に `v` を付けない。モード `0o644`、`init_only` は偽。
- **版を上げる Issue（I-9 の 0.3.0、I-13 の 0.4.0）の決まり**：`pyproject.toml` の版と同時にこのファイルを書き換え、`static-inventory.json` の `sha256` を直し、前の中身の SHA-256 を `known_old_sha256` に足す。足さないと、古い版のファイルを持つリポジトリで、`installation update` が「知らない中身」として手での統合を求め、`canonical check` が `STATIC_ASSET_INVALID` を返す。単体テスト（`tests/unit/infra/test_issue434_version_file.py`）が、中身と `pyproject.toml` の版が同じことを確かめる。
- この版のファイルは、手元の SpecDock を選ばない（今の CLI が退けた「engine pin」とは別のもの）。使うのは、検査のワークフローが入れる版と、`canonical check` の警告だけである。

#### 検査のワークフローの見本

- 配布資産の元：`src/spec_dock/assets/spec_dock/docs/ci/spec-dock-check.yml`。利用側：`spec-dock/docs/ci/spec-dock-check.yml`（定数 `WORKFLOW_SAMPLE`）。中身は Epic の `design.md` 8章の YAML のとおり（`pull_request` と、既定のブランチへの `push`、`permissions: contents: read`、`ubuntu-latest`、`actions/checkout@v4`、`pipx install "spec-dock @ git+https://github.com/chemitaro/spec-dock@v$(cat spec-dock/system/spec-dock-version)"`、`spec-dock canonical check --json`）。
- 既定のブランチの名前の行は、`branches: [main]`（定数 `WORKFLOW_BRANCH_LINE`）を含む行がちょうど1つである（テストで確かめる）。
- **I-8 の `cut` の決まり**：`migrate.py` は、パッケージを読み込まない1つのファイルなので（Epic の `plan.md` の「Issue をまたぐ契約」）、見本のバイト列を埋め込んで持つ。I-8 のテストは、埋め込んだバイト列が `src/spec_dock/assets/spec_dock/docs/ci/spec-dock-check.yml` とバイト単位で同じこと、写した4つの定数（`CI_VERSION_FILE`、`WORKFLOW_SAMPLE`、`WORKFLOW_DESTINATION`、`WORKFLOW_BRANCH_LINE`）がこのモジュールの定数と同じことを確かめる。`cut` は、そのバイト列を `.github/workflows/spec-dock-check.yml`（定数 `WORKFLOW_DESTINATION`）に写し、`WORKFLOW_BRANCH_LINE` の `main` だけを、そのリポジトリの既定のブランチの名前に置き換える（taikyohiyou_project は `branches: [develop]`）。ほかのバイトは変えない。名前が `^[A-Za-z][A-Za-z0-9._/-]*$` に合わない（YAML の流れの書き方で引用が要る、数として読まれる）ときは、書かずに止まる。`export-legacy` はこのファイルを外す。

#### `.github/scripts/specdock-ci-check.sh`

- 使い方：`specdock-ci-check.sh SOURCE_CHECKOUT TARGET_CHECKOUT EXPECTED_SOURCE_SHA`（`specdock-ci-validate.sh` と同じ）。
- 手順：`specdock-ci-validate.sh` と同じ（SHA の形と一致、ソースが汚れていないこと、`git archive` からの wheel の作成、`--without-pip` の venv への `uv pip install`、`SpecDock CI source=<SHA> wheel_sha256=<…>` の1行）で、最後の1行だけを `"$venv_root/bin/spec-dock" --project "$target_root" canonical check --json` にする。
- 終了コード：引数の誤りは2、SHA の食い違いと汚れたソースは3、作成と導入の失敗はそのコマンドの終了コード、それ以外は `canonical check` の終了コード（通過0、問題あり7）。
- **I-10 の決まり**：spec-dock の `.github/workflows/spec-dock-check.yml` は、見本と同じ `name: SpecDock check`、`on`（`pull_request` と `main` への `push`）、`permissions: contents: read`、ジョブの名前 `spec-dock-check`、`ubuntu-latest` を使う。手順は、`actions/checkout@v4`、`ci.yml` と同じ準備（`actions/setup-python@v5` の 3.11、`python -m pip install uv`）、`bash .github/scripts/specdock-ci-check.sh "$GITHUB_WORKSPACE" "$GITHUB_WORKSPACE" "${{ github.sha }}"` である（spec-dock は、版のタグではなく、PR のコードから作った wheel で検査する。Epic の8章）。`specdock-ci-validate.sh` は I-13 が消す。

#### 版のタグ（`.github/scripts/release-tag-decision.py`、`.github/workflows/release-tag.yml`）

- 判定のスクリプト（`git` の呼び出しは60秒で時間切れ。パッケージを読み込まない。標準ライブラリと `git` を使い、`pyproject.toml` の読み取りは 3.11 以上の `tomllib`、3.10 ではパッケージの依存の `tomli`。GitHub の `ubuntu-latest` の `python3` は 3.11 以上）：

```text
release-tag-decision.py --repo PATH --before SHA --after SHA
  標準出力：1行の JSON {"tag": "v0.3.0" | null, "version": "...", "previous": "..." | null, "reason": "..."}
  環境変数 GITHUB_OUTPUT があれば、そのファイルに "tag=<タグか空>" の1行を足す
  終了コード：判定できたら0、引数の誤りは2、push の後のコミットの pyproject.toml が読めないなど判定できないときは1
```

| `reason` | 条件（上から順に判定） | `tag` |
|---|---|---|
| `before-unavailable` | `--before` がすべて `0`、そのコミットがない、その `pyproject.toml` の版が読めない | `null` |
| `version-unchanged` | 前後の版が同じ | `null` |
| `not-a-release-version` | 新しい版が `X.Y.Z`（数字だけ）の形でない | `null` |
| `below-minimum` | 新しい版が 0.3.0 より小さい | `null` |
| `tag-exists` | `refs/tags/v<版>` が手元にある | `null` |
| `create` | 上のどれでもない | `v<版>` |

- `make lint` の対象は `src/spec_dock` と `tests` なので、このスクリプトには当たらない。この Issue では、ruff（check と format）と mypy を、このスクリプトに手で当てて確かめる（`report.md`）。
- ワークフロー：`on: push: branches: [main]`、`permissions: contents: write`。`concurrency` は付けない（GitHub は同じグループの待ち中の run を新しい run で取り消すので、版を上げた push の run が消され、タグができなくなるため。同時に動いても、タグを作ると判定するのは版を上げた push の run だけである）。`actions/checkout@v4`（`fetch-depth: 0`。前のコミットとタグを読むため）→ 判定（`github.event.before` と `github.sha` は環境変数で渡す）→ `tag` が空でないときだけ `git tag "$TAG" "$GITHUB_SHA"` と `git push origin "refs/tags/$TAG"`。軽量のタグにする（`pip install …@v<版>` に足り、署名者の設定が要らない）。リモートにすでにタグがあれば push が失敗し、上書きしない。

## data / failure

### データ

- 読むもの：コミットのツリーの一覧、宣言、`.gitignore`、版のファイル、`init_only` でない配布資産の blob。パッケージの `static-inventory.json` と資産。
- 書くもの：なし（リポジトリ、`.git`、カタログ、状態の置き場、GitHub のどれにも書かない）。

### 失敗の扱い

| 出来事 | 扱い |
|---|---|
| Git のリポジトリの外、`--project` が worktree のルートでない | 今のコマンドと同じ（`resolve_git_context` の `ValueError` や `GitProcessError`） |
| `--expect-current`、`--expect-backend` | `PRECONDITION_FAILED`（3）。調べない |
| コミットがない（コミットのないリポジトリ、知らない名前） | `PRECONDITION_FAILED`（3）と次の1手。調べない |
| `git ls-tree` や `git cat-file` の失敗、時間切れ | `GIT_FAILED`（5。今の `GitProcessError` の扱い） |
| 調べること1〜5の問題 | 失敗の1件ずつ。終了コード7 |
| 版のファイルの版の違い | 警告。終了コードは変えない |
| 宣言の JSON が壊れている、辞書でない | `WORKSPACE_DECLARATION_INVALID`（`invalid-json`）。ほかの調べることは続ける |

## 変更対象

| 置き場 | 変更 |
|---|---|
| `src/spec_dock/runtime/application/canonical_check.py`（新） | 5章 |
| `src/spec_dock/runtime/infra/commit_tree.py`（新） | 3章 |
| `src/spec_dock/runtime/infra/static_assets.py` | `classify_static_digest` |
| `src/spec_dock/runtime/application/direct_installation.py` | `installation show` の分類の式を `classify_static_digest` の呼び出しにする（振る舞いは同じ） |
| `src/spec_dock/runtime/commands/canonical_dispatch.py` | 表への登録 |
| `src/spec_dock/runtime/cli/catalog.py` | 1章 |
| `src/spec_dock/runtime/presentation/envelope.py` | 6章の文字の出力 |
| `src/spec_dock/assets/spec_dock/system/spec-dock-version`（新）、`src/spec_dock/assets/spec_dock/docs/ci/spec-dock-check.yml`（新） | C7 |
| `src/spec_dock/assets/spec_dock/docs/reference_cli.md`、`docs/README.md`、リポジトリのルートの `README.md` | コマンドの数（44 → 45）と、`canonical check` の行と、見本の置き場 |
| `src/spec_dock/runtime/application/canonical_errors.py` | `CANONICAL_CHECK_FAILED` の定数 |
| `src/spec_dock/assets/static-inventory.json` | 新しい2つの資産、変えた2つの文書の `sha256`、前の中身の `known_old_sha256` |
| `.github/scripts/specdock-ci-check.sh`、`.github/scripts/release-tag-decision.py`、`.github/workflows/release-tag.yml`（新） | C7 |
| `tests/` | 下の testability |

変えないもの：`runtime_dispatch.py`、従来の処理の関数と `.meta.json` のコード、`.github/scripts/specdock-ci-validate.sh`、`.github/workflows/ci.yml`、`provider-ci.yml`、配布資産の `spec-dock/.gitignore`（I-2）、テンプレート、利用側の `spec-dock/`（I-9、I-10 で更新する）。

## 移行・互換性・rollback

- **版3のリポジトリ**：`canonical check` を実行しなければ、何も変わらない。新しい配布資産2つは、`installation update` で足される（従来モードの動きに関係しない。`spec-dock/system/` と `spec-dock/docs/` の下の静的なファイル）。`installation show` の結果は、新しい2つの資産の行が増えるほかは同じ。
- **版4のリポジトリ**：`canonical check` だけが動く（ほかのコマンドは I-1 のとおり `CANONICAL_NOT_IMPLEMENTED`）。
- **I-2 との順**：I-2 が配布資産 `spec-dock/.gitignore` に無視の3行を足すまで、本物の配布資産だけのツリーは `IGNORE_RULES_MISSING` で失敗する（正しい動き）。テストは、無視の3行を持つ `.gitignore` の資産を注入して、通過を確かめる。後から入る側が、`origin/main` のマージで `SPEC_DOCK_IGNORE_LINES` を C3 の定数に置き換え、注入が要らなくなれば外す。
- **版のタグ**：今の版は 0.2.4 なので、マージの後に `release-tag.yml` が動いても、`below-minimum`（または `version-unchanged`）でタグを作らない。最初のタグは I-9（0.3.0）のマージの後にできる。
- **`release-tag.yml` が失敗したとき**：版を上げた push の run が失敗すると、次の push は `version-unchanged` になり、タグは自動ではできない。戻し方は、失敗した run を GitHub の画面で Re-run する（同じ `github.event.before` と `github.sha` で判定し直す）か、そのコミットに軽量のタグを手で作って push する。I-9 と I-13 は、マージの後にタグができたことを確かめる。
- **rollback**：PR を `git revert` すれば戻る。データの移行はない。版のタグが作られた後に戻すときは、タグを残してよい（タグはそのコミットの版を指すだけ）。

## testability

### テストの置き場

| テスト | 確かめること |
|---|---|
| `tests/unit/application/test_canonical_check.py` | `evaluate_commit_tree` の調べることごとの判定（作り物のツリー。パスの種類、版3、宣言の各 `reason`、資産の各分類、`init_only` を照合しないこと、無視の3行の欠けと順、版の違い、1つのパスを1回だけ報告すること、並び） |
| `tests/unit/infra/test_commit_tree.py` | `resolve_commit`、`list_commit_tree`（regular、実行可能、symlink、gitlink、UTF-8 でないパス）、`read_blob` |
| `tests/unit/infra/test_issue434_version_file.py` | 版のファイルと `pyproject.toml` の版、`static-inventory.json` の項目、見本の中身（手順、版のファイルの読み方、既定のブランチの行がちょうど1つ、`canonical check --json`）と定数 |
| `tests/cli_runtime/test_issue434_canonical_check.py` | 一時のリポジトリでの CLI（AC-434-01〜05）。`resolve_context` を呼ばないこと、作業ツリーの宣言によらないこと、`--commit`、コミットのないリポジトリ、`--expect-current`、ネットワークとトークンなし、何も書かないこと、文字の出力 |
| `tests/integration/test_issue434_ci_check.py` | `specdock-ci-check.sh`（ソースから wheel を作る。通過0、問題あり7、SHA の食い違いと汚れたソース、対象を変えないこと） |
| `tests/integration/test_issue434_release_tag.py` | 判定のスクリプトの各 `reason`、今の `pyproject.toml`（0.2.4）でタグを作らないこと、`GITHUB_OUTPUT`、ワークフローの中身 |
| `tests/integration/test_issue434_workflow_sample.py` | 見本の手順のコマンドを見本から取り出して実行する（Install は引数を記録する偽の `pipx`、Check は手元の wheel を入れた環境。正しいツリーで0、仕様のパスで7） |

- 通過のテストは、パッケージの資産に、無視の3行を持つ `.gitignore` を重ねたもの（`tests/support/canonical_check.py` の部品）でツリーを作る。in-process のテストは `canonical_check.package_static_assets` をその部品で置き換え、`specdock-ci-check.sh` のテストは、ソースの写しの `.gitignore` と `static-inventory.json` を同じように直す（どちらも、配布資産の `.gitignore` にすでに3行があれば何もしない）。
- 外のネットワークを使わない。`gh` を使わない。状態の置き場は `XDG_STATE_HOME` を一時ディレクトリにして、何も作られないことを確かめる。

### 従来モードの回帰で変えるテスト（Epic の testability の許された区分）

| テスト | 変えること | 区分 |
|---|---|---|
| `tests/cli_runtime/test_issue413_contract.py`（160行目） | コマンドの数 44 → 45 | コマンドの数 |
| `tests/cli_runtime/test_cli_vnext_contract.py`（17〜65行目） | 一覧に `canonical check` を足し、数を45に | コマンドの数と一覧 |
| `tests/integration/test_cli_docs_vnext.py`（35行目） | コマンドの数 44 → 45 | コマンドの数 |
| `tests/cli_runtime/test_help_completion_vnext.py`（253行目付近） | コマンドの数 44 → 45、読むだけのコマンドの一覧に `canonical check` を足す | コマンドの数と一覧 |
| `tests/cli_runtime/test_issue428_canonical_mode.py` | 全コマンドの引数の表に `canonical check` を足す（I-1 の canonical モードのテストで、版3の振る舞いのテストではない） | コマンドの一覧 |
| `tests/integration/test_issue413_assets.py`（626行目付近） | `installation uninstall` が外す資産の数 84 → 86（新しい2つの資産） | 配布資産の数 |
| `tests/integration/test_issue413_assets.py`（969行目付近） | `installation uninstall` の効果の数 85 → 87（同じ理由） | 配布資産の数 |

- このほかに版3の振る舞いを確かめるテストの変更が要るとわかったら、変えずに止まって統括に聞く。変えたテストと行と理由は `report.md` に一覧で書く。

### 受け入れ条件との対応

| AC | 確かめ方 |
|---|---|
| AC-434-01 | `tests/cli_runtime/test_issue434_canonical_check.py`（問題ごと、と全部を1つのコミットに入れたもの）、`tests/unit/application/test_canonical_check.py` |
| AC-434-02 | 同上（正しいツリー、既知の古い資産） |
| AC-434-03 | 同上（`resolve_context` を失敗させる置き換え、作業ツリーの宣言の4つの場合）、`tests/unit/commands/test_canonical_dispatch.py` に登録の確かめを足す |
| AC-434-04 | 同上（`PATH` から `gh` を外し、トークンの環境変数を消し、`XDG_STATE_HOME` を一時ディレクトリに。`tree_digest` でリポジトリと `.git` と状態の置き場が変わらないこと） |
| AC-434-05 | 同上（版のファイルを別の版にしたコミット） |
| AC-434-06 | `tests/unit/infra/test_issue434_version_file.py` |
| AC-434-07 | `tests/integration/test_issue434_ci_check.py` |
| AC-434-08 | `tests/integration/test_issue434_release_tag.py` |
| AC-434-09 | `tests/integration/test_issue434_workflow_sample.py`。実機：一時の `PIPX_HOME` と `PIPX_BIN_DIR` の `pipx` で、一時のクローンに付けた版のタグから `spec-dock @ git+file://…@v<版>` の形で入れ、`spec-dock canonical check --json` を実行する。本物の GitHub Actions は未確認（I-10） |
| AC-434-10 | `make lint`、`uv run pytest`。`git diff origin/main -- tests/` で、変えた既存のテストが上の表のものだけであることを確かめる |

## risk

| リスク | 影響 | 軽減 |
|---|---|---|
| I-2 より先に入ると、本物の配布資産だけのツリーが「無視の3行がない」で失敗する | 低 | 正しい動き。版4の本物のリポジトリは I-10 からで、それより前に I-2 が入る。テストは注入で通過を確かめ、`report.md` と PR に書く |
| `SPEC_DOCK_IGNORE_LINES` が C3 の定数と二重になる | 中 | 出どころ（Epic の3章）をコードと文書に書き、後から入る I-2 が置き換える |
| 版を上げるときに、版のファイルの前の中身を `known_old_sha256` に足し忘れる | 中 | C7 の決まりとして書き、版のファイルと `pyproject.toml` の版の一致を単体テストで確かめる。I-9、I-13 が版を上げる |
| 仕様のパスが数千あるツリーで、出力が長い | 低 | 1件1行の文字の出力。CI でどのパスを外すかが分かることを優先する |
| `!/initiatives/` の順の確かめが、利用者の `.gitignore` の書き方を誤って咎める | 低 | 最後の行どうしを比べるだけにする。配布資産の `.gitignore` をそのまま使っていれば当たらない |
| 版4で `writer_protocol` が古い既知の値（`specdock.writer/v1`）の宣言を通す。書くコマンドは `require_writer` で止まる | 低 | Epic の「既知である」のとおりにする。SpecDock のコマンドではこの宣言はできない（`installation init` は新しい値を書き、版4の `workspace migrate` は止まる）。失敗にするかは統括に報告して判断を仰ぐ |
| 見本の `pipx install … @v<版>` が、本物の GitHub Actions で動くか | 中 | ここでは手元の wheel と同じ手順で確かめ、本物は I-10 で確かめる（未確認として残す） |
| `release-tag.yml` が誤ってタグを作る | 中 | 判定をスクリプトに分けて単体で確かめる。0.3.0 より小さい版、変わらない版、既存のタグでは作らない。リモートにタグがあれば push が失敗し、上書きしない |
