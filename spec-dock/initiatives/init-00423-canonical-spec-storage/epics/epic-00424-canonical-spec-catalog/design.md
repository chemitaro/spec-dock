---
種別: 設計書（Epic）
ID: "epic-00424"
タイトル: "Centralize Specs On Canonical Branch And GitHub Issues"
関連GitHub: ["#424"]
状態: "approved"
最終更新: "2026-10-26"
依存: ["requirement.md"]
親: ["init-00423"]
---

# epic-00424 Centralize Specs On Canonical Branch And GitHub Issues — 設計

詳細: [Design Guide](../../../../docs/authoring/design.md)

表示名：仕様の正本を `spec-dock/canonical` ブランチと GitHub Issue に集約する

## この文書の読み方

この設計書は、この Epic の議論に参加していない実装担当のエージェントが、ほかの資料や会話を見なくても、迷わずに実装できるように書いている。

- **何を満たすか**は、同じディレクトリの `requirement.md` が正本である。要件の番号（R-A1 など）と受け入れ条件の番号（AC-01 など）は、`requirement.md` と同じものを使う。この設計書は、要件を言い換えず、実現の方法と契約を決める。
- **根拠の事実**は、Artifact `artifacts/20261025t080353z-research-verified-git-github-behaviors.md`（以下「調査の記録」）にある。この設計書で「確認済み」と書いたものは、そこに再現の条件がある。
- **Issue の分け方と順序**は、同じディレクトリの `plan.md` にある。各 Issue は、この設計書の章を担当範囲として受け取る。
- 迷ったときは、要件の「使いやすさの約束」（requirement.md の背景の章）に従う。約束は次の5つである。
  1. 仕様はいつもの場所にある。
  2. 用意はコマンド1つ。
  3. 自動で動くのは定期の同期だけ。
  4. ツールの設定を書き換えない。
  5. おかしいときは止まり、次の1手を示す。
- この設計書の「しなければならない」「してはならない」は必須の契約である。「よい」「推奨」は実装者の判断に任せる。
- 実装の前に、リポジトリの `AGENTS.md`（提供側と利用側の区別、層の構成、テストの置き場）と、`.agents/skills/spec-dock/SKILL.md` を読むこと。
- 2026-10-25 に、この会話を知らない別のエージェントが、この設計書を実装担当の立場で読み直した。その指摘（コマンドの抜け、`work finish` の確認の条件、移行時の無視されたファイル、書き換えの検出の穴、フック、出力の契約、GitHub の呼び出し、状態のファイルの置き場など）は、この版に反映してある。
- 同じ日に、利用者の判断を受けて、次を足した。GitHub の構造を一括で取得して使い回す「構造のスナップショット」（2章）、今までの形のダッシュボードの作り直し（13章）、Linux の systemd のない環境（コンテナ）での定期の実行と、マウントしたチェックアウトでの止まり方（3章、5章）。
- さらに同じ日に、利用者が、2つのモードを長く並べて維持せず、利用者の5つのリポジトリをすべて移し、従来モードのコードをこの Epic の中で撤去すると決めた（R-J1〜R-J8）。そのため、従来モードは「移行の間だけ」のものになり、14章（撤去）と、「移行・互換性・rollback」の章の全リポジトリの移行を足した。1〜13章の canonical モードの中身は変わらない。

### 用語

| 用語 | 意味 |
|---|---|
| mainのチェックアウト | リポジトリを最初にクローンした場所（Git の main worktree）。main ブランチのことではない。退去費用プロダクトでは `develop` をチェックアウトしている |
| 作業用のworktree | `git worktree add`、Orca、Codex、SpecDock の `worktree create` などで作った、mainのチェックアウト以外のチェックアウト |
| canonical | GitHub と手元にある、仕様の内容の正本のブランチ `spec-dock/canonical`。既定のブランチと共通の祖先を持たない |
| カタログ | クローンごとに1つ、mainのチェックアウトの `spec-dock/.canonical/` に置く、canonical のworktree |
| リンク | 各チェックアウトの `spec-dock/initiatives`。カタログを直接指すシンボリックリンク |
| 構造 | Scope の番号、種類、親子、依存、状態、題名。正本は GitHub Issue |
| 内容 | 要件、設計、計画、報告、Artifact などのファイル。正本は canonical |
| 宣言の版 | `spec-dock/workspace.json` の `schema_version`。3 は今の形（従来モード）、4 は新しい形（canonical モード） |
| 従来モード | 宣言の版が3のリポジトリでの動き。移行の間だけ、今のコードをそのまま使う（R-A6）。撤去で消す |
| canonical モード | 宣言の版が4のリポジトリでの動き。この設計書の対象 |
| 移行の間 | SpecDock 0.3.0 を入れてから、撤去した 0.4.0 を入れるまで。0.3.0 は2つのモードを扱う |
| 撤去 | R-J1 のすべてのリポジトリを移した後に、従来モードのコードを消し、0.4.0 を出すこと（14章） |
| 定期の同期 | PCのユーザーごとに1つの定期の実行が、60秒ごとに `spec-dock canonical sync --registered` の1周期を動かすこと。実行の仕組みは、macOS は launchd、systemd の動く Linux は systemd のユーザーのタイマー、systemd のない Linux（コンテナなど）は常駐のプロセス |
| 常駐のプロセス | systemd のない Linux で使う、`spec-dock canonical sync --registered --loop` のプロセス。1つの環境に1つだけ動き、60秒ごとに1周期を動かす |
| 状態の置き場 | PCのユーザーごとの `~/.local/state/spec-dock/`。登録簿、カタログごとの同期の状態、構造のスナップショット、ログを置く。カタログが読めないときでも記録できるよう、カタログの外に置く |
| 構造のスナップショット | GitHub のリポジトリごとに、Scope の Issue の構造を一括で取得して保存した1つのファイル（2章）。読むコマンドとダッシュボードは、ここから読む |
| 変わったかの確かめ | 構造のスナップショットを取り直す必要があるかを、GitHub の条件付きの要求（304 なら変化なし）で確かめること。主のレート制限を消費しない |
| ダッシュボード | mainのチェックアウトの `spec-dock/dashboard.md` と4つの PlantUML のファイル。定期の同期が、構造のスナップショットから作り直す（13章） |
| 登録簿 | このPCで定期の同期の対象にするカタログの一覧。状態の置き場にある |
| 変更の束 | SpecDock のコマンドがカタログに書いた変更の一覧。定期の同期が、30秒を待たずに1つのコミットとして保存する |
| 保留 | 定期の同期が、自動では保存しないと判断した変更（大量の削除、秘密情報らしいもの、大きすぎるファイル） |
| 別名ファイル | 同じファイルの競合で、後から push する側の版を保存するファイル（名前の規則は5章） |
| 基準 | 定期の同期が最後に確かめた GitHub の canonical のコミット（`last_seen_remote`）。書き換えの検出に使う |

## 設計目標

- **G1 1か所の正本**：内容は canonical、構造は GitHub Issue だけに置く。既定のブランチと、そこへ入るPRには、仕様を置かない（R-A1〜R-A4）。
- **G2 いつもの場所で、普通のファイルとして**：どのチェックアウトでも、仕様は `spec-dock/initiatives/` に見える。人とエージェントは、仕様のために Git を操作しない（約束1）。
- **G3 用意は1つ**：`spec-dock canonical link` が、カタログ、保護、除外、リンク、定期の同期の登録をまとめて行う。何度実行しても同じ結果になる（約束2、R-B3）。
- **G4 保存の経路は1本**：保存、取り込み、push は、定期の同期だけが行う。SpecDock のほかのコマンドはコミットしない（約束3、R-C1、R-D1）。
- **G5 止まって案内する**：足りないものや異常があれば、推測で直さず、次に実行するコマンドか、足す設定を示して止まる（約束5、R-B5、R-H2）。
- **G6 移行の間、移行していないリポジトリを壊さない**：移行の間、宣言の版が3のリポジトリでは、0.3.0 でも今の動きをそのまま保つ（R-A6）。
- **G7 すべてのコマンドが答える**：canonical モードで、今の44のコマンドと新しいコマンドのすべてが、canonical の処理か、理由と次の1手を付けた拒否のどちらかで動く。未実装のまま出してはならない。拒否するだけのものは、撤去で消す（14章）。
- **G8 GitHub に負荷をかけない**：構造は一括で取得して使い回し、操作のたびに問い合わせない。変化の確かめは主のレート制限を消費しない条件付きの要求で行い、要求は1つずつ順に送る（R-I1〜R-I6）。
- **G9 macOS と Linux で同じに動く**：定期の実行の仕組みだけを環境に合わせて選び、ほかの動きは同じにする（R-C7、R-C8）。
- **G10 最後は1つの仕組みだけ**：R-J1 のすべてのリポジトリを移したら、従来モードのコードを撤去し、canonical モードだけを持つ 0.4.0 にする。撤去で、共通の契約とそのテストを失わない（R-J6、R-J7）。

## Current / Target

### Current（2026-10-25、`origin/main` の時点のコード）

- 仕様のツリー `spec-dock/initiatives/` を、既定のブランチとすべての作業ブランチが追跡している。
- 構造は、各 Scope のディレクトリの `.meta.json`（schema 3）にある。必須のキーは `schema_version`、`type`、`id`、`title`、`slug`、`parent_id`、`initiative_id`、`epic_id`、`depends_on`、`backend`、`github`、`lifecycle`、`revision`（`src/spec_dock/runtime/domain/writer_admission.py:22-39`）。
- 木の読み込みは `src/spec_dock/runtime/infra/scope_tree.py` の `load_scope_tree` が行い、`application/scope_query.py` の `load_scope_views` がそれを包む。リンクの `spec-dock/initiatives` は拒否する（`scope_tree.py:53-57`、`scope_query.py:51,60-62`）。単一の対象では `git ls-files` を使う。多くのコマンド（`active`、`branch`、`artifact`、`worktree`、`workbench` を含む）が `load_scope_views` を通る。
- `.meta.json` を書くのは、`infra/scope_metadata.py`（新規）と、`application/direct_scope_edit.py`、`direct_scope_lifecycle.py`、`direct_finish.py`、`direct_dependencies.py`、`direct_scope_delete.py`（置き換え）である。
- GitHub は `infra/github_lifecycle.py` の `GithubIssueGateway` が、`gh api --hostname github.com --include --method M <endpoint> [--input -]` で扱う。操作は取得、作成（題名と本文だけ）、状態の変更だけで、再試行はない。メソッドは GET、POST、PATCH だけ、送る本文は文字列だけの辞書で、404 は権限なし（`GITHUB_ACCESS_DENIED`）に分類する（`github_lifecycle.py:38-57,107-115`）。
- `work start` は、基点のコミットのツリーから `.meta.json` を読む（`application/start_snapshot.py:92-144`）。排他 `StartLock`（`infra/start_lock.py`）は、Git の共通ディレクトリを開いて `flock` をかける。
- `spec-dock/active/` のリンクは `infra/active_links.py` が書き、先を `spec-dock/` からの相対パスで求める。
- コマンドはすべて `commands/runtime_dispatch.py` の `dispatch()` を通り、57行目付近の `resolve_context` でリポジトリを解決する。コマンドの一覧は `cli/catalog.py` の `LEAF_PATHS`（44個。テスト `test_issue413_contract.py:160`、`test_cli_vnext_contract.py:64`、`test_cli_docs_vnext.py:35` が数を確かめている）。
- 結果は `presentation/envelope.py` の `OperationResult` で返す。`failed` は適用済みの効果を持てず（`succeeded` か `unknown` の効果があると例外）、`partial` は終了コード6（適用済みか不明の効果が要る）か7でなければならない（`envelope.py:69-95`）。
- 宣言 `spec-dock/workspace.json` は `{"schema_version":3,"writer_protocol":"specdock.worktree-writer/v1"}`。`application/project_context.py` の `read_workspace_declaration` は、版が整数の3でなければ `ValueError` を出し、`PRECONDITION_FAILED`（終了コード3）になる。
- CI の「CI」（`.github/workflows/ci.yml`）は、`.github/scripts/specdock-ci-validate.sh` でソースから wheel を作り、`spec-dock workspace validate --ci --json` を実行する。
- 配布は wheel だけ。`pyproject.toml` の版は 0.2.4 で、版のタグはない。
- `spec-dock/dashboard.md` と4つの PlantUML のファイルを生成するコマンドはない。書く部品は、コミット `ae6c94369`（2026-10-01）で削除された。描く関数（`presentation/markdown.py` の `_render_dashboard_md`、`presentation/puml.py` の `_render_tree_ready_board_puml`、`_render_deps_issues_puml`、`_render_deps_raw_puml`）は残っているが、どこからも呼ばれず、テストもない。spec-dock のmainのチェックアウトにある5つのファイルは、2026-09-21 に作られたもの（今までの形の見本）で、配布資産の `spec-dock/.gitignore` で無視されている。
- 構造は、コマンドのたびに `.meta.json` と GitHub から読み、保存して使い回すことはしない。
- 提供側のCI（`.github/workflows/provider-ci.yml`）は、`make lint` と `uv run pytest` を `ubuntu-latest` で、配布の確かめを `ubuntu-latest` と `macos-latest` で動かしている。
- spec-dock のmainのチェックアウトの `spec-dock/initiatives/` には、Git で無視された `.workbench` のファイルが99個ある（2026-10-25）。これらは追跡されていないので、canonical には入らない。

#### 利用者のリポジトリ（R-J1。2026-10-25 に、読むだけで調べた）

| リポジトリ | mainのチェックアウト | 既定のブランチ | Scope | 作業用のworktree | 今のCIの SpecDock の手順 |
|---|---|---|---|---|---|
| spec-dock | `/Volumes/990p2t/workspace/tools/spec-dock` | `main` | 243（Initiative 3、Epic 24、Issue 216。依存135） | 5 | `ci.yml` が `.github/scripts/specdock-ci-validate.sh` で、ソースの wheel の `workspace validate --ci` を実行する |
| taikyohiyou_project（退去費用プロダクト） | `/Volumes/990p2t/workspace/product/taikyohiyou_project` | `develop` | 246（4、44、198。依存284） | 0 | `ci.yml` が `pip install 'git+…/spec-dock.git@0e7dc868…'` の後に `workspace validate --ci --json` |
| housing-lifecycle | `/Volumes/990p2t/workspace/company-os/businesses/housing-lifecycle` | `main` | 233（16、36、181。依存56） | 15（`/Volumes/990p2t/workspace/worktrees/orca/housing-lifecycle/` の下） | `ci.yml` が `pip install 'git+…/spec-dock@4d25a8b4…'`、`spec-dock --version`、`workspace validate --ci --json` |
| input-devices | `/Volumes/990p2t/workspace/company-os/businesses/input-devices` | `main` | 17（1、3、13。依存13） | 1（`/private/tmp` の下で、Git は prunable と示す） | `ci.yml` の1つの手順が `uvx --from git+…/spec-dock@4d25a8b4… spec-dock workspace validate --ci --json` |
| company-os | `/Volumes/990p2t/workspace/company-os` | `main` | 0（`spec-dock/initiatives/` は空） | 2 | `ci.yml` が `uv tool install git+…/spec-dock@4d25a8b4…` の後に `workspace validate --json` と `workspace doctor --json` |

- どの Scope も `backend` は GitHub である。ローカルの ID は、spec-dock の `init-local-00002` と `init-local-00003` だけである。
- 調べた時点で、作業用のworktreeのブランチに、既定のブランチにない仕様の変更（コミット済みも未コミットも）はなかった（この Epic のブランチを除く）。切り替えの時点で、もう一度調べる。
- housing-lifecycle と input-devices は、company-os の作業ツリーの中にある別のリポジトリである。company-os は `.gitignore` の `/businesses/*` で両方を無視している。それぞれが自分の `.git` を持つので、カタログもそれぞれの mainのチェックアウトの中にでき、互いに重ならない。
- spec-dock には、別のクローン `/Volumes/990p2t/workspace/worktrees/specdock-cleanup-planning`（ブランチ `iss-00411-retired-cli-surface-cleanup`、宣言の `writer_protocol` が古い `specdock.writer/v1`）がある。利用者は、これを放棄すると決めた（2026-10-26）。移さず、`canonical link` も実行しない。撤去の後にこのクローンで SpecDock を使うと、0.4.0 は版3の宣言を読んで止まる。
- taikyohiyou_project の `.github/scripts/resolve_staging_route.py`（67行目）は、`spec-dock/` で始まるパスを特別に扱う。`Makefile` の `spec-close` は `spec-dock work finish @current --yes --json` を呼ぶ。どちらも、切り替えの後に動きが変わらないかを I-12 で確かめる。

### Target

```text
GitHub
  Issue（構造の正本）           番号・種類のラベル・sub-issue（親子）・blocked by（依存）・状態・題名・本文の slug の印
  spec-dock/canonical（内容）    仕様のツリーだけ。既定のブランチと共通の祖先を持たない
  既定のブランチ（コード）        仕様のパスを1つも持たない

PC（クローンごと）
  <main>/                                 mainのチェックアウト
    spec-dock/
      workspace.json                      {"schema_version": 4, ...}
      .gitignore                          /.canonical/ と /initiatives と !/initiatives/ を含む
      .canonical/                         カタログ（canonical のworktree、lock 済み）
        .spec-dock-canonical.json         {"format": 1}
        .gitignore  README.md
        .runtime/                         変更の束、作成の作業場所、一時のインデックス、保留の許可（canonical でも無視）
        init-00079-…/epics/…/issues/…     仕様の内容
      initiatives -> .canonical           リンク（相対）
      dashboard.md  tree.puml  tree-all.puml  deps-issues.puml  deps-raw.puml
                                          ダッシュボード（定期の同期が作り直す。Git では無視）
  <作業用のworktree>/
    spec-dock/initiatives -> <main>/spec-dock/.canonical   リンク（絶対パス）

PCのユーザーごと（状態の置き場 ~/.local/state/spec-dock/）
  canonical-registry.json                 登録簿
  catalogs/<鍵>/state.json                カタログごとの同期の状態
  github/github.com/<owner>/<repo>/
    snapshot.json                         構造のスナップショット（リポジトリごとに1つ）
    probe.json                            変わったかの確かめの記録（ETag）
  runner.lock  runner.json  kick          常駐のプロセスの排他、記録、すぐの実行の合図（systemd のない Linux）
  canonical-sync.log                      ログ
  ~/Library/LaunchAgents/io.github.chemitaro.spec-dock.canonical-sync.plist   （macOS）
  ~/.config/systemd/user/spec-dock-canonical-sync.{service,timer}            （systemd の動く Linux）
```

- canonical モードでは、構造を構造のスナップショットから読み（書く判断の前には GitHub で確かめる）、内容をカタログのファイルから読む。`.meta.json` は読みも書きもしない。
- 移行の間（0.3.0）は、従来モードのコードを残し、変えない。どちらのモードで動くかは、宣言の版だけで決める。
- 撤去の後（0.4.0）は、canonical モードだけが残る。宣言は版4だけを受け付け、版3を読むと移行の方法を示して止まる（14章）。

## 責務・Interface

### 1. モードの判定（R-A5、R-A6）

- `read_workspace_declaration` は、版 3 と 4 を受け付けるように変える。宣言は今までどおり辞書で返し（従来の呼び出し元の `start_snapshot.py` と `direct_validation.py` を変えないため）、モード（`legacy` か `canonical`）は `workspace_mode(宣言)` と `ProjectContext.mode` で求める。それ以外の版は、今と同じく `PRECONDITION_FAILED` で止める。書き込みの許可（`require_writer`）は、どちらの版でも `writer_protocol` が `specdock.worktree-writer/v1` であることを求める。
- `dispatch()` は、モードに応じて従来の処理か canonical の処理を呼ぶ。従来の処理の関数と、その下の `.meta.json` の読み書きは変えてはならない。canonical の処理は、新しいモジュールに置く（「変更対象」の章）。振り分けは `dispatch()` の1か所に集める。
- `canonical` グループのコマンドは、宣言の版が3のリポジトリでは `CANONICAL_NOT_MIGRATED`（終了コード3）で止まり、「このリポジトリは移行していない」と示す。ただし `canonical check` は例外で、版3の宣言を失敗の1件として返す（8章）。
- `workspace migrate`（宣言の `writer_protocol` を切り替える今のコマンド）は、版4では `CANONICAL_NOT_APPLICABLE` で止まる。版4の宣言を版3に書き換えてはならない。
- **リポジトリによらないコマンド**：`canonical sync --registered` は、登録簿のカタログを順に処理するので、リポジトリの外（launchd の作業ディレクトリはホーム）から動く。`dispatch()` の `resolve_context` より前に振り分ける。そのために、I-1 が `resolve_context` より前に呼ぶ表 `REPOSITORY_INDEPENDENT_HANDLERS`（名前空間と作業ディレクトリを受け取り、宣言を自分で調べるコマンドも登録できる）を作り、C2 の公開の形とする。`canonical sync --registered`（I-3）と `canonical check`（I-7）は、この表に登録する。
- 移行前の版の SpecDock（0.2.4）は、版4の宣言を読むと止まる（今のコードの動き）。これで R-A5 の前半を満たす。
- canonical のルートの `.spec-dock-canonical.json` の `format` が、この SpecDock が知る版（1）より大きいとき、カタログに書くすべてのコマンドと定期の同期は、書く前に止まる（R-A5 の後半。`CANONICAL_FORMAT_UNSUPPORTED`、次の1手は「SpecDock を更新する」）。
- この章のモードの振り分けは、移行の間（0.3.0）だけのものである。撤去（14章）で、`read_workspace_declaration` は版4だけを受け付けるようになり、`dispatch()` の振り分けと従来の処理は消える。

### 2. GitHub の構造（R-A2、R-A3、R-E1〜R-E4）

#### 表し方

| 構造 | GitHub での表し方 |
|---|---|
| Scope であること・種類 | ラベル `spec-dock:initiative`、`spec-dock:epic`、`spec-dock:issue` のちょうど1つ。PRは Scope にならない |
| 番号・ID | Issue の番号。ID は `init-`、`epic-`、`iss-` に、5桁にそろえた番号を付けたもの（今の `domain/ids.py` の `format_id`） |
| 識別名（slug） | 本文の、`<!-- spec-dock:slug=<slug> -->` だけの行。作成のときに本文の末尾に置き、以後は変えない |
| 題名 | Issue の題名。いつでも変えてよい |
| 親子 | sub-issue。Initiative には親がない。Epic の親は Initiative、Issue の親は Epic |
| 依存 | blocked by |
| 状態 | open / closed と `state_reason`（今と同じ解釈） |
| 作業中の印 | `work start` で付け、`work finish` で外すラベル `spec-dock:in-progress` と、足すだけの担当者 |

