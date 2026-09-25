---
種別: 設計書（Issue）
ID: "iss-00409"
タイトル: "SpecDock CLI Scope Active Work Redesign"
関連GitHub: ["#409"]
状態: "draft"
原稿状態: "Issue #409 正本へ採用・実装前"
最終更新: "2026-09-24"
依存: ["requirement.md"]
親: ["epic-00356", "init-local-00003"]
基準Repository: "chemitaro/spec-dock"
実装調査基準Branch: "codex/scope-start-finish-analysis"
実装調査基準Commit: "eeb3e5965f0cb42de9a24081bfaea15e27fd4451"
---

# SpecDock CLI 案Bの全面採用と安全な一括切替 — 設計

本書は[Requirement](requirement.md)を実現する構造・状態・interface・failure contractを固定します。受入条件はRequirementのACを参照し、実装順は[Plan](plan.md)に置きます。本書は Issue #409 の正本であり、親は Epic #356／Initiative init-local-00003 です。ここに現れる新しいfile名・schema・error codeは**実装する将来仕様**であり、現行コードに存在するとの主張ではありません。

採用済み方針は案Bです。前回答の公開版四段階移行を、今回の依頼に従い一つのcoordinated cutoverへ置換します。細部が未定だったbranch対応の保存先、write admission、状態理由、recovery option、JSON payloadを本書で具体化します。コマンド名は変更せず、`active set`を使用します。

Authoring根拠は添付のDesign GuideとIssue Design templateです。説明HTMLは本書の概念と操作を人間向けに展開する非正本資料です。

## 設計目標

構造の主眼は、一次状態と選択を分離し、単機能use caseを `work start/finish` で合成することです。GitHub・Git・複数fileを跨ぐ操作を物理的な単一transactionと偽らず、effectごとの結果を残します。file-basedの既存構造と安全なfilesystem操作を再利用し、汎用workflow engine、DB、daemon、message brokerは導入しません。

共通文法と型付き結果からhelp・JSON・completionを一貫して生成します。全writerは同一のadmission・locking・path保護を通り、parserやrendererの例外経路から副作用が抜けない設計にします。

## Current / Target

### D-01 根拠と検証の境界

GitHub connectorで指定branch refを今回直接取得し、tipが `eeb3e5965f0cb42de9a24081bfaea15e27fd4451` と完全一致しました。本書のCurrentはそのcommitと添付sourceに限ります。この基準時点では他branch、実端末のworktree、consumer一覧、当時のローカルactive、将来の配布SHAは確認していません。その後 Issue #409 を作成・開始し、本書をactive Issueの正本として採用しました。基準実装のテストを今回実行したとの主張もしません。

以下で `RT` は既存の `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/` を表す文書上の略記です。fileの存在と挙動の根拠は次のsource locatorです。すべて同じ基準commitに固定します。

| Source | 既存path / 根拠 | この設計に関係する現行の事実 |
|---|---|---|
| S01 | RT `cli/parser.py` 32–166、`cli/registry.py` | runtimeは15root系統・28leafです。scope/work/branch等の新体系はまだありません。 |
| S02 | RT `application/issue_lifecycle.py` 226–363 | startはIssueのみ、checkout→active→post-syncです。finishはactive Issueをcloseした後で全activeを解除します。 |
| S03 | RT `application/set_active.py` 235–387、`domain/tree.py` 79–106 | active setは選択だけです。祖先チェーンを作り、clearは全解除します。active更新はsnapshot/復元を持ちます。 |
| S04 | RT `application/close_node.py` 129–174、`application/delete_node.py` 1158–1437 | closeはGitHub link必須です。deleteはremote close barrierの後にローカル削除し、force時に依存/activeを変更します。 |
| S05 | RT `commands/new.py`、`commands/import_cmd.py`、`application/import_node.py` | newはGitHub作成が既定です。importは明示title、親省略はactive fallback、foreignを拒否します。 |
| S06 | RT `commands/sync.py`、`application/sync_state.py` | 通常syncはGitHub有効・branch由来active更新が既定です。post-mutation syncと通常syncの規則は異なります。 |
| S07 | RT `commands/worktree.py` 133–163、`application/worktree.py`、`scripts/spec-dock` | create後のterminal requestでmake検出/実行を行います。worktree生成は固定commit・descriptor/path保護を持ちます。 |
| S08 | RT `application/workbench.py`、`infra/fs_cli.py` | Workbenchは一回のsource-winsマージで、同scopeが両作業場に必要です。symlinkを辿らない境界があります。 |
| S09 | RT `domain/artifacts.py`、`application/import_file_artifact.py`、添付Artifact Guide | 六種のcreation catalogと、保存済みevidenceのopen-world validation、opaque importは別契約です。 |
| S10 | `src/spec_dock/cli.py`、`src/spec_dock/installer.py`、RT `commands/update.py` | package CLIはinstaller専用です。updateは未固定upstream経由で、現installerはnontransactionalです。六directory/versionに加え条件付き.gitignore更新があります。 |
| S11 | RT `domain/status.py`、`infra/contracts.py`、`infra/fs_repo.py` 359–430 | 現在はリンクなしのstatusがopenです。metadataはtype/id/親/github等で、local completion/新writer契約はありません。 |
| S12 | `pyproject.toml`、`Makefile`、`scripts/static_analysis/run.sh` | Python >=3.10、pytest、ruff、mypyです。`make lint`はstatic analysis scriptを呼び、`uv run pytest`が通常test入口です。 |
| S13 | 添付 `spec-dock/docs/authoring/*.md`、Issue templates、critical Completion Guide | Requirement/Design/Plan/Artifactのauthorityと責務を分離します。criticalのbackup/restore/停止・incident要件を適用します。 |

S10の補足: 「六directoryとversion以外は変更しない」という文書表現だけに従わず、実際のinstallerの `.gitignore` 例外も移行対象として扱います。SourceはGitHubの `blob/<基準Commit>/<path>` で追跡できます。

補助的な外部一次仕様（2026-09-24確認）: GitHub Docs「REST API endpoints for issues」のupdate-an-issue（`https://docs.github.com/en/rest/issues/issues#update-an-issue`）とGNU make Manual「Instead of Executing Recipes」「The shell Function」（`https://www.gnu.org/software/make/manual/make.html`）を、remote reasonとdry-runの安全境界の確認だけに使用しました。これらをrepositoryの現行実装の証拠にはしていません。

### D-02 Target architectureと信頼境界

```text
利用者 / agent / CI
       │ argv + explicit project
       ▼
信頼済み固定distributionの外部entrypoint
       │ common parser / target resolver / writer admission
       ▼
CommandSpec → typed Request → Application use case → typed Result
                                 │                   │
                      純粋Domain policy              ▼
                                 │              Text / JSON / Help
                                 ▼
                 Ports: local store / Git / GitHub / installer / clock
                                 │
                 Infra: guarded files / subprocess argv / network adapter
```

外部entrypointのengineはcheckout対象外の固定packageから読み込みます。**現在のworktree内のmoduleをsys.pathの先頭へ入れて実行する方式を、Git切替・更新を行う通常経路では使用しません。** repo-local `spec-dock/scripts/spec-dock` は同じ固定engineへ委譲するshimにします。これにより実行途中のcheckoutやself-updateで、次にimportするmoduleだけ旧版になる事故を防ぎます。

固定engineの絶対path・distribution digestは導入control recordで検証し、PATH探索で見つけた同名実行物へ無条件に委譲しません。初回導入・復旧ではworktree外の検証済みengineを利用します。source packageの開発時入口は一時fixtureのみを既定対象とし、実consumerへの導入はcandidateを固定した後に行います。

CIの新規checkoutには導入controlも作業場固有のactive選択もありません。CIは固定commitの供給元を別checkoutし、Git SHAを照合してからworktree外にengineを構築し、distribution digestを記録します。そのengineからのみ `workspace validate --ci` を実行します。この読み取り専用経路はworkspace schema、Scope、依存、Artifactを検証し、control・導入pin・active・generation・branch registryを検証対象に含めません。通常の `workspace validate` は導入状態を含む診断のままです。`--ci` はmutatorで受け付けず、CIの検証結果をwriter admissionの根拠にしません。切替時に旧 `sync` / `validate` のCI呼出しをこの経路へ更新します。

履歴branchの古いshimを直接Pythonで実行する利用者権限まで封鎖するものではありません。対応範囲はサポートする起動経路と停止手順です。旧agent、旧venv、旧task、shell aliasの起動経路を切替時に停止・更新します。旧branchはそのまま新writerで書けず、read-only調査または明示的な再導入/移行を必要とします。

