---
種別: 要件定義書（Issue）
ID: "iss-00440"
タイトル: "Remove Legacy Mode"
関連GitHub: ["#440"]
状態: "draft"
最終更新: "2026-11-02"
親: ["epic-00424", "init-00423"]
---

# iss-00440 Remove Legacy Mode — 要件定義

詳細: [Requirement Guide](../../../docs/authoring/requirement.md)

表示名：従来モード（宣言の版3、`.meta.json`）のコード、テスト、文書を消し、canonical モードだけを持つ SpecDock 0.5.0 を出す（Epic の I-13）

## 目的

SpecDock が1つの仕組みだけになる。コード、テスト、文書から従来モードが消え、エージェントが2つのモードで迷わない。版3の宣言のリポジトリでは、どのコマンドも、移る方法を示して書く前に止まる。

- 材料：Epic の `plan.md` の「I-13 Remove Legacy Mode」の節（価値、作るもの、受け入れ、マージの後、I-8 と I-7 から引き継ぐもの、注意）と「実装担当への共通の指示」、Epic の `design.md` の14章「撤去（R-J6〜R-J8）」、「撤去で消すもの（I-13）」、12章（コマンドの一覧と出力の契約、`CANONICAL_NOT_MIGRATED` の 0.5.0 の次の1手）、testability の「従来モードの回帰」、Epic の `requirement.md` の R-J6〜R-J8 と AC-20、統括の依頼（2026-11-02。0.4.2 の後に入った改善を 0.5.0 の「更新」の節に書くこと、戻し方の版を確かめること）。
- 依存：I-12（`iss-00439`。5つのリポジトリの切り替えと、その後の運用の点検）。Planning Level：strict（理由は `plan.md`）。
- 契約 C2（宣言の版とモードの判定、`dispatch()` の振り分けの入口、`REPOSITORY_INDEPENDENT_HANDLERS`）を、Epic の契約の表の注記（I-13 で、版4だけの判定に変える）のとおり、この Issue が変える。契約 C7（版のファイルと検査のワークフローの見本）は、版を 0.5.0 にするために使う。

## 背景

- Epic の R-A6 により、0.3.0〜0.4.2 は、宣言の版3のリポジトリを従来モード（`.meta.json` と入れ子の置き場）で、版4のリポジトリを canonical モードで扱ってきた。従来モードは、R-J1 のリポジトリを移し終えるまでの、移行の間だけの扱いである。
- I-10（spec-dock、2026-10-30）と I-12（input-devices、company-os、housing-lifecycle、taikyohiyou_project、2026-11-01）で、R-J1 の5つのリポジトリは、すべて版4になり、0.4.2 を使っている。
- 2026-11-02 に、利用者が、I-12 の後の運用の点検（`iss-00439` の `report.md` の「運用の点検」：同期の周期6436件がすべて ok、5つのカタログに未解決の異常なし、カタログの `HEAD` が GitHub と同じ）を見て、戻す必要がないことを確かめ、I-13 を始めることを決めた。
- 0.4.2 の後に、次の2つの改善が main に入った。0.5.0 の「更新」の節に書く（統括の依頼）。
  - #496（PR #503）：`installation update`（`--dry-run` と、途中で止まった場合を含む）が `.claude/skills/spec-dock*` の古い写しを外すとき、リンクがない枠ごとに、外枠の `warnings[]` に `CLAUDE_SKILL_LINK_MISSING`（`details`：`slot`、`link_target`、`command`）が出る。終了コード、`status`、`effects`、`data.result` は変わらない。
  - #497（PR #504）：配布する `spec-dock/.gitignore` に `!**/.workbench/` を足した。ルートの `.gitignore` が `.workbench/` を無視していても、`spec-dock/` の下の `.workbench/README.md`（雛形の README を含む）がコミットの対象になる。ほかの中身は無視のまま。
