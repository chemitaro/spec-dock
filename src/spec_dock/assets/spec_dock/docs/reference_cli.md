# CLI参照（Current）

通常packageの外部 `spec-dock` が公開44 leafの入口です。正確な文法は `spec-dock help COMMAND` または `spec-dock COMMAND --help` で確認します。TARGETはScope ID、GitHub番号/ref、URL、許可されたdynamic selectorから一意に解決します。曖昧な対象は副作用前に拒否します。

新規ScopeはGitHub番号が正本です。Requirement・Design・Planが一次仕様、Artifactは証拠、Workbenchは一時作業です。Syncはその時点の観測で、派生状態を保存しません。

## 全コマンド

共通optionの--project ABSは正確なworktree root、--jsonはv2 envelopeです。--dry-runは計画のみ、--yesはCLI確認の省略です。必要なguardを迂回しません。applyで保全を要求するleafは外部の新しい--backup-dir ABSを使います。

| ID | Command / leaf | 引数・固有option | 対象と効果 | 主な副作用 |
|---|---|---|---|---|
| C01 | `scope create initiative` | `--backend github --title TITLE [--slug SLUG]` | GitHubで番号を発行してInitiativeを作ります。 | GitHub作成、ローカルScope |
| C02 | `scope create epic` | `--backend github --parent TARGET --title TITLE [--slug SLUG]` | 明示したInitiativeの下にEpicを作ります。 | GitHub作成、ローカルScope |
| C03 | `scope create issue` | `--backend github --parent TARGET --title TITLE [--slug SLUG]` | 明示したEpicの下にIssueを作ります。 | GitHub作成、ローカルScope |
| C04 | `scope import github initiative` | `GITHUB_REF --title TITLE [--slug SLUG] [--github-repo OWNER/REPO]` | 既存Issueを確認してInitiativeへ取り込みます。 | GitHub読取り、ローカルScope |
| C05 | `scope import github epic` | `GITHUB_REF --parent TARGET --title TITLE [--slug SLUG] [--github-repo OWNER/REPO]` | 既存IssueをEpicへ取り込みます。 | GitHub読取り、ローカルScope |
| C06 | `scope import github issue` | `GITHUB_REF --parent TARGET --title TITLE [--slug SLUG] [--github-repo OWNER/REPO]` | 既存IssueをIssue Scopeへ取り込みます。 | GitHub読取り、ローカルScope |
| C07 | `scope list` | `[--kind {initiative,epic,issue}] [--parent TARGET] [--state {open,completed,not-planned,unknown}]` | 現在treeのScopeを表示します。 | 読取りのみ |
| C08 | `scope show` | `TARGET` | metadata、親子、未観測を含む状態を表示します。 | 読取りのみ |
| C09 | `scope edit` | `TARGET --title TITLE` | titleだけを変更し、ID/linkageを保ちます。 | metadata |
| C10 | `scope close` | `TARGET [--reason {completed,not-planned}]` | 対象backendを閉じます。reason既定はcompletedです。 | GitHub状態、既存local互換状態 |
| C11 | `scope reopen` | `TARGET` | 対象だけをopenへ戻します。 | GitHub状態、既存local互換状態 |
| C12 | `scope delete` | `TARGET [--recursive] [--clear-active] [--detach-dependencies] [--backup-dir ABS]` | 明示したローカルsubtreeだけを保全・削除します。GitHub/branchは削除しません。 | backup、明示対象 |
| C13 | `active show` | 共通optionのみ | 一つの直接記録と現在の祖先を表示します。 | 読取りのみ |
| C14 | `active set` | `TARGET` | 現在の妥当な直接対象と同じならunchangedです。空/別対象はWORK_START_REQUIREDで停止します。 | 変更なし |
| C15 | `active clear` | `--from TARGET` または `--all` | 捕捉した直接記録だけを解除します。 | selectionのみ |
| C16 | `work start` | `TARGET [--branch NAME] [--base REF] [--switch-active] [--source github]` | live readiness後、短い排他内で重複再確認・branch作成/checkout・直接対象公開を行います。 | Git、worktree局所selection |
| C17 | `work finish` | `TARGET` | 完了確認後に捕捉selectionだけ解除し、branchに留まります。 | GitHub完了、selection |
| C18 | `branch show` | `TARGET [--name NAME]` | 現在のref/占有を観測します。対応台帳は保存しません。 | 読取りのみ |
| C19 | `branch create` | `TARGET [--name NAME] --base REF` | 固定baseからbranchを作り、checkoutしません。既存refをresetしません。 | Git ref |
| C20 | `branch switch` | `TARGET [--name NAME]` | branchへcheckoutし、selection取得/解除は行いません。 | Gitのみ |
| C21 | `dependency list` | `TARGET [--view {declared,effective}]` | 宣言/継承依存を表示します。 | 読取りのみ |
| C22 | `dependency check` | `TARGET [--source {local,github}]` | readinessと根拠を観測します。既定local、未観測GitHubはunknownです。 | 読取りのみ |
| C23 | `dependency add` | `--from TARGET --to TARGET` | fromがtoを前提とするedgeを追加します。重複はunchangedです。 | metadata |
| C24 | `dependency remove` | `--from TARGET --to TARGET [--missing-ok]` | 指定edgeを除きます。 | metadata |
| C25 | `artifact create` | `--scope ARTIFACT_SCOPE --type {blank,research,interview,disc,decision-candidate,adr} --title TITLE [--slug SLUG]` | templateから一件のMarkdownをno-replace公開します。 | Artifact |
| C26 | `artifact import file` | `PATH --scope ARTIFACT_SCOPE` | 一件のregular fileをopaque evidenceとして保存します。 | Artifact |
| C27 | `artifact list` | `--scope ARTIFACT_SCOPE` | 識別情報だけを一覧表示します。 | 読取りのみ |
| C28 | `artifact show` | `ARTIFACT_ID --scope ARTIFACT_SCOPE` | path/type等を表示し、本文を出力しません。 | 読取りのみ |
| C29 | `worktree create` | `NAME --base REF [--root ABS]` | native root/NAMEとworktree/NAME branchを作ります。bootstrapは別です。 | native Git |
| C30 | `worktree list` | 共通optionのみ | 同じphysical cloneのnative inventoryを表示します。 | 読取りのみ |
| C31 | `worktree show` | `ABS` | 一つのnative worktreeを表示します。 | 読取りのみ |
| C32 | `worktree remove` | `ABS [--unlock] [--discard-ignored]` | 明示作業場を除去し、branchを残します。 | native Git、対象directory |
| C33 | `worktree bootstrap` | `ABS` | project-owned make initを一回実行します。 | 任意project処理 |
| C34 | `workbench copy` | `--scope TARGET --to-worktree ABS [--on-conflict {error,overwrite}]` | 同じScopeの一時作業を一回コピーします。 | 宛先Workbench |
| C35 | `workspace sync` | `[--source {local,github}] [--allow-invalid]` | 複数WTの予約・論理active・祖先とlifecycleを都度観測します。 | 読取りのみ |
| C36 | `workspace validate` | `[--require-nodes] [--ci]` | working treeまたは固定HEADの構造を検証します。 | 読取りのみ |
| C37 | `workspace doctor` | `[--raw] [--legacy] [--github-repo OWNER/REPO --github-pr NUMBER --github-head-sha SHA] [--github-extended]` | 明示した現在/旧状態・capabilityをread-only診断します。 | 読取り、明示時GitHub照会 |
| C38 | `workspace migrate` | `--to-schema 3 --to-writer-protocol specdock.worktree-writer/v1 [--backup-dir ABS] [--confirm-old-writers-stopped]` | 一つのschema3 workspace宣言だけを保全・切替します。 | 外部backup、workspace宣言 |
| C39 | `installation show` | `[--target ABS]` | package版と一つのWTのstatic資産分類を表示します。 | 読取りのみ |
| C40 | `installation init` | `ABS` | 未導入WTへ静的資産と新writer宣言を置きます。 | static資産、workspace |
| C41 | `installation update` | `[--target ABS] [--backup-dir ABS]` | 既知static資産だけを保全して更新・個別退役します。 | 外部backup、static資産 |
| C42 | `installation uninstall` | `[--target ABS] [--backup-dir ABS]` | 既知static資産だけを保全・削除し、workspace/ignore/ユーザー成果を残します。 | 外部backup、static資産 |
| C43 | `help` | `[COMMAND PATH]` | 現在helpを表示します。repository不要です。 | 出力のみ |
| C44 | `completion` | `{bash,zsh,fish}` | 補完をstdoutへ返し、shell設定を変更しません。 | 出力のみ |