- **印の読み方**：本文を `\r?\n` で行に分け、行末の空白を除いた行が `^<!-- spec-dock:slug=(.*) -->$` に合うものを数える。本文のどこにあってもよいが、ちょうど1つでなければならない。0個なら `SLUG_MARKER_MISSING`、2個以上なら `SLUG_MARKER_MULTIPLE`（正しい印と規則外の印が1つずつのときも含む）、1個で slug が規則（`^[a-z0-9]+(?:-[a-z0-9]+)*$`）に合わなければ `SLUG_MARKER_INVALID` の異常とする。I-8 の移行のスクリプトは、この規則を写す。GitHub の画面で本文を編集すると改行が `\r\n` になることがあるため、こう読む。
- **ラベル**：ないときは、作る側のコマンド（`scope create`、`scope import`、`work start`、移行のスクリプト）が作る。色と説明は固定の値を使う。
- Scope でない Issue への blocked by は、着手の判定では「その Issue が開いていれば着手できない」と扱う。`workspace validate` は警告を出す。

#### 使う API（調査の記録で、公式の文書と実測で確かめた）

全体の読み取りは GraphQL、変わったかの確かめ、書き込み、書く前の読み直しは REST を使う。全体の読み取りの結果は、構造のスナップショット（この章の後半）に保存して使い回す。

- **全体を読む（GraphQL）**：3つの種類のラベルをまとめて指定した、次の問い合わせを、`pageInfo.hasNextPage` が偽になるまで行う。`labels` に複数のラベルを渡すと、どれかを持つ Issue が返る（OR。2026-10-25 に確認。空の配列は0件を返すので渡さない）。`parent`、`subIssues`、`blockedBy`、`databaseId` は、この token で読めることを確かめた。

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

  `subIssues.totalCount` か `blockedBy.totalCount` が100を超える Issue だけ、REST の一覧で残りを読む。`labels.totalCount` が20を超える Issue だけ、REST の `GET …/issues/{n}/labels?per_page=100` でラベルを読み直す（種類のラベルを見落とさないため）。どの読み直しも、1つずつ順に送る。spec-dock の規模（Scope 243件）では3回の呼び出しで済む。`rateLimit.cost` はログに残す。
  - 依存先（`blockedBy` の要素）のラベルは読まない。依存先が Scope かどうかは、その番号が `issues` に含まれるかで決める（`issues` は閉じた Scope も含む）。2026-10-26 に本物の GitHub で読むだけで測ると、依存先のラベルを読む形は1ページ104点、読まない形は4点だった（I-1 の実装担当の測定）。
  - `parent`、`subIssues`、`blockedBy` の要素は `repository { nameWithOwner }` を持つ。別のリポジトリの Issue は、番号だけでは同じリポジトリの Issue と取り違えるため、`parent`、`sub_issues`、`blocked_by`、`blocking`、`external` のどれにも入れず、`anomalies` に `PARENT_FOREIGN_REPOSITORY`、`SUB_ISSUE_FOREIGN_REPOSITORY`、`DEPENDENCY_FOREIGN_REPOSITORY`（相手のリポジトリと番号をメッセージに入れる）として記録する。`SUB_ISSUE_FOREIGN_REPOSITORY` は、子が別のリポジトリにあることを親の側に記録するもので、完了の判定（子孫が完了しているか）で別のリポジトリの子を見落とさないために置く（I-1 で追加）。
- **変わったかを確かめる（REST の条件付きの要求）**：種類のラベルごとに、次の要求を、前に記録した `ETag` を `If-None-Match` に付けて送る（3回）。

  ```text
  GET /repos/{o}/{r}/issues?labels=<種類のラベル>&state=all&sort=updated&direction=desc&per_page=1
  ```

  - 一覧の先頭は、そのラベルの Issue のうち最も最近に更新されたものなので、どれかが更新されると応答が変わる。304 なら変化なし、200 なら変化あり。
  - 304 は、主のレート制限に数えられない（2026-10-25 に、3回続けて送っても `x-ratelimit-used` が増えないことを確かめた。公式の文書にも同じ記述がある）。
  - `gh api --include` は、304 で終了コード1を返し、状態行 `HTTP/2.0 304 Not Modified` を出す（確認済み）。304 は、終了コードではなく状態行で判定しなければならない。
- **一部を読む（REST）**：書く前の読み直しと、全体の読み取りで足りない部分にだけ使う。

| 操作 | API |
|---|---|
| Issue の取得 | `GET /repos/{o}/{r}/issues/{n}` |
| 親の取得 | `GET …/issues/{n}/parent`（親がなければ404。404 は「親なし」という正常な答えである） |
| 子の一覧 | `GET …/issues/{n}/sub_issues?per_page=100` |
| 依存の一覧 | `GET …/issues/{n}/dependencies/blocked_by?per_page=100` |
| ラベルの一覧 | `GET …/issues/{n}/labels?per_page=100`（全体の読み取りでラベルが20を超えた Issue だけ） |
| ラベルの有無 | `GET /repos/{o}/{r}/labels/{name}`（なければ404。正常な答え） |
| 自分のログイン名 | `GET /user` |

- **書く（REST）**：

| 操作 | API |
|---|---|
| Issue の作成 | `POST /repos/{o}/{r}/issues`（`title`、`body`、`labels` の配列） |
| 題名、本文、状態の変更 | `PATCH …/issues/{n}`（`title`、`body`、`state`、`state_reason`）。本文を変えるのは、`scope import github` が既にある Issue に slug の印を足すときだけである。I-1 の `GithubStructureClient.update_issue` は本文を受け取らないので、最初に使う I-5 が `body` を足す（C1 の追加） |
| 親子を付ける、付け替える | `POST …/issues/{親}/sub_issues`（本文 `{"sub_issue_id": <子の id>, "replace_parent": true/false}`） |
| 親子を外す | `DELETE …/issues/{親}/sub_issue`（本文 `{"sub_issue_id": <子の id>}`） |
| 依存の追加、削除 | `POST …/issues/{n}/dependencies/blocked_by`（本文 `{"issue_id": <依存先の id>}`）、`DELETE …/dependencies/blocked_by/{依存先の id}` |
| ラベル | `POST /repos/{o}/{r}/labels`（ラベル自体の作成）、`POST …/issues/{n}/labels`（`{"labels": [...]}`）、`DELETE …/issues/{n}/labels/{name}` |
| 担当者 | `POST …/issues/{n}/assignees`（`{"assignees": [login]}`） |

- `sub_issue_id` と `issue_id` は、Issue の番号ではなく、Issue の `id`（REST の `id`、GraphQL の `databaseId`。数値）である。取り違えないこと。
- **呼び出しの部品**：`infra/github_structure.py` に、新しい呼び出しの関数を作る。`gh api` の呼び出し方（`--hostname github.com --include`、標準入力からの本文）は今の `GithubIssueGateway` と同じにするが、次の点を今の分類に頼らずに扱う。
  - メソッドは GET、POST、PATCH、DELETE。本文は、数値と配列を含む JSON を送れる。
  - エンドポイントごとに「正常な状態コード」を渡す（例：親の取得は 200 と 404）。それ以外を、今と同じ分類（権限なし、拒否、接続不可）にする。
  - **レート制限**：403 か 429 で、`retry-after` ヘッダー、`x-ratelimit-remaining: 0`、または本文の「rate limit」があれば、レート制限と判定する。読み取りは、要る待ち（`retry-after`、なければ `x-ratelimit-reset` までの時間）が60秒以下なら、その間だけ待って、3回まで再試行する。60秒を超えるときは、待たずに `GITHUB_RATE_LIMITED`（再開できる時刻 `retry_at` 付き）で止まる。500番台の読み取りは、1秒、2秒、4秒の間をおいて3回まで再試行する。書き込みは自動では再試行せず、`GITHUB_RATE_LIMITED` で止まる。
  - 呼び出しは1つずつ順に行う。並べて呼ばない（GitHub の二次のレート制限の指針）。
  - 1つのコマンドの中で書き込みを続けるときは、書き込みの間を1秒以上あける（公式の Best practices）。時刻と待ちは注入できるようにし、テストでは待たない。
  - 結果が分からない書き込みは、今と同じく読み直して確かめ、それでも分からなければ終了コード6で、効果（`effects`）と再開の手順（`recovery`）を返す。読み直しでは、送った値をすべて比べる。I-1 の `update_issue` の読み直しは `state_reason` を比べないので、`scope close` と `scope reopen` で使う I-5 が直す。
- 大量に書く移行のスクリプトは、さらに速さを抑える（11章）。

#### 構造のスナップショット（R-I1〜R-I6。契約 C10）

構造を、GitHub のリポジトリごとに一括で取得して1つのファイルに保存し、読むコマンド、ダッシュボード、HTML のダッシュボード（epic-00427）が使い回す。

- **置き場**：`<状態の置き場>/github/<ホスト>/<owner>/<repo>/`（すべて小文字。例 `github/github.com/chemitaro/spec-dock/`）。`snapshot.json`（構造）と `probe.json`（変わったかの確かめの記録）を置く。同じリポジトリのクローンが同じPCに複数あっても、1つを共有する。
- **書き方**：このディレクトリを読み取りで開いて `flock(LOCK_EX)` をかけ、その中で、一時ファイルに書いてから `rename` する。読むときは排他を取らない（`rename` なので、いつも完全なファイルが読める）。GitHub との通信は排他の外で行い、排他の中では書くだけにする。この排他は、カタログの排他（4章）とは別のものである。
- **`snapshot.json`（版1）**：

  ```json
  {
    "version": 1,
    "repository": "github.com/chemitaro/spec-dock",
    "fetched_at": "2026-10-25T12:00:00Z",
    "fetch_started_at": "2026-10-25T11:59:58Z",
    "issues": {
      "424": {
        "number": 424, "database_id": 3612345678, "id": "epic-00424", "kind": "epic",
        "slug": "canonical-spec-catalog", "title": "仕様の正本を…", "state": "open", "state_reason": null,
        "labels": ["spec-dock:epic"], "assignees": ["chemitaro"], "in_progress": false,
        "parent": 423, "sub_issues": [430, 431], "blocked_by": [], "blocking": [425],
        "created_at": "2026-10-25T03:00:00Z", "closed_at": null,
        "updated_at": "2026-10-25T11:00:00Z", "url": "https://github.com/chemitaro/spec-dock/issues/424"
      }
    },
    "external": {"17": {"number": 17, "title": "…", "state": "open"}},
    "anomalies": [{"number": 99, "code": "SLUG_MARKER_MISSING", "message": "…"}],
    "local_writes": [{"at": "2026-10-25T12:01:00Z", "command": "scope create", "numbers": [430]}]
  }
  ```

  - `issues` は、種類のラベルを持つ Issue（PRを除く）を、開いたものも閉じたものもすべて含む。キーは番号の文字列。`sub_issues` は GitHub の並びのまま、`blocked_by` と `blocking` は番号の昇順。`blocking` は、`blocked_by` を逆にたどって求める。
  - `external` は、Scope の `blocked_by` に現れる、同じリポジトリの、Scope でない Issue の題名と状態である。着手の判定（今の規則どおり、開いていれば着手できない）に使う。
  - 別のリポジトリの親、子、依存を持つ Scope（`anomalies` の `PARENT_FOREIGN_REPOSITORY`、`SUB_ISSUE_FOREIGN_REPOSITORY`、`DEPENDENCY_FOREIGN_REPOSITORY`）は、着手の判定で「着手できる」にしない（安全側に止める。ダッシュボードでは UNKNOWN）。
  - 本文は保存しない。slug の印だけを取り出す。種類や slug が決まらない Issue は `id` と `slug` を null にし、`anomalies` に入れる。
  - `created_at` と `closed_at`（閉じていなければ null）は、GitHub の `createdAt` と `closedAt` である。HTML のダッシュボード（epic-00427）の時間の軸（進み具合の推移、最近の動き）に使う。全体を読む GraphQL の問い合わせに2つの項目を足すだけで、要求の数は変わらない。I-1 の版1の形に、I-11 が足す（2026-10-26 の統括の判断）。0.3.0 の前で、利用者の状態の置き場にはまだスナップショットがないので、版は上げない。読む側は、この2つがない版1のファイルを、壊れたファイルと同じく取り直す。
  - 形を変えるときは `version` を上げる。読む側は、知らない版を読んではならない（取り直す）。
- **`probe.json`**：`{"version": 1, "checked_at": "…", "etags": {"spec-dock:initiative": "W/\"…\"", "spec-dock:epic": "…", "spec-dock:issue": "…"}, "last_error": null}`。新しい `ETag` は、全体の取り直しが成功したときだけ記録する（取り直しに失敗したら、次の確かめでも「変化あり」になるようにするため）。
- **新しさの段階**：構造を読む部品 `ensure_fresh(repository, level)` が、次の表で、確かめと取り直しを決める。時刻は注入できるようにする。

| 段階 | 使う場面 | 変わったかの確かめ | 全体を取り直す条件 | GitHub につながらないとき |
|---|---|---|---|---|
| `display` | 表示だけのコマンド（6章の表で「読む」が構造だけのもの）と `canonical status --structure` | 最後の確かめから60秒を超えていれば行う | 変化あり、`fetched_at` から30分を超えた、ファイルがない、版が違う | 今のスナップショットで続け、`warnings` に `GITHUB_SNAPSHOT_STALE`（取得の時刻）を入れる。ファイルがなければ、元の失敗のコード（つながらなければ `GITHUB_UNAVAILABLE`、制限なら `GITHUB_RATE_LIMITED`、権限なら `GITHUB_ACCESS_DENIED`）で止まる |
| `decision` | GitHub に書くコマンドの判断（6章の表で「書く」に GitHub があるもの） | 必ず行う | 変化あり、`fetched_at` から5分を超えた、ファイルがない、版が違う | 書く前に、元の失敗のコード（`GITHUB_UNAVAILABLE`、`GITHUB_RATE_LIMITED`、`GITHUB_ACCESS_DENIED` など）で止まる |
| `cycle` | 定期の同期（5章の周期の手順7） | 周期ごとに行う | `display` と同じ | 記録だけを残し、保存と push は続ける |

  - `decision` では、さらに、判断に使う Issue を `GET …/issues/{n}` で読み直す。作成では親、依存の追加では両端、`work start` では対象と、その依存先のうち Scope でないもの、閉じる操作では対象である。読み直した値がスナップショットと違えば、読み直した値で判断し、スナップショットにも反映する。
  - 見落とす変更：先頭の Issue が変わらない変更（種類のラベルが外れて一覧から消えただけの Issue）と、Issue の更新の時刻を変えないかもしれない親子と依存の変更（未確認）は、変わったかの確かめでは見つからない。30分ごとの取り直し、SpecDock の書き込みの反映、`decision` の読み直しで補う。
- **書き込みの反映**：SpecDock のコマンドは、GitHub への書き込みが成功するたびに、その結果（作った Issue、題名、状態、ラベル、担当者、親子、依存）をスナップショットの該当する要素に反映し、`local_writes` に記録する。全体の取り直しを書き込むときは、`fetch_started_at` より後の `local_writes` の変更を重ねてから書く（取り直しの途中の書き込みを消さないため）。それより前の `local_writes` は消す。
  - 反映できない変更（親子や依存の相手の番号がスナップショットにない、など）は、当てずに飛ばし、スナップショットを古いものとして扱って、次の `ensure_fresh` で全体を取り直させる。GitHub への書き込みは成功しているので、コマンドの結果を失敗にせず、`GITHUB_SNAPSHOT_STALE` を警告に入れる。I-1 の `reflect` はこの場合に `ValueError` を出すので、書き込みの後に最初に使う I-5 が、この扱いに直してテストを足す（`snapshot.json` の形式の版は変えない）。
- **書けないとき**：状態の置き場に書けないとき（サンドボックスの中など）は、スナップショットをプロセスのメモリーの上だけで持つ。書けないことを理由に失敗してはならない。
- **読むだけのコマンドの契約**：表示だけのコマンドが書いてよいのは、状態の置き場の `snapshot.json` と `probe.json` だけである。リポジトリ、カタログ、`.git`、GitHub には書かない。今の CLI の「構造をキャッシュしない」方針は、利用者の方針（R-I1）に従い、canonical モードでだけ変える。従来モードは変えない。
- **規則の部品**：`StructureSnapshot` は、スナップショットを読み込んだもので、Scope の一覧と、`id → ScopeNode` の対応と、異常の一覧を持つ。`ScopeNode` は、上の `issues` の1要素と同じ項目を持つ。階層、種類、循環の規則は、今の `domain/dependency_vnext.py` と `infra/scope_tree.py` の規則をそのまま使い、入力を `.meta.json` から `StructureSnapshot` に変える。`dependency add` の循環の確認も、スナップショットの上で行う。異常のために `id` が決まらない依存先は、循環の確かめに入れない。そのような依存を持つ Scope は、着手の判定で「着手できる」にしない（I-4、I-11）。
- 費用の見込み（spec-dock、Scope 243件）：変化がない周期は、304 が3回で、主のレート制限を消費しない。全体の取り直しは GraphQL の3回で、1回あたり約4点（2026-10-26 に実測。`rateLimit.cost` で確かめる）。30分ごとの取り直しを含めても、1時間に GraphQL の数十点である（上限は1時間に5,000点）。

#### 内容の置き場

- Scope のディレクトリは、今と同じ入れ子に置く。Initiative は `<カタログ>/<ID>-<slug>/`、Epic は `<Initiative>/epics/<ID>-<slug>/`、Issue は `<Epic>/issues/<ID>-<slug>/`。
- コマンドは、Scope のディレクトリを、入れ子の位置ではなく名前で探す。カタログの中で `<ID>-*` という名前のディレクトリが、ちょうど1つ見つかればよい（`infra/catalog_tree.py`。`git ls-files` は使わない。未保存の新しい Scope も見えるようにするため）。そのため、入れ子が GitHub とずれても、コマンドは動き続ける（R-A3）。ずれは `workspace validate` と `canonical status --structure` が報告し、`scope move` が直す。
- `.meta.json` がカタログにあれば、異常として報告する。

### 3. カタログとリンク（R-B1〜R-B8）

#### 場所の決め方

- Git の共通ディレクトリを `git rev-parse --path-format=absolute --git-common-dir` で求める。その名前が `.git` で、親のディレクトリの `.git` がそれ自身であるとき、親のディレクトリが mainのチェックアウトである。そうでなければ（bare など）、`CANONICAL_UNSUPPORTED_LAYOUT` で止める（R-B1）。
- カタログは `<main>/spec-dock/.canonical`、リンクは `<チェックアウト>/spec-dock/initiatives` である。
- リンクの先は、mainのチェックアウトでは `.canonical`（相対）、作業用のworktreeでは `<main>/spec-dock/.canonical`（絶対パス）とする。リンクの先をさらにリンクにしてはならない（調査の記録：リンクのリンクにすると、mainで古いコミットへ移ったときに、すべての作業用のworktreeが古い実体を開く）。
- **正しいリンク**とは、`spec-dock/initiatives` がシンボリックリンクで、その値が上の値と同じで、たどった先の実際のパスがカタログの実際のパスと同じものをいう。

#### 無視の設定

次の3行を使う。2行目と3行目の組み合わせは、`spec-dock/initiatives` がシンボリックリンクのときだけ無視し、実体のディレクトリのときは中の新しいファイルを無視しない（2026-10-25 に確認。Git はシンボリックリンクをファイルとして扱い、末尾が `/` の規則はディレクトリにだけ当たるため）。そのため、移行していないリポジトリに入れても害がない。

```text
/spec-dock/.canonical/
/spec-dock/initiatives
!/spec-dock/initiatives/
```

- 配布資産の `spec-dock/.gitignore` に、同じ3行を `spec-dock/` からの相対の形（`/.canonical/`、`/initiatives`、`!/initiatives/`）で足す。Claude Code の検索は `.gitignore` だけを読み、`info/exclude` を読まないため（調査の記録）。
- `canonical link` は、同じ3行を `<共通ディレクトリ>/info/exclude` にも足す。移行前のブランチ（`.gitignore` にこの行がない）をチェックアウトしたときも、カタログを `git add -A` で取り込まないようにするためである（調査の記録：この行がないと gitlink が入る）。

#### `spec-dock canonical link`

どのチェックアウトから実行しても、次を順に行う。何度実行しても結果は同じで、行ったことを `effects` に、利用者に残る作業を `warnings` に返す。

