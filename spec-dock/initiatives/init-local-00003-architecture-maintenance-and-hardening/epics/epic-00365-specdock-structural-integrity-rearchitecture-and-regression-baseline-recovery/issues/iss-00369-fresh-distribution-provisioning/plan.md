---
種別: 実装計画書（Issue）
ID: "iss-00369"
タイトル: "Fresh Distribution Provisioning"
関連GitHub: ["#369"]
状態: "planned"
最終更新: "2026-08-21"
依存: ["requirement.md", "design.md"]
親: ["epic-00365", "init-local-00003"]
---

# iss-00369 Fresh Distribution Provisioning — 実装計画

詳細: [Issue Plan Guide](../../../../../../docs/authoring/issue-plan.md)

## Planning Level

**selected level: `strict`**

理由:

- root-level repository contentとmanaged treeを新規作成する。
- journal storage directoryだけがpre-journal bootstrapになる。
- schema-1 fresh recoveryをschema-2 authorityへ移行する。
- action grammar、journal parser、created-parent bindingを拡張する。
- source/target race、hard-link、symlink、root rebind、crash recoveryを扱う。
- public `update` admission semanticsをfresh targetに対して変更する。
- provider full-regression laneはrepository-wide ledgerを持ち、誤ったfocused commandがfalse passまたはexit 3になり得る。

`critical`へ再評価する条件:

- `spec-dock`以外のpathをjournal前に変更する必要が生じる。
- unknown/user-owned contentをrecursive cleanupする設計が必要になる。
- schema-1 markerからdestructive `upgrade` / `prune` authorityを推測する必要が生じる。
- old recognized journalをresumeできないwire migrationが必要になる。
- external pathまたはreplacement entryを削除し得るfailure caseが見つかる。

## 目標

fresh targetの`init`、`init --force`、`update`をeffective intent `fresh`としてIssue 368後のservice/kernel/journalへcut overする。Issue終了時点で、new fresh operationは`scaffold_applier`、recursive scaffold writer、CLI-owned schema-1 phase marker、plan外version writeを使用しない。

recognized `update` / `init-force`、uninstall、purgeは既存ownerのまま維持する。

## 実装前の基線

実装開始時に次をcode/testから記録する。記録はcharacterizationであり、実行済みとみなさない。

- `DistributionOperation` と `DistributionActionName`
- `WorkspaceAssessment`、`ExecutableMutationPlan`、`OperationJournal`、`DistributionProcessResult`
- `_current_assets()`、`_scaffold_assets()`、`_CURRENT_SHORTCUTS`
- `_active_fallback_distribution_assets()`
- `OperationJournalStore` と schema-2 guard
- `_install_fresh_distribution_unlocked()`
- `_install_fresh_compatibility_distribution_unlocked()`
- `_install_spec_dock_bound()` と recursive copy helpers
- `apply_distribution_plan(scaffold_applier=...)`
- `admit_distribution_operation()` のmissing/empty/preserved/recognized matrix
- existing fresh CLI output、second-init guidance、retry command、exit codes
- current fresh Workbench seedとrecognized no-backfill
- provider test-lane policy

## 順序とdependency

1. current behavior characterizationとtest naming
2. intent/admission/result type generalization
3. fresh contractと`ensure-directory`
4. top-level bootstrapとfresh journal authority
5. shared execution coreとfresh service
6. CLI cutoverとlegacy marker conversion
7. legacy writer/callback removal
8. final tests、docs、Issue 370 handoff

各stepは前stepのtestsがreview可能な単位でcommitできるようにする。dual writer、runtime feature flag、long-lived fallbackは作らない。

## Step 1 — Characterization と test harness

### 変更

- `tests/unit/infra/test_managed_distribution.py`
- `tests/unit/infra/test_init_update.py`
- `tests/cli_runtime/test_distribution_cutover.py`
- 必要なら `tests/unit/cli/test_cli_smoke.py`

### 作業

