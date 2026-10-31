---
種別: 設計書（Issue）
ID: "iss-00474"
関連GitHub: ["#474"]
状態: "approved"
最終更新: "2026-10-31"
依存: ["requirement.md"]
---

# iss-00474 Scaffold CUE Scopes With Assurance — 設計

詳細: [Design Guide](../../../docs/authoring/design.md)

## 設計目標

- 保証レベルの引数の確かめを、canonical の作成と取り込みの最初の1か所にまとめ、GitHub にもカタログにも触れる前に止める（R-01、F-01）。
- 理由の文を CUE の文字列に変える処理を、domain の純粋な関数にし、本物の `cue` で正しさを縛る（R-03）。
- 雛形の場所を `templates/cue/<種類>/` に変え、その確かめを、今の「雛形の確かめ」の位置（GitHub に書く前）で行う（R-05）。
- Markdown の Scope と schema 3 の動きを変えない（R-07、AC-07、AC-09）。

## Current / Target

| | 今 | この Issue の後 |
|---|---|---|
| schema 4 の `scope create`・`import` の引数 | `--title`、`--parent`、`--backend` | 加えて `--assurance LEVEL`、`--assurance-reason TEXT`（canonical の処理で必須） |
| 写す雛形 | `spec-dock/templates/<種類>/`（`.md` の4つ） | `spec-dock/templates/cue/<種類>/`（5つ） |
| 作られる文書 | `requirement.md`、`design.md`、`plan.md`、`report.md` | `requirement.cue`、`design.cue`、`plan.cue`、`explanation.html`、`report.md` |
| 雛形がないとき | `RuntimeError` → `LOCAL_IO_FAILED`（exit 5） | `SCOPE_TEMPLATES_OUTDATED`（exit 3、`installation update`） |
| 雛形の CUE の見本 | `tests/fixtures/cue/v1/templates/`（テストだけ） | 配布資産 `templates/cue/`（見本は消す） |
| schema 3 | `.md` を作る | 同じ。2つの引数を付けたら `CANONICAL_NOT_MIGRATED` |

## 責務・Interface

### 1. 保証レベルの値（`runtime/domain/assurance.py`、新しい）

```python
ASSURANCE_LEVELS: Final = ("light", "standard", "strict", "critical")
LEVEL_MARKER: Final = "{{ASSURANCE_LEVEL}}"
REASON_MARKER: Final = "{{ASSURANCE_REASON}}"

@dataclass(frozen=True)
class Assurance:
    level: str
    reason: str          # 前後の空白を除いた文

def parse_assurance(level: str | None, reason: str | None) -> Assurance: ...   # ValueError（理由の文は英語）
def cue_string_body(text: str) -> str: ...
def assurance_replacements(assurance: Assurance) -> dict[str, str]: ...      # {LEVEL_MARKER: level, REASON_MARKER: cue_string_body(reason)}
```