1. **前提**：宣言の版が4であること。mainのチェックアウトが見つかること。`git --version` が 2.38 以上であること（`merge-tree --write-tree` のため。足りなければ `CANONICAL_GIT_TOO_OLD`。Ubuntu 22.04 の標準の 2.34 などが当たる）。
2. **先に確かめる**（書く前にすべて）：
   - **マウントしたチェックアウトでないこと**（R-C8）：カタログの `.git` ファイルの `gitdir:` の先、または Git の登録（`<共通ディレクトリ>/worktrees/<名前>/gitdir`）が指すパスが、このプロセスから見て存在しないとき、コンテナの中（`/.dockerenv` か `/run/.containerenv` がある、または環境変数 `container`、`REMOTE_CONTAINERS`、`CODESPACES` のどれかがある）なら、`CANONICAL_FOREIGN_CHECKOUT` で止まる。ホストのフォルダーをマウントすると、コンテナの中ではパスが変わり、ここで `git worktree repair` を行うとホストの記録をコンテナのパスに書き換えてしまうためである。次の1手は「保存と同期はホストで行われる。コンテナでは仕様のファイルを読み書きするだけにするか、コンテナの中でクローンする」。コンテナの中でなければ、mainのチェックアウトの移動として、手順3の `repair` に進む。
   - **mainの移動の判定**：パスの文字列ではなく実体（`os.path.samefile`）で比べる。`repair` に進むのは、登録のパスか `gitdir:` の先が、このプロセスから見えないときだけである。両方が存在して別の実体なら、`CANONICAL_PATH_OCCUPIED` で止まる（別名のパスでマウントした環境で、ホストのすべてのworktreeの `.git` を書き換えないため。I-2 の統括の判断）。
   - `<main>/spec-dock/.canonical` に、カタログでないファイルやディレクトリがないこと（あれば `CANONICAL_PATH_OCCUPIED`）。
   - **mainの宣言**：mainのチェックアウトの宣言が版4でない（mainが移行前のコミットにある、など）ときは、mainのリンクを置かず、mainの `spec-dock/initiatives` の確かめ（次の項目）も行わない。カタログの作成、除外、実行したチェックアウトのリンクは行い、警告 `CANONICAL_MAIN_NOT_MIGRATED` を返す。mainにリンクを置くと、mainの従来のコマンドが止まるためである（I-2 の統括の判断）。
   - mainのチェックアウトと、実行したチェックアウトの `spec-dock/initiatives` が、ない、正しいリンク、違う先のリンクのどれかであること。実体のファイルやディレクトリなら `CANONICAL_LINK_OCCUPIED` で止まり、そのパスと、中にあるファイルの数を示す。中身を消してはならない。
   - 以下の手順で書く必要のある場所に、このプロセスが書けること（`os.access`）。書けないときは、`CANONICAL_SANDBOX_DENIED` で止まり、「サンドボックスの外（普通の端末）で `spec-dock canonical link` を実行する」と示す。カタログ、除外、登録簿がそろっていて、リンクを置くだけなら、作業用のworktreeの中にしか書かないので、Codex のサンドボックスの中でも通る。この確かめは、`ls-remote` などのネットワークの処理より前に行う（Codex のサンドボックスは既定でネットワークがないので、`GITHUB_UNAVAILABLE` ではなく `CANONICAL_SANDBOX_DENIED` で止めるため。I-2 の統括の判断）。
   - ここまでで止まるときは、何も書いていないので、`failed`（終了コード3）で返す。
3. **カタログ**：`git worktree list --porcelain` で、`spec-dock/canonical` をチェックアウトしているworktreeを探す。
   - 登録されたパスが `<main>/spec-dock/.canonical` で、ディレクトリがあれば、何もしない。lock されていなければ lock する。
   - `<main>/spec-dock/.canonical` に `.git` ファイルのあるディレクトリがあるが、登録のパスが違う、または登録が壊れている（mainのチェックアウトを移動した後など）ときは、`git worktree repair <カタログ>` で直す。ディレクトリがあるときに `prune` してはならない。git の `repair` は、このとき、ほかの作業用のworktreeから mainへのつながりも直すことがある（`effects` とメッセージに書く）。SpecDock がほかのworktreeを直すことはせず、警告 `CANONICAL_MAIN_MOVED` を返す（I-2 の統括の判断）。
   - `spec-dock/canonical` が、`<main>/spec-dock/.canonical` ではないパスの登録でチェックアウトされているときは、何も書かずに `CANONICAL_PATH_OCCUPIED`（その登録のパス）で止まる。そのパスが存在するときも、存在しない（登録だけが残っている）ときも同じである。
   - 登録はあるがディレクトリがない（`git clean -ffdx` の後など）ときは、`git worktree add -f -f <カタログ> spec-dock/canonical` で同じ場所に作り直し、lock する（lock された消えたパスに作るには `--force` を2回付ける。git の文書）。`-f -f` は、`spec-dock/canonical` をチェックアウトしている登録がちょうど1つで、そのパスがカタログの場所のときだけ使う。`git worktree prune` は、クローン全体の消えた登録（外れた外付けのボリュームのworktreeなど）を選ばずに消すので、SpecDock は実行しない（I-2 の統括の判断。Git 2.54.0 で確認）。
   - **作りかけのカタログ**：`<共通ディレクトリ>/worktrees/<名前>/` に `index` がないカタログは、`git worktree add` が途中で止まったもの（時間切れで止めても、git の子プロセスが書き続けることがある）として扱う。完成したカタログと判定してはならない（同期が大量の削除を保存するおそれがあるため）。`canonical link` は書く前に、`canonical status` と `require_linked` も、`CANONICAL_PATH_OCCUPIED` で止まる。次の1手は「そこで git が動いていないことと、要るものがないことを確かめてから、`git -C <main> worktree remove --force --force <カタログ>`。その後で `spec-dock canonical link`」とし、消す操作は利用者が行う（I-2 の統括の判断）。別の `canonical link` が作っている最中（`index.lock` があるなど）は、先に「しばらく待って同じコマンドを実行する」を示す（I-3 が直す。I-2 の報告書の RST-1）。
   - 作るときは、まず `git ls-remote --exit-code origin refs/heads/spec-dock/canonical` で GitHub に canonical があるかを確かめる。終了コード2なら「ない」、0なら「ある」、それ以外は接続の失敗として止まる（`GITHUB_UNAVAILABLE`）。ある場合は、取得の対象にこのブランチが入っていない浅いクローンでは `git remote set-branches --add origin spec-dock/canonical` を行ってから `git fetch origin spec-dock/canonical` を行う。ローカルのブランチがなければ `git worktree add --track -b spec-dock/canonical <カタログ> origin/spec-dock/canonical`、あれば `git worktree add <カタログ> spec-dock/canonical` とする。最後に `git worktree lock --reason "spec-dock canonical catalog" <カタログ>` を行う。
   - GitHub に canonical がなく、既定のブランチの HEAD のツリーに `spec-dock/initiatives` がないとき（新しいリポジトリ）は、5章の「canonical の中身」の管理ファイルだけを持つ、親のないコミットを作って push する。push が先に進まれて拒否されたら（別のPCが同時に作った）、手元で作ったブランチを捨て、GitHub のものを取得して使う。
   - GitHub に canonical がなく、既定のブランチ（`origin/HEAD`、なければ mainのチェックアウトの HEAD）のツリーに `spec-dock/initiatives` があるとき（移行していない）は、何も書かずに `CANONICAL_NOT_MIGRATED` で止まり、移行の手順書を示す（I-2 の統括の判断）。
   - GitHub に canonical がなく、ローカルのブランチ `spec-dock/canonical` があるときは、新しい初期のコミットを作らず、ローカルのブランチからカタログを作る。そのブランチの中身が初期のコミットだけ（親のない1つのコミットで、ツリーが5章の管理ファイルだけ。I-8 が作ったもの、初期のコミットだけの canonical が GitHub で消された後など、どう生じたかは問わない）なら、新しいリポジトリのときと同じく push する（もう一度の実行で続きから整うため）。なお、`canonical link` が新しいリポジトリで初期のコミットを作るときは、push が成功する前にローカルの参照を作らない（参照を作らずにコミットを push する）ので、push に失敗した後のもう一度の実行は、新しいリポジトリの経路で整う。それ以外は push せず、警告 `CANONICAL_REMOTE_MISSING` を返す。GitHub で消されたときの扱いは、5章の基準と一時停止に任せる（I-2 の統括の判断）。
4. **除外の設定**：`info/exclude` に、上の3行のうち足りない行を足す。
5. **リンク**：mainのチェックアウトと、実行したチェックアウトに、正しいリンクを置く。ないときは作り、違う先のリンクは、一時的な名前で作ってから `rename` で置き換える（`ln -s` を重ねると、リンクの先の中に余計なリンクができるため。調査の記録）。
6. **登録簿と定期の実行**（I-3 が足す。実際の順は、6a 登録簿、7 基準、6b ジョブの作成とすぐの実行、6c 記録の確かめ。6b がジョブをすぐに動かすので、先に基準を記録する。ジョブの `PATH` には、git のディレクトリと標準の場所に加え、`gh` のディレクトリも入れる。I-3 の統括の判断）：登録簿にカタログを足し（移動の後なら古いパスの項目を消し）、5章の「定期の実行の選び方」で選んだ仕組みがなければ作って動かす（systemd のない Linux では、常駐のプロセスを起動する）。作った直後に1回だけ実行させ、最大15秒、状態の置き場の記録を待つ。その1回では、push の認証も確かめる（5章の `push_auth`）。読めなかったとき（macOS のプライバシーの保護など）、認証できなかったとき、ログアウト中に止まる環境（linger がない）、常駐のプロセスの環境（起動し直しの1行）は、その原因と次の1手を `warnings` に返す。
7. **基準**：カタログを作った、または基準がないときは、取得した `origin/spec-dock/canonical` を、そのカタログの基準として状態の置き場に記録する（5章）。追跡の参照がなく、ローカルに `spec-dock/canonical` があるとき（GitHub で消された後など）は、手元の HEAD を基準にする。手元に未pushのコミットがあると、次の周期は `remote_rewritten` で一時停止し、`resume --adopt-remote` で戻る（I-3 の統括の判断）。
8. **ツールの設定**：9章の判定を行い、足りない設定を正確な1行で `warnings` に返す。

- 書く手順（3〜5）は、クローンの `StartLock` の中で行う（同じクローンの2つのチェックアウトの同時の `canonical link` を防ぐ）。ネットワークの処理（`ls-remote`、`fetch`、初期の push）は排他の外で行う。取れなければ `START_LOCK_BUSY`（終了コード3）で止まる（I-2 の統括の判断）。
- 3〜7の途中で失敗したときは、それまでの効果を `succeeded`、残りを `not_attempted` とした `partial`（終了コード6）で返し、`recovery` に `spec-dock canonical link`（もう一度実行すれば続きから整う）を入れる。
- **`--no-schedule`**：付けると、手順6を行わない。`state.json` に `"schedule": "none"` を記録し、後の `worktree create` と `work start` の `link_after_command` も、この印があれば手順6を行わない（予行演習で、利用者の定期の実行に触れないため）。`--no-schedule` なしの `canonical link` は、印を消して登録する（I-3 の統括の判断）。登録簿に載せず、定期の実行を作らず、起動もしない。手順7の基準は、この場合も記録する。予行演習（R-J3。11章）と、手で `canonical sync` を実行する確かめのための指定である。`canonical status` の `sync` は、「定期の実行なし（`--no-schedule`）」と示す。登録されていないカタログは、`canonical sync`（`--registered` なし）をそのチェックアウトで実行すれば処理される。

#### SpecDock のほかのコマンドから

- `worktree create` は、`git worktree add` の後に、作ったworktreeについて `canonical link` と同じ手順（1〜8）を行う。`work start` は、選択を記録した後に、対象のチェックアウトについて同じ手順を行う（R-B4「同じ処理」）。リンクの手順の失敗は、そのコマンド自体の結果を変えず、警告と次の1手として返す。
  - どちらも、I-2 が置く公開の関数 `link_after_command`（C3。手順1〜5と8。登録と基準は I-3 が同じ経路に足す）を、`StartLock` を持たずに呼ぶ。canonical の `worktree create` は I-2 が `CANONICAL_HANDLERS` に登録し、今の作成の関数の後に呼ぶ。canonical の `work start` は、I-5 が選択を記録して `StartLock` を放した後に呼ぶ。従来の `direct_worktrees.py` と `work_start.py` は変えない（AC-15）。`START_LOCK_BUSY` などの失敗も、呼び出し元の結果を変えず、警告（次の1手は `spec-dock canonical link`）で返す（I-2 の統括の判断）。
- そのほかの、仕様を使う canonical モードのコマンドは、リンクやカタログがない、または正しくないとき、自分では直さずに `CANONICAL_NOT_LINKED` で止まり、`recovery` に `spec-dock canonical link` を入れる（R-B5）。カタログの Git の登録が、手順2と同じ形でコンテナの中から見えないときは、`CANONICAL_FOREIGN_CHECKOUT` で止まる。git が 2.38 より古いときも、`CANONICAL_GIT_TOO_OLD` で止まる（カタログの観察に `git worktree list --porcelain -z` を使い、古い git では読むだけのコマンドも正しく動かないため。この前提の確かめ `require_linked` は I-2 が置き、I-4 と I-5 が使う。I-2 の統括の判断）。仕様のファイルを読み書きするだけのコマンドではないので、ファイルの読み書きそのものは妨げない。
- **カタログの中からの実行**：エージェントが `spec-dock/initiatives/...` へ移って SpecDock を実行すると、Git はリンクの先の実際のパスでカタログのworktreeを解決し、宣言が見つからない。そこで、`dispatch()` は `resolve_context` の前に、解決したworktreeが `spec-dock/canonical` をチェックアウトしていて、ルートに `.spec-dock-canonical.json` があるときだけ、`CANONICAL_INSIDE_CATALOG`（終了コード3）で止まる。次の1手は「チェックアウトのルートで実行するか、`--project <チェックアウト>` を付ける」。版3のリポジトリにはカタログがないので、従来モードの振る舞いは変わらない（I-2 が置く。I-2 の統括の判断）。
- 読むだけのコマンド（`canonical status`、`scope show`、`workspace validate` など）は、リポジトリ、カタログ、`.git`、GitHub に何も書かない（書いてよいのは、状態の置き場の構造のスナップショットだけ。2章）。カタログに対する Git の呼び出しには `git --no-optional-locks` を付け、`.git` のインデックスも書かない。

#### `spec-dock canonical status`（読むだけ。R-B7）

次の項目を返す。問題ごとに、次の1手を1つ付ける。

| 項目 | 内容 |
|---|---|
| `catalog` | 場所、ブランチ、lock の有無、HEAD のコミット、Git の登録のパスとの一致 |
| `link` | mainのチェックアウトと、このチェックアウトのリンクが正しいか |
| `exclude` | 無視の3行が、`info/exclude` と `spec-dock/.gitignore` にあるか |
| `access` | このプロセスがカタログを読めるか、書けるか（`os.access`。サンドボックスの中では、書けない場所に False を返す。確認済み） |
| `tools` | 9章の判定の結果と、足りない設定の1行 |
| `sync` | 定期の実行の仕組み（`launchd`、`systemd`、`loop`）と、その有無と状態（常駐のプロセスなら動いているか）、linger（Linux）、push の認証の結果、最後に成功した同期の時刻、最後の失敗と理由、一時停止（`paused`）の理由 |
| `changes` | 未保存の変更の数、未pushのコミットの数と最も古い時刻、保留、別名ファイル、統合を止めているパスとその理由 |
| `format` | canonical の形式の版と、この SpecDock が書けるか |
| `git` | 使う git のパスと版（2.38 以上か） |
| `snapshot` | 構造のスナップショットの場所、取得の時刻、最後の確かめの時刻、異常の数。GitHub には問い合わせない |
| `dashboard` | ダッシュボードの5つのファイルの有無と、最後に作り直した時刻 |
| `structure` | 入れ子と GitHub の親子のずれ（`--structure` を付けたときだけ、`display` の新しさでスナップショットを確かめる） |

- 読むだけの診断なので、問題があっても `succeeded`（終了コード0）で返し、問題ごとに `warnings`（`details.next_step` に次の1手）と、各項目の状態と次の1手で示す。mainのチェックアウトが見つからない構成だけは `CANONICAL_UNSUPPORTED_LAYOUT` で `failed` にする。宣言が版3のときは `CANONICAL_NOT_MIGRATED`（1章）。
- 項目の担当：`catalog`、`link`、`exclude`、`access`、`tools`、`format`、`git`（今の `PATH` の git）、`changes`（未保存の変更の数、未pushのコミット、別名ファイル）は I-2。`sync`、`snapshot`、`changes` のうち `state.json` を読む部分（保留、統合を止めているパス）と、`git` の定期の実行が使う git は I-3。`dashboard` は I-11。`structure` と `--structure` は I-4。まだ足していない項目も `data` のキーとして置き、状態を「未対応」の値にする（I-2 の統括の判断）。
- 未pushのコミットが10分を超えたら警告する（R-C6）。
- 同期の項目は、状態の置き場の `state.json` を読む。カタログが読めないときも示せる。

#### `spec-dock canonical remove`（取り外し。R-B8）

- 対象はこのクローン。`--yes` がなければ、予定だけを示して何もしない（`planned`）。
- 次のどれかがあれば、書く前に止まる。未保存の変更か未pushのコミット（`CANONICAL_UNSAVED_CHANGES`）、カタログの中の、`.runtime/` 以外の無視されたファイル（`.workbench` など。`CANONICAL_IGNORED_FILES_PRESENT`。ファイルの一覧を示す。`git worktree remove` で消えてしまうため）。
- 次を外す。同じクローンのすべてのチェックアウトの、正しいリンク（実体は消さない）、カタログのworktree（unlock して `git worktree remove`）、`info/exclude` の3行、登録簿の項目と状態の置き場のカタログの記録、mainのチェックアウトのダッシュボードの5つのファイル、定期の実行（ほかに登録されたカタログがないときだけ。常駐のプロセスなら止める）。構造のスナップショットは、同じリポジトリのほかのクローンが使っていることがあるので消さない。
- ローカルのブランチ `spec-dock/canonical` と、GitHub のブランチは消さない。
- AGENTS.md の「対象と結果を明示した指示が要る破壊的なコマンド」に、このコマンドを足す。

### 4. カタログへの書き込みの排他と変更の束（R-D1）

- **排他**：カタログに書く SpecDock のコマンドと、定期の同期は、カタログのディレクトリを読み取りで開き、`flock(LOCK_EX)` をかける。待つのは既定で10秒までで、取れなければ `CANONICAL_LOCK_BUSY`（終了コード3）で止まる。定期の同期は、取れなければその周期でそのカタログを飛ばす。
  - ファイルを作らないので、Codex のサンドボックスの中からでも取れる。サンドボックスの内と外で互いに効くことを確かめた（調査の記録）。
  - 排他の中では、ネットワークを使ってはならない。
  - `StartLock` とは別のものとする。カタログの書き込みで `work start` を待たせないためである。
- **変更の束**：コマンドは、排他の中でファイルを書いた後、`<カタログ>/.runtime/changesets/<UTC の時刻>-<乱数>.json` を、一時ファイルに書いてから `rename` で置く。

  ```json
  {"version": 1, "origin": "command", "command": "scope create", "created_at": "2026-10-25T12:00:00Z",
   "paths": ["init-00423-canonical-spec-storage/epics/epic-00424-canonical-spec-catalog"], "deletions": []}
  ```

  - `paths` と `deletions` は、カタログのルートからの相対パスで、ディレクトリを書けばその下をすべて含む。
  - `origin` は `command`（SpecDock のコマンドが自分で行った変更）か `finish`（`work finish` が、利用者やエージェントの変更をすぐに保存するよう頼むもの）である。
  - 定期の同期は、束にあるパスを、30秒の待ちなしに、1つのコミットで保存する。`origin: command` の削除は保留しない。`origin: finish` の変更には、すべての保留の規則を当てる。保存したら束のファイルを消す。束にあるパスが今はなく、HEAD にもなければ、そのパスは無視する。
  - SpecDock のコマンドはコミットしない（Codex のサンドボックスからは `.git` に書けないため。調査の記録）。
- **作成の作業場所**：`scope create` などの作業場所（今は `spec-dock/.agent/staging`）は、canonical モードでは `<カタログ>/.runtime/staging/` に置く。同じファイルシステムの中で `rename` するためである。

### 5. 定期の同期（R-C1〜R-C6）

#### canonical の中身（形式 1）

```text
spec-dock/canonical のルート
  .spec-dock-canonical.json   {"format": 1}
  .gitignore                  .runtime/
                              **/.workbench/*
                              !**/.workbench/README.md
                              **/.workbench/README.md/**
  README.md                   このブランチが仕様の内容の正本であること、コードのブランチにマージしないこと、
                              編集は各チェックアウトの spec-dock/initiatives から行うことを書く
  init-…/                     今の spec-dock/initiatives/ の中身（.meta.json を除く）
```

- カタログには `spec-dock/.gitignore` が効かないので、`.workbench` の規則をカタログの `.gitignore` に持つ。

#### 状態の置き場

- 根は `${XDG_STATE_HOME:-$HOME/.local/state}/spec-dock/` とする（macOS でも同じ）。根の求め方は、構造のスナップショット（C10）の置き場にも使うので、I-1 が `infra/state_root.py` の `resolve_state_root` として作る。この関数は、明示の上書き（`--state-root` の値）を受け取り、あればそれを使う。I-3 は、登録簿、`state.json`、`--state-root` を、この上に足す。`canonical link` を実行したときに求めた絶対パスを、定期の実行の引数（`--state-root <絶対パス>`）に書き込む。定期の実行の環境では `XDG_STATE_HOME` が普通は設定されていないため、実行のたびに求め直してはならない。
- **登録簿**：`<根>/canonical-registry.json`。中身は `{"version": 1, "scheduler": "launchd|systemd|loop", "catalogs": [{"catalog": "<実際のパス>", "main_checkout": "...", "repository": "github.com/<owner>/<repo>", "git": "<git の絶対パス>", "registered_at": "..."}]}`。`repository` は、構造のスナップショットの置き場を決めるのに使う（2章）。
  - 書くときは、同じディレクトリの一時ファイルに書いてから `rename` する。同時の書き込みは、`<根>` のディレクトリへの `flock` で防ぐ。
  - `git` には、`canonical link` を実行したときの `PATH` で見つかった git の絶対パスを記録する。定期の実行の `PATH` は狭く、macOS のプライバシーの保護の許可もプログラムごとなので、利用者がふだん使う git を使うためである（調査の記録：Apple の `/usr/bin/git` は外付けのボリュームを読めず、Homebrew の git は読めた）。
