---
種別: 設計書（Issue）
ID: "iss-00473"
タイトル: "Add Scope Check With CUE"
関連GitHub: ["#473"]
状態: "draft"
最終更新: "2026-10-31"
依存: ["requirement.md"]
親: ["epic-00425", "init-00423"]
---

# iss-00473 Add Scope Check With CUE — 設計

詳細: [Design Guide](../../../docs/authoring/design.md)

## 設計目標

- `cue` を呼ぶ処理を、infra の1つの部品に閉じ込める（道具の確かめ、引数の並び、時間の上限、誤りの文の解析）。
- 1つの Scope の検査（形式の判定、K1 の評価、`findings` の読み取り、保証レベル、説明資料の形）を、application の1つの関数にまとめ、`scope check`、`work finish` の両方が同じ関数を呼ぶ。`scope show` と検査は、保証レベルの読み方を共有する。
- 契約 K3（検査の結果の形）を、`Diagnostic` の一覧として決め、JSON とテキストの両方で、ファイル、項目、直し方を示す。
- Markdown の Scope と、`cue` のない環境での既存の動きを変えない。

## Current / Target

| | 今 | この Issue の後 |
|---|---|---|
| 検査のコマンド | ない | `spec-dock scope check <ID> [--json]`（schema 4）。schema 3 は `CANONICAL_NOT_MIGRATED` |
| `cue` の呼び出し | テストの補助だけ（`tests/support/cue.py`） | `runtime/infra/cue_tool.py`（最低の版 v0.17.1） |
| `work finish` | 保存の確かめの後に閉じる | CUE の Scope は、GitHub を読み直した後、保存の確かめの前に検査し、誤りがあれば止まる |
| `scope show --json` | 保証レベルを返さない | `data.result.assurance` = `{level, reason, source, problem}` |
| `workspace validate`・`doctor` | すべての Scope に `.md` の4つを求める | 形式ごとに必須の文書の組を変える。両方の `requirement` は `SCOPE_FORMAT_CONFLICT` |
| CLI の葉 | 53 | 54（`scope check`）。参照の文書 `reference_cli.md` に C54 を足す |

## 責務・Interface

### 1. `cue` の道具（`runtime/infra/cue_tool.py`）

```python
MINIMUM_CUE_VERSION: Final = (0, 17, 1)
CUE_INSTALL_STEP: Final = "Install cue v0.17.1 or later on PATH (for example: go install cuelang.org/go/cmd/cue@v0.17.1), then run the command again."

class CueToolError(Exception):          # code, message, exit_code (3 か 5), next_step
    ...

@dataclass(frozen=True)
class CuePosition:  file: Path; line: int; column: int        # file は解決した絶対パス

@dataclass(frozen=True)
class CueError:     path: str | None; message: str; positions: tuple[CuePosition, ...]

@dataclass(frozen=True)
class CueRun:       returncode: int; stdout: str; stderr: str

@dataclass(frozen=True)
class CueTool:
    executable: str
    version: str
    def export(self, files: Sequence[Path], *, cwd: Path, timeout: float,
               tags: Mapping[str, str] = {}, expression: str | None = None) -> CueRun: ...

def locate_cue(*, timeout: float) -> CueTool: ...
def parse_cue_errors(stderr: str, *, cwd: Path) -> tuple[CueError, ...]: ...
```

