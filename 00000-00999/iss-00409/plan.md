---
種別: 実装計画書（Issue）
ID: "iss-00409"
タイトル: "SpecDock CLI Scope Active Work Redesign"
関連GitHub: ["#409"]
状態: "draft"
原稿状態: "Issue #409 正本へ採用・実装前"
最終更新: "2026-09-24"
依存: ["requirement.md", "design.md"]
親: ["epic-00356", "init-local-00003"]
基準Repository: "chemitaro/spec-dock"
実装調査基準Branch: "codex/scope-start-finish-analysis"
実装調査基準Commit: "eeb3e5965f0cb42de9a24081bfaea15e27fd4451"
---

# SpecDock CLI 案Bの全面採用と安全な一括切替 — 実装計画

本書は[Requirement](requirement.md)と[Design](design.md)の実装・検証・一括切替の順序を示す完成原稿です。実装コードや試験結果ではありません。実装stepは未実行です。Issue #409 と親 Epic #356 を確定し、この三文書を正本に採用しました。

想定実装担当は利用者指定の **GPT-6 Sol / High** です。各stepは一つずつ完了・検証してから次へ進められる粒度にします。ただし、authoring規約に従い、この計画の完成条件やruntimeを特定providerの機能・subagent構成に依存させません。

## Planning Level

**selected level: critical** とします。理由は変更量ではなく、GitHubの不可逆に近い状態変更、ローカル削除、任意consumer hook、供給元からの更新、全worktree/consumerへ跨るデータ移行を含み、誤対象・部分成功・旧writer混在時の回復が難しいためです。

risk factorは、失われる可能性のある仕様/証跡/ignored payload、remoteとlocalの非atomic性、権限/path差替え、実行中runtimeの置換、data schemaとwriter protocolの不一致です。critical Completion Guideのbackup/restore、kill switch、incident response、negative testを省略しません。levelはこの本文だけの文書上の選択であり、metadata、active manifest、runtime admissionへ複製しません。

再評価条件は、新しいexternal providerの追加、破壊的対象の拡大、local/GitHub authorityの変更、未登録consumerの発見、復元不能なbackup、旧writerを停止できない状況です。この場合は該当stepを停止し、Requirement/Designの変更要否を明示して判断します。Plan内だけで仕様を変更しません。

Guideのstaged rolloutは「一回のmaintenance内の検証・適用順」として実現します。公開版の複数releaseや長期移行期間は設けません。

## 目標

完成時の振る舞いはRequirement AC-01〜AC-32、具体契約はDesign D-01〜D-24を正とします。本書では再定義しません。成果は、全44新leaf、旧28leafの安全な切替、保全可能なschema migration/installer recovery、更新済みdocs/skillsと一括切替証跡です。

実装中は、原則として各stepで「失敗するテスト→最小実装→回帰→小さいcommit」を行います。すべてを先にリファクタしてから最後に挙動を合わせる方式は採りません。仮実装でremote mutationを通す、未実装commandをsuccess/no-opと偽る、テストを一括skipすることを禁止します。

## 順序・依存

### 一つの調整された作業としての区分

| 区分 | step | 次へ進む条件 |
|---|---|---|
| 基準・契約固定 | T00〜T05 | source/旧28leaf/新44leaf/型/selector/表示契約が一致します。 |
| 安全な実行基盤 | T06〜T08 | lock/journal/固定engineのnegative testが成功します。 |
| Scopeとlifecycle | T09〜T20 | local/GitHub、selection、依存、branch、start/finish/deleteが契約通りです。 |
| 周辺操作 | T21〜T27 | Artifact/Worktree/Workbench/生成/診断の副作用境界を確認します。 |
| 導入・移行 | T28〜T30 | supply pin、journal、backup/restore、全worktree移行をfixtureで検証します。 |
| 文書・全体統合 | T31〜T32 | full regressionと配布物を確認します。 |
| 一括切替・引渡し | T33〜T35 | 全対象を停止し、同じcandidateへ切り替えてから一括再開します。 |

T番号の順に実施すれば依存は満たされます。T09〜T12のScope基礎、T13〜T16の選択/依存/branch、T21のArtifactは基盤完成後に並行検討できますが、同じfileへの並行編集は避けます。T17/T19は統合点、T32は全面検証の合流点です。

必要な補助Issueは、この一つのcutoverの内部作業を分担するためだけに使います。補助Issueの実在IDは後で採録し、T番号を架空のIssueとして登録済み扱いしません。親Epic/Initiativeの目的をこのPlanで変更しません。

### 作業単位の読み方

各stepに依存・対象file群・作業・完了条件・テスト・ACを記載します。`RT`はDesignで定義した既存runtime source prefixです。**「新設」と書いたtest/fileは将来の作成対象であり、基準commitに既存とは主張しません。** 基準の `tests/cli_runtime/`、`tests/unit/`、`tests/integration/`、`tests/fixtures/` はGitHubで確認した実在groupです。

1step内でも複数の独立変更が生じる場合は、同じ完了条件を保持して小さいcommitへ分けます。共通schemaやコマンド名を便宜的に改変して先へ進めません。

## 実装step

### T00 正本取込先と基準の固定

| 項目 | 内容 |
|---|---|
| 依存 | なし |
| 対象file群 | 既存 authoring guides、実在する選定Issueの三文書。実装sourceは変更しません。 |
| 実施内容 | 実装調査基準のrepository/branch/SHAと、実装開始時のreview済みHEADを区別して記録します。Issue #409／Epic #356／Initiative init-local-00003 の正本三文書とdirect-child HTML Artifactを確認します。実装担当は開始時点のsourceとACを再照合します。 |
| 完了条件 | 三正本が採用済み方針を保持し、実施scopeとbaseが固定されています。モデル指定は作業設定にだけ記録します。 |
| 必要なテスト | frontmatter・相対リンク・採用済み方針・実装調査基準SHAとreview済みHEADの照合。Issue #409 の正本およびArtifactを確認します。 |
| 対応AC | AC-01, AC-31, AC-32 |

### T01 旧28leafとデータの基準fixture化

