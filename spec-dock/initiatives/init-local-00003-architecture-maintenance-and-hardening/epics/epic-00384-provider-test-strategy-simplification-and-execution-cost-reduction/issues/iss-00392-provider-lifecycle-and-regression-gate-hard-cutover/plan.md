---
種別: 実装計画書（Issue）
ID: "iss-00392"
タイトル: "Provider Lifecycle And Regression Gate Hard Cutover"
契約名: "Fixed Ownership Provider Lifecycle Hard Cutover"
関連GitHub: ["#392"]
状態: "detailed-review-candidate"
詳細化状態: "independent-review-pending"
最終更新: "2026-09-08"
依存:
  - "requirement.md"
  - "design.md"
  - "artifacts/20260908t011846z-luna-max-implementation-handoff.md"
  - "artifacts/20260908t011846z-01-lifecycle-test-ownership-and-migration.md"
親: ["epic-00384", "init-local-00003"]
Planning Level: "critical"
実装開始許可: false
repository_evidence:
  role: "issue-elaboration-source-provenance"
  repository: "chemitaro/spec-dock"
  branch: "iss-00392-provider-lifecycle-and-regression-gate-hard-cutover"
  sha: "dc638e936e763cc7a6087f258201ed9ed654e7fb"
  tree: "17ce38234033393c385c4b17e40c0ccdc78bfc19"
---

# iss-00392 Provider Lifecycle And Regression Gate Hard Cutover — 実装計画

## 1. 結論と実行単位

#392は四つのcausal checkpointを順に実装し、最後に一つのPRとして人間がEpic integration branchへmergeします。Checkpointはレビューしやすい内部状態であり、単独merge、単独Issue closure、main向けPR、#395開始条件にはなりません。

1. CP1: closed model、wire projection、candidate/legacy identity、private state、native filesystem。
2. CP2: installer engine/public CLI hard cutover、recovery、migration/uninstall、旧writer撤去。
3. CP3: frozen runtime bootstrap、lease/helper/handoff、pinned checkout、worktree B/hook。
4. CP4: provider-first packaging、complete dogfood、test migration、current gate、B1受入。

各checkpointは最初にRED testを追加し、そのREDが意図した欠落だけを示すことを確認してからProductを変更します。次checkpointへ進む条件は、当該checkpointのcompletion stateとnarrow verificationが揃い、stop conditionが0件であることです。

## 2. G0 — Product実装前gate

現時点の値は`implementation_allowed=false`です。次の全条件が外部証拠として成立したときだけ、CodexがCP1 packetをLuna Maxへ渡します。

- 本Requirement/Design/Plan/Handoff/Test Artifactを一つの候補として独立reviewし、P0=0、P1=0、`review_status=pass`。
- Review対象bytesのmanifest/hashが固定されている。
- 同内容がIssue branchへcommit/pushされ、remote branch tipのfull SHAが取得済み。
- GitHub #392 body/projectionがそのfreeze identityを参照し、readback確認済み。
- Epic integration branch B0 GREEN、predecessor #387 completion、15 rows/14 active/1 resolved、243 timing entries、four required-fastが再確認済み。
- User/Codexが「次の一checkpoint」であるCP1開始を許可している。

不足時は仕様packを改善するだけで、Product fileを変更しません。

## 3. 共通実行規則

- Repository root `AGENTS.md`を毎checkpoint開始時に再読します。
- Baseはその時点のexact Issue branch tipです。別branch、default branch、mainへ黙って切り替えません。
- Product sourceの正本は`src/spec_dock/`、dogfoodは最後のprojectionです。
- Test削除はsuccessor GREEN後だけです。
- Parent Wire、accepted ADR、register、#395/#396文書を編集しません。
- Unexpected failure、wire drift、baseline driftをapproved/skip/xfailで隠しません。
- 各packetの変更対象外fileに差分が出たら、そのcheckpointを停止します。
- Product code、tests、docs、packagingの変更は#392 branch内に保持し、人間merge前にIssueを完了扱いにしません。

## 4. CP1 — Closed lifecycle foundation

### 4.1 Entry state

- G0成立済み。
- Productは0.2.3、旧`managed_distribution.py`がproduction ownerのまま。
- Parent Wire v12はread-only。
- 旧public routeをまだ変更しない。
- Baseline 15/14/1、required-fast、timing 243が一致。