- `locate_cue`：`shutil.which("cue")` で探す。ない → `CUE_NOT_FOUND`（exit 3）。`[cue, "version"]` の1行目を `^cue version v(\d+)\.(\d+)\.(\d+)` で読み、`MINIMUM_CUE_VERSION` 未満、または読めない → `CUE_VERSION_UNSUPPORTED`（exit 3。見つけた版を示す）。`version` の時間切れ・起動の失敗は `CUE_TIMEOUT`・`CUE_FAILED`（exit 5）。
- `export`：`[executable, "export", "--out", "json", *("-t", f"{k}={v}"), *("-e", expression), *map(str, files)]` を、`shell=False`、`cwd`、`capture_output`、`text`、`timeout` で呼ぶ。時間切れ → `CUE_TIMEOUT`、`OSError` → `CUE_FAILED`。終了の状態は呼ぶ側が判断する。
- `parse_cue_errors`：`cue` の誤りの文は、行頭の行が1件の誤り（`<項目の道筋>: <文>:` か `<文>:`）、字下げした行が位置（`<相対パス>:<行>:<列>`）である。道筋は、識別子、引用符の文字列、数字を `.` でつないだ形として読む。道筋の形でない行頭の行は、道筋 `None` の誤りにする。位置のパスは `cwd` からの相対で出るので、`cwd` を基に絶対パスへ直す。字下げした行で位置の形でないものは、直前の誤りの文に足す。
- この部品は、`cue` の誤りの文の意味（どれが重複か）を判断しない（application が判断する）。

### 2. 説明資料の形（`runtime/domain/explanation_shape.py`）

```python
SKELETON_MARKER: Final = "<!-- spec-dock:explanation-skeleton -->"
DESIGN_SYSTEM_CSS: Final = "../../../design-system/ds.css"
DESIGN_SYSTEM_JS: Final = "../../../design-system/ds.js"

@dataclass(frozen=True)
class ExplanationShape:
    skeleton: bool                 # Markdown の中に印が残っている
    problems: tuple[str, ...]      # 形を壊している点（英語の文）。空なら形は正しい

def inspect_explanation(text: str) -> ExplanationShape: ...
```

- `html.parser.HTMLParser` で読む（外の部品を使わない）。
- 形の正しさ（K5）：
  - `type="text/markdown"` かつ `id="ds-source"` の `<script>` が、ちょうど1つ。
  - その中身の先頭（前の空白・改行を除く）が `---` の行で始まる前付けで、閉じる `---` までに、空白だけでない値の `title:` がある。
  - `rel` に `stylesheet` を含み、`href` が `DESIGN_SYSTEM_CSS` の `<link>` がある。
  - `src` が `DESIGN_SYSTEM_JS` の `<script>` がある。
- 「雛形のまま」は、`ds-source` の中身に `SKELETON_MARKER` があるかで決める（形が壊れて `ds-source` がないときは、ファイル全体で探す）。

### 3. 1つの Scope の検査（`runtime/application/scope_check.py`）

```python
ScopeFormat = Literal["markdown", "cue", "conflict"]
MARKDOWN_DOCUMENTS: Final = ("requirement.md", "design.md", "plan.md", "report.md")
CUE_DOCUMENTS: Final = ("requirement.cue", "design.cue", "plan.cue", "report.md")

def scope_format(directory: Path) -> ScopeFormat: ...

@dataclass(frozen=True)
class AssuranceReading:
    level: str | None; reason: str | None
    source: Literal["cue", "unset", "unreadable"]
    problem: Diagnostic | None
    def payload(self) -> dict[str, object]: ...   # {level, reason, source, problem: {code, message} | None}

def read_assurance(directory: Path | None, *, timeout: float, tool: CueTool | None = None) -> AssuranceReading: ...   # 例外を出さない

@dataclass(frozen=True)
class ScopeCheckReport:
    format: ScopeFormat
    checked: bool                  # CUE の評価まで進んだか
    schema: str | None
    assurance: AssuranceReading
    errors: tuple[Diagnostic, ...]
    warnings: tuple[Diagnostic, ...]
    findings: dict[str, list[dict[str, str]]] | None   # 評価が通ったときの findings の全体
    cue_version: str | None
    cue_output: str | None         # 評価の誤りの文の全体（評価が失敗したとき）
    evaluation: dict | None        # 評価が通ったときの JSON の全体（I-5 の描画が使う）

def k1_files(types: Path, repository_root: Path, scope: Path) -> list[Path]: ...   # K1 の並べ方

def check_scope_documents(directory: Path, *, kind: str, shown: str, repository_root: Path,
                          timeout: float) -> ScopeCheckReport: ...
```