1. 現行fresh contract inventory helperをtest側に作る。
2. physical Current files、scaffold files、mode、root `spec`、active fallback、version、fresh Workbench seed、required directoriesをsnapshotする。
3. current public contractを固定する。
   - init success output/exit
   - init-force on empty
   - second init without force
   - invalid target
   - unrelated root content
   - exact asset adoption
   - wrong-mode/collision block
   - fresh retry command
4. fresh `update`は現行で`workspace-missing`になることをcharacterizationとして明示し、target behavior testはIssue-owned expected failureまたはnew testとして別名にする。
5. source inspection testでproduction `scaffold_applier=` callerがlegacy fresh routeだけであることを固定する。
6. testsに`test_i369_...` prefixを使用し、focused selectionを安定させる。

### Failure cases

- root Current collision
- `spec-dock` file/symlink
- Workbench modified/symlink/hard-link
- source executable bit欠落
- target root rebind

### Exit criteria

- current factsとIssue-owned changeが同じassertionに混在していない。
- no testがfuture implementationをcurrent factとしてpassさせていない。
- heavy-lane testsがordinary focused runでskipされることをtest planに明記している。

## Step 2 — Intent、admission、resultの一般化

### 変更

- `src/spec_dock/managed_distribution.py`
- `src/spec_dock/cli.py`
- `tests/unit/infra/test_managed_distribution.py`
- `tests/unit/cli/test_cli_smoke.py`

### 作業

1. `JournaledDistributionIntent = Literal["fresh", "update", "init-force"]` を追加する。
2. `RecognizedDistributionIntent` aliasを維持する。
3. `WorkspaceAssessment.intent`、`ExecutableMutationPlan.intent`、`OperationJournal.intent`、`DistributionProcessResult.intent`を一般化する。
4. `DistributionAdmission`へeffective `intent`を追加し、`operation`をrequested operationとして維持する。
5. `admit_distribution_operation()` をentrypoint matrixに合わせて変更する。
   - absent/empty/preserved targetの`update` → status fresh / intent fresh
   - schema-2 fresh recoveryはrequested fresh/init-force/updateからintent freshとしてresume
   - recognized recoveryはexact requested intentだけresume
   - uninstallはfresh recoveryを拒否
6. journal parserのintent/authority validationをhelperへ抽出する。
7. existing recognized unit testsを変更せず通せるcompatibility wrapperを維持する。

### Negative tests

- fresh guardをrecognized intentとしてload
- recognized journalをfreshとしてload
- update journalをinit-forceでresume
- cross-root guard
- downgrade
- dual recovery state
- unknown authority

### Exit criteria

- admissionがrequested operationとeffective intentを混同しない。
- recognized routesのexisting resultとjournal authorityに差分がない。
- fresh `update` routeがread-only admissionまで到達する。

## Step 3 — Fresh Contract と `ensure-directory`

### 変更

- `src/spec_dock/managed_distribution.py`
- `src/spec_dock/assets/managed_distribution.json`（Current inventoryは追加しない。schema変更が不要であることを確認するだけ）
- `tests/unit/infra/test_managed_distribution.py`
- `tests/unit/infra/test_init_update.py`

### 作業

1. `DistributionDirectoryRequirement` と `DistributionPlan.required_directories`を追加する。
2. `_fresh_required_directories()`を実装し、current installerとasset parent inventoryからpath集合を導出する。
3. `DistributionActionName`へ`ensure-directory`を追加する。
4. `_classify_required_directory()`を実装する。
5. `_contract_identity()`とplan digestへrequired-directory setを追加する。
6. `_action_precondition_payload()` / `_action_postcondition_payload()`をdirectory actionへ対応させる。
7. `build_workspace_assessment(..., intent="fresh")`を許可し、fresh-only assets、generated assets、required directoriesを結合する。
8. fresh intentが`upgrade` / `prune`を含むplanを発行できないvalidationを追加する。
9. `_scaffold_assets(operation="fresh")`のWorkbench seedをsingle sourceとして維持し、CLI copy logicを新contractへ重複させない。

