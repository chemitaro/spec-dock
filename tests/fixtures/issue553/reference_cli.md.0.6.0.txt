# CLI参照（Current）

通常packageの外部 `spec-dock` が公開61 leafの入口です。正確な文法は `spec-dock help COMMAND` または `spec-dock COMMAND --help` で確認します。通常Scope TARGETとGitHub取込用REFは別の文法です。曖昧な対象は副作用前に拒否します。

| 用途 | 入力 | 境界 |
|---|---|---|
| 通常Scope TARGET | 完全Scope ID、`gh:OWNER/REPO#NUMBER`、各leafで許可された`@current`／`@initiative`／`@epic`／`@issue` | 裸番号・Issue URL・任意filesystem pathは使えません。対象の存在と選択状態は別途検査します。 |
| `scope import github KIND REF` | 完全gh ref、完全GitHub Issue URL、または裸番号＋`--github-repo OWNER/REPO` | repositoryを暗黙推定しません。矛盾するhintや別repositoryは拒否します。 |
| Artifact所有者 | Scope selectorに加えて許可されたArtifact操作の`@root` | `@root`をScope作成やStartの対象にはできません。 |

新規ScopeはGitHub番号が正本です。Requirement・Design・Planが一次仕様、Artifactは証拠、Workbenchは一時作業です。Syncはその時点の観測で、派生状態を保存しません。

SpecDock 0.5.0 は宣言の版4（canonical モード）だけを扱います（版3の宣言では、`canonical check` のほかのどのコマンドも `CANONICAL_NOT_MIGRATED` で止まります。移し方は[導入・移行・保全](migration.md)）。Scope のディレクトリは `spec-dock/initiatives/<区切り>/<ID>/`（区切りは番号の千ごとの範囲。例 `00000-00999/iss-00454/`）に平らに並びます。ID は `<種類>-<番号5桁>` で、入力は0埋めしなくてよく（`iss-454`）、slug はありません（`scope create` と `scope import github` に `--slug` の引数はありません。`scope import github` の `--title` は使わずに GitHub の題名で進め `CANONICAL_TITLE_IGNORED` を警告します）。題名は GitHub の題名が正本、親子と依存は GitHub だけにあり、場所と親子は `scope show <ID> --json` で確かめます。`work start` の既定のbranch名は `<ID>` です。canonical モードの用意、ツールの設定、エラーのコードと次の1手の一覧は[canonical モードの使い方](canonical.md)にあります。

業務コマンドの対応OSはLinuxとmacOS、Pythonは3.10以上です。その他のOSではproject解決やGit/GitHub・file操作より前に `UNSUPPORTED_PLATFORM` / exit3 / effects=[]を返します。help・version・completionはこの業務判定やOS固有の依存を読み込まず利用できます。

## 全コマンド

共通optionの--project ABSは正確なworktree root、--jsonはv2 envelopeです。--dry-runは計画のみ、--yesはCLI確認の省略です。必要なguardを迂回しません。applyで保全を要求するleafは外部の新しい--backup-dir ABSを使います。

