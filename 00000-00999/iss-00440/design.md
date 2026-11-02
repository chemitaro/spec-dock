---
種別: 設計書（Issue）
ID: "iss-00440"
タイトル: "Remove Legacy Mode"
関連GitHub: ["#440"]
状態: "draft"
最終更新: "2026-11-02"
依存: ["requirement.md"]
親: ["epic-00424", "init-00423"]
---

# iss-00440 Remove Legacy Mode — 設計

詳細: [Design Guide](../../../docs/authoring/design.md)

## 設計目標

- **D1 宣言の受け付けは1か所で版4だけ**：宣言を読むのは `application/project_context.py` の `read_workspace_declaration` だけにし、版3を読んだら専用の例外を投げる。`dispatch()` はそれを `CANONICAL_NOT_MIGRATED` に変える。コマンドごとに版を調べない。
- **D2 振り分けは表だけ**：`dispatch()` は、宣言を受け付けた後、`CANONICAL_HANDLERS` の表を引くだけにする。モードの分岐と、従来の処理の import をなくす。
- **D3 消すものは到達で決める**：0.5.0 の入口から到達できないモジュール、関数、クラス、メソッドを消す（14章）。ファイルの一覧を正本にしない。canonical の処理が使う部品は、従来のモジュールにあっても残す。
- **D4 作られるものを変えない**：canonical モードのコマンドの出力、作るファイル、GitHub への要求は、消すコマンドと引数のほかは 0.4.2 と同じにする。雛形から前付けの2行を外し、写すときの除去をやめても、作るファイルのバイトは同じ。
- **D5 共通の契約はテストで残す**：(b) のテストは、同じ主張を canonical の作り物で確かめる形に移す（R-J7）。

## Current / Target

| 部分 | Current（`caaeebe45`、0.4.2 の後） | Target（0.5.0） |
|---|---|---|
| 宣言の受け付け | `read_workspace_declaration` が版3と4を受け付け、`workspace_mode` と `ProjectContext.mode` で `legacy` か `canonical` を返す。`probe_workspace_mode` が `dispatch()`（`installation`、`workspace validate --ci`、`workspace doctor --raw`）、`canonical_status.py:130`、`canonical_link.py:165,837`、`canonical_dashboard.py:85` で、`workspace_mode` と `LEGACY_WORKSPACE_SCHEMA` が `canonical_check.py` で使われる | 版4だけを受け付ける。版3は `WorkspaceNotMigrated`（`ValueError` の子）。モードの型と関数はない。「その checkout の宣言は受け付けられる版4か」は `declares_schema_4(root)` の1つで判定する（`canonical_status`、`canonical_link`、`canonical_dashboard` の4か所。どれも今の `probe_workspace_mode(...) == "canonical"` と同じ真偽になる）。`canonical check` は宣言の版の整数を直接比べる |
| `dispatch()` | プラットフォーム → リポジトリによらない表 → `installation` → `workspace validate --ci` → `workspace doctor --raw` → `resolve_context` → `mode` で canonical の表か、30余りの `elif` の従来の処理 | プラットフォーム → リポジトリによらない表 → `installation`（版3なら止める）→ `workspace doctor --raw`（宣言が読めないときだけ生の観測）→ `resolve_context`（版3なら止める）→ `CANONICAL_HANDLERS` |
| コマンド | 55（`help` と `completion` を含む。`workspace migrate`、`workbench copy` は canonical では拒否するだけ） | 53 |
| 引数 | `--slug`（scope の作成と取り込み）、`workspace validate --ci`、`--source local`（`workspace sync`、`dependency check`）は canonical では `CANONICAL_NOT_APPLICABLE` | ない（引数の誤り） |
| Scope の雛形 | `templates/{initiative,epic,issue}/*.md`（従来の作成用）と `templates/cue/`。CUE の `report.md` に `タイトル:`・`親:`。写すときに除き、「詳細:」の深さを書き換える | `templates/cue/` だけ。前付けの2行がなく、写すときに書き換えない |
| 規則の資産 | `docs/rules/initiative/epics.md`、`docs/rules/epic/issues.md`（従来の `epics/rules.md`、`issues/rules.md` の先）を canonical の作成も確かめる | ない。canonical の作成は `artifacts.md` と `discussions.md` だけを確かめる |
| 名前の規則 | `domain/ids.py` に slug と英数字の題名の規則 | ない。題名は `validate_canonical_title` だけ |
| 移行のスクリプト | `scripts/migrate-to-canonical/`、`run.sh` の `TARGETS`、`.github/scripts/specdock-ci-validate.sh` | ない（タグ `v0.4.2` に残る） |
| 版 | 0.4.2 | 0.5.0 |