- **カタログごとの状態**：`<根>/catalogs/<鍵>/state.json`。鍵は、カタログの実際のパスの SHA-256 の先頭16文字。定期の同期と `canonical link` だけが書き、ほかのコマンドは読むだけ。カタログが読めないときや、`git clean -ffdx` でカタログの `.runtime/` が消えたときでも、記録と基準が残る。

  ```json
  {
    "version": 1,
    "catalog": "<実際のパス>",
    "updated_at": "2026-10-25T12:00:00Z",
    "last_cycle": {"started_at": "...", "finished_at": "...", "result": "ok|skipped|error|paused"},
    "last_success_at": "...",
    "last_error": {"code": "...", "message": "...", "next_step": "...", "program": "<拒否されたプログラム。あれば>"},
    "paused": null,
    "head": "<周期の終わりの HEAD>",
    "last_seen_remote": "<基準>",
    "remote_contains_head": true,
    "unpushed_since": null,
    "pending_since": {"<パス>": "<最初に見つけた時刻>"},
    "holds": [{"path": "...", "kind": "mass_delete|secret|too_large", "since": "..."}],
    "conflicts": [{"path": "...", "copy": "...", "at": "..."}],
    "blocking": [{"path": "...", "reason": "local_edit|held"}],
    "consumed_changesets": ["<束のファイル名>"],
    "push_auth": {"result": "ok|failed|unknown", "at": "...", "message": "..."},
    "schedule": "none",
    "adopt_remote_pending": null,
    "dashboard": {"input_hash": "<sha256>", "written_at": "...", "error": null}
  }
  ```

  - 書くときは、一時ファイルに書いてから `rename` する。`consumed_changesets` は直近の100件だけを残す。
  - `schedule` は、`--no-schedule` の印である（3章。ないときは定期の実行あり）。`adopt_remote_pending` は、`resume --adopt-remote` の後の取り込み直しの途中の記録である（下の「一時停止と再開」。途中でなければ null）。`last_error` は、最後の失敗のコード、次の1手、時刻（`at`）を持つ（I-3 の統括の判断）。
  - `push_auth` は、`canonical link` の後の最初の周期と、push が認証で失敗したときに書く。「最初の周期」は、`state.json` に `push_auth` がないか、`result` が `unknown` の周期とし、`canonical link` の手順7が `state.json` を作るときは `unknown` を書く（I-3 の統括の判断）。最初の周期では、送るものがなくても `git push --dry-run origin HEAD:refs/heads/spec-dock/canonical` を行い、認証できるかを確かめる（dry-run でも認証が要ることは確認済み）。失敗したら、リモートの URL が `https` なら `gh auth setup-git`、`ssh` なら「定期の実行には SSH のエージェントが渡らないことがあるので、`https` と `gh` の認証を使う」を次の1手にする。
- **ログ**：`<根>/canonical-sync.log`。1 MiB を超えたら1世代だけ残して切り替える。ファイルの中身は書いてはならない。

#### 定期の実行の選び方（R-C7）

`canonical link` が、次の順に選び、登録簿の `scheduler` に記録する。一度選んだら、`canonical remove` の後か、選んだ仕組みが使えなくなったときだけ選び直す。

1. macOS なら `launchd`。
2. Linux で、`/run/systemd/system` があり、`systemctl --user is-system-running` が `running` か `degraded` を返すなら `systemd`。「Failed to connect to bus」で失敗したときは、1秒おきに5回まで試し直す（仮想マシンの起動の直後に、最初の1回だけ失敗し、数秒後には通った。確認済み）。
3. それ以外の Linux（コンテナ、devcontainer など。systemd も cron もないことを確認済み）なら `loop`（常駐のプロセス）。

3つのどれでも、1周期の中身（下の「1回の周期」）は同じである。

#### 定期の実行の登録

macOS（launchd）：

- `~/Library/LaunchAgents/io.github.chemitaro.spec-dock.canonical-sync.plist` に置く。外付けのボリュームに置いた plist は `launchctl bootstrap` が拒否した（調査の記録）ので、必ずここに置く。
- 中身は次のとおり。
  - `Label`：上の名前。
  - `ProgramArguments`：spec-dock の実行ファイルの絶対パス、`canonical`、`sync`、`--registered`、`--state-root`、`<根の絶対パス>`。実行ファイルは、`canonical link` を動かしている spec-dock のコンソールのスクリプトの実際のパス（`sys.argv[0]` をたどったもの）とする。
  - `WorkingDirectory`：ホーム。
  - `StartInterval` 60、`RunAtLoad` true。
  - `StandardOutPath` と `StandardErrorPath`：`<根>/canonical-sync.log`。
  - `EnvironmentVariables` の `PATH`：記録した git のディレクトリを先頭に、`/usr/bin:/bin:/usr/sbin:/sbin`。
- 登録は `launchctl bootstrap gui/<uid> <plist>`、すぐの実行は `launchctl kickstart gui/<uid>/<Label>`、解除は `launchctl bootout gui/<uid>/<Label>` で行う。launchd は、同じジョブを重ねて動かさない。

Linux（systemd のユーザーのタイマー。デスクトップ、SSH で入るサーバーと仮想マシン）：

- `${XDG_CONFIG_HOME:-~/.config}/systemd/user/spec-dock-canonical-sync.service` と `spec-dock-canonical-sync.timer` を置く。

  ```ini
  # spec-dock-canonical-sync.service
  [Unit]
  Description=SpecDock canonical sync
  [Service]
  Type=oneshot
  WorkingDirectory=%h
  Environment=PATH=<記録した git のディレクトリ>:/usr/local/bin:/usr/bin:/bin
  ExecStart=<spec-dock の絶対パス> canonical sync --registered --state-root <根の絶対パス>

  # spec-dock-canonical-sync.timer
  [Unit]
  Description=SpecDock canonical sync timer
  [Timer]
  OnActiveSec=10s
  OnUnitActiveSec=60s
  AccuracySec=5s
  [Install]
  WantedBy=timers.target
  ```

  - 値の中の `%` は `%%` と書く（systemd の指定子として読まれるため。確認済み）。パスに空白などがあれば、systemd の引用の規則で書く。
  - `OnActiveSec` は、タイマーが動き始めてから最初の実行までの時間で、`OnUnitActiveSec` は、前の実行から次の実行までの時間である。この組み合わせで動くことを確かめた（下）。
- `systemctl --user daemon-reload` と `systemctl --user enable --now spec-dock-canonical-sync.timer` で動かす。解除は `systemctl --user disable --now spec-dock-canonical-sync.timer` の後にファイルを消し、`daemon-reload` する。
- **linger**：`loginctl show-user <ユーザー> -p Linger --value` が `no` なら、ログアウトしている間は、ユーザーの systemd ごと止まり、同期も止まる。デスクトップならそれでよい。SSH で入るサーバーや仮想マシンでは、エージェントがログアウトの後も動くことがあるので、`canonical link` と `canonical status` が、`loginctl enable-linger <ユーザー>`（管理者の権限が要ることがある）を次の1手として示す。SpecDock は、linger を変えてはならない（環境の設定であり、セッションのない環境では変えられないことも確認済み）。
- 2026-10-25 に、Ubuntu 24.04（systemd 255）の仮想マシンで、この形のタイマーが動くこと、`WorkingDirectory=%h` と `Environment=PATH=…` が渡ることを確かめた。タイマーからの push の認証は、担当の Issue で確かめる。

Linux（常駐のプロセス。systemd のないコンテナ、devcontainer）：

- `spec-dock canonical sync --registered --loop --state-root <根の絶対パス>` が、終了の合図（SIGTERM、SIGINT）まで、60秒ごとに1周期を動かす。
- **1つだけ動く**：起動したら、`<根>/runner.lock` を開いて `flock(LOCK_EX|LOCK_NB)` をかけ、終わるまで持つ。取れなければ、すでに動いているので、終了コード0で何もせずに終わる。`<根>/runner.json` に、プロセスの番号、起動の時刻、spec-dock の版を書く。
- **起動**：`canonical link` の手順6が、動いていなければ、切り離して起動する（`--detach`。新しいセッションで起動し、標準入力を閉じ、出力を `<根>/canonical-sync.log` に向け、作業ディレクトリをホームにする）。起動した後、最初の周期の記録を最大15秒待つ。
- **起動し直し**：コンテナを起動し直すと、常駐のプロセスは止まる。`canonical link` と `canonical status` は、次の1行を `warnings` に返す。SpecDock は、devcontainer やコンテナの起動の設定を書き換えない（約束4）。

  ```text
  spec-dock canonical sync --registered --loop --detach --state-root <根の絶対パス>
  ```

  devcontainer なら `postStartCommand` に、ほかのコンテナなら起動のスクリプトに足す。足さなくても、次に `spec-dock canonical link` を実行すれば動き直す。
- **止める**：`canonical remove` は、ほかに登録されたカタログがなければ、`runner.json` のプロセスに SIGTERM を送る。常駐のプロセスは、周期の途中なら、その周期を終えてから止まる。
- 2026-10-25 に、`ubuntu:24.04` のコンテナで、PID 1 が `sh` で、systemd も cron もないことを確かめた。

**すぐの実行の頼み方**（`canonical link` の手順6、`work finish` が使う）：

- `launchd`：`launchctl kickstart gui/<uid>/<Label>`。
- `systemd`：`systemctl --user start --no-block spec-dock-canonical-sync.service`。
- `loop`：常駐のプロセスが動いていれば、`<根>/kick` を作る。常駐のプロセスは2秒ごとにこのファイルを見て、あれば消して、すぐに1周期を動かす。動いていなければ、`--detach` で起動する。
- どれも、サンドボックスの中などで失敗しても、無視してよい。遅くとも60秒で次の周期が来る。

#### カタログに対する Git の呼び出し

- 定期の同期、`canonical link`、`canonical restore`、`canonical remove` が、カタログに対して実行するすべての Git のコマンドに、`-c core.hooksPath=/dev/null -c commit.gpgSign=false` を付ける。`worktree add` の post-checkout、`merge --ff-only` の post-merge、push の pre-push などのフックを動かさないためと、署名の確認の待ちで定期の実行が止まらないようにするためである（R-C1。調査の記録：退去費用の `pre-commit` はカタログでも動いて失敗する）。
  - さらに、`-c core.fsmonitor=false`（fsmonitor のフックを動かさない）と、`-c gc.auto=0 -c maintenance.auto=false`（fetch が誘発する gc が、worktree の登録を prune しないようにする。3章の「SpecDock は prune しない」を守るため）を付ける（I-2 の統括の判断）。push の署名も外す（`-c push.gpgSign=false`）。fetch には `--no-recurse-submodules` を付ける（I-2 の最終品質ゲートの指摘）。この関数は I-2 が置き、I-3 と I-5 はそのまま使う（C6）。
- パスを渡すときは、`--literal-pathspecs` を付け、`--pathspec-from-file=<一時ファイル> --pathspec-file-nul` で渡す。
- この付け方は、1つの関数に集め、ほかの経路で Git を呼ばない。

#### `spec-dock canonical sync` の1回の周期

`--registered` では登録簿のすべてのカタログを、引数なしではこのクローンのカタログを、順に処理する。1つのカタログの失敗で、ほかのカタログを止めてはならない。1つのカタログについて、次の順に行う。

1. **前提を確かめる**：カタログがあり、読めて、`spec-dock/canonical` にいて、マージの途中でないこと。形式の版が書ける版であること。`paused` でないこと。登録簿の git が 2.38 以上であること（足りなければ `CANONICAL_GIT_TOO_OLD`）。満たさなければ、状態に理由を書いて、このカタログを飛ばす。読めない（`Operation not permitted`）ときは、`last_error.code = "OS_ACCESS_DENIED"` と、拒否されたプログラム（spec-dock の Python と、記録した git）を記録する。
2. **GitHub を確かめる**（排他の外）：
   - `git ls-remote --exit-code origin refs/heads/spec-dock/canonical` を行う。終了コード2（ブランチがない）で、基準があれば、`paused: "remote_deleted"` を記録して止まる。基準がなければ、push だけを行う（新しいリポジトリの作成の続き）。2以外の失敗は、接続の失敗として記録し、3と4だけを行う（コミットはローカルに積む）。
   - あれば、`git fetch --no-tags origin +refs/heads/spec-dock/canonical:refs/remotes/origin/spec-dock/canonical` を行う。
   - **書き換えの検出**（R-C5）：基準があり、取得した `origin/spec-dock/canonical`（以下 R）がその子孫でなければ（`git merge-base --is-ancestor`）、`paused: "remote_rewritten"` を記録して止まる。そうでなければ、基準を R にする。
3. **保存**（排他の中）：
   - 最初に、本当のインデックスを HEAD にそろえる（`git reset -q`）。誰かがカタログで `git add` していても、統合が止まらないようにするためである。
   - 変更を `git status --porcelain=v2 -z --untracked-files=all` で集める（`.runtime/` は `.gitignore` で除かれる）。
   - 保存するパスを選ぶ。変更の束にあるパスは、すぐに選ぶ。そのほかは、最後の変更から30秒以上たったものを選ぶ。変わり続けるファイルでも、最初に変更を見つけてから5分たったら選ぶ。削除は更新時刻がないので、最初に見つけた時刻を `pending_since` に記録して数える（R-C2）。
   - 保留を除く（R-C4。下の表）。
   - 一時のインデックス（`GIT_INDEX_FILE=<カタログ>/.runtime/index.tmp`）に `git read-tree HEAD` を読み、選んだパスを `git add -A` で載せ、`git write-tree` と `git commit-tree -p HEAD` でコミットを作り、`git update-ref refs/heads/spec-dock/canonical <新> <旧>` で進める。その後、`git reset -q` で、本当のインデックスをそろえる。
   - メッセージは `spec-dock: save <件数> files (<PC名>)` とする。作者は、利用者の Git の設定のとおりとする。
   - 選んだパスがなければ、コミットしない。
4. **統合**（排他の中）：L を手元の HEAD とする。
   - R がない、または R が L の祖先なら、何もしない。
   - L が R の祖先なら、`git merge --ff-only R` を行う。編集中のファイル（未保存か保留）に当たって失敗したら、何も壊れていない（調査の記録）。当たったパスと理由を `blocking` に記録し、次の周期でもう一度試す。未保存のファイルは遅くとも5分で保存され、次の「分岐」の場合として統合される。保留のファイルが止めているときは、`canonical status` が保留の解き方を示す。
   - 分岐していれば、`git merge-tree --write-tree -z L R` で統合する（作業ツリーに触れない）。
     - 終了コード0なら、出力の1行目のツリーを使う。
     - 終了コード1は競合である。競合したファイルの情報（`<モード> <オブジェクト> <段>\t<パス>`）を使い、一時のインデックスに統合したツリーを読んで、次のように直す。段1は共通の祖先、段2は第1引数の L、段3は第2引数の R である（2026-10-25 に Git 2.54.0 で確認）。
       - 段2と段3の両方があるパス：パスには段3を置き、別名ファイルに段2を置く（先着優先。先に push された版が元の名前に残る）。
       - 段2だけ（R で削除、手元で変更）：段2を置く。段3だけ（手元で削除、R で変更）：段3を置く（変更を残す）。変更と削除の競合では、変更した側の版がすでにツリーに残っている（確認済み）。
       - 名前の変更が絡む競合も、段の規則だけで同じように扱う。
     - 終了コードが2以上（共通の祖先がない、など）なら、`paused: "merge_failed"` と Git の出力を記録して止まる。
     - 直したツリーで、親を L と R の2つにしたコミットを `git commit-tree` で作り、`git merge --ff-only <そのコミット>` で作業ツリーを進める。編集中のファイルに当たって失敗したら、上と同じく待つ。
   - カタログに、競合のマーカーやマージの途中の状態を残してはならない。`rebase` と強制の push は使ってはならない（R-C3）。
   - 別名ファイルを作ったら、状態の `conflicts` に記録する。
5. **push**（排他の外）：L が R より進んでいれば `git push origin HEAD:refs/heads/spec-dock/canonical`（強制しない）。先に進まれて拒否されたら、2からもう一度行う。1つの周期でのやり直しは2回までとする。成功したら、基準を HEAD にする。
6. **記録**：`head`、`remote_contains_head`（HEAD が基準の祖先か同じか）、`unpushed_since`、`consumed_changesets` などを、状態に書く。
7. **構造とダッシュボード**（排他の外）：すべてのカタログの1〜6を終えてから、登録簿の `repository` ごとに1回、`ensure_fresh(repository, cycle)`（2章）を行う。続けて、そのリポジトリのカタログごとに、13章の条件でダッシュボードを作り直す。ここでの失敗（GitHub につながらないなど）は、1〜6の結果を変えない。`probe.json` の `last_error` と、`state.json` の `dashboard.error` に記録する。カタログが一時停止や、読めないために飛ばされていても、7は行う。

#### 別名ファイルの名前

- `<元の名前の本体>.conflict-<PC名>-<UTC の YYYYMMDDTHHMMSSZ>[.<拡張子>]` とし、元と同じディレクトリに置く。
- 拡張子は、ファイル名の最後の `.` より後ろとする。ただし、`.` が先頭にしかないファイル（`.gitignore` など）と、`.` のないファイルは拡張子なしとし、元の名前の全体を本体とする。
- PC名は、ホスト名の最初の `.` より前を小文字にし、`a-z0-9-` 以外を `-` に変え、連続した `-` をまとめ、前後の `-` を除き、32文字までに切ったものとする。空なら `pc` とする。
- 同じ名前がすでにあれば、本体の後に `-2`、`-3` を足す。

#### 保留（R-C4）

| 種類 | 判定 | 解除 |
|---|---|---|
| 大量の削除 | 1回の周期で、`origin: command` の束にない削除が20件以上、または5件以上かつ追跡しているファイルの10%以上 | 意図した削除なら `spec-dock canonical accept --deletions`、意図しない削除なら `spec-dock canonical restore` |
| 秘密情報らしいもの | 中身が次の正規表現のどれかに当たる：`ghp_[A-Za-z0-9]{36}`、`gho_[A-Za-z0-9]{36}`、`github_pat_[A-Za-z0-9_]{82}`、`AKIA[0-9A-Z]{16}`、`-----BEGIN [A-Z ]*PRIVATE KEY-----\r?\n[A-Za-z0-9+/=]` | 中身を直せば、次の周期で自動で外れる。誤判定なら `spec-dock canonical accept <パス>` |
| 大きすぎるファイル | 10 MiB より大きい | 小さくするか、`spec-dock canonical accept <パス>` |

- 秘密情報の判定は、トークンの全体の形に当てる。接頭辞だけでは当てない（この設計書のように、接頭辞を説明する文書を止めないため）。
- 保留したことは、状態とログに書き、`canonical status` が示す。中身はログに書いてはならない。
- `canonical accept <パス>` は、そのパスの今の中身（Git の blob の値）を `<カタログ>/.runtime/accepted.json` に記録する。中身が変われば、許可は効かなくなり、もう一度判定する。`--deletions` は、今保留している削除の一覧を記録する。
- `canonical restore [<パス>…]` は、保留中の削除（またはパスの変更）を、HEAD の内容に戻す。どちらもコミットはしない。対象は、今 `state.json` の保留にあるパスだけで、ほかのパスを指定すると、何も書かずに `CANONICAL_NOT_HELD`（終了コード3）で止まる（保留でない編集中のファイルを HEAD に戻すと、編集が消えるため）。パスなしは、保留中の削除をすべて戻す。戻すときは、カタログの排他の中で保留を取り直し、今も削除で、今も保留に当たるものだけを戻す（I-3 の統括の判断）。
- **大量の削除の数え方**：保留の表の「1回の周期で」は、その周期で保存に選んだ削除ではなく、今の作業ツリーにある、`origin: command` の束にない削除のすべてで数える。周期をまたいで少しずつ選ばれて、閾値をすり抜けるのを防ぐためである（I-3 の統括の判断）。
- **周期の重なり**：同じカタログの周期（定期の実行と、手での `canonical sync`）が重ならないよう、周期の間 `<根>/catalogs/<鍵>/cycle.lock` に `flock(LOCK_EX|LOCK_NB)` をかける。取れなければ、そのカタログを `skipped` で飛ばし、失敗にしない。`canonical remove` と、カタログの移動の処理も、これを取ってから確かめて書く（カタログの排他とは別。I-3 の統括の判断）。

#### 一時停止と再開

- 一時停止（`paused`）は、`remote_rewritten`、`remote_deleted`、`merge_failed` の3つである。止まったカタログは、利用者が判断するまで、保存も push もしない（編集はできる。ファイルは失われない）。
- `spec-dock canonical resume` で再開する。
  - `remote_rewritten` と `merge_failed`：`--adopt-remote` を付けると、基準を今の GitHub の canonical に置き直して再開する。手元にしかないコミットは、次の周期で、通常の統合（別名ファイルの規則）で GitHub のものに重ねる。共通の祖先がない場合は、`resume` が `state.json` に残した一度きりの許可があるときだけ、`merge-tree --allow-unrelated-histories` で統合する（消さない）。
    - どちらの場合も、統合の結果は、親が GitHub の R だけの1つのコミット C にし、手元の L を親にしない。手元のブランチは `git reset --keep C` で C へ移し（編集中のファイルに当たれば何もせずに `blocking` で持ち越す）、push は R からの早送りにする。強制 push の典型の理由は、秘密情報などを履歴から消すことなので、消された古い履歴を送り直さないためである。
    - C を push する前に、R から C への差分に、保留の規則（秘密情報らしいもの、大きすぎるファイル、大量の削除）を当てる。当たれば push せずに保留にする。手元で変えたファイルが GitHub で消されていると、「変更が残る」規則で戻ってくるためである（I-3 の統括の判断）。
  - `remote_deleted`：`--push-local` を付けると、手元の canonical を GitHub に作り直して再開する。
  - どちらも、実行する前に、利用者に何が起きたかを確かめてもらう。手順は、配布する文書 `spec-dock/docs/canonical.md` の「同期が止まったとき」に書く。

### 6. Scope を扱うコマンド（canonical モード）

すべてのコマンドについて、canonical モードでの動きを決める（G7）。「担当」は `plan.md` の Issue である。

- 「読む」の欄の構造（対象、親、祖先、子孫、依存、全体）は、どれも構造のスナップショットから読む（2章）。「一部」「全体」は、スナップショットの中で使う範囲を示すだけで、GitHub への要求の数は変わらない。
- 「書く」に GitHub への書き込みがあるコマンドは、`decision` の新しさでスナップショットを確かめ、判断に使う Issue を読み直してから書く。書いた結果は、すぐにスナップショットに反映する（2章）。
- 「書く」がないコマンドは、`display` の新しさで読む。

