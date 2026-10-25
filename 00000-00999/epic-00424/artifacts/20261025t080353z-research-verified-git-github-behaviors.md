---
種別: research
ID: "20261025t080353z-research"
タイトル: "検証済みのGitとGitHubの挙動"
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-10-25"
親: ["epic-00424"]
template: "research"
authority: "evidence"
derived_from: []
reflected_to: []
---

# 20261025t080353z-research 検証済みのGitとGitHubの挙動

2026-10-24〜25 の検討で、使い捨てのリポジトリと実データで確かめた事実を集めます。Epic の要件と設計の根拠です。採用した内容は、要件定義書と設計書に書き直します。

## Question

- 仕様の正本を `spec-dock/canonical` ブランチと GitHub Issue に分けるとき、Git、GitHub、各ツールは実際にどう動くか。
- 前提にする実データ（Scope の数、題名、依存、ブランチ）は、どうなっているか。

## Source

- 参照先と確認日:
  - 使い捨てのリポジトリでの再現（2026-10-24〜25、Git 2.54.0、macOS）。確認後に削除済み。
  - spec-dock と退去費用プロダクトの実データ（`.meta.json`、`gh issue list`、`gh api`。2026-10-25）。
  - spec-dock の実装（`src/spec_dock/runtime/`、2026-10-25 の `origin/main` = `8bcad1a0a`）。
  - 先行資料：同じ Epic の Artifact `20261025t080256z--scope-catalog-centralization-analysis.html`、`20261025t080257z--scope-catalog-centralization-detail.html`、`20261025t080259z--scope-catalog-design.html`（v0.8）。

## Findings

### 配置とリンク

- mainのチェックアウトで移行前のコミットへ移ると、追跡されていない仕様の実体が上書きされる。実体を `spec-dock/.canonical/`（どのコミットも追跡したことのない場所）に置くと、置き換わるのはリンクだけで、実体は残る。
- 作業用のworktreeのリンクを、mainのリンクに向ける（リンクのリンク）と、mainで移行前のコミットへ移ったときに、mainの古い実体を開き、書き込みがmainの追跡ファイルを変える。実体を直接指すリンクは影響を受けない。
- `git clean -fdx` は入れ子のworktreeを残す。`git clean -ffdx` は消す。消えた後の `git worktree add` は「missing but locked worktree」で失敗し、unlock・prune・add・lock で戻せる。
- `git stash --all` は `Ignoring path spec-dock/.catalog/` と出して触らない。
- mainのチェックアウトを移動すると、worktreeの登録が切れる。`git worktree repair` で直る。mainの相対リンクは動き続ける。
- 移行前のブランチをmainで開いて `git add -A` すると、除外の1行（`.git/info/exclude`）がない場合、`warning: adding embedded git repository` と出て gitlink（160000）が入る。1行あれば入らない。
- Claude Code のシェルの検索（ugrep の `--ignore-files`）は `.gitignore` だけを読み、`info/exclude` を読まない。
- `--relative-paths` は `extensions.relativeWorktrees` を設定し、worktreeを消しても残る。
- 作業用のworktreeを `git worktree remove`、`git worktree remove --force`、`rm -rf` と `prune` で消しても、中のリンク先（カタログ）は消えない。リンクは無視されているので、`git status` にも出ない。
- lock したカタログのworktreeは、`git worktree remove --force` を「cannot remove a locked working tree」で拒否する（`-f -f` が必要）。`git worktree prune` も残す。

### ツールの権限

- Claude Code の隔離セッション（`--worktree`）では、リンク経由の Edit が「This path is in a different worktree」で拒否される。`additionalDirectories`、`--add-dir`、PreToolUse の許可フック、`worktree.symlinkDirectories`、`WorktreeCreate` フックのどれでも通らない。シェルの書き込みは通る。
- Claude Code の隔離しない普通のセッションでも、作業ディレクトリの外を指すリンクの扱いは、権限モードで変わる（2026-10-25、`claude -p`、Claude Code の既定の設定は `defaultMode` と `additionalDirectories` がない状態）。
  - `bypassPermissions` では、リンク経由の Edit が成功した。
  - `default` と `acceptEdits` では、リンク経由の Read が「resolves through a symlink to …, which is outside the allowed working directories」で拒否され、その結果 Edit もできなかった。対話のセッションでは、許可を求められる。
  - `acceptEdits` で、`permissions.additionalDirectories` にリンク先のディレクトリを加えると、Read と Edit が成功した。
