---
種別: 設計書（Issue）
ID: "iss-00436"
タイトル: "Integrate Agent Rules Docs And Release"
関連GitHub: ["#436"]
状態: "approved"
最終更新: "2026-10-30"
依存: ["requirement.md"]
親: ["epic-00424", "init-00423"]
---

# iss-00436 Integrate Agent Rules Docs And Release — 設計

詳細: [Design Guide](../../../docs/authoring/design.md)

## 設計目標

- 規則、使い方、CLI 参照、`help` の4つの文書を、runtime の定数とテストで結び、片方だけを直したずれをテストで見つける（文書が実装から離れないこと）。
- 53のコマンドが版4で答えることと、`link` から `work finish` までの横断の流れを、既存のテストの部品（偽の `gh`、一時の bare のリポジトリ、偽のスケジューラ）だけで確かめる。新しいテストの基盤は作らない。
- 引き継ぎの直しは、それぞれの持ち主のモジュールの中の小さな変更にとどめ、C1〜C11 の公開の形と従来モードを変えない。

## Current / Target

| 項目 | Current（`ea3d3c9ee`） | Target |
|---|---|---|
| 規則の節 | なし（スキルは版3の運用だけ） | スキルと `AGENTS.md` に同じ項目の節。破壊的なコマンドに `canonical remove` |
| 使い方の文書 | なし | `docs/canonical.md`（新設）。4つの文書と `README.md` から参照 |
| `reference_cli.md` | 表は53の行だが冒頭の文は「52」、`--slug` の説明が従来のまま、`docs/README.md` は「全47」 | 冒頭の文も53、平らな置き場と ID、canonical モードの引数の扱い、エラーの一覧への参照。`docs/README.md` は53 |
| `cli-redesign-guide.html` | 「全44コマンド」と C01〜C44 | 53のコマンド（C45〜C53 を足す） |
| `help` | `canonical link` の Writes に refspec とブランチの付け替えがない。作成と Start の `help` に置き場と ID がない | 足す（Writes と Effects の文。引数は変えない） |
| `CANONICAL_NOT_IMPLEMENTED` | `dispatch_canonical` の表にないコマンドで返す | 経路と定数を消す。表にないものは来ないことをテストで守る |
| 横断のテスト | なし（Issue ごとのテスト） | `tests/cli_runtime/test_issue436_end_to_end.py` |
| 全コマンドのテスト | なし | `tests/cli_runtime/test_issue436_every_command.py` |
| `CLAUDE_CONFIG_DIR` | 見ない | ユーザーの設定の場所に使う |
| `resume --push-local` | 取り込み直しの途中でも push する | 止める |
| `migrate.py undo` | 記録がなくても0 | 記録がなければ2で止まる |
| 版 | 0.2.4 | 0.3.0 |
| 利用側の `spec-dock/` | 0.2.4 の配布資産（一部 `known-old`、新しい資産は `missing`） | 0.3.0 の配布資産、宣言は版3のまま |

## 責務・Interface

### 規則の節（R-436-01）

- 本文は Epic の `design.md` 10章の節をそのまま使い、R-436-01 の5つの項目を足す。スキルは英語の文書だが、この節は日本語のまま置く（10章の節が正本で、`AGENTS.md` と同じ文面にするため。エージェントはどちらも読める）。
- 置き場：
  - スキル：`SKILL.md` の「Distinguish the four owned layers」の後に `## 仕様の扱い（canonical モード）`。「Destructive boundary」の列挙に `canonical remove` を足す。
  - `AGENTS.md`：「SpecDock Agent-First Operations」の後に同じ見出しの節。「Require an exact target and explicit destructive outcome …」の列挙に `canonical remove` を足す。
- テスト（`tests/unit/infra/test_issue436_agent_rules.py`）：2つのファイルから見出しの節を切り出し、項目（箇条書き）の並びが同じで、10章の各項目と R-436-01 の追加の項目に当たる語の対応表（項目ごとに1つ以上。例：Git で扱わない → `git add`、`stash`、`reset`、`checkout`、`clean`。名前と位置を変えない → 「名前を変えたり」。サンドボックス → 「普通の端末」。設定 → 「自分でツールの設定を変えない」）の語をすべて含むことを確かめる。対応表の語の例（`spec-dock/initiatives/`、`git add`、`spec-dock canonical link`、`spec-dock canonical status`、`rg`、`<区切り>/<ID>/`、`scope show <ID> --json`、`*.conflict-*`、`--worktree`、`spec-dock work finish`、`rm spec-dock/initiatives`、`git clean -ff`、`iss-454`、`--slug`、`scope move`、`SCOPE_KIND_CHANGED`、`SCOPE_IN_PROGRESS`、`180`）をすべて含むことを確かめる。`AGENTS.md` はリポジトリのルートのファイルなので、ないときは失敗させる（提供側のリポジトリのテスト）。