### Tests

- required dirs absent → ensure-directory
- required dir exact real directory → adopt
- required dir symlink/file/special → block
- nested missing dirs deterministic top-down
- fresh regular/symlink create/adopt
- historical/wrong-mode/unknown → preserve-and-block
- Workbench seed absent/exact/hard-link/modified/symlink
- recognized update/init-force contractにseedが含まれない
- contract identityがdirectory setとgenerated assetを含む
- `managed_distribution.json`をCurrent inventoryとして参照しない

### Exit criteria

- fresh executable planがcallbackなしで全desired pathとrequired directoryを列挙する。
- blocker planからmutation authorityが発行されない。
- directoryを作るplan外callback/direct mkdirがtop-level bootstrap以外に不要になる。

## Step 4 — `ensure-directory` Kernel と durable binding

### 変更

- `src/spec_dock/managed_distribution.py`
- `tests/unit/infra/test_managed_distribution.py`

### 作業

1. existing `created_parent_bindings` wire fieldをcreated-directory bindingとして一般化する。
2. parser/validatorがmissing parentに加え`ensure-directory` action targetをbinding authorityとして受理するようにする。
3. `_apply_directory_action()`を追加する。
4. action実行前にmissing bindingをjournalへwrite-aheadする。
5. descriptor-relative mkdir、parent fsync、held/visible identity検証を行う。
6. exact created inode bindingをjournalへ昇格する。
7. `_assert_created_parent_bindings_closed_set()`をdirectory actionに対応させる。
8. `apply_distribution_plan()`のaction orderをdirectory top-down → file/symlink path orderにする。
9. fresh intentからupgrade/prune handlerへ到達した場合はprotocol errorにする。

### Failure injection

- missing binding publish failure
- mkdir直後のabrupt stop
- exact binding journal rename直前のstop
- parent appearance between assessment and mkdir
- created directory replacement
- symlink parent
- created directoryへunknown child出現
- parent fsync failure
- journal checkpoint failure

### Exit criteria

- same-plan retryがempty/explained created directoryだけをadoptする。
- unknown childまたはreplacement inodeをoperation-ownedへ昇格しない。
- recursive directory cleanupを行わない。

## Step 5 — Top-level bootstrap と fresh journal authority

### 変更

- `src/spec_dock/managed_distribution.py`
- `src/spec_dock/cli.py`
- `tests/unit/infra/test_managed_distribution.py`
- `tests/cli_runtime/test_distribution_cutover.py`

### 作業

1. `_prepare_fresh_workspace_boundary()`を実装する。
2. provider/source preflightとroot-level collision assessmentをbootstrap前に行う。
3. absent `spec-dock`だけをheld root fdから作成する。
4. exact workspace identityをfull fresh assessmentとjournalへ渡す。
5. `OperationJournalStore._initial_journal()`のauthority hard-codeをintent別builderへ置換する。
6. fresh journal:
   - `intent="fresh"`
   - `authority="fresh-distribution-provisioning"`
   - existing schema-2 guard wire
   - existing journal field shape
7. guard/journal publish failure時のexact-empty rollbackを実装する。
8. guard publish後はforward recoveryだけを許可する。

### Failure injection

- source preflight failure: target write 0
- root collision: target write 0
- mkdir failure
- root rebind before/after mkdir
- mkdir success、guard未発行crash
- guard stage write/publish/fsync failure
- guard publish後journal failure
- exact empty rollback中replacement
- created workspace non-empty化
- terminal guard/journal cleanup failure

### Exit criteria

- first managed asset actionより前にschema-2 guard+journalが存在する。
- top-level bootstrap以外のfresh mutationはjournaled kernelを通る。
- crashでempty workspaceが残っても次回entrypointがfresh recoveryへ進む。
- replacement workspaceをrmdirしない。

## Step 6 — Shared execution core と `execute_fresh_distribution()`

### 変更