| コマンド | 読む | 書く | 今との違い | 担当 |
|---|---|---|---|---|
| `scope create` | 親とその祖先（一部） | Issue の作成（題名、本文の印、種類のラベル）→ 親への sub-issue → 排他の中でディレクトリの公開と変更の束 | `.meta.json` を作らない。日本語の題名を受け付ける（7章）。Issue を作った後に失敗したら、`partial`（終了コード6）と `recovery` に `scope import github <種類> <番号>` を返す | I-5 |
| `scope import github` | Issue と親 | 足りないものだけを足す（種類のラベル、本文の印、親子、ディレクトリ）。何度実行しても同じ | `.meta.json` を作らない | I-5 |
| `scope show`、`scope list` | `show` は一部、`list` は全体 | なし | 題名と状態をスナップショット（GitHub の構造）から示す（R-E4）。ディレクトリの場所と、スナップショットの取得の時刻も示す | I-4 |
| `scope edit` | 対象 | `PATCH` で題名だけ | ファイルは変えない | I-5 |
| `scope move`（新設） | 対象と新しい親（一部） | `--parent` があれば、`POST …/sub_issues` の `replace_parent: true` で付け替える。その後、排他の中でディレクトリを GitHub の親の下へ移し、変更の束を書く | `--parent` がなければ、ディレクトリを今の GitHub の親に合わせるだけ | I-5 |
| `scope close`、`scope reopen` | 子孫か祖先（一部） | 今と同じく状態の `PATCH` | 子孫と祖先を GitHub の親子から求める | I-5 |
| `scope delete` | 対象、子孫、依存 | 種類のラベルを外す、親から外す、`--detach-dependencies` なら依存を外す、`--backup-dir` に写してから、排他の中でディレクトリを消し、削除を変更の束に書く | Issue 自体は閉じも消しもしない | I-5 |
| `dependency list`、`dependency check` | 対象と祖先の依存（一部） | なし（スナップショットだけ） | 入力を blocked by にする。着手の判定の規則は今と同じ。引数なしはスナップショット（`display`）で判定する。`dependency check --source github` は全体を取り直してから判定し、明示した `--source local` だけが `CANONICAL_NOT_APPLICABLE` で止まる（従来モードの既定の値、`--help`、出力は変えない。I-4 の統括の判断） | I-4 |
| `dependency add`、`dependency remove` | 循環の確認のための探索 | `POST` / `DELETE …/dependencies/blocked_by` | `.meta.json` を書かない | I-5 |
| `artifact create`、`artifact import file` | 対象 | 排他の中でファイルを公開し、変更の束を書く | 置き場がカタログになる | I-5 |
| `artifact list`、`artifact show` | 対象とカタログ | なし | 置き場がカタログになる | I-4 |
| `active show` | 選択の記録、対象（一部） | なし | 対象の場所をカタログから求める | I-4 |
| `active set`、`active clear` | 選択の記録 | `spec-dock/active/` のリンク | リンクの先を `../initiatives/<カタログの中の相対パス>` で作る（そのチェックアウトのリンクを通るので、作業用のworktreeでも開く）。今の `active_links` の、`spec-dock/` からの相対パスの求め方を、canonical モードではカタログからの相対パスに変える | I-4 |
| `branch show`、`branch create`、`branch switch` | 対象（一部） | 今と同じブランチの操作 | 既定のブランチ名 `<ID>-<slug>` を GitHub の印から求める。従来の基点のコミットの `.meta.json` の照合はやめ、対象のコミットのツリーに `spec-dock/initiatives` があれば `CANONICAL_BASE_HAS_SPECS` で止まる（定数は I-4 が置き、I-5 の `work start` も使う。I-4 の統括の判断） | I-4 |
| `work start` | 対象と祖先と、それらの依存（一部） | 今と同じブランチの作成と選択の記録 → リンク（3章）→ 作業中の印（ラベルと担当者。失敗は警告だけ） | 基点のコミットのツリーから `.meta.json` を読まない。基点のコミットのツリーに `spec-dock/initiatives` があるとき（移行前のコミット）は、`CANONICAL_BASE_HAS_SPECS` で止まる | I-5（着手の判定の部品は I-4、リンクは I-2） |
| `work finish` | 対象と子孫（一部） | 仕様の保存の確認（下）→ 今と同じく Issue を閉じる → 作業中のラベルを外す（失敗は警告だけ）→ 選択の解除 | 保存を確かめてから閉じる | I-5 |
| `worktree create` | 今と同じ | 今と同じ → リンク（3章） | `--expect-current` を付けたときの選択の解決は I-4 が作る（それまでは、この組み合わせだけ `CANONICAL_NOT_IMPLEMENTED`） | I-2（`--expect-current` は I-4） |
| `worktree list`、`worktree show`、`worktree bootstrap` | 今と同じ | 今と同じ | 選択の表示で、対象の場所をカタログから求める。カタログのworktreeは「カタログ」と示す | I-4 |
| `worktree remove` | 今と同じ | 今と同じ | カタログのworktreeを対象にしたら、`CANONICAL_CATALOG_PROTECTED` で止まる（取り外しは `canonical remove`） | I-4 |
| `workbench copy` | なし | なし | `CANONICAL_WORKBENCH_SHARED` で止まる。どのworktreeからも同じカタログの `.workbench` が見えるので、写す必要がない、と示す | I-4 |
| `workspace sync` | 全体 | なし（スナップショットだけ） | 構造をスナップショットから読む。`--source github` を付けたときは、変わったかの確かめを待たずに全体を取り直す（今の「live GitHub を読む」の意味に合わせる）。明示した `--source local` だけが `CANONICAL_NOT_APPLICABLE` で止まり、引数なしはスナップショットを読む。ダッシュボードは作らない（作るのは定期の同期だけ。13章） | I-4 |
| `workspace validate` | 全体とカタログ | なし | 下の検査を行う。`--ci` は `CANONICAL_NOT_APPLICABLE` で止まり、`canonical check` を案内する | I-4 |
| `workspace doctor` | 今の項目と、`canonical status` と同じ項目 | なし | | I-4 |
| `workspace migrate` | 宣言 | なし | `CANONICAL_NOT_APPLICABLE` で止まる | I-1 |
| `installation init` | 今と同じ | 版4の宣言と配布資産 | 次の1手を、`warnings` の `CANONICAL_NOT_LINKED`（警告には `recovery` の欄がないので、`details.next_step` に `spec-dock canonical link`）で示す。このコードの定数は I-1 が1か所に置き、I-2 はそれを使う | I-1 |
| `installation show`、`update`、`uninstall` | 今と同じ | 今と同じ | 版3と版4の両方を受け付ける。版4で `--expect-current` を付けたときの選択と Scope の解決は I-4 が作る（I-1 の時点では、この組み合わせだけ `CANONICAL_NOT_IMPLEMENTED`） | I-1（`--expect-current` は I-4） |
| `active`、`help`、`completion` の文書 | — | — | 新しいコマンドを載せる | I-9 |

- **`work finish` での保存の確認**（R-C6）：
  1. 排他の中で、Scope のディレクトリの下の未保存の変更を集める（`git --no-optional-locks status`。サンドボックスの中でも `.git` に書かない）。あれば、`origin: finish` の変更の束を書く。
  2. 定期の実行に、すぐの実行を頼む（5章）。
  3. 状態の置き場の `state.json` を2秒ごとに読み、次のすべてを満たすまで待つ。待つのは既定で180秒まで（`--save-timeout`）。
     - 書いた束が `consumed_changesets` にある（束がなければ、この条件はない）。
     - `last_cycle.finished_at` が、待ち始めた時刻より後である。
     - Scope の下に、未保存の変更がない。
     - `remote_contains_head` が真である（HEAD が GitHub の canonical に含まれている。他のPCの push を取り込んだだけで自分は push しなかった場合も、これで確かめられる）。
     - Scope の下に、保留がない。保留があれば、待たずに `CANONICAL_SAVE_HELD` で止まり、保留の種類ごとの解き方（5章）を示す。
  4. 確かめられなければ、Issue を閉じずに `CANONICAL_SAVE_UNCONFIRMED` で止まり、`recovery` に `spec-dock canonical status` を入れる。束を書いた後なので、`partial`（終了コード6。束の書き込みを `succeeded`、Issue を閉じることを `not_attempted` とする）で返す。
- **`workspace validate` の検査**：種類と階層の規則、本文の印と slug、ID の重複、依存の循環、Scope のディレクトリがちょうど1つあること、入れ子と GitHub の親子のずれ（警告。直し方は `scope move <ID>`）、Issue のないディレクトリ、必要な文書（`requirement.md`、`design.md`、`plan.md`、`report.md`）があること、`.meta.json` がないこと、別名ファイル（警告）、Scope でない Issue への依存（警告）。
- **作成時のファイル**：移行の間は、テンプレートの配布資産は変えない（従来モードを変えないため）。canonical モードの作成では、写すときに、前付けの `タイトル:` と `親:` の行を除く。題名と親の正本を GitHub だけにするためである。見出しの題名は、作成時の題名のまま残す。正本ではない。撤去（14章）で、テンプレートの前付けからこの2行を外し、写すときに除く処理を消す。

### 7. 名前（R-E1〜R-E4）

- 題名は、空白を除いて空でなく、改行などの制御文字を含まず、256文字以下であればよい（GitHub の上限）。日本語を含んでよい。
- 題名が今の規則（`^[A-Za-z0-9]+(?: [A-Za-z0-9]+)*$`、`domain/ids.py:11`）に合うときは、今と同じく題名から slug を作る（小文字にして空白をハイフンに）。合わないときは、`--slug` を必須にする（R-E3。ないときは `SLUG_REQUIRED` で止まる）。slug の規則は今と同じ（`^[a-z0-9]+(?:-[a-z0-9]+)*$`）。
- この変更は canonical モードだけに入れる。移行の間、従来モードの作成は、今の規則のままとする（R-A6）。撤去の後は、これが唯一の規則になる。
- 既定のブランチ名は、今と同じ `<ID>-<slug>`。題名を変えても、slug、ディレクトリ名、ブランチ名は変わらない（R-E2）。
- 表示（`scope show`、`scope list`、`workspace sync`、`dependency check` など）とダッシュボード（13章）は、GitHub の題名を使う（R-E4）。

### 8. 既定のブランチの検査（R-F1〜R-F3）

#### `spec-dock canonical check`

- チェックアウトの、指定したコミット（既定は `HEAD`）のツリーを `git ls-tree -r --full-tree` で調べる。カタログ、ネットワーク、GitHub のトークンがなくても動く。
- 調べること：
  1. `spec-dock/initiatives` そのものと、その下のパスがない（ファイル、リンク、gitlink を含む）。
  2. `spec-dock/.canonical` の下のパスがない。
  3. `spec-dock/` の下に `.meta.json` がない。
  4. `spec-dock/workspace.json` があり、版が4で、`writer_protocol` が `specdock.worktree-writer/v1` である（1章の `require_writer` が求める値。古い `specdock.writer/v1` は、書くコマンドが止まるので失敗にする。I-7 は「既知の値」として通したので、版4の宣言を書く I-8 が、この確かめに直してテストを足す。2026-10-26 の統括の判断）。
  5. 配布資産が、このパッケージの資産か、既知の古い版と一致する（今の `installation show` の判定を使う）。`spec-dock/.gitignore` に、3章の無視の3行がある。
  6. `spec-dock/system/spec-dock-version` が、動いている SpecDock の版と同じ（違えば警告）。
- 失敗は1件ずつ、パスと次の1手を付けて返し、`CANONICAL_CHECK_FAILED`（終了コード7）で終わる。宣言の版が3のときも、調べること4の失敗の1件（パスと次の1手付き）として返す。見つけた問題をすべて並べて CI に示すためで、1章の版3の止まり方の例外である（撤去の後も同じ）。

#### ワークフロー

- **見本**：配布資産 `src/spec_dock/assets/spec_dock/docs/ci/spec-dock-check.yml`（利用側では `spec-dock/docs/ci/spec-dock-check.yml`）。R-J1 の各リポジトリには、切り替えのPRで、移行のスクリプトの `cut` が、これを `.github/workflows/` に写す（`branches` には、そのリポジトリの既定のブランチを入れる。taikyohiyou_project は `develop`）。

  ```yaml
  name: SpecDock check
  on:
    pull_request:
    push:
      branches: [main]   # 既定のブランチの名前に合わせる
  permissions:
    contents: read
  jobs:
    spec-dock-check:
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@v4
        - name: Install SpecDock
          run: pipx install "spec-dock @ git+https://github.com/chemitaro/spec-dock@v$(cat spec-dock/system/spec-dock-version)"
        - name: Check
          run: spec-dock canonical check --json
  ```

- **版の固定**：入れる SpecDock の版は、リポジトリの `spec-dock/system/spec-dock-version`（1行の版の文字列）で決まる。このファイルは配布資産で、`installation update` が SpecDock の版に合わせて書き換える。そのため、SpecDock の版を上げても、ワークフローは書き換えなくてよい（R-F2）。資産の中身と `pyproject.toml` の版が同じであることを、単体テストで確かめる。
- **版のタグ**：spec-dock のリポジトリに `.github/workflows/release-tag.yml` を置く。既定のブランチへの push で動き、push の前後（`github.event.before` と `github.sha`）で `pyproject.toml` の版が変わっていて、新しい版が 0.3.0 以上で、タグ `v<版>` がないときだけ、そのコミットにタグを作る（`permissions: contents: write`）。0.2.4 などの過去の版にはタグを作らない。
- **canonical の push では動かない**：GitHub Actions は、push されたコミットのツリーのワークフローを使う。canonical には `.github/` がないので、定期の同期の push では、どのワークフローも動かない。
- **spec-dock での検査**：spec-dock 自身は、PRのコードで検査する。`.github/scripts/specdock-ci-check.sh` を新しく作る（今の `specdock-ci-validate.sh` と同じ方法でソースから wheel を作り、最後に `spec-dock --project <対象> canonical check --json` を実行する）。`.github/workflows/spec-dock-check.yml` はそれを呼ぶ。今の `ci.yml` の `workspace validate --ci` の手順は外す。スクリプトは I-7 で作り、ワークフローの追加と `ci.yml` の変更は、仕様を既定のブランチから外す切り替えのPRで入れる（それまでは、既定のブランチに仕様があり、検査が失敗するため）。
- **マージの条件**：検査は、既存のCIと同じく、PRをきっかけに動き、結果をPRに表示する。GitHub の必須の検査（ブランチの保護、ルールセット）は設定しない。人は通過を確かめてからマージし、エージェントは通過していないPRを、マージできる状態として渡さない（R-F3）。

### 9. ツールの設定（R-B6、R-H3）

- 作業用のworktreeから仕様を読み書きするには、ツールごとに1行の設定が要る（調査の記録で確認済み）。利用者が1回だけ手で足す。SpecDock は、`installation init` と `installation update` を含めて、設定のファイルを書き換えてはならない（約束4。2026-10-25 に利用者が了承。自動で書くと、利用者の設定を壊す危険と、ツールの設定の形式の変化に追従する保守が生じるため）。
- 示す1行（`<カタログ>` は、そのクローンのカタログの絶対パス）：
  - Claude Code：ユーザーの設定 `~/.claude/settings.json` の `permissions.additionalDirectories` に `"<カタログ>"` を加える。

    ```json
    { "permissions": { "additionalDirectories": ["<カタログ>"] } }
    ```

  - Codex：`~/.codex/config.toml` の `[sandbox_workspace_write]` の `writable_roots` に `"<カタログ>"` を加える。

    ```toml
    [sandbox_workspace_write]
    writable_roots = ["<カタログ>"]
    ```

- 判定：
  - Codex は、環境変数 `CODEX_SANDBOX` があるときに、`os.access(<カタログ>, W_OK)` で書けるかを判定する（確認済み）。書けなければ、上の1行を示す。
  - Claude Code の権限は、ツールの中で判定され、SpecDock のプロセスからは確かめられない。そこで、作業用のworktreeで `canonical link` と `canonical status` を実行したときは、`~/.claude/settings.json`、`<チェックアウト>/.claude/settings.json`、`<チェックアウト>/.claude/settings.local.json` を読むだけ読んで、`additionalDirectories` にカタログ（またはその親）があるかを見る。なければ、上の1行を示す。判定できないときは、判定できないと示す。
  - mainのチェックアウトの中で動くセッションには、設定は要らない（カタログが作業ディレクトリの中にある）。そのため、mainのチェックアウトでは、環境変数 `CLAUDECODE`（Claude Code のシェルでは `1`。2026-10-25 に確認）があっても判定せず、1行も示さない。`CLAUDECODE` の有無は、`tools` の項目に示すだけにする（I-2 の統括の判断）。
- カタログはクローンごとにあるので、R-J1 の5つのリポジトリを移すと、足す値は5つになる。どちらのツールも配列なので、1行の配列に並べればよい。`canonical status` は、そのクローンのカタログが足りないことだけを示す。使い方の文書（I-9）には、5つを並べた例を書く。
  - Claude Code の隔離セッション（`--worktree`）からの書き込みは、設定では通らない（確認済み）。読むだけにする。
- Codex のサンドボックスの中からは、`.git` と登録簿に書けないため、カタログの作成、除外の追加、定期の実行の登録はできない。これらが要るときは、`canonical link` が `CANONICAL_SANDBOX_DENIED` で止まり、サンドボックスの外で実行するよう示す（3章）。
- 確かめていないこと：Claude Code の1行を、`--settings` ではなくユーザーの設定ファイルに書いたときの動き。担当の Issue で、利用者の設定を変えずに、一時の `HOME` か `--settings` のファイルで確かめる。

### 10. エージェント向けの規則（R-H1、R-H2）

配布するスキル（`src/spec_dock/assets/install_root/.agents/skills/spec-dock/SKILL.md`）と、spec-dock の `AGENTS.md` に、次の節をそのまま置く（表現は整えてよいが、項目を減らしてはならない）。

```markdown
## 仕様の扱い（canonical モード）

`spec-dock/workspace.json` の `schema_version` が 4 のリポジトリでは、次に従う。3 のリポジトリでは、今までどおり、仕様もコードと一緒にコミットする。

- 仕様は `spec-dock/initiatives/` にある。普通のファイルとして読み書きする。
- 仕様は Git で扱わない（`git add`、`commit`、`stash`、`reset`、`checkout`、`clean` を仕様に使わない）。保存と共有は、1〜2分のうちに自動で行われる。
- 仕様が見えない、またはリンクの異常を示されたときは、`spec-dock canonical link` を実行する。サンドボックスの中で拒否されたら、利用者に、普通の端末での実行を頼む。
- 読み書きを拒否されたときは、`spec-dock canonical status` が示す1行の設定を、利用者に伝える。自分でツールの設定を変えない。
- 検索では、パスを明示する（`rg 語 spec-dock/initiatives/`、コードと一緒なら `rg 語 . spec-dock/initiatives/`）。
- 構造（作成、親子、依存、状態、題名）は、SpecDock のコマンドだけで変える。ディレクトリを手で動かさない。
- `*.conflict-*` のファイルがあれば、中身を元のファイルに統合してから、そのファイルを消す。
- Claude Code の隔離セッション（`--worktree`）では、仕様を読むだけにする。
- 作業を終えるときは `spec-dock work finish` を使う。保存が確かめられるまで待つ。
- リンクを消すときは `rm spec-dock/initiatives` と書く。末尾に `/` を付けない。mainのチェックアウトで `git clean -ff` を使わない。
```

- SpecDock のエラーは、`recovery`（`Recovery.commands` か `RecoveryInstructions.instructions`）に、次に実行するコマンドか足す設定を必ず入れる（R-H2）。12章の表のエラーには、すべて次の1手がある。
- 撤去（14章）で、節の最初の段落の「3 のリポジトリでは、今までどおり…」の文を消し、見出しから「（canonical モード）」を外す。

### 11. 移行のスクリプト（R-G1〜R-G6）

- 置き場は `scripts/migrate-to-canonical/`（spec-dock のリポジトリのルート。パッケージには入れない）。`migrate.py`（標準ライブラリと、`git` と `gh` のコマンドだけを使う1つのファイル）と `README.md`（各リポジトリの移行で使う短い手順書）を置く。撤去（14章）で消す。消した後も、版のタグ `v0.3.0` に残る。
- 対象は R-J1 のリポジトリである。スクリプトは spec-dock にだけ置き、ほかのリポジトリには写さない。対象は `--project <対象の mainのチェックアウト>` で選ぶ。既定のブランチは、対象の `origin/HEAD` から求める（taikyohiyou_project は `develop`）。`main` を決め打ちしてはならない。
- 作業の記録は `scripts/migrate-to-canonical/.state/<owner>-<repo>/`（Git では無視）に、リポジトリごとに置く。取り消しの一覧（`undo.jsonl`）と、ID の置き換えの表（`idmap.json`）である。
- サブコマンド。どれも、既定では予定を表示するだけで、`--apply` を付けたときだけ書く。何度実行しても同じ結果になる。

| サブコマンド | すること |
|---|---|
| `plan` | `.meta.json` と GitHub を読み、登録の予定と、データの異常（循環する依存、種類の規則の違反、閉じた親の下の開いた子、ID と番号の不一致、GitHub との題名の食い違い、ローカルの Scope）を一覧にする（R-G4）。あわせて、SpecDock を呼ぶ今のCIの手順（`.github/` の下で `spec-dock` か `specdock` を含む行）と、作業用のworktreeごとの、既定のブランチにない仕様の変更の有無を一覧にする。読むだけなので、どの時点でも実行してよい |
| `register` | ラベルの作成、種類のラベル、本文の印、sub-issue、blocked by を、足すだけで登録する。題名は変えない（GitHub の題名を正とする）。ローカルの Scope の扱い（下）で新しい Issue を作ったら、`idmap.json` に記録する。リポジトリのファイルは変えない。今の CLI での運用は壊れない（R-G3） |
| `verify` | `.meta.json` の構造（`idmap.json` で置き換えた後）と、GitHub の構造が一致するかを比べる（AC-04） |
| `build-canonical` | 使い捨てのクローンで `git subtree split --prefix=spec-dock/initiatives` を行い、`idmap.json` に従ってディレクトリの名前を変え、管理ファイルを足し、`.meta.json` を消すコミットを作って、`spec-dock/canonical` として push する。本物の `.git` に作業用のファイルを残さない（調査の記録） |
| `cut` | 既定のブランチから、仕様のツリーを外すブランチを作って push する。宣言を版4にし、`spec-dock-check.yml` を足す（`branches` には、そのリポジトリの既定のブランチを入れる）。今のCIの SpecDock の手順は書き換えず、一覧を示す（下の「今のCIの手順」）。PRは統括のエージェントが作り、人がマージする |
| `move-local <チェックアウト>` | そのチェックアウトの `spec-dock/initiatives/` の下の、追跡されていないファイルと無視されたファイル（`.workbench` など）を、カタログの同じ相対パス（`idmap.json` で置き換えた後）へ移す。カタログに同じ名前があれば上書きせず、`.local-<PC名>` を付けた名前にする。移した後、空になったディレクトリを消し、`canonical link` がリンクを置けるようにする |
| `adopt-worktree <チェックアウト>` | 移行前のブランチのチェックアウトの仕様を、canonical に取り込む（R-G5。下の方法） |
| `undo` | `undo.jsonl` に従って、`register` が足したものを外す |
| `export-legacy` | 戻すときに使う。既定のブランチから新しいブランチを作り、`spec-dock/initiatives` にカタログの内容を置き、GitHub の構造から `.meta.json`（schema 3）を作り直し、宣言を版3に戻し、`spec-dock-check.yml` を外す。切り替えのPRで外した今のCIの手順は、そのPRの差分から手で戻す。PRは人がマージする |