## 責務・Interface

### D-03 レイヤーの責務

| 層 | 担当 | 禁止する責務 |
|---|---|---|
| CLI / commands | argvの厳密parse、共通flag、CommandSpec、legacy入力の説明付き拒否、Request生成 | filesystem/Git/GitHub変更、業務状態判定、文字列messageからexit決定 |
| Application | 対象解決snapshot、admission、検証順、確認、OperationPlan、journal、Ports呼出し、回復合成 | renderer呼出し、shell文字列の再実行、DomainへのOS依存持込み |
| Domain | 階層、selectorの構文型、lifecycle遷移、activeチェーン、依存、branch対応一意性、pure validation | path探索、clock呼出し、JSON I/O、subprocess、network |
| Infra | guarded store、atomic replace、fsync、lock、Git ref固定、GitHub状態/理由、source pin、subprocess実行 | 隠れたpost-sync、勝手なfallback、暗黙のforce、human prompt |
| Presentation | 結果のText/JSON/help変換、redaction、安定code、console output | 状態読取り直し、修復、対象再解決、partialを成功へ丸める処理 |
| 外部installer | 固定bundleのstage/検証/replace、全作業場の導入記録、journal/resume/rollback | 一次仕様の内容変更、schemaの暗黙migrate、未固定供給元実行 |

`work start` と `branch create/switch` / `active set` は共通の下位操作を使いますが、CLIの文字列を組み立てて再帰実行しません。`work finish` と `scope close` は共通CompletionPolicyとbackend gatewayを使い、finishだけが選択解除を合成します。

主要な型付き境界は以下です。名称は新設計です。

```text
CommandSpec(path, argument_schema, target_roles, effect_class, help_sections)
ResolvedTarget(requested, scope_id, kind, backend, metadata_revision, snapshot_id)
ResolvedSelection(worktree_id, revision, focus_id, initiative_id, epic_id, issue_id)
OperationPlan(command, targets, preconditions, ordered_effects, confirmation_policy)
OperationResult(status, data, effects, warnings, error, recovery, state_revision)
StatusObservation(state, authority, source, observed_at, remote_updated_at, stale)
```

CommandSpecとRequestは任意dictionaryではなく、command別に型付けします。backendはdiscriminated union、selectorはScope/ArtifactRoot/Worktree等の別型です。共通envelopeの `data` はcommand別payloadにし、汎用JSON blobをuse case内部の入力にはしません。

### D-04 完全な公開コマンド文法

業務leafは42、utilityは2です。次表が公開文法の完全な一覧です。列内の `|` は選択、`[]` は任意、`()`は排他です。共通optionはD-06で定義し、復旧用optionはD-16で限定します。新しいleafを別名で増やしません。

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


トップレベルの木は以下です。`scope create`や`import github`自体は実行leafではありません。

```text
spec-dock
├─ scope
│  ├─ create {initiative,epic,issue}
│  ├─ import github {initiative,epic,issue}
│  └─ {list,show,edit,close,reopen,delete}
├─ active {show,set,clear}
├─ work {start,finish}
├─ branch {show,create,switch}
├─ dependency {list,check,add,remove}
├─ artifact {create,import file,list,show}
├─ worktree {create,list,show,remove,bootstrap}
├─ workbench copy
├─ workspace {sync,validate,doctor,migrate}
├─ installation {show,init,update,uninstall}
├─ help
└─ completion
```

### D-05 TARGET・project・path解決

| selector | 正確な意味 |
|---|---|
| 完全Scope ID | `init-<数字>` / `epic-<数字>` / `iss-<数字>`、または `*-local-<数字>`。trim/lowercaseと数字の既存幅正規化だけを認め、文中抽出をしません。正の数字だけです。 |
| `gh:OWNER/REPO#NUMBER` | current repositoryに属する完全リンクでScopeを一意解決します。未取込ならnot foundです。 |
| `@current` | activeの `focus_id`。常にチェーンの最下位非null要素です。 |
| `@initiative` / `@epic` / `@issue` | current focusのkindに関係なく、その選択チェーンの該当欄です。不在はnot foundです。 |
| `@root` | Artifact import/list/show専用のroot配置先です。Scope/branch/work/dependency/Workbenchではエラーです。 |
| `wt:ID` | 登録されたstable worktree IDです。作成時のNAMEをaliasに持てますが、一意性はregistryで確認します。 |
| 絶対worktree path | 登録worktreeのcanonical directory identityと照合します。存在するだけの任意directoryは対象にしません。 |

`GITHUB_REF`は完全修飾ref、厳密な `https://github.com/OWNER/REPO/issues/NUMBER`、または `NUMBER` + `--github-repo OWNER/REPO` です。裸 `#NUMBER`、query/fragment付きURL、credentials、非github host、PR URLは拒否します。--github-repoとref双方指定時は一致必須です。originのrepository identityを読んで照合し、local-only projectのGitHub操作では同一性が確認できなければ拒否します。

`--project PATH`は通常操作のローカルprojectを選びます。省略時はCWDから最寄りのGit worktree rootを解決します。子directoryや親workspaceから勝手に別projectを選びません。repo-local shimも呼出し元を記録し、自分の設置projectと矛盾する指定は拒否します。

`installation --target PATH`は導入対象であり、--projectと同時指定して異なるrootならエラーです。initのPATHは必須です。update/uninstallはtarget省略時に解決済みproject rootを使用し、旧wrapperの「任意のCWD文字列を更新する」解釈を継承しません。Git外のtooling-only init/update/uninstallは可能ですが、Scope操作はGit repository内だけです。

Artifactの相対source PATHとmapping-fileは呼出し時CWD基準です。結果はrepository相対pathを優先し、Artifactの外部source絶対pathは出力しません。`--`以降を位置引数として扱い、optionに見えるfile名を安全に指定可能にします。

### D-06 共通flag・既定値・確認

| 共通flag | 契約 |
|---|---|
| `--project PATH` | D-05のproject解決です。 |
| `--json` | stdoutを単一envelopeにし、非対話を含意します。--yesは含意しません。 |
| `--non-interactive` | prompt・pager・editorを開きません。stdinは値収集に使わず、不足をcode 3で返します。stdin非TTYでも同じ扱いです。 |
| `--yes` / `-y` | 必要な最終確認だけを省略します。ガードを迂回しません。read-onlyでも無効な副作用は起こさず、不要flagとしてusage errorを返します。 |
| `--dry-run` | 変更leafだけで有効です。対象解決・検証・予定effectを返し、managed dataの書込み、journal作成、hook、Git ref変更はしません。確認は要求しません。 |
| `--offline` | SpecDock自身のnetwork接続を禁止します。必要なremote操作は変更前に拒否します。cache/localへの暗黙fallbackはしません。 |
| `--expect-current ID` | active focusの期待値です。非対話の変更でcurrent系selectorを一つでも使うと必須です。親selectorでもfocusのIDを渡します。 |
| `--expect-backend {github,local}` | 単一Scope対象の操作でbackendを照合します。create/importのようにbackend固定の入口では重複指定を拒否します。 |
| `--lock-timeout SECONDS` | 既定0秒、非負値です。write lock待ちの上限です。 |
| `--timeout SECONDS` | 外部call一回の上限です。既定30秒、bootstrapは既定300秒です。タイムアウト後の副作用有無を別に判定します。 |
| `--color {auto,always,never}` | Textのみ。JSONは常に色なしです。 |
| `--help` / `-h` | 全階層で処理します。--jsonと併用ならhelpも同じenvelopeのdataへ格納します。 |
| rootの `--version` / `-V` | commandより前に指定するengine version表示専用です。`installation update --version VERSION` は別のleaf optionであり、early parseで奪いません。--jsonとの併用もenvelopeにします。 |

rootのversion表示flagを除き、共通optionはleaf前後で認め、矛盾する重複、abbreviation、未定義flagを拒否します。singletonの同値重複は一つに正規化します。--jsonが `--` より前に指定されれば、後続のusage errorもJSONにします。

`source`既定は `work start=github`、`dependency check=cache`、`workspace sync=cache` です。ここでgithubは必要なGitHub-backed対象のみをlive観測する方針であり、完全local graphに対して無意味なnetwork callをしません。`--offline`と `--source github` は、GitHub-backed対象が一件でも必要ならエラーです。startをcacheで許可するには `--allow-stale` も必要です。unknownはallow-staleでも開始不可です。finish/close/reopenはGitHub backendならlive確認必須で、cache指定を公開しません。