| ID | Command / leaf | 引数・固有option | 対象と効果 | 主な副作用 |
|---|---|---|---|---|
| C01 | `scope create initiative` | `--backend github --title TITLE --assurance LEVEL --assurance-reason TEXT` | GitHubで番号を発行してInitiativeを作り、`templates/cue/initiative/`からカタログに置きます。 | GitHub作成、カタログのScope |
| C02 | `scope create epic` | `--backend github --parent TARGET --title TITLE --assurance LEVEL --assurance-reason TEXT` | 明示したInitiativeの下にEpicを作ります。 | GitHub作成、カタログのScope |
| C03 | `scope create issue` | `--backend github --parent TARGET --title TITLE --assurance LEVEL --assurance-reason TEXT` | 明示したEpicの下にIssueを作ります。 | GitHub作成、カタログのScope |
| C04 | `scope import github initiative` | `GITHUB_REF --title TITLE [--github-repo OWNER/REPO] --assurance LEVEL --assurance-reason TEXT`（`--title`は使わずGitHubの題名で進めます） | 既存Issueを確認してInitiativeへ取り込みます（足りない種類のラベル、親子、カタログのディレクトリだけを足します）。 | GitHubのラベル・親子、カタログのScope |
| C05 | `scope import github epic` | `GITHUB_REF --parent TARGET --title TITLE [--github-repo OWNER/REPO] --assurance LEVEL --assurance-reason TEXT`（同上） | 既存IssueをEpicへ取り込みます。 | GitHubのラベル・親子、カタログのScope |
| C06 | `scope import github issue` | `GITHUB_REF --parent TARGET --title TITLE [--github-repo OWNER/REPO] --assurance LEVEL --assurance-reason TEXT`（同上） | 既存IssueをIssue Scopeへ取り込みます。 | GitHubのラベル・親子、カタログのScope |
| C07 | `scope list` | `[--kind {initiative,epic,issue}] [--parent TARGET] [--state {open,completed,not-planned,unknown}]` | 構造のスナップショットのScopeを、カタログの場所とともに表示します。 | 読取りのみ |
| C08 | `scope show` | `TARGET` | GitHubの題名、親子、状態、カタログの場所、保証レベルを表示します。 | 読取りのみ |
| C09 | `scope edit` | `TARGET --title TITLE` | GitHub Issueの題名だけを変更し、ID、ディレクトリ、branchを保ちます。 | GitHubの題名 |
| C10 | `scope close` | `TARGET [--reason {completed,not-planned}]` | 対象のGitHub Issueを閉じます。reason既定はcompletedです。completedで閉じるときは、子孫がすべてcompletedかnot-plannedなら閉じられ、openまたは状態が分からない子孫が1つでもあれば`DESCENDANT_NOT_COMPLETED`で止まります。 | GitHub状態 |
| C11 | `scope reopen` | `TARGET` | 対象だけをopenへ戻します。 | GitHub状態 |
| C12 | `scope delete` | `TARGET [--recursive] [--clear-active] [--detach-dependencies] [--backup-dir ABS]` | 種類のラベルと親子（と、明示すれば依存）を外し、保全してからカタログのディレクトリを削除します。Issueとbranchは消しません。 | GitHubのラベル・親子、backup、カタログ |
| C13 | `active show` | 共通optionのみ | 一つの直接記録と現在の祖先を表示します。 | 読取りのみ |
| C14 | `active set` | `TARGET` | 現在の妥当な直接対象と同じなら選択はunchangedで、ずれた閲覧用active linkだけを揃えます。空/別対象はWORK_START_REQUIREDで停止します。 | active linkのみ |
| C15 | `active clear` | `--from TARGET` または `--all` | 捕捉した直接記録だけを解除し、未選択ならactive linkをfallbackへ揃えます。 | selection、active link |
| C16 | `work start` | `TARGET [--branch NAME] [--base REF] [--switch-active] [--source github]` | live readiness後、短い排他内で重複再確認・branch作成/checkout・直接対象公開を行い、排他の後でactive linkを揃えます。schema4の既定branch名は`<ID>`で、作業中の印を付け、別のPCの印があれば警告`SCOPE_IN_PROGRESS`を返します。 | Git、worktree局所selection、active link |
| C17 | `work finish` | `TARGET` | 完了確認後に捕捉selectionだけ解除し、branchに留まります。解除したらactive linkをfallbackへ揃えます。閉じる前に仕様の保存とpushを最大180秒待ち、確かめられなければ`CANONICAL_SAVE_UNCONFIRMED`で閉じずに止まります。 | GitHub完了、selection、active link |
| C18 | `branch show` | `TARGET [--name NAME]` | 現在のref/占有を観測します。対応台帳は保存しません。 | 読取りのみ |
| C19 | `branch create` | `TARGET [--name NAME] --base REF` | 固定baseからbranchを作り、checkoutしません。既存refをresetしません。 | Git ref |
| C20 | `branch switch` | `TARGET [--name NAME]` | 同cloneのStart lock内でbranchへcheckoutし、selection取得/解除は行いません。lockを--lock-timeout内に取れなければSTART_LOCK_BUSYで止まります。 | Gitのみ |
| C21 | `dependency list` | `TARGET [--view {declared,effective}]` | 宣言/継承依存を表示します。 | 読取りのみ |
| C22 | `dependency check` | `TARGET [--source github]` | readinessと根拠を観測します。既定は構造のスナップショット、`--source github`は取り直してから判定します。 | 読取りのみ |
| C23 | `dependency add` | `--from TARGET --to TARGET` | fromがtoを前提とするblocked-byをGitHubに足します。重複はunchangedです。 | GitHubの依存 |
| C24 | `dependency remove` | `--from TARGET --to TARGET [--missing-ok]` | 指定のblocked-byをGitHubから外します。 | GitHubの依存 |
| C25 | `artifact create` | `--scope ARTIFACT_SCOPE --type {blank,research,interview,disc,decision-candidate,adr} --title TITLE [--slug SLUG]` | templateから一件のMarkdownをno-replace公開します。 | Artifact |
| C26 | `artifact import file` | `PATH --scope ARTIFACT_SCOPE` | 一件のregular fileをopaque evidenceとして保存します。 | Artifact |
| C27 | `artifact list` | `--scope ARTIFACT_SCOPE` | 識別情報だけを一覧表示します。 | 読取りのみ |
| C28 | `artifact show` | `ARTIFACT_ID --scope ARTIFACT_SCOPE` | path/type等を表示し、本文を出力しません。 | 読取りのみ |
| C29 | `worktree create` | `NAME --base REF [--root ABS]` | native root/NAMEとworktree/NAME branchを作ります。bootstrapは別です。 | native Git |
| C30 | `worktree list` | 共通optionのみ | 同じphysical cloneのnative inventoryを表示します。 | 読取りのみ |
| C31 | `worktree show` | `ABS` | 一つのnative worktreeを表示します。 | 読取りのみ |
| C32 | `worktree remove` | `ABS [--unlock] [--discard-ignored]` | 明示作業場を除去し、branchを残します。 | native Git、対象directory |
| C33 | `worktree bootstrap` | `ABS` | project-owned make initを一回実行します。 | 任意project処理 |
| C34 | `workspace sync` | `[--source github] [--allow-invalid]` | 複数WTの予約・論理active・祖先とlifecycleを都度観測します。 | 読取りのみ |
| C35 | `workspace validate` | `[--require-nodes]` | 構造のスナップショットとカタログのディレクトリ・文書を照らして検証します。CIでは`canonical check`を使います。 | 読取りのみ |
| C36 | `workspace doctor` | `[--raw] [--legacy] [--github-repo OWNER/REPO --github-pr NUMBER --github-head-sha SHA] [--github-extended]` | 明示した現在/旧状態・capabilityをread-only診断します。 | 読取り、明示時GitHub照会 |
| C37 | `installation show` | `[--target ABS]` | package版と一つのWTのstatic資産分類を表示します。 | 読取りのみ |
| C38 | `installation init` | `ABS` | 未導入WTへ静的資産と新writer宣言を置きます。 | static資産、workspace |
| C39 | `installation update` | `[--target ABS] [--backup-dir ABS]` | 既知static資産だけを保全して更新・個別退役します。 | 外部backup、static資産 |
| C40 | `installation uninstall` | `[--target ABS] [--backup-dir ABS]` | 既知static資産だけを保全・削除し、workspace/ignore/ユーザー成果を残します。 | 外部backup、static資産 |
| C41 | `help` | `[COMMAND PATH]` | 現在helpを表示します。repository不要です。 | 出力のみ |
| C42 | `completion` | `{bash,zsh,fish}` | 補完をstdoutへ返し、shell設定を変更しません。 | 出力のみ |
| C43 | `canonical check` | `[--commit REV]` | 指定commit（既定HEAD）のtreeに仕様のpath・`.meta.json`がなく、版4の宣言・static資産・ignore規則が揃うかをCI向けに検査します。問題はpathと次の1手付きでexit7です。workflow見本は `docs/ci/spec-dock-check.yml` です。 | 読取りのみ |
| C44 | `canonical link` | `[--no-schedule]` | このcloneのカタログ（mainの`spec-dock/.canonical`）を探すか作ってlockし、除外の3行を足し、mainとこのチェックアウトの`spec-dock/initiatives`をカタログへのリンクにし、定期の同期に登録します（登録簿、定期の実行、基準）。`--no-schedule` は登録せず基準だけを記録します。何度実行しても同じ結果です。 | カタログのworktree、`info/exclude`、リンク、状態の置き場、定期の実行 |
| C45 | `canonical status` | 共通optionのみ | カタログ、リンク、除外、読み書きの可否、ツールの設定の1行、定期の同期、未保存と保留、形式、git、構造のスナップショットを示し、問題ごとに次の1手を示します。GitHubに問い合わせません。 | 読取りのみ |
| C46 | `canonical sync` | `[--registered] [--state-root PATH] [--loop [--detach]]` | カタログの保存、取り込み、pushを1回行います（強制pushしません）。`--registered` は登録簿のすべてのカタログを処理し、`--loop` はsystemdのない環境の常駐のプロセスとして60秒ごとに動きます。日常は定期の実行が動かします。 | カタログのcommit、push、状態の置き場 |
| C47 | `canonical accept` | `[PATH...] [--deletions]` | 保留した変更（秘密情報らしいもの、大きすぎるファイル、大量の削除）を、次の同期で保存してよいと記録します。中身が変われば効きません。 | `.runtime/accepted.json` |
| C48 | `canonical restore` | `[PATH...]` | 保留中のパス（パスなしは保留中の削除）を、カタログのHEADの内容に戻します。commitしません。 | カタログの作業ツリー |
| C49 | `canonical resume` | `--adopt-remote` \| `--push-local` | 一時停止したカタログの同期を、利用者が決めた扱いで再開します。 | 状態の置き場、`--push-local` はpush |
| C50 | `canonical remove` | `[--yes]` | 未保存と未pushがないことを確かめてから、このcloneのリンク、カタログ、除外、定期の同期の登録を外します。ブランチは消しません。 | リンク、カタログ、`info/exclude`、状態の置き場、定期の実行 |
| C51 | `scope move` | `TARGET --parent TARGET` | ScopeのGitHubの親だけを付け替えます（sub-issueの`replace_parent`）。カタログの平らなディレクトリは動きません。このチェックアウトが対象かその子孫を選んでいれば`spec-dock/active`のリンクを整えます。schema3では`CANONICAL_NOT_MIGRATED`で止まります。 | GitHubの親子、active link |
| C52 | `scope check` | `TARGET` | 1つのScopeの仕様をインターネットなしで検査します。CUEのScope（`requirement.cue`）は、型・リポジトリの型（`spec-dock/cue/*.cue`）と一緒に`cue`（v0.17.1以上）で評価し、形の誤り（`CUE_INVALID`）、つながりの指摘（`SPEC_FINDINGS`）、保証レベルの置き場、説明資料の形を、ファイルと直し方つきで示します。誤りがあれば終了コード7（`SCOPE_CHECK_FAILED`）。MarkdownのScopeは`checked=false`で成功します。`work finish`も閉じる前に同じ検査をします。schema3では`CANONICAL_NOT_MIGRATED`で止まります。 | 読取りのみ |
| C53 | `scope render` | `TARGET [--design-system MODE]` | 1つのCUEのScopeの要件・設計・計画を、インターネットなしでHTMLに描き、標準出力に出します（`--json`では`data.result.html`）。`scope check`と同じ評価を使い、検査の結果（つながりの指摘、形の誤り）をページの初めに、続けて要件、失敗・境界条件、設計、計画（手順の状態と数、実行の割り当て）を、番号のリンクで結んで示します。デザインシステムはそのチェックアウトの`spec-dock/design-system/`を`file:`のURLで、図の部品はCDNから読みます。`--design-system inline`（既定は`file`）では、`ds.css`、`ds.js`、`marked`をHTMLに埋め込み、別のPCでも崩れないページにします（デザインシステムがなければ`DESIGN_SYSTEM_MISSING`、終了コード3）。評価が通らなければ検査の結果だけのページで成功し`SCOPE_RENDER_INCOMPLETE`を警告します。MarkdownのScopeは終了コード7（`SCOPE_NOT_CUE`）。ダッシュボードなどは、Pythonの入口`spec_dock.runtime.application.scope_render.render_scope_html(ScopeRenderSource, *, design_system_base, vendor_base)`で、読み込み先のURLを渡して描けます（`timeout`秒、既定30。`embed_design_system`にデザインシステムのディレクトリを渡すと埋め込みます。返り値はHTMLの`str`。MarkdownのScopeは`CanonicalCommandError`の`SCOPE_NOT_CUE`、`cue`と型の版の問題は`scope check`と同じコードで止まります）。schema3では`CANONICAL_NOT_MIGRATED`で止まります。 | 読取りのみ |
| C54 | `dashboard summary` | `[REPOSITORY]` | 1つのリポジトリのダッシュボードの要約（契約 `specdock.dashboard-summary/v1`）を返します。チェックアウトの中ではREPOSITORYを省けます（`origin`から決めます）。外では`owner/name`か`github.com/owner/name`で指します。利用者ごとの状態の置き場の構造のスナップショット（版1と版2）を自分で読み、GitHubにもダッシュボードのサーバーにも要求を送りません（在りかの記録の`pid`が生きているかだけを見ます）。サーバーが動いていなくても、隠したリポジトリでも動きます。`--json`では`data.result`が要約です。スナップショットがなければ`DASHBOARD_SNAPSHOT_MISSING`、壊れていれば`DASHBOARD_SNAPSHOT_UNREADABLE`、知らない版なら`DASHBOARD_SNAPSHOT_UNSUPPORTED`（どれも終了コード3）、REPOSITORYの形が違えば`DASHBOARD_REPOSITORY_INVALID`（終了コード2）。 | 読取りのみ |
| C55 | `dashboard serve` | `[--port N] [--tailscale] [--state-root ROOT]` | 利用者ごとに1つのダッシュボードのサーバーを前面で動かし、Ctrl-CかSIGTERMで止まります。登録簿の、`repository`が分かり隠していない全リポジトリを`/r/<host>/<owner>/<name>/`で、見るだけで配ります（登録の追加と隠す印の変更は、起動し直さずに現れます）。既定は`127.0.0.1`の番号47800だけに待ち受け（`--port`で変え、0は空いた番号）、`--tailscale`では`tailscale ip -4`の住所にも待ち受けます（`0.0.0.0`には待ち受けず、Tailscaleの設定を変えません）。起動のときに、標準エラーにURLと見せるリポジトリの一覧を書きます。すでに動いていれば、そのURLを示して終了コード0で終わります（`already_running`）。番号が使われていれば`DASHBOARD_PORT_IN_USE`、Tailscaleの住所がなければ`DASHBOARD_TAILSCALE_UNAVAILABLE`（どちらも終了コード3）。`--state-root ROOT`は状態の置き場を絶対の道で指します（相対の道は`DASHBOARD_STATE_ROOT_INVALID`、終了コード2）。GitHubにもほかのネットワークにも要求を送りません。 | 状態の置き場の`dashboard/server.json`・`server.lock`・`seen.json` |
| C56 | `dashboard hide` | `[REPOSITORY]` | そのリポジトリをダッシュボードの表示から外します（一覧、横断の概況、Tailscaleで見せる範囲）。直接のURLには、戻すコマンドの案内だけを返します。定期の同期は止まりません（同期も止めるのは`canonical remove`）。チェックアウトの中ではREPOSITORYを省けます。印の置き場が読めなければ`DASHBOARD_STATE_UNREADABLE`（終了コード3）で止まり、上書きしません。 | 状態の置き場の`dashboard/repositories.json` |
| C57 | `dashboard show` | `[REPOSITORY]` | `dashboard hide`で外したリポジトリを表示に戻します。 | 状態の置き場の`dashboard/repositories.json` |
| C58 | `dashboard list` | | 登録簿の各行の、リポジトリ（分からなければ`null`）、表示中か隠しているか、配れるか、サーバーのURL（動いていれば）を示します。 | 読取りのみ |
| C59 | `dashboard service install` | `[--port N] [--tailscale]` | ログインのときにダッシュボードのサーバーを起動し、落ちても起動し直す常駐を入れます（macOSはlaunchdの`~/Library/LaunchAgents/io.github.chemitaro.spec-dock.dashboard.plist`、Linuxはsystemdのユーザーの単位`spec-dock-dashboard.service`）。定期の同期の常駐とは別のもので、同期の常駐には触りません。`canonical link`や`installation update`はこの常駐を入れません。実行ファイルは同期の常駐が記録したもの（なければ今の`spec-dock`）。同じ設定ならなにもせず（`unchanged`）、`--port`か`--tailscale`を変えて実行し直すと書き直して起動し直します（`updated`）。番号は1〜65535（既定47800。外れれば`DASHBOARD_PORT_INVALID`、終了コード2）。launchdもsystemdのユーザーの管理もなければ何も書かずに`DASHBOARD_SERVICE_UNSUPPORTED`（終了コード3、`dashboard serve`を案内）、`launchctl`か`systemctl`が失敗すれば`DASHBOARD_SERVICE_FAILED`（終了コード3）。`--dry-run`はありません。 | 常駐の設定のファイルと登録、状態の置き場の`dashboard/` |
| C60 | `dashboard service status` | | 常駐が入っているか（`installed`）、管理の側に読み込まれているか（`loaded`）、サーバーが動いているか（`running`、在りかの記録の`pid`）、URL、設定の番号とTailscaleと状態の置き場、動いているサーバーの版と入っているパッケージの版（違えば`restart_pending`）を示します。常駐を入れられないPCでは`supported: false`です。 | 読取りのみ |
| C61 | `dashboard service uninstall` | | 常駐を止め（`launchctl bootout`か`systemctl --user disable --now`）、設定のファイルと`dashboard/service.log`を消します。入っていなければ`removed: false`で成功します。同期の常駐、隠す印、「見た」の記録には触りません。`--dry-run`はありません。 | 常駐の設定のファイルと登録、`dashboard/service.log` |