### 4.2 最初のRED test

最初に次を追加し、Product変更前に実行します。

- `tests/unit/provider_lifecycle/test_wire.py::test_t01_wire_v12_inventory_and_generated_projection_are_exact`
- `tests/unit/provider_lifecycle/test_private_state.py::test_t04_prepared_active_precedes_stage_and_p1_only_rebuilds_registered_entries`
- `tests/unit/provider_lifecycle/test_atomic_filesystem.py::test_t05_linux_and_macos_native_atomic_adapters_have_no_unsafe_fallback`

Expected RED:

- import先`spec_dock.provider_lifecycle`またはgenerated projectionが存在せずfail。
- Existing unrelated test failureをRED理由にしない。
- Parent Wire countsはtest側で6/41/23/24/168/40/4としてparse成功する。

### 4.3 Exact owned files and symbols

**NEW**

- `src/spec_dock/provider_lifecycle/__init__.py`
- `src/spec_dock/provider_lifecycle/contracts.py`
- `src/spec_dock/provider_lifecycle/_wire_generated.py`
- `src/spec_dock/provider_lifecycle/wire.py`
- `src/spec_dock/provider_lifecycle/candidate.py`
- `src/spec_dock/provider_lifecycle/legacy_fixture.py`
- `src/spec_dock/provider_lifecycle/private_state.py`
- `src/spec_dock/provider_lifecycle/filesystem.py`
- `src/spec_dock/provider_lifecycle/coordination.py`
- `scripts/maintenance/generate_provider_lifecycle_wire.py`
- `scripts/maintenance/generate_provider_lifecycle_legacy_fixture.py`
- `src/spec_dock/assets/provider_lifecycle/legacy-0.2.3.json`
- `tests/unit/provider_lifecycle/test_wire.py`
- `tests/unit/provider_lifecycle/test_candidate.py`
- `tests/unit/provider_lifecycle/test_authority.py`
- `tests/unit/provider_lifecycle/test_private_state.py`
- `tests/unit/provider_lifecycle/test_atomic_filesystem.py`

**Exact new symbols**

- `contracts.py`: Design §8のdataclass/literalのみ。
- `wire.py`: `parse_installation_record`、`serialize_installation_record`、`parse_slot_marker`、`serialize_slot_marker`、`build_public_result`、`validate_public_result`。
- `candidate.py`: `capture_packaged_candidate`、`compute_candidate_digest`、`validate_staged_candidate`。
- `legacy_fixture.py`: `load_legacy_fixture`、`classify_exact_legacy_workspace`。
- `private_state.py`: `resolve_private_namespace`、`ActiveStateStore`、`CompletionReceiptStore`、`StageStore`。
- `filesystem.py`: `NativeAtomicFilesystem`、`LinuxRenameAt2Adapter`、`MacOSRenameAtXAdapter`。
- `coordination.py`: `RepositoryLease`、SH/EX/inherited validation functions。

### 4.4 Implementation order

1. Wire generatorをtest-only inputとして作り、Parent Wire v12のinventory/order/golden parseをGREENにします。
2. `_wire_generated.py`を生成し、manual edit guardとsource SHAを固定します。
3. Record/marker parser・serializerを実装します。Public result constructorはrelation table未一致を例外にします。
4. Candidate six-domain captureとcanonical digestを実装します。
5. Legacy fixture generatorをexact commitへ固定し、compact fixtureを生成します。Regeneration equality testを追加します。
6. `InodeWitness`とdescriptor-relative captureを実装します。
7. Linux/macOS Adapterを実装し、native capability unavailableでfail closedにします。
8. Private namespace、ACTIVE/STAGE/receipt parser/writer、mode0644 `RECORD-TEMP` witness、P0/P1/P2 classifierを実装します。
9. Unknown/foreign/temp re-entry、record no-replace/exchange前後のmode/witness/residue、P1 rebuild、P2 no-rewriteのfault testsをGREENにします。
10. このcheckpointでは`src/spec_dock/cli.py`と旧writerのproduction routeを変更しません。

### 4.5 Narrow verification

```bash
uv run pytest -q \
  tests/unit/provider_lifecycle/test_wire.py \
  tests/unit/provider_lifecycle/test_candidate.py \
  tests/unit/provider_lifecycle/test_authority.py \
  tests/unit/provider_lifecycle/test_private_state.py \
  tests/unit/provider_lifecycle/test_atomic_filesystem.py
make lint
```