## 責務・Interface

パスは `src/spec_dock/runtime/` から。

### `application/project_context.py`（C2）

```python
CANONICAL_WORKSPACE_SCHEMA: Final = 4      # 今の名前のまま
NOT_MIGRATED_WORKSPACE_SCHEMA: Final = 3   # 版3を見分けて止めるためだけの名前（受け付けない）

class WorkspaceNotMigrated(ValueError):
    """The declaration is schema 3: this SpecDock no longer reads unmigrated repositories."""

def read_workspace_declaration(path: Path) -> dict[str, object]: ...
    # 版4と既知の writer_protocol だけを返す。版3は WorkspaceNotMigrated、ほかは ValueError（今の文のまま）

def declares_schema_4(root: Path) -> bool: ...
    # 例外を投げずに、root の宣言が受け付けられる版4かを返す（canonical_status、canonical_link の2か所、canonical_dashboard の判定用）

def require_migrated(root: Path) -> None: ...
    # root の宣言が版3なら WorkspaceNotMigrated。宣言がない、壊れているなら何もしない（installation と doctor --raw 用）
```

- `CANONICAL_WORKSPACE_SCHEMA` は今の名前のまま残す（`canonical_check.py` が使う）。`LEGACY_WORKSPACE_SCHEMA`、`WorkspaceMode`、`_MODES`、`workspace_mode`、`probe_workspace_mode`、`ProjectContext.mode` は消す。版3を表す名前は、止めるための `NOT_MIGRATED_WORKSPACE_SCHEMA` だけにする（R-440-03 の「版3を受け付けるコードがない」は、版3を受け付ける定数と分岐がないことを指す）。
- `canonical_check.py`：`workspace_mode` の代わりに、版が整数の3なら今の `WORKSPACE_NOT_MIGRATED` の失敗（次の1手は `NOT_MIGRATED_RECOVERY`）、整数の4なら次の確かめ、そのほかは今の `unknown-schema` の失敗にする。新しい版の次の1手の文は「this SpecDock knows workspace schema 4 only.」にする（「schema 3 and 4」を残さない）。
- `canonical_dashboard.py:85` の、main の宣言が版4でないときにダッシュボードを書かない判定は残す（`declares_schema_4` に置き換える。`canonical sync --registered` は、登録簿の checkout の宣言をこの判定でだけ読み、版3で止まらない）。
- `OLD_WRITER_PROTOCOL`（`specdock.writer/v1`）は、版4の読み取りで今と同じく受け付け、書くコマンドの `require_writer` が今と同じく止める（I-8 の引き継ぎで、`canonical check` は失敗の1件にする。変えない）。

### `commands/runtime_dispatch.py`（C2）

```text
dispatch(namespace, cwd):
  UNSUPPORTED_PLATFORM の確かめ（今のまま）
  try:
    independent = dispatch_repository_independent(...)      # canonical check、canonical sync --registered（今のまま）
    installation のコマンド:
      target = installation_context(...)
      require_migrated(target.root)                          # 版3 → WorkspaceNotMigrated
      expect_current があれば canonical の install_with_expectation、なければ install_static_assets
    workspace doctor --raw:
      git = resolve_git_context(...)
      require_migrated(git.root)
      宣言が版4として読めるなら canonical の diagnose_workspace、読めないなら diagnose_raw_workspace
    context = resolve_context(...)                           # 版3 → WorkspaceNotMigrated。カタログの中の案内は今のまま
    result = dispatch_canonical(namespace, context)
  except WorkspaceNotMigrated: result = canonical_not_migrated(command)   # ValueError より前に捕まえる
  except ...（今のまま）
```

