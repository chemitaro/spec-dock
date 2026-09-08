---
種別: artifact
ID: "20260908t011846z"
タイトル: "Luna Max 実装引継ぎ"
状態: "detailed-review-candidate"
作成者: "blue-team specification author"
最終更新: "2026-09-08"
親: ["iss-00392"]
template: "blank"
authority: "evidence"
derived_from: ["../requirement.md", "../design.md", "../plan.md", "20260908t011846z-01-lifecycle-test-ownership-and-migration.md"]
reflected_to: ["../plan.md"]
implementation_allowed: false
repository_evidence:
  repository: "chemitaro/spec-dock"
  branch: "iss-00392-provider-lifecycle-and-regression-gate-hard-cutover"
  baseline_sha: "dc638e936e763cc7a6087f258201ed9ed654e7fb"
  baseline_tree: "17ce38234033393c385c4b17e40c0ccdc78bfc19"
---

# Luna Max 実装引継ぎ

## 1. 使用方法

このArtifactは、GPT-5.6 Luna / reasoning Maxへ「#392を全部実装する」と一括委譲するためのpromptではありません。CodexはG0を満たした後、**次のcheckpoint一件だけ**をexecution packetとして渡します。Luna Maxはpacket外のcheckpoint、#395、#396、PR mergeへ進みません。

現時点の`implementation_allowed`は`false`です。Baseline SHAは仕様作成時の調査identityであり、実装packetのfreeze SHAではありません。実行時は、独立review済み仕様を含むclean pushed Issue branch tipをCodexがpacketへ注入し、そのfull SHAとremote tipをLuna MaxがGitHub/localの両方で一致確認します。

## 2. Execution packet template

```yaml
packet_schema: 1
issue: "#392"
checkpoint: "CP1 | CP2 | CP3 | CP4"
repository: "chemitaro/spec-dock"
branch: "iss-00392-provider-lifecycle-and-regression-gate-hard-cutover"
freeze_sha: "<40-hex supplied by Codex>"
base_branch: "codex/epic-00384-provider-test-strategy-planning"
implementation_allowed_evidence:
  spec_review_receipt: "<immutable receipt path/hash>"
  projection_readback: "<GitHub readback identity>"
  previous_checkpoint_receipt: "<none for CP1, exact receipt for later CP>"
objective: "<one checkpoint outcome only>"
entry_state_assertions:
  - "<exact observed fact>"
immutable_contracts:
  - "provider-lifecycle-wire-contract.md v12"
  - "Requirement/Design/Plan at freeze_sha"
  - "15 rows / 14 active / 1 resolved / 243 timing / four required-fast"
owned_files_and_symbols:
  - "<exact path and symbol>"
no_touch:
  - "parent Wire/ADR/register"
  - "#395/#396 Product responsibility"
  - "main and Epic integration branch history"
first_red:
  command: "<narrow pytest command>"
  expected_failure: "<missing behavior only>"
implementation_sequence:
  - "<ordered operation>"
verification:
  - command: "<narrow command>"
    expected: "exit 0 and exact evidence"
stop_conditions:
  - "wire gap, baseline drift, scope expansion, unsafe fallback, unrelated failure"
completion_receipt:
  required_fields:
    - freeze_sha
    - working_tree_status
    - changed_files
    - changed_symbols
    - red_evidence
    - green_commands_and_results
    - unresolved_findings
    - next_checkpoint_ready
next_handoff: "Return to Codex; do not start the next checkpoint."
```

### Packet execution invariants

1. 最初にroot `AGENTS.md`、packet、Requirement、Design、Plan、test Artifactを読みます。
2. `git rev-parse HEAD`、remote branch tip、packet `freeze_sha`をbyte-for-byte一致させます。不一致なら変更0で停止します。
3. Existing working tree差分、untracked Product files、baseline driftがあれば停止します。
4. First REDを実行し、指定した欠落だけで失敗することを確認します。Unrelated failureや既存approved failureをRED代用にしません。
5. Owned files/symbolsだけを変更します。必要な新fileがpacket外ならDesign gapとして戻します。
6. Narrow verificationがGREENでもnext checkpointを開始しません。Completion receiptをCodexへ返します。
7. Commit/pushはCodexの上位workflowが明示した場合だけ行い、PR作成/merge、Issue close、integration branch direct pushは行いません。