確認が必要なのは、GitHub新規作成、close/reopen/finish、delete、worktree remove/bootstrap、Workbench overwrite、installation init/update/uninstall、schema migrateです。`--yes`は確認だけを省略し、`scope close`のreason省略がcompletedになる規則を変更しません。単純local create/edit/selection/dependency/branch/startは明示入力自体を操作意思と扱います。startの別作業切替は `--switch-active` を別途要求します。TTY確認では解決済みID・repository・write一覧を表示します。許可されていない操作への包括的なagent同意は作りません。

全current参照は一回のsnapshotで解決し、確認後に再解決しません。実行前にfocus/revision/各target revisionを再照合し、変化はcode 3 `STATE_CONFLICT`です。非対話の `--expect-current` は誤対象防止、内部revision checkは並行変更防止であり、別の役割です。

### D-07 個別read/write契約

**Scope create/import。** 三階層ともローカル仕様を生成します。github createはremote作成とローカル生成を別effectにします。全ローカル事前検証の後でremote作成し、remoteだけ成功した場合は同Issueのimportへ固定された回復を案内します。入力titleをremote titleから補完せず、既存リンクを重複生成しません。local IDはcommon registryのkind別high-water allocatorで発行し、予約済み/削除済みIDを再利用しません。独立clone間は同期しないため、merge前の一意性検証を必要とします。create/importは選択もbranchも変えず、暗黙GitHub全件syncもしません。

**Scope list/show/edit。** listはkind→numeric ID順、filterは完全一致です。--parentは直接の子に限ります。showは親子・backend・localまたはcache状態・branch対応・snapshotを返します。表示のためにremote refreshしません。title編集はローカルtitleのみ、既存slug/path/本文/frontmatterの一括置換はしません。空文字を拒否し、同値編集はno-opです。

**Delete。** 対象はcurrent worktreeのsnapshotです。他worktreeの仕様やactiveを変更しません。--clear-activeはそのsnapshot内の削除対象以下だけを解除し、--detach-dependenciesはそのgraphの境界edgeを列挙して除去します。別branchや履歴に同じScopeが存在し得るため、canonical branch対応と使用済みID予約は保持し、削除履歴をregistryに記録します。GitHub linkは削除意図の表示だけに使い、照会/closeは実行しません。

**Active。** completed Scopeを資料参照用に選ぶことは許可します。選択はlifecycleではありません。--from-branchはcanonical branch registryとの完全一致だけで解決し、branch名中の番号から推測しません。未登録・曖昧は無変更で失敗します。`active clear --from TARGET`でTARGETがチェーンにない場合は `unchanged`、不明なIDはnot foundです。解除後focusは残る最下位祖先で、snapshot不存在を勝手に別祖先で補いません。

**Dependency。** `from -> to` は「fromがtoのcompletedを必要とする」です。declaredはmetadataの直接edge、effectiveは祖先からの継承を含む開始用edgeです。親を依存先とした場合、その親自身のcompletedを必要とし、子の割合で置換しません。scope間の自己・循環・祖先/子孫への依存で完了不可能な関係は拒否します。typeの異なるノード間も、これらに反しなければ許可します。add/removeのlocal変更はderivedをdirtyにし、networkは呼びません。

**Artifact。** creation catalogは六種固定です。保存済みMarkdownは有効UTC timestamp・安全なbasenameならunknown typeも証跡として受理し、historicalの既存filenameも現行互換を保持します。新しい任意ラベルをtypeとして生成する機能は足しません。`artifact import file`は既存の安全なpublisherを再利用し、source保持・no overwrite・timestamp衝突のslot割当を維持します。list/show/import結果にsource本文/hash/byte count/外部source絶対pathを出しません。showは本文閲覧コマンドではありません。生成typeと保存済みauthorityの観測は別fieldにし、generic evidenceからauthorityを推定しません。

**Workbench。** sourceは--projectのcurrent worktree、destinationは--to-worktree、Scopeは同じIDで両側に存在する必要があります。local Scopeも新しい共通resolverで認めます。rootは対象外です。既定conflict errorはコピー前に全entryを検査して停止します。overwriteでは同type/file-symlinkの許可された上書きだけを行い、directory/file型衝突は拒否します。dest-only entryは残します。preflight後の競合はrevision/identity再検証で検出し、既にコピーした分はpartialにします。任意payloadの汎用rollbackを約束しません。相対symlinkをそのまま写すが辿らず、root/ancestor redirectは拒否します。

**Sync/Validate/Doctor。** syncは一次仕様と選択を変更しません。cacheはstaleと出典を保持します。`--allow-invalid`は安全に読める構造の診断用生成だけを許し、`valid=false`かつcode 7にします。path/identity/schema不明を強制突破しません。GitHub取得の一部失敗は旧観測をfreshにせず、不完全性を明示します。validateはfilesystem・metadata・依存・Artifact・controlの整合、doctorは導入状態・権限・lock・未完了journal等の運用診断です。doctorのGH三引数はall-or-none、extended単独も拒否します。repair flagは公開しません。

### D-08 Branch / Worktreeの具体契約

canonical branch対応は、tracked `.meta.json` に書きません。branch作成のためのmetadata変更がdirty状態を作り、直後のcheckoutを妨げる循環を避けるため、Git common directory配下の共有registryへ保存します。

初回候補は `<Scope ID>-<既存slug>` です。`--branch`（start）または`--name`（branch create）があればそれを使用します。不正ref・非ASCII候補に黙ってIDだけを代用しません。登録後に異なる名前を指定したら `CANONICAL_BRANCH_CONFLICT` です。同名branchの既存対応は保持し、別Scopeの登録を拒否します。

新規作成は --base必須で、commitに一度resolveして固定します。既存canonical branchには--baseを渡せず、resetもしません。branch createは常に新規作成操作です。既存branchを通常のbranch createでadoptする機能は公開せず、移行の明示mappingだけで既存対応を登録します。

registry未登録なのに候補branchが既に存在する場合は `BRANCH_ADOPTION_REQUIRED` で停止します。既存の名前から勝手に関連づけず、停止中の `workspace migrate --mapping-file` で明示adoptします。registered branchが消えた場合は `CANONICAL_BRANCH_MISSING` とし、new baseで勝手に再作成しません。refを既知commitへ復元するか、明示復旧mappingを停止中に適用します。title編集やuninstallで対応を失効させません。

start/switchは、変更前に新checkout先に対象のmetadata・親・対応schemaが存在すること、branchが他worktreeで使われていないこと、現在treeがcleanであることを確認します。検証からcheckoutまでのref差替えも再確認します。切替先graphが異なるときは開始条件をそのsnapshotで評価し、切替後に同じsnapshotを確認してactiveを書きます。targetがbaseに存在しないなら、まず利用者が仕様を適切なcommitへ含める必要があります。自動commit/cherry-pick/copyはしません。

`branch create`はcheckoutしないため、対象のmetadataをbaseへ含める条件は同じでも現在の無関係なdirty fileは破壊しません。start/switchはdirtyを拒否します。detached HEADからのnew startは明示baseがある場合だけ許可します。既存branchへのswitchも許可します。HEADのないrepositoryはcommit解決失敗です。

WorktreeはScopeとは独立した作業場です。`worktree create [NAME] --base REF`はbaseを固定し、運用branch `worktree/<stable-id>` を新規作成します。これはScopeのcanonical branchではありません。既存の同名branchを奪いません。NAME省略時はregistryで `wt1` から未使用名を予約し、明示NAME衝突は自動suffixで別名にせず拒否します。rootはoption、次に既存 `SPEC_DOCK_WORKTREE_ROOT` の順に解決し、絶対pathを要求します。現行の同一filesystem/descriptor保護を維持し、未対応環境では安全に停止します。

new worktreeのactiveは空です。baseが必要schema・導入protocolを満たさない場合は、通常の作業場生成を拒否し、旧branchからの移行はmaintenance操作へ分けます。createは利用者shellのCWDを変更しません。listはGit inventoryとcontrol registryを照合し、外部worktreeを読み取るだけで自動登録しません。未登録作業場への変更は拒否し、migration inventoryへ追加します。

createはGit効果より前に対象ID・alias・root・path・branch・commit・phaseをcommon controlの対象別記録へ永続化し、成功/部分失敗を記録します。途中停止後の同じ対象への通常再実行は拒否します。`worktree create --recover wtN` は同じ入力と、path・branch・Git worktree登録がすべて存在しないことを照合してから同じIDを再利用します。効果が残る場合は自動削除・自動再試行せず、記録を用いて対象ごとに診断します。