- `canonical_not_migrated` の `recovery` は `NOT_MIGRATED_RECOVERY` の1つの文で、0.5.0 の文にする：「SpecDock 0.4.2 を入れ直し、版のタグ v0.4.2 の scripts/migrate-to-canonical/README.md に従って移す（英語の文。今の文の形に合わせる）」。`canonical link`（既定のブランチに仕様があるとき）と `canonical check`（版3の宣言）も同じ定数を使う（今のまま）。メッセージは「`<command>` needs a migrated repository; this workspace declares schema 3」のまま。
- `scope_payload` と、`active show`、`scope show`、`scope list` の従来の処理、`BUSINESS_NOT_CONNECTED` の分岐は消す（表にないコマンドは解析で止まるので、表の引き当ては `KeyError` にならない。G7 のテストで表と `LEAF_PATHS` の一致を確かめる）。
- `diagnose_raw_workspace`（`application/direct_diagnostics.py`）は、宣言が読めないときだけ呼ばれるので、`known` は常に偽になる。版3を前提にした `--expect-current` の分岐（`load_scope_views` を使う）を消し、`--expect-current` と `--expect-backend` は今と同じ `ValueError` の文で止める。返す findings（`WORKSPACE_FILE_OBSERVED`、`WORKSPACE_DECLARATION_UNVERIFIED`、`--legacy` の観測、GitHub の確かめ）は今のまま。

### ほかの worktree の観測（統括の判断、2026-11-02）

- `resolve_observed_context(project, cwd, *, timeout)`（`project_context.py`。足す）：ほかの worktree の Git の識別（clone と worktree の物理の識別、HEAD、ブランチ）と宣言を返す。`resolve_context` と違い、版3の宣言も受け付ける。読むのは宣言だけで、`.meta.json` や仕様は読まない。`writer_protocol` の確かめは今のまま。
- 使うのは、ほかの worktree を観測する2か所だけ：`canonical_work.canonical_worktree_rows`（`work start` の重複選択と枝の占有の確かめ）と `canonical_workspace._observe_rows`（`workspace sync` の worktree の一覧）。その worktree の直接の選択の記録は、`WorkTargetStore` と `read_selection` で今と同じく読む（R-J7 の直接の選択）。
- 根拠：spec-dock のクローンには、利用者が残すと決めた版3の linked worktree が2つある（`local-macos-vm-ci`、`schema1-preserving-migration-20261004`）。版3の worktree を `unavailable` にすると、`check_inventory` が拒否し、同じクローンのすべての `work start` が止まる。ほかの4つのリポジトリには版3の worktree はない。
- 版3の worktree の中で実行したコマンドは、`resolve_context` で `WorkspaceNotMigrated` になり、`CANONICAL_NOT_MIGRATED` で止まる（R-440-01）。
- テスト：`tests/cli_runtime/test_issue431_workspace.py::test_sync_observes_a_schema_three_worktree_and_an_unreadable_one`（版3の worktree は観測でき、読めないものは `unavailable`。0.4.2 の意図を保つ）と、`test_a_schema_three_sibling_keeps_its_selection_observed_and_stops_its_own_commands`（版3の worktree の選択が `selected` に見え、同じ Scope の `work start` が `SCOPE_ALREADY_SELECTED`、その worktree の中の `scope list` が `CANONICAL_NOT_MIGRATED`）。

### `commands/canonical_dispatch.py`

- `CANONICAL_HANDLERS` から `workspace migrate` と `workbench copy` の行を消す。`refuse_workspace_migrate`（`canonical_refusals.py`。ファイルごと消す）と `refuse_workbench_copy`（`canonical_worktrees.py`）を消す。
- 表のキーの集合は、`LEAF_PATHS` から `help`、`completion`、`installation` の4つ、`canonical check`（`REPOSITORY_INDEPENDENT_HANDLERS` だけにある）を除いたものと等しい（46。`canonical sync` は両方の表にある）。

### `cli/catalog.py`、`cli/options.py`

- `LEAF_PATHS` から2つを消して53にする。`HELP_EFFECTS`、`HELP_PRECONDITIONS`、`MUTATING_LEAF_PATHS`、`LEAF_ARGUMENTS`、`RECOVERY_LEAF_COMMANDS`（`workspace migrate` の行）、`_CONFIRMATION_LEAVES` などの表から、その2つと消す引数を消す。
- `LEAF_ARGUMENTS`：`scope create *` と `scope import github *` の `--slug` を消す。`workspace validate` は `--require-nodes` だけ。`workspace sync --source` と `dependency check --source` は `choices=("github",)`（既定の値は今のまま `None`）。
- 説明の文（`HELP_EFFECTS`、`HELP_PRECONDITIONS`、`_READS_BY_ROOT`、`_DOES_NOT_BY_ROOT`、`_JSON_DATA_BY_ROOT` など）から、`Schema 4:` の前置き、`.meta.json` と「ローカルの metadata」、`--ci`、`--slug` の拒否、`CANONICAL_NOT_APPLICABLE` の文を消し、canonical モードの今の動きだけを書く。`options.py` の補完と使い方の文も同じ。
- `--slug` は `artifact create` には残る（Artifact の命名。R-J7）。