| 項目 | 内容 |
|---|---|
| 依存 | T00 |
| 対象file群 | 既存 tests/cli_runtime、tests/fixtures、RT cli/parser.py。新設 tests/fixtures/cli_redesign/legacy_manifest.json。 |
| 実施内容 | 旧parserの28leaf、主要help/options/exit、代表的な旧metadata・active・Artifactをfixture化します。remote/Git effectはfake gatewayの観測に固定し、実GitHubを変更しません。 |
| 完了条件 | 旧28leafがexact setで保存され、現在通る安全試験と変更予定の挙動差が区別されています。 |
| 必要なテスト | 既存uv run pytestのbaselineとmake lintを記録します。事前失敗を無視せず、原因と今回差分を切り分けます。 |
| 対応AC | AC-26, AC-27 |

### T02 Domainの新状態型とcodec

| 項目 | 内容 |
|---|---|
| 依存 | T01 |
| 対象file群 | 既存 RT domain/{models,status,tree}.py、infra/contracts.py。新設 domain/lifecycle.py。 |
| 実施内容 | backend union、local lifecycle、StatusObservation、focus/revision、schema3 codecを定義します。既存構造fieldとunknown fieldを保持し、新writerの入力と旧read-only fixtureを区別します。 |
| 完了条件 | local/GitHub二重authorityが型/検証で拒否され、closed unknown reasonをcompletedへ誤写像しません。 |
| 必要なテスト | 新設 tests/unit/domain/test_cli_lifecycle_vnext.py。三kind×各state、reason不明、duplicate、unknown metadata field round-trip。 |
| 対応AC | AC-04, AC-10, AC-12 |

### T03 公開catalogと旧入口拒否

| 項目 | 内容 |
|---|---|
| 依存 | T01 |
| 対象file群 | 既存 RT cli/{parser,registry}.py、commands/contracts.py。新設 cli/{catalog,legacy,options}.py。 |
| 実施内容 | Design C01–C44をmachine-readable catalogにし、共通flagのearly parseを実装します。旧rootのtombstoneと、同名leafの旧引数拒否を副作用前に置きます。active setを正とします。 |
| 完了条件 | 44leaf/28旧leafの集合が固定され、abbreviation/曖昧な入力がuse caseへ到達しません。 |
| 必要なテスト | 新設 tests/cli_runtime/test_cli_vnext_contract.py。全leaf help parse、旧入力、option位置、--、--json usage error。 |
| 対応AC | AC-01, AC-02, AC-27 |

### T04 共通結果・JSON・Text・help

| 項目 | 内容 |
|---|---|
| 依存 | T02,T03 |
| 対象file群 | 既存 RT presentation/{contracts,cli_text,json_state}.py。新設 presentation/{envelope,errors,help,completion}.py。 |
| 実施内容 | status/effects/error/recoveryの外枠とcommand別dataを実装し、renderingからI/Oを除きます。JSON/usage/help/version/completionを統一します。 |
| 完了条件 | stdoutが一文書、TextとJSONのeffect内容が一致し、secret-safeな出力です。 |
| 必要なテスト | test_cli_vnext_contract.pyと新設 tests/unit/presentation/test_cli_envelope_vnext.py。全exit、制御文字、Unicode、empty list、unknown result。 |
| 対応AC | AC-02, AC-22, AC-29 |

### T05 共通selectorとsnapshot解決

| 項目 | 内容 |
|---|---|
| 依存 | T02,T03 |
| 対象file群 | 既存 RT commands/targets.py、application/set_active.py。新設 domain/selectors.py、application/resolve_target.py。 |
| 実施内容 | Scope/current/ArtifactRoot/Worktreeの型付きresolverとproject解決を共通化します。GITHUB_REFの別文法、parent kind、foreign、@current期待値を実装します。 |
| 完了条件 | 同一requestの全roleが一つのsnapshotから固定されます。誤kind・省略・誤repoで変更ゼロです。 |
| 必要なテスト | 新設 tests/unit/domain/test_cli_selectors_vnext.py。multi-role @current/@epic、空active、数字、URL fragment、PR、path traversal、曖昧ID。 |
| 対応AC | AC-03, AC-05, AC-28 |

### T06 共通controlとwriter lock

| 項目 | 内容 |
|---|---|
| 依存 | T02,T05 |
| 対象file群 | 新設 RT infra/{control_store,writer_lock}.py、cli/admission.py。既存 bootstrap/ports。 |
| 実施内容 | common directoryのcontrol、epoch、inventory、admission状態、lock順とworktree leaseを実装します。D-16の明示resume対象だけが未完了blocking journalでglobal recovery-requiredへ移り、その他の操作は対象固有の競合診断に留めます。書込み前にschemaとengineを検証します。 |
| 完了条件 | mixed protocol/未登録作業場/maintenance/D-16対象のpending blocking journal時だけ通常mutatorが開始できず、read-only診断は可能です。復旧対象外の部分失敗は無関係なwriteをglobalに止めません。 |
| 必要なテスト | 新設 tests/integration/test_cli_writer_compatibility_vnext.py。二process、二worktree、lock timeout、kill後解放、再入/lease競合。D-16対象のpendingだけがglobal writeを止め、対象外partialでは同対象の競合を拒否しつつ無関係なwriteが続くことを検証します。 |
| 対応AC | AC-25, AC-28, AC-30 |

### T07 Journalと安全な永続化原語

| 項目 | 内容 |
|---|---|
| 依存 | T06 |
| 対象file群 | 既存 RT infra/{json_store,fs_repo,active_store}.py。新設 infra/operation_journal.py、domain/operation.py、application/operation_executor.py。 |
| 実施内容 | 同filesystem stage・fsync・atomic publish・identity再照合を共通原語にします。D-16の列挙対象だけにblocking journalとeffect前後記録、固定対象/fingerprint/revision照合によるresume、許可されたrollbackを適用します。対象外はatomic/CASまたは操作別partial/unknown診断とし、global recovery-requiredを生成しません。汎用workflow engineにしません。 |
| 完了条件 | D-16の全blocking journal対象がkill後に固定操作のresume経路を持ち、unknownのremote効果を盲目的に再送しません。対象外のkillはglobal未解消journalを残さず、状態再観測前に作成や外部効果を自動重複させません。他人のfileをcleanupしません。 |
| 必要なテスト | 新設 tests/integration/test_cli_recovery_vnext.py。D-16列挙対象を各一件以上killし、全pendingにresumeが存在すること、非対応leafはpending blocking journalを作らないこと、通常同一コマンド再実行がblocking journalを迂回しないことを検証します。disk full、rename失敗、hardlink/symlink、inode差替え、journal欠損/改変も含めます。 |
| 対応AC | AC-13, AC-23, AC-28, AC-29 |