### 使い方の文書（R-436-02）

- `src/spec_dock/assets/spec_dock/docs/canonical.md` を足し、`static-inventory.json` の `files` に、ほかの文書と同じ形の項目として足す（新しい資産。`known_old_sha256` は空）。
- 節の見出しは R-436-02 の1〜10に対応させる：`## モードと置き場`、`## 用意と状態`、`## ツールの設定`、`## 保存と同期`、`## 同期が止まったとき`、`## Linux とコンテナ`、`## 構造のスナップショットとダッシュボード`、`## 制約`、`## 既定のブランチの検査`、`## エラーと次の1手`。
- ツールの1行は、`domain/canonical_tools.py` の関数が作る文字列（`canonical status` が示すもの）と同じ字面を、`<カタログ>` を置いた形で書く。テストは、その関数に `<カタログ>` を渡した結果が文書に含まれることを確かめる（AC-07）。
- 5つのカタログの例は、R-J1 の5つのリポジトリの mainのチェックアウトの `spec-dock/.canonical` の絶対パスを、例のパス（`/path/to/<repo>/spec-dock/.canonical`）で並べる（利用者の実際のパスは書かない）。
- エラーの一覧は、Epic の12章の表と同じ形（コード、終了コード、次の1手）の Markdown の表にし、12章で別の Issue の設計書を参照している行も、ここでは次の1手を文で書く（文書だけで使えるように）。

### CLI 参照と `help`（R-436-03）

- `reference_cli.md`：表の C01〜C06 の `--slug` の欄に「schema4 では使えません」を、C16 に「schema4 の既定の branch は `<ID>`」を足す。冒頭の段落の数を53にし、canonical モードの置き場と ID の段落と `canonical.md` へのリンクを足す。
- `cli-redesign-guide.html`：今の表の形（C01〜C44 の行）に C45〜C53 の行を足し、「全44コマンド」を「全53コマンド」にする。
- `help`：`cli/catalog.py` の `HELP_EFFECTS` は1行の要約なので変えない。`canonical link` の Writes の文（`_help_spec` の `elif leaf == "canonical link":` の枝）に refspec、`update-ref`、登録簿、定期の実行、基準を足す。`scope create *`、`scope import github *`、`work start`、`work finish` の `HELP_PRECONDITIONS` の文に、schema 4 の置き場、`--slug` の拒否、既定のブランチ名、`SCOPE_IN_PROGRESS`、180秒の待ちと `CANONICAL_SAVE_UNCONFIRMED`、`CANONICAL_TITLE_IGNORED` を足す。引数の定義は変えない。文は版3の `--help` にも出る（文書の中身の変化として扱う）。
- テスト：`reference_cli.md` と HTML の C01〜C53 の行のコマンドの集合が `LEAF_PATHS` と同じこと（`tests/unit/infra/test_issue436_docs.py`）。`help` の文はそれぞれの語を確かめる。

### エラーの一覧と実装の対応（R-436-04）