### `application/canonical_errors.py`

- `CANONICAL_NOT_APPLICABLE`、`CANONICAL_WORKBENCH_SHARED`、`MIGRATE_NOT_APPLICABLE_RECOVERY` と、それらだけを使う文を消す。`canonical_scope_read.py`、`canonical_writes.py`、`canonical_workspace.py` の、消した引数を拒否する分岐を消す。
- `NOT_MIGRATED_RECOVERY` を 0.5.0 の文にする（上）。

### Scope の作成（`application/canonical_scope_create.py`、`application/scope_scaffold.py`、`infra/canonical_scaffold.py`、`domain/canonical_scaffold.py`）

- `copy_scope_template_at` は、`render_text` と `final_replacements` だけを当てる。`strip_structure_front_matter`、`rebase_spec_dock_links`、`STRUCTURE_FRONT_MATTER_KEYS`、`_SPEC_DOCK_LINK` を消す（`domain/canonical_scaffold.py` には題名の規則と `TITLE_MAX_LENGTH` が残る）。
- `canonical_rules_links` と作成の前の確かめは、`artifacts.md` と `discussions.md` だけを見る。`_rules_source_paths` と `_rules_scaffold_specs` の `epics.md`・`issues.md` の分岐と、`epics/rules.md`・`issues/rules.md` の組を消す（canonical は今もそれらのリンクを作らない）。
- `templates/cue/{initiative,epic,issue}/report.md` の前付けから `タイトル:` と `親:` の行を消す。ほかの行と本文は変えない。0.4.2 では写すときにこの2行を除いていたので、作られる `report.md` のバイトは変わらない。

### `domain/ids.py`

- 消す：`INPUT_TITLE_RE`、`validate_slug`、`validate_input_title`、`derive_input_slug_from_title`、`resolve_input_title_and_slug`、そのほか到達の判定で使われないもの（`normalize_id_input`、`resolve_id_input`、`validate_lowercase`、`find_existing_id_by_num` など）。
- 残す：`CANONICAL_ID_RE`、`DEFAULT_ID_WIDTH`、`format_id`、`parse_id`、`slugify`、Artifact の `--slug` を確かめる `INPUT_SLUG_KEBAB_RE` と `validate_input_slug_kebab`（`direct_artifact.py` と `canonical_artifact_write.py` が使う。R-J7）。不正な Artifact の `--slug`（`Add_Token`）が今と同じ結果（`validate_input_slug_kebab` の `RuntimeError` が `dispatch()` に届き `LOCAL_IO_FAILED`、終了コード5）で止まり何も書かないことを、canonical の `artifact create` のテストで確かめる（今はない。失敗の形は R-J7 のため変えない）。

### 配布資産と `static-inventory.json`

- 外す：`spec_dock/templates/{initiative,epic,issue}/{requirement,design,plan,report}.md` と `…/.workbench/README.md`（15）、`spec_dock/docs/rules/initiative/epics.md`、`spec_dock/docs/rules/epic/issues.md`。`files` から消し、`retired` に `{"path", "known_old_sha256": [0.4.2 のバイト（と、`files` にあった既知の古い版）], "source_basis": {"commit": "caaeebe459726647fdebb9461843a3b120557fa4", "path": …}}` を足す。`installation update` は、`retired` の既知のバイトのファイルを退避して消し、変えられたファイルは `legacy static resource is modified or unknown; merge manually` で止める（今の `direct_static_update.py` の仕組み。変えない）。
- 退役してよい場所の許可（`infra/static_assets.py` の `package_retired_assets`）に、`RETIRED_LEGACY_SCAFFOLD_PATHS`（上の17のパスを名前で並べた `frozenset`）を足す。接頭辞では許さない（`spec-dock/templates/` の下の利用者のファイルや、ほかの雛形を消せる形にしない）。`tests/unit/infra/test_issue421_claude_skill_retirement.py` の「許可の外は止まる」のテストに、`spec-dock/templates/cue/issue/report.md` と `spec-dock/templates/issue/notes.md` が止まることを足す。
- 変える（`sha256` を 0.5.0 のバイトにし、`known_old_sha256` に 0.4.2 のバイトを足す）：版のファイル、`docs/migration.md`、`docs/canonical.md`、`docs/guide.md`、`docs/reference_*.md`、`docs/README.md`、`docs/cli-redesign-guide.html`、`docs/authoring/` と `docs/rules/` のうち従来モードの記述を消したもの、`templates/README.md`、`templates/cue/*/report.md`、`.agents/skills/spec-dock*/SKILL.md` など、実際に変えたすべて。どれを変えたかは差分から機械的に求め、テストで「`files` の各項目の `sha256` が今のバイトと一致し、0.4.2 から変えた項目は 0.4.2 のバイトを `known_old_sha256` に持つ」を確かめる（0.4.2 のバイトは `git show v0.4.2:<パス>` から作ったテストの見本で持つ）。
- `workspace.json`（`init_only`）は変えない。