- 2026-10-25 の時点で、`.meta.json` を扱うテストのファイルは100のうち50（717件）あった。今はテストのファイルが219ある。従来の処理と canonical の処理は、同じモジュールの部品を共有しているところがある（`direct_worktrees.py`、`work_start.py`、`direct_artifact.py` など）。
- 関係者：
  - 利用者とエージェント：コマンド、`--help`、文書に、版3の説明と、canonical モードで拒否するだけのコマンドと引数がないこと。
  - 統括：マージの後に、0.5.0 を利用者の環境に入れ、ほかの4つのリポジトリの配布資産を `installation update` で 0.5.0 に上げる（R-J8）。
  - 撤去の後に見つかった、移していないリポジトリかクローン：移る方法を示されて止まること（Epic の requirement.md の境界条件）。

## 観測可能な要件

### R-440-01 版3の宣言では、すべてのコマンドが書く前に止まる（R-J6、14章の2）

- `spec-dock/workspace.json` の `schema_version` が 3 のリポジトリ（worktree を含む）で、次のどのコマンドも、何も読み書きせずに `CANONICAL_NOT_MIGRATED`（終了コード3、`status` は `failed`、`effects` は空）で止まる。
  - 公開の53のコマンド（R-440-02）から、宣言を読まない `help` と `completion` を除いた51のうち、`canonical check` を除く50のコマンド。`installation show`、`installation init`、`installation update`、`installation uninstall`、`workspace doctor --raw`、`canonical sync`（`--registered` のないもの）を含む。`--dry-run` を付けても同じ。
  - `recovery` は1つの文で、「SpecDock 0.4.2 を入れ直し、版のタグ `v0.4.2` の `scripts/migrate-to-canonical/README.md` に従って移す」を示す（R-440-09）。
- `canonical check` は、今と同じく、版3の宣言を失敗の1件（`CANONICAL_CHECK_FAILED`、終了コード7）として返し、その次の1手に同じ文を使う（8章）。
- `help` と `completion` は、宣言を読まずに今と同じに動く。
- `canonical sync --registered` は、登録簿のカタログを処理するもので、宣言の版を読まない。今と同じに動く。
- 版が 5 以上、整数でない、宣言がない、壊れているときは、今と同じく `PRECONDITION_FAILED`（終了コード3）で止まる。`workspace doctor --raw` は、宣言がないか読めないときに、今と同じく宣言のファイルの観測だけを返す（R-440-03）。
- 版4の宣言のリポジトリの動きは、R-440-02〜R-440-05 で消すもの、変えるもののほかは変わらない。

### R-440-02 canonical モードで拒否するだけのコマンドと引数がない（14章の3、12章）

- コマンド `workspace migrate` と `workbench copy` がない。`spec-dock workspace migrate` と `spec-dock workbench copy` は、知らないコマンドとして引数の誤り（終了コード2）になり、`help` と `completion` と `--help` に出ない。
- 次の引数がない。付けると引数の誤り（終了コード2）になる。
  - `workspace validate --ci`。
  - `workspace sync --source local` と `dependency check --source local`（`--source` が受け付けるのは `github` だけになる。引数なしの動きは今と同じ）。
  - `scope create initiative|epic|issue` と `scope import github initiative|epic|issue` の `--slug`。
- 公開のコマンドの数は 53（`help` と `completion` を含む）になる。Epic の文書の「51」は、epic-00425 が 0.4.0 で `scope check` と `scope render` を足す前の 53 から数えたもので、今の 55 から2つを消すと 53 である（この Issue で Epic の文書の数を直す）。`cli/catalog.py` の `LEAF_PATHS`、`HELP_EFFECTS`、`HELP_PRECONDITIONS`、`MUTATING_LEAF_PATHS`、引数の表と、配布する `spec-dock/docs/cli-redesign-guide.html` のコマンドの一覧が、この53とそろう。
- 使われなくなったエラーのコード `CANONICAL_NOT_APPLICABLE` と `CANONICAL_WORKBENCH_SHARED` を、どのコマンドも返さない。コードと文書から定数と説明を消す。
- `--help` と `help` の各コマンドの説明（効果、前提、読むもの、書くもの、JSON の形）に、版3の説明（`Schema 4:` の区別、`.meta.json`、ローカルの Scope の metadata、`--ci`、入れ子の置き場、slug）がない。canonical モードの今の動きだけを書く。