- 実装の側の集合：`src/spec_dock/runtime` の、`application/canonical_*.py`、`domain/canonical_*.py`、`infra/github_structure.py`、`infra/github_snapshot.py` の、`NAME = "NAME"`（`Final` を含む）の形の定数のうち、名前が `CANONICAL_`、`GITHUB_`、`SCOPE_`、`DEPENDENCY_`、`PARENT_`、`KIND_`、`SUB_ISSUE_`、`READINESS_` で始まるもの、`application/canonical_errors.py` のすべてのコードの定数（`START_LOCK_BUSY`、`OS_ACCESS_DENIED` を含む）、`canonical check` の失敗の種類（`canonical_check.py` の定数）、同じモジュールに字面で書かれた `"CANONICAL_…"` の文字列。`CANONICAL_NOT_IMPLEMENTED` は消すので入らない。
- 文書の側の集合：`canonical.md` の `## エラーと次の1手` の表の、最初の列の `` `CODE` `` のすべて。
- テストは、実装の側の集合が文書の側に含まれ、文書の側のほかのコード（`ValueError` の前置きの `DESCENDANT_STATUS_UNKNOWN`、`READINESS_UNKNOWN` など）も runtime のソースのどこかに同じ字面があり、表のどの行も3列目（次の1手）が空でないことを確かめる。`GITHUB_STRUCTURE_INVALID` は runtime にないので載せない。
- Epic の `design.md` の12章の表：`GITHUB_STRUCTURE_INVALID` の行を、実装の構造の異常のコード（`KIND_LABEL_MULTIPLE`、`PARENT_MISSING` など。`workspace validate` の findings と構造の読み取り）の行に置き換える。`CANONICAL_SAVE_UNCONFIRMED` の終了コードを「3（束を書く前）／6（partial。束を書いた後）」にし、`CANONICAL_PROGRESS_MARK_FAILED` の行（警告。次の1手は「GitHub で `spec-dock:in-progress` のラベルと担当者を確かめて付け外す」）を足し、`CANONICAL_NOT_IMPLEMENTED` の行を「0.3.0 では返さない（I-9 で経路を消した）」にする。ほかの章は変えない。

### すべてのコマンドが答える（R-436-05）

- `commands/canonical_dispatch.py` の `dispatch_canonical` は、表を直接引く（`CANONICAL_HANDLERS[namespace.command_path]`）。表にないコマンドは来ない（`installation`、`help`、`completion` と、リポジトリによらない表のものは `dispatch()` が先に振り分ける）ことを、下の表のテストで守る。`application/canonical_errors.py` の `CANONICAL_NOT_IMPLEMENTED`、`NOT_IMPLEMENTED_RECOVERY`、`canonical_not_implemented` を消す。
- テスト：
  - 表のテスト：`LEAF_PATHS` の各要素が、`CANONICAL_HANDLERS`、`REPOSITORY_INDEPENDENT_HANDLERS`、モードによらない集合（`installation init`、`show`、`update`、`uninstall`、`help`、`completion`）のどれかに入る。
  - 実行のテスト：`WriteWorld`（I-5 の部品。リンク済みの版4のクローンと偽の `gh`）の上で、`origin` を一時の bare のリポジトリにし、`repository_for_checkout` を偽のリポジトリに差し替え、`work finish` の待ちの時計を注入して、53のコマンドのそれぞれに、受け付ける引数（対象は作っておいた Scope。書くコマンドは本当に書くか `--dry-run`）を与えて、プロセスの中で `main()` を1回呼ぶ。例外で落ちず（落ちればテストが落ちる）、JSON の結果が読め、`command` が同じで、`error.code` が `CANONICAL_NOT_IMPLEMENTED` でなく、canonical モードのコード（`CANONICAL_*`、`GITHUB_*`、`SCOPE_KIND_CHANGED`）の失敗なら `recovery` があることを確かめる。`PRECONDITION_FAILED`、`SCOPE_NOT_FOUND`、`WORK_START_REQUIRED` などの汎用のコードは、共有の `dispatch()` が `ValueError` と `LookupError` から作り、版3と同じ形なので、`recovery` を求めない（R-436-04）。`help` と `completion` は JSON を返さないので、終了コード0だけを見る。
  - 表から消すことに伴い、`CANONICAL_NOT_IMPLEMENTED` の暫定の経路を確かめていた canonical モードのテスト（`tests/cli_runtime/test_issue428_canonical_mode.py` の2つ、`tests/unit/commands/test_canonical_dispatch.py` の1つ）を消すか、別の canonical の拒否で確かめる形に直す。版3の振る舞いのテストではない。

### 横断のシナリオ（R-436-06）