removeはmain/current/bare/missing-record、tracked dirty、untrackedを無条件に拒否します。lockedは--unlock、ignored payloadは--discard-ignoredを別途必要とします。--yesだけでは許可になりません。branchを削除せず、registryはworktreeをretiredとして残します。判定直後のinode/ref差替えを再照合し、別directoryを削除しません。

bootstrapは `make init` の実行を明示的に依頼するコマンドです。**make -nでもMakefile評価による任意処理が起こり得るため、dry-runでmakeを起動しません。** 適用時は既存make initの検出/実行をtrust済みconsumerで行い、未定義targetは `BOOTSTRAP_UNAVAILABLE` として返します。実行済みなら失敗/中断時の副作用不明をcode 6で返します。任意scriptのnetworkをsandboxなしに禁止できないため、--offlineとの併用は拒否します。stdout/stderrはcaptureし、JSON時はenvelopeへrawログを埋めず、sanitized summaryとexit codeを返します。

bootstrapの対象別記録が `running` または `partial` の間は同対象の再実行を拒否します。対象directoryの排他leaseにより実行中の回復操作も拒否します。operatorが子process停止と任意効果を確認した後、`worktree bootstrap TARGET --recover --yes` は記録を `reconciled` にするだけでhookを呼びません。再試行は別の明示操作です。無関係なScopeのwriteは停止しません。

## data / failure

### D-09 状態の分離と保存場所

以下のschema名とversionは新しい契約です。既存metadataのfieldを全面的に別名にせず、移行で認識したfieldを保持・拡張します。unknown user fieldsをround-trip保持し、重複したauthorityを作りません。

| 状態 | 将来の保存場所・権威 | 寿命 / 共有範囲 |
|---|---|---|
| workspace schema | 新設 `spec-dock/workspace.json`、schema_version=3、writer_protocol=`specdock.writer/v1` | tracked。各checkoutのschemaを宣言します。 |
| Scope構造 | 既存Scope directoryの `.meta.json`、schema_version=3、revision追加 | tracked。type/id/title/slug/parent/github/depends_onを保持します。 |
| local lifecycle | `.meta.json` の `backend="local"` と `lifecycle={state,revision,updated_at}` | tracked。current checkoutの一次状態です。 |
| GitHub lifecycle | GitHub Issue state+state_reasonが権威、metadataは `backend="github"` と既存github link | localに競合する完了値を保存しません。 |
| Active selection | 既存 `spec-dock/.agent/active.json` をschema3へ移行。focus_id・revision・worktree_id追加 | ignored、worktree-local。checkoutによる切替対象ではありません。 |
| 選択表示 | `spec-dock/active/`、context-pack、生成indexのactive表示 | activeのprojection。異なるrevisionならstaleです。 |
| GitHub観測cache | `.agent/` 内の専用status cache、観測時刻/理由/出典付き | 生成物。freshの根拠にはしません。 |
| Derived generation | `.agent/generations/<generation-id>/` + `.agent/generation.json` pointer | 一世代をstageし、pointerをatomic publishします。旧固定名はprojectionです。 |
| Repository control | Gitが返すabsolute common directory配下の新設 `spec-dock/control/` | 全linked worktreeで共有。Gitで追跡せず、通常updateで消しません。 |
| Branch / ID registry | control内 `registry.json` | scope→canonical branch、branch→scope、ID予約、高水位、worktree inventoryです。 |
| Operation journal | control内 `operations/<operation-id>/journal.json` と必要なbackup | phase、effect、pre/post revision、固定targetを保持します。 |
| Installer journal | control内 `installations/<operation-id>/`。Git外はtarget外のoperator指定領域 | 更新する六directoryの外に置きます。self-updateで消えません。 |

Scopeの内部backendは文字列discriminantです。githubでは `github.issue_number/repo_owner/repo_name` を必須とし、`lifecycle` はnullです。localではgithubはnull、lifecycleのstateは `open/completed/not-planned` のみです。`unknown`は観測の状態であり、localの保存可能値ではありません。新しいbackend間変換コマンドは作りません。

Activeのfocusは重複した別selectionではなく、チェーンから決まる値を検証のため保存したものです。空はfocus/各階層すべてnullです。`active set`やfinishによりrevisionが増え、同じ選択へのsetはno-opです。schema移行で空から架空のtargetを生成しません。

local lifecycleはGit追跡されるため、別branchでは別snapshotになり得ます。**writer互換性があることと、別branchの業務状態が自動同期されることは別です。** local completionを別branchへ反映するには通常のGit統合を行います。showはproject/worktree/HEADを返し、別branchの完了を共有cacheから偽装しません。GitHub backendは同じremoteを参照しますが、cache鮮度は別です。

branch registryは「このrepositoryで一つ」の対応です。独立cloneへのコピー時は、そのcloneのGit inventoryとtracked metadataから明示的に再登録します。ID allocatorはローカルに存在する参照可能な履歴と全登録worktreeの既存IDを初回に検査し、以降は予約ledgerを用います。独立clone同士の同時採番の世界的な一意性は保証しません。衝突はmerge/validateで拒否して人間に解決を求め、IDを黙って書き換えません。

### D-10 不変条件

| Invariant | 検証する条件 |
|---|---|
| INV-01 | Scope IDはrepository snapshot内で一意、kindとprefixは対応、階層はInitiative→Epic→Issueのみです。 |
| INV-02 | activeは一つの有効な祖先チェーンであり、focusは最下位非null欄と一致します。 |
| INV-03 | selectionを変える単機能操作はlifecycle/Gitを変えず、lifecycle単機能操作はselection/Gitを変えません。 |
| INV-04 | local/remoteのauthorityは排他的です。GitHub観測をlocal completionとして永続化しません。 |
| INV-05 | 親へのcompleted finish/closeを受理する時点では、既にcompletedへの同一理由closeであっても、現在観測した全子孫自身がcompletedです。open/unknown/not-plannedは通りません。 |
| INV-06 | 一Scopeに0または1 canonical branch、同branchに0または1 Scopeです。branch欠損は第二branchの作成理由になりません。 |
| INV-07 | new branchのbaseは固定commit、existing branchはresetしません。other worktree ownershipを奪いません。 |
| INV-08 | `--yes`や限定的な例外flagは、path safety/identity/child completion/循環検査を迂回しません。 |
| INV-09 | 同じcommon directoryのmutatorは同一writer protocolとcontrol epochを要求し、schema不一致で書込みません。 |
| INV-10 | D-16の復旧対象操作が残したpending/unknown blocking journalだけが通常writeをブロックし、固定操作の明示resume/rollbackまたはdiagnosticだけを許可します。復旧対象外のpartial/unknownは対象固有の安全確認・競合guardを維持しますが、common control全体をrecovery-requiredにしません。 |
| INV-11 | retryのtargetはoperation開始時の解決済みIDで固定し、@currentを再解決しません。 |
| INV-12 | read-only/help/parse failureは一次状態を変更せず、dry-runはmanaged writeとproject hookを実行しません。 |
| INV-13 | deleteはremote closeしない、syncはactive推定しない、worktree createはbootstrapしないという禁止effectを守ります。 |
| INV-14 | metadata/Artifact/Workbenchへの書込みは検証したroot・entry identity内だけです。unknown欄と非対象bytesを保全します。 |

INV-05は外部GitHub操作を禁止するglobal invariantではなく、SpecDockが完了操作を認める時点のpreconditionです。完了後に外部または別branchで子状態が変わった場合は診断対象として扱います。localで完了済み祖先の下へ新規子を作る/reopenする操作は拒否し、祖先を上から明示reopenしてから行います。GitHub-backed状態を必要とするstart/finish/close/reopenとgithub createではlive確認を行い、race後の不整合は観測して報告します。local createだけはnetworkを呼ばず、localまたは既存cacheの祖先状態を確認します。cacheがopenならstale警告付きで構造作成を許し、terminal/unknownなら拒否して明示syncを案内します。これは作業開始/完了のlive gateを緩めるものではありません。

### D-11 Lifecycleと選択の遷移

```text
localまたはGitHub authority
      open ──close completed / work finish──→ completed
        └──close not-planned──────────────→ not-planned
      completed / not-planned ──reopen────→ open

選択（lifecycleとは独立）
      空 ──active set I / work start I──→ (I, -, -)
      任意 ──active set E / work start E──→ (I, E, -)
      任意 ──active set Q / work start Q──→ (I, E, Q)
      (I,E,Q) ──finish Q──────────────→ (I,E,-)
      (I,E,-) ──finish E──────────────→ (I,-,-)
      (I,-,-) ──finish I──────────────→ (-,-,-)
```

図のI/E/Qは説明用の役割記号であり、実在IDではありません。