### R-440-03 `dispatch()` から到達できない従来モードのコードがない（14章の1、AC-20）

- `dispatch()` にモードの振り分けがない。宣言を受け付けた後のコマンドは、`REPOSITORY_INDEPENDENT_HANDLERS`、`installation` のコマンド、宣言を読めないときの `workspace doctor --raw` の3つのほかは、すべて `CANONICAL_HANDLERS` の表を通る。
- パッケージ（`src/spec_dock/`）に、0.5.0 の入口（`spec_dock.cli.main`、`spec_dock.shim_vnext`）から到達できないモジュール、関数、クラス、メソッドがない。到達の判定は `design.md` の方法（import のグラフと、未使用の名前の検出の繰り返し）に従い、判定から外したもの（名前で呼ばれるもの、配布するスクリプト）は `report.md` に理由とともに書く。これには、撤去の前から到達できなかった古いモジュール（`infra/fs_cli.py`、`infra/deps_reader.py`、`domain/deps.py` など）も含む。
- パッケージのコードで `.meta.json` を読み書きするものがない。`.meta.json` の名前が残るのは、canonical モードがカタログや既定のブランチに残った `.meta.json` を異常として見つける検査（`SCOPE_METADATA_PRESENT`、`canonical check`、`branch` と `work start` の基点の検査）だけである。
- 宣言の版3を受け付けるコード（版3を受け付ける定数 `LEGACY_WORKSPACE_SCHEMA`、`legacy` のモード、`workspace_mode`、`ProjectContext.mode`、`probe_workspace_mode` による振り分け）がない。版3を表す名前は、見分けて止めるための1つ（`NOT_MIGRATED_WORKSPACE_SCHEMA`）だけである。
- I-7 から：`infra/commit_tree.py` と `infra/committed_validation.py` の `ls-tree` の解析の重複が1つになる（`committed_validation.py` が到達できなくなって消えるなら、それで満たす）。

### R-440-04 Scope の雛形と名前の規則は canonical の形だけになる（14章の4）

- 配布資産から、`.md` の雛形 `spec-dock/templates/initiative/`、`templates/epic/`、`templates/issue/`（各5ファイル：`requirement.md`、`design.md`、`plan.md`、`report.md`、`.workbench/README.md`）がなくなる。dogfood の写し（spec-dock の `spec-dock/templates/`）も、同じ PR の `installation update` でなくなる。`spec-dock/templates/README.md` は `cue/` の雛形と Artifact の雛形だけを説明する。
- CUE の雛形の `report.md`（`templates/cue/{initiative,epic,issue}/report.md`）の前付けに、`タイトル:` と `親:` の行がない。「詳細:」のリンクは `<区切り>/<ID>/` からの深さ（`../../../docs/…`）である（今の雛形のまま）。
- `scope create` と `scope import github` が写すとき、前付けの行を除く処理と、「詳細:」の相対リンクを書き換える処理がない。作られるファイルのバイトは、0.4.2 の配布資産を持つリポジトリで 0.4.2 が作るものと同じである（雛形から除いた行は、0.4.2 も写すときに除いていたため）。
- 配布資産から、従来モードの入れ子の Scope に `epics/rules.md` と `issues/rules.md` を置くための `spec-dock/docs/rules/initiative/epics.md` と `spec-dock/docs/rules/epic/issues.md` がなくなる。canonical モードの作成は、それらを確かめも参照もしない（`artifacts/rules.md` と `discussions/rules.md` は今のまま）。
- `domain/ids.py` から、Scope の slug の規則（`validate_slug`、`derive_input_slug_from_title`、`resolve_input_title_and_slug`）と、英数字だけの題名の規則（`INPUT_TITLE_RE`、`validate_input_title`）がなくなる。題名の規則は canonical の `validate_canonical_title` だけになる。Artifact の名前の規則（`artifact create --slug` と、それを確かめる `INPUT_SLUG_KEBAB_RE`・`validate_input_slug_kebab`。Artifact の命名。R-J7）は残し、変えない。