### 文書（R-440-05）

- 規則の節（10章）と `AGENTS.md`、`.agents/skills/spec-dock/SKILL.md`：Epic の10章の撤去の指示のとおり、見出しを「## 仕様の扱い」にし（「（canonical モード）」を外す）、最初の段落の「3 のリポジトリでは、今までどおり、仕様もコードと一緒にコミットする。」の文を消す。「`spec-dock/workspace.json` の `schema_version` が 4 のリポジトリでは、次に従う。」の文は残す（版4のリポジトリにだけ当てはまる規則であることは変わらない）。規則の節に版3の動きの文は足さない。SKILL.md の「CUE の Scope と説明資料」の節の版3の文（「版3のリポジトリでは今までどおり Markdown の Scope を作り…」）を消す。既存の Markdown の Scope は読めて `scope check` が `checked=false` で通るので、「Markdown の Scope は今までどおり `spec-dock/docs/authoring/overview.md` から書く」の案内は、既存の Markdown の Scope を直すときの案内として残す。
- `migration.md`：「## 0.5.0 への更新」の節を「## 0.4.2 への更新」の節の後に足す（版の節は古い順に並んでいる）。版の節（0.4.0〜0.4.2）は変えない。版の節でない節は、「## schema3の旧writerから移行」（`workspace migrate` の手順）を消し、「## canonical モードへの移行」を「0.5.0 は版4だけを扱う。版3のリポジトリは、0.4.2 を入れ直し、`v0.4.2` の手順書に従って移す（手順書の 0.3.0 は 0.4.2 と読み替える）」の形に直し、ほかの節（「外部CLI」「新規導入」「static資産の更新・削除」「途中で停止した場合」）からも版3の文を消す。文書のテストは、0.5.0 の節の中身と、版の節でない節に `workspace migrate`、`workbench copy`、`schema 3`／版3で動く旨の文がないことを確かめる。
- README、`guide.md`、`canonical.md`、`reference_cli.md`、`reference_naming.md`、`reference_worktree.md`、`reference_sync.md`、`reference_deps.md`、`reference_github.md`、`authoring/`、`rules/`、`cli-redesign-guide.html`、`templates/README.md`：版3の動き、`.meta.json` の作成、入れ子の置き場、slug、`workspace migrate`、`workbench copy`、`--ci`、`--source local`、`CANONICAL_NOT_APPLICABLE`、`CANONICAL_WORKBENCH_SHARED` の記述を消すか、canonical の今の動きに書き直す。どの文書をどう変えたかは `report.md` に一覧で書く。

### 到達の判定の方法（D3）