ARTIFACT_SCOPEの@rootはArtifact所有者だけで、Scope作成/Startの対象ではありません。通常操作はworkspaceの新writer宣言を検証します。help/version/completion、raw doctor、installation show/init、CI validateは各leafの限定的なcontextを使います。

## Start・Finishと排他

新規branchのStartには--base REF、既存branchの再利用には明示--branch NAMEとbase省略が必要です。GitHub照会は短いStart排他の外です。排他内で同cloneの予約を再観測し、checkoutから直接記録公開まで保持します。通常編集、Artifact、Sync、Finish、migration、installationは共通Start lockを取りません。

同一direct target/branchのStartはunchangedです。別branchへ移った予約、破損/複数記録も重複検査から捨てません。active setは同じ妥当な直接対象へのno-opだけで、新規取得や親への切替は行いません。clearはselectionだけ、FinishはGitHub完了を確認してから解除します。後から始まった別対象は消さず、元branchへ戻りません。

## JSONと途中失敗

v2はschema_version、command、status、exit_code、data、effects、warnings、error、recoveryです。operation IDや固定engine digestを通常authorityにしません。exit6のeffectsはsucceeded/unknown/not_attemptedを区別します。Gitのargv/stdout/stderr/returncodeを隠蔽せず、unknownなremote結果を成功や未実施と断定しません。

Artifact create/importは `data.result.artifact.path` を使います。Syncは `data.complete`、`data.worktrees`、`data.scopes`、`data.counts` 等を返し、process_state=not_observedです。CI validateは固定snapshot_oidを返します。正確な各data形状は現在helpと実JSONを確認してください。

## 導入・移行

詳細は[移行ガイド](migration.md)です。package更新は外部環境だけ、static更新は明示WTだけに作用します。未知改変fileはmanual merge、旧writer停止や復元確認の不足は適用停止です。廃止されたcache/stale、engine pin/maintenance/finalize、registry alias、resume/rollbackの操作を再導入しません。

既存true-local metadataのread/Finish互換性は、新規local Scope作成を許すものではありません。Finishの成功と実装・検証・PR・mergeの完了は別の証拠です。