### R-440-05 文書に従来モードの記述がない（14章の5）

- README、配布する `spec-dock/docs/`（`guide.md`、`canonical.md`、`migration.md` の版の節でない節（「canonical モードへの移行」「schema3の旧writerから移行」など）、`reference_*.md`、`authoring/`、`rules/`、`cli-redesign-guide.html`、`templates/README.md`、雛形の `.workbench/README.md`）、配布するスキル（`.agents/skills/spec-dock/SKILL.md`、`spec-dock-grill-with-docs`）、spec-dock の `AGENTS.md` に、版3のリポジトリでの動き（「3 のリポジトリでは、今までどおり…」、`.meta.json` の作成、入れ子の置き場、slug、`workspace migrate`、`workbench copy`、`--ci` など）の説明がない。
- 規則の節（Epic の10章。配布するスキルと spec-dock の `AGENTS.md`）は、Epic の10章の撤去の指示のとおり、最初の段落の「3 のリポジトリでは、今までどおり、仕様もコードと一緒にコミットする。」の文を消し、見出しから「（canonical モード）」を外す。規則の節に版3の動きの文を足さない。
- 版3の宣言を見たときの動き（`CANONICAL_NOT_MIGRATED` と、0.4.2 を入れ直して移すこと）は、`migration.md` と `canonical.md` と `reference_cli.md` に書く。
- `migration.md` の過去の版の節（「## 0.4.0 への更新」〜「## 0.4.2 への更新」）は、その版の記録として、版3の動きの文を含めてそのまま残す。版の節でない節のうち、`workspace migrate` だけを説明する「## schema3の旧writerから移行」は消し、「## canonical モードへの移行」は 0.4.2 と版のタグ `v0.4.2` の手順書を案内する形に直す。
- `spec-dock/docs/historical/` は、過去の記録として変えない。

### R-440-06 移行のスクリプトと従来のCIの手順がない（14章の6、I-8 から）

- `scripts/migrate-to-canonical/`（`migrate.py`、`README.md`、`.gitignore`）が、リポジトリから消える。版のタグ `v0.4.2`（と `v0.3.0`）に残る。
- `scripts/static_analysis/run.sh` の `TARGETS` に `scripts/migrate-to-canonical` がない。
- spec-dock の `.github/scripts/specdock-ci-validate.sh` がない（I-10 で `ci.yml` から外され、使われていない）。
- 移行のスクリプトだけを確かめるテスト（`tests/integration/migration/`、`tests/support/migration_repo.py`、`tests/unit/infra/test_migration_contract_copies.py` など）がない。

### R-440-07 共通の契約のテストを失わない（R-J7、14章のテストの扱い）

- 消す前に、今のテストを次の3つに分けた一覧を `report.md` に載せる。
  - (a) 版3だけの振る舞いを確かめるもの。
  - (b) 共通の契約（直接の選択の記録、`StartLock`、Artifact の命名と作成、失敗したら止まる境界、読むだけのコマンドは書かないこと、`OperationResult` の結果の状態と終了コードの規則、配布資産の導入と更新、worktree とブランチの操作）を、版3の作り物（`.meta.json` のある一時のリポジトリ）を使って確かめるもの。
  - (c) モードに関係のないもの。
- (a) は消す。(b) は、同じ契約を canonical モードの作り物（偽の `gh` と一時のカタログ）で確かめる形に書き直す。すでに canonical のテストが同じことを確かめていれば、一覧に対応するテストの名前を書いてから消す。(c) は変えない（消すコードだけを確かめるものは、(a) と同じく消す）。
- 一覧で、(b) のすべてに、対応する canonical のテスト（ファイルとテストの名前）がある。消すかどうかに迷うテストは、一覧に理由を書いて残し、統括に確かめる。
- `make lint` と `uv run pytest`（全体）が通る。

### R-440-08 版は 0.5.0、0.4.2 の配布資産から上がれる（14章の版、R-J8）