- `scope_format`：`requirement.cue` が通常のファイルなら `cue`、さらに `requirement.md` もあれば `conflict`、どちらもなければ `markdown`。
- `read_assurance`（`scope show` と検査が共有。型を使わない）：
  1. ディレクトリがない、形式が `markdown` → `unset`。`conflict` → `unreadable`（`SCOPE_FORMAT_CONFLICT`）。
  2. `locate_cue` の失敗 → `unreadable`（そのコード）。`tool` を渡されたら、`locate_cue` を呼ばずにそれを使う（検査の中で、`cue version` を2度呼ばない）。
  3. `cue export --out json -e assurance requirement.cue`（`cwd` は Scope のディレクトリ）。失敗のうち、誤りが `reference "assurance" not found` だけなら `ASSURANCE_UNREADABLE`、ほかは `CUE_INVALID`（最初の誤りの文）。
  4. 値が `{level, reason}` で、`level` が4つの値のどれか、`reason` が文字列で `str.strip()` 後に空でない（Python の空白の判定。I-1 の `#Text` と同じ範囲）→ `cue`。そうでなければ `ASSURANCE_UNREADABLE`。
- `check_scope_documents` の手順：
  1. 形式が `markdown` → `checked=False`、誤りなし、`assurance` は `unset`。`conflict` → `SCOPE_FORMAT_CONFLICT` の誤りだけを返す（評価しない）。
  2. `locate_cue`（失敗は `CanonicalCommandError` に変えて投げる。`exit_code` と `recovery` は `CueToolError` のもの）。
  3. `design.cue`、`plan.cue` がなければ、1つずつ `SCOPE_DOCUMENT_MISSING` の誤りにし、あるファイルだけで続ける。
  4. `schema` を読む：`cue export --out json -e schema requirement.cue`。
     - 誤りの文があり、`reference "schema" not found` だけなら、`CUE_INVALID`（`field: schema`、`requirement.cue` に `schema: "specdock/v1"` を書くよう示す）。ほかの誤りなら、それを `CUE_INVALID` に変える。どちらも評価に進まない（説明資料の検査は行う）。
     - 値が文字列で `^specdock/v[1-9][0-9]*$` に合わない → `CUE_INVALID`（`field: schema`）。評価に進まない。
     - 形は合うが `cue_schemas.schema_directory` が `None` → `CanonicalCommandError(CUE_SCHEMA_UNSUPPORTED, exit_code=3)`。`details.shipped` と `recovery` に、持っている版（`shipped_schemas()`）と、SpecDock を上げる次の手順を示す。
  5. K1 の評価：`k1_files(types, repository_root, scope)` = `sorted(<型のディレクトリ>/*.cue) + sorted(<repository_root>/spec-dock/cue/*.cue（通常のファイルだけ）) + Scope の3つ（あるものだけ）`、`tags = {"kind": kind}`、`cwd` は Scope の実のディレクトリ。パスは、すべて `resolve()` した実のパスで渡す（`cue` の出す相対パスを、確実に元のファイルに戻すため）。`k1_files` は公開の関数で、I-5 の描画が同じ並べ方を使う。
  6. 終了の状態が 0 以外：`parse_cue_errors` の結果を `CUE_INVALID` に変える。重複の扱い：道筋の最初の部分が `_` で始まるもの、文に `error in call to` を含むもの、文が `N errors in empty disjunction` のものは「派生」とし、派生でない誤りが1つでもあれば派生を捨てる。同じ（道筋、文）は1つにする。
  7. 終了の状態が 0：JSON を読み、全体を `evaluation` に持つ。`findings` の空でない規則の指摘を、規則の名前の順、指摘の並びのとおりに `SPEC_FINDINGS` に変える。JSON が読めない、オブジェクトでない、`findings` が辞書でない → `CanonicalCommandError(CUE_FAILED, exit_code=5)`。
  8. 保証レベル：手順2の `tool` を渡して `read_assurance` を呼ぶ。読み取りが道具の失敗（`CUE_NOT_FOUND`、`CUE_VERSION_UNSUPPORTED`、`CUE_TIMEOUT`、`CUE_FAILED`）なら、文書の誤りにせず、そのコードで止める（`CanonicalCommandError`。exit と次の手順は「止まる失敗」の表のとおり）。それ以外で`source` が `cue` でないとき、評価が通っていれば必ず、評価が失敗していれば `problem.code` が `ASSURANCE_UNREADABLE` で、かつ道筋が `assurance` で始まる `CUE_INVALID` がないときだけ、`ASSURANCE_UNREADABLE` の誤りを足す（同じ原因を2度示さない）。
  9. 説明資料：`explanation.html` を読み、`inspect_explanation` の結果を、`EXPLANATION_MISSING`、`EXPLANATION_SKELETON`（Epic は誤り、ほかは警告）、`EXPLANATION_INVALID`（誤り。問題ごとに1件）に変える。読めない（`OSError`、UTF-8 でない）は `EXPLANATION_INVALID`。