- `src/spec_dock/managed_distribution.py`
- `src/spec_dock/cli.py`
- `tests/unit/infra/test_managed_distribution.py`
- `tests/cli_runtime/test_distribution_cutover.py`

### 作業

1. `execute_recognized_distribution()`から共通処理をprivate `_execute_distribution_reconciliation()`へ抽出する。
2. recognized wrapperのsignatureとbehaviorを維持する。
3. `execute_fresh_distribution()`を追加し、次を渡す。
   - fresh contract
   - required directories
   - package version asset
   - generated active fallback assets
   - fresh bootstrap workspace identity
   - fresh authority
4. blocker/no-op/guard/journal/resume/apply/postcondition/finalizationを共通化する。
5. full post-assessmentでdirectoryを含む全actionがadopt/preserve onlyであることを要求する。
6. source/provider identityをapply直前にも再検証する。
7. `DistributionProcessResult`をfresh対応にする。
8. recognized generated-state preserved validatorをfreshへ誤用しない。freshはbootstrap後のbound stateからgenerated contractを構築する。

### Failure injection

- destination appearance
- provider source bytes/mode change
- stage reservation/write/publish
- regular/symlink no-replace failure
- postcondition failure
- mark-verified / mark-completed failure
- guard removal / journal removal failure
- same-bytes different-inode replacement
- root/parent visible rebind

### Exit criteria

- freshとrecognizedが同じprivate execution core、journal store、action kernel、result typeを使用する。
- fresh serviceにcallback parameterがない。
- fresh versionとactive fallbackがplan actionsに含まれる。
- failed operationがrelative/sanitized reasonとapplied/pending pathsを返す。

## Step 7 — Schema-1 conversion と CLI cutover

### 変更

- `src/spec_dock/managed_distribution.py`
- `src/spec_dock/cli.py`
- `tests/unit/infra/test_managed_distribution.py`
- `tests/cli_runtime/test_distribution_cutover.py`
- `tests/unit/infra/test_init_update.py`

### 作業

1. schema-1 fresh markerをread-only conversion inputにする。
2. exact marker identity/bytes、root、same package、phase、stage ownershipを検証する。
3. current treeをfresh assessmentで再分類し、legacy phaseからcheckpointを推測しない。
4. exact schema-1 markerをschema-2 guardへatomic swapする。
5. guard anchored planからjournalを発行する。
6. invalid/unconvertible markerを保持して`recovery_required`を返す。
7. `main()`のentrypoint dispatchを`DistributionAdmission.intent`へ切り替える。
8. result adapterでpublic output/exit/retry commandを写像する。
9. fresh `init` retryはexisting canonical `init` guidanceを維持する。
10. new fresh `init --force` / `update`はrequested entrypointをretry guidanceに使う。
11. special target名はexisting `_safe_retry_target_label()` / `_shell_join()`を使用する。

### Legacy conversion tests

- each supported legacy phase with exact current state
- preflight marker + valid stage lease
- later phase + exact desired entries
- marker same bytes/different inode replacement
- invalid stage name/identity/content
- package mismatch
- root mismatch
- modified scaffold collision
- dual marker/journal
- conversion guard publish failure
- conversion後journal publish failure
- legacy marker retained on every refusal

### CLI matrix tests

- absent target: init/init-force/update
- exact empty workspace: init/init-force/update
- preserved-specs workspace: init/init-force/update
- recognized: second init/update/init-force
- fresh journal resume through three entrypoints
- uninstall rejects fresh journal
- success output/exit
- blocked output/exit
- recovery output/exit
- retry command with spaces/leading `-`
- no absolute provider/temp path leakage

### Exit criteria

- all new fresh entrypointsがnew serviceへ到達する。
- schema-1 markerは新規operationで作成されない。
- schema-1 conversion拒否がlegacy writer fallbackへ落ちない。
- recognized CLI behaviorに差分がない。

## Step 8 — Legacy seam removal

### 変更候補

- `src/spec_dock/cli.py`
- `src/spec_dock/managed_distribution.py`
- tests referencing retired private seams

