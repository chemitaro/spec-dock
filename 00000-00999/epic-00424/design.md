---
種別: 設計書（Epic）
ID: "epic-00424"
タイトル: "Centralize Specs On Canonical Branch And GitHub Issues"
関連GitHub: ["#424"]
状態: "draft"
最終更新: "2026-10-25"
依存: ["requirement.md"]
親: ["init-00423"]
---

# epic-00424 Centralize Specs On Canonical Branch And GitHub Issues — 設計

詳細: [Design Guide](../../../docs/authoring/design.md)

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
| 従来モード | 宣言の版が3のリポジトリでの動き。今のコードをそのまま使う（R-A6） |
| canonical モード | 宣言の版が4のリポジトリでの動き。この設計書の対象 |
| 定期の同期 | PCのユーザーごとに1つの定期の実行（macOS は launchd、Linux は systemd のユーザーのタイマー）が、60秒ごとに `spec-dock canonical sync --registered` を動かすこと |
| 登録簿 | このPCで定期の同期の対象にするカタログの一覧。ユーザーのホームに置く |
| 変更の束 | SpecDock のコマンドがカタログに書いた変更の一覧。定期の同期が、1つのコミットとしてすぐに保存する |
| 保留 | 定期の同期が、自動では保存しないと判断した変更（大量の削除、秘密情報らしいもの、大きすぎるファイル） |
| 別名ファイル | 同じファイルの競合で、後から push する側の版を保存する `<名前>.conflict-<PC名>-<時刻>.<拡張子>` |

## 設計目標

- **G1 1か所の正本**：内容は canonical、構造は GitHub Issue だけに置く。既定のブランチと、そこへ入るPRには、仕様を置かない（R-A1〜R-A4）。
- **G2 いつもの場所で、普通のファイルとして**：どのチェックアウトでも、仕様は `spec-dock/initiatives/` に見える。人とエージェントは、仕様のために Git を操作しない（約束1）。
- **G3 用意は1つ**：`spec-dock canonical link` が、カタログ、保護、除外、リンク、定期の同期の登録をまとめて行う。何度実行しても同じ結果になる（約束2、R-B3）。
- **G4 保存の経路は1本**：保存、取り込み、push は、定期の同期だけが行う。SpecDock のほかのコマンドはコミットしない（約束3、R-C1、R-D1）。
- **G5 止まって案内する**：足りないものや異常があれば、推測で直さず、次に実行するコマンドか、足す設定を示して止まる（約束5、R-B5、R-H2）。
- **G6 移行していないリポジトリを壊さない**：宣言の版が3のリポジトリでは、新しい SpecDock でも今の動きをそのまま保つ（R-A6）。

## Current / Target

### Current（2026-10-25、`origin/main` の時点のコード）

- 仕様のツリー `spec-dock/initiatives/` を、既定のブランチとすべての作業ブランチが追跡している。
- 構造は、各 Scope のディレクトリの `.meta.json`（schema 3）にある。必須のキーは `schema_version`、`type`、`id`、`title`、`slug`、`parent_id`、`initiative_id`、`epic_id`、`depends_on`、`backend`、`github`、`lifecycle`、`revision`（`src/spec_dock/runtime/domain/writer_admission.py:22-39`）。
- 木の読み込みは `src/spec_dock/runtime/infra/scope_tree.py` の `load_scope_tree` が、ディレクトリをたどって行う。単一の対象では `git ls-files` を使う。リンクの `spec-dock/initiatives` は拒否する（`scope_tree.py:53-57`、`application/scope_query.py:51,60-62`）。
- `.meta.json` を書くのは、`infra/scope_metadata.py`（新規）と、`application/direct_scope_edit.py`、`direct_scope_lifecycle.py`、`direct_finish.py`、`direct_dependencies.py`、`direct_scope_delete.py`（置き換え）である。
- GitHub は `infra/github_lifecycle.py` の `GithubIssueGateway` が、`gh api --hostname github.com --include --method M <endpoint> [--input -]` で扱う。操作は取得、作成（題名と本文だけ）、状態の変更だけで、再試行はない。401/403/404 は権限なし、400/410/422 は拒否、そのほかの400以上は接続不可に分類する。
- `work start` は、基点のコミットのツリーから `.meta.json` を読む（`application/start_snapshot.py:92-144`）。排他 `StartLock`（`infra/start_lock.py`）は、Git の共通ディレクトリを開いて `flock` をかける。
- コマンドはすべて `commands/runtime_dispatch.py` の `dispatch()` を通る。コマンドの一覧は `cli/catalog.py` の `LEAF_PATHS`（44個）。結果は `presentation/envelope.py` の `OperationResult`（`status`、`exit_code`、`error`、`recovery` など）で返す。
- 宣言 `spec-dock/workspace.json` は `{"schema_version":3,"writer_protocol":"specdock.worktree-writer/v1"}`。`application/project_context.py` の `read_workspace_declaration` は、版が整数の3でなければ `ValueError` を出し、`PRECONDITION_FAILED`（終了コード3）になる。
- CI の「CI」（`.github/workflows/ci.yml`）は、ソースから wheel を作り、`spec-dock workspace validate --ci --json` を実行する（`.github/scripts/specdock-ci-validate.sh`）。
- 配布は wheel だけ。`pyproject.toml` の版は 0.2.4 で、版のタグはない。
- `spec-dock/dashboard.md` を生成するコマンドはない。

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
      .canonical/                         カタログ（canonical のworktree、lock 済み、Git では除外）
        .spec-dock-canonical.json         {"format": 1}
        .gitignore  README.md
        .runtime/                         定期の同期とコマンドの作業場所（canonical でも無視）
        init-00079-…/epics/…/issues/…     仕様の内容
      initiatives -> .canonical           リンク（相対）
  <作業用のworktree>/
    spec-dock/initiatives -> <main>/spec-dock/.canonical   リンク（絶対パス）

PCのユーザーごと
  ~/.local/state/spec-dock/canonical-registry.json        登録簿
  ~/Library/LaunchAgents/io.github.chemitaro.spec-dock.canonical-sync.plist   （macOS）
  ~/.config/systemd/user/spec-dock-canonical-sync.{service,timer}            （Linux）