- 示すファイルの道筋（`details.file`）：Scope のファイルは `shown`（`spec-dock/initiatives/<区切り>/<ID>`）の下の名前、リポジトリの型は `spec-dock/cue/<名前>`、SpecDock の型は `<spec_dock package>/cue/v1/<名前>`。

### 4. 結果の形（契約 K3）

検査の誤りと警告は、`Diagnostic(code, message, details)` の一覧である。`details` の共通の鍵は `file`（上の道筋か `null`）と `hint`（直し方）。

| コード | 重さ | `details` | 意味 |
|---|---|---|---|
| `CUE_INVALID` | 誤り | `file`、`line`、`column`、`field`（道筋か `null`）、`cue_message`、`positions`（`[{file, line, column}]`）、`hint` | 型の形の誤り、文法の誤り、`schema` の誤り |
| `SPEC_FINDINGS` | 誤り | `rule`、`id`、`file`、`hint` | `findings` の指摘1件。`file` は `id` の頭で決める（`R-`・`F-` は `requirement.cue`、`D-` は `design.cue`、`S-`・`T-`・子の ID・`rollback`・`execution.` は `plan.cue`、ほかは `null`） |
| `ASSURANCE_UNREADABLE` | 誤り | `file`（`requirement.cue`）、`problem`、`hint` | 保証レベルを `requirement.cue` だけから読めない |
| `SCOPE_FORMAT_CONFLICT` | 誤り | `file`（Scope のディレクトリ）、`hint` | `requirement.md` と `requirement.cue` の両方 |
| `SCOPE_DOCUMENT_MISSING` | 誤り | `file`、`hint` | CUE の Scope の `design.cue`・`plan.cue` がない |
| `EXPLANATION_MISSING` | Epic は誤り、ほかは警告 | `file`、`hint` | 説明資料がない |
| `EXPLANATION_SKELETON` | Epic は誤り、ほかは警告 | `file`、`hint` | 雛形の印が残っている |
| `EXPLANATION_INVALID` | 誤り | `file`、`problem`、`hint` | 形を壊している |

止まる（結果を返さない）失敗：

| コード | exit | 次の手順 |
|---|---|---|
| `CUE_NOT_FOUND`、`CUE_VERSION_UNSUPPORTED` | 3 | `CUE_INSTALL_STEP` |
| `CUE_TIMEOUT` | 5 | `--timeout` を延ばすか、文書を小さくする |
| `CUE_FAILED` | 5 | `cue` を入れ直す |
| `CUE_SCHEMA_UNSUPPORTED` | 3 | SpecDock を上げる（持っている版を示す） |

### 5. `scope check` のコマンド（`runtime/application/canonical_scope_check.py`）