### T08 外部固定engineとrepo shimの統一

| 項目 | 内容 |
|---|---|
| 依存 | T03,T04,T06 |
| 対象file群 | 既存 src/spec_dock/cli.py、pyproject.toml、repo-local script。新設 src/spec_dock/runtime_loader.py。 |
| 実施内容 | 外部packageの固定runtimeを起動し、repo-local shimは信頼済みengineを参照します。package CLIにも新文法を提供し、colocated moduleへの暗黙fallbackを廃止します。 |
| 完了条件 | checkoutがengineの実行コードを差し替えず、旧schema branchを通常writerで変更できません。 |
| 必要なテスト | 新設 tests/integration/test_cli_entrypoint_vnext.py。source/installed/shimの契約一致、engine不一致、PATH偽装、checkout途中import。 |
| 対応AC | AC-01, AC-25, AC-30 |

### T09 local Scopeの作成と採番

| 項目 | 内容 |
|---|---|
| 依存 | T02,T05,T06,T07 |
| 対象file群 | 既存 RT application/create_node.py、infra/fs_repo.py、domain/ids.py、templates。新設 registry allocatorの境界。 |
| 実施内容 | local backendと予約ledgerを追加し、三kindを安全にscaffoldします。親を必須化し、既存local IDsを再利用しません。GH ancestorのstructural cache規則を適用します。 |
| 完了条件 | local graphはnetworkゼロで作成でき、失敗でremote fallbackせず、ID重複と構造不正を拒否します。 |
| 必要なテスト | 新設 tests/cli_runtime/test_scope_local_vnext.py。三kind、二worktree同時採番、予約欠番、親不在/終端/cache不明。 |
| 対応AC | AC-04, AC-26 |

### T10 GitHub state/reason gateway

| 項目 | 内容 |
|---|---|
| 依存 | T02,T07 |
| 対象file群 | 既存 RT infra/github_cli.py、application/ports.py、infra/contracts.py。 |
| 実施内容 | Issue read/create/update/reopenを型付けし、state_reasonとPR判別を取得します。payloadは必要項目だけ、repositoryを必ず固定し、timeout後照会を実装します。 |
| 完了条件 | not_planned/duplicate/nullを区別し、権限失敗・成否不明をcode 5/6で分離します。 |
| 必要なテスト | 新設 tests/unit/infra/test_github_lifecycle_vnext.py。fake gh/API、foreign、PR、401/403/404、timeout後成功/不明、secret redaction。 |
| 対応AC | AC-05, AC-12, AC-28, AC-29 |

### T11 GitHub作成と取込

| 項目 | 内容 |
|---|---|
| 依存 | T09,T10 |
| 対象file群 | 既存 RT application/{create_node,import_node}.py、commands/new.py/import_cmd.py。新設 commands/scope.py。 |
| 実施内容 | createはremote/localを分けてjournal化し、importはtitle/parent/sourceを明示します。重複リンクとforeignを拒否し、post-mutation全件syncを取り除きます。 |
| 完了条件 | 各kindのcreate/importが同じ型契約で動き、remote-only成功をblind retryさせません。 |
| 必要なテスト | 新設 tests/cli_runtime/test_scope_github_vnext.py。remote-only、local-only失敗、duplicate link、title必須、opaque remote body。 |
| 対応AC | AC-04, AC-05, AC-28 |

### T12 Scope list/show/edit

| 項目 | 内容 |
|---|---|
| 依存 | T04,T05,T09 |
| 対象file群 | 新設 RT application/{scope_query,edit_scope}.py、commands/scope.py、既存fs_repo。 |
| 実施内容 | list/filter/showとlocal title編集を実装します。GitHub cacheは出典付きで表示し、readのための書込みをしません。 |
| 完了条件 | title以外の正本/branch/remote bytesが不変で、表示のsnapshotが明示されます。 |
| 必要なテスト | 新設 tests/cli_runtime/test_scope_query_vnext.py。empty/filter/kind、same-title no-op、unknown field/permission保持、@current。 |
| 対応AC | AC-06, AC-22 |

### T13 Active selectionの更新

| 項目 | 内容 |
|---|---|
| 依存 | T04,T05,T07 |
| 対象file群 | 既存 RT application/set_active.py、domain/tree.py、infra/active_store.py、commands/active.py。 |
| 実施内容 | focus/revisionを導入し、set/from-branch入口、clear from/all、CASを実装します。既存snapshot保護を維持し、Git/GH呼出しを排除します。 |
| 完了条件 | 各kindのチェーン、祖先保持、無関係clear no-op、空activeが正確です。from-branch解決は次stepのregistryへportで接続します。 |
| 必要なテスト | 新設 tests/cli_runtime/test_active_vnext.py。current role、CAS、壊れたactive、projection失敗、GH/Git mutation呼出しゼロ。 |
| 対応AC | AC-07, AC-28 |

### T14 Dependencyの宣言操作

| 項目 | 内容 |
|---|---|
| 依存 | T05,T07,T09 |
| 対象file群 | 既存 RT application/mutate_deps.py、domain/deps.py、infra/deps_reader.py。新設 commands/dependency.py。 |
| 実施内容 | 三kindのraw edge、list declared/effective、add/remove、missing-okを共通selectorに移します。暗黙network syncを除きます。 |
| 完了条件 | raw/effectiveを混同せず、自己/循環/祖先子孫の自己待ちを拒否します。 |
| 必要なテスト | 新設 tests/cli_runtime/test_dependency_vnext.py。全kind pair、duplicate/remove missing、境界edge、no network。 |
| 対応AC | AC-14 |

### T15 開始readinessの分離

| 項目 | 内容 |
|---|---|
| 依存 | T10,T14 |
| 対象file群 | 既存 RT application/check_deps.py、domain/deps.py/status.py。 |
| 実施内容 | 対象と祖先の前提集合を純粋policyにします。親の開始に子完了を要求せず、依存先親自身のcompletedと進捗aggregateを分離します。source/cache/unknown規則を実装します。 |
| 完了条件 | dependency checkとwork start用評価が同じpolicyになり、unknownをreadyにしません。 |
| 必要なテスト | test_dependency_vnext.pyとunit。親が開始可能/子がblocked、親自身open/子全完了、not-planned、stale cache。 |
| 対応AC | AC-08, AC-11, AC-14 |

### T16 Canonical branch registryと単機能操作