| 操作時の状態 | 結果 |
|---|---|
| finish対象がopen、全子孫completed | 対象をcompletedにし、選択チェーン内なら対象以下を解除します。 |
| finish対象が既にcompleted | 子孫条件を再確認し、remote書込みはno-op、未解除activeだけ処理できます。 |
| finish対象がnot-planned | reasonを黙ってcompletedに変えず拒否します。reopen後に明示finishします。 |
| close completed対象が同じcompleted | 現在の子孫状態にAC-11のcompleted guardを先に適用します。open、not-planned、unknownの子孫があれば拒否します。満たす場合だけremote lifecycle writeのないno-opとし、選択・Gitは変えません。 |
| closeで別の終端理由を指定 | `TERMINAL_REASON_CONFLICT`。reopenを挟みます。 |
| close not-plannedにopenの子がある | 親だけnot-plannedにできます。子は変更せず残ることを確認画面/JSONに表示します。親の正常finishは別で、子の正常完了を必要とします。 |
| 祖先がcompleted/not-plannedの子をstart/create/reopen | `ANCESTOR_TERMINAL`。祖先を必要な順でreopenします。 |
| finish対象が現在チェーン外 | その対象だけ完了します。他のworktreeのactiveも変更しません。 |
| activeが壊れている | 動的selector/通常selection変更は拒否します。明示all-clearまたはmigrationの承認済みrepairで復旧します。 |

GitHub adapterはIssue取得と更新のREST契約を使用し、PRを示すpull_request fieldがあれば拒否します。更新はstateとstate_reasonだけを送ります。`completed` はcompleted、`not_planned` はnot-planned、openは理由にかかわらずopenへ写像します。新しい `duplicate`、未知の理由、reasonを返さないclosed観測はunknown扱いとし、過去の `done` cacheだけからcompletedを断定しません。現行closed→doneという粗い写像からの意図的な変更です。

### D-12 開始readiness

対象Tの開始前提集合は、T自身とTの祖先に宣言された依存先の集合です。Issueではその実効依存を検査し、上位Scopeでも同じ集合を検査します。子孫にだけ宣言された依存は上位Scopeの開始ゲートへ持ち上げません。子孫の進捗は別のdiagnosticsとして表示します。

依存先が親Scopeなら、その親自身のcompletedを要求します。子Issueの全完了や割合は代替になりません。親Scope依存の完了条件が子の完了を必要とするため、ancestor/descendant間のedgeで自己待ちを作る入力は拒否します。全種別のraw edgeと、階層完了を含めた待ち関係の双方で循環を検査します。具体的には、全Scopeについて `node → effective prerequisite` と `parent → immediate child` を辺とするWaitGraphを構成し、DFSまたはSCCでcycleを拒否します。元のdeclared edgeは別に保持し、表示で人工的なcompletion edgeと区別します。

現在focusとstart対象が同じ、または一方が他方の祖先なら文脈内移動として許可します。兄弟などの別枝で、現在focusがopen/unknownなら--switch-activeが必要です。明示許可しても旧対象を完了しません。not-planned/completed focusから別作業への移動は許可します。branch名をactive guardの代わりに使いません。

### D-13 OperationPlan・lock・admission

各変更は「resolve/read → pure plan → human confirmation → admission/lock再確認 → effect実行 → durable結果」の順です。D-16の復旧対象操作だけはeffect前にblocking journalを準備します。復旧対象外ではatomic/CAS/identity-safe persistenceまたは操作固有のpartial/unknown診断を使い、全体停止するpending journalを作りません。確認中にwriter lockを占有せず、実行直前にsnapshot/revisionを再検証します。

controlの状態は `uninitialized / maintenance / ready / recovery-required` です。readyではschema3・writer/v1・承認済みengine digest・全登録active worktreeの互換性を要求します。maintenance中はinstallation/migrate/recoveryだけ、recovery-required中はD-16のblocking journal対象operationのdiagnosticと固定操作の回復だけを許可します。復旧対象外の失敗は対象・entry固有の競合を診断し、無関係な通常writeをglobalに止めません。環境変数一個によるlock bypassは設けません。

同一common directoryの通常mutatorは一つの共有advisory write lockで直列化します。単純さを優先し、短いmetadata操作の並列性を最適化しません。GitHubcallにはtimeoutを設定し、D-16の復旧対象操作では停止したprocessのlock解放後も未完了blocking journalで継続writeを防ぎます。その他の操作は原子的な公開、状態再観測、対象固有の衝突拒否で二重適用を避けます。pid文字列や経過時間だけでlockを削除しません。

複数作業場を触るcopy/update/migrateはcommon lockの後、stable worktree ID順にleaseを取得します。bootstrapは対象のshared lifetime leaseを維持し、common write lockを子process実行中ずっと保持しません。子process内の通常metadata操作は可能ですが、対象作業場のcheckout/remove/updateのexclusive leaseは失敗します。bootstrapから同じbootstrapを再帰実行する場合もbusyとして拒否します。

subprocessはargv配列で実行し、shell=True、eval、command substitutionでuser入力を実行しません。consumer hookだけが明示的な任意コード境界です。外部GitがSpecDockのlockを無視し得るため、lockだけを安全根拠にせずHEAD/ref/inodeの再照合を行います。

### D-14 JSON・終了コード・command data

全出力は `schema_version="specdock.cli/v1"` のenvelopeです。Textは同じ結果から生成します。statusは `succeeded / unchanged / planned / failed / partial` の五値です。effect statusは `planned / succeeded / unchanged / failed / not_attempted / unknown` です。失敗のdetailを読む前に、statusとcodeで制御できます。

```json
{
  "schema_version": "specdock.cli/v1",
  "command": "active.show",
  "status": "succeeded",
  "operation_id": null,
  "target": null,
  "data": {
    "focus_id": null,
    "initiative": null,
    "epic": null,
    "issue": null,
    "revision": 0
  },
  "effects": [],
  "warnings": [],
  "error": null,
  "recovery": null
}
```

これは空選択の**形式例**であり、実端末の観測結果ではありません。実際のdataにはproject/worktree/snapshot識別を共通に含めます。一般envelopeのtargetは `{requested, id, kind, backend, snapshot_id}`、複数roleの対象はdata.targetsへ格納します。機密性のあるraw argv/source pathをrequestedへ機械的に複写しません。

| command群 | dataの必須情報 |
|---|---|
| scope create/import/show/edit/close/reopen | `data.scope` にid/kind/backend/parent_id/path/revisionを格納します。`data.status` に観測state/source/staleを格納し、create/importでは作成/リンクした `data.github_ref` を追加します。 |
| scope list | `items`配列、filter、snapshot。0件は空配列です。 |
| active | focus/チェーン/revision/source、変更時before/after |
| work start/finish | 固定target、state_before/after、selection_before/after、branch_before/after、guard結果、derived_dirty |
| branch | canonical name/base commit/存在/他worktree owner/registry revision |
| dependency | from/toまたは一覧、declared/effective、ready/blockersとそれぞれのstate出典 |
| artifact | artifact_id、scope、relative path、creation_typeまたはgeneric、observed_authority。本文/元file hash/byte countは含めません。 |
| worktree | stable id/path/HEAD/branch/registration、阻害理由、removeではbranch_deleted=false |
| bootstrap | command label、exit code、started、timed_out、sanitized diagnostic |
| workbench | source/destination作業場ID、scope、conflict policy、mutation_started。payload本文は含めません。 |
| workspace sync/validate/doctor | snapshot/generation/validity、findings配列、source/stale、pending journalと復旧先 |
| migrate/installation | inventory、schema/protocol/engine digest、phase、計画対象、適用結果、backup/journal識別 |
| help/completion/version | `help`構造または`script`文字列、shell、version/digest。補完fileを直接書きません。 |

errorは `{code,message,details}`、warningsは同じcode付き配列、recoveryは `{operation_id,can_resume,can_rollback,commands,blocked_reason}` とします。回復commandはshell文字列だけでなくargv配列を保持して安全に引用します。変化し得る日本語messageをscriptの分岐に使いません。 D-16対象外のpartial/unknownでは`can_resume=false`、`can_rollback=false`とし、実在しない復旧commandを出しません。対象固有のread-only確認先と、盲目的な再実行を拒否する理由を`details`/`recovery.blocked_reason`に示します。