- `check_scope(namespace, context) -> OperationResult[object]`：`load_canonical_scopes(link=True, offline=namespace.offline)`、`resolve_canonical_scope`、`check_canonical_scope_expectations`、`scopes.require_directory`（ない → `LOCAL_TARGET_NOT_FOUND`、exit 4）。`check_scope_documents(<実のディレクトリ>, kind=view.kind, shown=<チェックアウトからの道筋>, repository_root=context.root, timeout=namespace.timeout)`。
- 成功（誤りなし）：`OperationResult("scope check", "succeeded", FamilyData("scope-check", result), 0, warnings=(*scopes.warnings(), *report.warnings))`。
- 誤りあり：`status="failed"`、exit 7、`error=Diagnostic("SCOPE_CHECK_FAILED", "<ID> has N spec check errors", {"scope_id", "count"})`、`recovery`：「示した誤りを直し、`spec-dock scope check <ID>` をもう一度実行する」。
- `result`：`scope_id`、`kind`、`path`、`format`、`checked`、`valid`、`schema`、`assurance`（`AssuranceReading.payload()`）、`errors`、`warnings`、`findings`、`cue`（`{"version": ...}` か `null`）、`cue_output`、`snapshot`。
- テキスト（`presentation/envelope.py` の `render_text` に `scope check` の枝を足す）：1行目 `scope_id=<ID> format=<形式> checked=<真偽> valid=<真偽> errors=<数> warnings=<数>`、続けて誤りと警告を1件ずつ `error [CODE] file="..." line=N field="..." <文>` と `  hint: <直し方>` で示す。
- CLI：`catalog.py` の `LEAF_PATHS` に `scope check` を `scope show` の次に足す。引数は `target`。`HELP_EFFECTS`、`HELP_PRECONDITIONS`、`_help_spec` の枝（読むだけ、JSON の形、確認は不要）。`MUTATING_LEAF_PATHS` には入れない。`canonical_dispatch.CANONICAL_HANDLERS` に足す。`runtime_dispatch` の schema 3 の枝で、`command.startswith("canonical ") or command == "scope move"` に `scope check` を足し、`canonical_not_migrated` を返す。

### 6. `work finish`（`canonical_work.finish_work`）

- `_finish_rules`（GitHub の読み直し）の直後、`_require_saveable` の前に `_check_before_finish(session, target, observed_state, timeout)` を呼ぶ。dry-run の枝より前なので、dry-run でも同じに働く。
- `_check_before_finish(...) -> (警告, 開いている Scope に当てる拒否 | None)`：
  - Scope のディレクトリがない、形式が `markdown` → 何もしない（空の警告）。
  - 検査の誤りがある、または道具の失敗（`CanonicalCommandError`）：
    - `observed_state != "completed"` → `CanonicalCommandError("SCOPE_CHECK_FAILED", exit_code=3, details={"scope_id", "errors": [{code, message, details}...]}, recovery=(<直して scope check、もう一度 work finish>,))` を投げる。道具の失敗はそのコードのまま投げる。この時点では何も書いていない（カタログの変更集も、GitHub も、選択も）。
    - `observed_state == "completed"` → 止めずに、同じ内容を警告（`SCOPE_CHECK_FAILED`、または道具の失敗のコード）にして返し、拒否（`CanonicalCommandError`）も返す。
  - 保存を待った後の2回目の `_finish_rules` で `observed_state` が完了でなくなっていたら（別の PC が開き直した）、返された拒否（検査の誤りなら `SCOPE_CHECK_FAILED`、道具の失敗ならそのコード）を投げる。今の `work finish` の扱いのとおり、変更集を書いた後なら `partial`（exit 6、`github.issue.close` は `not_attempted`）、書いていなければ `failed`（exit 3）になる。どちらでも Issue は閉じない。誤りの残る Scope を閉じない（R-B7）ため（仕様のレビューの P2。2026-10-31）。
  - 警告（説明資料）→ 結果の警告に足す。