## 3. CP1 concrete packet — Closed lifecycle foundation

### Objective

Wire v12をdeterministic codeへ投影し、candidate/record/marker/legacy fixture、private namespace/ACTIVE/stage/receipt、Linux/macOS native atomic Adapter、lease primitiveを、public CLI未接続のpure foundationとして完成させます。

### Entry state

- G0 receiptあり。
- Product versionは0.2.3、旧writerがpublic owner。
- Parent wire/ADR/registerはread-only。
- 15/14/1、243、four required-fast一致。
- CP2以降のroute変更は未着手。

### Owned files/symbols

- NEW `src/spec_dock/provider_lifecycle/{__init__,contracts,_wire_generated,wire,candidate,legacy_fixture,private_state,filesystem,coordination}.py`
- NEW `scripts/maintenance/generate_provider_lifecycle_wire.py`
- NEW `scripts/maintenance/generate_provider_lifecycle_legacy_fixture.py`
- NEW `src/spec_dock/assets/provider_lifecycle/legacy-0.2.3.json`
- NEW `tests/unit/provider_lifecycle/test_{wire,candidate,authority,private_state,atomic_filesystem}.py`
- Exact symbols are Design §3、§8、§11、§12.1。`engine.py`とpublic CLI接続はCP2です。

### First RED

```bash
uv run pytest -q   tests/unit/provider_lifecycle/test_wire.py::test_t01_wire_v12_inventory_and_generated_projection_are_exact   tests/unit/provider_lifecycle/test_private_state.py::test_t04_prepared_active_precedes_stage_and_p1_only_rebuilds_registered_entries   tests/unit/provider_lifecycle/test_atomic_filesystem.py::test_t05_linux_and_macos_native_atomic_adapters_have_no_unsafe_fallback
```

Expected: new package/projection/Adapterが存在しないためfailし、Wire parseは6/41/23/24/168/40/4を読み取れます。

### Implementation sequence

1. GeneratorをWire v12 parserとして実装し、finite values/relation/goldensのcountとuniquenessを検証して`_wire_generated.py`を生成します。
2. Strict compact JSON parser/serializerとimmutable contractsを実装します。
3. Six-domain candidate grammarとslot marker注入を実装します。
4. Verified Git objectだけからlegacy fixtureを生成し、regeneration mismatchをfailさせます。
5. Repository/euid-bound private namespace、strict stores、bounded inode witness、P0/P1/P2 classifierを実装します。
6. Linux/macOS native Adapterを実装し、fallback禁止をtestします。
7. SH/EX lease primitiveとinherited-fd validatorを追加します。Runtime接続はしません。

### Verification

```bash
uv run pytest -q tests/unit/provider_lifecycle/test_wire.py   tests/unit/provider_lifecycle/test_candidate.py   tests/unit/provider_lifecycle/test_authority.py   tests/unit/provider_lifecycle/test_private_state.py   tests/unit/provider_lifecycle/test_atomic_filesystem.py
uv run python scripts/maintenance/generate_provider_lifecycle_wire.py --check
uv run python scripts/maintenance/generate_provider_lifecycle_legacy_fixture.py --check
make lint
```

Expected: exit0、generated diff 0、P2 stage inode/bytes unchanged、native fallback references 0、Consumer mutation 0。

### Stop

Wire count/value/golden不足、legacy source不明、native primitiveをunsafe fallbackなしで実装不能、private namespaceがsame filesystem/owner-boundにならない場合は停止します。

### Receipt

Changed paths/symbols、RED/Green output、generated hashes、fixture source commit、platform evidence、remaining P0/P1/P2 uncertaintyを返します。`next_checkpoint_ready`はCodex review後だけtrueです。