1. `dispatch()` から従来の分岐を消した状態で、`src/spec_dock` のすべての `import`（関数の中を含む）のグラフを `spec_dock.cli`、`spec_dock.shim_vnext`、`spec_dock.asset_layout`、`spec_dock` から辿り、届かないモジュールを消す。
2. `vulture`（0.5.0 の作業のときの版。`uvx vulture src/spec_dock --min-confidence 60 --exclude src/spec_dock/assets`）の「unused function / class / method / import / property」を見て、本当に使われていないものを消す。テストだけが使うものも消す（そのテストは (a) か、消すコードだけを確かめる (c) として消す）。
3. 1と2を、何も見つからなくなるまで繰り返す。
4. 判定から外すもの：名前で呼ばれるもの（`html.parser.HTMLParser` の `handle_*` など）、配布する資産の中のスクリプト（`assets/install_root/.agents/skills/spec-dock-grill-with-docs/scripts/finalize-artifact`）、`dataclass` のフィールド（vulture の「unused variable / attribute」は見ない。クラスごと消すときはフィールドも消える）、従来モードと関係のない canonical の側の部品（後の機能のために置いた `infra/diagram_vendor.py`（epic-00425 の K5）、文書にした Python の入口 `scope_render.render_scope_html`、テストの差し込み口 `github_snapshot.clear_memory`、canonical の規則の部品 `canonical_structure.branch_names_scope` と `canonical_sync.registered_entries`）。外したものは `report.md` に書く。
   - vulture は名前で判定するので、同じ名前の関数がほかにあると見落とす（`work_start.start_work` と `canonical_work.start_work`、`direct_diagnostics.diagnose_workspace` と `canonical_workspace.diagnose_workspace` など）。そのため、モジュールごとの名前の参照（`from M import N`、`M.N`、モジュールの中の参照）を辿る判定も、何も見つからなくなるまで繰り返す。
   - 関数が呼ばれていても、canonical の呼び出し元が決まった引数だけを渡すために通らない分岐（従来の `.meta.json` の木を読む分岐）は、関数の中を読んで消す。2026-11-02 の試しで見つかったもの：`direct_artifact.query_artifact` と `mutate_artifact`、`artifact_query.list_artifacts` と `show_artifact`（canonical は `@root` だけを渡すので、`@root` だけの形にする）、`direct_worktrees` の `--expect-current` の確かめと `direct_installation.install_static_assets` の `--expect-current` の分岐（canonical はいつも `expect_current=None` で呼ぶ）。これで `scope_query.load_scope_views`、`infra/scope_tree.py`、`application/start_snapshot.py`（`LocalInput` は `start_plan.py` に移す）も届かなくなる。
5. 2026-11-02 の試し（従来の分岐を消した写しで1を1回）では、次のモジュールが届かなくなる。最終の一覧は `report.md` に書く。
   - 従来の処理：`application/direct_{active,dependencies,finish,migration,scope_delete,scope_edit,scope_lifecycle,scope_publish,sync,validation,workbench}.py`、`application/github_scope_scaffold.py`、`application/scope_ancestors.py`、`infra/{fs_repo,scope_metadata,committed_validation,workbench_publication}.py`。
   - 撤去の前から届かない古いモジュール：`application/{artifact_preflight,github_issue_targets,ports,repo_context,status_context,validate_tree}.py`、`domain/{active,deps,discussion_docs,status,tree,validation}.py`、`infra/{binary_artifact_publisher,deps_reader,fs_cli,git_helper,github_cli}.py`、`presentation/cli_text.py`。これらは、`.meta.json` を読む（`fs_cli`、`deps_reader`、`validation`、`artifact_preflight`）か、それらだけが使うもので、AC-20 のコードの検索に残るので、14章の到達の規則で消す。（`infra/diagram_vendor.py` も今は届かないが、4のとおり残す）
   - canonical の処理と同じファイルにある部分（`direct_worktrees.py`、`work_start.py`、`direct_artifact.py`、`direct_diagnostics.py`、`scope_query.py`、`start_snapshot.py`、`worktree_observation.py` など）は、2で従来の経路だけを消す。
- I-7 から：`committed_validation.py` が1で届かなくなれば、`ls-tree` の解析は `commit_tree.py` の1つだけになる。届くときは、`committed_validation.py` が `commit_tree.py` の解析を使う形にする。

### テストの分類の方法（R-440-07）

1. 静的な印：テストのファイルと `tests/support/` で、`.meta.json`、`"schema_version": 3`（と同じ意味の書き方）、`LEGACY_WORKSPACE_SCHEMA`、版3の作り物を作る補助（`tests.cli_runtime.test_issue413_contract.make_workspace`、`add_scope` など）を使うもの、消すモジュールを import するものを集める。
2. 動的な印：D1 と D2 を入れた後に全体のテストを流し、失敗したテスト（版3の宣言で止まるようになったもの、消したコードを使うもの）を集める。
3. 1か2に当たるテストを、テストの名前と主張から (a) か (b) に分ける。(b) は、R-440-07 の共通の契約のどれを確かめているかを書き、対応する canonical のテストを探す。なければ、`tests/support/canonical_scopes.py` の `CanonicalWorld`（偽の `gh` と一時のカタログ）で書き直す。
4. 当たらないテストは (c) で、変えない。ただし、コマンドの数、文書の中身、配布資産の一覧と値を確かめるテスト（testability の「従来モードの回帰」で変えてよいとされたもの）は、0.5.0 の値に直す。
5. 一覧は、ファイルごとの行（分類、件数、(b) の契約と対応する canonical のテスト、(a) の理由）で `report.md` に載せる。1つのファイルに分類が混ざるときは、テストの名前ごとに行を分ける。