- **I-8 の統括の判断**（2026-10-26。詳しくは `iss-00435-canonical-migration-script/plan.md`）：
  - `.meta.json` は、作業ツリーではなく `origin/<既定のブランチ>` のコミットから読む。mainのチェックアウトの HEAD と違えば、`plan` が警告する。予行演習の bare の origin では `--repo OWNER/NAME` を渡し、本物では origin の URL から求めた値と一致しなければ止まる。
  - `register` は足すだけである。GitHub に違う種類のラベル、違う slug の印、違う親があれば、上書きせずに異常として残し、`verify` は不一致にする。ローカルでない ID の番号の不一致は、`build-canonical` を止める。
  - `move-local` は、カタログがなければ、`canonical link` の手順3と同じ git の操作（C6 の `-c`、同じ場所、追跡、lock の理由）でカタログを作ってから移す。origin に canonical がなく、移すファイルがあれば止まる。
  - `adopt-worktree --apply` は、使い捨てのクローンで統合して早送りで push し、push が届いて中身が一致したことを確かめてから、B の仕様を外すコミットと、取り込んだ追跡外のファイルの削除を行う（分岐点と同じ中身のファイルは、取り込むものがないので一致とする）。消す予定の一覧は、`--apply` なしの出力に出す。
  - `export-legacy` の `.meta.json` は、構造の項目を GitHub から作り、ほかの項目は切り替え前のコミットのものを引き継ぐ。宣言は切り替え前のバイト列に戻す。
  - `undo` は、作った Issue を `not_planned` で閉じて種類のラベルを外し、`register` が作ったと記録したラベルの定義だけを消す。作業の記録がないときは、次の1手を付けて止まる（I-9 が直す）。
- **ローカルの Scope と番号の不一致**：`init-local-00002`（#39 に結び付く）と `init-local-00003`（#31 に結び付く。#31 は題名が別物で閉じている）は、`plan` が異常として示す。結び付いた Issue の題名が `.meta.json` の題名と同じなら、その番号の ID に置き換える。違えば、`register` が `.meta.json` の題名で新しい Initiative の Issue を作り、その番号の ID に置き換える。置き換えは `idmap.json` に記録し、ディレクトリの名前は `build-canonical` と `move-local` と `adopt-worktree` だけが変える。どちらにするかは `plan` の出力に書き、`--apply` の前に確かめられるようにする。
- **速さ**：書き込みは1つずつ送り、間を1秒以上あけ、1分に80回、1時間に500回を超えない（目安の制限）。レート制限の応答では、2章の規則で待つ（書き込みでも、スクリプトは待って続けてよい。再開できるため）。spec-dock では約620回で、1.5時間ほどかかる見込み。途中で止まっても、`undo.jsonl` と GitHub の今の状態から、続きを判断して再開する（R-G2）。
- **凍結の後にもう一度**：`register` と `verify` は、切り替えの前に済ませてよいが、凍結（仕様の編集の停止）の後に、もう一度 `register --apply` と `verify` を行う。その間に変わった構造を拾うためである。
- **移行前のチェックアウトの取り込み**（`adopt-worktree`）：
  1. そのチェックアウトのブランチ B と既定のブランチの分岐点を M とする。`build-canonical` が作った canonical のコミットのうち、ツリーが `M:spec-dock/initiatives`（`idmap.json` の置き換えの後）と同じもの C を探す（subtree split のコミットは、元のコミットの `spec-dock/initiatives` と同じツリーを持つ）。
  2. 作業ツリーの今の状態（追跡しているファイルの変更と、追跡されていない新しいファイル。無視されたファイルは除く）を、一時のインデックスで木にし、`spec-dock/initiatives` の部分木から `.meta.json` を除き、`idmap.json` の置き換えをしたツリーで、親を C とするコミット X を作る。コミットされていない変更も取り込むためである。
  3. X を canonical に3者マージで取り込む（競合は5章の規則と同じに解く）。
  4. B の `.meta.json` を M のものと比べ、構造の違い（親、依存、題名の変更）を一覧にする。これらは自動では登録しない。一覧を見て、SpecDock のコマンドで登録し直す。
  5. 無視されたファイルは `move-local` で移す。
  6. B から仕様のツリーを外すコミットを作り、既定のブランチを B に取り込めば、PRは仕様を含まずにマージできる（調査の記録で確認済み）。
- **今のCIの手順**（R-J5）：各リポジトリの今のCIの SpecDock の手順は、形がそれぞれ違う（Current の表。spec-dock はシェルスクリプトを経由して呼ぶ）。そのため、`cut` は自動では書き換えない。`plan` と `cut` が、SpecDock を呼ぶ手順を一覧にし、統括のエージェントが、切り替えのブランチに、その手順を外すコミットを手で足す。SpecDock を入れるだけの手順（`pip install`、`uv tool install` など）も、あわせて外す。ほかの手順は変えない。切り替えのPRのCI（そのリポジトリの既存のテストと、新しい検査のワークフロー）が通ることで確かめる。
- **0.3.0 の配布資産**：`canonical check` は、配布資産と、`spec-dock/.gitignore` の無視の3行と、版のファイルを確かめる（8章）。そのため、各リポジトリでは、切り替えより前に、`spec-dock installation update` で配布資産を 0.3.0 に上げ、通常のPRでマージしておく。従来モードのままなので、今の運用は変わらない（「移行・互換性・rollback」の組み合わせの表）。今のCIは古い SpecDock のコミットに固定して `workspace validate` を実行しているので、古い版が 0.3.0 の配布資産を知らずに失敗するおそれがある。同じPRで、CIが入れる SpecDock をタグ `v0.3.0` に上げる（0.3.0 は、版3のリポジトリを従来モードで検査する）。spec-dock は、CIがソースから wheel を作るので、この変更は要らない。
- **予行演習**（R-J3）：各リポジトリの切り替えの前に、次の形で、切り替えと戻しの両方を通す。本物のリポジトリ、GitHub への書き込み、利用者の定期の実行と状態の置き場に触れない。
  1. 対象の mainのチェックアウトから、内蔵のディスクの一時ディレクトリに、使い捨てのクローンを作る。GitHub の代わりに、同じ一時ディレクトリに bare のリポジトリを作り、使い捨てのクローンの `origin` にする。
  2. 環境変数 `XDG_STATE_HOME` を一時ディレクトリにする。スクリプトの作業の記録も、一時ディレクトリに置く（`--state-dir`）。
  3. `plan` と `verify` は、本物の GitHub を読むだけで行う（`register` は本物で済ませてある）。`build-canonical --apply` と `cut --apply` は、bare のリポジトリへ push する。
  4. 切り替えのブランチを、使い捨てのクローンの既定のブランチに取り込み（PRのマージの代わり）、`spec-dock canonical link --no-schedule` と `spec-dock canonical sync` を実行して、仕様が読み書きでき、`canonical check` が通ることを確かめる。
  5. `export-legacy --apply` で戻し、作られた `.meta.json` が、移行前のものと `revision` と `lifecycle` のほかは一致することを確かめる。
  6. 結果を、その Issue の報告書に書き、一時ディレクトリを消す。

### 12. コマンドの一覧と出力の契約

新しく足すコマンド（`cli/catalog.py` の `LEAF_PATHS`、`HELP_EFFECTS`、`--help` の Target/Reads/Writes/Does not の節を、今のコマンドと同じ形で書く）。コマンドの数は、0.3.0 で 44 から 53 になり、撤去（14章）で `workspace migrate` と `workbench copy` を消して 51 になる。

| コマンド | 書くもの | 効果の要約（`HELP_EFFECTS`） | 担当 |
|---|---|---|---|
| `canonical link` | カタログ、lock、除外、リンク、登録簿、定期の実行、基準 | Find or create this clone's catalog, link this checkout, and register periodic sync. | I-2、I-3 |
| `canonical status` | なし | Read catalog, link, access, tool settings and sync state; no changes. | I-2、I-3 |
| `canonical sync` | カタログのコミット、push、状態、構造のスナップショット、ダッシュボード | Save, merge and push the catalog once; `--registered` processes every registered catalog; `--loop` keeps running as the resident runner where systemd is unavailable. | I-3（スナップショットの更新は I-1 の部品、ダッシュボードは I-11） |
| `canonical accept` | `accepted.json` | Allow held changes to be saved by the next sync. | I-3 |
| `canonical restore` | カタログの作業ツリー | Restore held deletions or paths from the catalog HEAD; no commit. | I-3 |
| `canonical resume` | 状態の `paused` と基準 | Resume a paused catalog after the user decided how to treat the remote. | I-3 |
| `canonical check` | なし | Check that a commit of the code tree holds no specs and has intact SpecDock files; for CI. | I-7 |
| `canonical remove` | リンク、カタログ、除外、登録簿、定期の実行 | Remove this clone's catalog, links and sync registration after confirming nothing is unsaved. | I-3 |
| `scope move` | GitHub の親子、カタログのディレクトリ | Change or re-align a Scope parent in GitHub and move its directory to match. | I-5 |

- **名前の判断**：保存と同期の入口は `canonical sync` とする。今の `workspace sync`（Scope の状態とworktreeの選択を観測する、読むだけのコマンド）とは別のグループに置き、`--help` の最初の行で違いを示す。エージェント向けの規則は「保存は自動」とし、どちらのコマンドも日常では使わせない。
- **結果の状態**：今の `OperationResult` の規則に従う。
  - 書く前の確かめで止まるときは `failed`（効果なし）。そのために、書くコマンドは、止まる条件をすべて書く前に確かめる。
  - 書いた後に止まるときは `partial`（終了コード6）で、効果ごとに `succeeded`、`unknown`、`not_attempted` を示す。
  - `canonical sync --registered` は、カタログごとの結果を `data.catalogs` に入れる。すべて成功か変化なしなら `succeeded` か `unchanged`、1つでも失敗し、どこかで効果があれば `partial`（終了コード6）、効果がなければ `failed`（終了コード3）とする。
- **引数**：`canonical sync` は、`--registered`、`--state-root <パス>`、`--loop`（常駐。`--registered` と一緒にだけ使える）、`--detach`（`--loop` を切り離して起動して、すぐに終わる）を受け付ける。`canonical link` は `--no-schedule`（3章）を受け付ける。
- **JSON**：`canonical status --json` の `data` は、3章の表の項目をキーに持つ。`canonical sync --json` の `data.catalogs[]` は、`catalog`、`saved_commit`、`merged`、`pushed`、`conflicts`、`holds`、`blocking`、`skipped_reason`、`paused` を持ち、`data.repositories[]` は、`repository`、`probe`（`unchanged`、`changed`、`failed`）、`refreshed`、`dashboards_written` を持つ。
- 構造を示すコマンドの JSON は、`data` に `snapshot`（`fetched_at`、`stale`）を持つ。
- **エラーのコード**（どれも `recovery` に次の1手を入れる）：

| コード | 終了コード | 次の1手 |
|---|---|---|
| `CANONICAL_NOT_MIGRATED` | 3 | 0.3.0 では、移行の手順書（`scripts/migrate-to-canonical/README.md`）を見る（宣言の版が3のとき。`canonical link` では、GitHub に canonical がなく既定のブランチに仕様があるときも）。撤去の後の 0.4.0 では、どのコマンドも版3の宣言を読むとこれで止まり、「SpecDock 0.3.0 を入れ直し、版のタグ `v0.3.0` の `scripts/migrate-to-canonical/README.md` に従って移す」を示す |
| `CANONICAL_NOT_APPLICABLE` | 3 | 示した代わりのコマンドを使う（`canonical check` など） |
| `CANONICAL_UNSUPPORTED_LAYOUT` | 3 | mainのチェックアウトのある構成で使う |
| `CANONICAL_GIT_TOO_OLD` | 3 | Git 2.38 以上を入れ、`spec-dock canonical link` をもう一度実行する（登録簿の git を入れ替えるため） |
| `CANONICAL_FOREIGN_CHECKOUT` | 3 | 保存と同期はホストで行われる。コンテナでは仕様のファイルを読み書きするだけにするか、コンテナの中でクローンして `spec-dock canonical link` |
| `CANONICAL_NOT_LINKED` | 3 | `spec-dock canonical link` |
| `CANONICAL_PATH_OCCUPIED`、`CANONICAL_LINK_OCCUPIED` | 3 | 示したパスの中身を確かめて退避してから `spec-dock canonical link`（SpecDock は消さない）。`spec-dock/canonical` のworktreeの登録だけが残っているときは、確かめてから `git worktree remove` か `git worktree prune` を自分で実行し、もう一度 `spec-dock canonical link` |
| `CANONICAL_SANDBOX_DENIED` | 3 | サンドボックスの外（普通の端末）で同じコマンドを実行する |
| `CANONICAL_LOCK_BUSY` | 3 | しばらく待って同じコマンドを実行する |
| `CANONICAL_FORMAT_UNSUPPORTED` | 3 | SpecDock を更新する |
| `CANONICAL_UNSAVED_CHANGES` | 3 | `spec-dock canonical status` で確かめ、保存を待つ |
| `CANONICAL_IGNORED_FILES_PRESENT` | 3 | 示したファイルを退避してから同じコマンドを実行する |
| `CANONICAL_SAVE_HELD` | 3 | 保留の種類ごとの解き方（`canonical accept`、`canonical restore`、中身の修正） |
| `CANONICAL_SAVE_UNCONFIRMED` | 6（partial） | `spec-dock canonical status` |
| `CANONICAL_PAUSED` | 3 | `spec-dock canonical status` で理由を見て、文書の「同期が止まったとき」に従う |
| `CANONICAL_BASE_HAS_SPECS` | 3 | 切り替えの後のコミットを基点にする |
| `CANONICAL_CATALOG_PROTECTED` | 3 | 取り外すなら `spec-dock canonical remove` |
| `CANONICAL_WORKBENCH_SHARED` | 3 | 何もしなくてよい（どのworktreeからも見える） |
| `CANONICAL_CHECK_FAILED` | 7 | 失敗ごとに示したパスを、既定のブランチから外す |
| `GITHUB_STRUCTURE_INVALID` | 7 | 示した Issue のラベル、印、親子を直す（`scope move` など） |
| `GITHUB_RATE_LIMITED` | 5 | 示した時刻の後に同じコマンドを実行する |
| `GITHUB_UNAVAILABLE` | 5 | 接続と `gh auth status` を確かめる |
| `GITHUB_ACCESS_DENIED`、`GITHUB_REQUEST_REJECTED`、`GITHUB_RESPONSE_INVALID` | 今と同じ | 今の `github_lifecycle` と同じ分類と次の1手（権限と `gh auth status`、示した GitHub の応答を確かめる） |
| `GITHUB_EFFECT_UNKNOWN`、`GITHUB_CREATE_IDENTITY_UNKNOWN` | 6 | GitHub の今の状態を確かめてから、`recovery` の手順に従う（作成なら `scope import github`） |
| `CANONICAL_NOT_IMPLEMENTED` | 3 | SpecDock 0.3.0 を待つ（I-1〜I-8 の途中だけ。I-9 で残っていないことを確かめる） |
| `GITHUB_SNAPSHOT_STALE` | —（警告） | 表示は取得の時刻の時点のもの。つながったら、次の表示か定期の同期で新しくなる |
| `CANONICAL_TOOL_SETTING_MISSING`、`CANONICAL_TOOL_SETTING_UNKNOWN` | —（警告） | 9章の1行を足す。判定できないときは、ツールの設定を自分で確かめる（I-2） |
| `CANONICAL_IGNORE_RULES_MISSING` | —（警告） | 3章の無視の3行を足す（`spec-dock installation update` か `spec-dock canonical link`）（I-2） |
| `CANONICAL_MAIN_MOVED` | —（警告） | 各作業用のworktreeで `spec-dock canonical link`（そのworktreeも動かしたなら、先にmainで `git worktree repair <パス>`）（I-2） |
| `CANONICAL_REMOTE_MISSING` | —（警告） | GitHub の `spec-dock/canonical` が消されていないか確かめ、`spec-dock canonical status` の案内に従う（I-2） |
| `CANONICAL_MAIN_NOT_MIGRATED` | —（警告） | mainのチェックアウトで移行後のコミットをチェックアウトしてから `spec-dock canonical link`（I-2。`canonical status` の `link` の項目でも示す） |
| `CANONICAL_INSIDE_CATALOG` | 3 | チェックアウトのルートで実行するか、`--project <チェックアウト>` を付ける（I-2） |
| `CANONICAL_NOT_HELD`、`CANONICAL_NOT_RESTORABLE`、`CANONICAL_PATH_NOT_FOUND`、`CANONICAL_REGISTRY_UNREADABLE` | 3 | I-3 の `iss-00430-canonical-periodic-sync/design.md` 14章の表の次の1手（I-3） |
| `CANONICAL_STATE_ROOT_MISMATCH` | 3（`link`）／警告（`status`） | そのジョブの状態の置き場（リンクしたときの `XDG_STATE_HOME`）でコマンドを実行するか、そこに登録したカタログを先に `spec-dock canonical remove` する（I-3） |
| `CANONICAL_SCHEDULER_FAILED`、`CANONICAL_REMOVE_FAILED` | 6（partial） | I-3 の design.md 14章の表の次の1手（I-3） |
| `CANONICAL_SYNC_NOT_SCHEDULED`、`CANONICAL_SYNC_NOT_CONFIRMED`、`CANONICAL_PUSH_AUTH_FAILED`、`CANONICAL_LINGER_DISABLED`、`CANONICAL_RUNNER_RESTART`、`CANONICAL_RUNNER_STOPPED`、`CANONICAL_UNPUSHED_STALE`、`CANONICAL_SYNC_BLOCKED`、`CANONICAL_SYNC_FAILED` | —（警告） | I-3 の design.md 14章の表の次の1手。`canonical status` の `sync` の項目での順も、同じ設計書のとおり（I-3） |
| `CANONICAL_STATE_UNREADABLE`、`CANONICAL_GIT_IN_PROGRESS`、`SYNC_FAILED` | —（`state.json` の `last_error`、`data.catalogs[].error`） | I-3 の design.md 14章の表の次の1手（I-3） |
- `CANONICAL_PAUSED` は、`resume` の引数の誤りでは終了コード3、`canonical status` では警告として使う。`CANONICAL_SAVE_HELD` も、`canonical status` では警告として使う（`work finish` の終了コード3は I-5）。
| `DEPENDENCY_NOT_IN_SNAPSHOT`、`READINESS_UNKNOWN`、`DEPENDENCY_NOT_SCOPE`、`SCOPE_DIRECTORY_SLUG_MISMATCH`、`SCOPE_DIRECTORY_DUPLICATE`、`SCOPE_DIRECTORY_MISSING`、`SCOPE_DIRECTORY_MISPLACED`、`SCOPE_ISSUE_MISSING`、`SCOPE_DOCUMENT_MISSING`、`SCOPE_METADATA_PRESENT`、`CANONICAL_CONFLICT_COPY` | —（`workspace validate` の findings と、読むコマンドの警告） | I-4 の `iss-00431-canonical-scope-read/design.md` の表の次の1手（I-4） |
| `SLUG_REQUIRED` | 3 | `--slug <英小文字とハイフン>` を付ける |

### 13. ダッシュボード（R-E5、AC-17）

今までと同じ Markdown と PlantUML のダッシュボードを、canonical モードで、構造のスナップショットから作り直す。これは、つなぎである。HTML のダッシュボードは epic-00427（#427）で作り、その段階1を出した後に、この5つのファイルの生成を撤去する（epic-00427 の R-H1。2026-10-25 に、ダッシュボードを epic-00425 から epic-00427 に分けた）。

- **作るファイル**：mainのチェックアウトの `spec-dock/` の、次の5つ。どれも、配布資産の `spec-dock/.gitignore` で、すでに無視されている（確認済み）。

| ファイル | 中身 | 描く関数（今のコード） |
|---|---|---|
| `dashboard.md` | 着手できる Issue の集計と、Doing、Ready、Blocked、Unknown の一覧（終わったものは除く） | `presentation/markdown.py` の `_render_dashboard_md` |
| `tree.puml` | Initiative、Epic、Issue の入れ子の図で、終わっていないものだけ。状態ごとの色（READY、BLOCKED、DOING、DONE、UNKNOWN） | `presentation/puml.py` の `_render_tree_ready_board_puml`（`todo_only=True`） |
| `tree-all.puml` | 同じ図で、終わったものも含める | 同じ関数（`todo_only=False`） |
| `deps-issues.puml` | Issue どうしの依存の図 | `_render_deps_issues_puml` |
| `deps-raw.puml` | 宣言された依存を、祖先を含めてそのまま示す図 | `_render_deps_raw_puml` |

- **形**：今までと同じにする。見本は、spec-dock のmainのチェックアウトの `spec-dock/` にある、2026-09-21 に作られた5つのファイルである（切り替えの後は、定期の同期が上書きする。I-11 の担当は、始めるときに、これを写してテストの見本にする）。違いは次の3つだけとする。
  - 題名は、スナップショットの GitHub の題名（日本語を含む）を使う。PlantUML の文字列に入れるときは、今の関数の扱い（引用符と改行の扱い）に従う。
  - 作業中（DOING）は、今の選択の記録ではなく、GitHub の作業中のラベル（`spec-dock:in-progress`）で決める。どのPCで作業中のものも示される。
  - `dashboard.md` の「Observability」の行は、`.agent/index.json` の代わりに、構造のスナップショットのパスを示す。