- `pyproject.toml`、`uv.lock` の `spec-dock` の版、版のファイル `src/spec_dock/assets/spec_dock/system/spec-dock-version` とその dogfood の写しが `0.5.0` である。`spec-dock --version` は `spec-dock 0.5.0` を示す。
- `migration.md` に「## 0.5.0 への更新」の節がある。0.4.1・0.4.2 の節の形に合わせ、次を書く。
  - 撤去の内容：版3の宣言で、どのコマンドも `CANONICAL_NOT_MIGRATED` で止まること（0.4.2 を入れ直して移すこと）、消えたコマンド（`workspace migrate`、`workbench copy`）と引数（`workspace validate --ci`、`--source local`、`--slug`）、使われなくなったエラーのコード、`.md` の Scope の雛形と `epics.md`・`issues.md` の撤去、CUE の雛形の `report.md` の前付けの2行。
  - #496 と #497 の改善（「背景」の2つ）。すでに使っているリポジトリは、更新の後に `git add spec-dock/templates` で、それまで無視されていた雛形の README を足してコミットすること。
  - 0.5.0 に上げる手順（すべてのリポジトリが版4であることを確かめてから、パッケージを入れ、各リポジトリで `installation update`）。
  - 版3のまま残ったリポジトリの移し方：SpecDock 0.4.2 を入れ直し、版のタグ `v0.4.2` の `scripts/migrate-to-canonical/README.md` に従う。その手順書が「0.3.0」「`v0.3.0`」と書くところ（配布資産と CI の固定の版、撤去の後の戻し方）は、「0.4.2」「`v0.4.2`」と読み替える（タグの中の手順書は変えられないため）。
- `static-inventory.json` で、外した配布資産（`.md` の雛形の15ファイル、`epics.md`、`issues.md`）は `retired` に入り、その `known_old_sha256` に 0.4.2 のバイトの SHA-256 がある。退役してよい場所の許可（`infra/static_assets.py` の `package_retired_assets`。今は `spec-dock/spec-dock.version`、`spec-dock/scripts/spec_dock_runtime/*.py`、`.claude/skills/spec-dock*` の枠だけ）に、この17のパスを、名前を挙げて足す（`spec-dock/templates/{initiative,epic,issue}/` の下と、`docs/rules/` の2つのファイル）。ほかのパスは、今と同じく `retired static inventory contains an unsafe target` で止まる。中身を変えた配布資産は、`files` の `known_old_sha256` に 0.4.2 のバイトの SHA-256 がある。
- 0.4.2 の配布資産を持つ一時のリポジトリ（版4）で、`installation update --backup-dir … --yes` が成功し、変えた資産が 0.5.0 のバイトになり、外した資産が消え（退避される）、`installation show` で既知の古い版も知らない変更も残らない。
- spec-dock の利用側の配布資産（`spec-dock/` の下と `.agents/skills/`）を、この PR の中で、作った 0.5.0 の候補の `installation update` で上げる。

### R-440-09 戻し方は 0.4.2 を入れ直す（統括の依頼の8）

- Epic の `requirement.md`（R-J6 の「0.3.0 と、版のタグ v0.3.0 に残る手順書」、失敗・境界条件の「撤去の後なら、0.3.0 を入れ直してから戻す」と「撤去の後に、移していないリポジトリかクローンが見つかった」）、Epic の `design.md`（12章の `CANONICAL_NOT_MIGRATED` の行、14章の戻し方、「失敗と境界の扱い」の表の「撤去の後に、版3のリポジトリかクローンが見つかった」の行、「移行・互換性・rollback」の組み合わせと戻し方）、Epic の `plan.md`（rollback の I-13）、`migration.md`、`CANONICAL_NOT_MIGRATED` の次の1手が、同じ版（0.4.2 と `v0.4.2`）を示す。移行の間の記述（0.3.0 が両方のモードを扱った、という過去の事実）は変えない。0.4.2 は、両方のモードを持つ最後の版で、CUE の Scope（0.4.0 から）も扱い、版のタグ `v0.4.2` の移行のスクリプトは I-12 で見つかった注意点を含む。0.3.0 は CUE の Scope を扱えないので、0.5.0 から戻す先にしない。