- Codex は `writable_roots` にカタログを加える前は `Operation not permitted`、加えた後は書ける。Codex からカタログでコミットすると、mainの `.git/worktrees/<名前>/index.lock` を作れずに失敗する。
- 2026-10-25 時点で、`codex exec` は既定のモデル `gpt-6-astra`（`-m gpt-5.5` でも）で「ChatGPT のアカウントでは使えない」と拒否され、サンドボックスの中での `flock` は確かめられていない。

### 保存と同期

- パスの指定で子のScopeを除外したコミットは、ほかの変更やステージを残したまま成功する。
- `git merge` は、関係のないファイルに未保存の編集があっても成功する。取り込む変更が編集中のファイルに当たると、何も壊さずに止まる。何かがステージされていると止まる。
- `git rebase` は未保存の編集があると拒否する。
- `git merge-tree --write-tree` は作業ツリーに触れずに統合結果を作り、競合なら終了コード1を返す。種類（内容、変更と削除、移動先の提案）も返す。
- 統合結果を一時インデックスで直し、`commit-tree` でマージコミットにして `merge --ff-only` で反映すると、編集中のほかのファイルは残る。
- 先着優先の解決（同じ名前には先に push された版、後から push する側の版は別名）で、先に push したPCと、すでに取り込んでいたPCでは、文書が変わらず、別名ファイルが増えるだけだった。
- 2台が同じ移動とリンクの書き換えを同時に行っても、競合しない。片方の移動ともう片方の中の編集は、移動先に統合される。古い場所に足したファイルも、移動先に置かれる。
- 変更と削除がぶつかると、変更が残る。
- 退去費用プロダクトの `pre-commit` フックは、共通のフックとしてカタログのworktreeでも動き、設定ファイルがないので毎回失敗する。`-c core.hooksPath=/dev/null` で外せる。

### 履歴とブランチの関係

- `git subtree split` で切り出した canonical は、main と共通の祖先を持たず、`git merge main` は `refusing to merge unrelated histories` で拒否される。ファイルの中身（blob）は同じオブジェクトを指す。
- 移行前のブランチ（既存の仕様を変更）を、仕様のツリーを消した main にマージすると「変更と削除」の競合になる。新しい仕様を足しただけのブランチは、競合せずに main に仕様のファイルを入れてしまう。
- 移行前のブランチの仕様は、分岐点と同じツリーを持つ canonical のコミットを親にしたコミットを作れば、3者マージで canonical に取り込める。その後、ブランチから仕様のツリーを消して main を取り込むと、PRは仕様を含まずにマージできる。
- 仕様を含む未マージのPRは、2026-10-25 時点で spec-dock も退去費用も0件。spec-dock の作業用worktreeは4つ。

### GitHub と実データ

- chemitaro は個人アカウント（`User`）。Issue types は組織向けで、`issueType` は null。
- sub-issue と依存（blocked by）の API は使える。両リポジトリとも、登録された親子と依存は0件（spec-dock は Issue 数件、退去費用は100件で確認）。
- sub-issue は親1件につき100件、深さ8段まで（公式文書）。今の最大は子33件、深さ3段。
- spec-dock は公開リポジトリで、ルールセットは0件。退去費用は非公開で、ルールセットの取得が「Upgrade to GitHub Pro or make this repository public」で拒否される。push のパスの制限は Team プランの非公開リポジトリ向け。
- 退去費用の今のCIは、GitHub ではマージを止めていない（2026-10-25、`gh api`）。
  - 既定のブランチ `develop` は `protected: false` で、保護されたブランチは0件。ブランチに効くルールの取得（`rules/branches/develop`）も、上と同じ文言で拒否される。
  - 開いているPRのうち #1900、#1805、#1768 は `mergeStateStatus` が `UNSTABLE`、`mergeable` が `MERGEABLE`（GitHub の定義では「通っていない検査があるが、マージできる」）。#1900 と #1805 では、`Test and Deploy for Staging` が失敗している。
  - 直近にマージされた40件のPRは、マージの時点で、最後のコミットのPRのワークフローがすべて成功していた（#2189、#2173 は、一度失敗した後に成功してからマージ）。失敗したPRをマージしないことは、運用で守られている。