- **状態の決め方**：終わった（DONE）は閉じた Issue。作業中（DOING）は開いていて作業中のラベルがあるもの。止められている（BLOCKED）と着手できる（READY）は、`dependency check` と同じ着手の判定（I-4 の部品。Scope でない Issue への依存は、開いていれば止められている）で決める。不明（UNKNOWN）は、スナップショットの異常に挙がったもの。
  - 着手の判定の部品（I-4 の `domain/canonical_readiness.py`。I-5、I-11、epic-00427 が使う）の状態の優先は、DONE（閉じた。理由を問わない）> UNKNOWN（対象、祖先、前提に異常、別のリポジトリの親・子・依存、スナップショットにない依存先）> DOING（作業中のラベル）> BLOCKED > READY である。`ready`（着手できるか）は DOING を見ない。結果は、止めている理由（ブロッカーの Scope と、Scope でない Issue の番号）と、UNKNOWN の理由（異常のコード）の一覧を持つ（I-4 の統括の判断）。Epic と Initiative の配下からの集計は、epic-00427 が行う。
- **作り方**：`application/canonical_dashboard.py` に、スナップショットから、今の描く関数が受け取る辞書（`presentation/json_state.py` の `_build_state_payloads`、`_build_deps_issues_v2_payload`、`_build_deps_raw_payload` が作るものと同じ形）を作る部品を置き、描く関数をそのまま呼ぶ。描く関数は、従来モードのどこからも呼ばれていないので、直す必要が出たら直してよいが、出力の形は変えない。
- **作り直す時**：定期の同期の周期の手順7（5章）で、カタログごとに、スナップショットの `issues` と `external` の中身の SHA-256 が、`state.json` の `dashboard.input_hash` と違うとき、または5つのファイルのどれかがないときだけ作る。構造が変わらない周期では書かない。ほかのコマンド（`workspace sync` を含む）は作らない（約束3）。
- **書き方**：ファイルごとに、同じディレクトリの一時ファイルに書いてから `rename` する。書く場所にディレクトリかシンボリックリンクがあれば、そのファイルは書かずに、`dashboard.error` に記録する。作業用のworktreeには作らない（1つのクローンの構造は1つのため）。
- **従来モード**：作らない（今のまま。R-A6）。

### 14. 撤去（R-J6〜R-J8）

R-J1 のすべてのリポジトリを移した後に、従来モードのコードを消し、canonical モードだけを持つ 0.4.0 を出す。担当は I-13 である。

- **時期**：I-12（残りの4つの切り替え）の後の3日間の運用で、戻す必要がないことを、利用者が確かめた後に始める。
- **消すものの決め方**：0.4.0 の `dispatch()` から到達できないコードを消す。ファイルの一覧を正本にしない（canonical の処理が、今のモジュールの部品を使っていることがあるため）。目安として、2026-10-25 の時点で `.meta.json` を読み書きするか、それに頼る木の読み込みを使うファイルは、`src/spec_dock/runtime/` の下に34ある（代表は `infra/scope_metadata.py`、`infra/scope_tree.py`、`infra/fs_repo.py`、`infra/deps_reader.py`、`application/scope_query.py`、`application/start_snapshot.py`、`application/direct_scope_*.py`、`direct_finish.py`、`direct_dependencies.py`、`direct_migration.py`）。canonical の処理と同じファイルにある部分（`direct_worktrees.py`、`work_start.py` など）は、従来の経路だけを消す。
- **消すもの**：
  1. `dispatch()` のモードの振り分けと、従来の処理。`.meta.json` の読み書き。
  2. 宣言の版3の受け付け。`read_workspace_declaration` は版4だけを受け付け、版3を読むと、すべてのコマンドが `CANONICAL_NOT_MIGRATED`（12章の 0.4.0 の次の1手）で止まる（`canonical check` だけは、8章のとおり失敗の1件として返す）。版5以上は、今と同じく `PRECONDITION_FAILED` で止まる。
  3. canonical モードで拒否するだけのコマンドと引数。コマンドの `workspace migrate` と `workbench copy`、引数の `workspace validate --ci`、`workspace sync --source local`、`dependency check --source local`。使われなくなるエラーのコード（`CANONICAL_NOT_APPLICABLE`、`CANONICAL_WORKBENCH_SHARED`）も消す。コマンドの数は 53 から 51 になる。
  4. テンプレートの前付けの `タイトル:` と `親:` と、写すときにそれを除く処理（6章）。
  5. 規則の節の版3の文（10章）と、README、配布する `spec-dock/docs/`、spec-dock の `AGENTS.md` の、従来モードの記述。
  6. 移行のスクリプト `scripts/migrate-to-canonical/`（版のタグ `v0.3.0` に残る）と、spec-dock の `.github/scripts/specdock-ci-validate.sh`（I-10 で `ci.yml` から外した後、使われない）。
  7. 従来モードだけを確かめるテスト（下の「テストの扱い」）。
- **残すもの**（R-J7）：直接の選択の記録（`spec-dock/.agent/work-target/`）、`StartLock`、Artifact の命名と作成、`OperationResult` の結果の状態と終了コードの規則、読むだけのコマンドは書かないこと、配布資産の導入と更新（`installation` のコマンド）、worktree とブランチの操作。配布資産の「既知の古い版」の判定は、利用側の配布資産を 0.4.0 に上げるのに使うので残す。
- **テストの扱い**：
  1. 消す前に、今のテストを、次の3つに分けた一覧を作り、I-13 の報告書に載せる。(a) 版3だけの振る舞いを確かめるもの。(b) 共通の契約を、版3の作り物（`.meta.json` のある一時のリポジトリ）を使って確かめるもの。(c) モードに関係のないもの。2026-10-25 の時点で、`.meta.json` を扱うテストのファイルは100のうち50（テスト717件）ある。
  2. (a) は消す。(b) は、同じ契約を canonical モードの作り物（偽の `gh` と一時のカタログ）で確かめる形に書き直す。すでに canonical のテストが同じことを確かめていれば、その対応を一覧に書いてから消す。(c) は変えない。
  3. 版3の宣言を読むと、すべてのコマンドが案内付きで止まることを確かめるテストを足す。G7 のテストは、51のコマンドが canonical の処理だけで動くことを確かめる形にする。
- **版**：`pyproject.toml` と版のファイル（`spec-dock/system/spec-dock-version`）を 0.4.0 にする。`release-tag.yml` が、マージの後にタグ `v0.4.0` を作る。
- **各リポジトリを 0.4.0 にそろえる**（R-J8）：0.4.0 のPRがマージされ、利用者の環境に 0.4.0 を入れた後、統括のエージェントが、R-J1 の各リポジトリで `spec-dock installation update` を行い、通常のPRを作る（5つ）。各リポジトリの検査のワークフローは、版のファイルに従って 0.4.0 を入れて動く。人がマージする。
- **戻し方**：0.4.0 に問題があれば、利用者の環境に 0.3.0 を入れ直す。0.3.0 は canonical モードを持つので、移したリポジトリはそのまま動く。各リポジトリの配布資産を 0.4.0 に上げた後なら、版のファイルを戻すPRも作る。

## data / failure

### データの境界

| データ | 置き場 | 書くもの | 読むもの |
|---|---|---|---|
| 構造 | GitHub Issue | Scope を扱うコマンド、移行のスクリプト | 構造のスナップショットの取り直し、書く前の読み直し |
| 構造のスナップショット | `<状態の置き場>/github/<ホスト>/<owner>/<repo>/snapshot.json`、`probe.json` | 定期の同期、構造を読むコマンド（取り直しと、書き込みの反映） | 構造を読むすべてのコマンド、ダッシュボード、次の Epic の HTML のダッシュボード |
| ダッシュボード | `<main>/spec-dock/` の5つのファイル | 定期の同期だけ | 人 |
| 常駐のプロセスの記録 | `<状態の置き場>/runner.lock`、`runner.json`、`kick` | 常駐のプロセス、`canonical link`、`work finish`（`kick`） | `canonical status`、`canonical remove` |
| 内容 | canonical（カタログの作業ツリー） | 人、エージェント、SpecDock のコマンド | すべて |
| カタログのコミット | `.git` の `refs/heads/spec-dock/canonical` | 定期の同期だけ | 定期の同期、`canonical status` |
| 変更の束、作成の作業場所、保留の許可 | `<カタログ>/.runtime/` | SpecDock のコマンド | 定期の同期 |
| 同期の状態、基準 | `<状態の置き場>/catalogs/<鍵>/state.json` | 定期の同期と `canonical link` だけ | `canonical status`、`work finish` |
| 登録簿、ログ | `<状態の置き場>/` | `canonical link`、`canonical remove`、定期の同期（ログ） | 定期の同期 |
| 定期の実行の設定 | `~/Library/LaunchAgents/`、`~/.config/systemd/user/` | `canonical link`、`canonical remove` | OS |
| 無視の設定 | `<共通ディレクトリ>/info/exclude`、`spec-dock/.gitignore` | `canonical link`（exclude）、配布資産（.gitignore） | Git |
| 選択の記録 | 今と同じ `spec-dock/.agent/work-target/` | `work start`、`work finish` | 今と同じ |

### 失敗と境界の扱い

| 出来事 | SpecDock の動き | 次の1手 |
|---|---|---|
| mainで移行前のコミットへ移った | リンクが実体のディレクトリに置き換わる。カタログは残る（確認済み）。コマンドは `CANONICAL_NOT_LINKED` か `CANONICAL_LINK_OCCUPIED` で止まる | 元のブランチに戻ってから `spec-dock canonical link` |
| mainで `git clean -ffdx` | カタログが消える。保存済みのコミットは `.git` と GitHub に、基準は状態の置き場に残る（確認済み） | `spec-dock canonical link`（unlock、prune、作成、lock で作り直す） |
| mainのチェックアウトの移動や改名 | worktreeの登録と、作業用のworktreeの絶対パスのリンクが切れる | 新しい場所のmainで `spec-dock canonical link`（`git worktree repair` を行い、登録簿を直す）。その後、各作業用のworktreeで `spec-dock canonical link` |
| 作業用のworktreeの削除 | リンクだけが消え、カタログは残る（確認済み） | なし |
| 外付けのボリュームが外れている | 定期の同期は、そのカタログを飛ばして、状態の置き場に記録だけを残す | ボリュームをつなぐ |
| macOS のプライバシーの保護で読めない | 定期の同期は何も変えずに失敗し、`OS_ACCESS_DENIED` と、拒否されたプログラムを記録する | システム設定の「プライバシーとセキュリティ」で、示したプログラム（spec-dock の Python と git）に、フルディスクアクセスか、リムーバブルボリュームへのアクセスを許可する |
| ネットワークの断絶、認証の失敗 | 保存はローカルに積む。push は次の周期で試す。10分を超えたら警告する | `gh auth status` で認証を確かめる |
| 同じファイルの同時の編集 | 先着優先で別名ファイルを作る | 別名ファイルの中身を元のファイルに統合し、消す |
| 大量の削除、秘密情報、大きすぎるファイル | 保留する | 5章の保留の表 |
| GitHub の canonical の強制 push、削除、統合できない履歴 | 取り込まずに、そのカタログの同期を一時停止する | 利用者に知らせ、`canonical resume` の手順に従う |
| ツールの設定が足りない | `canonical status` と `canonical link` が1行を示す | 1行を足す |
| サンドボックスの中で、カタログの作成や登録が要る | 書く前に `CANONICAL_SANDBOX_DENIED` で止まる | 普通の端末で `spec-dock canonical link` |
| 移行前の版の SpecDock | 版4の宣言を読んで止まる | SpecDock を更新する |
| GitHub の画面での親の変更 | コマンドは名前でディレクトリを探すので動き続ける。`workspace validate` が、ずれを警告する | `spec-dock scope move <ID>` |
| GitHub の題名の変更 | 表示が変わるだけ | なし |
| 同じPCに同じリポジトリのクローンが複数 | クローンごとにカタログがあり、登録簿に別々に載る。互いには GitHub を通して同期する | なし |
| 2台のPCが同時に新しいリポジトリの canonical を作る | 後から push した側が、手元のものを捨てて GitHub のものを使う | なし |
| GitHub につながらない（構造） | 表示は今のスナップショットで続け、`GITHUB_SNAPSHOT_STALE` で取得の時刻を示す。書くコマンドは、書く前に `GITHUB_UNAVAILABLE` で止まる。定期の同期は、カタログの保存と push を続ける | 接続と `gh auth status` を確かめる |
| GitHub の画面で親子や依存だけを変えた | 変わったかの確かめで見つからないことがあり、表示とダッシュボードに出るまで最大30分かかる。書く判断の前には、判断に使う Issue を読み直す（2章） | なし（急ぐときは `spec-dock workspace sync --source github`） |
| コンテナ（中でクローン）を起動し直した | 常駐のプロセスが止まる。編集はファイルに残る | 起動の設定の1行か、`spec-dock canonical link` |
| ホストのフォルダーをマウントしたコンテナ | カタログの Git の登録が見えないので、Git を使うコマンドは `CANONICAL_FOREIGN_CHECKOUT` で止まる。ホストの記録は書き換えない | ホストで同期する。コンテナでは仕様のファイルの読み書きだけにするか、中でクローンする |
| SSH のサーバーで linger がない | ログアウトの間、定期の同期が止まる。`canonical status` が示す | `loginctl enable-linger <ユーザー>` |
| Git が 2.38 より古い | `canonical link` は書く前に、定期の同期はそのカタログを飛ばして、`CANONICAL_GIT_TOO_OLD` を示す | 新しい Git を入れ、`spec-dock canonical link` |
| 定期の実行から push の認証ができない | 保存はローカルに積み、`push_auth` に記録する。`canonical status` が示す | `gh auth setup-git`（`https`）。`ssh` なら `https` と `gh` の認証に変える |
| 移行の間に、一部のリポジトリだけが移った | 0.3.0 は、移したリポジトリを canonical モードで、移していないリポジトリを従来モードで扱う | なし |
| 切り替えの後、撤去の前に、新しい仕組みに重大な問題が見つかった | そのリポジトリだけを、切り替える前の形に戻せる。ほかのリポジトリには影響しない | 利用者が判断し、「戻し方」に従う |
| 撤去の後に、版3のリポジトリかクローンが見つかった | すべてのコマンドが `CANONICAL_NOT_MIGRATED` で止まる | 0.3.0 を入れ直し、版のタグ `v0.3.0` の手順書で移す |

## 変更対象

### 足すもの（提供側。層の置き場は AGENTS.md に従う）

| 置き場 | 中身 | 担当 |
|---|---|---|
| `src/spec_dock/runtime/domain/canonical_structure.py` | `StructureSnapshot`、`ScopeNode`、本文の印、階層と種類の規則 | I-1 |
| `src/spec_dock/runtime/infra/github_structure.py` | 2章の GraphQL と REST の呼び出し、状態コードの扱い（304 を状態行で判定する）、レート制限、書き込みの間の1秒 | I-1 |
| `src/spec_dock/runtime/infra/github_snapshot.py` | 構造のスナップショットの置き場、読み書きと排他、変わったかの確かめ、全体の取り直し、`ensure_fresh`、書き込みの反映（C10） | I-1 |
| `src/spec_dock/runtime/infra/runtime_environment.py` | OS の判定、コンテナの判定、git の版、systemd のユーザーの判定（試し直しを含む）、linger の判定 | I-2（systemd と linger は I-3） |
| `src/spec_dock/runtime/application/canonical_dashboard.py` | スナップショットから、描く関数の入力を作り、5つのファイルを書く（13章） | I-11 |
| `src/spec_dock/runtime/domain/canonical_*.py`（そのほか） | 純粋な規則：リンクの正しさの判定、保存するパスの選び方（30秒、5分）、保留の判定、競合の段からの解決の計画、別名ファイルの名前、変更の束と状態のモデル | I-2、I-3 |
| `src/spec_dock/runtime/infra/canonical_git.py` | カタログのための Git の操作（フックと署名を外す呼び出しの1つの関数、worktree、lock、repair、除外、ls-remote、fetch、一時のインデックスでの保存、merge-tree、commit-tree、ff、push） | I-2、I-3 |
| `src/spec_dock/runtime/infra/catalog_lock.py` | カタログのディレクトリへの `flock`（`start_lock.py` と同じ作り） | I-2 |
| `src/spec_dock/runtime/infra/catalog_tree.py` | カタログのファイルシステムを、名前で Scope のディレクトリを探してたどる | I-2 |
| `src/spec_dock/runtime/infra/canonical_state.py`、`canonical_registry.py`、`canonical_scheduler_launchd.py`、`canonical_scheduler_systemd.py`、`canonical_scheduler_loop.py` | 状態の置き場、登録簿、定期の実行の選び方、登録、解除、すぐの実行、常駐のプロセス（1つだけ動くこと、切り離しての起動、`kick`、止め方） | I-3 |
| `src/spec_dock/runtime/application/canonical_link.py`、`canonical_status.py` | 用意と状態 | I-2（登録と同期の項目は I-3） |
| `src/spec_dock/runtime/application/canonical_sync.py`、`canonical_hold.py`（accept、restore）、`canonical_resume.py`、`canonical_remove.py` | 同期と、その周りのコマンド | I-3 |
| `src/spec_dock/runtime/application/canonical_check.py` | 既定のブランチの検査 | I-7 |
| `src/spec_dock/runtime/application/canonical_scope_*.py` | 6章の、canonical モードのコマンドの処理 | I-4、I-5 |
| `src/spec_dock/runtime/presentation/` | 新しいコマンドの JSON と文字の出力 | 各担当 |
| `src/spec_dock/assets/spec_dock/docs/ci/spec-dock-check.yml`、`src/spec_dock/assets/spec_dock/system/spec-dock-version` | 配布資産（`static-inventory.json` にも足す） | I-7 |
| `src/spec_dock/assets/spec_dock/docs/canonical.md` | 使い方、ツールの設定、同期が止まったとき | I-9 |
| `.github/scripts/specdock-ci-check.sh`、`.github/workflows/release-tag.yml` | spec-dock のCI | I-7 |
| `.github/workflows/spec-dock-check.yml` | spec-dock の検査（切り替えのPRで入れる） | I-10 |
| `scripts/migrate-to-canonical/` | 移行のスクリプトと手順書 | I-8 |

### 変えるもの

- `src/spec_dock/runtime/application/project_context.py`：版3と4の受け付けと、モードの判定（I-1）。
- `src/spec_dock/runtime/commands/runtime_dispatch.py`：モードによる振り分けと、新しいコマンドの経路、リポジトリによらないコマンドの振り分け（I-1 で入口、各担当で経路）。
- `src/spec_dock/runtime/cli/catalog.py`、`cli/options.py`：新しいコマンドと引数（各担当）。
- `worktree create` と `work start` の後のリンクは、従来の `direct_worktrees.py` と `work_start.py` を変えずに、canonical の処理から I-2 の `link_after_command` を呼んで行う（`worktree create` は I-2、`work start` は I-5。3章）。
- `src/spec_dock/runtime/presentation/markdown.py`、`puml.py`：13章の描く関数。今は呼ばれていない。直す必要が出たときだけ、出力の形を変えずに直す（I-11）。
- `src/spec_dock/runtime/application/direct_installation.py`、`direct_static_update.py`：版4の宣言と、版3と4の受け付け（I-1）。
- `src/spec_dock/assets/spec_dock/.gitignore`：3章の無視の3行を足す（I-2）。
- `src/spec_dock/assets/spec_dock/workspace.json`：新しく導入するリポジトリ向けに版4にする。`init_only` のままなので、今のリポジトリは変わらない（I-1）。
- `src/spec_dock/assets/install_root/.agents/skills/spec-dock/SKILL.md`：10章の節。`static-inventory.json` の `.agents/` と `.claude/` の両方の項目を更新する（I-9）。
- `README.md`、`src/spec_dock/assets/spec_dock/docs/{README.md,guide.md,migration.md,reference_cli.md}`：使い方と、ツールの設定（R-H3。I-9）。
- `AGENTS.md`（spec-dock 自身）：10章の節と、破壊的なコマンドへの `canonical remove` の追加（I-9）。
- spec-dock の利用側の配布資産（`spec-dock/` の下）：0.3.0 の配布資産に `installation update` で上げる（I-9。従来モードのまま）。
- `pyproject.toml`：版を 0.3.0 にする（I-9）。

### 移行の間（I-1〜I-12）、変えないもの

- 従来モードの処理と、`.meta.json` の読み書きのコード（R-A6）。撤去（14章、I-13）で消す。
  - 例外（I-2 の統括の判断。この1か所だけ）：従来の `application/worktree_observation.observe_worktrees` は、`spec-dock/canonical` をチェックアウトし、ルートに `.spec-dock-canonical.json` がある worktree（カタログ）を観測から外す。切り替えの間とその後の運用で、同じクローンに版3の worktree が残っていても、従来の `work start` と `workspace sync` がカタログの宣言のなさで止まらないようにするためである。カタログのない版3のリポジトリでは、振る舞いは変わらない。
- テンプレートの配布資産の中身（6章）。撤去で、前付けの2行を外す。

### いつも変えないもの

- `StartLock` と、選択の記録の形式。
- 利用者のツールの設定のファイル。
- 人がPRをマージする関門。

### 撤去で消すもの（I-13）

14章のとおり。`dispatch()` から到達できない従来モードのコード、版3の受け付け、拒否するだけのコマンドと引数、テンプレートの前付けの2行、従来モードの文書、移行のスクリプト、`specdock-ci-validate.sh`、従来モードだけのテスト。

## 移行・互換性・rollback

### 組み合わせ

| SpecDock | 宣言の版3（移行前） | 宣言の版4（移行後） |
|---|---|---|
| 0.2.4（今） | 今のまま動く | 宣言を読んで止まる（R-A5） |
| 0.3.0（移行の間） | 今のまま動く（従来モード。R-A6、AC-15） | canonical モード |
| 0.4.0（撤去の後） | 移行の方法を示して止まる（`CANONICAL_NOT_MIGRATED`。14章） | canonical モード |

- パッケージは PCのユーザーごとに1つで、全リポジトリが共有する。0.3.0 を入れても、移行前のリポジトリは変わらない。そのため、どのリポジトリの切り替えよりも前に 0.3.0 を入れてよい。
- 0.3.0 の配布資産を移行前のリポジトリに `installation update` で入れても、従来モードは壊れない。`.gitignore` の3行は、実体のディレクトリの中の新しいファイルを無視しない（3章、確認済み）。規則の節は、版4のときだけ効く。
- 0.4.0 は、R-J1 のすべてのリポジトリを移した後にだけ入れる。