## スコープ

- 変更対象：`src/spec_dock/`（runtime、assets、`static-inventory.json`）、`tests/`、`pyproject.toml`、`uv.lock`、`scripts/`（`migrate-to-canonical/` の削除と `static_analysis/run.sh`）、`.github/scripts/specdock-ci-validate.sh` の削除、`README.md`、`AGENTS.md` の従来モードの記述、dogfood の写し（`spec-dock/` の下と `.agents/skills/`。`installation update` で）、Epic とこの Issue の Scope のディレクトリ（カタログの中。Git では扱わない）。
- 対象外：
  - 0.5.0 を利用者の環境に入れること、ほかの4つのリポジトリの `installation update`、`release-tag.yml` のタグの確かめ（マージの後に統括が行う。AC-20 の残り）。
  - `spec-dock work finish`（マージの後に統括が行う）。
  - `scripts/migrate-to-canonical/.state/`（Git の外。main のチェックアウトにだけある）。
  - Artifact の命名（`artifact create --slug` を含む）、`workspace doctor --legacy`（撤去済みの v1 の記録のファイルの観測。モードの撤去とは別のもの）、直接の選択の記録、`StartLock`、`OperationResult` の規則（R-J7。変えない）。
  - HTML のダッシュボード（epic-00427）と、Markdown と PlantUML のダッシュボード（13章。canonical モードのまま残す）。
- 親の契約として守る境界：C2 は版4だけの判定に変える（Epic の契約の表）。C1、C3〜C11 の形は変えない。

## 失敗・境界条件

- 版3の宣言を持つ worktree が、版4の宣言を持つクローンの中にあっても、その worktree のコマンドは版3として止まる（宣言は worktree ごとに読む）。
- 版3の宣言でも、`--project` の誤り、Git の外、`UNSUPPORTED_PLATFORM` は、今と同じコードで先に止まる（宣言を読む前の確かめ）。
- `installation init` の宛先に版3の宣言があるときは、`CANONICAL_NOT_MIGRATED` で止まり、何も置かない。宣言がない宛先は今と同じ。
- 0.4.2 の配布資産を 0.5.0 に上げる前に、0.5.0 のパッケージで `scope create` を行うと、雛形の `report.md` の前付けに `タイトル:` と `親:` の行が残る（雛形の内容のまま。正本ではない）。`installation update` で 0.5.0 の雛形になる。`cue/` の雛形がないときは今と同じく `SCOPE_TEMPLATES_OUTDATED` で止まる。
- 0.4.2 の配布資産の `docs/rules/initiative/epics.md` と `docs/rules/epic/issues.md` は、利用者が変えていなければ `installation update` で消える（退避される）。変えていれば、今の規則どおり手で合わせるよう止まる。
- 撤去の前に版3の宣言で動いていた作業（版3の worktree、移行前のブランチ）は、0.5.0 では読めない。必要なら 0.4.2 を入れ直す（R-440-09）。

## 受け入れ条件