### 削除対象

- `_install_fresh_distribution_unlocked()`
- `_install_fresh_compatibility_distribution_unlocked()`
- fresh `apply_scaffold()` closures
- production `scaffold_applier=`
- production `allow_blocked_scaffold_paths`
- new fresh operation用 `_write_distribution_retry_marker()`
- fresh phase progression
- fresh plan外 `_write_spec_dock_version()`
- fresh direct `_ensure_active_fallback_entrypoints()` call

### 条件付き削除

次はrepository-wide call graphを確認してから削除する。

- `_install_spec_dock_bound()`
- `_install_spec_dock()`
- `_sync_tree()`
- `_copy_managed_scaffold_tree()`
- `_copy_managed_directory_contents()`
- `_copy_managed_regular_file_at()`
- `_write_atomic_regular_file()`
- `_ensure_active_fallback_entrypoints()`
- schema-1 marker parser/helpers

uninstall、runtime、tests、legacy conversionで使用されるhelperは残すか、owner moduleへ移す。

### Tests

- `inspect.getsource()`またはAST/call graphでfresh routeにretired seamsがない。
- `apply_distribution_plan()`のcallback branchが削除されている。
- all fresh scaffold filesがordinary actionsとしてjournalに現れる。
- version actionがjournalに現れる。
- legacy marker parserは存在してもwriter callがproduction new pathにない。

### Exit criteria

- fresh mutation writerが一つだけである。
- dead callback/private publish shortcutがない。
- source inspection testがfunction nameだけでなくcall edgeを検査する。

## Step 9 — Documentation、verification、handoff

### 変更

- Issue 369 `requirement.md`、`design.md`、`plan.md`
- implementation completion時の`report.md`
- public README recovery guidanceが実装と不一致なら必要最小限更新
- Issue 370 handoff notes

### 作業

1. public init/update/retry/second-init guidanceをactual outputに合わせる。
2. schema-1 markerがlegacy inputであることを記録する。
3. fresh journal authorityとbootstrap exceptionを記録する。
4. source/dogfood/package inventory comparisonを作る。
5. residual riskをIssue 370〜372へ分離する。
6. reportにexact candidate SHAとactual command resultsを記録する。planned commandを実行済みとして記載しない。

## Test laneに従う検証command

### 有効なfocused verification

ordinary runで実行可能なunit surface:

```bash
uv run pytest -q tests/unit/infra/test_managed_distribution.py -k 'i369 or fresh'
uv run pytest -q tests/unit/test_provider_test_lanes.py
uv run pytest -q tests/unit/cli/test_cli_smoke.py -k 'i369 or init or update'
```

heavy testsのnode名とselection確認だけを行う場合:

```bash
uv run pytest --collect-only -q tests/unit/infra/test_init_update.py -k 'i369'
uv run pytest --collect-only -q tests/cli_runtime/test_distribution_cutover.py -k 'i369'
```

`--collect-only`はbehavior passではない。

### 無効なfocused acceptance command

次を成功条件にしてはならない。

```bash
uv run pytest --run-full-regression -q tests/unit/infra/test_init_update.py -k 'i369'
uv run pytest --run-full-regression -q tests/cli_runtime/test_distribution_cutover.py -k 'i369'
```

`--run-full-regression`はrepository-wide approved-failure ledgerを常時検証する。focused selectionはexpected nodesを収集しないため、test bodyがpassしてもledger mismatchでexit 3になる。exit 3をpassとして扱わない。

ordinary heavy selection:

```bash
uv run pytest -q tests/unit/infra/test_init_update.py -k 'i369'
uv run pytest -q tests/cli_runtime/test_distribution_cutover.py -k 'i369'
```

はpolicy-skipされるため、これもbehavior pass evidenceにしない。

### final verification

```bash
make lint
uv run pytest -q
uv run python spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00365-specdock-structural-integrity-rearchitecture-and-regression-baseline-recovery/issues/iss-00368-recognized-workspace-reconciliation/artifacts/verify-full-regression.py
./spec-dock/scripts/spec-dock validate
git diff --check
```