| 項目 | 内容 |
|---|---|
| 依存 | T06,T07,T13 |
| 対象file群 | 既存 RT infra/git_cli.py、domain/active.py。新設 infra/branch_registry.py、domain/branch_binding.py、application/branch.py、commands/branch.py。 |
| 実施内容 | 一Scope一branchの共有registry、branch show/create/switch、base固定、adoption拒否、他worktree競合を実装します。active from-branchを完全一致で接続します。 |
| 完了条件 | branch作成がtracked metadataをdirtyにせず、同名の他Scope登録と無断adoptionを拒否します。 |
| 必要なテスト | 新設 tests/cli_runtime/test_branch_vnext.py。新規/既存/base、ref移動、他worktree、missing binding、unicode slug、Git hook/外部変更の検出。 |
| 対応AC | AC-07, AC-09, AC-28 |

### T17 三階層work start

| 項目 | 内容 |
|---|---|
| 依存 | T08,T13,T15,T16 |
| 対象file群 | 既存 RT application/issue_lifecycle.pyを分離。新設 application/work_lifecycle.py、commands/work.py。 |
| 実施内容 | resolve/guards/branch/activeをtyped use caseで合成し、同じ階層内移動と別枝switch-activeを分けます。checkout後active失敗をjournalで回復します。 |
| 完了条件 | 三kind×local/githubの開始と禁止effectが一致します。forceやCLI再帰呼出しを使用しません。 |
| 必要なテスト | 新設 tests/cli_runtime/test_work_start_vnext.py。dirty、ancestor移動、sibling guard、stale opt-in、checkout後kill/active fail。 |
| 対応AC | AC-08, AC-09, AC-28 |

### T18 Close/Reopenと子孫完了policy

| 項目 | 内容 |
|---|---|
| 依存 | T10,T12,T15,T07 |
| 対象file群 | 既存 RT application/close_node.py、domain/status.py。新設/拡張domain/lifecycle.py、commands/scope.py。 |
| 実施内容 | local/GHのclose/reopen、終端理由、親のcompleted guard、祖先terminal guardを実装します。reason省略はcompleted、not-plannedは明示指定に限定します。completed親への同一理由closeも子孫guardを先に再評価します。child集計で親自身の完了を代用しません。 |
| 完了条件 | selection/branchは無変更で、理由変更を暗黙適用せず、mixed-backend subtreeを観測できます。 |
| 必要なテスト | 新設 tests/cli_runtime/test_scope_close_vnext.py。reason省略→completedと明示completedの同値性、明示not-plannedのみの取り止め、help/JSONの既定値表示、empty parent、local reopen/GH祖先を確認します。既にcompletedの親に対する同一理由closeは、子孫が全completedならremote書込みなしのno-op、open/not-planned/unknownの各子孫があれば拒否し、active/Gitを変えないことを確認します。 |
| 対応AC | AC-11, AC-12, AC-28 |

### T19 三階層work finish

| 項目 | 内容 |
|---|---|
| 依存 | T13,T18 |
| 対象file群 | 新設 RT application/work_lifecycle.py、commands/work.py。旧issue_finishの全解除経路を置換します。 |
| 実施内容 | 完了policy→backend effect→対象以下の選択解除を合成します。無関係activeと他worktreeを変更せず、再試行targetを固定します。 |
| 完了条件 | 祖先を残す各遷移が正確で、already completedから解除だけを回復できます。 |
| 必要なテスト | 新設 tests/cli_runtime/test_work_finish_vnext.py。全遷移、明示非current、@current後再試行、close成功/active失敗、CAS競合。 |
| 対応AC | AC-10, AC-11, AC-28 |

### T20 ローカルDeleteと回復

| 項目 | 内容 |
|---|---|
| 依存 | T07,T13,T14,T18 |
| 対象file群 | 既存 RT application/delete_node.py、commands/delete.py、infra/fs_repo.py。新scope delete入口。 |
| 実施内容 | remote close barrierと暗黙syncを削除し、明示recursive/clear-active/detach-dependenciesを実装します。quarantine/before imageとresume/rollbackを限定実装します。 |
| 完了条件 | remote gateway呼出しゼロ、branch保持、ID予約保持、対象外bytes保全が成立します。 |
| 必要なテスト | 新設 tests/cli_runtime/test_scope_delete_vnext.py。既存delete安全試験を再利用し、全停止phase、outgoing/incoming edge、permission/identity競合を注入します。 |
| 対応AC | AC-13, AC-26, AC-29 |

### T21 Artifactの共通入口と読取り

| 項目 | 内容 |
|---|---|
| 依存 | T04,T05,T07 |
| 対象file群 | 既存 RT application/{create_artifact_doc,import_file_artifact}.py、domain/artifacts.py、binary_artifact_publisher、commands/artifact_import.py。 |
| 実施内容 | create/import/list/showを共通scope selectorへ移し、publisherの安全境界・保存済みopen-world判定・privacy-safe出力を保持します。 |
| 完了条件 | 六creation種とgeneric/historical evidenceを区別し、rootの利用可能操作を制限できます。 |
| 必要なテスト | 新設 tests/cli_runtime/test_artifact_vnext.py。binary/HTML/unknown label、衝突slot、source保持、外部pathとhash非露出、staged publication failure。公開直後killでは既存Artifactを観測する前のblind retryを行わず、global recovery-requiredを作らないことも確認します。 |
| 対応AC | AC-15, AC-29 |

### T22 Worktree inventoryとcreate

| 項目 | 内容 |
|---|---|
| 依存 | T06,T08,T16 |
| 対象file群 | 既存 RT application/worktree.py、infra/git_cli.py、commands/worktree.py、worktree_target.py。 |
| 実施内容 | stable selectorとregistryを導入し、createにbase必須・運用branch・空activeを実装します。consumer hook terminal requestをcreateから除きます。createの対象別永続attemptと、効果なしを確認して同じIDを再利用する明示 `--recover` を追加します。 |
| 完了条件 | new treeのcommitが固定され、makeは一度も起動せず、source/target安全境界が維持されます。 |
| 必要なテスト | 新設 tests/cli_runtime/test_worktree_create_vnext.py。label省略/衝突、旧base省略拒否、detached base、same-filesystem、entrypoint置換、registry差替え。 |
| 対応AC | AC-16, AC-30 |

### T23 Worktree removeとpayload保護