Expected result:

- Both commands exit 0。
- Wire counts 6/41/23/24/168/40/4。
- Generated wire/legacy fixture diff 0。
- P1だけstage rebuild、P2 stage write count 0。
- `RECORD-TEMP`とpublic recordはno-replace/exchange前後ともmode0644で、exchange residueはoriginal-record witness一致時だけcleanup。
- Linux runnerはrenameat2実operation、macOS runnerはrenameatx_np実operationを後続matrixで実行可能な状態。
- Existing public routeはまだ旧ownerであるため、#392 acceptanceではない。

### 4.6 Completion state

- New foundationはisolated unit testsでGREEN。
- Parent Wire、legacy source commit、private schema、digest、native Adapterに未決判断がない。
- 旧Product routeと旧testsは残存。
- Baseline identityに差分なし。

### 4.7 Stop condition

- Wire parserがfinite inventoryを一意に生成できない。
- Candidate digestがslot markerとの循環を生む。
- Legacy fixtureをverified commitのGit objectsだけから生成できない。
- Private namespaceをsame-filesystemで置けない一般ケースが、既存wireで表せない新public判断を要求する。
- macOS/Linux native no-replace/exchangeがdescriptor-relativeに実装不能。

### 4.8 Next-step handoff

CP1 summaryにchanged files、generated hashes、RED/GREEN commands、remaining old routeを記録し、CP2 packetだけを新規に渡します。CP1成果を単独mergeしません。

## 5. CP2 — Installer lifecycle hard cutover

### 5.1 Entry state

- CP1 completion済み。
- New foundation GREEN、旧public route/旧writerは現存。
- Parent wire/fixture hashes固定。
- No baseline drift。

### 5.2 最初のRED test

- `tests/unit/provider_lifecycle/test_engine.py::test_t06_all_fixed_fault_boundaries_converge_to_wire_continuations`
- `tests/unit/provider_lifecycle/test_engine.py::test_t07_legacy_migration_uninstall_and_old_package_mutation_zero`
- `tests/integration/test_issue_392_acceptance.py::test_t12_public_cli_uses_only_new_lifecycle_and_old_writer_is_absent`

Expected REDはengine/route未実装または旧purge routeが呼ばれることです。旧test failureをassertion削除で解消しません。

### 5.3 Exact owned files and symbols

**NEW**

- `src/spec_dock/provider_lifecycle/engine.py`
- `tests/unit/provider_lifecycle/test_engine.py`
- `tests/integration/test_issue_392_acceptance.py`

**MODIFY**

- `src/spec_dock/cli.py`
- `pyproject.toml`の`[project].version`だけを0.2.4へ更新（package/dogfood acceptanceはCP4）
- Lifecycle-related portions of `tests/unit/infra/test_init_update.py`
- Lifecycle-related portions of `tests/cli_runtime/test_distribution_cutover.py`
- `tests/integration/test_epic_00343_distribution.py`

**DELETE after successors GREEN**

- `src/spec_dock/managed_distribution.py`
- `src/spec_dock/assets/managed_distribution.json`
- obsolete-only nodes in `tests/unit/infra/test_managed_distribution.py`

### 5.4 Implementation order

1. `ProviderLifecycleEngine.execute`にcommon admissionとpending cleanup precedenceを実装します。
2. Prepared ACTIVE→stage→bootstrap/incomplete→runningの順を実装します。
3. Install/update/migrationのfour roots/two slots/seeds/verify/ready/terminal/cleanupを実装します。
4. Uninstall dry-run/applyとtooling-absent recordを実装します。
5. Completion receipt、deferred invocation、token replay、new-operation invalidationを実装します。
6. Fault injectorのfixed IDsでP0/P1/P2、全root/slot、terminal、cleanup、response-lossを網羅します。
7. `src/spec_dock/cli.py`をthin adapterへ切り替えます。Public outputはnew wire constructorだけから生成します。
8. `--remove-specs`をtarget/private observation前のrequest errorへ切り替えます。
9. Existing CLI compatibility/golden testsをnew resultへ置換します。
10. Exact legacy/ready/incomplete/tooling-absent normal and fault integrationをGREENにします。
11. New routeとabsence guardsがGREENになってから旧module、旧manifest、旧journal/retry testsを削除します。
12. `grep`/AST testで旧writer import/call/path string 0を証明します。