| exit | 用途 |
|---:|---|
| 0 | succeeded / unchanged / 正常なplanned |
| 1 | 変更未実施を確認できた未分類internal error |
| 2 | syntax、selector形式、flag衝突、旧コマンド/旧引数の拒否 |
| 3 | readiness、confirmation、state conflict、writer mismatch、busy、child guard等 |
| 4 | 対象なし。現在未選択を含みます。 |
| 5 | 外部/環境失敗で、変更未実施を確認できる場合 |
| 6 | 一部effect成功または副作用の成否不明。internal errorでもこちらを優先します。 |
| 7 | validate/doctorの不整合、またはallow-invalid syncの診断結果 |

JSON指定時は最初のusage errorを含めstdout一文書です。stderrにprogressを出す場合も機密をredactします。壊れたfilesystemから部分成功を再観測できないときは `unknown` です。`--dry-run`でguardに失敗した場合も非0で、実行可能な計画であるように表示しません。

### D-15 effect別のfailure contract

| 操作 / 失敗地点 | 保持する情報・状態 | 回復 |
|---|---|---|
| create: remote作成前 | local予約のみなら予約を使用済みとして残せます。利用者Scope未作成。 | 修正後再実行。欠番は許容します。 |
| create: remote成功・local失敗 | 作成済みremote ref、固定親/title、local書込phase。remoteを自動closeしません。 | 同refのimport。成否不明ならremote照会を先に行い、blind retryで二件作りません。 |
| start: new branch成功・checkout未成功 | branch名/base SHA/registry予約を記録し、activeは変更しません。 | 固定targetとoperationのresume。branchを消してやり直すことを既定にしません。 |
| start: checkout成功・active失敗 | before/after branch、active revision、projection結果。checkoutは自動で戻しません。 | 同targetでresume、active CAS後に再生成。 |
| finish: GitHub close成否不明 | remote ref、request開始、reason、観測失敗をunknownで残します。activeは解除しません。 | live再照会して一致確認後に解除、未知のまま再closeを繰り返しません。 |
| finish: close成功・active解除失敗 | remote completed、対象固定、selection before。 | 固定IDでresume。現在選択が別に進んでいればCAS失敗として停止します。 |
| local close: metadata保存成功・projection失敗 | authoritative local stateは維持、derived dirty。 | sync cacheで再生成。状態保存を二回適用しません。 |
| Artifact create/import: 公開後に結果不明 | 対象ScopeのArtifact catalogと新規fileのidentityを再観測します。 | 既存成果の確認前に別slotへblind create/importを繰り返しません。対象外のwriteをglobalに止めません。 |
| branch switch / worktree create/remove: Git効果後に結果不明 | HEAD・ref・worktree登録・対象pathをread-onlyで再観測し、同対象の不整合を報告します。 | ref/dirを無条件に再作成・再削除せず、競合した対象だけ停止します。 |
| delete: detach/active/削除の途中 | 許可された操作計画、退避した対象tree、before metadata、applied effects。 | D-16のresumeまたは安全条件付きrollback。GitHub操作は一切ありません。 |
| sync: generation公開前失敗 | 以前のgeneration pointerを維持します。 | same sourceで再実行。失敗したstageを無条件deleteせず所有確認します。 |
| sync: pointer公開後旧projection失敗 | 新generationを一次の派生読取り先として維持、旧固定名のstaleを表示。 | syncでprojectionを修復。active authorityは変更しません。 |
| copy / bootstrapの途中 | mutation_startedと実施済み範囲/exitを返します。任意consumer変更はunknownを許します。 | 内容を検査後、明示再実行。汎用rollbackなし。 |
| update / migrateの途中 | 固定engine、backup、phase、各pathのbefore/after identity、inventory epoch。 | 旧writerを再開せず、resumeまたはwhole-cutover rollback。 |

Deleteは実削除前に対象treeを同filesystem内の操作専用quarantineへrenameし、依存/activeのbefore imageとともに保存します。操作完了後もbackupの自動purgeは行いません。利用者からは対象Scopeが消えますが、回復用copyはretention対象です。metadataを壊してからバックアップを取る順にはしません。disk不足や安全な退避ができない場合は削除を開始しません。

### D-16 Journalと具体的な復旧interface

blocking journalは業務イベントソーシングではなく、D-16で明示resumeを持つ操作のクラッシュ時に限る操作記録です。対象は `scope create/import/close/reopen/delete`、`work start/finish`、`branch create`、`workspace migrate`、`installation init/update/uninstall` です。これ以外の変更leafはblocking journalとglobal `recovery-required`を生成しません。blocking journalには最低限 `operation_id / command / fixed_targets / request_fingerprint / before_revisions / phase / effects / backup_refs / engine_digest / writer_epoch / terminal_status` を保存します。network送信前にrequest開始を記録し、成功応答後に確定を書きます。request timeoutを失敗確定とみなしません。

blocking journalを解消する標準の再試行は、D-16の`--resume`を使う固定ID・固定対象の同じ操作です。元operation、request fingerprint、revision、実施済み効果を照合し、remote効果がunknownならlive再照会で確認するまで重ねて送信しません。曖昧なpending operationを通常の同一コマンド再実行や別leafで自動再開せず、解消できない間は`recovery-required`を維持します。以下の補助optionを既存leafにだけ追加します。新しいnamespaceやコマンド名は増やしません。

```text
--resume OPERATION_ID
  scope create/import/close/reopen/delete、work start/finish、branch create、
  workspace migrate、installation init/update/uninstallで対応します。
  元operationと同じcommand・target・意味のあるoptionを照合します。

--rollback OPERATION_ID
  scope delete、workspace migrate、installation init/update/uninstallだけで対応します。
  --resumeとは排他です。通常targetやpin指定は元計画と一致する必要があります。
```

D-16の一覧にない変更leaf、すなわち`scope edit`、`active set/clear`、`branch switch`、`dependency add/remove`、`artifact create/import`、`worktree create/remove/bootstrap`、`workbench copy`、`workspace sync`では`--resume/--rollback`を受理しません。中断後は対象と実施済み効果を再観測し、同一entryやtargetの衝突が未解消ならその操作だけを拒否します。Artifact作成/importやworktree作成の成否が不明な場合は、既存成果を確認する前に新規作成を繰り返しません。copy/bootstrapの任意効果は自動再実行せず、実施済み範囲の確認後だけ明示再実行します。syncは公開済みgeneration pointerを読んでから同じsourceで再実行します。いずれも無関係な通常writeはglobalに止めません。

rollbackはremote close/reopen/createの逆操作を自動実行しません。Git refの復元も勝手に行わず、before/afterが記録値と一致し、利用者の後続変更がない場合だけローカルbackupを復元します。未確認changeがあれば `ROLLBACK_CONFLICT` で停止し、forward recoveryに切り替えます。operationが既に終了していればresumeは元の結果を返すno-opです。

例は固定IDを変数から受け取ります。値をこの原稿で捏造しません。

```bash
spec-dock work finish "$SCOPE_ID" --resume "$OPERATION_ID" --yes --json
spec-dock scope delete "$SCOPE_ID" --resume "$OPERATION_ID" --yes --json
spec-dock installation update --target "$PROJECT" --commit "$BUNDLE_COMMIT" \
  --rollback "$OPERATION_ID" --yes --json
spec-dock workspace migrate --to-schema 3 --resume "$OPERATION_ID" --yes --json
```

### D-17 セキュリティ・プライバシー

root containmentとentry identityを、実行前だけでなく公開/削除直前にも検証します。system assets・control・journal・managed JSONへのsymlink redirect、複数hardlink、別inodeへの差替えを拒否します。tempfileとrenameは所有したdirectory descriptor内で行い、cleanupで他processの新fileをunlinkしません。OSが必要な原語を提供しない場合、unsafe fallbackを作りません。

Artifact/Workbench payloadはuntrusted bytesです。file名や本文をcommandとして実行せず、terminal escape/control charactersをsanitized displayへ変換します。Makefileは明示bootstrap時だけのtrust境界です。固定distributionも信頼されたoperator供給物であり、digest一致が任意供給元を安全にするわけではありません。

journal/backupはoperator-only permissionとし、token・credential環境変数・認証付きURL・raw subprocess環境を保存しません。整合性検証に内部hashを使用しても、Artifact sourceのhash/byte countを公開結果へ出しません。backupの内容をZIPやGitHubへ自動送信しません。ログのdebug modeでこれらの契約を解除しません。

## 変更対象

### D-18 既存file群と新設file群