```

- canonical モードでは、構造を GitHub から読み、内容をカタログのファイルから読む。`.meta.json` は読みも書きもしない。
- 従来モードのコードは残し、変えない。どちらのモードで動くかは、宣言の版だけで決める。

## 責務・Interface

### 1. モードの判定（R-A5、R-A6）

- `read_workspace_declaration` は、版 3 と 4 を受け付けるように変え、モード（`legacy` か `canonical`）を返す。それ以外の版は、今と同じく `PRECONDITION_FAILED` で止める。書き込みの許可（`require_writer`）は、どちらの版でも `writer_protocol` が `specdock.worktree-writer/v1` であることを求める。
- `dispatch()` は、Scope を扱うコマンドで、モードに応じて従来の処理か canonical の処理を呼ぶ。従来の処理の関数と、その下の `.meta.json` の読み書きは変えてはならない。canonical の処理は、新しいモジュールに置く（「変更対象」の章）。
- `canonical` グループのコマンドは、宣言の版が3のリポジトリでは `CANONICAL_NOT_MIGRATED`（終了コード3）で止まり、「このリポジトリは移行していない」と示す。
- 移行前の版の SpecDock（0.2.4）は、版4の宣言を読むと止まる（今のコードの動き）。これで R-A5 の前半を満たす。新しい処理を足す必要はない。
- canonical のルートの `.spec-dock-canonical.json` の `format` が、この SpecDock が知る版（1）より大きいとき、カタログに書くすべてのコマンドと定期の同期は、書く前に止まる（R-A5 の後半）。エラーのコードは `CANONICAL_FORMAT_UNSUPPORTED` で、次の1手は「SpecDock を更新する」である。

### 2. GitHub の構造（R-A2、R-A3、R-E1〜R-E4）

#### 表し方

| 構造 | GitHub での表し方 |
|---|---|
| Scope であること・種類 | ラベル `spec-dock:initiative`、`spec-dock:epic`、`spec-dock:issue` のちょうど1つ。PRは Scope にならない |
| 番号・ID | Issue の番号。ID は `init-`、`epic-`、`iss-` に、5桁にそろえた番号を付けたもの（今の `domain/ids.py` の `format_id`） |
| 識別名（slug） | 本文の末尾の行 `<!-- spec-dock:slug=<slug> -->`。ちょうど1つ。作成のときに固定する |
| 題名 | Issue の題名。いつでも変えてよい |
| 親子 | sub-issue。Initiative には親がない。Epic の親は Initiative、Issue の親は Epic |
| 依存 | blocked by |
| 状態 | open / closed と `state_reason`（今と同じ解釈） |
| 作業中の印 | `work start` で付け、`work finish` で外すラベル `spec-dock:in-progress`と、足すだけの担当者 |

- 印の正規表現は `^<!-- spec-dock:slug=([a-z0-9]+(?:-[a-z0-9]+)*) -->$`（複数行のモード）とする。印がない、2つ以上ある、slug が規則に合わないときは、構造の異常として扱う。
- ラベルがないときは、作る側のコマンド（`scope create`、`scope import`、`work start`、移行のスクリプト）が、`GET /repos/{o}/{r}/labels/{name}` で確かめてから、`POST /repos/{o}/{r}/labels` で作る。色と説明は固定の値を使う。
- Scope でない Issue への blocked by は、着手の判定では「その Issue が開いていれば着手できない」と扱う。`workspace validate` は警告を出す。

#### 使う REST API（調査の記録で、公式の文書と実測で確かめた）

| 操作 | API |
|---|---|
| Issue の一覧 | `GET /repos/{o}/{r}/issues?labels=<label>&state=all&per_page=100`。ページは `Link` ヘッダーでたどる。`pull_request` のある要素は除く。要素には `sub_issues_summary` と `issue_dependencies_summary` が入っている |
| Issue の取得、作成、題名と状態の変更 | `GET`、`POST /repos/{o}/{r}/issues`（`title`、`body`、`labels`）、`PATCH …/issues/{n}`（`title`、`state`、`state_reason`） |
| 子の一覧、親の取得 | `GET …/issues/{n}/sub_issues`、`GET …/issues/{n}/parent`（親がなければ404） |
| 親子を付ける、外す | `POST …/issues/{親}/sub_issues`（本文 `{"sub_issue_id": <子の id>, "replace_parent": <bool>}`）、`DELETE …/issues/{親}/sub_issue`（本文 `{"sub_issue_id": <子の id>}`） |
| 依存の一覧、追加、削除 | `GET …/issues/{n}/dependencies/blocked_by`、`POST …/dependencies/blocked_by`（本文 `{"issue_id": <依存先の id>}`）、`DELETE …/dependencies/blocked_by/{依存先の id}` |
| ラベル、担当者 | `POST …/issues/{n}/labels`（`{"labels": [...]}`）、`DELETE …/issues/{n}/labels/{name}`、`POST …/issues/{n}/assignees`（`{"assignees": [login]}`）、`GET /user` |

- `sub_issue_id` と `issue_id` は、Issue の番号ではなく、Issue の `id`（数値）である。取り違えないこと。
- 呼び出しは、今の `GithubIssueGateway` と同じく `gh api` を使う。GraphQL は使わない。
- 読み取り（GET）は、429 と 500 番台のときだけ、最大3回、1秒、2秒、4秒の間をおいて再試行する。書き込みは自動では再試行しない。結果が分からない書き込みは、今と同じく読み直して確かめ、それでも分からなければ終了コード6で、効果（`effects`）と再開の手順（`recovery`）を返す。
- 追加と削除が速すぎると二次のレート制限にかかる（公式の文書）。1つのコマンドの書き込みは数回なので、間をおく必要はない。大量に書く移行のスクリプトだけが、速さを抑える（11章）。

#### 構造の読み取りのモデル

- `StructureSnapshot` は、Scope の一覧と、`id → ScopeNode` の対応を持つ。`ScopeNode` は、`id`、`kind`、`number`、`issue_id`（数値の id）、`title`、`slug`、`state`、`state_reason`、`parent_id`、`blocked_by`（番号の一覧）、`assignees`、`in_progress` を持つ。
- **全体を読む**（`read_all`）：3つの種類のラベルで一覧を取り、`sub_issues_summary.total` が1以上の Issue だけ子の一覧を、`issue_dependencies_summary.blocked_by` が1以上の Issue だけ依存の一覧を取る。呼び出しは並べて行ってよい（同時に6つまで）。spec-dock の規模（Scope 243件、依存135本）で、およそ150回の呼び出しになる。
- **一部を読む**（`read_node`、`read_ancestors`、`read_children`、`read_blockers`）：1つの Scope と、その親のつながりや依存だけを読む。
- 構造をファイルに保存して使い回すこと（キャッシュ）はしない。今の CLI の方針（キャッシュを再導入しない）と、「読むだけのコマンドは書かない」契約を守るためである。
- 階層、種類、循環の規則は、今の `domain/dependency_vnext.py` と `infra/scope_tree.py` の規則をそのまま使い、入力を `.meta.json` から `StructureSnapshot` に変える。

#### 内容の置き場

- Scope のディレクトリは、今と同じ入れ子に置く。Initiative は `<カタログ>/<ID>-<slug>/`、Epic は `<Initiative>/epics/<ID>-<slug>/`、Issue は `<Epic>/issues/<ID>-<slug>/`。
- コマンドは、Scope のディレクトリを、入れ子の位置ではなく名前で探す。カタログの中で `<ID>-*` という名前のディレクトリが、ちょうど1つ見つかればよい。そのため、入れ子が GitHub とずれても、コマンドは動き続ける（R-A3）。ずれは `workspace validate` と `canonical status` が報告し、`scope move` が直す。
- `.meta.json` がカタログにあれば、異常として報告する。

### 3. カタログとリンク（R-B1〜R-B8）

#### 場所の決め方

- Git の共通ディレクトリを `git rev-parse --path-format=absolute --git-common-dir` で求める。その名前が `.git` で、親のディレクトリの `.git` がそれ自身であるとき、親のディレクトリが mainのチェックアウトである。そうでなければ（bare など）、`CANONICAL_UNSUPPORTED_LAYOUT` で止める（R-B1）。
- カタログは `<main>/spec-dock/.canonical`、リンクは `<チェックアウト>/spec-dock/initiatives` である。
- リンクの先は、mainのチェックアウトでは `.canonical`（相対）、作業用のworktreeでは `<main>/spec-dock/.canonical`（絶対パス）とする。リンクの先をさらにリンクにしてはならない（調査の記録：リンクのリンクにすると、mainで古いコミットへ移ったときに、すべての作業用のworktreeが古い実体を開く）。
- **正しいリンク**とは、`spec-dock/initiatives` がシンボリックリンクで、その値が上の値と同じで、たどった先の実際のパスがカタログの実際のパスと同じものをいう。

#### `spec-dock canonical link`

どのチェックアウトから実行しても、次を順に行う。何度実行しても結果は同じで、行ったことを `effects` に、利用者に残る作業を `warnings` に返す。

1. **前提**：宣言の版が4であること。mainのチェックアウトが見つかること。
2. **カタログ**：`git worktree list --porcelain` で、`<main>/spec-dock/.canonical` にあり、`spec-dock/canonical` をチェックアウトしているworktreeを探す。
   - あれば、何もしない。lock されていなければ lock する。
   - Git に登録されているが、ディレクトリがない（`git clean -ffdx` の後など）ときは、`git worktree unlock`、`git worktree prune`、作成、lock の順に作り直す（調査の記録で確認済みの手順）。
   - 作るときは、まず `git fetch origin spec-dock/canonical` を行う。取得の対象にこのブランチが入っていない浅いクローンでは、先に `git remote set-branches --add origin spec-dock/canonical` を行う。ローカルのブランチがなければ `git worktree add --track -b spec-dock/canonical <カタログ> origin/spec-dock/canonical`、あれば `git worktree add <カタログ> spec-dock/canonical` とする。最後に `git worktree lock --reason "spec-dock canonical catalog" <カタログ>` を行う。
   - GitHub にも手元にも canonical がなく、既定のブランチの HEAD のツリーに `spec-dock/initiatives` がないとき（新しいリポジトリ）は、5章の「canonical の中身」の管理ファイルだけを持つ、親のないコミットを作って push する。この場合は、作ったことを `effects` に書く。
   - `<main>/spec-dock/.canonical` に、カタログでないファイルやディレクトリがあるときは、変えずに止まる（`CANONICAL_PATH_OCCUPIED`）。
3. **除外の設定**：`<共通ディレクトリ>/info/exclude` に、`/spec-dock/.canonical/` と `/spec-dock/initiatives` の2行がなければ足す。この2行は、すべてのworktreeに効く。`spec-dock/.gitignore`（配布資産）には `/.canonical/` を足す（「変更対象」の章。Claude Code の検索は `.gitignore` だけを読み、`info/exclude` を読まないため）。`/initiatives` は配布資産には足さない（従来モードのリポジトリで、新しい仕様が追跡されなくなるため）。
4. **リンク**：mainのチェックアウトと、実行したチェックアウトに、正しいリンクを置く。
   - ないときは作る。違う先のリンクは、一時的な名前で作ってから `rename` で置き換える（`ln -s` を重ねると、リンクの先の中に余計なリンクができるため。調査の記録）。
   - 実体のファイルやディレクトリがあるとき（mainで移行前のコミットにいるときなど）は、置き換えずに止まる（`CANONICAL_LINK_OCCUPIED`）。中身を消してはならない。
5. **登録簿と定期の実行**：登録簿にカタログを足す。定期の実行がなければ作って動かす（5章）。作った直後に1回だけ実行させ、最大15秒、その結果を待つ。カタログを読めなかったとき（macOS のプライバシーの保護など）は、その原因と次の1手を `warnings` に返す。
6. **ツールの設定**：9章の判定を行い、足りない設定を正確な1行で `warnings` に返す。

#### SpecDock のほかのコマンドから

- `worktree create` は、`git worktree add` の後に、作ったworktreeについて 2〜4 の手順を行う（カタログがなければ作る。R-B4）。
- `work start` は、選択を記録した後に、対象のチェックアウトについて同じ手順を行う。
- そのほかの、仕様を使う canonical モードのコマンドは、リンクやカタログがない、または正しくないとき、自分では直さずに `CANONICAL_NOT_LINKED` で止まり、`recovery` に `spec-dock canonical link` を入れる（R-B5）。読むだけのコマンドは、何も書かない。

#### `spec-dock canonical status`（読むだけ。R-B7）

次の項目を返す。問題ごとに、次の1手を1つ付ける。

| 項目 | 内容 |
|---|---|
| `catalog` | 場所、ブランチ、lock の有無、HEAD のコミット |
| `link` | mainのチェックアウトと、このチェックアウトのリンクが正しいか |
| `exclude` | 除外の2行があるか |
| `access` | このプロセスがカタログを読めるか、書けるか（`os.access`。サンドボックスの中では、書けない場所に False を返す。確認済み） |
| `tools` | 9章の判定の結果と、足りない設定の1行 |
| `sync` | 定期の実行の有無と状態、最後に成功した同期の時刻、最後の失敗と理由 |
| `changes` | 未保存の変更の数、未pushのコミットの数と最も古い時刻、保留、別名ファイル、統合の待ち |
| `format` | canonical の形式の版と、この SpecDock が書けるか |
| `structure` | 入れ子と GitHub の親子のずれ（`--structure` を付けたときだけ、GitHub を読む） |

- 未pushのコミットが10分を超えたら警告する（R-C6）。

#### `spec-dock canonical remove`（取り外し。R-B8）

- 対象はこのクローン。`--yes` がなければ、予定だけを示して何もしない。
- 未保存の変更か未pushのコミットがあれば、止まる（`CANONICAL_UNSAVED_CHANGES`）。
- 次を外す。同じクローンのすべてのチェックアウトの、正しいリンク（実体は消さない）、カタログのworktree（unlock して `git worktree remove`）、除外の2行、登録簿の項目、定期の実行（ほかに登録されたカタログがないときだけ）。
- ローカルのブランチ `spec-dock/canonical` と、GitHub のブランチは消さない。
- AGENTS.md の「対象と結果を明示した指示が要る破壊的なコマンド」に、このコマンドを足す。

### 4. カタログへの書き込みの排他と変更の束（R-D1）

- **排他**：カタログに書く SpecDock のコマンドと、定期の同期は、カタログのディレクトリを読み取りで開き、`flock(LOCK_EX)` をかける。待つのは既定で10秒までで、取れなければ `CANONICAL_LOCK_BUSY`（終了コード3）で止まる。定期の同期は、取れなければその周期を飛ばす。
  - ファイルを作らないので、Codex のサンドボックスの中からでも取れる。サンドボックスの内と外で互いに効くことを確かめた（調査の記録）。
  - 排他の中では、ネットワークを使ってはならない。
  - `StartLock` とは別のものとする。カタログの書き込みで `work start` を待たせないためである。
- **変更の束**：コマンドは、排他の中でファイルを書いた後、`<カタログ>/.runtime/changesets/<時刻>-<乱数>.json` を書く。
  - 中身は `{"version": 1, "command": "scope create", "created_at": "...", "paths": ["init-…/epics/…"], "deletions": ["…"], "reason": "..."}` である。パスはカタログのルートからの相対パスで、ディレクトリを書けばその下をすべて含む。
  - 定期の同期は、束にあるパスを、30秒の待ちなしに、1つのコミットで保存する。束にある削除は、保留しない。保存したら束のファイルを消す。
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

#### 登録簿

- 場所は `${XDG_STATE_HOME:-$HOME/.local/state}/spec-dock/canonical-registry.json` とする（macOS でも同じ）。
- 中身は `{"version": 1, "catalogs": [{"catalog": "<実際のパス>", "main_checkout": "...", "git": "<git の絶対パス>", "registered_at": "..."}]}` である。
- 書くときは、同じディレクトリの一時ファイルに書いてから `rename` する。同時の書き込みは、登録簿のディレクトリへの `flock` で防ぐ。
- `git` には、`canonical link` を実行したときの `PATH` で見つかった git の絶対パスを記録する。定期の実行の `PATH` は狭く、macOS のプライバシーの保護の許可もプログラムごとなので、利用者がふだん使う git を使うためである（調査の記録：Apple の `/usr/bin/git` は外付けのボリュームを読めず、Homebrew の git は読めた）。

#### 定期の実行の登録

macOS（launchd）：

- `~/Library/LaunchAgents/io.github.chemitaro.spec-dock.canonical-sync.plist` に置く。外付けのボリュームに置いた plist は `launchctl bootstrap` が拒否した（調査の記録）ので、必ずここに置く。
- 中身は、`Label`（上の名前）、`ProgramArguments`（spec-dock の実行ファイルの絶対パス、`canonical`、`sync`、`--registered`）、`StartInterval` 60、`RunAtLoad` true、`StandardOutPath` と `StandardErrorPath`（`${XDG_STATE_HOME:-~/.local/state}/spec-dock/canonical-sync.log`）、`EnvironmentVariables` の `PATH`（記録した git のディレクトリを先頭に、`/usr/bin:/bin:/usr/sbin:/sbin`）である。
- 実行ファイルの絶対パスは、`canonical link` を動かしている spec-dock のコンソールのスクリプトの実際のパス（`sys.argv[0]` をたどったもの）とする。
- 登録は `launchctl bootstrap gui/<uid> <plist>`、すぐの実行は `launchctl kickstart gui/<uid>/<Label>`、解除は `launchctl bootout gui/<uid>/<Label>` で行う。
- launchd は、同じジョブを重ねて動かさない。

Linux（systemd のユーザーのタイマー）：

- `${XDG_CONFIG_HOME:-~/.config}/systemd/user/spec-dock-canonical-sync.service`（`Type=oneshot`、`ExecStart=<spec-dock の絶対パス> canonical sync --registered`、`Environment=PATH=…`）と、`spec-dock-canonical-sync.timer`（`OnBootSec=60`、`OnUnitActiveSec=60`、`AccuracySec=5s`）を置く。
- `systemctl --user daemon-reload` と `systemctl --user enable --now spec-dock-canonical-sync.timer` で動かす。すぐの実行は `systemctl --user start spec-dock-canonical-sync.service` で行う。
- 利用者がログインしていない間は動かない。それでよい（ログアウト中は編集もない）。
- Linux での動きと push の認証は、まだ確かめていない。担当の Issue で確かめる。

#### `spec-dock canonical sync` の1回の周期

`--registered` では登録簿のすべてのカタログを、引数なしではこのクローンのカタログを、順に処理する。1つのカタログの失敗で、ほかのカタログを止めてはならない。1つのカタログについて、次の順に行う。

1. **前提を確かめる**：カタログがあり、`spec-dock/canonical` にいて、マージの途中でないこと。形式の版が書ける版であること。満たさなければ、状態のファイルに理由を書いて、このカタログを飛ばす。読めない（`Operation not permitted`）ときは、macOS のプライバシーの保護として記録する（下の失敗の表）。
2. **取り込む**（排他の外）：`git fetch --no-tags origin +refs/heads/spec-dock/canonical:refs/remotes/origin/spec-dock/canonical`。失敗したら記録し、3と4だけを行う（コミットはローカルに積む）。
3. **書き換えを見つける**（R-C5）：状態のファイルの `last_seen_remote` があり、取り込んだ `origin/spec-dock/canonical` がその子孫でなければ（`git merge-base --is-ancestor`）、`paused: "remote_rewritten"` を記録し、このカタログの同期を止める。以後の周期も、利用者が直すまで止まる。
4. **保存**（排他の中）：
   - 変更を `git status --porcelain=v2 -z --untracked-files=all` で集める（`.runtime/` は `.gitignore` で除かれる）。
   - 保存するパスを選ぶ。変更の束にあるパスは、すぐに選ぶ。そのほかは、最後の変更から30秒以上たったものを選ぶ。変わり続けるファイルでも、最初に変更を見つけてから5分たったら選ぶ。削除は更新時刻がないので、最初に見つけた時刻を状態のファイルに記録して数える（R-C2）。
   - 保留を除く（R-C4。下の表）。
   - 一時のインデックス（`GIT_INDEX_FILE=<カタログ>/.runtime/index.tmp`）に `git read-tree HEAD` を読み、選んだパスを `git add -A -- <パス>` で載せ、`git write-tree` と `git commit-tree -p HEAD` でコミットを作り、`git update-ref refs/heads/spec-dock/canonical <新> <旧>` で進める。その後、`git reset -q -- <パス>` で、本当のインデックスをそろえる。
   - コミットは、`-c core.hooksPath=/dev/null` を付けて、リポジトリのコード用のフックを動かさない（R-C1。調査の記録：退去費用の `pre-commit` はカタログでも動いて失敗する）。
   - メッセージは `spec-dock: save <件数> files (<PC名>)` とする。作者は、利用者の Git の設定のとおりとする。
   - 選んだパスがなければ、コミットしない。
5. **統合**（排他の中）：L を手元の HEAD、R を `origin/spec-dock/canonical` とする。
   - R がない、または R が L の祖先なら、何もしない。
   - L が R の祖先なら、`git merge --ff-only R` を行う。編集中のファイルに当たって失敗したら、何も壊れていない（調査の記録）。`waiting_for_local_edits` に当たったパスを記録し、次の周期でもう一度試す（そのファイルは、遅くとも5分で保存され、次の分岐の場合として統合される）。
   - 分岐していれば、`git merge-tree --write-tree -z L R` で統合する（作業ツリーに触れない）。終了コードが0なら、そのツリーを使う。1なら競合で、出力の競合したファイルの情報（モード、オブジェクト、段、パス）を使い、一時のインデックスで次のように直す。
     - 段2（手元）と段3（GitHub）の両方があるパス：パスには段3を置き、`<名前>.conflict-<PC名>-<UTC の YYYYMMDDTHHMMSSZ>.<拡張子>` に段2を置く（先着優先。先に push された版が元の名前に残る）。
     - 段2だけ（GitHub で削除、手元で変更）：段2を置く。段3だけ（手元で削除、GitHub で変更）：段3を置く（変更を残す）。
     - 名前の変更が絡む競合も、段の規則だけで同じように扱う。
   - 直したツリーで、親を L と R の2つにしたコミットを `git commit-tree` で作り、`git merge --ff-only <そのコミット>` で作業ツリーを進める。編集中のファイルに当たって失敗したら、上と同じく待つ。
   - カタログに、競合のマーカーやマージの途中の状態を残してはならない。`rebase` と強制の push は使ってはならない（R-C3）。
   - 別名ファイルを作ったら、状態のファイルの `conflicts` に記録する。
6. **push**（排他の外）：L が R より進んでいれば `git push origin HEAD:refs/heads/spec-dock/canonical`（強制しない）。先に進まれて拒否されたら、2からもう一度行う。1つの周期でのやり直しは2回までとする。成功したら、`last_pushed_commit` と `last_seen_remote` を HEAD にする。
7. **記録**：状態のファイルを書く。

#### 保留（R-C4）

| 種類 | 判定 | 解除 |
|---|---|---|
| 大量の削除 | 1回の周期で、変更の束にない削除が20件以上、または追跡しているファイルの10%以上 | 意図した削除なら `spec-dock canonical accept --deletions`、意図しない削除なら `spec-dock canonical restore` |
| 秘密情報らしいもの | 中身が `ghp_`、`github_pat_`、`gho_`、`AKIA[0-9A-Z]{16}`、`-----BEGIN [A-Z ]*PRIVATE KEY-----` などに当たる | 中身を直せば、次の周期で自動で外れる。誤判定なら `spec-dock canonical accept <パス>` |
| 大きすぎるファイル | 10 MiB より大きい | 小さくするか、`spec-dock canonical accept <パス>` |

- 保留したことは、状態のファイルとログに書き、`canonical status` が示す。中身はログに書いてはならない。
- `canonical accept` は、指定した保留を、次の周期で保存してよいと記録する（`<カタログ>/.runtime/accepted.json`）。`canonical restore [<パス>…]` は、保留中の削除（またはパスの変更）を、HEAD の内容に戻す。どちらもコミットはしない。

#### 状態のファイル

`<カタログ>/.runtime/state.json`（定期の同期だけが書く）：

```json
{
  "version": 1,
  "updated_at": "2026-10-25T12:00:00Z",
  "last_success_at": "...",
  "last_error": {"code": "...", "message": "...", "next_step": "..."},
  "paused": null,
  "head": "<コミット>",
  "last_pushed_commit": "<コミット>",
  "last_seen_remote": "<コミット>",
  "unpushed_since": null,
  "pending_since": {"<パス>": "<時刻>"},
  "holds": [{"path": "...", "kind": "mass_delete|secret|too_large", "since": "..."}],
  "conflicts": [{"path": "...", "copy": "...", "at": "..."}],
  "waiting_for_local_edits": []
}
```

- 書くときは、一時ファイルに書いてから `rename` する。
- 定期の実行のログは、1 MiB を超えたら1世代だけ残して切り替える。

### 6. Scope を扱うコマンド（canonical モード）

| コマンド | 読む | 書く | 今との違い |
|---|---|---|---|
| `scope create` | 親とその祖先（一部） | Issue の作成（題名、本文の印、種類のラベル）→ 親への sub-issue → 排他の中でディレクトリの公開と変更の束 | `.meta.json` を作らない。日本語の題名を受け付ける（7章）。Issue を作った後に失敗したら、終了コード6と `recovery` に `scope import github <種類> <番号>` を返す |
| `scope import github` | Issue と親 | 足りないものだけを足す（種類のラベル、本文の印、親子、ディレクトリ）。何度実行しても同じ | `.meta.json` を作らない |
| `scope show`、`scope list` | `show` は一部、`list` は種類のラベルの一覧 | なし | 題名と状態を GitHub から示す（R-E4）。ディレクトリの場所も示す |
| `scope edit` | 対象 | `PATCH` で題名だけ | ファイルは変えない |
| `scope move`（新設） | 対象、新しい親、全体の構造は読まない | `--parent` があれば、`POST …/sub_issues` の `replace_parent: true` で付け替える。その後、排他の中でディレクトリを GitHub の親の下へ移し、変更の束を書く | `--parent` がなければ、ディレクトリを今の GitHub の親に合わせるだけ |
| `scope close`、`scope reopen` | 子孫か祖先（一部） | 今と同じく状態の `PATCH` | 子孫と祖先を GitHub の親子から求める |
| `scope delete` | 対象、子孫、依存 | 種類のラベルを外す、親から外す、`--detach-dependencies` なら依存を外す、`--backup-dir` に写してから、排他の中でディレクトリを消し、削除を変更の束に書く | Issue 自体は閉じも消しもしない |
| `dependency list`、`dependency check` | 対象と祖先の依存（一部）、`--all` なら全体 | なし | 入力を blocked by にする。着手の判定の規則は今と同じ |
| `dependency add`、`dependency remove` | 全体（循環の確認） | `POST` / `DELETE …/dependencies/blocked_by` | `.meta.json` を書かない |
| `artifact create`、`artifact import file` | 対象 | 排他の中でファイルを公開し、変更の束を書く | 置き場がカタログになる |
| `work start` | 対象と祖先と、それらの依存（一部） | 今と同じブランチの作成と選択の記録 → 作業中の印（ラベルと担当者。失敗は警告だけ）→ 対象のチェックアウトのリンク | 基点のコミットのツリーから `.meta.json` を読まない |
| `work finish` | 対象と子孫（一部） | 仕様の保存の確認（下）→ 今と同じく Issue を閉じる → 作業中のラベルを外す（失敗は警告だけ）→ 選択の解除 | 保存を確かめてから閉じる |
| `workspace sync` | 全体 | なし | 構造を GitHub から読む。`--source local` は `PRECONDITION_FAILED` にする |
| `workspace validate` | 全体とカタログ | なし | 下の検査を行う。`--ci` は `PRECONDITION_FAILED` にして、`canonical check` を案内する |
| `workspace doctor` | 今の項目に、`canonical status` と同じ項目を足す | なし | |
| `workspace migrate`、`installation *` | 今と同じ | 今と同じ | `installation init` は版4の宣言を置き、次の1手として `spec-dock canonical link` を示す。`installation update` と `show` は、版3と版4の両方を受け付ける |

- **`work finish` での保存の確認**（R-C6）：
  1. 排他の中で、Scope のディレクトリの下の未保存の変更を集め（`git --no-optional-locks status`。サンドボックスの中でも `.git` に書かない）、あれば変更の束を書く。
  2. 定期の実行にすぐの実行を頼む（`launchctl kickstart` など。サンドボックスの中で失敗しても無視してよい。遅くとも60秒で次の周期が来る）。
  3. 状態のファイルを2秒ごとに読み、束が消え、Scope の下に未保存の変更がなく、`last_pushed_commit` が手元の HEAD と同じになるまで待つ。待つのは既定で180秒まで（`--save-timeout`）。
  4. 確かめられなければ、Issue を閉じずに `CANONICAL_SAVE_UNCONFIRMED`（終了コード3）で止まり、`recovery` に `spec-dock canonical status` を入れる。
- **`workspace validate` の検査**：種類と階層の規則、本文の印と slug、ID の重複、依存の循環、Scope のディレクトリがちょうど1つあること、入れ子と GitHub の親子のずれ（警告。直し方は `scope move <ID>`）、Issue のないディレクトリ、必要な文書（`requirement.md`、`design.md`、`plan.md`、`report.md`）があること、`.meta.json` がないこと、別名ファイル（警告）、Scope でない Issue への依存（警告）。
- **作成時のファイル**：テンプレートの配布資産は変えない（従来モードを変えないため）。canonical モードの作成では、写すときに、前付けの `タイトル:` と `親:` の行を除く。題名と親の正本を GitHub だけにするためである。見出しの題名は、作成時の題名のまま残す。正本ではない。

### 7. 名前（R-E1〜R-E4）

- 題名は、空白を除いて空でなく、改行などの制御文字を含まず、256文字以下であればよい（GitHub の上限）。日本語を含んでよい。
- 題名が今の規則（`^[A-Za-z0-9]+(?: [A-Za-z0-9]+)*$`、`domain/ids.py:11`）に合うときは、今と同じく題名から slug を作る（小文字にして空白をハイフンに）。合わないときは、`--slug` を必須にする（R-E3）。slug の規則は今と同じ（`^[a-z0-9]+(?:-[a-z0-9]+)*$`）。
- この変更は canonical モードだけに入れる。従来モードの作成は、今の規則のままとする（R-A6）。
- 既定のブランチ名は、今と同じ `<ID>-<slug>`。題名を変えても、slug、ディレクトリ名、ブランチ名は変わらない（R-E2）。
- 表示（`scope show`、`scope list`、`workspace sync`、`dependency check` など）は、GitHub の題名を使う（R-E4）。`dashboard.md` の生成は復活させない。

### 8. 既定のブランチの検査（R-F1〜R-F3）

#### `spec-dock canonical check`

- チェックアウトの、指定したコミット（既定は `HEAD`）のツリーを `git ls-tree -r --full-tree` で調べる。カタログ、ネットワーク、GitHub のトークンがなくても動く。
- 調べること：
  1. `spec-dock/initiatives` そのものと、その下のパスがない（ファイル、リンク、gitlink を含む）。
  2. `spec-dock/.canonical` の下のパスがない。
  3. `spec-dock/` の下に `.meta.json` がない。
  4. `spec-dock/workspace.json` があり、版が4で、`writer_protocol` が既知である。
  5. 配布資産が、このパッケージの資産か、既知の古い版と一致する（今の `installation show` の判定を使う）。`spec-dock/.gitignore` に `/.canonical/` がある。
  6. `spec-dock/system/spec-dock-version` が、動いている SpecDock の版と同じ（違えば警告）。
- 失敗は1件ずつ、パスと次の1手を付けて返し、`CANONICAL_CHECK_FAILED`（終了コード7）で終わる。宣言の版が3なら、`CANONICAL_NOT_MIGRATED` で止まる。

#### ワークフロー

- **見本**：配布資産 `src/spec_dock/assets/spec_dock/docs/ci/spec-dock-check.yml`（利用側では `spec-dock/docs/ci/spec-dock-check.yml`）。各プロダクトは、導入するときに、これを `.github/workflows/` に写す。

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
- **版のタグ**：spec-dock のリポジトリに `.github/workflows/release-tag.yml` を置く。既定のブランチへの push で動き、`pyproject.toml` の版 `X.Y.Z` のタグ `vX.Y.Z` がなければ、そのコミットに作る（`permissions: contents: write`）。
- **canonical の push では動かない**：GitHub Actions は、push されたコミットのツリーのワークフローを使う。canonical には `.github/` がないので、定期の同期の push では、どのワークフローも動かない。
- **spec-dock での検査**：spec-dock 自身は、PRのコードで検査する。`.github/workflows/spec-dock-check.yml` を置き、今の `.github/scripts/specdock-ci-validate.sh` と同じ方法でソースから wheel を作り、`spec-dock canonical check --json` を実行する。今の `ci.yml` の `workspace validate --ci` の手順は外す。どちらも、仕様を既定のブランチから外す切り替えのPRで入れる（それまでは、既定のブランチに仕様があり、検査が失敗するため）。
- **マージの条件**：検査は、既存のCIと同じく、PRをきっかけに動き、結果をPRに表示する。GitHub の必須の検査（ブランチの保護、ルールセット）は設定しない。人は通過を確かめてからマージし、エージェントは通過していないPRを、マージできる状態として渡さない（R-F3）。

### 9. ツールの設定（R-B6、R-H3）

- 作業用のworktreeから仕様を読み書きするには、ツールごとに1行の設定が要る（調査の記録で確認済み）。SpecDock は、設定のファイルを書き換えてはならない（約束4）。
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
  - Claude Code の権限は、ツールの中で判定され、SpecDock のプロセスからは確かめられない。そこで、環境変数 `CLAUDECODE`（Claude Code のシェルでは `1`。2026-10-25 に確認）があるとき、または作業用のworktreeで `canonical link` と `canonical status` を実行したときは、`~/.claude/settings.json`、`<チェックアウト>/.claude/settings.json`、`<チェックアウト>/.claude/settings.local.json` を読むだけ読んで、`additionalDirectories` にカタログ（またはその親）があるかを見る。なければ、上の1行を示す。
  - mainのチェックアウトの中で動くセッションには、設定は要らない（カタログが作業ディレクトリの中にある）。
  - Claude Code の隔離セッション（`--worktree`）からの書き込みは、設定では通らない（確認済み）。読むだけにする。
- 確かめていないこと：Claude Code の1行を、`--settings` ではなくユーザーの設定ファイルに書いたときの動き。担当の Issue で、利用者の設定を変えずに、一時の `HOME` か `--settings` のファイルで確かめる。

### 10. エージェント向けの規則（R-H1、R-H2）

配布するスキル（`src/spec_dock/assets/install_root/.agents/skills/spec-dock/SKILL.md`）と、spec-dock の `AGENTS.md` に、次の節をそのまま置く（表現は整えてよいが、項目を減らしてはならない）。

```markdown
## 仕様の扱い（canonical モード）