### 5.5 Narrow verification

```bash
uv run pytest -q \
  tests/unit/provider_lifecycle/test_engine.py \
  tests/integration/test_issue_392_acceptance.py::test_t12_public_cli_uses_only_new_lifecycle_and_old_writer_is_absent \
  tests/integration/test_epic_00343_distribution.py
uv run pytest -q tests/cli_runtime/test_distribution_cutover.py \
  -k 'retained_skill_identity_matches_current_provider_and_dogfood or provider_lifecycle'
make lint
```

Expected result:

- Commands exit 0、unexpected failure 0。
- 168 relation rowsと40/4 goldensがpublic CLIでbyte一致。
- 全fault retryがexact tuple、P2 stage writes 0。
- Protected sentinel不変。
- Exact 0.2.3だけmigration。
- Tooling uninstall後はrecord残存、roots/slots absent。
- `--remove-specs` exit 2/mutation 0。
- `src/spec_dock/managed_distribution.py`とold manifest absent、production references 0。
- Resolved successor nodeは同nodeidでpass。

### 5.6 Completion state

- External installer public lifecycleはnew engineだけ。
- Old writer/manifestはrepositoryから除去。
- Runtime wrapperはまだCP3前のため、B1 acceptanceではない。
- Source-level lifecycle tests GREEN。

### 5.7 Stop condition

- Existing wire rowでは区別不能なfaultが発生。
- Protected dataを読む/直す必要が発生。
- Old writerをcompatibility fallbackとして残す必要が発生。
- Existing public commandのalias/flagをWire外で変更する必要が発生。
- `test_s40b_retained_skill_identity_matches_current_provider_and_dogfood`を維持できない。

### 5.8 Next-step handoff

CP2 summaryでold writer absenceとpublic wire conformanceを示し、CP3 packetだけを渡します。外部installerが完成していても、runtime coordination前にmergeしません。

## 6. CP3 — Runtime/Git/worktree coordination

### 6.1 Entry state

- CP2 completion済み。
- External installerは0.2.4 new lifecycle。
- Repo-local wrapperはまだpre-import SH/terminal handoff未対応。
- Existing issue-start/worktree behavior testsは残存。

### 6.2 最初のRED test

- `tests/cli_runtime/test_provider_lifecycle_bootstrap.py::test_t08_pre_import_shared_lease_and_ready_admission_are_enforced`
- `tests/cli_runtime/test_provider_lifecycle_handoff.py::test_t09_update_uninstall_exec_and_helper_lease_lifetime_are_terminal`
- `tests/cli_runtime/test_generation_checkout.py::test_t10_existing_and_new_checkout_are_pinned_and_generation_safe`
- `tests/cli_runtime/test_worktree_lifecycle_coordination.py::test_t11_worktree_b_create_remove_and_make_handoff_are_inode_bound`

Expected REDはcurrent wrapperがline 19でlease前importすること、Git helperにfd lifetimeがないこと、checkoutがbranch名だけであること、worktree createがentrypointを先に公開してmakeをuse-case内実行することです。

### 6.3 Exact owned files and symbols

**MODIFY provider source only**

- `src/spec_dock/assets/spec_dock/scripts/spec-dock`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/app.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/bootstrap.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/dispatch.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/contracts.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/update.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/uninstall.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/contracts.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/ports.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/set_active.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_lifecycle.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/worktree.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/git_cli.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/make_cli.py`

**NEW provider source and tests**

- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/git_helper.py`
- `tests/cli_runtime/test_provider_lifecycle_bootstrap.py`
- `tests/cli_runtime/test_provider_lifecycle_handoff.py`
- `tests/cli_runtime/test_generation_checkout.py`
- `tests/cli_runtime/test_worktree_lifecycle_coordination.py`

**REPLACE current assertions**

- `tests/cli_runtime/test_update.py`
- `tests/cli_runtime/test_uninstall.py`
- bootstrap-specific node in `tests/cli_runtime/test_wrappers.py`
- checkout-specific nodes in `tests/cli_runtime/test_issue_lifecycle.py`
- create/remove/hook-specific nodes in `tests/cli_runtime/test_worktree.py`

### 6.4 Implementation order