- Scope は spec-dock 243件、退去費用 246件。依存は135本（最大6）と284本（最大12）。種類と親子は Initiative → Epic → Issue の3段で固定（`src/spec_dock/runtime/infra/scope_tree.py` も同じ）。`lifecycle` はすべて null、`revision` はほぼ0。
- 退去費用の GitHub Issue 751件のうち、Scope は246件。ほかに Scope でない Issue が多い。
- `.meta.json` の題名はすべて英語。GitHub の題名と食い違うものが36件と62件あり、GitHub 側が日本語のものが24件と51件。
- 今の CLI は題名に `^[A-Za-z0-9]+(?: [A-Za-z0-9]+)*$` しか受け付けない（日本語を拒否）。`--slug` は別に受け付ける。`work start` の既定のブランチ名は `<ID>-<slug>`。
- `init-local-00002` は #39、`init-local-00003` は #31 に結び付く。#31 は題名が別物（"Replace Wrapper Scripts With Symlink Rules"）で、完了で閉じている。そのため、その下に新しい Epic を作れない（`GitHub Scope ancestor is not open`）。
- テンプレートの要件定義書は、作成時の題名を `タイトル:` として写す。
- `spec-dock worktree create` は、プロジェクトの初期化（`make init`）を暗に実行しない。初期化は、別のコマンド `spec-dock worktree bootstrap` が、明示したworktreeで1回だけ実行する。
- 今の CLI は、`spec-dock/dashboard.md` を生成しない（2026-10-25 訂正）。`render_dashboard`（`src/spec_dock/runtime/presentation/markdown.py`）はあるが、どこからも呼ばれていない。`workspace sync` は「Writes: None」の読むだけのコマンドである。spec-dock の `spec-dock/dashboard.md` は、2026-09-21 に古い版が生成したものが残っている（Git では無視）。
- ワークスペースの宣言 `spec-dock/workspace.json` は、`schema_version: 3` と `writer_protocol` を持つ。今の CLI は、版が整数の3でないと `PRECONDITION_FAILED`（終了コード3）で止まる（`src/spec_dock/runtime/application/project_context.py`）。

### 今の排他

- `StartLock` は、`work start`、ブランチの切り替え、リンクの書き込みが共有するクローン単位の排他。共通の `.git` ディレクトリに `flock` をかけ、ファイルを作らない。既定の待ち時間は5秒。
- `create.lock` は、worktreeごとの `spec-dock/system/.runtime/create.lock` で、600秒で古いと見なす。
- launchd の `WatchPaths` は、説明書で「変更を取りこぼすことがある」として非推奨。launchd は既定で同じジョブを10秒に1回までしか起動しない。

### 設計の検証（2026-10-25、macOS、codex-cli 0.163.0）