- `tests/cli_runtime/test_issue436_end_to_end.py`。1つの bare のリポジトリ（`origin`）から2つのクローン A と B を作り、両方の構造のリポジトリを偽の `gh` の1つのリポジトリにする（I-5 の `test_issue432_work_finish.py` と同じく `repository_for_checkout` を差し替え、`origin` は bare のまま）。2台のPCの代わりなので、A と B のコマンドは別の `XDG_STATE_HOME` で実行し（コマンドごとに環境変数を切り替え、メモリーの上のスナップショットも消す）、登録簿、`state.json`、構造のスナップショットを分ける。
- 定期の実行は `canonical_scheduling.scheduler_for` を偽物（`tests/conftest.py` の `periodic_jobs`）にし、環境の判定を、`tests/support/canonical_repo.environment()` の結果を `dataclasses.replace` で `system="linux"` と `systemd_present`、`systemd_user`、`linger` の値に変えたもの（systemd と `loop` の2通り。I-3 の `test_issue430_canonical_link_schedule.py` と同じ形）で注入する（パラメーター）。`detect_service_manager` は `tests/conftest.py` が差し替え済みで、注入した値をそのまま使う。`work finish` の「すぐの実行」は、偽のスケジューラの `kick` で B の `canonical sync` を1回まわす。
- 流れ：A `canonical link` → A `scope create initiative`（日本語の題名）と `epic`、`issue` → A でその Issue の `design.md` を編集 → A の `worktree create` のworktreeから、保存の前に読める（AC-02 の同じPC） → A `canonical sync` → B `canonical link` → B `canonical sync` → B で A の編集が読める → B `scope show`（偽の `gh` の記録で全体の取り直しがないこと）→ B `work start iss-…` → B で `plan.md` を編集 → B `work finish --yes` → bare のリポジトリに B の編集があり、Issue が `completed` で閉じている → A `canonical sync` の後、A でも読める。
- 選んだ仕組み（`systemd` か `loop`）が `canonical link` の登録で使われたことを、偽のスケジューラの記録で確かめる（`--no-schedule` は使わない）。

### 引き継ぎの直し（R-436-07）

- `CLAUDE_CONFIG_DIR`：`application/canonical_tools_check.py` の `_claude_settings` のユーザーの設定の場所を、`environ.get("CLAUDE_CONFIG_DIR")` が空でなければ `Path(値) / "settings.json"`、なければ `home / ".claude/settings.json"` にする。環境変数は、すでに注入できる `RuntimeEnvironment.environ` から読む。示す1行の「ファイルの場所」（`domain/canonical_tools.py` の `CLAUDE_USER_SETTINGS_FILE` を使う文）は、同じ規則で求めた場所を示す。場所の規則は `domain/canonical_tools.py` の `claude_user_settings(environ, home)` の1か所に置く。相対パスか `~` で始まる `CLAUDE_CONFIG_DIR` は場所を決められないので、そのユーザーの設定を「読めない」として扱い、判定を `CANONICAL_TOOL_SETTING_UNKNOWN` にする。テストの `isolate_user_state` は `CLAUDE_CONFIG_DIR` も消す（利用者の値がテストに入らないように）。
- `resume --push-local`：`application/canonical_resume.py` の `_resume` で、`wanted == "--push-local"` かつ `state.adopt_remote_pending` のとき、push の前に `CANONICAL_PAUSED`（終了コード3）で止める。次の1手は「GitHub の `spec-dock/canonical` を、取り込み直しの元にした履歴で作り直さない。別のPCかカタログで GitHub の canonical を確かめ、戻っていれば `spec-dock canonical resume --adopt-remote`。消したままにするなら利用者に確かめる」。`details` に `adopt_remote_pending: true`。
- `migrate.py undo`：`command_undo` の始めで、`undo.jsonl` のファイルがなければ `Refused`（終了コード2）で止める。文は「no work record at <path>」、次の1手は「register を実行したときと同じ `--state-dir`（既定は `scripts/migrate-to-canonical/.state/`）を渡す」。
- undo の後の再 register：`tests/integration/migration/` の既存の部品（偽の `gh` と一時のリポジトリ）で、ローカルの Scope の置き換えで Issue を作る `register --apply` → `undo --apply` → `register --apply` を通し、2回目が新しい番号の Issue を作り、`idmap.json` がその番号を指すことを確かめる。

### 版と配布資産（R-436-08）