## 4. CP2 concrete packet — Installer lifecycle hard cutover

### Objective

Foundationへ`ProviderLifecycleEngine`を追加し、init/update/uninstall public installer routeを新ownerへ一括切替します。Exact-clean migration、WIR-PREP-001、root/slot/seed publication、terminal cleanup/receipt/replayを閉じ、successor GREEN後に旧writer/manifestを撤去します。

### Entry state

- CP1 receiptがreview済み、generated checks GREEN。
- Public CLIはまだ旧owner。
- Parent/CP1 filesに未解決差分なし。

### Owned files/symbols

- NEW `src/spec_dock/provider_lifecycle/engine.py`
- MODIFY `src/spec_dock/provider_lifecycle/__init__.py`
- MODIFY `src/spec_dock/cli.py`の`_parse_args`、`main`とlifecycle adapter。Old helper群はsuccessor GREEN後削除。
- DELETE after proof `src/spec_dock/managed_distribution.py`
- DELETE after proof `src/spec_dock/assets/managed_distribution.json`
- NEW `tests/unit/provider_lifecycle/test_engine.py`
- MODIFY/RETIRE exact test families in test ownership Artifact。

### First RED

```bash
uv run pytest -q   tests/unit/provider_lifecycle/test_engine.py::test_t06_all_fixed_fault_boundaries_converge_to_wire_continuations   tests/unit/provider_lifecycle/test_engine.py::test_t07_legacy_migration_uninstall_and_old_package_mutation_zero
```

Expected: engine/public route不在またはold ownerへ到達してfail。Protected sentinels test自体は実行可能です。

### Implementation sequence

1. Read-only admissionとdry-runを実装します。
2. Prepared ACTIVE→stage→incomplete record→runningの順を実装します。
3. Roots docs/templates/system/scripts、slots、seeds、verify、ACTIVE ready、terminal recordの順を実装します。
4. Terminal cleanup、receipt、token replay、response loss/deferred requestを実装します。
5. Exact-clean 0.2.3 migrationとmaintenance-window diagnosticsを実装します。
6. Tooling-only uninstall/absent recordと`--remove-specs` exit2/mutation0を実装します。
7. CLIをvalidated `LifecycleResult` emit-only adapterへ切替します。
8. T06/T07/T12 successorをGREENにします。
9. Production reference scanが0になった後だけold module/manifest/helper/testを削除します。

### Verification

```bash
uv run pytest -q tests/unit/provider_lifecycle   tests/integration/test_issue_392_acceptance.py::test_t12_public_cli_uses_only_new_lifecycle_and_old_writer_is_absent
uv run pytest --run-full-regression --full-regression-shard tests/cli_runtime/test_distribution_cutover.py
uv run pytest --run-full-regression --full-regression-shard tests/integration/test_epic_00343_distribution.py
make lint
```

Expected: exit0、all fault subcases exact Wire relation、protected data unchanged、old writer/manifest production reference 0。

### Stop

新public code/valueが必要、P2 stage rewriteが必要、root順を守れない、old packageがmutationできる、purge compatibilityのためconsumer spec deleteが必要、successor REDのままold file削除が必要なら停止します。

### Receipt

Fault matrix result、deleted symbols/filesとsuccessor、public golden comparison、old-reference scan、protected sentinel evidenceを返します。CP3を開始しません。

## 5. CP3 concrete packet — Runtime, Git, worktree coordination

### Objective

Frozen bootstrapへpre-import SH admissionを入れ、update/uninstallをrelease-to-execへ変更します。Managed helper lease lifetime、effective Git capability guard、pinned existing/new checkout、post-drift reporting、worktree B create/remove、consumer make terminal handoffを完成させます。

### Entry state

- CP2 public lifecycle/focused tests GREEN。
- New record/root/slot semanticsがsole installer authority。
- Runtimeはまだold import/handoff/Git/worktree behavior。

### Owned files/symbols