ARTIFACT_SCOPEの@rootはArtifact所有者だけで、Scope作成/Startの対象ではありません。通常操作はworkspaceの版4の新writer宣言を検証します。help/version/completion、raw doctor、installation、canonical checkは各leafの限定的なcontextを使います。

## Start・Finishと排他

新規branchのStartには--base REF、既存branchの再利用には明示--branch NAMEとbase省略が必要です。GitHub照会は短いStart排他の外です。排他内で同cloneの予約を再観測し、checkoutから直接記録公開まで保持します。`branch switch`もcheckoutから確認までStart lockを保持し、active linkの書込みと排他します（--lock-timeout、既定5秒）。同じbranchの重複checkoutはGitが、同じIssue・ノードの重複選択はStart排他内の再観測（SCOPE_ALREADY_SELECTED、branch名ではなくScope IDとGitHub番号で比較）が防ぎます。Start lockはGit共通dirへのOS flockだけで、Gitへファイルや設定を書きません。SpecDockを経由しないGit操作と別cloneは排他の対象外です。通常編集、Artifact、Sync、Finish、migration、installationは共通Start lockを取りません。

同一direct target/branchのStartはunchangedです。別branchへ移った予約、破損/複数記録も重複検査から捨てません。active setは同じ妥当な直接対象の確認と閲覧用active linkの修復だけで、新規取得や親への切替は行いません。active linkは選択の正本ではなく、失敗してもwarningだけで選択の結果を変えません。clearはselectionだけ、FinishはGitHub完了を確認してから解除します。後から始まった別対象は消さず、元branchへ戻りません。