`verify-full-regression.py` は内部でrepository-wide `pytest --run-full-regression -q --junitxml=...`を実行し、approved baseline failureのnode IDとnormalized signatureが完全一致する場合だけwrapperとしてexit 0を返す。raw pytest exit 1またはfocused exit 3を手動で成功へ読み替えない。

Issue 369で新規failureをledgerへ追加して許可しない。unexpected failure、missing baseline node、signature mismatch、setup/teardown errorはexit criteria failureである。

## Evidence matrix

| Requirement | Primary tests/evidence |
|---|---|
| I369-R01〜R03 | CLI smoke、`test_init_update.py`、entrypoint matrix golden |
| I369-R04〜R06 | contract inventory、required-directory unit tests、package parity |
| I369-R07〜R11 | managed distribution classifier/kernel failure matrix |
| I369-R12 | bootstrap mkdir/guard/journal fault matrix |
| I369-R13〜R16 | journal parser/store/resume/intent isolation tests |
| I369-R17 | schema-1 conversion matrix |
| I369-R18 | post-assessment、terminal cleanup、byte/mode/link parity |
| I369-R19 | CLI sanitized result/retry tests |
| I369-R20 | AST/call graph and no-callback tests |
| I369-R21 | `test_provider_test_lanes.py` とfinal verifier logs |

## Rollback と recovery

- new schema-2 fresh guard/journal発行前はcode revert可能である。
- exact empty bootstrapだけが残った場合、old current codeの`init`はfresh admission可能である。ただしnew schema-2 fresh journal発行後はold codeへ戻してoperationを続行しない。
- schema-2 fresh recovery stateがあるconsumerはsame/compatible implementationでforward recoveryする。
- schema-1 marker conversion前はold packageでlegacy retry可能である。conversion後はold packageへ戻さない。
- created directory、stage、quarantine、backup、GC entryはexact leaseなしに削除しない。
- package rollbackでcontract identityが変わる場合、resumeしない。
- journal/guard protocolを変更する場合、recognized protocol 1 resumeを同時に検証する。

## Exit criteria

- I369-R01〜R21がcode/test/evidenceへtraceできる。
- fresh targetの三entrypointがeffective intent `fresh`で同じserviceを使用する。
- recognized targetのIssue 368 behaviorが維持される。
- fresh desired assetsとrequired directoriesが全てjournal actionで表現される。
- top-level `spec-dock`以外にpre-journal mutationがない。
- fresh-only Workbench seedとrecognized no-backfillが固定される。
- schema-1 markerがbounded conversion inputになり、新規writerがない。
- `scaffold_applier`とplan外version writeがfresh call graphから消える。
- valid focused、fast-lane、ledger-aware full-regression、lint、validate、diff-checkのactual resultsがreportに記録される。
- testsが未実行、policy-skipped、collect-only、exit 3の場合はpassと記録しない。

## Issue 370へのhandoff

Issue 369は次をIssue 370へ渡す。

- generalized `JournaledDistributionIntent`
- shared `WorkspaceAssessment` / `ExecutableMutationPlan`
- action grammarとdirectory binding
- descriptor-bound apply kernel
- guard/journal/result mapping
- fresh/recognized authority isolation
- created-directory closed-set semantics

Issue 370は`remove` / recursive managed-root deprovisionを追加するownerである。Issue 369はfresh planへ`prune`、recursive delete、uninstall marker、keep/remove-specs policyを取り込まない。

## 未確定事項

- exact required-directory inventoryはStep 1/3のsource-derived testで確定する。
- current fresh `update`は未実装であるため、成功とnew retry mappingはIssue 369のgolden contractとして確定する。
- final test counts、runtime、candidate SHA、ledger comparison結果は実装後のreport/quality-gate evidenceでのみ記録する。
- 本計画に列挙したcommandは実行予定であり、この文書作成時点で実行済みとは扱わない。