- MODIFY provider runtime `src/spec_dock/assets/spec_dock/scripts/spec-dock`
- MODIFY provider runtime `spec_dock_runtime/{app.py,cli/bootstrap.py,cli/dispatch.py,commands/contracts.py,commands/update.py,commands/uninstall.py,application/contracts.py,application/ports.py,application/set_active.py,application/issue_lifecycle.py,application/worktree.py,infra/git_cli.py,infra/make_cli.py`
- NEW `spec_dock_runtime/infra/git_helper.py`
- Mirror copies under `spec-dock/scripts/**` only after provider tests GREEN。
- NEW T08–T11 test files in Plan/Test Artifact。

### First RED

```bash
uv run pytest -q   tests/cli_runtime/test_provider_lifecycle_bootstrap.py::test_t08_pre_import_shared_lease_and_ready_admission_are_enforced   tests/cli_runtime/test_provider_lifecycle_handoff.py::test_t09_update_uninstall_exec_and_helper_lease_lifetime_are_terminal   tests/cli_runtime/test_generation_checkout.py::test_t10_existing_and_new_checkout_are_pinned_and_generation_safe   tests/cli_runtime/test_worktree_lifecycle_coordination.py::test_t11_worktree_b_create_remove_and_make_handoff_are_inode_bound
```

Expected: current wrapper imports before lease、returns after subprocess、branch-name checkout/worktree path behaviorのためfail。

### Implementation sequence

1. Wrapperをstdlib-only frozen bootstrapへ変え、component no-follow open、SH/NB、record ready、candidate closure、no bytecodeを実装します。
2. `CommandOutcome`へterminal directive unionを追加し、emitをbootstrapへ集約します。
3. Update/uninstallを`InstallerExecRequest`へ変え、全lease close→`execvpe`、direct streams/status、exact127を実装します。
4. Managed Git helperとstrict `pass_fds` allowlist、inherited fd validationを実装します。
5. `post-checkout`、`reference-transaction`、`post-index-change`を含むeffective Git capability guardとGit-object provider closure digestを実装します。設定を変更しません。
6. Existing/new branch refをcommitへpinし、pre-checkout equalityとpost-checkout closure revalidationを実装します。
7. `issue_start`はpost drift時active/syncを呼ばず、branch side effectを報告します。Auto rollbackしません。
8. Worktree createを`--no-checkout`、B EX、object materialization、entrypoint-lastへ変更します。
9. RemoveをB EX、helper lifetime、former-path inode checkへ変更しCを保存します。
10. Make detect/runをterminal `ConsumerHookRequest`へ変え、nonlocking original-B fd、全lease release後fchdir、outer status compatibilityを実装します。
11. Provider runtime GREEN後にdogfood runtimeをbyte同期します。

### Verification

```bash
uv run pytest -q   tests/cli_runtime/test_provider_lifecycle_bootstrap.py   tests/cli_runtime/test_provider_lifecycle_handoff.py   tests/cli_runtime/test_generation_checkout.py   tests/cli_runtime/test_worktree_lifecycle_coordination.py   tests/cli_runtime/test_update.py tests/cli_runtime/test_uninstall.py   tests/cli_runtime/test_wrappers.py tests/cli_runtime/test_issue_lifecycle.py   tests/cli_runtime/test_worktree.py
make lint
```

Expected: exit0、import spy 0 before admission、real SH/EX behavior、parent-only SIGKILL proof、old-module return 0、pre/post checkout expectations、B/C/hook expectations。

### Stop

Lease前import、helper fd lifetime不成立、三種のwriting hookを含むGit capabilityをdisableしなければ通せない、normal worktree/rebase/merge protection bypassが必要、B entrypoint-last不能、hookをold moduleから実行する必要がある場合は停止します。

### Receipt

Bootstrap hash、real process traces、fd allowlist、checkout pin/closure evidence、B/C inode evidence、hook status matrix、provider/dogfood byte parityを返します。CP4を開始しません。

## 6. CP4 concrete packet — Packaging, dogfood and acceptance

### Objective