## ダッシュボードの要約の契約（`specdock.dashboard-summary/v1`）

`dashboard summary`とダッシュボードのサーバー（`/api/v1/r/<host>/<owner>/<name>/summary`）が返す要約の形です。項目を足すのは版を変えずに行い、消すか意味を変えるときは版を上げます。

| 項目 | 意味 |
|---|---|
| `schema` | `specdock.dashboard-summary/v1` |
| `repository` | `github.com/<owner>/<name>` |
| `fetched_at`、`stale` | 構造を取得した時刻（UTC）と、30分を超えて古いか |
| `counts` | `total`、状態ごとの数 `by_state`（`done`、`doing`、`blocked`、`ready`、`unknown`）、種類ごとの数 `by_kind`（`initiative`、`epic`、`issue` の各 `total` と状態ごとの数） |
| `completion_ratio` | 終わった数／全体の数（Scopeがなければ`null`） |
| `awaiting_merge`、`in_progress`、`ready`、`blocked` | ボードの列の一覧（推奨順）。各要素は`id`、`number`、`kind`、`title`、`state`、`reason`。`awaiting_merge`は`merge`（`mergeable`か`needs_fix`）を足します。`in_progress`はマージ待ちを除きます |
| `cleanup` | 片付けの候補（推奨順）。`reason`は候補の理由、`cleanup`は種類（`all_descendants_closed`、`closed_with_open_descendants`、`open_under_closed_parent`） |
| `anomaly_count` | スナップショットに記録された構造の異常の数 |
| `pull_requests` | PRの状態の確かさ：`status`（`fresh`、`stale`は直近の取得の失敗で前回の値、`unknown`は版1・未取得・30分超で使わない）、`fetched_at`、`error` |
| `paths` | 各Scopeの詳しい画面の道 `/r/<host>/<owner>/<name>/scopes/<ID>` |
| `hidden`、`server` | 表示から隠しているか、動いているサーバーの手元のURL（なければ`null`） |