| 項目 | 内容 |
|---|---|
| 依存 | T07,T22 |
| 対象file群 | 既存 RT application/worktree.py、infra/git_cli.py、commands/worktree.py。 |
| 実施内容 | main/current/bare/dirty/untrackedを保護し、lockedとignoredを別許可に分けます。branch保持とremove後registry retirementを実装します。 |
| 完了条件 | 旧forceでは保護を迂回できず、対象directoryの差替えを検出できます。 |
| 必要なテスト | 新設 tests/cli_runtime/test_worktree_remove_vnext.py。ignored Workbench、locked、active lease、cleanでもsecret payload、途中remove失敗。 |
| 対応AC | AC-17, AC-29 |

### T24 明示Bootstrapと出力境界

| 項目 | 内容 |
|---|---|
| 依存 | T04,T06,T22 |
| 対象file群 | 既存 repo-local scriptのconsumer hook処理を分離、RT commands/worktree.py、application/worktree.py。 |
| 実施内容 | bootstrap leafを追加し、dry-run/ offline時にmakeを起動しない規則を入れます。対象の排他lease、timeout、capture、partialを実装します。対象別のrunning/partial recordは再実行を止め、`--recover --yes` ではhookを呼ばず記録だけを確認済みにします。 |
| 完了条件 | hook失敗はsuccessにならず、JSON stdoutを汚さず、子processからの危険な再入を拒否します。 |
| 必要なテスト | 新設 tests/cli_runtime/test_worktree_bootstrap_vnext.py。make -n評価trap、missing target、stdout flood、timeout/kill、offline、child SpecDock metadata操作。途中停止・任意効果unknownでは自動再実行/rollbackがなく、対象の診断は残しつつ無関係なwriteをglobal停止しないことも確認します。 |
| 対応AC | AC-18, AC-22, AC-29 |

### T25 Workbench copyの衝突契約

| 項目 | 内容 |
|---|---|
| 依存 | T05,T07,T22 |
| 対象file群 | 既存 RT application/workbench.py、infra/fs_cli.py、commands/workbench.py。 |
| 実施内容 | 新--to-worktreeとcurrent/local scopeを受理し、default conflict errorの全件preflightと明示overwriteを実装します。rootなし・内容非解釈を維持します。 |
| 完了条件 | dest-onlyを残し、型衝突/unsafe ancestryを拒否し、途中競合はpartialです。 |
| 必要なテスト | 新設 tests/cli_runtime/test_workbench_vnext.py。local Scope、dest-only、source変更、symlink、conflict before-write、overwrite途中失敗。partial後は実施済み範囲を検査するまでblind overwriteをせず、global recovery-requiredは作らないことを確認します。 |
| 対応AC | AC-19, AC-29 |

### T26 生成世代とSyncの分離

| 項目 | 内容 |
|---|---|
| 依存 | T04,T07,T13,T15,T21 |
| 対象file群 | 既存 RT application/sync_state.py、infra/artifact_writer.py/derived_state_reader.py、presentation/json_state.py。新設 infra/generation_store.py、commands/workspace.py。 |
| 実施内容 | active自動推定と通常mutation後の全件GitHub取得を除きます。cache既定、generation stage/pointer、projection stale、validityを実装します。 |
| 完了条件 | syncの全sourceで一次仕様/active/Git不変、live部分失敗をfreshと偽りません。 |
| 必要なテスト | 新設 tests/cli_runtime/test_workspace_sync_vnext.py。finish後syncで非再選択、zero nodes、live failure、pointer前後kill、allow-invalid、安全性拒否。kill後のgeneration pointer再観測と同source再実行が安全で、global recovery-requiredを作らないことを確認します。 |
| 対応AC | AC-20, AC-22 |

### T27 Validate/Doctorの診断統合

| 項目 | 内容 |
|---|---|
| 依存 | T06,T07,T15,T26 |
| 対象file群 | 既存 RT application/{validate_tree,doctor}.py、commands/{validate,doctor}.py。 |
| 実施内容 | 新schema/registry/generation/未完了journal/installed engine不一致を診断します。空tree許容とrequire-nodes、GH probe all-or-noneを入れます。新規CI checkout向けに固定SHAで構築・digest確認したengineからのみ使う `workspace validate --ci` を追加し、一次データだけを読み取ります。 |
| 完了条件 | 全診断がread-onlyで、repairはせず、code 7と安定finding codeを返します。 |
| 必要なテスト | 新設 tests/cli_runtime/test_workspace_doctor_vnext.py。空、broken control、legacy branch、unknown cache、GitHub引数部分指定、redaction、controlを持たないCI checkoutの有効・無効schemaと無変更。 |
| 対応AC | AC-21, AC-29 |

### T28 固定供給元のdistribution解決

| 項目 | 内容 |
|---|---|
| 依存 | T08,T07 |
| 対象file群 | 既存 src/spec_dock/installer.py、commands/update.py。新設 src/spec_dock/installation/{contracts,source,plan}.py。 |
| 実施内容 | 供給元固定、version→commit固定、bundle digest、tooling path manifestを作ります。ネットワークで取得した任意sourceを実行しません。 |
| 完了条件 | --version/--commit排他とsame content保証が成立し、uninstallは供給元不要です。 |
| 必要なテスト | 新設 tests/unit/infra/test_installation_source_vnext.py。moving tag、wrong repo、archive traversal、source/target overlap、missing packaged hidden assets。 |
| 対応AC | AC-23, AC-24, AC-29 |

### T29 Installer journal・全作業場更新

| 項目 | 内容 |
|---|---|
| 依存 | T06,T07,T28 |
| 対象file群 | 既存 src/spec_dock/installer.py/cli.py。新設 installation/{executor,journal}.py、commands/installation.py。 |
| 実施内容 | init/show/update/uninstallを新envelopeへ統一します。六managed rootsとversion/ignore差分、backup/stage/apply/verify、maintenance保持、resume/rollbackを実装します。 |
| 完了条件 | self-update中にengine/journalを失わず、consumerデータをtouchしません。全登録作業場の部分適用を隠しません。 |
| 必要なテスト | 新設 tests/integration/test_installation_journal_vnext.py。各root間kill、disk不足、後続変更rollback拒否、custom ignore保持、uninstall offline/data保全。 |
| 対応AC | AC-23, AC-24, AC-26 |

### T30 全worktreeのschema migration