- 「既に閉じた Scope では止めない」理由（2026-10-31 統括の決定）：GitHub で既に完了の Scope の `work finish` は、選択を外すだけである。閉じた後に型の版やリポジトリの型が変わって誤りになった Scope で、選択を外せなくなるのを避ける。R-B7 の目的は「誤りの残る Scope を閉じないこと」で、既に閉じた Scope には当たらない。
- 子孫は検査しない（今の `work finish` は、子孫が完了でなければ止まるので、子孫は既に閉じている）。

### 7. `scope show`（`canonical_scope_read.show_scope`）

- `result["assurance"] = read_assurance(<実のディレクトリか None>, timeout=namespace.timeout).payload()`。例外を出さないので、`scope show` の成否は変わらない。`scope list` と `scopes.payload` は変えない。

### 8. `workspace validate`・`doctor`（`canonical_workspace.inspect_canonical_structure`）

- Scope ごとに `scope_format(directory.path)` を見る。`conflict` → `SCOPE_FORMAT_CONFLICT`（`{scope_id, path}`）の誤り。`cue` → `CUE_DOCUMENTS`、`markdown` → `MARKDOWN_DOCUMENTS` の欠けを `SCOPE_DOCUMENT_MISSING` にする（今の形の `missing` のまま）。`REQUIRED_DOCUMENTS` の名前は、Markdown の組として残す。`cue` は呼ばない。

## data / failure

- **書くもの**：ない。`scope check`、`scope show` は読むだけ（GitHub の構造の写しの更新は、今の読むコマンドと同じ）。`work finish` は、検査で止まるときは何も書かない。
- **`cue` の子のプロセス**：引数の並びで呼び、シェルを通さない。環境は親のものを引き継ぐ。時間の上限は `--timeout`（既定30秒）を1回の呼び出しごとに使う（`version`、`schema`、評価、`assurance` の最大4回。`scope show` は `version` と `assurance` の2回）。
- **誤りの文の解析に失敗**：位置が読めない行は文に足す。1件も読めなければ、全体を1件の `CUE_INVALID`（道筋 `null`）にする。
- **リポジトリの型のディレクトリが読めない**：`OSError` は `LOCAL_IO_FAILED`（今の dispatch の扱い）。
- **カタログのファイルの経路**：`spec-dock/initiatives` はカタログへのリンクなので、`cue` には実のパスを渡し、示す道筋はチェックアウトからの道筋にする。
- **インターネット**：構造は表示の鮮度で読み、GitHub に届かなければ保存した写しを警告付きで使う（今の `scope show` と同じ）。`--offline` も使える。`cue` は外部のモジュールを読まない（型は標準の `list` だけを使う）。

## 変更対象

- 足すもの：
  - `src/spec_dock/runtime/infra/cue_tool.py`
  - `src/spec_dock/runtime/domain/explanation_shape.py`
  - `src/spec_dock/runtime/application/scope_check.py`、`canonical_scope_check.py`
  - テスト：`tests/unit/infra/test_cue_tool.py`、`tests/unit/domain/test_explanation_shape.py`、`tests/unit/application/test_scope_check.py`、`tests/cli_runtime/test_issue473_scope_check.py`、`tests/cli_runtime/test_issue473_work_finish.py`、`tests/cli_runtime/test_issue473_scope_show.py`、`tests/cli_runtime/test_issue473_workspace.py`、`tests/support/cue_scopes.py`（CUE の Scope を置く補助と、偽の `cue`）