状態は`dependency check`と同じ着手の判定から決め、EpicとInitiativeだけ、開いた子孫に作業中の印があれば作業中にします。

## ダッシュボードのサーバーの契約

`dashboard serve`のサーバーが守る約束です。項目を足すのは版を変えずに行い、消すか意味を変えるときは版を上げます。画面の中のJSON（`/api/v1/r/…/structure`と`scopes/<ID>`）と、表示の切り替えの問い合わせは契約にしません。

- **画面の道**：`/`（横断の概況）、`/r/<host>/<owner>/<name>/`（ホーム）、`…/graph`、`…/board`、`…/timeline`、`…/scopes/<ID>`。`/r/<host>/<owner>/<name>/scopes/<ID>`と`?embed=1`は変えません。
- **API**：`GET /api/v1/repositories`、`GET /api/v1/r/<host>/<owner>/<name>/{summary|structure|scopes/<ID>|revision}`（`schema: "specdock.dashboard/v1"`）。`summary`は上の`specdock.dashboard-summary/v1`で、`dashboard summary`と同じ内容です（データがなければ同じコードで503）。APIにはCORSの見出しを付けません。
- **受け付けるもの**：`GET`、`HEAD`と、「見た」の口の`POST`だけ（ほかは405）。`Host`が`127.0.0.1`、`localhost`、TailscaleのIP、MagicDNSの名前と待ち受けの番号の組でなければ421。
- **資料**：カタログのScopeのディレクトリの通常のファイルを`/r/<host>/<owner>/<name>/files/<ID>/<道>`から配り、すべての応答に`Content-Security-Policy: sandbox allow-scripts allow-popups; frame-ancestors <埋め込みの許可>`と`X-Content-Type-Options: nosniff`を付けます（リンク、`..`、ディレクトリは断ります）。`/ds/`（デザインシステム）と`/vendor/`（図の部品）だけに`Access-Control-Allow-Origin: *`を付けます。
- **枠の決まり**：通常の画面は`frame-ancestors 'self'`、`?embed=1`の画面と資料は`frame-ancestors 'self' http://127.0.0.1:* http://localhost:*`（Tailscaleで待ち受けるときは`http://<TailscaleのIP>:*`も）。`X-Frame-Options`は付けません。
- **在りかの記録（`specdock.dashboard-server/v1`）**：`<state_root>/dashboard/server.json`に`schema`、`urls.local`、`urls.tailscale`（なければ`null`）、`pid`、`version`、`started_at`。待ち受けを始めた後に書き、止まるときに消します。`pid`が生きていなければ古い記録です。二重起動は`dashboard/server.lock`で防ぎます。
- **隠す印（`specdock.dashboard-repositories/v1`）**：`<state_root>/dashboard/repositories.json`の`repositories: {<host/owner/name>: {hidden_at}}`。書くのは`dashboard hide`と`show`だけです。
- **「見た」の記録（`specdock.dashboard-seen/v1`）**：`<state_root>/dashboard/seen.json`に、リポジトリごとに直近の5件（`seen_id`、`seen_at`、各Scopeの`{state, pr}`）。`POST /api/v1/r/<host>/<owner>/<name>/seen`は、`Origin`がサーバー自身の起点と完全に一致し、`X-SpecDock-Dashboard: 1`と`Content-Type: application/json`がある要求だけを受けます（ほかは403）。中身は読まず、サーバーがそのときのモデルから記録します。`structure?baseline=<seen_id>`はその記録と比べた変化を返します。
- **埋め込みの約束（`specdock.embed/v1`）**：知らせは`{source: "specdock"|"host", v: 1, type, …}`。親は枠の`load`のたびに`hello`を送ります。SpecDockは、`event.source`が親の窓で、起点が埋め込みの許可に合う`hello`を受けたら、その起点を覚えて`ready {repository, path, title, capabilities}`を返し、続けて今の画面の`navigated {path, title, scope}`を1回送ります。その後は画面を移るたびに`navigated`です。親は`navigate {path}`と`theme {scheme: "light"|"dark"|"auto"}`を送れます。SpecDockは`hello`の前は何も送らず、覚えた起点だけを`targetOrigin`にします。高さは親が決めます。