| 項目 | 内容 |
|---|---|
| 依存 | T02,T06,T07,T16,T27,T29 |
| 対象file群 | 新設 RT application/migrate_workspace.py、infra/migration_store.py。既存schema readersとtemplates。 |
| 実施内容 | inventory/dry-run/mapping-file/apply/recoveryを実装し、旧shapeの明示変換・既存branch adoption・active保持/明示repairを行います。履歴commitは書換えません。 |
| 完了条件 | 全作業場を同epochへ揃える前にreadyへ戻らず、unknown shape/foreign/曖昧mappingは停止します。 |
| 必要なテスト | 新設 tests/integration/test_workspace_migration_vnext.py。local/GH混在、旧local、duplicate ID、未知field、各phase kill、二worktree、歴史branch、backup restore。 |
| 対応AC | AC-25, AC-26, AC-28, AC-30 |

### T31 配布docs・skills・回復案内の切替

| 項目 | 内容 |
|---|---|
| 依存 | T17,T19,T20,T21,T23,T24,T25,T26,T27,T30 |
| 対象file群 | 既存 assets/spec_dock/docs、templates、install_root/.agents/skills、README、全error recovery文言。 |
| 実施内容 | Designのcatalogから新CLI参照を更新し、旧例をhistorical/移行欄だけに限定します。command名・effects・正本責務をskillsに反映し、HTMLを配布文書から参照可能にします。 |
| 完了条件 | active selectを導入せず、旧delete/finish/syncへの実行案内がCurrent資料に残りません。 |
| 必要なテスト | 新設 tests/integration/test_cli_docs_vnext.py。catalog/help/docs対応、historical例のラベル、skills呼出し、リンク、HTML offline。 |
| 対応AC | AC-02, AC-27, AC-31 |

### T32 全契約・回復・packagingの統合検証

| 項目 | 内容 |
|---|---|
| 依存 | T31 |
| 対象file群 | tests全体、package-data、静的解析、配布candidate。 |
| 実施内容 | 旧試験の変化を28leaf対照で説明し、不要だからではなく仕様変更だから更新します。44leaf/AC matrix、禁止effect、full regression、wheel assetsを検証します。 |
| 完了条件 | 下記最終検証が成功し、既存失敗/skip/未検証を差分付きで可視化します。実consumerへの書込みはまだ行いません。 |
| 必要なテスト | make lint、uv run pytest、git diff --check、package buildとisolated install、two consumer fixtureのcutover rehearsal。 |
| 対応AC | AC-01, AC-22, AC-27, AC-29, AC-32 |

### T33 固定candidateと全対象inventoryの凍結

| 項目 | 内容 |
|---|---|
| 依存 | T32 |
| 対象file群 | 実在candidate distribution、operatorが確認したprovider/dogfood/consumer/worktree inventory、バックアップ領域。 |
| 実施内容 | candidate commit/digestと外部engineを固定します。全旧writerの起動源、data path、Git common directory、backup先、rollback担当を採録し、同一maintenance作業の実施を承認します。 |
| 完了条件 | 未確認consumerがなく、before状態と復元試験が揃い、各対象を一意指定できます。 |
| 必要なテスト | read-only inventory照合、backupを隔離領域に復元して比較、旧writer停止dry-run、候補engineのdigest一致。 |
| 対応AC | AC-25, AC-26, AC-30 |

### T34 一回のcoordinated cutover

| 項目 | 内容 |
|---|---|
| 依存 | T33 |
| 対象file群 | 承認済みinventoryの全導入先。source本体の設計変更はこのstepでは行いません。 |
| 実施内容 | 下記cutover手順で停止→backup確定→全bundle更新maintenance→全schema移行→全対象検証→再開を行います。失敗した単位だけ旧writerを再開しません。 |
| 完了条件 | global inventoryの全項目が同じ固定candidateで受入条件を満たし、pending operationがありません。 |
| 必要なテスト | 適用先ごとのinstallation show/doctor/validate/sync cache、全worktree protocol、before/after bytes差分、旧入口無変更拒否。 |
| 対応AC | AC-23, AC-25, AC-26, AC-27, AC-30 |

### T35 再開後確認とhandoff

| 項目 | 内容 |
|---|---|
| 依存 | T34 |
| 対象file群 | 選定IssueのReport、検証証跡、inventory/backup/journal retention情報。 |
| 実施内容 | 新しい通常呼出しだけを再開し、代表的local正常系を隔離fixtureで再確認します。実データはread-only確認を基本とし、実GitHub closeは別途承認なしに実施しません。結果を薄いReportにまとめます。 |
| 完了条件 | AC matrixに結果が入り、未確認事項・残余リスク・回復境界・所有者が明示されます。正本へ結果日誌を追記しません。 |
| 必要なテスト | 最終handoff checklist、外部engine/shim照合、pending journalゼロ、旧automationなし、人間によるHTMLの移行説明確認。 |
| 対応AC | AC-31, AC-32 |


## 検証

### V-01 受入条件と作業の追跡

次表はACの実装/検証責任です。完了時には薄いReportまたは検証artifactに、実際のcommand・exit・成功/失敗/未実行を記録します。この事前Planに架空の結果を埋めません。

| AC | 主なstep | 検証の状態 |
|---|---|---|
| AC-01 | T00, T03, T08, T32 | 実装時に実行・記録します。 |
| AC-02 | T03, T04, T31 | 実装時に実行・記録します。 |
| AC-03 | T05 | 実装時に実行・記録します。 |
| AC-04 | T02, T09, T11 | 実装時に実行・記録します。 |
| AC-05 | T05, T10, T11 | 実装時に実行・記録します。 |
| AC-06 | T12 | 実装時に実行・記録します。 |
| AC-07 | T13, T16 | 実装時に実行・記録します。 |
| AC-08 | T15, T17 | 実装時に実行・記録します。 |
| AC-09 | T16, T17 | 実装時に実行・記録します。 |
| AC-10 | T02, T19 | 実装時に実行・記録します。 |
| AC-11 | T15, T18, T19 | 実装時に実行・記録します。 |
| AC-12 | T02, T10, T18 | 実装時に実行・記録します。 |
| AC-13 | T07, T20 | 実装時に実行・記録します。 |
| AC-14 | T14, T15 | 実装時に実行・記録します。 |
| AC-15 | T21 | 実装時に実行・記録します。 |
| AC-16 | T22 | 実装時に実行・記録します。 |
| AC-17 | T23 | 実装時に実行・記録します。 |
| AC-18 | T24 | 実装時に実行・記録します。 |
| AC-19 | T25 | 実装時に実行・記録します。 |
| AC-20 | T26 | 実装時に実行・記録します。 |
| AC-21 | T27 | 実装時に実行・記録します。 |
| AC-22 | T04, T12, T24, T26, T32 | 実装時に実行・記録します。 |
| AC-23 | T07, T28, T29, T34 | 実装時に実行・記録します。 |
| AC-24 | T28, T29 | 実装時に実行・記録します。 |
| AC-25 | T06, T08, T30, T33, T34 | 実装時に実行・記録します。 |
| AC-26 | T01, T09, T20, T29, T30, T33, T34 | 実装時に実行・記録します。 |
| AC-27 | T01, T03, T31, T32, T34 | 実装時に実行・記録します。 |
| AC-28 | T05, T06, T07, T10, T11, T13, T16, T17, T18, T19, T30 | 実装時に実行・記録します。 |
| AC-29 | T04, T07, T10, T20, T21, T23, T24, T25, T27, T28, T32 | 実装時に実行・記録します。 |
| AC-30 | T06, T08, T22, T30, T33, T34 | 実装時に実行・記録します。 |
| AC-31 | T00, T31, T35 | 実装時に実行・記録します。 |
| AC-32 | T00, T32, T35 | 実装時に実行・記録します。 |