Version/package inventoryを0.2.4へ整列し、source→wheel→sdist→isolated install→dogfoodを同一candidateへ収束させます。Test ArtifactどおりKEEP/REPLACE/RETIREし、current gatesを弱めず#392 PR acceptance候補を作ります。

### Entry state

- CP1–CP3 receipts review済み。
- Focused Product/runtime tests GREEN。
- Old production writer absent。
- Human merge、B1、#395開始は未実施。

### Owned files/symbols

- MODIFY `pyproject.toml`、必要時のみ`setup.py` package/stale-prune inventory。
- MODIFY `.github/workflows/provider-ci.yml` without trigger/job/protection weakening。
- MODIFY provider README/migration/reference_worktree and exact dogfood mirrors。
- MODIFY provider/dogfood two skill slots。
- MODIFY/DELETE tests exactly per test Artifact。
- NEW `tests/integration/test_provider_lifecycle_dogfood.py`、`tests/integration/test_issue_392_acceptance.py`。

### First RED

```bash
uv run pytest -q   tests/integration/test_provider_lifecycle_dogfood.py::test_t13_source_wheel_sdist_installed_and_dogfood_candidate_are_identical   tests/integration/test_issue_392_acceptance.py::test_t14_transitional_gates_baseline_and_issue_boundary_are_unchanged
```

Expected: version/package/dogfood/provider-ci/test dispositionがfinal candidateへ未整列のためfail。

### Implementation sequence

1. 0.2.4 versionとpackage dataを整列します。
2. Wheel/sdistをbuildし、checkout fallbackなしisolated installでcandidate/fixture/bootstrapを検証します。
3. Provider docs/skillsを更新し、maintenance window、protected data、recoveryを記載します。
4. Providerからdogfoodへcomplete byte projectionします。
5. Test Artifactのordered registryでtestsを移行し、successor GREEN後だけRETIREします。
6. Resolved successor、14 active rows、four required-fast、243 timingを再検証します。
7. Provider CI focused commandだけをnew pathsへ更新し、PR-only/Linux/macOS/SHA assert/no continue-on-errorを維持します。
8. Focused、default fast、current full verifier、packaging/dogfood、platform parityを実行します。
9. Whole diff review用evidenceをReportへ記録し、一つの#392 PR候補にします。

### Verification

```bash
uv run pytest -q tests/integration/test_provider_lifecycle_dogfood.py   tests/integration/test_issue_392_acceptance.py   tests/unit/infra/test_init_update.py   tests/cli_runtime/test_distribution_cutover.py   tests/integration/test_epic_00343_distribution.py
make lint
uv run pytest
uv run python -m scripts.quality.verify_full_regression --shards 4
```

Provider CI exact focused commandsはPlan §7.5を使用します。Expected: all exit0、unexpected failure0、classification gaps0、15/14/1 and 243 unchanged、artifact parity、old references0。

### Stop

#395 baseline repair、#396 gate deletion/build-once、skip/xfail/continue-on-error、main向けPR、partial dogfood、built artifact mismatchが必要なら停止します。

### Receipt and terminal handoff

Candidate SHA、all command results、artifact hashes、classification result、baseline/gate inventory、review findingsをCodexへ返します。Luna MaxはPR mergeを行わず、#395を開始しません。Codexがwhole diff reviewとPR準備を行い、人間がEpic integration branchへmergeします。Merged tip B1再検証がGREENになった後だけ#395開始可能です。

## 7. Handoff rejection conditions

次の場合、packetを実行せずCodexへ返します。

- Freeze SHA不一致、branch不一致、dirty tree。
- Spec review receiptまたはprojection readback不足。
- Wire v12とIssue仕様の実質的矛盾。
- Owned path外のProduct変更が必要。
- Parent public value/三Issue責務/E384-QUAL-001/E384-DEC-001/002の変更が必要。
- Baseline row/signature/lifecycle、required-fast、timing countがdrift。
- Unsupported fallback、user data mutation、automatic rollback、normal Git guard bypassが必要。
- Previous checkpointのreceipt/verificationが不十分。