## ダッシュボードの常駐の契約

`dashboard service install`が入れる常駐の約束です（言い直した約束3：常駐は利用者が明示して入れたときだけ入り、`status`で見え、`uninstall`で何も残さず消えます）。

- **動かすもの**：`<spec-dock> dashboard serve --service --port <N> [--tailscale] --state-root <状態の置き場>`。`--service`は常駐のための内部の引数で、ヘルプには出しません。`--state-root`は前面の`serve`でも使えます（絶対の道）。
- **launchd**：ラベル`io.github.chemitaro.spec-dock.dashboard`、`RunAtLoad`、`KeepAlive`、`ThrottleInterval` 10、標準出力と標準エラーは`<状態の置き場>/dashboard/service.log`、`PATH`はgitとtailscaleの場所と`/usr/bin:/bin:/usr/sbin:/sbin`。
- **systemd**：`${XDG_CONFIG_HOME:-~/.config}/systemd/user/spec-dock-dashboard.service`、`Type=simple`、`Restart=always`、`RestartSec=10`、`WantedBy=default.target`。出力はjournal（`journalctl --user -u spec-dock-dashboard`）。systemdのユーザーの管理が一時的に応えないときも、単位があれば`status`に見え、`uninstall`で外せます。
- **前面の`serve`との共存**：`--service`のサーバーは、ほかのサーバーが`dashboard/server.lock`を持っていれば終わらずに30秒ごとに取り直して待ち、そのサーバーが止まれば引き継ぎます。待っている間のSIGTERMでは終了コード0です。前面の`serve`は、常駐が動いていればそのURLを示して終わります。
- **Tailscale**：`--service --tailscale`で住所が得られなければ`127.0.0.1`だけで起動し、30秒ごとに住所を取り直して、得られたら待ち受けと`Host`の検査と埋め込みの許可と在りかの記録の`urls.tailscale`に足します。
- **版の更新**：サーバーは60秒ごとに入っているパッケージの版を読み直します。`--service`のサーバーは、版が変わっていれば在りかの記録を消して終了コード75で終わり（CLIのJSONは書きません）、launchdとsystemdが新しい版で起動し直します。前面の`serve`は終わらず、標準エラーに1回知らせ、`/api/v1/repositories`の`server`に`installed_version`と`restart_required: true`を出します。

## JSONと途中失敗

v2はschema_version、command、status、exit_code、data、effects、warnings、error、recoveryです。operation IDや固定engine digestを通常authorityにしません。exit6のeffectsはsucceeded/unknown/not_attemptedを区別します。Gitのargv/stdout/stderr/returncodeを隠蔽せず、unknownなremote結果を成功や未実施と断定しません。

Artifact create/importは `data.result.artifact.path` を使います。Syncは `data.complete`、`data.worktrees`、`data.scopes`、`data.counts` 等を返し、process_state=not_observedです。正確な各data形状は現在helpと実JSONを確認してください。

## 導入・移行

詳細は[移行ガイド](migration.md)です。package更新は外部環境だけ、static更新は明示WTだけに作用します。未知改変fileはmanual merge、旧writer停止や復元確認の不足は適用停止です。廃止されたcache/stale、engine pin/maintenance/finalize、registry alias、resume/rollbackの操作を再導入しません。

Finishの成功と実装・検証・PR・mergeの完了は別の証拠です。