- `pyproject.toml` の `version`、`src/spec_dock/assets/spec_dock/system/spec-dock-version`、`uv.lock` の `spec-dock` の `version` を 0.3.0 にする。`static-inventory.json` の版のファイルの `known_old_sha256` に `0.2.4\n` の SHA-256 を足す。文書を変えた資産（`docs/README.md`、`guide.md`、`migration.md`、`reference_cli.md`、`cli-redesign-guide.html`、スキル）の `sha256` を新しい値にし、前の値を `known_old_sha256` に足す。
- 版の文字列 `0.2.4` を固定で比べているテストのうち、「今の版」を意味するもの（版のファイルの一致など）は、`pyproject.toml` から読む今の形のままで通る。過去の版を意味するもの（`0.2.4` の利用側の写し、`release-tag` の判定の例）は変えない。
- 利用側の更新：0.3.0 の候補の wheel を一時の環境に入れ、その console で `installation update --target <この worktree> --dry-run` → `--backup-dir <新しい一時ディレクトリ> --yes` を行う。

### btrfs での選択の記録の確かめ（R-436-09）

- `WorkTargetStore.read()` は、保持したディレクトリの記述子から `os.open(".", O_RDONLY | O_DIRECTORY | O_NOFOLLOW, dir_fd=…)` で毎回新しい記述子を開いて列挙し、閉じる（`_list_fresh`）。保持した記述子と identity の確かめ（`_verify_directory`）は今のまま。
- テストは `tests/unit/infra/test_work_target_store.py` に、一度列挙した記述子は閉じるまで空を返す偽の `os.listdir` を使うものを足す。

## data / failure

- 新しいデータはない。`canonical.md` は配布資産で、`installation update` が知っている中身なら置き換える。
- `resume` の拒否は書く前（`failed`、効果なし）。`undo` の拒否も書く前（終了コード2）。
- 横断と全コマンドのテストは、`XDG_STATE_HOME` を一時ディレクトリにし、`github_api_for` と `repository_for_checkout` を偽物にするので、外のネットワークと利用者の状態に触れない。

## 変更対象

- 足す：`src/spec_dock/assets/spec_dock/docs/canonical.md`、`tests/cli_runtime/test_issue436_end_to_end.py`、`tests/cli_runtime/test_issue436_every_command.py`、`tests/unit/infra/test_issue436_agent_rules.py`、`tests/unit/infra/test_issue436_docs.py`、引き継ぎの直しのテスト（各モジュールの既存のテストのファイルに足す）。
- 変える：`src/spec_dock/assets/install_root/.agents/skills/spec-dock/SKILL.md`、`AGENTS.md`、`README.md`、`src/spec_dock/assets/spec_dock/docs/{README.md,guide.md,migration.md,reference_cli.md,cli-redesign-guide.html}`、`src/spec_dock/assets/static-inventory.json`、`src/spec_dock/assets/spec_dock/system/spec-dock-version`、`pyproject.toml`、`uv.lock`、`src/spec_dock/runtime/cli/catalog.py`（文だけ）、`src/spec_dock/runtime/commands/canonical_dispatch.py`、`src/spec_dock/runtime/application/{canonical_errors.py,canonical_tools_check.py,canonical_resume.py}`、`src/spec_dock/runtime/domain/canonical_tools.py`（場所の文を求める部分だけ）、`scripts/migrate-to-canonical/{migrate.py,README.md}`、Epic の `design.md` の12章の表、この worktree の `spec-dock/` の配布資産（`installation update` が書く）。
- 変えない：従来モードの処理（`direct_*.py`、`work_start.py`、`.meta.json` の読み書き）、版3の振る舞いのテスト、C1〜C11 の公開の形、コマンドと引数の数。

## 移行・互換性・rollback

- 版3のリポジトリ：規則の節と `canonical.md` が配布されるだけで、振る舞いは変わらない。`installation show` は新しい資産を `missing`、変えた資産を `known-old` と示し、`installation update` で `current` になる（今の資産の更新の規則）。
- 0.2.4 の利用者：0.3.0 の配布資産は 0.2.4 の `installation update` には知らない中身なので、package を先に上げる（今の規則）。
- rollback：PR を `git revert` すれば戻る。版のタグ `v0.3.0` がマージの後に作られた後に戻すときは、タグは残る（`release-tag.yml` は版が上がったときだけ作る）。

## testability