`spec-dock/workspace.json` の `schema_version` が 4 のリポジトリでは、次に従う。3 のリポジトリでは、今までどおり、仕様もコードと一緒にコミットする。

- 仕様は `spec-dock/initiatives/` にある。普通のファイルとして読み書きする。
- 仕様は Git で扱わない（`git add`、`commit`、`stash`、`reset`、`checkout`、`clean` を仕様に使わない）。保存と共有は、1〜2分のうちに自動で行われる。
- 仕様が見えない、またはリンクの異常を示されたときは、`spec-dock canonical link` を実行する。
- 読み書きを拒否されたときは、`spec-dock canonical status` が示す1行の設定を、利用者に伝える。自分でツールの設定を変えない。
- 検索では、パスを明示する（`rg 語 spec-dock/initiatives/`、コードと一緒なら `rg 語 . spec-dock/initiatives/`）。
- 構造（作成、親子、依存、状態、題名）は、SpecDock のコマンドだけで変える。ディレクトリを手で動かさない。
- `*.conflict-*` のファイルがあれば、中身を元のファイルに統合してから、そのファイルを消す。
- Claude Code の隔離セッション（`--worktree`）では、仕様を読むだけにする。
- 作業を終えるときは `spec-dock work finish` を使う。保存が確かめられるまで待つ。
- リンクを消すときは `rm spec-dock/initiatives` と書く。末尾に `/` を付けない。mainのチェックアウトで `git clean -ff` を使わない。
```

- SpecDock のエラーは、`recovery`（`Recovery.commands` か `RecoveryInstructions.instructions`）に、次に実行するコマンドか足す設定を必ず入れる（R-H2）。12章の表のエラーには、すべて次の1手がある。

### 11. 移行のスクリプト（R-G1〜R-G6）

- 置き場は `scripts/migrate-to-canonical/`（リポジトリのルート。パッケージには入れない）。`migrate.py`（標準ライブラリと、`git` と `gh` のコマンドだけを使う1つのファイル）と `README.md`（ほかのプロジェクトで使う短い手順書）を置く。利用者の個人のプロジェクトの移行が終わったら消す。
- サブコマンド。どれも、既定では予定を表示するだけで、`--apply` を付けたときだけ書く。何度実行しても同じ結果になる。

| サブコマンド | すること |
|---|---|
| `plan` | `.meta.json` と GitHub を読み、登録の予定と、データの異常（循環する依存、種類の規則の違反、閉じた親の下の開いた子、ID と番号の不一致、GitHub との題名の食い違い、ローカルの Scope）を一覧にする（R-G4） |
| `register` | ラベルの作成、種類のラベル、本文の印、sub-issue、blocked by を、足すだけで登録する。題名は変えない（GitHub の題名を正とする）。今の CLI での運用は壊れない（R-G3） |
| `verify` | `.meta.json` の構造と、GitHub の構造が一致するかを比べる（AC-04） |
| `build-canonical` | 使い捨てのクローンで `git subtree split --prefix=spec-dock/initiatives` を行い、管理ファイルを足し、`.meta.json` を消すコミットを作って、`spec-dock/canonical` として push する。本物の `.git` に作業用のファイルを残さない（調査の記録） |
| `cut` | 既定のブランチから、仕様のツリーを外すブランチを作る。宣言を版4にし、`spec-dock-check.yml` を足し、`ci.yml` の `validate --ci` を外す。PRは人がマージする |
| `adopt-branch <ブランチ>` | 移行前のブランチの仕様を canonical に取り込み、そのブランチから仕様のツリーを外す（R-G5。下の方法） |
| `undo` | 取り消しの一覧に従って、`register` が足したものを外す |

- **ローカルの Scope と番号の不一致**：`init-local-00002`（#39 に結び付く）と `init-local-00003`（#31 に結び付く。#31 は題名が別物で閉じている）は、`plan` が異常として示す。`register` は、結び付いた Issue の題名が `.meta.json` の題名と同じなら、その番号の ID にディレクトリの名前を変える。違えば、`.meta.json` の題名で新しい Initiative の Issue を作り、その番号を使う。どちらにするかは、`plan` の出力に書き、`--apply` の前に確かめられるようにする。
- **取り消しの一覧**：GitHub に書いたことを1件ずつ、`scripts/migrate-to-canonical/.undo/<リポジトリ>.jsonl`（Git では無視）に追記する。中身は、操作、Issue の番号と id、相手の id、時刻である。
- **速さ**：書き込みは、1分に80回、1時間に500回を超えない（目安の制限）。spec-dock では約620回で、1.5時間ほどかかる見込み。途中で止まっても、取り消しの一覧と GitHub の今の状態から、続きを判断して再開する（R-G2）。
- **移行前のブランチの取り込み**：ブランチ B と既定のブランチの分岐点を M とする。`build-canonical` が作った canonical のコミットのうち、ツリーが `M:spec-dock/initiatives` と同じもの C を探す（subtree split のコミットは、元のコミットの `spec-dock/initiatives` と同じツリーを持つ）。`B:spec-dock/initiatives` から `.meta.json` を除いたツリーで、親を C とするコミット X を作り、canonical に3者マージで取り込む。B から仕様のツリーを外すコミットを作り、既定のブランチを B に取り込めば、PRは仕様を含まずにマージできる（調査の記録で確認済み）。

### 12. コマンドの一覧と出力の契約

新しく足すコマンド（`cli/catalog.py` の `LEAF_PATHS`、`HELP_EFFECTS`、`--help` の Target/Reads/Writes/Does not の節を、今のコマンドと同じ形で書く）：

| コマンド | 書くもの | 効果の要約（`HELP_EFFECTS`） |
|---|---|---|
| `canonical link` | カタログ、lock、除外、リンク、登録簿、定期の実行 | Find or create this clone's catalog, link this checkout, and register periodic sync. |
| `canonical status` | なし | Read catalog, link, access, tool settings and sync state; no changes. |
| `canonical sync` | カタログのコミット、push、状態のファイル | Save, merge and push the catalog once; `--registered` processes every registered catalog. |
| `canonical accept` | `accepted.json` | Allow held changes to be saved by the next sync. |
| `canonical restore` | カタログの作業ツリー | Restore held deletions or paths from the catalog HEAD; no commit. |
| `canonical check` | なし | Check that a commit of the code tree holds no specs and has intact SpecDock files; for CI. |
| `canonical remove` | リンク、カタログ、除外、登録簿、定期の実行 | Remove this clone's catalog, links and sync registration after confirming nothing is unsaved. |
| `scope move` | GitHub の親子、カタログのディレクトリ | Change or re-align a Scope parent in GitHub and move its directory to match. |

- **名前の判断**：保存と同期の入口は `canonical sync` とする。今の `workspace sync`（Scope の状態とworktreeの選択を観測する、読むだけのコマンド）とは別のグループに置き、`--help` の最初の行で違いを示す。エージェント向けの規則は「保存は自動」とし、どちらのコマンドも日常では使わせない。
- **JSON**：今の `OperationResult` の形で返す。`canonical status --json` の `data` は、3章の表の項目をキーに持つ。`canonical sync --json` の `data` は、カタログごとの `saved_commit`、`merged`、`pushed`、`conflicts`、`holds`、`skipped_reason` を持つ。
- **エラーのコード**（どれも `recovery` に次の1手を入れる）：

| コード | 終了コード | 次の1手 |
|---|---|---|
| `CANONICAL_NOT_MIGRATED` | 3 | 移行の手順書を見る（宣言の版が3） |
| `CANONICAL_UNSUPPORTED_LAYOUT` | 3 | mainのチェックアウトのある構成で使う |
| `CANONICAL_NOT_LINKED` | 3 | `spec-dock canonical link` |
| `CANONICAL_PATH_OCCUPIED`、`CANONICAL_LINK_OCCUPIED` | 3 | 示したパスの中身を確かめて退避してから `spec-dock canonical link`（SpecDock は消さない） |
| `CANONICAL_LOCK_BUSY` | 3 | しばらく待って同じコマンドを実行する |
| `CANONICAL_FORMAT_UNSUPPORTED` | 3 | SpecDock を更新する |
| `CANONICAL_UNSAVED_CHANGES` | 3 | `spec-dock canonical status` で確かめ、保存を待つ |
| `CANONICAL_SAVE_UNCONFIRMED` | 3 | `spec-dock canonical status` |
| `CANONICAL_REMOTE_REWRITTEN` | 3 | 利用者に知らせる。手順書の「canonical が書き換えられたとき」に従う |
| `CANONICAL_CHECK_FAILED` | 7 | 失敗ごとに示したパスを、既定のブランチから外す |
| `GITHUB_STRUCTURE_INVALID` | 7 | 示した Issue のラベル、印、親子を直す（`scope move` など） |

## data / failure

### データの境界

| データ | 置き場 | 書くもの | 読むもの |
|---|---|---|---|
| 構造 | GitHub Issue | Scope を扱うコマンド、移行のスクリプト | Scope を扱うコマンド |
| 内容 | canonical（カタログの作業ツリー） | 人、エージェント、SpecDock のコマンド | すべて |
| カタログのコミット | `.git` の `refs/heads/spec-dock/canonical` | 定期の同期だけ | 定期の同期、`canonical status` |
| 変更の束、作成の作業場所 | `<カタログ>/.runtime/` | SpecDock のコマンド | 定期の同期 |
| 同期の状態 | `<カタログ>/.runtime/state.json` | 定期の同期だけ | `canonical status`、`work finish` |
| 登録簿、ログ | `~/.local/state/spec-dock/` | `canonical link`、`canonical remove`、定期の同期（ログ） | 定期の同期 |
| 定期の実行の設定 | `~/Library/LaunchAgents/`、`~/.config/systemd/user/` | `canonical link`、`canonical remove` | OS |
| 除外の設定 | `<共通ディレクトリ>/info/exclude` | `canonical link`、`canonical remove` | Git |
| 選択の記録 | 今と同じ `spec-dock/.agent/work-target/` | `work start`、`work finish` | 今と同じ |

### 失敗と境界の扱い

| 出来事 | SpecDock の動き | 次の1手 |
|---|---|---|
| mainで移行前のコミットへ移った | リンクが実体のディレクトリに置き換わる。カタログは残る（確認済み）。コマンドは `CANONICAL_NOT_LINKED` か `CANONICAL_LINK_OCCUPIED` で止まる | 元のブランチに戻ってから `spec-dock canonical link` |
| mainで `git clean -ffdx` | カタログが消える。保存済みのコミットは `.git` と GitHub に残る（確認済み） | `spec-dock canonical link`（unlock、prune、作成、lock で作り直す） |
| mainのチェックアウトの移動や改名 | worktreeの登録と、作業用のworktreeの絶対パスのリンクが切れる | `git worktree repair` の後に、各チェックアウトで `spec-dock canonical link` |
| 作業用のworktreeの削除 | リンクだけが消え、カタログは残る（確認済み） | なし |
| 外付けのボリュームが外れている | 定期の同期は、そのカタログを飛ばして記録だけを残す | ボリュームをつなぐ |
| macOS のプライバシーの保護で読めない | 定期の同期は何も変えずに失敗し、`last_error.code = "OS_ACCESS_DENIED"` と、拒否されたプログラムのパスを記録する | システム設定の「プライバシーとセキュリティ」で、示したプログラム（spec-dock の Python と git）に、フルディスクアクセスか、リムーバブルボリュームへのアクセスを許可する |
| ネットワークの断絶、認証の失敗 | 保存はローカルに積む。push は次の周期で試す。10分を超えたら警告する | `gh auth status` で認証を確かめる |
| 同じファイルの同時の編集 | 先着優先で別名ファイルを作る | 別名ファイルの中身を元のファイルに統合し、消す |
| 大量の削除、秘密情報、大きすぎるファイル | 保留する | 5章の保留の表 |
| GitHub の canonical の強制 push や削除 | 取り込まずに、そのカタログの同期を止める | 利用者に知らせる |
| ツールの設定が足りない | `canonical status` と `canonical link` が1行を示す | 1行を足す |
| 移行前の版の SpecDock | 版4の宣言を読んで止まる | SpecDock を更新する |
| GitHub の画面での親の変更 | コマンドは名前でディレクトリを探すので動き続ける。`workspace validate` が、ずれを警告する | `spec-dock scope move <ID>` |
| GitHub の題名の変更 | 表示が変わるだけ | なし |
| 同じPCに同じリポジトリのクローンが複数 | クローンごとにカタログがあり、登録簿に別々に載る。互いには GitHub を通して同期する | なし |

## 変更対象

### 足すもの（提供側。層の置き場は AGENTS.md に従う）

| 置き場 | 中身 |
|---|---|
| `src/spec_dock/runtime/domain/canonical_*.py` | 純粋な規則：リンクの正しさの判定、保存するパスの選び方（30秒、5分）、保留の判定、競合の段からの解決の計画、別名ファイルの名前、変更の束と状態のファイルのモデル、`StructureSnapshot` と階層の検査 |
| `src/spec_dock/runtime/infra/github_structure.py` | ラベル、sub-issue、blocked by、一覧、題名、担当者の REST の呼び出し。今の `GithubIssueGateway` の `gh api` の呼び出しと、エラーの分類を共有する |
| `src/spec_dock/runtime/infra/canonical_git.py` | カタログのための Git の操作（worktree、lock、除外、fetch、一時のインデックスでの保存、merge-tree、commit-tree、ff、push） |
| `src/spec_dock/runtime/infra/catalog_lock.py` | カタログのディレクトリへの `flock`（`start_lock.py` と同じ作り） |
| `src/spec_dock/runtime/infra/canonical_registry.py`、`canonical_scheduler_launchd.py`、`canonical_scheduler_systemd.py` | 登録簿と、定期の実行の登録、解除、すぐの実行 |
| `src/spec_dock/runtime/infra/catalog_tree.py` | カタログのファイルシステムを、名前で Scope のディレクトリを探してたどる（`git ls-files` は使わない。未保存の新しい Scope も見えるようにするため） |
| `src/spec_dock/runtime/application/canonical_link.py`、`canonical_status.py`、`canonical_sync.py`、`canonical_check.py`、`canonical_remove.py`、`canonical_hold.py`（accept、restore） | 新しいコマンドの処理 |
| `src/spec_dock/runtime/application/canonical_scope_*.py` | 6章の、canonical モードの Scope を扱うコマンドの処理 |
| `src/spec_dock/runtime/presentation/` | 新しいコマンドの JSON と文字の出力 |
| `src/spec_dock/assets/spec_dock/docs/ci/spec-dock-check.yml`、`src/spec_dock/assets/spec_dock/system/spec-dock-version`、`src/spec_dock/assets/spec_dock/docs/canonical.md` | 配布資産（`static-inventory.json` にも足す） |
| `.github/workflows/release-tag.yml`、`.github/workflows/spec-dock-check.yml`（切り替えのPRで） | spec-dock のCI |
| `scripts/migrate-to-canonical/` | 移行のスクリプトと手順書 |

### 変えるもの

- `src/spec_dock/runtime/application/project_context.py`：版3と4の受け付けと、モードの判定。
- `src/spec_dock/runtime/commands/runtime_dispatch.py`：モードによる振り分けと、新しいコマンドの経路。
- `src/spec_dock/runtime/cli/catalog.py`、`cli/options.py`：新しいコマンドと引数。
- `src/spec_dock/runtime/application/direct_worktrees.py`（`worktree create` の後のリンク）と `work_start.py`（選択の後のリンク）。
- `src/spec_dock/runtime/application/direct_installation.py`、`direct_static_update.py`：版4の宣言と、版3と4の受け付け。
- `src/spec_dock/assets/spec_dock/.gitignore`：`/.canonical/` を足す。
- `src/spec_dock/assets/spec_dock/workspace.json`：新しく導入するリポジトリ向けに版4にする（`init_only` のままなので、今のリポジトリは変わらない）。
- `src/spec_dock/assets/install_root/.agents/skills/spec-dock/SKILL.md`：10章の節。`static-inventory.json` の `.agents/` と `.claude/` の両方の項目を更新する。
- `README.md`、`src/spec_dock/assets/spec_dock/docs/{README.md,guide.md,migration.md,reference_cli.md}`：使い方と、ツールの設定（R-H3）。
- `AGENTS.md`（spec-dock 自身）：10章の節と、破壊的なコマンドへの `canonical remove` の追加。
- `pyproject.toml`：版を 0.3.0 にする。

### 変えないもの

- 従来モードの処理と、`.meta.json` の読み書きのコード（R-A6）。削除は、利用者の個人のプロジェクトの移行が終わった後の別の Epic で行う。
- `StartLock` と、選択の記録の形式。
- テンプレートの配布資産の中身（6章）。
- 利用者のツールの設定のファイル。
- 人がPRをマージする関門。

## 移行・互換性・rollback

### 組み合わせ

| SpecDock | 宣言の版3（移行前） | 宣言の版4（移行後） |
|---|---|---|
| 0.2.4（今） | 今のまま動く | 宣言を読んで止まる（R-A5） |
| 0.3.0（この Epic） | 今のまま動く（従来モード。R-A6、AC-15） | canonical モード |

- パッケージは PCのユーザーごとに1つで、全リポジトリが共有する。0.3.0 を入れても、移行前のリポジトリは変わらない。そのため、spec-dock の切り替えの前に 0.3.0 を入れてよい。
- 0.3.0 の配布資産を移行前のリポジトリに `installation update` で入れても、従来モードは壊れない（`/.canonical/` の除外は害がなく、`/initiatives` は足さない。規則の節は版4のときだけ効く）。

### spec-dock の切り替え

手順の正本は、`plan.md` と、移行のスクリプトの `README.md` である。要点は次のとおり。

1. 0.3.0 のPRをすべてマージし、利用者の環境に 0.3.0 を入れる（従来モードで今のまま動く）。
2. `migrate.py plan`、`register --apply`、`verify` で、構造を GitHub に登録して確かめる。この間も、今の運用は止めない。
3. 切り替えを始めたら、終わるまで、ほかのエージェントで仕様を編集しない。
4. `build-canonical --apply` と `cut --apply` で canonical を作って push し、既定のブランチから仕様を外すPRを作る。
5. 人がPRをマージする。
6. 各チェックアウトで `spec-dock canonical link` を実行し、ツールの1行を足す。
7. 作業用のworktreeに残った仕様の変更は、`adopt-branch` で取り込む。

### 戻し方

- **切り替えのPRのマージ前**：PRを閉じ、`spec-dock/canonical` を消し、`undo --apply` で GitHub への登録を外せば、元に戻る。今の運用はずっと動いている。
- **マージの後**：切り替えのPRを `git revert` で取り消し、宣言を版3に戻す。マージの後に canonical に入った変更は、カタログから既定のブランチへ写すPRで戻す。`.meta.json` は、GitHub の構造から移行のスクリプトで作り直す（`undo` の前に行う）。各チェックアウトで `spec-dock canonical remove --yes` を行う。
- 戻すかどうかは、利用者が判断する。エージェントは、戻す必要を見つけたら、止まって知らせる。

## testability

- テストは、今の方針どおり、外のネットワークを使わない。GitHub は、今と同じく、`PATH` の先頭に置いた偽の `gh` か、注入した実行器で置き換える（`tests/cli_runtime/test_issue413_scope_publish.py:426-463`、`tests/unit/infra/test_github_lifecycle_vnext.py:39-58`）。偽の `gh` には、sub-issue、blocked by、ラベル、一覧のページ送りを足す。
- **2台のPCの代わり**：一時ディレクトリに bare のリポジトリを作って GitHub の代わりにし、そこから2つのクローンを作る。各クローンで `canonical link` と `canonical sync` を直接呼ぶ（定期の実行は使わない）。時刻は注入できるようにし、30秒と5分の規則を待たずに試す。
- **受け入れ条件との対応**：

| AC | 確かめ方 |
|---|---|
| AC-01 | 切り替えの後、spec-dock の既定のブランチで `spec-dock canonical check` が通り、`git ls-tree -r HEAD` に仕様のパスがない |
| AC-02 | 2つのworktreeで、片方の書き込みが保存の前に見える。2つのクローンで、`sync` を2回まわした後に見える。実機では、別のクローンからおよそ2分以内に見える |
| AC-03 | 2つのクローンで同じファイルを変え、両方で `sync` すると、先着の版と別名ファイルが両方に残り、競合のマーカーがない |
| AC-04 | `migrate.py verify` が一致を報告し、カタログに `.meta.json` がない |
| AC-05 | 仕様を変えた移行前のブランチで `adopt-branch` の後、既定のブランチへのマージで仕様のパスが入らない |
| AC-06 | 新しいクローンと `git worktree add` のworktreeで `canonical link` の1回の後に読み書きできる。`worktree create` のworktreeでは何もせずに読み書きできる |
| AC-07 | `canonical status` が、Codex のサンドボックスと Claude Code の設定のそれぞれで、正確な1行を示す。文書に同じ1行がある |
| AC-08 | `git clean -ffdx`、mainのチェックアウトの移動、移行前のコミットへの checkout の後に、`canonical status` が原因と次の1手を示し、`canonical link` で戻る |
| AC-09 | 日本語の題名と `--slug` で作った Scope のディレクトリとブランチが英語で、`scope show` が日本語の題名を示す |
| AC-10 | 25件の削除が保留され、push されない |
| AC-11 | bare のリポジトリで canonical を強制 push で書き換えると、`sync` が取り込まずに止まり、状態に記録する |
| AC-12 | 既定のブランチへ仕様のファイルを足したPRで、検査のワークフローが失敗し、PRに表示される |
| AC-13 | 未保存の変更があるとき、`work finish` が保存と push を待ち、確かめられないと Issue を閉じずに止まる |
| AC-14 | 設計書を渡さない白紙のエージェントに、10章の節だけを渡して、読み書き、検索、別名ファイルの統合をさせる |
| AC-15 | 今の回帰テスト（`uv run pytest`）が、変更なしで通る。版3のリポジトリでの代表のコマンドの出力が、0.2.4 と同じ |

- **実機での確かめ**（自動のテストでは確かめられないもの）：macOS の launchd の登録と、外付けのボリュームでのプライバシーの保護の案内、利用者の `gh` での push、Linux の systemd のタイマーと push、Codex のサンドボックスの中からの `scope create` と `work finish`、Claude Code の設定の1行。結果は、各 Issue の報告書に書く。

## risk

| リスク | 影響 | 軽減 |
|---|---|---|
| 定期の同期の誤りで、仕様が失われる | 大 | 削除の保留、強制 push をしない、競合で消さずに別名を作る、移行の前に全体のバックアップ（GitHub の既定のブランチの履歴に残る）。統合の処理は純粋な関数に分け、競合の種類ごとにテストする |
| 2つのモードのコードが混ざり、従来モードが変わる | 大 | 従来の処理を変えず、振り分けを `dispatch()` の1か所にする。AC-15 の回帰テストを毎回通す |
| macOS のプライバシーの保護で、定期の同期が黙って動かない | 中 | `canonical link` が直後に1回実行して確かめ、`canonical status` が最後の成功の時刻を示す |
| GitHub の構造の読み取りが遅い | 中 | 一部を読む関数を使い分け、全体を読むのは validate、sync、依存の追加だけにする。並べて呼ぶ |
| 移行のスクリプトの書き込みが、二次のレート制限にかかる | 中 | 速さを抑え、止まっても続きから再開できるようにする |
| エージェントが仕様を Git で扱ってしまう | 中 | 規則の節、カタログの除外、定期の同期による上書きのない統合 |
| Claude Code の設定の判定が当たらない | 低 | 判定できないことを正直に示し、文書に設定の手順を書く |
| Linux で確かめていない | 中 | 担当の Issue で、実機（利用者の Lima の VM など）で確かめる。確かめるまで、Linux を対応と書かない |

## 設計の判断

| 判断 | 理由 |
|---|---|
| 宣言の版で2つのモードを分け、従来の処理を変えない | パッケージは全リポジトリで共有され、移行の時期がずれるため（R-A6）。後で消しやすいように、振り分けを1か所にする |
| 保存と同期の入口を `canonical sync` とし、`canonical` グループに集める | 用意（link）、状態（status）、保存（sync）、検査（check）、取り外し（remove）を1つのグループで見つけられるようにする。`workspace sync` とはグループで分ける |
| 排他をカタログのディレクトリへの `flock` にする | ファイルを作らないので、Codex のサンドボックスからも取れる（確認済み） |
| 変更の束で、コマンドの変更をすぐに1つのコミットにする | 30秒の規則で、コマンドの変更が途中で分かれないようにするため（R-D1） |
| 競合を段の規則だけで解く | 名前の変更などの特別な場合を作らず、どの競合も同じ規則で、消さずに残すため |
| 構造をキャッシュしない | 今の CLI の方針と、読むだけのコマンドは書かない契約を守るため |
| `/initiatives` の除外を `info/exclude` に置き、配布資産に置かない | 配布資産は従来モードのリポジトリにも入り、そこで新しい仕様が追跡されなくなるため |
| 検査のワークフローの SpecDock の版を、配布資産の版のファイルで決め、版のタグから入れる | ワークフローを書き換えずに、再現できる版を入れるため（R-F2）。PyPI には出していない |
| ジョブの plist を `~/Library/LaunchAgents/` に、git を絶対パスで | 外付けのボリュームの plist は拒否され、プライバシーの保護の許可はプログラムごとであるため（確認済み） |
| `dashboard.md` の生成を復活させない | 今の CLI も生成しておらず、表示は CLI の出力で足りるため（R-E4） |

## 未確認の事項

- Linux の systemd のユーザーのタイマーと、そこからの push の認証。
- Claude Code の1行を、ユーザーの設定ファイルに書いたときの動き（`--settings` では確認済み）。
- GitHub の二次のレート制限の、実際の閾値。
- `adopt-branch` の、ツールでの実行（手順は使い捨てのリポジトリで確認済み）。