- AC-440-01（R-440-01）：版3の宣言の一時のリポジトリで、R-440-01 の50のコマンドのそれぞれが、終了コード3、`CANONICAL_NOT_MIGRATED`、`effects` が空、リポジトリのファイルが変わらないことを、1つのテストで確かめる。`canonical check` は失敗の1件で同じ次の1手を返す。版5の宣言は `PRECONDITION_FAILED` のまま。
- AC-440-02（R-440-02）：`LEAF_PATHS` が53で、`workspace migrate` と `workbench copy` がない。G7 のテストが、版4の53のコマンドのうち `help` と `completion` と `installation` の4つを除くすべてが `CANONICAL_HANDLERS` か `REPOSITORY_INDEPENDENT_HANDLERS` の canonical の処理で動き、`CANONICAL_NOT_IMPLEMENTED`、`CANONICAL_NOT_APPLICABLE`、`CANONICAL_WORKBENCH_SHARED`、`BUSINESS_NOT_CONNECTED` を返さないことを確かめる。消した引数が引数の誤りになる。
- AC-440-03（R-440-03）：`report.md` に、到達の判定の結果（消したモジュールの一覧、残した名前とその理由）と、コードの検索（`.meta.json`、`schema_version` の 3、`LEGACY_WORKSPACE_SCHEMA`、`workspace migrate`、`workbench copy`、`CANONICAL_NOT_APPLICABLE`、`CANONICAL_WORKBENCH_SHARED`、`--slug` の scope の引数、`--source local`、`--ci`）の結果がある。残った `.meta.json` は canonical の検査だけである。
- AC-440-04（R-440-04）：雛形の3つのディレクトリ（15ファイル）と `epics.md`・`issues.md` が配布資産と dogfood の写しにない。CUE の雛形の `report.md` に `タイトル:` と `親:` がない。canonical の `scope create` で作った `report.md` のバイトが、テストの見本（変更の前と同じ）と一致する。`domain/ids.py` に Scope の slug と英数字の題名の規則がなく、不正な Artifact の `--slug` が今と同じく止まる（テストを足す）。
- AC-440-05（R-440-05）：文書の中身のテストが、従来モードの記述がないこと（版3の動きの文、`workspace migrate`、`workbench copy`、`--ci`、`.meta.json` の作成）と、`CANONICAL_NOT_MIGRATED` と 0.4.2 の案内があることを確かめる。
- AC-440-06（R-440-06）：`scripts/migrate-to-canonical/` と `.github/scripts/specdock-ci-validate.sh` がなく、`run.sh` の `TARGETS` にない。
- AC-440-07（R-440-07）：`report.md` のテストの分類の一覧で、(b) のすべてに対応する canonical のテストがある。`make lint` と `uv run pytest` が通る。
- AC-440-08（R-440-08）：版が 0.5.0 にそろう。0.4.2 の配布資産を持つリポジトリが `installation update` で 0.5.0 に上がるテストが通る。`migration.md` の「0.5.0 への更新」の節に、撤去の内容、#496、#497 がある。spec-dock の dogfood の配布資産が 0.5.0 の候補と同じバイトである。
- AC-440-09（R-440-08）：wheel を作り、一時の venv に入れて、`spec-dock --version` が 0.5.0、`spec-dock help` と `spec-dock canonical --help` が動き、`spec-dock workspace migrate` と `spec-dock workbench copy` がない（引数の誤り）。結果を `report.md` に書く。
- AC-440-10（R-440-09）：Epic の `requirement.md`、`design.md`、`plan.md`、`migration.md`、`CANONICAL_NOT_MIGRATED` の次の1手が、撤去の後の戻し先と移し方として 0.4.2 と `v0.4.2` を示し、0.3.0 を示さない。
- AC-20 のうち、パッケージについての部分（Epic の I-13 の受け入れ）は、AC-440-01〜AC-440-09 で満たす。各リポジトリの配布資産の PR と、検査のワークフローの 0.5.0 での通過は、マージの後に統括が確かめる。

## 制約・前提

- 前提：R-J1 の5つのリポジトリは、すべて版4である（I-12 の報告書）。利用者は戻す必要がないことを確かめた（2026-11-02）。
- 共通の契約（R-J7）のテストを、対応を示さずに消さない（Epic の I-13 の注意）。
- 消すものは、`dispatch()` から到達できるかで決める。ファイルの一覧を正本にしない（14章）。
- 仕様は Git で扱わない（canonical モード）。この Issue の文書と Epic の文書は、カタログの中のファイルとして直す。
- `canonical remove`、`installation uninstall`、`scope delete`、`worktree remove` を実行しない。利用者の環境（`~/.claude/settings.json`、`~/.codex/config.toml`、`~/.agents/`、`~/.local/state/spec-dock/`、uv の tool の環境）とほかのリポジトリを変えない。
- テストは外のネットワークを使わない（偽の `gh`、一時の bare のリポジトリ、一時の `XDG_STATE_HOME`）。
- 人が PR をマージする。`--no-verify`、強制 push、履歴の書き換え、`main` への直接の push、タグの作成をしない。