| AC | 確かめ方 |
|---|---|
| AC-436-01 | `test_issue436_agent_rules.py`（項目の一致と必須の語、破壊的なコマンド）。白紙のエージェントの試行は、一時ディレクトリの作り物のカタログ（規則の節を `AGENTS.md` に置き、`spec-dock/initiatives/00000-00999/iss-00001/` と `*.conflict-*` のファイルを置いたもの）で行う |
| AC-436-02 | `test_issue436_docs.py`（節の見出し、参照のリンク、ツールの1行の字面） |
| AC-436-03 | `test_issue436_docs.py`（53の行と `LEAF_PATHS`）、`help` の文のテスト |
| AC-436-04 | `test_issue436_docs.py`（コードの集合の一致と次の1手） |
| AC-436-05 | `test_issue436_every_command.py` と、`rg CANONICAL_NOT_IMPLEMENTED src/` が0件 |
| AC-436-06 | `test_issue436_end_to_end.py`（systemd と loop のパラメーター）。Epic の AC-16 のうち、変化のない周期が 304 だけで終わることと、題名の変更の後の周期で取り直すことは、I-3 の `test_issue430_canonical_sync.py` と I-11 の `test_issue438_canonical_dashboard.py` が確かめている（この Issue では重ねない） |
| AC-436-07 | `test_issue429_canonical_status.py` などの既存の canonical のテストのファイルへの追加、`test_issue430_canonical_resume.py`、`tests/integration/migration/` |
| AC-436-08 | wheel の外の環境での確かめ（報告書）、利用側の `installation show`（`workspace.json` は `known-old`、ほかは `current`）と `workspace validate` と `specdock-ci-validate.sh` |
| AC-436-09 | `make lint`、`uv run pytest`、`git diff --stat ea3d3c9ee -- tests/` の確かめ。0.2.4 と 0.3.0 の版3の出力の比べ（`ea3d3c9ee` の `git archive` から一時ディレクトリで作った wheel と、候補の wheel を、別の一時の環境に入れ、同じ版3の作り物のリポジトリで同じコマンドの `--json` を比べる。許す差：`package_version` と版のファイルの値、配布資産の分類と `sha256`、`help` の文） |
| AC-436-10 | OrbStack の仮想マシンと Docker のコンテナと macOS での実機の確かめ（報告書） |

- 実機の確かめの形：
  - 仮想マシンとコンテナと macOS の確かめには、0.3.0 の候補の wheel と、テストの偽の `gh`（`tests/support/fake_github.py` を、ネットワークを使わない実行ファイルとして置いたもの）だけを使う。利用者の `gh` と資格情報は入れない。リモートは一時の bare のリポジトリにする。構造のリポジトリは `origin` の URL から決まるので、`origin` は `https://github.com/<例>/<例>.git` の形にし、カタログのworktreeだけの設定（`extensions.worktreeConfig` と `git config --worktree url.<bare>.insteadOf https://github.com/<例>/<例>.git`）で、同期の fetch と push だけを bare のリポジトリに向ける（mainのチェックアウトの `remote get-url` は GitHub の形のまま）。うまくいかなければ、何を確かめられなかったかを報告書に書く。
  - macOS の `work finish`：一時の `HOME` と `XDG_STATE_HOME`、`--no-schedule` のリンク、待ちの間に別のプロセスで数秒ごとに `canonical sync` を回す（利用者の `~/Library/LaunchAgents/` に書かない）。
  - Git 2.38 ちょうどは、Alpine 3.17 のコンテナ（git 2.38 の包み）で確かめる。

## risk

| リスク | 影響 | 軽減 |
|---|---|---|
| 文書のテストが語の有無だけを見て、意味のずれを見逃す | 中 | 項目の一致（2つの節）と、コードの集合の一致（エラーの一覧）は集合で比べる。白紙のエージェントの試行で、節の使いやすさを確かめる |
| 全コマンドのテストの引数が、コマンドの振る舞いを確かめずに通るだけになる | 低 | このテストの目的は G7（答えること）に限る。各コマンドの振る舞いは各 Issue のテストが確かめている |
| `installation update` が利用側の知らない中身で止まる | 中 | dry-run で先に分類を見る。止まったら手で直さずに統括に報告する |
| 実機の確かめで、CI の仮想マシンとメモリを取り合う | 中 | 1台ずつ動かし、終わったらすぐ消す |
| 版の文字列を固定で比べるテストが落ちる | 低 | 今の版を意味するものだけを直し、過去の版の例は変えない（変えたテストは報告書に一覧で書く） |