- 変えるもの：
  - `runtime/application/canonical_work.py`（`_check_before_finish`）、`canonical_scope_read.py`（`assurance`）、`canonical_workspace.py`（形式ごとの文書）
  - `runtime/cli/catalog.py`、`runtime/commands/canonical_dispatch.py`、`runtime/commands/runtime_dispatch.py`、`runtime/presentation/envelope.py`
  - 配布資産と dogfood の写し（同じバイト）：`docs/reference_cli.md`（C54 の行と「公開54 leaf」）、`docs/README.md`（「全54 leaf」）、`docs/cli-redesign-guide.html`（「54 leaf」「全54コマンド」と、表の C54 の行）、`docs/canonical.md`（「エラーと次の1手」の表に `SCOPE_CHECK_FAILED`、`SCOPE_FORMAT_CONFLICT`、`CUE_*` の行を足し、`SCOPE_DOCUMENT_MISSING` の次の1手に CUE の Scope の文書の組を足す。既存のテストが、`application/canonical_*.py` の `SCOPE_` の定数を、この表に求めるため）。`static-inventory.json` の4つの `sha256` を新しい値にし、古い値を `known_old_sha256` に足す。
  - 葉の数（53）を固定した既存のテスト：`tests/integration/test_cli_docs_vnext.py`、`tests/cli_runtime/test_help_completion_vnext.py`、`test_cli_vnext_contract.py`、`test_issue413_contract.py`、`test_issue436_every_command.py`（数と、全部の葉を1回ずつ流す一覧への `scope check` の追加）、`tests/unit/infra/test_issue436_docs.py`（数と、読むだけの葉の一覧）
- 変えないもの：`src/spec_dock/cue/`、`runtime/infra/cue_schemas.py`、`tests/support/cue.py`、`spec-dock/templates/<種類>/`、`src/spec_dock/assets/spec_dock/templates/`、`design-system/`、スキル、schema 3 の処理、`.github/workflows/`。

## 移行・互換性・rollback

- 移行：N/A（データを持たない。CUE の Scope は I-3 まで作られない）。
- 互換：Markdown の Scope の `work finish`、`scope show`（`assurance` の鍵が増えるだけ）、`workspace validate`・`doctor` の結果は変わらない。新しい葉は、既存の葉の文法を変えない。
- `cue` のない環境：Markdown の Scope の操作は今までどおり。`scope check` は Markdown の Scope では `cue` を求めない。
- 配布資産：`reference_cli.md`、`README.md`、`cli-redesign-guide.html`、`canonical.md` の4つのファイルが変わる。利用者のリポジトリは `installation update` で受け取る（`known_old_sha256` で、手を加えていない古い写しを置き換えられる）。
- rollback：この PR を戻す。戻した後も、データの戻しは要らない。

## testability

| AC | 観測点と方法 |
|---|---|
| AC-01 | `CanonicalWorld` に CUE の Scope と Markdown の Scope を置き、`scope show --json` の `assurance`。読めない場合ごとの `problem.code`。`--offline` と、偽の `gh` を失敗させた場合 |
| AC-02 | 誤りのない Scope、形の誤りの Scope、指摘の Scope で `scope check --json` とテキスト。実行の前後で、カタログとチェックアウトのファイルの一覧と中身が同じ |
| AC-03 | I-1 の見本を Scope として写し、`scope check` の `CUE_INVALID` の道筋と、`findings` を `expected.json` と比べる |
| AC-04 | チェックアウトに `spec-dock/cue/repo.cue` を置く。制約と規則が加わる。誤りの型のファイルの道筋 |
| AC-05 | standard で通る Scope を strict に書き換えて誤り、項目を足して通る |
| AC-06 | `design.cue` に `assurance` を書いた Scope、`schema` がない Scope、`specdock/v9` の Scope |
| AC-07 | 偽の `cue`（PATH の前に置くスクリプト）で、ない・古い・読めない版・時間切れ（`--timeout` を短く）・読めない出力。呼ばれた引数の記録（K1 の順番）。`cue_tool` の単体のテスト（解析） |
| AC-08 | PATH から `cue` を外して、Markdown の Scope の `scope check`。両方の `requirement` の Scope |
| AC-09 | `WriteWorld` で、誤りの CUE の Scope の `work finish`（`--dry-run` も）。変更集・書き込み・選択が変わらない。直して閉じる。Issue の雛形のままの説明資料で、警告付きで閉じる |
| AC-10 | `cue` を PATH から外して、Markdown の Scope の `work finish`。既存の回帰のテストを変えずに流す |
| AC-11 | GitHub で完了にした CUE の Scope（誤りあり、`cue` なし）の `work finish` |
| AC-12 | Markdown と CUE の Scope が並ぶカタログの `workspace validate`・`doctor`。`plan.cue` の欠け、両方の `requirement` |
| AC-13 | `explanation_shape` の単体のテスト（壊し方ごと）と、種類ごとの重さを `scope check` で。I-4 の雛形のバイトをそのまま使う |
| AC-14 | schema 3 のリポジトリ（既存の補助）で `scope check` |
| AC-15 | `help scope check`、`scope check --help`、completion の出力 |
| AC-16 | `make lint`、全テスト（clean な clone で）。`git diff --stat origin/main -- tests/` の既存ファイルの変更が、葉の数の更新だけ |