## data / failure

- 宣言の読み取り：`read_guarded_json` の後、`schema_version` が整数の 4 なら受け付ける。整数の 3 なら `WorkspaceNotMigrated`。そのほか（ない、整数でない、5以上）は今と同じ `ValueError("workspace requires known schema 3 or 4")` の代わりに `ValueError("workspace requires known schema 4")`。`writer_protocol` の確かめは今のまま（4の後）。
- `require_migrated` は、宣言がない、読めない、壊れている、版が3でないときは何もしない（後の処理が今と同じ扱いをする）。
- 版3で止まるときは、どのコマンドも、宣言の読み取りのほかに何も読まない（スナップショット、カタログ、GitHub、`--expect-current` の選択の記録を読まない）。`effects` は空、`warnings` は空。
- `--dry-run` を付けても、版3で止まる結果は `--dry-run` のないときと同じである（`status` は `failed`、`data` は空の `DiagnosticData`）。`_render_result` は `FamilyData` にだけ `can_apply` と `blockers` を足すので、`DiagnosticData` の結果には足さない（今の規則のまま）。
- 0.4.2 の配布資産から 0.5.0 への `installation update`：`retired` の既知のバイトのファイルは退避して消す。利用者が変えた `.md` の雛形や `epics.md` は、`installation update` が今の規則（知らない変更は止まる）で扱う。

## 変更対象

- 変える：`infra/static_assets.py`（退役の許可）、`application/canonical_check.py`、`application/canonical_link.py`、`application/canonical_dashboard.py`、`commands/runtime_dispatch.py`、`commands/canonical_dispatch.py`、`application/project_context.py`、`application/canonical_errors.py`、`application/canonical_status.py`、`application/canonical_scope_create.py`、`application/canonical_scope_read.py`、`application/canonical_writes.py`、`application/canonical_workspace.py`、`application/canonical_worktrees.py`、`application/direct_installation.py`、`application/direct_diagnostics.py`、`application/scope_scaffold.py`、`infra/canonical_scaffold.py`、`domain/canonical_scaffold.py`、`domain/ids.py`、`cli/catalog.py`、`cli/options.py`、到達の判定で従来の経路だけを消すファイル。
- 消す：到達の判定で届かないモジュール（上の5）、`application/canonical_refusals.py`、配布資産の17ファイル（雛形の15と規則の2）、`scripts/migrate-to-canonical/`、`.github/scripts/specdock-ci-validate.sh`、(a) のテストと移行のスクリプトのテスト、消すコードだけを確かめるテスト。
- 足す：版3で全コマンドが止まるテスト、G7 の53のコマンドのテスト（今の `test_issue436_every_command.py` を直す）、0.5.0 の版と 0.4.2 からの更新のテスト（`test_issue501_release_0_4_2.py` の形）、(b) の書き直し。`test_issue501_release_0_4_2.py` からは、前例（コミット `5a7552b67`。0.4.1 の版の置き場の確かめだけを消した）と同じく `test_the_version_is_0_4_2_in_every_place` だけを消し、0.4.1 のバイトからの更新の経路のテスト（モードに関係のない (c)）は残す。
- 変えない：`direct_static_update.py` の更新と退避の規則、直接の選択の記録（`work-target`）、`StartLock`、`OperationResult` と出力の封筒、canonical の同期とカタログ、構造のスナップショット、ダッシュボード、`workspace doctor --legacy`、Artifact の命名、`workspace.json` の配布資産。

## 移行・互換性・rollback

| SpecDock | 宣言の版3 | 宣言の版4 |
|---|---|---|
| 0.4.2（両方のモードを持つ最後の版） | 従来モード | canonical モード |
| 0.5.0 | `CANONICAL_NOT_MIGRATED`（0.4.2 を入れ直して移す） | canonical モード |