| 境界 | 既存の変更対象 | 新設するfile群（将来path） |
|---|---|---|
| package入口/installer | `src/spec_dock/cli.py`、`installer.py`、`pyproject.toml` | `src/spec_dock/runtime_loader.py`、`installation/{__init__,contracts,plan,executor,journal,source}.py` |
| runtime入口 | `src/spec_dock/assets/spec_dock/scripts/spec-dock`、RT `app.py` | RT `cli/admission.py`、`cli/legacy.py`、`cli/options.py`、`cli/catalog.py` |
| commands | RT `cli/{parser,registry,dispatch,bootstrap}.py`、`commands/*.py` | RT `commands/{scope,work,branch,dependency,workspace,installation}.py`。active/artifact/worktree/workbenchは既存fileを整理します。 |
| domain | RT `domain/{models,ids,tree,active,status,deps,validation,artifacts}.py` | RT `domain/{selectors,lifecycle,branch_binding,operation}.py` |
| application | RT `application/{contracts,ports,create_node,import_node,close_node,delete_node,set_active,issue_lifecycle,mutate_deps,check_deps,sync_state,worktree,workbench,doctor,validate_tree}.py` | RT `application/{resolve_target,scope_query,edit_scope,work_lifecycle,branch,operation_executor,migrate_workspace}.py` |
| infra | RT `infra/{contracts,fs_repo,active_store,git_cli,github_cli,derived_state_reader,artifact_writer,json_store,fs_cli}.py` | RT `infra/{control_store,operation_journal,writer_lock,branch_registry,generation_store,migration_store}.py` |
| presentation | RT `presentation/{contracts,cli_text,json_state}.py` | RT `presentation/{envelope,errors,help,completion}.py` |
| tests | `tests/unit/`、`tests/cli_runtime/`、`tests/integration/`、`tests/fixtures/` | Planに列挙するcontract・cutover・failure injection suite |
| 配布文書/skills | `src/spec_dock/assets/spec_dock/docs/`、`templates/`、`assets/install_root/.agents/skills/` | 新コマンド参照と移行手順。既存のauthoringの責務は変えません。 |
| dogfood/consumer | 各導入先の `spec-dock/{docs,templates,system,scripts}` と二つのskills | 生成sourceから固定bundleで更新します。手で異なるruntimeを継ぎ足しません。 |

追加file名は実装境界を確定するための提案済みpathです。既存実装として引用しません。`app.py`をもう一つの巨大互換monolithにせず、new parserからtyped use caseを通す構造に整理します。不要な旧use case削除は移行fixtureを確保した後に行い、安全なpublisherやpath guardを消しません。

## 移行・互換性・rollback

### D-19 旧28leafの一括切替契約

互換性の目標は旧入力を永久に実行し続けることではなく、**データを守り、意味の変わる旧入力を無変更で拒否すること**です。旧rootのtombstoneは副作用ゼロの `LEGACY_COMMAND_REMOVED` code 2です。新版に存在する同名leafは、新しい必須引数・安全規則を満たす場合だけ実行します。旧出力をparseするautomationも切替inventoryへ含めます。

| 旧leaf | 新しい入口 | 切替時の扱い | 移行上の差分 |
|---|---|---|---|
| `new initiative` | `scope create initiative --backend github` | 削除済み入口として拒否 | backendを明示します。--github-issueによるリンクはimportへ手動変換します。 |
| `new epic` | `scope create epic --backend github --parent TARGET` | 削除済み入口として拒否 | 旧--initiativeを--parentに置き換えます。 |
| `new issue` | `scope create issue --backend github --parent TARGET` | 削除済み入口として拒否 | 旧--epicを--parentに置き換えます。 |
| `new artifact` | `artifact create --type TYPE --scope TARGET` | 削除済み入口として拒否 | 種別位置引数と三種類のscope flagを明示optionへ移します。 |
| `artifact import file` | `artifact import file PATH --scope ARTIFACT_SCOPE` | 名前維持・旧引数は拒否 | --file/--root/--initiative/--epic/--issueをそのまま受理しません。 |
| `active set` | `active set TARGET` | 選択のみの効果を維持 | 完全ID指定は継続します。旧数値/URL抽出と--id/--github-issueは拒否します。 |
| `active show` | `active show` | 読取り効果を維持 | 出力は共通envelopeへ移し、旧出力をparseするscriptは切替時に更新します。 |
| `active clear` | `active clear --all` | 名前維持・引数なしは拒否 | --from TARGETで対象以下、--allで全解除を明示します。 |
| `delete` | `scope delete TARGET` | 削除済み入口として拒否 | GitHub closeを行わない新操作へ黙ってaliasしません。 |
| `close` | `scope close TARGET` | 削除済み入口として拒否 | reason省略はcompleted、取り止めは--reason not-plannedを明示します。親完了ガードを確認して移します。 |
| `update` | `installation update --commit SHA` | 削除済み入口として拒否 | 未固定upstream取得は廃止します。新distribution外部入口を使います。 |
| `uninstall` | `installation uninstall --dry-run` | 削除済み入口として拒否 | 旧既定dry-runを新適用操作へ黙ってaliasしません。 |
| `issue start` | `work start TARGET` | 削除済み入口として拒否 | 三階層共通化、新branchには--base、forceは--switch-activeです。 |
| `issue finish` | `work finish @issue` | 削除済み入口として拒否 | 全解除から祖先保持へ変わるためaliasしません。 |
| `worktree create` | `worktree create [NAME] --base REF` | 名前維持・旧base省略は拒否 | make initはworktree bootstrapへ明示分離します。 |
| `worktree list` | `worktree list` | 読取り効果を維持 | 新stable selectorと共通JSONを使用します。 |
| `worktree show` | `worktree show WORKTREE_REF` | 名前維持・曖昧な旧selectorは拒否 | wt:IDまたは絶対pathで対象を固定します。 |
| `worktree remove` | `worktree remove WORKTREE_REF` | 名前維持・新安全条件を要求 | --forceは拒否し、--unlock/--discard-ignored/確認を明示します。branchは残します。 |
| `workbench copy` | `workbench copy --scope TARGET --to-worktree WORKTREE_REF` | 名前維持・旧--toは拒否 | 上書きは--on-conflict overwriteを明示します。 |
| `sync` | `workspace sync --source github` | 削除済み入口として拒否 | 旧active推定は別のactive set --from-branchです。新既定sourceはcacheです。 |
| `deps check` | `dependency check TARGET --source github` | 削除済み入口として拒否 | 新既定cacheとliveの違いを明示します。 |
| `deps add` | `dependency add --from TARGET --to TARGET` | 削除済み入口として拒否 | 変更後の暗黙GitHub post-syncを除きます。 |
| `deps remove` | `dependency remove --from TARGET --to TARGET` | 削除済み入口として拒否 | 不存在は従来同様エラー、--missing-okだけが明示例外です。 |
| `import initiative` | `scope import github initiative GITHUB_REF --title TITLE` | 削除済み入口として拒否 | 完全修飾ref、明示title、foreign拒否を使います。 |
| `import epic` | `scope import github epic GITHUB_REF --parent TARGET --title TITLE` | 削除済み入口として拒否 | 旧active由来の親省略を廃止します。 |
| `import issue` | `scope import github issue GITHUB_REF --parent TARGET --title TITLE` | 削除済み入口として拒否 | 旧active由来の親省略を廃止します。 |
| `validate` | `workspace validate [--require-nodes]` | 削除済み入口として拒否 | 空workspaceは既定で有効、非空要求だけをoption化します。 |
| `doctor` | `workspace doctor` | 削除済み入口として拒否 | 診断はread-only、共通JSONとjournal診断を追加します。 |


package側の旧 `init/update/uninstall` も別にtombstone化します。既存script入口のpathは残せますが、入口の存在を旧挙動の保証と混同しません。helpにも「新文法。旧互換実行ではない」と表示します。旧コマンドを呼ぶerror recovery text、context-pack、README、skills、shell completion、Makefile/task設定をすべて更新します。

### D-20 schema移行と保全規則

migrationは停止中の全登録worktreeを対象とし、個々のcheckoutのmetadataを変換します。過去のGit commitをrewriteしません。必要なら各稼働branchへ通常commitでschema変更を含めます。これは一回の切替内の複数ローカル更新であり、複数製品releaseではありません。