1. Frozen bootstrapへcomponent-wise root open、SH NB、ready admission、exact diagnosticsを実装します。
2. `app.run`/`dispatch`/`CommandOutcome`をreturn-onlyにし、ordinary emitをbootstrapへ移します。
3. update/uninstallを`InstallerExecRequest`へ変更し、bootstrapのclose→exec、direct streams/status、127を実装します。
4. `git_helper.py`と`pass_fds` allowlistを実装し、real process lifetime/SIGKILL testをGREENにします。
5. `GitCapabilityAssessment`（`post-checkout`、`reference-transaction`、`post-index-change`を含むeffective hook guard）とGit object provider closure digestを実装します。
6. Existing/new pinned checkoutとpre/post generation guardを実装します。
7. `issue_start`へpost-checkout revalidationを挿入し、drift時active/sync 0を保証します。
8. Worktree createをno-checkout/pinned materialization/entrypoint-lastへ変更します。
9. Worktree removeをB EX/original inode/path C preservationへ変更します。
10. `ConsumerHookRequest`、nonlocking B fd、bootstrap fchdir make runner、existing status/warning/outer exitを実装します。
11. Provider runtime testsをGREENにし、provider bootstrap/runtime bytesを固定してcandidate digestへ反映します。Dogfoodへは投影しません。

### 6.5 Narrow verification

```bash
uv run pytest -q \
  tests/cli_runtime/test_provider_lifecycle_bootstrap.py \
  tests/cli_runtime/test_provider_lifecycle_handoff.py \
  tests/cli_runtime/test_generation_checkout.py \
  tests/cli_runtime/test_worktree_lifecycle_coordination.py \
  tests/cli_runtime/test_update.py \
  tests/cli_runtime/test_uninstall.py \
  tests/cli_runtime/test_wrappers.py \
  tests/cli_runtime/test_issue_lifecycle.py \
  tests/cli_runtime/test_worktree.py
make lint
```

Expected result:

- Commands exit 0。
- Module import spyはSH acquisition/ready validation後にだけ発火。
- Runtime SH vs installer EX、two SH coexistence、busy/unavailable/unsafe/not-ready exact diagnostics。
- Parent-only SIGKILL中はinstaller busy、helper exit後EX succeeds。
- A→B/B→A、same/cross target、全retained flagsでold-module return 0。
- Existing/new checkout accepted、三種のwriting hookを含むdifferent/unprovable capabilityでpre-checkout mutation 0、post drift active/sync 0。
- Worktree create before entrypoint publicationはruntime unavailable、after publicationはcomplete/clean。
- Remove path C preserved。
- make hookはlocking fd 0でoriginal B cwd、nested installer self-contentionなし、outer exit 0。

### 6.6 Completion state

- Cooperative lifecycle/runtime/Git/worktree modelがend-to-end GREEN。
- Bootstrap bytes固定。
- Provider runtime sourceのfocused testsとbootstrap hashが固定。
- Dogfoodは旧projectionのままで、CP4 artifact proof前には部分同期しない。
- Packaging/full suiteはCP4待ち。

### 6.7 Stop condition

- Frozen bootstrapがreplaceable moduleをlease前にimportする必要がある。
- Helperがwriting descendantへleaseを保持できない。
- Git capabilityを無断disableしなければ同一bytesを証明できない。
- Existing branch checkoutでGitのother-worktree/merge/rebase guardを迂回する必要がある。
- Worktree B entrypoint-lastでfinal clean index/HEADを証明できない。
- Consumer hookをold moduleへ戻らずrenderできない。

### 6.8 Next-step handoff

CP3 summaryにreal concurrency process evidence、bootstrap SHA、Git/worktree behaviorを記録し、CP4 packetだけを渡します。まだmergeしません。

## 7. CP4 — Packaging, dogfood, test migration and B1 acceptance

### 7.1 Entry state

- CP1–CP3 completion済み。
- Source/new runtime focused tests GREEN。
- Old writer absent。
- Dogfoodは旧projectionのままで、CP4のartifact proof後にだけcomplete candidateへ同期する。
- Full current gatesとbuilt artifactsは未受入。

### 7.2 最初のRED test

- `tests/integration/test_provider_lifecycle_dogfood.py::test_t13_source_wheel_sdist_installed_and_dogfood_candidate_are_identical`
- `tests/integration/test_issue_392_acceptance.py::test_t14_transitional_gates_baseline_and_issue_boundary_are_unchanged`