### 全体の順序（R-J4）

```text
0.3.0 を入れる ─ spec-dock の切り替え（I-10）─ 3日間の運用 ─ 残りの4つの切り替え（I-12）─ 3日間の運用 ─ 撤去と 0.4.0（I-13）
                  │                            │
                  └ 切り替えのPRのマージの後 ───┴ 残りの4つの準備（0.3.0 の配布資産、登録、照合、予行演習）
```

- 残りの4つの準備は、spec-dock の切り替えのPRがマージされ、構造の表し方が本物の GitHub で確かめられた後に始める。3日間の運用と並べて進めてよい。どれも今の運用を止めない。
- 残りの4つの本番は、3日間の運用の後に、1回の作業で、1つずつ順に行う。順は、小さく、影響の少ないものからとする：input-devices、company-os、housing-lifecycle、taikyohiyou_project（退去費用プロダクト）。

### 各リポジトリの切り替え

手順の正本は、`plan.md` の I-10 と I-12、移行のスクリプトの `README.md` である。1つのリポジトリについて、要点は次のとおり。

1. **準備**（今の運用は止めない）：0.3.0 の配布資産に上げるPRをマージする（11章）。`plan` の結果を確かめ、異常の扱いを決めて記録する。`register --apply` と `verify` で、構造を GitHub に登録して確かめる。予行演習（11章）を通す。
2. **凍結**：切り替えを始めたら、終わるまで、ほかのエージェントでそのリポジトリの仕様を編集しない。凍結の後に、`plan` で作業用のworktreeの仕様の変更を一覧にし、`register --apply` と `verify` をもう一度行う。
3. `build-canonical --apply` と `cut --apply` で canonical を作って push し、既定のブランチから仕様を外すブランチを作る。今のCIの SpecDock の手順を外すコミットを足し、PRを作る（11章）。
4. PRの検査（そのリポジトリの既存のCIと、新しい検査のワークフロー）が通ったことを確かめ、人がPRをマージする。
5. mainのチェックアウトで既定のブランチを取り込み、`move-local` で無視されたファイル（spec-dock では `.workbench` の99個）をカタログへ移してから、`spec-dock canonical link` を実行し、ツールの1行を足す。
6. 各作業用のworktreeで、`adopt-worktree` と `move-local` を行い、既定のブランチを取り込んでから、`spec-dock canonical link` を実行する。
7. 凍結を解く。

- **Scope のないリポジトリ**（company-os）：追跡された仕様がなく、`spec-dock/initiatives/` は空のディレクトリだけである。`register` で作るのは種類のラベルだけで、`build-canonical` は何もしない。手順5の `move-local` が空のディレクトリを消し、`canonical link` が、GitHub に canonical がない新しいリポジトリとして、最初の canonical を作る（3章の手順3）。

### 戻し方

- **切り替えのPRのマージ前**：PRを閉じ、`spec-dock/canonical` を消し、`undo --apply` で GitHub への登録を外せば、元に戻る。今の運用はずっと動いている。
- **マージの後、撤去の前**：そのリポジトリだけを戻す。`export-legacy --apply` で、カタログの内容と、GitHub から作り直した `.meta.json` と、版3の宣言を持つブランチを作り、切り替えのPRで外した今のCIの手順を戻すコミットを足して、PRで戻す。戻すPRをマージする前（各チェックアウトがまだ版4のうち）に、そのリポジトリのすべてのクローン（ほかのPCのものを含む）の各チェックアウトで `spec-dock canonical remove --yes` を行う。版3に戻った後は、canonical のコマンドが `CANONICAL_NOT_MIGRATED` で止まり、取り外せないためである（I-3 の統括の判断）。その後に戻すPRをマージし、必要なら `undo --apply` で登録を外す。0.3.0 のままでよく、ほかのリポジトリには影響しない。
- **撤去の後**：利用者の環境に 0.3.0 を入れ直してから、上と同じ手順で戻す。移行のスクリプトは、版のタグ `v0.3.0` から取り出す。
- 戻すかどうかは、利用者が判断する。エージェントは、戻す必要を見つけたら、止まって知らせる。

## testability

- テストは、今の方針どおり、外のネットワークを使わない。GitHub は、今と同じく、`PATH` の先頭に置いた偽の `gh` か、注入した実行器で置き換える（`tests/cli_runtime/test_issue413_scope_publish.py:426-463`、`tests/unit/infra/test_github_lifecycle_vnext.py:39-58`）。偽の `gh` には、GraphQL の問い合わせ（複数のラベルの OR）、sub-issue、blocked by、ラベル、一覧のページ送り、レート制限の応答（403 と `retry-after`）、条件付きの要求（`If-None-Match` が今の `ETag` と同じなら、終了コード1と状態行 `HTTP/2.0 304 Not Modified` を返す。本物の `gh` と同じ）を足す。偽の `gh` は、受けた要求を記録し、テストが要求の数と種類（主のレート制限を消費するものの数）を確かめられるようにする。
- **2台のPCの代わり**：一時ディレクトリに bare のリポジトリを作って GitHub の代わりにし、そこから2つのクローンを作る。各クローンで `canonical link` と `canonical sync` を直接呼ぶ（定期の実行は使わない。定期の実行の登録は、launchd と systemd の部分を注入できるようにして、偽物で試す）。時刻は注入できるようにし、30秒と5分の規則を待たずに試す。
- **フック**：テストのリポジトリに、必ず失敗する `pre-commit`、`post-checkout`、`post-merge`、`pre-push` を置いても、同期が成功することを確かめる。`commit.gpgSign=true` を設定しても止まらないことも確かめる。
- **環境の判定**：OS、コンテナの印、`systemctl` の結果、`loginctl` の結果、git の版は、注入できるようにする。macOS、systemd の Linux、systemd のない Linux、マウントしたチェックアウトの各場合を、どの OS の上のテストでも確かめられるようにする。提供側のCIは、`uv run pytest` を `ubuntu-latest` で動かしているので、Linux でのテストは毎回のPRで通る。
- **常駐のプロセス**：`--loop` を、時刻と待ちを注入して数周期だけ動かし、1つだけ動くこと（2つ目が終了コード0で終わる）、`kick` ですぐに周期が動くこと、SIGTERM で周期を終えてから止まることを確かめる。
- **従来モードの回帰（AC-15）**：撤去（I-13）までの Issue では、版3の振る舞いを確かめるテストは、変えてはならない。撤去での扱いは14章の「テストの扱い」に従う。撤去までに変えてよいのは、次のものだけである。
  - コマンドの数（44）とコマンドの一覧を確かめるテスト（`test_issue413_contract.py:160`、`test_cli_vnext_contract.py:17-65`、`test_cli_docs_vnext.py:35`）。新しいコマンドを足した数と一覧に直す。
  - 配布資産の一覧と値（`static-inventory.json` の値、資産のファイルの数）を確かめるテスト。
  - 文書の中身を確かめるテスト（新しいコマンドと規則の節を足したことによる変化）。
  - 版3のリポジトリの `installation show` で、配布資産の `workspace.json` が版4になるため、宣言が `known-old` と示されること（I-1。配布資産の値の変化）。そのほかの版3の振る舞い（`workspace validate`、`workspace validate --ci`、`workspace doctor`、`installation update` が宣言を書き換えないこと）は変わらないことをテストで確かめ、spec-dock 自身のCIの手順 `.github/scripts/specdock-ci-validate.sh` が通ることも確かめる。
  - `installation init` が版4の宣言を書くこと（I-1）に伴い、init で作った作り物に従来のコマンドを当てるテストは、init の直後に宣言を版3に戻す準備の行だけを足してよい。確かめる中身は変えない。変えたテストは、その Issue の報告書に一覧で書く（2026-10-26 の統括の判断）。
- **受け入れ条件との対応**：

| AC | 確かめ方 |
|---|---|
| AC-01 | 切り替えの後、spec-dock の既定のブランチで `spec-dock canonical check` が通り、`git ls-tree -r HEAD` に仕様のパスがない |
| AC-02 | 2つのworktreeで、片方の書き込みが保存の前に見える。2つのクローンで、`sync` を2回まわした後に見える。実機では、別のクローンからおよそ2分以内に見える |
| AC-03 | 2つのクローンで同じファイルを変え、両方で `sync` すると、先着の版と別名ファイルが両方に残り、競合のマーカーがない |
| AC-04 | `migrate.py verify` が一致を報告し、カタログに `.meta.json` がない |
| AC-05 | 仕様を変えた移行前のブランチで `adopt-worktree` の後、既定のブランチへのマージで仕様のパスが入らない |
| AC-06 | 新しいクローンと `git worktree add` のworktreeで `canonical link` の1回の後に読み書きできる。`worktree create` のworktreeでは何もせずに読み書きできる |
| AC-07 | `canonical status` が、Codex のサンドボックスと Claude Code の設定のそれぞれで、正確な1行を示す。文書に同じ1行がある |
| AC-08 | `git clean -ffdx`、mainのチェックアウトの移動、移行前のコミットへの checkout の後に、`canonical status` が原因と次の1手を示し、`canonical link` で戻る |
| AC-09 | 日本語の題名と `--slug` で作った Scope のディレクトリとブランチが英語で、`scope show` が日本語の題名を示す |
| AC-10 | 25件の削除が保留され、push されない |
| AC-11 | bare のリポジトリで canonical を強制 push で書き換えると、`sync` が取り込まずに一時停止する。ブランチを消したときも一時停止する |
| AC-12 | 既定のブランチへ仕様のファイルを足したPRで、検査のワークフローが失敗し、PRに表示される |
| AC-13 | 未保存の変更があるとき、`work finish` が保存と push を待ち、確かめられないと Issue を閉じずに止まる。他のクローンの push を取り込んだだけの場合も、確かめられて閉じる |
| AC-14 | 設計書を渡さない白紙のエージェントに、10章の節だけを渡して、読み書き、検索、別名ファイルの統合をさせる |
| AC-15 | 版3の振る舞いを確かめる今のテストが、上の許された変更のほかは変更なしで通る。版3のリポジトリでの代表のコマンドの出力が、0.2.4 と同じ |
| AC-16 | 偽の `gh` の記録で、変化のない周期と、続けて実行した `scope show` と `scope list` が、304 の確かめだけで終わり、全体の取り直しをしないこと。題名を変えた後の周期で取り直し、表示とダッシュボードに出ること。`scope create` の後の `scope show` が、取り直しなしで新しい Scope を示すこと |
| AC-17 | 一時のカタログと偽の `gh` で、周期の後に5つのファイルが、見本と同じ形（題名と作業中の色のほか）で作られること。構造が変わらない次の周期では、ファイルの更新の時刻が変わらないこと |
| AC-18 | 環境の判定を注入して、systemd、`loop`、マウントの各場合の動きを確かめる。実機では、systemd の Linux の仮想マシンと、systemd のないコンテナ（中でクローン）で、AC-02、AC-03、AC-13 を確かめる |
| AC-19 | 各リポジトリの予行演習の記録（I-10、I-12 の報告書）。切り替えの後に、各リポジトリの既定のブランチで `spec-dock canonical check` が通り、`migrate.py verify` が一致を報告する。各リポジトリの切り替えのPRで、検査のワークフローが動いて通る。I-12 の後の3日間の運用で、`canonical status` に未解決の異常がない |
| AC-20 | 0.4.0 で、14章の「消すもの」が残っていないことを、コードの検索（`.meta.json`、`schema_version` の3、`workspace migrate`、`workbench copy` など）と、版3の宣言で全コマンドが止まるテストで確かめる。撤去の前のテストの分類の一覧で、(b) のすべてに、対応する canonical のテストがある。各リポジトリの配布資産の PR で、検査のワークフローが 0.4.0 で通る |

- **実機での確かめ**（自動のテストでは確かめられないもの）：macOS の launchd の登録と、外付けのボリュームでのプライバシーの保護の案内、利用者の `gh` での push、Linux の systemd のタイマーと push、コンテナの常駐のプロセス、Codex のサンドボックスの中からの `scope create` と `work finish` と `canonical link`（リンクだけのとき）、Claude Code の設定の1行。結果は、各 Issue の報告書に書く。
- **Linux の実機**：利用者の Mac には OrbStack（2.2.5）と Docker が入っている。systemd の Linux は `orb create ubuntu:noble <名前>` の仮想マシンで、systemd のない Linux は `docker run` のコンテナで確かめる（2026-10-25 に、この方法で確かめた）。仮想マシンに git がないので `sudo apt-get install -y git` で入れる。確かめた後は、作った仮想マシン（`orb delete -f <名前>`）、コンテナ、取得したイメージを消す。利用者の `gh` の資格情報を、仮想マシンやコンテナに写してはならない。push の認証は、一時の bare のリポジトリへの push で代わりに確かめ、GitHub への push の認証は macOS で確かめる。

## risk

| リスク | 影響 | 軽減 |
|---|---|---|
| 定期の同期の誤りで、仕様が失われる | 大 | 削除の保留、強制 push をしない、競合で消さずに別名を作る、書き換えと削除の検出で一時停止する。統合の処理は純粋な関数に分け、競合の種類ごとにテストする |
| 2つのモードのコードが混ざり、従来モードが変わる | 大 | 従来の処理を変えず、振り分けを `dispatch()` の1か所にする。AC-15 の回帰テストを毎回通す |
| canonical モードで、答えないコマンドが残る | 大 | 6章の表で全コマンドの動きと担当を決めた。I-9 で、全コマンドを版4で動かすテストを置く |
| 移行で、無視されたファイルや未コミットの変更が失われる | 中 | `move-local` と `adopt-worktree` で作業ツリーから取り込む。`canonical link` は実体を消さない |
| macOS のプライバシーの保護で、定期の同期が黙って動かない | 中 | `canonical link` が直後に1回実行して確かめ、状態の置き場の記録を `canonical status` が示す |
| GitHub の構造の読み取りが遅い、制限にかかる | 中 | 構造のスナップショットを使い回し、変わったかの確かめは 304 で済ませる。全体は GraphQL の数回で読み、呼び出しは順に行う。レート制限は待って再試行する |
| スナップショットが古く、誤った判断で書く | 中 | 書く判断の前には `decision` の新しさで確かめ、判断に使う Issue を読み直す。SpecDock の書き込みは、すぐに反映する。30分ごとに取り直す |
| 常駐のプロセスが重なって動く、止まったまま気づかれない | 中 | `runner.lock` で1つだけ動かす。`canonical status` が動いているかを示し、`work finish` は止まっていれば起動する |
| マウントしたコンテナから、ホストの Git の記録を書き換える | 大 | コンテナの中で登録が見えないときは、`repair` や `prune` の前に止まる（3章） |
| 移行のスクリプトの書き込みが、二次のレート制限にかかる | 中 | 速さを抑え、止まっても続きから再開できるようにする |
| リポジトリのフックや署名の設定で、定期の同期が止まる | 中 | カタログへのすべての Git の呼び出しで、フックと署名を外す |
| エージェントが仕様を Git で扱ってしまう | 中 | 規則の節、無視の設定、定期の同期による上書きのない統合 |
| Claude Code の設定の判定が当たらない | 低 | 判定できないことを正直に示し、文書に設定の手順を書く |
| 同じ不具合が、移した全リポジトリに同時に当たる | 大 | spec-dock を先に移して3日間使う。撤去までは、リポジトリごとに 0.3.0 のまま戻せる |
| 撤去で、共通の契約のテストが失われる | 中 | 消す前にテストを3つに分けた一覧を作り、共通の契約のテストを canonical のテストに書き直してから消す（14章） |
| ほかのリポジトリの事情（既定のブランチ、CI、入れ子、多くのworktree）で切り替えが止まる | 中 | `plan` が CI の手順と作業用のworktreeを一覧にする。予行演習で、切り替えと戻しを通す。小さいものから順に移す |
| 残りの4つの凍結が長引く | 低 | 登録、照合、予行演習を前もって済ませ、当日の GitHub への書き込みを差分だけにする |
| Linux の一部を確かめていない | 中 | systemd のタイマーと `flock` は、Ubuntu 24.04 の仮想マシンで確かめた。残り（タイマーからの GitHub への push の認証、Landlock の中の `flock`）は、担当の Issue で、OrbStack の仮想マシンと Docker のコンテナで確かめる。確かめられないものは、報告書に未確認と書く |

## 設計の判断

| 判断 | 理由 |
|---|---|
| 宣言の版で2つのモードを分け、従来の処理を変えない | パッケージは全リポジトリで共有され、リポジトリごとに切り替える時期がずれるため（R-A6）。撤去で消しやすいように、振り分けを1か所にする |
| 従来モードを移行の間だけにし、この Epic で撤去する | 利用者が1人で、全リポジトリを自分で移せる。2つの仕組みを長く維持する費用と、エージェントが2つのモードで迷う原因をなくす（2026-10-25 の利用者の決定） |
| 開発中は新しいコードを横に足し、撤去は最後にまとめて行う | 今のコードをその場で書き換えると、多くのコマンドが通る読み込みの経路を変えたときに、手を付けていないコマンドまで壊れ、Issue を並べて進められない。足し算なら、main がいつも動き、利用者の日常（0.2.4、0.3.0）も変わらない |
| spec-dock を先に、残りの4つを1回の作業で | 同じ不具合が全リポジトリに当たるのを避け、dogfooding のリポジトリで先に見つける。残りをまとめるのは、凍結と準備を1回で済ませるため |
| 撤去で、拒否するだけのコマンドと引数も消す | 2つの仕組みが並ぶ間に、すべてのコマンドが答えるため（G7）に置いたもので、撤去の後は意味がない |
| 予行演習に `canonical link --no-schedule` を使う | 利用者の定期の実行（同じ名前のジョブ）と状態の置き場に触れずに、本物の CLI で切り替えを通すため |
| 今のCIの手順を、スクリプトで自動では書き換えない | リポジトリごとに形が違い（シェルスクリプト経由のものもある）、自動の書き換えは壊れやすい。切り替えのPRで手で直し、そのPRのCIで確かめる |
| 保存と同期の入口を `canonical sync` とし、`canonical` グループに集める | 用意（link）、状態（status）、保存（sync）、検査（check）、取り外し（remove）を1つのグループで見つけられるようにする。`workspace sync` とはグループで分ける |
| 排他をカタログのディレクトリへの `flock` にする | ファイルを作らないので、Codex のサンドボックスからも取れる（確認済み） |
| 変更の束で、コマンドの変更をすぐに1つのコミットにする | 30秒の規則で、コマンドの変更が途中で分かれないようにするため（R-D1）。`work finish` の束には保留の規則を当て、誤った削除を流さない |
| 同期の状態と基準をカタログの外に置く | カタログが読めない、消えたときでも、記録と書き換えの検出が働くようにするため |
| 競合を段の規則だけで解く | 名前の変更などの特別な場合を作らず、どの競合も同じ規則で、消さずに残すため |
| 構造の全体を GraphQL で読み、書き込みは REST にする | 全体の読み取りが約150回から数回になる。今の CLI も診断で GraphQL を使っている。書き込みは公式の文書で確かめた REST に揃える |
| 構造を、リポジトリごとのスナップショットにして使い回す | 利用者の方針（GitHub の負荷と待ち時間を抑える。R-I1）。次の Epic の HTML のダッシュボードの入力にもなる。今の CLI の「キャッシュしない」方針は、canonical モードでだけ変える。置き場はリポジトリの外にし、読むだけのコマンドの「リポジトリに書かない」契約は守る |
| 変わったかの確かめを、種類のラベルごとの一覧の条件付きの要求にする | 304 は主のレート制限に数えない（確認済み）。PRの更新では変化にならない。親子と依存の変更を見落とすかもしれない分は、30分ごとの取り直しと、書く前の読み直しで補う |
| systemd のない Linux では、SpecDock 自身の常駐のプロセスを使う | コンテナには systemd も cron もない（確認済み）。`canonical link` が起動するので、用意はコマンド1つのまま。起動し直しの1行は示すだけにする（約束4） |
| マウントしたチェックアウトでは止まる | コンテナの中から `repair` すると、ホストの記録を壊す。マウントの使い方は利用者がまだ決めていないので、安全に止まることだけを保証する |
| 無視の設定を、`/initiatives` と `!/initiatives/` の組み合わせにする | リンクだけを無視し、実体のディレクトリの中の新しいファイルは無視しないので、移行前のリポジトリとブランチでも安全なため（確認済み） |
| 検査のワークフローの SpecDock の版を、配布資産の版のファイルで決め、版のタグから入れる | ワークフローを書き換えずに、再現できる版を入れるため（R-F2）。PyPI には出していない |
| ジョブの plist を `~/Library/LaunchAgents/` に、git を絶対パスで、状態の置き場を引数で | 外付けのボリュームの plist は拒否され、プライバシーの保護の許可はプログラムごとで、定期の実行の環境変数は狭いため（確認済み） |
| ダッシュボードを、今までの形で、定期の同期が作り直す | 利用者の判断（R-E5）。描く関数が残っているので、入力を作るだけで済む。作るのを定期の同期だけにして、読むだけのコマンドの契約と約束3を守る |

## 未確認の事項

- systemd のユーザーのタイマーからの、GitHub への push の認証（タイマーが動くことは確認済み）。
- Linux の Codex のサンドボックス（Landlock）の中での、ディレクトリへの `flock`。
- 親子と依存の変更で、Issue の更新の時刻が変わるか（変わるなら、変わったかの確かめで見つかる）。I-10 の切り替えで、本物の GitHub への登録のときに確かめる。
- Claude Code の1行を、ユーザーの設定ファイルに書いたときの動き（`--settings` では確認済み）。
- GitHub の二次のレート制限の、公開されていない点数の endpoint（公式の文書は、一部の endpoint の点数を公開していない）。
- `adopt-worktree` と `export-legacy` の、ツールでの実行（手順の元になる Git の動きは、使い捨てのリポジトリで確認済み）。
- ほかの4つのリポジトリの、データの異常（題名の食い違い、循環、種類の規則の違反など）の数。I-8 で、`plan` を読むだけで実行して確かめる。
- 撤去で書き直す共通の契約のテストの数（14章の (b)）。I-13 の最初に分類して確かめる。