## risk

- **`cue` の誤りの文の形が版で変わる**：解析は、行頭と字下げの2つの形だけに依る。読めない形でも、文の全体を1件の誤りとして示す（情報を落とさない）。最低の版を v0.17.1 に固定し、それより新しい版の文の形の変化は、解析のテストを足して扱う。
- **重複の誤りを捨てすぎる**：派生の判定は、派生でない誤りが1つでもあるときだけ働く。誤りの文の全体（`cue_output`）も返す。
- **`work finish` を誤って止める**：Markdown の Scope、ディレクトリがない Scope、既に閉じた Scope では止めない。止めるときは、誤りの一覧と次の手順を示す。
- **`cue` の起動の回数と時間**：1回の検査で最大4回（`cue version` は1回だけ）。大きな Scope で遅ければ、I-7 で `schema` と `assurance` の読み取りをまとめる。
- **祖先のディレクトリの `cue.mod`**：`cue` は、作業のディレクトリの祖先の `cue.mod` を見ることがある。型は外部のモジュールを使わないので、評価の結果は変わらない見込み（未確認として報告に書く）。
- **葉の数の文書の更新**：配布資産の4つのファイルを変えるので、dogfood の写しと inventory の `sha256` を同じコミットでそろえる。

## 決めたこと

2026-10-31 に統括が確かめた（Q7 は統括が一部を変えた）。

- **Q1**：`cue` の最低の版は v0.17.1（確かめた唯一の版）。版が読めないときも止める。
- **Q2**：誤りのコードと終了の状態は、上の「結果の形」のとおり。`scope check` は誤りがあれば exit 7、`work finish` は `SCOPE_CHECK_FAILED`（exit 3）。
- **Q3**：`scope show` は `data.result.assurance = {level, reason, source, problem}`。`scope list` には足さない（Scope ごとに `cue` を呼ぶと遅いため）。
- **Q4**：`schema` と `assurance` は `requirement.cue` だけから読み、読めなければ誤り（R-C2 の正本を1か所に保ち、`scope show` との食い違いを防ぐ）。
- **Q5**：slices のキーが GitHub の本当の子かは調べない（計画を先に書き、子の Issue を後で作る順番があるため。I-7 で要れば足す）。
- **Q6**：schema 3 の `scope check` は `CANONICAL_NOT_MIGRATED`。CUE の Scope は canonical の `scope create`（I-3）だけが作るので、schema 3 の `work finish`・`validate` は変えない。
- **Q7**：`work finish` は、ディレクトリがない、または Markdown の Scope では検査しない。`--dry-run` でも同じに止まる。GitHub で既に完了の Scope では、誤りで止めず、同じ一覧を警告にして選択を外す（理由は「責務・Interface 6」）。
- **Q8**：リポジトリの型は、チェックアウトの作業ツリーの `spec-dock/cue/*.cue` を読む。