| 入力データ | 変換 / 保全 |
|---|---|
| 正しいGitHub linkを持つ旧Scope | backend=githubを追加し、同repositoryを検証します。旧cache doneだけからreasonを確定しません。 |
| linkのない旧local Scope | backend=local、state=openを付けます。過去に完了したと推測しません。ID/親/path/titleを維持します。 |
| linkのない非local ID、部分link、foreign link | 意図を推測せず移行を停止します。mapping-fileで明示的に分類/補完できる場合だけ承認済み変換を適用します。foreignを同repoへ黙って付け替えません。 |
| valid active | 既存チェーンを保存し、最下位からfocusを導出します。空は空です。 |
| stale/broken active | 原本を保全し診断します。mapping-fileで該当worktreeのclearを明示承認した場合だけ解除します。 |
| candidate canonical branch | 実inventoryから唯一のcandidateを提案します。dry-runを経て明示mappingに含むものだけ登録します。複数candidateは自動決定しません。 |
| local ID allocator | 全登録worktreeとローカルにある履歴のIDを予約し、counterをそれ以上にします。unknown衝突は停止します。 |
| 仕様三文書・Report・Artifact・Workbench | 内容を変更しません。既存evidenceのname/type/authorityも自動正規化しません。 |
| .meta.jsonのunknown field | byte-level backupを保持し、意味を変更しないround-tripを行います。許可した追加fieldだけをchange manifestへ記録します。 |
| .gitignore | 新導入なら配布既定を配置します。既存custom内容は保持し、必要なignore不足は診断/明示patchにします。legacy exact-match例外の置換も計画に列挙します。 |

`--mapping-file PATH`はUTF-8 JSONです。schemaは `specdock.migration-map/v1`、repository UID、source inventory digest、配列 `scope_backend_overrides / branch_bindings / active_repairs / worktrees` を持ちます。各行は実inventoryに存在するID/pathしか許しません。branch_bindingsはScope ID、branch名、確認済みtip SHA、reasonを指定します。active_repairsはworktree IDとaction=clearのみ、backend補完は元metadata digestを伴います。fileを実行せず、planと異なる入力を拒否します。

migrationは `workspace migrate --to-schema 3 --dry-run` でinventoryと未解決対応を出力し、`--mapping-file`で確定後に適用します。既にschema3でも未登録worktreeやbranch対応の明示追加だけを認めます。ID再割当やbranch resetの汎用編集機能にはしません。

### D-21 固定供給元とUpdate journal

供給元は `chemitaro/spec-dock` のdistributionだけです。arbitrary source option、任意shell install command、未固定latestは公開しません。--commitは完全commit ID、--versionはその供給元の一意なtag/versionをimmutable commitへresolveし、その後は同じcommitと内容digestを使用します。tagが途中で動いても再解決しません。tagが一意に解決できなければ拒否します。

実行中engineと更新されるrepo-local assetsを分離します。updateは以下のphaseをjournalに記録します。

```text
resolved → staged → verified → backed_up
  → replacing(each managed root) → verified_installed → committed
  failure → recovery-required → resume または rollback
```

対象は六managed directory、version record、導入control recordと、計画で明示した.gitignoreです。`initiatives/`、既存Artifact、Workbench payload、unmanaged skill等は対象外です。sourceとtargetが重なる場合は拒否します。dogfoodingの `src/spec_dock/assets/` を導入先 `spec-dock/` と取り違えません。

new bundleをstageし、source digest、file type、permission、全write pathを検証し、必要容量とbackup先を確保した後でreplaceします。各rootは同filesystem内renameで置換できるようstageし、全rootの結果が確認できた後にversion/controlのcommit markerをpublishします。複数rootが同時にatomicになると約束しません。途中状態はmaintenanceのままです。

self-updateで削除されるpathにjournalや唯一のbackupを置きません。正常完了後もbackupを自動purgeしません。rollbackはafter digestが一致する所有物だけをbeforeへ戻します。後続の利用者変更があるなら上書きせず停止します。schema migrationを済ませた環境でtoolingだけを旧版へ戻してwriterを再開してはいけません。

`--maintenance`はupdate後もcommon controlをmaintenanceに保つ補助optionです。切替時に全worktreeの導入とschema移行が完了するまで使います。単独の互換更新は、全登録worktreeが互換条件を満たす場合だけreadyへ戻れます。

Uninstallは固定engine/manifestからofflineで実行し、同じjournal/backup境界を使います。仕様データを残すので制御backupも残ります。現在実行している外部engineそのものを削除しません。

### D-22 全worktree・dogfood・consumerのcoordinated cutover

1つのGit common directoryを一つの整合性単位とします。別consumer repositoryは別単位ですが、今回の切替では対象inventory全体を同じcandidate bundleに揃えてから通常運用を再開します。どれかが未確認なら全体完了にしません。

inventoryにはproviderのsource checkout、provider内dogfooding設置、全linked worktree、各consumer repositoryと全linked worktree、外部engine/venv、旧CLIを呼ぶagent/task/alias/CI/skillsを含めます。自動探索だけで全consumerを発見できるとはしないため、operator確認を必要にします。現在activeなしという一つの申告を全consumerのactiveなしへ一般化しません。

新writerを初めて許可する前に、旧processとautomationを停止します。data/version/controlだけでなくignored/untracked payload・index・refと復元可能性をbackupで確認します。新control markerを置けば古いPythonが従うという設計にはしません。

固定candidateをworktree外から各導入先へstageし、同じcommon directoryではinstallation updateが全登録導入先をmaintenanceにして適用します。次にworkspace migrateがそのcommon directoryの全登録worktreeを検証・変換し、各checkoutのschemaとwriter protocolを揃えます。最後にglobal inventoryの全項目がready条件を満たしたことをoperatorが確認し、通常writerを再開します。

履歴branchへcheckoutして旧schema/旧runtimeが現れた場合、新外部engineは通常writeを拒否します。read-only調査はraw snapshotを明示して扱い、mutatorへ暗黙migrationしません。履歴内容を新しい稼働branchで使う場合は、停止した作業場で固定bundle再導入・明示schema migration・新しい通常commitによって移行します。過去commitは変更しません。

### D-23 rollback境界

cutover中に一つでも適用失敗したら、新旧writerを混在再開せず全体を停止します。remote mutationはcutoverで行わないため、backupからtooling・schema・controlを揃えて戻すことができます。ただし、通常運用再開後のGitHub close等はbackupで取り消せません。この境界を越えたら原則forward recoveryです。

rollback前には全writerを止め、after digest/revisionの一致を確認します。利用者が後から変更したfileやGit refは上書きしません。バックアップを別の隔離場所に復元して比較し、必要な個別復旧を明示します。`git reset --hard` / `git clean -fdx` を包括的な復旧手段として案内しません。

## testability

### D-24 観測点とテスト境界

Domainはfilesystemなしで階層・selector・状態遷移・依存を検査できるpure functionsにします。Applicationは偽Ports・固定clock・失敗注入pointを使い、各effectが何回・どの順で呼ばれたかを検証します。Infraはtmp directory・実Git repository・fake gh executableを使い、stdout/exit・permissions・symlink/inode・process停止の境界を検証します。

CLI contract suiteはD-04の44leafとD-19の28旧leafをデータ駆動で列挙し、help/JSON/noninteractive/禁止effectを検証します。JSON schemaとcompletionは同じcatalogを元にsnapshot化します。長いhuman message全体ではなく、code・対象・effect・必須help項目を安定契約にします。

cutover testは複数worktreeと二つ以上の独立consumer fixture、dogfood fixtureを持ちます。旧writer起動試行、部分導入、mixed schema、履歴branch再出現、backup/restore、update各root間でのkill、pending operationのresume/rollbackを検査します。実consumerのremote書込みをテストの代わりに実行しません。

## risk

| リスク | この設計での対処と残る制約 |
|---|---|
| 新markerを知らない旧writer | 旧process/automationの停止と固定外部入口が必須です。所有者の任意コード実行までは封鎖しません。 |
| local状態のbranch間相違 | Git snapshotを表示し、勝手なstatus共有をしません。別branchへの反映はGit統合です。 |
| remote close/reasonの競合 | pre/post観測とunknown/partialで表現します。外部変更をtransaction内に取り込めるとは主張しません。 |
| repo-wide lockの待ち時間 | 単純性と安全を優先します。timeoutとbusy診断を用意し、将来の細粒度化は別判断です。 |
| installerの容量・backup保持 | 実行前容量検査とoperatorのretention管理を必要にします。自動purgeしません。 |
| common registryがcloneで失われる | explicit migration/adoptionで再構築します。候補推定だけでは変更しません。 |
| criticalなbootstrap | 任意project codeです。信頼/承認/ログ分離を行い、offline保証のある単機能操作とは区別します。 |
| fixed bundleの供給元侵害 | pinとdigestは同一性の保証です。供給元の信頼そのものはoperatorが管理します。 |

製品方針の未決事項はありません。実施時に必要なIssue/parent/consumer inventory/backup先/candidate SHAは運用入力であり、本原稿が架空値で埋める対象ではありません。これらが未記録の状態で実データへcutoverしません。
