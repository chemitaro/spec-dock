# CLI 参照（Current）

SpecDock の公開CLIは `scope`、`active`、`work`、`branch`、`dependency`、`artifact`、`worktree`、`workbench`、`workspace`、`installation` に操作をまとめます。この表は44個の実行可能なleafを示します。正確な引数と復旧オプションは、配布された外部 `spec-dock help COMMAND` または `spec-dock COMMAND --help` で確認してください。`TARGET` は明示的な Scope ID、GitHub Issue番号、またはURLを解決します。曖昧なら書込み前に拒否します。

`work start TARGET` は Initiative、Epic、Issue のいずれでも依存を検査し、対応branchへcheckoutしてそのScopeを選択します。`work finish TARGET` は対象を完了し、選択中ならその対象以下の選択を解除します。単なる選択変更は `active set TARGET`、単なる状態変更は `scope close TARGET`、branchのみの切替は `branch switch TARGET` を使います。これらの副作用を混同しないでください。

GitHubとlocal backendの状態は別のauthorityです。ScopeのRequirement、Design、Planが一次仕様、Artifactが採用前の証拠、`workspace sync` のindex/treeは再生成できる観測結果です。CLIの確認に `--yes` を使っても対象・依存・path等のガードは省略されません。

## 全コマンド

| ID | Command / leaf | 引数・固有option | 対象と効果 | 主な副作用 |
|---|---|---|---|---|
| C01 | `scope create initiative` | `--backend {github,local} --title TITLE [--slug SLUG]` | Initiativeを新規作成します。GitHub backendはIssueを新規作成します。 | 一次仕様、必要時GitHub |
| C02 | `scope create epic` | `--backend {github,local} --parent TARGET --title TITLE [--slug SLUG]` | 明示したInitiativeの下にEpicを作成します。 | 一次仕様、必要時GitHub |
| C03 | `scope create issue` | `--backend {github,local} --parent TARGET --title TITLE [--slug SLUG]` | 明示したEpicの下にIssueを作成します。 | 一次仕様、必要時GitHub |
| C04 | `scope import github initiative` | `GITHUB_REF --title TITLE [--slug SLUG] [--github-repo OWNER/REPO]` | 既存GitHub Issueを読取り確認してInitiativeを作成します。 | GitHub読取り、一次仕様 |
| C05 | `scope import github epic` | `GITHUB_REF --parent TARGET --title TITLE [--slug SLUG] [--github-repo OWNER/REPO]` | 既存GitHub Issueを明示した親のEpicとして取り込みます。 | GitHub読取り、一次仕様 |
| C06 | `scope import github issue` | `GITHUB_REF --parent TARGET --title TITLE [--slug SLUG] [--github-repo OWNER/REPO]` | 既存GitHub Issueを明示した親のIssueとして取り込みます。 | GitHub読取り、一次仕様 |
| C07 | `scope list` | `[--kind {initiative,epic,issue}] [--parent TARGET] [--state {open,completed,not-planned,unknown}]` | 現在のworktreeに存在するScopeを安定したID順で表示します。 | 読取りのみ |
| C08 | `scope show` | `TARGET` | 指定Scopeのmetadata、状態の出典、親子、branch対応を表示します。 | 読取りのみ |
| C09 | `scope edit` | `TARGET --title TITLE` | ローカルmetadataのtitleだけを変更します。 | 一次仕様 |
| C10 | `scope close` | `TARGET [--reason {completed,not-planned}]` | reason省略はcompleted、not-plannedは明示指定のみです。backendに従って終端状態を設定し、選択は変更しません。 | local状態またはGitHub |
| C11 | `scope reopen` | `TARGET` | 対象だけをopenへ戻します。選択もbranchも変更しません。 | local状態またはGitHub |
| C12 | `scope delete` | `TARGET [--recursive] [--clear-active] [--detach-dependencies]` | 指定したローカルScopeの所有物を削除します。GitHubは閉じません。 | 一次仕様、明示許可時の選択・依存 |
| C13 | `active show` | `` | worktree-localな選択チェーンと中心対象を表示します。 | 読取りのみ |
| C14 | `active set` | `(TARGET \| --from-branch)` | 対象と祖先を選択します。branchからの解決も明示操作だけです。 | 選択のみ |
| C15 | `active clear` | `(--from TARGET \| --all)` | 指定対象以下、または全階層の選択を解除します。 | 選択のみ |
| C16 | `work start` | `TARGET [--branch NAME] [--base REF] [--switch-active] [--source {github,cache}] [--allow-stale]` | 対象と依存を確認し、対応branchを作成またはcheckoutして選択します。 | Git、branch対応、選択、状態観測 |
| C17 | `work finish` | `TARGET` | 対象をcompletedにし、選択中なら対象以下だけを解除します。 | local状態またはGitHub、選択 |
| C18 | `branch show` | `TARGET` | canonical branchの対応、存在、利用worktreeを表示します。 | 読取りのみ |
| C19 | `branch create` | `TARGET [--name NAME] --base REF` | 明示baseからcanonical branchを作成して対応を登録します。checkoutしません。 | Git ref、branch対応 |
| C20 | `branch switch` | `TARGET` | 登録済みcanonical branchへcheckoutします。選択は変更しません。 | Gitのみ |
| C21 | `dependency list` | `TARGET [--view {declared,effective}]` | 依存元から前提対象へのedgeを表示します。 | 読取りのみ |
| C22 | `dependency check` | `TARGET [--source {github,cache}]` | 開始用readinessと根拠を表示します。 | 状態読取りのみ |
| C23 | `dependency add` | `--from TARGET --to TARGET` | fromがtoに依存するedgeを追加します。重複追加はno-opです。 | 依存metadata |
| C24 | `dependency remove` | `--from TARGET --to TARGET [--missing-ok]` | 指定edgeを除去します。不存在は既定でエラーです。 | 依存metadata |
| C25 | `artifact create` | `--scope TARGET --type {blank,research,interview,disc,decision-candidate,adr} --title TITLE [--slug SLUG]` | scope-localな文書をテンプレートから生成します。 | Artifact |
| C26 | `artifact import file` | `PATH --scope ARTIFACT_SCOPE` | 明示した単一regular fileをopaque evidenceとして保存します。 | Artifact |
| C27 | `artifact list` | `--scope ARTIFACT_SCOPE` | 所有Artifactの識別情報だけを一覧表示します。 | 読取りのみ |
| C28 | `artifact show` | `ARTIFACT_ID --scope ARTIFACT_SCOPE` | 識別情報、相対配置先、種別・authority観測を表示します。本文は出力しません。 | 読取りのみ |
| C29 | `worktree create` | `[NAME] --base REF [--root PATH]` | 明示baseから別のGit作業場を作ります。bootstrapしません。 | Git worktree、作業場登録 |
| C30 | `worktree list` | `` | 同じGit common directoryに属する作業場を表示します。 | 読取りのみ |
| C31 | `worktree show` | `WORKTREE_REF` | 指定作業場のbranch、状態、削除阻害要因を表示します。 | 読取りのみ |
| C32 | `worktree remove` | `WORKTREE_REF [--unlock] [--discard-ignored]` | 作業場を除去します。branchは残します。 | Git worktree、対象directory |
| C33 | `worktree bootstrap` | `WORKTREE_REF` | 明示承認された対象でmake initを実行します。 | 利用者projectの任意処理 |
| C34 | `workbench copy` | `--scope TARGET --to-worktree WORKTREE_REF [--on-conflict {error,overwrite}]` | 同じScopeの非正本作業領域を一回だけマージコピーします。 | 宛先Workbench |
| C35 | `workspace sync` | `[--source {github,cache}] [--allow-invalid]` | 生成状態を再構築します。activeは変更しません。 | 生成物、明示時GitHub読取り |
| C36 | `workspace validate` | `[--require-nodes]` | 仕様、依存、Artifact、schemaの整合性を検証します。 | 読取りのみ |
| C37 | `workspace doctor` | `[--github-repo OWNER/REPO --github-pr NUMBER --github-head-sha SHA] [--github-extended]` | 状態・運用・未完了journalを診断します。自動修復しません。 | 読取り、明示時capability probe |
| C38 | `workspace migrate` | `--to-schema VERSION [--mapping-file PATH]` | 停止中の全登録worktreeを計画に従ってデータ移行します。 | schema、制御状態、journal |
| C39 | `installation show` | `[--target PATH]` | engine、固定供給元、writer protocol、全作業場の導入状態を表示します。 | 読取りのみ |
| C40 | `installation init` | `PATH` | 未導入projectに現在実行中の固定distributionを導入します。 | ツール資産、初期制御状態 |
| C41 | `installation update` | `[--target PATH] (--version VERSION \| --commit SHA) [--maintenance]` | 固定供給元のimmutable bundleでツールをjournal付き更新します。 | ツール資産、導入journal |
| C42 | `installation uninstall` | `[--target PATH]` | ツール資産だけを除去します。仕様履歴を残します。 | ツール資産、導入journal |
| C43 | `help` | `[COMMAND PATH]` | 共通構造のヘルプを表示します。 | 読取りのみ |
| C44 | `completion` | `{bash,zsh,fish}` | 選んだshellの補完定義をstdoutへ出力します。shell設定fileは書きません。 | 出力のみ |