### V-02 必須の組合せ

| 検証軸 | 最低限含める組合せ |
|---|---|
| lifecycle | Initiative/Epic/Issue × local/GitHub × explicit/current × new/existing branch |
| active解除 | leaf/親/最上位/無関係/空/壊れたactive、ancestor保持、別worktreeは不変 |
| state | open/completed/not-planned/unknown、理由null/duplicate、empty親、子Epic自身open |
| branch | base必須/既存base拒否、registry未登録、紛失、同branch別scope、他worktree、dirty、ref差替え |
| dependency | 全kind pair、直接/継承、親自身完了、子のみblocked、循環/自己待ち、cache stale |
| CLI | 全44leaf、全旧28leaf、option前後、--、日本語title、parse error、JSON/noninteractive/confirm |
| filesystem | symlink/hardlink、ancestor redirect、rename前後inode変更、disk full、readonly、partially published |
| rollout | 2つ以上のworktree、2つ以上のconsumer、dogfood、旧engine/新schema、未知schema、履歴branch |
| recovery | D-16対象のnetwork送信前後・各blocking journal phase・active保存前後・各managed root間kill。対象外のatomic/partial（Artifact、worktree、copy/bootstrap、generation pointer）ではglobal blockなし、対象固有のblind retry拒否 |
| privacy | secretを含むstderr/URL、Artifact source外部path/hash/byte count、Workbench payload、terminal control文字 |

例示fixtureのIDはtestが生成する値を使います。実repositoryのIssue番号をhard-codeしてテスト対象にしません。fixture専用IDを本番Issue IDと混同する文書も作りません。

### V-03 最終検証コマンド

以下は**将来の実装完了時に実行するコマンド**です。本原稿作成時には実行していません。provider sourceの作業rootから実行します。現行Makefile/pyproject/scriptで確認した標準入口は `make lint` と `uv run pytest` です。存在しない `make test`、coverage option、独自skipを前提にしません。

```bash
# 基準差分と標準static analysis / full regression
 git diff --check
 make lint
 uv run pytest

# 上のT03以降で新設するcontract / integration suiteを個別に再確認します。
 uv run pytest -q tests/cli_runtime/test_cli_vnext_contract.py
 uv run pytest -q tests/integration/test_cli_writer_compatibility_vnext.py
 uv run pytest -q tests/integration/test_cli_recovery_vnext.py
 uv run pytest -q tests/integration/test_installation_journal_vnext.py
 uv run pytest -q tests/integration/test_workspace_migration_vnext.py
 uv run pytest -q tests/integration/test_cli_docs_vnext.py
```

必要ならstatic analysisを分けて診断します。これはMakefileが呼ぶ既存scriptの内訳です。

```bash
uv run ruff check src/spec_dock tests
uv run ruff format --check src/spec_dock tests
uv run mypy src/spec_dock tests
```

配布検証ではcleanなcandidateからwheelをbuildし、worktree外の一時環境へinstallして `spec-dock --help --json` とnew/legacy契約を再実行します。build方法は現行のsetuptools/pyprojectに従います。使用するbuild toolが環境にない場合は、その依存を導入して記録し、未実施を成功扱いしません。T32でpackage-dataのdotfiles/skills/templatesが含まれることも検査します。

固定candidateから取得した実在する外部entrypointを `SD`、検証対象projectを `PROJECT` とします。変数は手で架空pathに置換せず、inventoryから設定します。

```bash
: "${SD:?固定candidateの外部entrypointを指定してください}"
: "${PROJECT:?確認対象projectの実在pathを指定してください}"
"$SD" --help --json
"$SD" --project "$PROJECT" installation show --json
"$SD" --project "$PROJECT" active show --json
"$SD" --project "$PROJECT" scope list --json
"$SD" --project "$PROJECT" workspace validate --json
"$SD" --project "$PROJECT" workspace doctor --json
```

syncは生成物を書き換えるため、read-only確認と区別し、切替後の許可済み検証として実行します。一次仕様・active・HEADが変わらないことを前後比較します。

```bash
"$SD" --project "$PROJECT" workspace sync --source cache --offline --json
"$SD" --project "$PROJECT" workspace validate --json
"$SD" --project "$PROJECT" workspace doctor --json
```

CLIが `--json` を受けた全ケースで、stdoutをJSON parserへ渡して余分なログがないことを確認します。code 3/4/6/7を期待するnegative testは、exitだけでなくdata/effect/無変更snapshotも検証します。

### V-04 一括切替の実行runbook

これはT33〜T35の実行順です。すべて一つの調整されたmaintenance作業で行い、区分間に旧writerと新writerを混在運用しません。