Expected REDはpackage inventory/dogfood/test disposition/provider-ci commandがまだfinal candidateへ整列していないことです。Version 0.2.4はCP2で固定済みです。

### 7.3 Exact owned files

**READ-ONLY**

- `pyproject.toml`の`[project].version=0.2.4`。実buildで追加設定が必要と判明した場合は、exact keyを指定したpacket訂正へ戻る。

**MODIFY**
- 必要な場合だけ`setup.py`のpackage/stale-prune allowlist
- `.github/workflows/provider-ci.yml`
- `README.md`
- `src/spec_dock/assets/spec_dock/docs/README.md`
- `src/spec_dock/assets/spec_dock/docs/migration.md`
- `src/spec_dock/assets/spec_dock/docs/reference_worktree.md`
- matching dogfood docs under `spec-dock/docs/`
- `.agents/skills/spec-dock/**` provider/dogfood pair
- `.agents/skills/spec-dock-grill-with-docs/**` provider/dogfood pair
- Test files classified REPLACE/RETIRE in the test Artifact

**NEW**

- `tests/integration/test_provider_lifecycle_dogfood.py`

**MODIFY EXISTING**

- CP2で作成済みの`tests/integration/test_issue_392_acceptance.py`へT14だけを追加

**NO-TOUCH**

- 14 active node identities/signatures/lifecycle
- 243 timing entries
- final gate implementation

### 7.4 Implementation order

1. CP2で固定済みのversion 0.2.4をread-only確認し、provider package data、fixture、docs、two skills、new package inventoryをcomplete candidateへ整列します。
2. Provider source testsをGREENにし、complete provider candidate digestを固定します。
3. 同じsource treeからwheel/sdistをbuildし、isolated environmentでinstalled packageだけをimportしてcandidate/fixture/bootstrap/docs/skillsを検証します。
4. Artifact proofがGREENになった後だけ、provider sourceからdogfood scripts/docs/two skillsを一括byte projectionします。Partial projectionは禁止します。
5. T13でsource/wheel/sdist/isolated install/fresh install/dogfood parityを検証します。
6. Existing test filesをtest ArtifactどおりKEEP/REPLACE/RETIREします。Successor GREEN前削除はしません。
7. Resolved successor nodeidを維持します。
8. Provider CIのold focused commandをnew lifecycle focused commandへ差し替え、PR-only/Linux-macOS/no-continue-on-error/current full pathsを維持します。
9. T14とstatic acceptanceでold imports/path strings 0、Wire counts、required-fast、15/14/1、243、mirror parityを検証します。
10. Default fast、current explicit full verifier、platform parityを実行します。
11. Review findingsを修正し、全変更を一つの#392 PRへまとめます。

### 7.5 Narrow and final verification

Focused:

```bash
uv run pytest -q \
  tests/integration/test_provider_lifecycle_dogfood.py \
  tests/integration/test_issue_392_acceptance.py \
  tests/unit/infra/test_init_update.py \
  tests/cli_runtime/test_distribution_cutover.py \
  tests/integration/test_epic_00343_distribution.py
```

Current required gates:

```bash
make lint
uv run pytest
uv run python -m scripts.quality.verify_full_regression --shards 4
```

Provider parity commands retained in `.github/workflows/provider-ci.yml`:

```bash
uv run pytest tests/unit/provider_lifecycle
uv run pytest --run-full-regression --full-regression-shard tests/cli_runtime/test_distribution_cutover.py
uv run pytest --run-full-regression --full-regression-shard tests/integration/test_epic_00343_distribution.py
```

Expected result:

- All commands exit 0、unexpected failure 0。
- Required-fast four nodeids collected/executed as current policy requires。
- Register 15 rows/14 active/1 resolved、active signatures/lifecycle unchanged。
- Timing entries exactly243。
- Source/wheel/sdist/installed/dogfood candidate/fixture/bootstrap parity。
- Linux/macOS provider parity GREEN。
- Old writer/manifest/journal authority references 0。
- No `continue-on-error`、skip/xfail/approved failure追加。

### 7.6 Completion state

- #392 Product、tests、docs、packaging、dogfoodが一つのcandidateとしてGREEN。
- PR baseはEpic integration branch、mergeは未実施。
- Reportへ実行したexact commands/results/hashを記録。
- Human merge gateへ渡せる。