- **Codex のサンドボックスと `flock`**：`codex sandbox -- …`（seatbelt、`~/.codex/config.toml` の workspace-write）の中で、書き込みが拒否される場所（mainの `.git` と `spec-dock/`）でも、ディレクトリを読み取りで開いて `flock(LOCK_EX|LOCK_NB)` を取れた。サンドボックスの外のプロセスが同じディレクトリに `flock` を持つ間、中からは取れず（BUSY）、逆も同じだった。外したあとは取れた。
- **サンドボックスでの書き込みの可否の判定**：サンドボックスの中では、書けない場所への `os.access(path, W_OK)` が False を返した。環境変数 `CODEX_SANDBOX=seatbelt` が設定されていた。
- **launchd からの push の認証**：一時的なジョブ（`launchctl bootstrap gui/<uid>`）で、Homebrew の git から `git push --dry-run` を実行すると、`~/.gitconfig` の `credential.https://github.com.helper = !/opt/homebrew/bin/gh auth git-credential`（利用者の `gh` のログイン）で認証できた。資格情報を外すと「could not read Username」で失敗したので、dry-run でも認証が要ることも確かめた。リモートには何も作られていない。launchd のジョブの `PATH` は既定で `/usr/bin:/bin:/usr/sbin:/sbin` で、`GH_TOKEN` はない。
- **launchd と外付けのボリューム（macOS のプライバシーの保護）**：launchd のジョブから外付けのボリューム `/Volumes/990p2t` を読めるかは、実行するプログラムごとに決まった。`/bin/sh`、`/usr/bin/python3`、`/usr/bin/git`（Apple の git）は「Operation not permitted」で拒否され、uv の Python（spec-dock のパッケージが使う `cpython-3.12.11`）と Homebrew の git は読めた。許可は、以前に利用者が与えたものと考えられる（推測）。
- **launchd の設定ファイルの置き場**：外付けのボリューム（所有者の情報が無効）に置いた plist は、`launchctl bootstrap` が「5: Input/output error」で拒否した。内蔵のディスク（`/private/tmp`）に置くと受け付けた。そのため、ジョブの plist は `~/Library/LaunchAgents/` に置く。ログの出力先も内蔵のディスクにする。
- **既存のジョブ**：利用者の `~/Library/LaunchAgents/` には、外付けのボリュームを使う自作のジョブ（nestboard、CI の VM の監視）がすでにある。
- **GitHub の REST API**（公式文書、2026-10-25）：
  - sub-issue：`GET /repos/{owner}/{repo}/issues/{n}/sub_issues`、`POST …/sub_issues`（本文は `sub_issue_id`。Issue の番号ではなく `id`。任意で `replace_parent`）、`DELETE …/issues/{n}/sub_issue`（本文は `sub_issue_id`）、`GET …/issues/{n}/parent`（親がなければ404）。
  - 依存：`GET …/issues/{n}/dependencies/blocked_by`、`POST …/dependencies/blocked_by`（本文は `issue_id`。番号ではなく `id`）、`DELETE …/dependencies/blocked_by/{issue_id}`、`GET …/dependencies/blocking`。
  - 追加と削除は、速すぎると二次のレート制限にかかると書かれている。
  - Issue の一覧（`GET /repos/{owner}/{repo}/issues`）の各要素にも、`sub_issues_summary` と `issue_dependencies_summary` が入っている（実測）。一覧にはPRも入るので、`pull_request` のある要素を除く。
- **今のCLIの構造**（`src/spec_dock/runtime/`、調査用のエージェントによる読み取り）：
  - コマンドはすべて `commands/runtime_dispatch.py` の `dispatch()` を通る。コマンドの一覧は `cli/catalog.py` の `LEAF_PATHS`（44個）。
  - GitHub は `infra/github_lifecycle.py` の `GithubIssueGateway` が `gh api`（REST）で扱い、操作は取得・作成・状態の変更だけ。ラベル、sub-issue、依存、題名の変更、一覧はない。再試行もない。
  - `.meta.json` を読む場所と書く場所は、`infra/scope_tree.py`、`infra/scope_metadata.py`、`application/direct_scope_*.py`、`application/direct_dependencies.py`、`application/direct_finish.py`、`application/start_snapshot.py` など。
  - 今のCLIは、リンクの `spec-dock/initiatives` を拒否する（`infra/scope_tree.py:53-57`、`application/scope_query.py:51,60-62`）。`work start` は基点のコミットのツリーから `.meta.json` を読む（`application/start_snapshot.py:92-144`）。`workspace validate --ci` は、HEAD のツリーに `spec-dock/initiatives` の実体があることを求める。
  - Scope の作成は、`spec-dock/.agent/staging` に作ってから移す（`application/direct_scope_publish.py`）。
  - `create.lock` を作る処理は、もうない。
  - 配布は wheel だけで、`pyproject.toml` の版は 0.2.4。git の URL からの導入の手順はない。
  - CI の「CI」（`.github/workflows/ci.yml`）は、ソースから wheel を作り、`workspace validate --ci --json` を実行する。

## Reflection

- 上の事実は、Epic の要件定義書の「背景」「制約・前提」「失敗・境界条件」と、設計書の各論の根拠として書き直す。
- Codex のサンドボックスの中での `flock` と、launchd からの `push` の認証は、2026-10-25 に macOS で確かめた（上の「設計の検証」）。まだ確かめていないのは、Linux（systemd のユーザーのタイマーと、そこからの push）で、実装の Issue で確かめる。