| Gate | 実行内容 | 継続条件 / 停止条件 |
|---|---|---|
| G0 対象確定 | provider source、dogfood、全consumerと全worktree、旧起動経路、candidate SHA/digest、backup先、担当をinventory化します。 | 未登録/不明consumerや停止できないwriterがあれば実適用しません。 |
| G1 停止 | agent/session/task/CI等のSpecDock writerを止めます。外部Git操作も禁止し、全process終了を確認します。 | 新markerだけを根拠に停止済みとしません。 |
| G2 保全 | current HEAD/refs/index、全仕様/Artifact/Workbench、untracked/ignored、tooling、control/legacy stateをbackupします。復元を隔離領域で検証します。 | hash/permission/symlink metadataを含む復元不一致、容量不足なら停止します。Git bundleだけでuntracked保全済みとはしません。 |
| G3 外部engine固定 | 検証済みcandidateをcheckout外の環境に配置し、absolute entrypointとdigestを記録します。旧PATH/alias/venvの起動を切替します。 | engine/source/targetの重なり、digest不一致で停止します。 |
| G4 導入計画 | 各common directoryの全worktreeをinspectionし、update --dry-runで全writeとpreserve pathを確認します。 | custom tooling差分が未退避、unknown path、未対応filesystemなら停止します。 |
| G5 導入適用 | 各projectで固定commitのupdate --maintenanceを実行します。全作業場をmaintenanceに保ちます。 | 一箇所でも失敗したら全体停止。成功した場所だけ通常運用へ戻しません。 |
| G6 移行計画 | migrate --to-schema 3 --dry-runで変換一覧を確認し、実inventoryからmappingを確定します。 | foreign/曖昧branch/不明schema/stale active未承認は停止します。 |
| G7 移行適用 | 同じmappingで全登録worktreeへmigrationを適用します。必要なschema/tooling差分は通常commitにまとめます。履歴をrewriteしません。 | 各phase失敗はjournalを保持して停止。旧writerを再開しません。 |
| G8 全面確認 | V-03のshow/validate/doctor/sync cache、差分照合、旧command無変更拒否、全作業場のepoch/digest一致を確認します。 | pending operation、未確認consumer、仕様bytesの予定外差分があれば再開不可です。 |
| G9 一括再開 | global inventoryがすべてready条件を満たした後、新しい起動経路だけを再開します。 | remote mutationを再開した時点をrollback境界として記録します。 |

適用例は将来の新CLIです。candidate SHAとPROJECTはinventoryの値を使います。基準source SHAを「新実装のcandidate SHA」として流用しません。

```bash
: "${BUNDLE_COMMIT:?新実装candidateの完全commit IDを指定してください}"
"$SD" installation update --target "$PROJECT" --commit "$BUNDLE_COMMIT" \
  --maintenance --dry-run --json
"$SD" installation update --target "$PROJECT" --commit "$BUNDLE_COMMIT" \
  --maintenance --yes --json

"$SD" --project "$PROJECT" workspace migrate --to-schema 3 --dry-run --json
# MIGRATION_MAPは上のinventoryに対する承認済みmapping-fileです。
: "${MIGRATION_MAP:?承認済みmapping-fileを指定してください}"
"$SD" --project "$PROJECT" workspace migrate --to-schema 3 \
  --mapping-file "$MIGRATION_MAP" --dry-run --json
"$SD" --project "$PROJECT" workspace migrate --to-schema 3 \
  --mapping-file "$MIGRATION_MAP" --yes --json
```

user専用toolなので、candidateを固定した一つの実装成果から全対象へ適用します。update/migrateが複数repositoryに跨って物理atomicに実行されるとは扱いません。停止状態の維持とglobal inventoryによって部分適用を運用に露出させない方針です。

## rollback

### RB-01 Kill switchとincident開始

新writerに異常があればcommon controlを `maintenance/recovery-required` に保ち、実行中agent・taskを停止します。新writerのadmissionはこの状態で停止しますが、古いwriterは理解しないため旧processも別に停止します。停止を確認できない場合はrestoreを始めません。

incidentの記録は、operation ID、固定target、candidate digest、実施済み/不明effect、影響するworktree/consumer、最終成功phaseだけをsanitizedに残します。token、raw source内容、顧客データをReportやチャットへ転記しません。利用者へ「何が確定し、何が不明か」を伝え、再試行を自動ループにしません。

### RB-02 適用段階別の戻し方

| 時点 | 方針 |
|---|---|
| G5以前でwriteなし | 計画を中止し、原因修正後に再計画します。 |
| tooling一部適用、schema未変更 | 同一candidateでresume、またはafter digest一致を確認してinstaller rollbackします。全writerは停止のままです。 |
| schema一部適用、通常運用未再開 | migration journalからresume、またはtooling/schema/control/inventory全体を整合して戻します。toolingだけ旧版へ戻しません。 |
| G9後にlocal利用者変更あり | backupの一括上書きをしません。隔離restoreとの差分を確認し、原則forward recoveryです。 |
| G9後にGitHub mutationあり | ローカルbackupでremoteを巻き戻したことにはなりません。成否照会と固定IDで回復し、reopen等は別の明示判断です。 |
| copy/bootstrapの任意副作用 | 実変更を検査して個別回復します。汎用rollbackがないことを事前に説明します。 |

復旧commandはDesign D-16を使用します。`--rollback`はafter-state不一致を拒否する必要があります。backup保存先の存在や識別子だけでは復元成功とせず、別の隔離directoryへ実際に復元してfile bytes、権限、symlink、Git状態を比較します。

### RB-03 Forward recoveryと再開判定

checkpoint以後の操作を固定targetで再開し、remote実施済みeffectを繰り返しません。解決済みID以外の `@current` による再試行を案内しません。再開条件は全inventoryのwriter/schema一致、pending journalの解消、データ差分の承認、再検証の成功です。

backup/journalのpurgeは本切替の完了条件にしません。保持先・権限・必要容量を引き渡し、利用者が別途retentionを判断します。緊急時にも `git clean -fdx`、包括的 `rm -rf`、remote状態の推測修復を実行しません。

## exit / handoff

完了時にRequirement AC-01〜AC-32へ結果を対応づけます。全44leaf、旧28leaf、安全境界、migration/update recovery、docs/skills、isolated distributionが検証され、全inventoryが固定candidateへ切り替わり、未完了journalがないことが必要です。

引渡しには、source/candidate SHAとdistribution digest、実施した検証commandとexit、consumer/worktree別適用状態、実際のbackup/journal配置、復元試験結果、残余リスク、次の管理者、停止/再開時刻を含めます。実施していないremote live-write試験は未実行と明示し、fake gateway試験をlive実行と表現しません。

運用値以外の採用方針を再度未決に戻しません。実装が方針に反する必要がある場合はPlanで黙って差し替えず、Requirement/Designへ戻ります。今回の四file原稿には実装Reportを追加せず、将来の実在Issueで結果だけを薄く記録します。