- `parse_assurance`：`level` が `None` → 誤り（`--assurance is required`）。`ASSURANCE_LEVELS` にない → 誤り（引数の解析が先に止めるので、直接の呼び出しの守り）。`reason` が `None`、または `reason.strip()` が空 → 誤り（`--assurance-reason must not be blank`）。`reason.strip()` を UTF-8 にできない（サロゲート）→ 誤り。返す `reason` は `strip()` したもの。空白の判定は Python の `str.strip()` で、I-1 の `#Text` と I-2 の `read_assurance` と同じ範囲（全角の空白も空白）。
- `cue_string_body`：`json.dumps(text, ensure_ascii=False)` の両端の引用符を除いたもの。JSON の文字列の書き方（`\"`、`\\`、`\n`、`\t`、`\uXXXX` など）は、CUE の二重引用符の文字列でも同じ意味になる。`\` を `\\` にするので、`\(`（CUE の文字列の埋め込み）は文字のまま残る（`cue` v0.17.1 で、引用符、改行、タブ、バックスラッシュ、`\(`、NUL、BEL、DEL、ESC、U+2028、絵文字を確かめた。2026-10-31）。
- `scope_check.LEVELS` は、この定数を使う（同じ値を2か所に持たない）。

### 2. 引数（`runtime/cli/catalog.py`）

- `scope create {initiative,epic,issue}` と `scope import github {initiative,epic,issue}` の `LEAF_ARGUMENTS` に、`_arg("--assurance", choices=ASSURANCE_LEVELS)` と `_arg("--assurance-reason")` を足す。argparse では任意にする（schema 3 の回帰のテストが引数なしで呼ぶため。Q1）。
- `HELP_PRECONDITIONS` の6つの葉に、「Schema 4: `--assurance LEVEL`（light|standard|strict|critical）と `--assurance-reason TEXT` が必須（なければ `ASSURANCE_REQUIRED`、GitHub に何も書かない）。雛形は `spec-dock/templates/cue/<kind>/`（なければ `SCOPE_TEMPLATES_OUTDATED`、`spec-dock installation update`）」を足す。import には「既にディレクトリがあれば書かず `ASSURANCE_NOT_WRITTEN`」を足す。
- 例（`_example`）：6つの葉の例に `--assurance standard --assurance-reason '<reason>'` を足す。
- completion は `LEAF_ARGUMENTS` から作られるので、自動で2つの引数を含む。

### 3. canonical の作成と取り込み（`runtime/application/canonical_scope_create.py`）

```python
ASSURANCE_REQUIRED: Final = "ASSURANCE_REQUIRED"            # exit 2
ASSURANCE_NOT_WRITTEN: Final = "ASSURANCE_NOT_WRITTEN"      # 警告
SCOPE_TEMPLATES_OUTDATED: Final = "SCOPE_TEMPLATES_OUTDATED"  # exit 3
CUE_TEMPLATE_FILES: Final = ("requirement.cue", "design.cue", "plan.cue", "explanation.html", "report.md")

def _require_assurance(namespace) -> Assurance: ...          # CanonicalCommandError(ASSURANCE_REQUIRED, exit_code=2)
def cue_template_directory(root: Path, kind: ScopeKind) -> Path: ...   # root / "spec-dock/templates/cue" / kind
```

- `create_scope`：`refuse_slug` の直後、確認・`open_write_session`（GitHub とカタログを読む前）の前に `_require_assurance`。`import_scope` も `refuse_slug` の直後（`parse_github_ref` より前）。どちらも `--dry-run` の前なので、予行でも止まる。`recovery`：「`--assurance <light|standard|strict|critical> --assurance-reason <text>` を付けて同じコマンドを実行する」。`details`：`{"argument": "--assurance" | "--assurance-reason"}`。
- `_check_scaffold_sources(session, kind)`：今の規則のソースの確かめに加えて、`cue_template_directory` が実のディレクトリで、`CUE_TEMPLATE_FILES` がすべて通常のファイルで、`requirement.cue` が `LEVEL_MARKER` と `REASON_MARKER` を含むことを確かめる。欠けていれば `CanonicalCommandError(SCOPE_TEMPLATES_OUTDATED, exit_code=3, recovery=("Run spec-dock installation update to install the CUE Scope templates, then run the same command again.",), details={"path": <チェックアウトからの道筋>, "missing": [...]})`。呼ぶ位置は今のまま（create はラベルと Issue の作成より前、import は既存のディレクトリがないときだけ、ラベルより前）。
- `_publish(..., assurance)`：`templates = cue_template_directory(...)`。`copy_scope_template_at(templates, destination, descriptor, replacements, final_replacements=assurance_replacements(assurance))`。
- `import_scope`：`existing is not None` のとき、`ASSURANCE_NOT_WRITTEN` の警告（`details`：`{scope_id, next_step: "Edit assurance in requirement.cue of the existing Scope if it should change."}`）を `session.warnings` に足す。Markdown の Scope でも CUE の Scope でも同じ（どちらも書き換えない）。
- `_import_command(kind, number, parent, title, assurance)`：`--assurance <level> --assurance-reason <shlex.quote(reason)>` を足す。

### 4. 雛形の写し（`runtime/infra/canonical_scaffold.copy_scope_template_at`）

- 引数に `final_replacements: Mapping[str, str] = {}`（キーワードだけ）を足す。UTF-8 の文書は、今の `render_text` → `strip_structure_front_matter` → `rebase_spec_dock_links` の後に、`final_replacements` を置き換える。理由の文が、ほかの置き換え（`YYYY-MM-DD` など）やリンクの付け替えを受けないため（F-08）。`render_text` の置き換えは順に行うので、`final_replacements` も、値に別の印を含んでも二度は置き換えない形（`re.sub` の1回の走査）にする。
- 置き換えた結果がもとのバイトと同じファイルは、もとの権限を保つ（今の動き）。`explanation.html` は印を持たないので、バイトが変わらない（AC-10）。

### 5. schema 3（`runtime/application/direct_scope_publish._publish_scope`）

- 最初に、`namespace.assurance` か `namespace.assurance_reason` が `None` でなければ、`CanonicalCommandError(CANONICAL_NOT_MIGRATED, "--assurance and --assurance-reason apply only in canonical mode (schema 4)", recovery=("Run the same command without --assurance and --assurance-reason, or migrate the repository to canonical mode.",), details={"argument": ...})`。何も読まない・書かない。

### 6. 配布資産

- `src/spec_dock/assets/spec_dock/templates/cue/{initiative,epic,issue}/`：
  - `requirement.cue`、`design.cue`、`plan.cue`：`tests/fixtures/cue/v1/templates/<種類>/` のバイトのまま移す（`git mv`）。
  - `explanation.html`：`src/spec_dock/assets/spec_dock/design-system/explanation-skeleton.html` のバイト一致の写し。
  - `report.md`：今の `templates/<種類>/report.md` を元に、`依存` を `["requirement.cue", "design.cue", "plan.cue"]` にし、ガイドへのリンクを `templates/cue/<種類>/` からの相対（`../../../docs/authoring/report.md`）にしたもの。front matter の `タイトル`・`親` の行は、作るときに今の規則で消える。
- `static-inventory.json`：15のファイルを、`mode: 420`、`init_only: false`、`known_old_sha256: []` で足す。変えた文書（`docs/canonical.md`、`docs/reference_cli.md`、`docs/cli-redesign-guide.html`）は、新しい `sha256` にし、古い値を `known_old_sha256` に足す。
- dogfood の写し：`spec-dock/templates/cue/` と、変えた3つの文書を、提供側とバイト一致にする。
- `tests/unit/cue/test_schema_v1_templates.py` は、移した先を読む。ファイルの一覧の確かめは、3つの CUE の文書が含まれることに変える。`_fill` は runtime の `assurance_replacements` を使い、テストの補助 `cue_string_body` と同じ結果になることも確かめる。

### 7. 文書（配布資産）

- `docs/canonical.md` の「エラーと次の1手」に3行：`ASSURANCE_REQUIRED`（2、`scope create`・`scope import github`、GitHub に何も書かない）→「`--assurance` と `--assurance-reason` を付けて同じコマンドを実行する」。`SCOPE_TEMPLATES_OUTDATED`（3、同上）→「`spec-dock installation update` で配布資産を上げてから同じコマンドを実行する」。`ASSURANCE_NOT_WRITTEN`（警告、`scope import github`）→「既にある Scope は書き換えない。変えるなら `requirement.cue` の `assurance` を直す」。冒頭の slug の行の近くに、保証レベルの必須の1文を足す。
- `docs/reference_cli.md` と `docs/cli-redesign-guide.html` の C01〜C06 の引数の欄に `--assurance LEVEL --assurance-reason TEXT`（schema4 で必須）を足す。

## data / failure

- **書くもの**：今と同じ（GitHub の Issue、ラベル、親、カタログの1つの変更集）。中身が CUE の一式になるだけ。
- **止まる順番**（create）：`require_writer` → `refuse_slug` → **`_require_assurance`** → 確認 → カタログ・GitHub の読み取り → 親の確かめ → **雛形の確かめ（`SCOPE_TEMPLATES_OUTDATED`）** → ラベル → Issue の作成 → 親 → カタログ。太字が新しい。どちらも GitHub に書く前である。
- **止まる順番**（import）：`require_writer` → `refuse_slug` → **`_require_assurance`** → 参照の形 → GitHub の読み取り → … → 既存のディレクトリがなければ**雛形の確かめ** → ラベル → 親 → カタログ。
- **partial**：Issue を作った後の失敗は、今の `SCOPE_PUBLICATION_INCOMPLETE`。復旧のコマンドが2つの引数を含む（R-06）。
- **cue**：作成と取り込みは `cue` を呼ばない（Q5）。

## 変更対象

- 足すもの：`runtime/domain/assurance.py`、`assets/spec_dock/templates/cue/**`（15）と dogfood の写し、テスト（`tests/unit/domain/test_assurance.py`、`tests/cli_runtime/test_issue474_scope_create.py`、`tests/cli_runtime/test_issue474_schema3.py`、`tests/unit/infra/test_issue474_cue_templates.py`）。
- 変えるもの：`canonical_scope_create.py`、`canonical_scaffold.py`（infra）、`direct_scope_publish.py`、`cli/catalog.py`、`scope_check.py`（定数を使うだけ）、`static-inventory.json`、配布資産の3つの文書と dogfood の写し、既存のテスト（`requirement.md` の「制約・前提」の範囲）。
- 移すもの：`tests/fixtures/cue/v1/templates/**` → `assets/spec_dock/templates/cue/**`。
- 変えないもの：`templates/<種類>/`、`design-system/`、`src/spec_dock/cue/`、`scope_check` の検査の中身、`work finish`、`scope show`、スキル、ガイド、`templates/README.md`、`.github/workflows/`。

## 移行・互換性・rollback

- 移行：N/A（既存の Scope のデータを変えない）。
- CLI の契約の変更：schema 4 の `scope create`・`import` に2つの引数が要る。呼んでいるスキルや手順は、I-6 で直す（`spec-dock` スキル、利用者の手順）。それまで、引数のない呼び出しは `ASSURANCE_REQUIRED` で止まり、直し方を示す（何も書かない、安全な側）。
- 配布資産の版の食い違い：新しい CLI と古い配布資産は `SCOPE_TEMPLATES_OUTDATED`。前の版の CLI と新しい配布資産は、`templates/<種類>/` を写すので、今までどおり `.md` の Scope を作る（AC-07）。
- rollback：この PR を戻す。作られた CUE の Scope は、カタログに残る（Epic の rollback）。

## testability

| AC | 観測点と方法 |
|---|---|
| AC-01 | `WriteWorld`（偽の `gh`、提供側の配布資産を種にしたチェックアウト）で、3つの種類の `scope create`。ディレクトリの一覧、`requirement.cue` を本物の `cue` で読んだ `assurance` |
| AC-02 | 引数の組（片方、空白、全角の空白、両方なし）× `create`・`import`、`--dry-run`。`fake.requests` が空、`changesets()` が空。不正な値の `USAGE_ERROR` |
| AC-03 | 単体：`cue_string_body` を本物の `cue` で往復。結合：特殊な理由で作った `requirement.cue` を `cue export -e assurance.reason`。サロゲートを含む理由 |
| AC-04 | 作った直後に `scope check --json`、`scope show --json --offline`（`cue` を PATH に置く） |
| AC-05 | 偽の GitHub に Issue を置き `scope import github`。既存のディレクトリ（`world.scope(...)`）で import、警告とファイルの不変 |
| AC-06 | 種のファイルから `templates/cue/` を外す・1つ欠く・印を欠く。`fake.writes()` が空 |
| AC-07 | 提供側の `templates/<種類>/` のファイルの一覧。schema 3 の既存の作成のテスト |
| AC-08 | 親への `sub_issues` を失敗させた `scope create` の `recovery` を `shlex.split` して、そのまま実行 |
| AC-09 | schema 3 の世界（`tests/cli_runtime/test_issue413_scope_publish.py` の補助）で2つの引数を付ける |
| AC-10 | 目録・写し・スケルトンのバイトの比較、`installation init` の `created_paths` |
| AC-11 | `help` の出力、`test_issue436_docs.py` の表の検査 |
| AC-12 | `make lint`、`PATH=.workbench/bin:$PATH uv run pytest`、`git diff --stat origin/main -- tests/` |

## risk

- **既存のテストの書き換えで確かめを弱める**：変えるのは引数の追加と、作られるファイルの期待だけに限り、差分を `report.md` に列挙する。
- **理由の文の書き方の誤り**：JSON の書き方に頼る。本物の `cue` での往復のテストで縛る。
- **雛形の確かめと写しの食い違い**：確かめと写しが同じ `cue_template_directory` を使う。
- **スキルや手順が古い引数で呼ぶ**：I-6 まで、`ASSURANCE_REQUIRED` で止まって直し方を示す。報告に残す。

## 決めたこと

2026-10-31 に統括が、推奨どおりに決めた（Orca の ask）。

- **Q1 schema 3**：引数は argparse では任意にし、canonical の処理で必須にする。schema 3 で指定されたら、何も書かずに `CANONICAL_NOT_MIGRATED` で止める。理由：schema 3 の回帰のテストが引数なしで呼び、ほかのリポジトリは epic-00424 の I-12 まで schema 3 のまま動く。黙って捨てて `.md` を作ると、利用者は保証レベルが書かれたと誤解する。
- **Q2 既にディレクトリがある import**：引数は常に必須（引数の段階で止める、K4）。既にディレクトリがあれば書かず、警告 `ASSURANCE_NOT_WRITTEN`。理由：「足りないものだけを足す」動きを守り、既存の `requirement` を書き換えない。
- **Q3 復旧のコマンド**：Issue を作った後の失敗で示す `scope import github` に、2つの引数を引用付きで含める。理由：示したコマンドが、そのまま実行できるようにする。
- **Q4 エラーのコード**：`ASSURANCE_REQUIRED`（exit 2、引数の誤り）、`SCOPE_TEMPLATES_OUTDATED`（exit 3、`installation update`）。`canonical.md` の表に足す（この PR）。理由：引数の誤りは exit 2 の慣例、配布資産の古さは前提の誤り（exit 3）。
- **Q5 `cue` を呼ばない**：作成と取り込みは `cue` を呼ばない。理由：書き換えの関数は純粋で、テストで本物の `cue` に縛れる。作った後の確かめは `scope check` と `work finish` が受け持つ（判定を1か所に保つ）。
- **Q6 `report.md`**：今の `.md` の report を元に、依存を CUE の3つにした新しいファイルにする。`templates/README.md` とガイドは I-6。
- **AC-12 の読み方**：`requirement.md` の「制約・前提」のとおり（統括の決定）。
- **理由の前後の空白**（この Issue で決めた）：題名と同じく、前後の空白を除いて書く。