### 7.7 Stop condition

- Full/current gateを通すため#395 active failureを修正する必要がある。
- #396 toolingを先取りする必要がある。
- Built artifactとsource/dogfoodが一致しない。
- Provider CIを弱める、skip/xfail/continue-on-errorが必要になる。
- Human merge前にmainへ向ける必要がある。

### 7.8 Next-step handoff

Luna Maxの実装作業は終了し、Codexがwhole diff、review、PR準備を行います。人間だけがPRをEpic integration branchへmergeします。

## 8. Human merge and B1 post-merge gate

1. PR baseが`codex/epic-00384-provider-test-strategy-planning`であることを確認する。
2. Candidate head SHA、review pass、all required checks、baseline integrityを確認する。
3. 人間がmergeする。Agentはmergeしない。
4. Merged Epic branch tipのfull SHAを固定する。
5. CP4 current required gatesとprovider parityをmerged tipで再実行する。
6. Source/dogfood/ledger/timing/required-fastを再検証する。
7. 全てGREENならB1を記録し、#392をclose可能とする。
8. B1 GREEN後だけ#395をstartする。

Merge後failureでは#395を開始せず、#392 mergeをhuman revertしてB0へ戻すか、#392 PR相当のrepairを人間判断します。Partial cherry-pickで状態を混ぜません。

## 9. Operational risk plan

| Concern | Applicability / control |
|---|---|
| Security/privacy | Applicable。No-follow、owner/mode、fd allowlist、content-free public diagnostics、private stateへuser data/credential非格納をtestする。Wireのclosed continuation二fieldだけはnormalized targetのabsolute pathを含み得るため、任意path field禁止と不要なevidence転載禁止も検証する。 |
| Blast radius | High。Installer、runtime、Git、worktree、packagingを跨ぐ。Checkpointで局所化するがmergeは一つ。 |
| Migration | Applicable。Exact-clean 0.2.3 only、human maintenance window、external installer、post-mutation forward recovery。 |
| Staged rollout | Production feature flag rolloutはN/A。Integration branch B0→B1が唯一のstaged rolloutで、mainへ直接出さない。 |
| Kill switch | Runtime toggleはN/Aかつ禁止。Human PR merge停止またはwhole merge revertがkill switch。 |
| Backup/restore | User-data backupをlifecycleが作るのはN/A。Provider rootsのold generationはoperation中stageにのみ存在し、完了後は破棄。Git branch/repository backupはhuman運用。 |
| Forward recovery | Applicable。ACTIVE/stage/receiptとexact tuple/tokenだけ。Manual private deletion、operation switch、old writer fallback禁止。 |
| Rollback | Unmergedはbranch discard、merged B1 failureはhuman whole-merge revert。Partial old writer restore禁止。 |
| Incident response | New invocation停止、exact root/ACTIVE/receipt/record bytesとpublic result保存、protected dataへ触れずparentへ報告。Cleanup tokenを公開ログへ不要に転載しない。 |
| Ownership | #392 owns lifecycle。#395/#396 read-only。Post-merge保守はrepository maintainer。 |
| Human gate | Spec review、clean pushed freeze/projection、PR review/merge、B1 revalidation、legacy maintenance windowはhuman/Codex gate。 |

## 10. Incident response procedure

1. 新規SpecDock command/automationを停止する。
2. Consumerのspec/Artifact/workbenchを移動・修正しない。
3. External installerのpublic JSON/text、exit、candidate digest、target labelを保存する。
4. Private pathはownerがread-only確認する。Unknown objectを削除しない。
5. ACTIVE/receipt/recordのhash、repository `(dev,ino)`、OS、native capability、operation generationを記録する。秘密tokenは必要な担当者以外へ出さない。
6. Wireのexact continuationがある場合だけそのcommandを実行する。別operationへ切り替えない。
7. Wireにない状態、identity drift、foreign objectなら停止し、parentへcontract gapとして返す。
8. B1 merge後のincidentでは#395を開始せず、human revert判断を行う。

## 11. Plan completion and current gate

本Planはcritical-level唯一の実装計画候補です。Checkpoint packetは[実装引継ぎ](artifacts/20260908t011846z-luna-max-implementation-handoff.md)に定義します。独立内容reviewとclean pushed freeze/projectionが未完了であるため、現時点でProduct実装を開始しません。