- 0.5.0 は、R-J1 のすべてのリポジトリが版4になった後にだけ入れる（前提は満たした）。
- 戻し方：マージの前なら PR を閉じる。マージの後なら、PR を `git revert` するか、利用者の環境に 0.4.2 を入れ直す（0.4.2 は canonical モードと CUE の Scope を持つので、移したリポジトリはそのまま動く）。各リポジトリの配布資産を 0.5.0 に上げた後に戻すときは、0.4.2 の `installation update` で配布資産を戻すか、版のファイルを戻す PR を作る（検査のワークフローは版のファイルの版を入れるため）。撤去の後にリポジトリを従来の形に戻すときは、0.4.2 を入れ直し、版のタグ `v0.4.2` の移行のスクリプトで戻す。
- 0.3.0 を戻す先にしない理由：0.3.0 は CUE の Scope（0.4.0 から）を扱えず、5つのリポジトリには CUE の Scope がある。移行のスクリプトも `v0.4.2` のものが I-12 の注意点を含む最新である。Epic の `requirement.md`、`design.md`、`plan.md` の撤去の後の「0.3.0 を入れ直す」と「版のタグ `v0.3.0` に残る」を、この Issue で「0.4.2」と「`v0.4.2`」に直す（統括の依頼の8。R-440-09 の一覧）。

## testability

- AC-440-01：版3の宣言を持つ一時のリポジトリ（Git の初期化と宣言だけ。カタログも `.meta.json` もいらない）で、50のコマンドを、それぞれ最小の正しい引数で `main()` から呼ぶ。終了コード、`error.code`、`effects`、`recovery` の文、`tree_digest` が変わらないことを確かめる。`installation init` は宣言のある宛先を渡す。`canonical check` は版3の宣言のコミットで失敗の1件を確かめる。
- AC-440-02：`test_issue436_every_command.py` を、53のコマンドの表と `CANONICAL_HANDLERS` の一致、拒否するだけのコードがないこと、消したコマンドと引数が引数の誤りになることを確かめる形に直す。
- AC-440-03：コードの検索をするテスト（`.meta.json` の名前が canonical の検査のファイルだけにあること、版3を受け付ける定数と分岐（`LEGACY_WORKSPACE_SCHEMA`、`workspace_mode`、`probe_workspace_mode`）がなく、版3の名前は止めるための `NOT_MIGRATED_WORKSPACE_SCHEMA` だけであること）を足す。到達の判定は手順を `report.md` に書く。
- AC-440-04：配布資産のテスト（`static-inventory.json` と雛形の一覧）と、canonical の `scope create` の作るファイルの見本のテスト（`test_issue474_scope_create.py` など今のもの）が、雛形から2行を外しても同じバイトを確かめる。
- AC-440-05：文書の中身のテスト（`test_issue436_docs.py`、`test_issue436_agent_rules.py`、`test_cli_docs_vnext.py` など）を、従来モードの記述がないことと、0.5.0 の案内があることを確かめる形に直す。
- AC-440-08：`tests/integration/test_issue440_release_0_5_0.py`（足す）で、版、`migration.md` の節、`static-inventory.json` の既知の古い版、0.4.2 の配布資産からの `installation update` を確かめる。0.4.2 のバイトは `tests/fixtures/issue440/` に置く。
- AC-440-09：wheel の確かめは、テストの外で行い、`report.md` に書く（今の `test_issue413_wheel.py` は全体のテストで通す）。
- 共通の契約：(b) の書き直しのテストは、元のテストと同じ主張（終了コード、`status`、`effects`、書かないこと、記録のバイト）を確かめる。

## risk

- **共通の契約のテストを失う**：一覧で (b) ごとに対応を書き、レビューで確かめる。迷うものは消さずに統括に聞く。
- **canonical の処理が従来の部品を使っているのに消してしまう**：到達の判定は import のグラフと vulture の両方で行い、消すたびに全体のテストを流す。canonical のテストが失敗したら消しすぎである。
- **vulture の見落とし**（名前が同じものがあると使われていると見なす）：消し残しは動きを変えないので、見つけたら消す。レビューで残りを確かめる。
- **0.4.2 の配布資産からの更新が止まる**：変えたすべての配布資産に 0.4.2 のバイトを足したことを、テストで機械的に確かめる。dogfood の更新を、この PR で実際に行って確かめる。
- **0.5.0 で、0.4.2 の雛形のまま Scope を作る**：`report.md` に前付けの2行が残るだけで、正本ではない。`migration.md` に、パッケージの後に `installation update` することを書く。
- **差分が大きい**：コミットを意味のまとまり（受け付けと振り分け、コマンドと引数、到達できないコードの削除、雛形と名前の規則、文書、スクリプト、版と dogfood）に分ける。