## 操作例

```sh
spec-dock scope create initiative --backend local --title "Platform"
spec-dock scope create epic --backend local --parent init-local-00001 --title "Authentication"
spec-dock scope create issue --backend local --parent epic-local-00001 --title "Refresh tokens"
spec-dock scope show iss-local-00001
spec-dock work start epic-local-00001 --base main
spec-dock active show
spec-dock dependency check epic-local-00001 --source cache
spec-dock workspace validate
spec-dock workspace sync --source cache
# 成果のdelivery確認後、明示した対象を完了する
spec-dock work finish epic-local-00001 --yes
```

`work finish` 自体はcommit、push、PR、merge、test、reviewの完了を保証しません。実際のIDとbranchはcreate/startの出力を使ってください。GitHub backendの作成・終了にはGitHubの副作用があります。

CIを新しい入口へ切り替える際は、固定commitのSHAを確認してworktree外にengineを構築し、そのdistribution digestを記録してから `spec-dock workspace validate --ci --json` を実行します。この経路はworkspace schema、Scope、依存、Artifactだけを読み、導入controlやactive選択を作成しません。導入済み作業場の検査には通常の `workspace validate` を使います。

## 配布と復旧

インストール済みCLIはworktree外の固定distributionから実行します。`spec-dock/scripts/spec-dock` はそのengineを参照する薄いshimです。更新は `installation update --commit SHA --maintenance --yes`、データ変換は `workspace migrate --to-schema 3 --yes` として別々に実行します。対象群の停止、backup、固定candidate、全worktreeのwriter protocol一致を先に確認してください。journalがpendingなら診断に従い、対象leafの `--resume OPERATION_ID` または `--rollback OPERATION_ID` を明示します。詳細は[移行・復旧](migration.md)を参照してください。

全登録worktreeの導入・schema移行後、`installation update --finalize --dry-run --json` で復帰条件を確認します。成功したら同じ固定engineから `installation update --finalize --yes --json` を実行します。制御状態の更新後に中断した場合は、出力またはcommon controlの `finalizations/` に残るoperation IDを確認し、`installation update --finalize --resume OPERATION_ID --yes` で完了記録を復旧します。復旧記録が未完了の間は通常の変更操作を拒否します。

[命名](reference_naming.md)・[依存](reference_deps.md)・[GitHub](reference_github.md)・[生成状態](reference_sync.md)・[worktree](reference_worktree.md)の参照と併せて使用してください。過去版の操作は[historical](historical/README.md)に隔離しています。
