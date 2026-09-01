---
種別: 実装計画書（Issue）
ID: "iss-00392"
タイトル: "Provider Lifecycle And Regression Gate Hard Cutover"
関連GitHub: ["#392"]
状態: "draft"
最終更新: "2026-09-01"
依存: ["requirement.md", "design.md", "../../plan.md", "../../artifacts/20260831t152024z-adr-single-implementation-unit-and-provider-hard-cutover-policy.md"]
親: ["epic-00384", "init-local-00003"]
Planning Level: "critical"
正本検証:
  repository: "chemitaro/spec-dock"
  branch: "codex/epic-00384-provider-test-strategy-planning"
  sha: "91667235c6892f025a1d9ee69cf37525537a3c9e"
---

# iss-00392 Provider Lifecycle And Regression Gate Hard Cutover — 実装計画

## 1. Execution rules

1. 本書だけをentry pointとし、Issue Requirement / Designのtrace IDを参照する。
2. Product source of truthは`src/spec_dock/`。provider-firstで変更し、dogfood `spec-dock/`を後から同期する。
3. behavior changeはtest-first。REDが既存testで十分に観測される場合だけ、理由とexact nodeをreportへ記録してnew testを省略できる。
4. 各stepはimplementationとfocused verificationを同時に完了するvertical milestoneである。最後にまとめて検証しない。
5. successor proofより先にold production contractを削除しない。
6. public bridge generation、runtime toggle、old-engine fallbackを作らない。
7. agentはmerge、required-context変更、Issue closeを実行しない。human operationはexact handoffとして提示する。
8. evidenceはIssue directoryの`report.md`へ記録する。canonical R/D/Pをimplementation中に書き換えない。
9. stop condition発火時は同じ#392をopenのまま停止し、指定ownerへevidenceを渡す。
10. 各main merge pointでmainはreleasableでなければならない。
11. I392-S40とI392-S50はPR-B内部のnon-main checkpointであり、完了commitをmainへmergeしてはならない。PR-Bの唯一のmain merge gateは、同一branch/PR上でI392-S40、I392-S50、I392-S60の全proofが完了した後である。

## 2. Common no-touch boundary

全stepに共通して、次を変更しない。

- `spec-dock/initiatives/**`のuser/Historical content。ただし#392 `report.md`、#392自身のgenerated metadata、human-approved lifecycle updateを除く。
- Issue #372のcanonical docs/evidence。
- `spec-dock/.gitignore`とroot `.github/workflows/ci.yml`のdogfood consumer-owned bytes。
- `.agents/skills/`内の2 fixed slots以外。
- `.workbench/**`のconsumer content。test/CI evidenceはignored temporary pathへ生成しcommitしない。
- human review requirement、unrelated required contexts、merge policy。
- #387 implementation paths after I392-S00 baseline fixation。ただし#392がwhole provider rootをdogfood syncする際、provider asset由来のfinal contentへ更新することは本Issue ownershipとしてtraceする。
- release publication、tag、PyPI。

## 3. Step graph

```text
I392-S00 admission
  -> I392-S10 model/classifier/candidate
  -> I392-S20 fresh install/atomic publication
  -> I392-S30 update/convergence
  -> PR-B: one branch / one PR / no main merge until S60
       I392-S40 uninstall/reinstall/public CLI [internal checkpoint]
       -> I392-S50 legacy migration/downgrade tripwire [internal checkpoint]
       -> I392-S60 old engine removal/failure terminalization [PR-B only main merge gate]
  -> I392-S70 build-once CI transition/old CI removal
  -> I392-S80 qualification/dogfood/final handoff
```

## I392-S00 — #387 post-merge deterministic admission and baseline

**Objective and contract-visible outcome**

#387がhuman mergeされたexact main SHAを固定し、#392が依存するmanaged distribution semanticsがauthoring時から変わっていないことを機械的に証明する。baseline old `0.2.3` wheel/sdist、node inventory、active failure inventoryを同じSHAへ束縛する。Product codeは変更しない。

**Exact owned paths and symbols**

- Read-only: repository全体。
- Evidence write only: `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00384-provider-test-strategy-simplification-and-execution-cost-reduction/issues/iss-00392-provider-lifecycle-and-regression-gate-hard-cutover/report.md`
- Ignored temporary: `spec-dock/.workbench/iss-00392/admission/**`
- No production symbol change。

**Explicit non-owned / no-touch paths**

- 全tracked production/test/workflow path。
- branch protection、required contexts。
- #387 code/doc diffの修正。

**Prerequisites and dependency**

- GitHub #387 closed。
- #387 merge commitがmainへhuman merge済み。
- clean working tree。
- exact authoring SHA `91667235c6892f025a1d9ee69cf37525537a3c9e`を取得可能。
- implementation branchは`POST_387_SHA`から作成する。

**Deterministic allowed drift**

Path allowlist:

```text
README.md
pyproject.toml
src/spec_dock/assets/spec_dock/docs/authoring/overview.md
spec-dock/docs/authoring/overview.md
src/spec_dock/assets/spec_dock/system/active-none/initiative/report.md
src/spec_dock/assets/spec_dock/system/active-none/epic/report.md
src/spec_dock/assets/spec_dock/system/active-none/issue/report.md
spec-dock/system/active-none/initiative/report.md
spec-dock/system/active-none/epic/report.md
spec-dock/system/active-none/issue/report.md
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/active.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/contracts.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/set_active.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_lifecycle.py
spec-dock/scripts/spec_dock_runtime/commands/active.py
spec-dock/scripts/spec_dock_runtime/application/contracts.py
spec-dock/scripts/spec_dock_runtime/application/set_active.py
spec-dock/scripts/spec_dock_runtime/application/issue_lifecycle.py
tests/unit/infra/test_authoring_kit_assets.py
tests/unit/application/test_set_active.py
tests/cli_runtime/test_storage_core_cli.py
tests/cli_runtime/test_issue_lifecycle.py
tests/cli_runtime/test_doctor.py
tests/cli_runtime/s09_invariance.py
tests/cli_runtime/test_runtime_active_s05.py
tests/cli_runtime/test_runtime_active_s06.py
tests/conftest.py
full-regression-ledger.json
full-regression-timing-weights.json
spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00356-specdock-core-simplification-and-external-intelligence-boundary/issues/iss-00387-current-surface-workflow-residue-cleanup/**
```

Content restrictions:

- `pyproject.toml`: project version/build-system/dependencies/pytest marker/package-data authorityを変更してはならない。#387 planが許可したstale mypy overrideと`assets/install_root/.codex/**` phantom package-data removalだけを許可する。
- `tests/conftest.py`: #387が削除したexact node IDのset membership removalだけを許可する。`pytest_addoption`、`pytest_collection_modifyitems`、`pytest_sessionfinish`、`HEAVY_NODE_PREFIXES`、`POLICY_SKIP_REASON`、ledger evaluationを変更してはならない。
- ledger/timing: #387でdeleted/retiredとなったexact node entryのremove/terminal updateだけを許可し、schema、command、failure approval rule、other weightsを変更してはならない。
- provider/dogfood pairはcontent-equivalentでなければならない。

Protected path driftは一件でも停止:

```text
src/spec_dock/cli.py
src/spec_dock/managed_distribution.py
src/spec_dock/assets/managed_distribution.json
src/spec_dock/assets/install_root/**
.github/workflows/**
scripts/quality/**
tests/unit/infra/test_managed_distribution.py
tests/unit/infra/test_init_update.py
tests/cli_runtime/test_distribution_cutover.py
tests/cli_runtime/test_uninstall.py
tests/cli_runtime/test_update.py
tests/integration/test_epic_00343_distribution.py
```

**RED evidence or justified no-new-test rule**

Admissionのためnew product testは作らない。REDはallowlist checkerが意図的にprotected dummy pathを入力したdry-run fixtureでnonzeroになること、content checkerがforbidden `pyproject.toml` changeをrejectすることで示す。checkerをrepositoryへcommitせず、reportへcommand/exitを残す。

**Smallest implementation action**

1. GitHub/APIとGitで#387 state、merge commit、main ancestryを取得する。
2. `POST_387_SHA`をfull SHAで固定する。
3. `git diff --name-status 91667235c6892f025a1d9ee69cf37525537a3c9e..$POST_387_SHA`をallowlistへ通す。
4. restricted filesのzero-context diffをcontent ruleへ通す。
5. current commandsを実行する。
6. clean detached worktreeからbaseline wheel/sdistをone invocationでbuildしhashする。
7. baseline wheelでfresh consumerを作り、legacy root/slot digest fixture source dataを生成する。
8. node inventory、active ledger rows、ruleset/readable protection stateをcaptureする。

**Focused verification commands**

```bash
test -z "$(git status --short)"
git merge-base --is-ancestor "$ISSUE_387_MERGE_SHA" "$POST_387_SHA"
git diff --name-status 91667235c6892f025a1d9ee69cf37525537a3c9e.."$POST_387_SHA"
uv run python -c 'import tomllib; p=tomllib.load(open("pyproject.toml","rb")); assert p["project"]["version"]=="0.2.3"'
make lint
uv run pytest -q
uv run python -m scripts.quality.verify_full_regression --shards 4
rm -rf spec-dock/.workbench/iss-00392/admission/dist
uv build --sdist --wheel --out-dir spec-dock/.workbench/iss-00392/admission/dist
python3 ./spec-dock/scripts/spec-dock validate
git diff --check
test -z "$(git status --short)"
```

**Expected observable result**

- allowlist/content check pass。
- all current gates pass under current policy。
- baseline package version exactly `0.2.3`。
- exactly one wheel and one sdist、hash recorded。
- legacy fresh workspace digest data generated。
- tracked tree clean。

**Evidence to record in Issue `report.md`**

`AUTHORING_SHA`、`ISSUE_387_MERGE_SHA`、`POST_387_SHA`、diff path table、content restriction result、commands/exit/duration、baseline filenames/hashes、legacy tree digests、node inventory digest、active ledger exact node list、rulesets/protection read result。

**Stop conditions and escalation owner**

Any mismatch、#387 not merged、version != 0.2.3、protected drift、baseline failure、dirty treeで停止。Owner: repository owner / Product owner `chemitaro`。Implementation agentはallowlistを拡張しない。

**Cleanup**

Detached worktreeとtemporary virtual environmentを削除する。baseline artifact/hash evidenceはignored workbenchに保持し、binaryをcommitしない。

**Merge-point invariant**

Admissionはcode diffを作らない。mainは#387 merge後のreleasable stateのまま。

**Trace IDs**

I392-RQ-001、I392-RQ-014、I392-RQ-019、I392-D-014、I392-D-018。

## I392-S10 — Fixed model, record, classifier, candidate, legacy fixture

**Objective and contract-visible outcome**

Public routeを変更せず、final fixed paths、strict record/marker、candidate digest、target classifier、single-version legacy fixtureをdirect APIで利用可能にする。old product behaviorはmain上で維持する。

**Exact owned paths and symbols**

```text
src/spec_dock/provider_lifecycle/__init__.py
src/spec_dock/provider_lifecycle/model.py
src/spec_dock/provider_lifecycle/candidate.py
src/spec_dock/provider_lifecycle/legacy_023.py
src/spec_dock/assets/legacy_0_2_3.json
tests/unit/infra/test_provider_lifecycle_model.py
tests/unit/infra/test_provider_lifecycle_candidate.py
tests/unit/infra/test_provider_assets.py
```

Symbols: I392-D-002のmodel/candidate/legacy symbols。`FINAL_DISTRIBUTION_VERSION`のproduction valueは`0.2.4`。

**Explicit non-owned / no-touch paths**

`src/spec_dock/cli.py`、`managed_distribution.py/json`、provider workflows、current old tests、dogfood roots/slots/record。

**Prerequisites and dependency**

I392-S00 pass。baseline legacy fixture input/hash固定済み。

**RED evidence**

最初に次のfailing testsを追加する。

- exact constants/path order
- strict record exact keys/state-operation invariants/duplicate key/size/type
- slot marker exact keys/digest match
- candidate rejects symlink/special/hard link/path traversal
- candidate digest deterministic、mode/content/version sensitive、seed/marker excluded
- record JSON blocks old canonical version parsing fixture
- legacy fixture exact 4 roots、2 slots、recovery paths
- legacy recognizer: exact/absent slots pass、modified/foreign/recovery block

**Smallest implementation action**

Dataclasses/enums/strict parser、candidate capture/digest、legacy fixture loader/whole-tree observationを実装する。No mutation functionを作らない。

**Focused verification commands**

```bash
uv run pytest -q \
  tests/unit/infra/test_provider_lifecycle_model.py \
  tests/unit/infra/test_provider_lifecycle_candidate.py \
  tests/unit/infra/test_provider_assets.py
uv run ruff check src/spec_dock/provider_lifecycle \
  tests/unit/infra/test_provider_lifecycle_model.py \
  tests/unit/infra/test_provider_lifecycle_candidate.py \
  tests/unit/infra/test_provider_assets.py
uv run mypy src/spec_dock/provider_lifecycle
```

**Expected observable result**

All new unit tests pass。No CLI behavior/tree mutation。Legacy fixture hashがS00 generated dataと一致する。

**Evidence to record**

RED node/expected failure、GREEN command/exit、candidate digest examples、legacy fixture source baseline hash、coverage-to-trace table。

**Stop conditions and escalation owner**

Baseline fixtureをper-file historical catalogへ拡張しないと認識できない、fixed path以外が必要、record schemaへprogress/checkpointが必要になった場合停止。Owner: Product owner。

**Cleanup**

Test temp dirs/cacheを削除。generated fixture script/outputのうちcommitted JSON以外を削除。

**Merge-point invariant**

Dormant successorのみ。public CLIはold engineのまま、existing gatesもGREEN。Runtime toggleなし。

**Trace IDs**

I392-RQ-002〜007、I392-RQ-014、I392-D-001〜006、I392-D-010、I392-D-014。

## I392-S20 — Descriptor-bound filesystem and fresh install vertical slice

**Objective and contract-visible outcome**

Fresh targetに対しcandidate全体をstage/validateしてから、4 roots、2 slots、seeds、ready recordをfinal orderでatomic publishするdirect service sliceを完成する。foreign collisionとunsafe bindingはmutation zeroでblockする。

**Exact owned paths and symbols**

```text
src/spec_dock/provider_lifecycle/filesystem.py
src/spec_dock/provider_lifecycle/service.py
tests/unit/infra/test_provider_lifecycle_filesystem.py
tests/unit/infra/test_provider_lifecycle_service.py
tests/unit/infra/test_provider_lifecycle_faults.py
```

Symbols: `PosixProviderFilesystem`、binding/native rename/record publication、`ProviderLifecycleService.install_tooling`、`LifecycleFaultHook`。

**Explicit non-owned / no-touch paths**

Public `cli.py` route、update/uninstall routing、legacy old engine、workflow、dogfood tracked tree。

**Prerequisites and dependency**

I392-S10 GREEN。Linux/macOS native symbol behaviorはunit wrapperとplatform probeで確認可能。

**RED evidence**

- stage/source digest mismatch leaves target digest unchanged
- root/parent symlink、hard-link record、foreign fixed root/slot block
- fresh order and ready-last
- existing seed bytes/type preserved
- absent seeds created exactly once
- `.github` parent symlink block when seed absent
- executable mode preserved
- native no-replace/exchange wrapper fail closed
- fault after each durable boundary yields incomplete record and protected data unchanged

**Smallest implementation action**

Root lock/binding、external deterministic stage、native rename wrappers、atomic record、directory publish、seed creation、fresh install serviceだけを実装する。Update/uninstall behaviorはまだpublicに接続しない。

**Focused verification commands**

```bash
uv run pytest -q \
  tests/unit/infra/test_provider_lifecycle_filesystem.py \
  tests/unit/infra/test_provider_lifecycle_service.py \
  tests/unit/infra/test_provider_lifecycle_faults.py \
  -k 'fresh or binding or candidate or seed or publish'
make lint
```

**Expected observable result**

Synthetic fresh workspaceがfinal 4 roots/2 slots/recordを持ち、seed ruleとprotected digestを満たす。Injected failureはsuccessにならず、record state/operationがexactである。

**Evidence to record**

Mutation order log、pre/post protected digest、record/marker sample、fault-point table、native primitive availability、RED/GREEN commands。

**Stop conditions and escalation owner**

Generic `os.rename` fallbackが必要、target内部arbitrary stagingが必要、seed overwriteが必要、root単位でなくper-file recoveryが必要になった場合停止。Owner: Product owner / filesystem safety reviewer。

**Cleanup**

Owned external stagesを削除。cleanup failure testではwarning evidenceを残した後test temp parentごと削除。

**Merge-point invariant**

Public productはold engine。Dormant fresh serviceはdirect testsでGREEN。Existing ordinary/full gatesがGREEN。

**Trace IDs**

I392-RQ-002〜010、I392-RQ-013、I392-D-007〜009、I392-D-012。

## I392-S30 — Update, incomplete convergence, cross-intent/cross-candidate blocking

**Objective and contract-visible outcome**

Ready/incomplete workspaceに対するwhole-root/slot update、missing repair、same-operation same-candidate convergenceをdirect serviceで完成する。No automatic rollback。

**Exact owned paths and symbols**

Existing S10/S20 files:

```text
src/spec_dock/provider_lifecycle/model.py
src/spec_dock/provider_lifecycle/candidate.py
src/spec_dock/provider_lifecycle/filesystem.py
src/spec_dock/provider_lifecycle/service.py
tests/unit/infra/test_provider_lifecycle_service.py
tests/unit/infra/test_provider_lifecycle_faults.py
```

Symbols: `update_tooling`、`resume_incomplete`、state transition validation、exchange publication。

**Explicit non-owned / no-touch paths**

Public CLI、uninstall/purge code、legacy production route、workflow、old test deletion。

**Prerequisites and dependency**

I392-S20 GREEN。Fresh serviceがready recordを生成できる。

**RED evidence**

- modified record-owned root whole-replaced
- missing root/slot repaired
- marker mismatch blocks before write
- fault after each root/slot/ready boundary
- matching rerun skips already-matching targets and completes
- different candidate digest blocks
- uninstall intent against incomplete install/update blocks
- root/parent identity race fails closed
- cleanup-only failure after ready returns warning exit semantic

**Smallest implementation action**

Update planとresume classifierを追加し、fresh publish primitiveを再利用する。Persistent progress listは追加しない。Current target observationとcandidate comparisonだけでremaining workを決める。

**Focused verification commands**

```bash
uv run pytest -q \
  tests/unit/infra/test_provider_lifecycle_service.py \
  tests/unit/infra/test_provider_lifecycle_faults.py \
  -k 'update or incomplete or resume or cross_intent or cross_candidate or warning'
make lint
```

**Expected observable result**

全fault pointでfirst runがexpected partial failure、same candidate rerunがreadyへ収束。Cross-intent/candidateはmutation_started false。

**Evidence to record**

Fault matrix（point、first status、record、rerun status）、target action order、cross-block codes、protected digest。

**Stop conditions and escalation owner**

Operation checkpoint/progress bit、automatic rollback、old engine fallbackが必要になった場合停止。Owner: Product owner。

**Cleanup**

Owned stage/tombstone cleanupを検証し、test tempを削除。

**Merge-point invariant**

Public productはold engine。Dormant successor install/updateがGREEN。No new public generation。

**Trace IDs**

I392-RQ-009〜010、I392-RQ-013、I392-RQ-018、I392-D-009〜013。

## I392-S40 — Tooling-only uninstall, durable reinstall, public CLI hard cutover, purge trap

**Objective and contract-visible outcome**

Uninstall/reinstallを完成し、package versionを`0.2.4`へ上げ、`init`/`update`/`uninstall`をnew servicesへ一度に接続する。`--remove-specs`をpermanent mutation-zero trapへ変更する。これはPR-B branch内部でcombined public hard cutoverを開始するcheckpointであり、mainへのcutover pointではない。S40のcommitを単独でmainへmergeしてはならない。

**Exact owned paths and symbols**

```text
pyproject.toml
src/spec_dock/cli.py
src/spec_dock/provider_lifecycle/service.py
src/spec_dock/provider_lifecycle/public_result.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/uninstall.py
spec-dock/scripts/spec_dock_runtime/commands/uninstall.py
README.md
tests/unit/infra/test_provider_lifecycle_public_result.py
tests/cli_runtime/test_provider_lifecycle.py
tests/cli_runtime/test_uninstall.py
tests/cli_runtime/test_update.py
```

Symbols: `uninstall_tooling`、dispatch functions、public result mappers、CLI parser/dispatch。`_run_uninstall_explicit_spec_history_purge`とpurge request/result helpersは削除対象。

**Explicit non-owned / no-touch paths**

User history、seed bytes、provider workflows、managed engine file（まだsuccessor proofのため削除しない）、old CI machinery、release publication。

**Prerequisites and dependency**

I392-S30 GREEN。I392-S40、I392-S50、I392-S60を同一branch/PRで連続実行する。S40でpublic routeを切り替えても、S50のmigration/downgrade proofとS60のold engine/test terminalizationが完了するまでPR-Bはmerge不可能である。

**RED evidence**

- uninstall dry-run complete action set/mutation zero
- apply without specs flag succeeds tooling-only
- keep alias exact-equivalent
- remove trap precedence on missing/invalid target、text/JSON、exit 2、mutation zero
- uninstall ready/legacy/tooling-absent states
- durable record remains
- reinstall does not recreate deleted seeds
- `init --force` state dispatch
- `update` absent installs without seeds
- public text/JSON existing fields + additive code/mutation_started
- wrapper forwarding remains `uvx --no-cache`
- public success/error channels and exit map

Before implementation these tests must fail against old semantics、特に`uninstall --apply` without specs modeとremove trap。

**Smallest implementation action**

1. Implement uninstall direct service and result adapter。
2. Wire parser/dispatch to successor only。
3. Set project version `0.2.4`。
4. Remove public callsites to old fresh/recognized/deprovision/purge executors。
5. Update shipped runtime uninstall help/forwarding semantics and dogfood mirror。
6. Update README public guidance。
7. Keep old engine file temporarily unreachable until S50/S60 proof。

**Focused verification commands**

Current root policy still marks CLI runtime as full-regression; use explicit current flags until I392-S60:

```bash
uv run pytest -q tests/unit/infra/test_provider_lifecycle_public_result.py
uv run pytest --run-full-regression --full-regression-shard -q \
  tests/cli_runtime/test_provider_lifecycle.py \
  tests/cli_runtime/test_uninstall.py \
  tests/cli_runtime/test_update.py
uv run python -c 'import tomllib; p=tomllib.load(open("pyproject.toml","rb")); assert p["project"]["version"]=="0.2.4"'
make lint
```

**Expected observable result**

Public commands use only new services。Uninstall default/apply/aliases/trap satisfy matrix。Purge mutation path is unreachable。User data/seeds remain identical。

**Evidence to record**

Parser help snapshots、command/state matrix、text/JSON payloads、exit codes、mutation_started、protected digests、version bump、old service callsite grep result。

**Stop conditions and escalation owner**

Public route needs runtime toggle/bridge、purge compatibility requires mutation、seed update is needed、existing JSON field removal is unavoidable。Stop and escalate to Product owner。Do not silently change schema。

**Cleanup**

Remove temporary snapshots not used as test fixtures。Ensure provider/dogfood runtime wrapper pair identical。

**Internal checkpoint invariant (PR-B; no main merge)**

PR-B branch上ではnew `0.2.4` public routeがfocused GREENで、old engineはunreachableかつfallback不可である。ただしlegacy migration/downgrade proofとold engine/test terminalizationが未完了のため、このcommitをmainへmergeしない。許可される次の遷移は同じbranch/PR上のI392-S50だけである。

**Trace IDs**

I392-RQ-008〜013、I392-RQ-016〜018、I392-D-011〜015。

## I392-S50 — Exact legacy migration and old-package composite tripwire

**Objective and contract-visible outcome**

Post-#387 exact `0.2.3` baselineから`0.2.4`へのmigrationとlegacy tooling uninstallをbuilt artifactsで証明し、old packageがfinal workspaceへmutationをattemptしないことをLinux/macOSで証明する。

**Exact owned paths and symbols**

```text
src/spec_dock/provider_lifecycle/legacy_023.py
src/spec_dock/provider_lifecycle/service.py
tests/integration/test_provider_lifecycle_artifacts.py
tests/integration/test_provider_lifecycle_tripwire.py
tests/platform/macos/test_provider_lifecycle_macos.py
tests/support/provider_lifecycle_tripwire/sitecustomize.py
tests/support/provider_lifecycle_tripwire/native_positive_control.py
```

**Explicit non-owned / no-touch paths**

Legacy consumer history/seeds、baseline old artifact bytes、provider CI settings、old engine deletion（S60）。

**Prerequisites and dependency**

同一PR-B branch上でI392-S40 internal checkpointがGREENであり、S40 commitはmainへ未mergeである。S00 baseline wheel/hash available。Final wheel can be built locally。

**RED evidence**

- exact baseline workspace migrates
- modified each root blocks
- each slot absent/exact passes; modified/foreign markerless blocks
- each active recovery marker blocks
- migration failure after record/root/slot resumes only with same final candidate
- legacy uninstall preserves data/seeds
- old command matrix initially must refuse final JSON record
- startup sentinel proves tripwire loaded
- Python write positive control trapped before write
- Linux native `renameat2` positive control trapped before call
- macOS native `renameatx_np` positive control trapped before call
- old commands event count 0/tree digest unchanged

**Smallest implementation action**

Complete legacy adapter wiring、build isolated old/final artifacts、add startup `sitecustomize` proxy/audit hook、add command matrix and native controls。If an old command reaches mutation event, change final record/marker admission boundary within current design; do not add bridge。

**Focused verification commands**

Until S60 policy removal:

```bash
uv build --sdist --wheel --out-dir spec-dock/.workbench/iss-00392/final-artifacts
uv run pytest --run-full-regression --full-regression-shard -q \
  tests/integration/test_provider_lifecycle_artifacts.py \
  tests/integration/test_provider_lifecycle_tripwire.py
# On macOS:
uv run pytest --run-full-regression --full-regression-shard -q \
  tests/platform/macos/test_provider_lifecycle_macos.py
```

**Expected observable result**

Exact migration/uninstall matrix GREEN。Every old command reports refusal、tripwire events `[]`、target digest identical。Positive controls each produce exactly one pre-call event and no target mutation。

**Evidence to record**

Baseline/final wheel hashes、workspace fixture digest、migration matrix、old command argv/exit/stdout/stderr sanitized、tripwire event logs、native symbol/platform、positive control result、pre/post tree digest。

**Stop conditions and escalation owner**

Old command event > 0、positive control not intercepted、baseline fixture mismatch、active recovery converted、unsupported platform fallback。Immediate stop; owner: Product owner + filesystem safety reviewer。Public PR is not mergeable。

**Cleanup**

Delete isolated venv、temporary workspaces、native probes。Retain only hash/evidence references in report。

**Internal checkpoint invariant (PR-B; no main merge)**

PR-B branch上でS40 public routeとS50 exact `0.2.3` migration/downgrade proofがGREENである。Old engineはunreachableだがS60でのphysical removal、active failure terminalization、unskipped canonical proofが未完了であるため、このcommitをmainへmergeしない。許可される次の遷移は同じbranch/PR上のI392-S60だけである。

**Trace IDs**

I392-RQ-014〜015、I392-RQ-020、I392-D-006、I392-D-014、I392-D-017。

## I392-S60 — Old engine removal, test portfolio ownership, active failure terminalization

**Objective and contract-visible outcome**

Successor proofをauthorityに、old per-file/journal/purge engineとduplicate testsを削除する。Post-#387 active failuresを全件terminal化し、canonical pytestにapproved failure/policy skipを残さない。S40〜S60を同一branch/PRで完了し、PR-Bをcomplete final lifecycleとしてhuman merge可能にする。

**Exact owned paths and symbols**

Delete:

```text
src/spec_dock/managed_distribution.py
src/spec_dock/assets/managed_distribution.json
tests/unit/infra/test_managed_distribution.py
tests/unit/infra/test_init_update.py
tests/cli_runtime/test_distribution_cutover.py
tests/integration/test_epic_00343_distribution.py
full-regression-ledger.json
tests/conftest.py
```

Add/update:

```text
src/spec_dock/context_pack.py
src/spec_dock/cli.py
tests/unit/infra/test_provider_assets.py
tests/provider_test_ownership.json
pyproject.toml
tests/**  # exact active failure owner files only
```

Move `render_context_pack()` behavior if still required。Remove `fast`/`full_regression` markers from tests and marker declarations from pyproject。

**Explicit non-owned / no-touch paths**

Current product behavior unrelated to accepted retirement、Issue #372、consumer history、provider workflow（S70）、timing/sharder files（S70）、human settings。

**Prerequisites and dependency**

同一PR-B branch上でI392-S40とI392-S50の全proofがGREENで、いずれもmainへ未mergeである。No old public callsite。S60のremoval/terminalization/canonical proofを同じPRで完了する。

**RED evidence**

- `git grep` detects forbidden old imports/symbols/files
- ownership map rejects duplicate/missing node
- canonical collection rejects policy skip reason
- each active ledger entry has failing current test or retirement proof before fix
- context pack extraction preserves current surviving behavior
- non-lifecycle asset assertions survive move from `test_init_update.py`

**Smallest implementation action**

1. Extract surviving non-lifecycle context behavior。
2. Move retained asset assertions。
3. For each post-#387 active ledger row, apply mechanical disposition:
   - current accepted behavior exists -> fix source/test until pass
   - exact successor node covers same requirement -> map and delete old node
   - #387/accepted hard-cutover retires behavior -> delete node and record requirement retirement
   - anything else -> stop; never approve failure
4. Add ownership JSON and verifier unit tests。
5. Delete old engine/manifest/tests/ledger/root policy hook。
6. Remove marker decorators/options/retry assumptions。
7. Run full unskipped canonical suite in one process。

**Focused verification commands**

```bash
test -z "$(git grep -nE 'managed_distribution|execute_explicit_spec_history_purge_distribution|--run-full-regression|--full-regression-shard|POLICY_SKIP_REASON|approved-no-op' -- \
  src tests pyproject.toml README.md ':!spec-dock/initiatives/**' ':!*.md' || true)"
uv run pytest -q tests/unit/infra/test_provider_assets.py tests/unit/infra/test_provider_gate.py
uv run python scripts/provider_gate.py verify-node-ownership --map tests/provider_test_ownership.json
uv run pytest -q tests --ignore=tests/platform/macos
make lint
```

**Expected observable result**

Old engine/files/imports absent。Canonical one-process run unexpected failure 0、approved failure 0、policy skip reason 0。All active ledger entries have terminal disposition in report。Ownership duplicate 0。

**Evidence to record**

Old file deletion list、symbol grep、active failure disposition table（old node、status、successor/retirement trace、command）、collection count/digest、skip reason inventory、ownership verifier output、context extraction proof。

**Stop conditions and escalation owner**

Active entry cannot be terminalized、surviving behavior depends on old journal/catalog、security invariant lacks successor、canonical suite fails。Stop; owner: Product owner。Do not restore ledger/skip。

**Cleanup**

Remove obsolete fixtures/helpers/imports/mypy overrides。Delete empty `scripts/quality` only in S70 after sharder removal。Run `git diff --check`。

**PR-B main merge gate invariant**

同一branch/PR上でS40 public route cutover、S50 legacy migration/downgrade proof、S60 old engine removal・active failure terminalization・unskipped canonical proofが全て完了している。Final public lifecycleはold engine fallback、approved failure、policy skipを持たず、current provider workflow下でも全testがGREENである。ここがPR-Bの唯一のmain merge gateであり、human merge後のmainはold public productからcomplete final lifecycleへ直接遷移してreleasableである。

**Trace IDs**

I392-RQ-017、I392-RQ-019、I392-D-001、I392-D-016。

## I392-S70 — Build-once artifact gate, Linux canonical/macOS delta, required-context transition, old CI removal

**Objective and contract-visible outcome**

Provider CIをone build / same wheel / Linux canonical / macOS delta / aggregate gateへ切り替え、main-push 4-shard Full Regression、timing/sharder、duplicate parityを削除する。Human review gateを弱めない。

**Exact owned paths and symbols**

```text
scripts/provider_gate.py
tests/unit/infra/test_provider_gate.py
tests/provider_test_ownership.json
scripts/static_analysis/run.sh
Makefile
.github/workflows/provider-ci.yml
.github/workflows/provider-full-regression.yml      # delete
full-regression-timing-weights.json                 # delete
scripts/quality/full_regression_baseline.py         # delete
scripts/quality/verify_full_regression.py           # delete
scripts/quality/__init__.py                         # delete if directory empty
```

Symbols/subcommandsはI392-D-018。

**Explicit non-owned / no-touch paths**

Root consumer `.github/workflows/ci.yml`、shipped seed `src/spec_dock/assets/install_root/.github/workflows/ci.yml`、commit-identity workflow、unrelated required contexts、review requirement、merge queue unless exact restoration required。

**Prerequisites and dependency**

I392-S60 final unskipped suite GREEN。GitHub settings read permission available for human/admin transition。Current repo rulesets observation at authoring was empty; classic protection must be re-read at transition time。

**RED evidence**

- manifest rejects wrong source SHA/hash/size/build count/output count
- build wrapper test proves one subprocess invocation
- canonical rejects `-n`, more than one pytest child, policy skip/approved failure
- macOS rejects wheel hash mismatch and Linux-owned node intersection
- ownership verifier rejects duplicate
- qualification evaluator rejects wall/CPU/flake/retry
- workflow inspection proves macOS downloads artifact and does not build
- intentional RED canary blocks merge before old context removal

**Smallest implementation action**

1. Implement `scripts/provider_gate.py` and unit tests。
2. Add Makefile targets、static-analysis coverage。
3. Rewrite provider CI。
4. Run new jobs while old required contexts remain。
5. Human captures protection state。
6. Human executes new gate intentional RED/GREEN and required transition。
7. Delete old full-regression workflow、timing、sharder scripts。
8. Verify no main-push provider regression/rebuild remains。

**Focused verification commands**

```bash
uv run pytest -q tests/unit/infra/test_provider_gate.py
uv run python scripts/provider_gate.py build \
  --source-sha "$(git rev-parse HEAD)" \
  --out spec-dock/.workbench/provider-gate/candidate
uv run python scripts/provider_gate.py verify-artifact \
  --manifest spec-dock/.workbench/provider-gate/candidate/manifest.json \
  --source-sha "$(git rev-parse HEAD)"
uv run python scripts/provider_gate.py verify-node-ownership \
  --map tests/provider_test_ownership.json
uv run python scripts/provider_gate.py canonical \
  --manifest spec-dock/.workbench/provider-gate/candidate/manifest.json
# macOS runner:
uv run python scripts/provider_gate.py macos-delta \
  --manifest spec-dock/.workbench/provider-gate/candidate/manifest.json
make lint
git grep -nE 'verify_full_regression|full-regression-ledger|full-regression-timing|--shards 4|--run-full-regression|full_regression' \
  -- . ':!spec-dock/initiatives/**' || true
```

**Expected observable result**

Build invocation count 1、one wheel/one sdist。Linux/macOS wheel hash identical。Canonical one process/worker 1。Lane intersection 0。New aggregate gate GREEN and intentional RED blocking verified。Old files/triggers absent。

**Evidence to record**

Candidate manifest、workflow run IDs/jobs、Linux/macOS environment、node inventories/digests/intersection、build invocation log、same wheel hash、sdist smoke、required contexts before/after、intentional RED proof、human operator、removed files。

**Stop conditions and escalation owner**

Settings unreadable、new context not emitted、RED does not block、unrelated gate changes、macOS rebuild、hash mismatch、canonical uses multiple pytest processes、old main-push trigger remains。Stop。Owner: human repository admin + Product owner。

**Cleanup**

Remove canary fault、restore green branch、delete temporary CI artifact after retention need、remove old required contexts only after new required state confirmed。

**Merge-point invariant**

New provider gate is required and GREEN。Human review requirement unchanged。Main push does not run old Full Regression。Main remains releasable。

**Trace IDs**

I392-RQ-019〜020、I392-D-016、I392-D-018。

## I392-S80 — Qualification tooling, final dogfood, package/fresh consumer, exact PR handoff

**Objective and contract-visible outcome**

Same final candidateでfive-run/CPU、seeded faults、rolling 20を実行し、provider/dogfood/public docsをfinal contractへ収束させる。Final PR headのexact artifact/tree/context handoffを作る。Pure verification-only stepにせず、qualification command、final drift guard、dogfood record/slot markers、docsを完成させる。

**Exact owned paths and symbols**

```text
scripts/provider_gate.py                         # qualify/summarize finalization
tests/unit/infra/test_provider_gate.py
README.md
src/spec_dock/assets/spec_dock/docs/authoring/overview.md
spec-dock/docs/authoring/overview.md
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/uninstall.py
spec-dock/scripts/spec_dock_runtime/commands/uninstall.py
spec-dock/{docs,templates,system,scripts}         # dogfood sync output
.agents/skills/spec-dock
.agents/skills/spec-dock-grill-with-docs
spec-dock/spec-dock.version                      # final JSON record
.agents/skills/*/.spec-dock-provider-slot.json   # exact two slots
tests/provider_test_ownership.json
#392 report.md
```

Dogfood seed files remain no-touch。

**Explicit non-owned / no-touch paths**

All consumer history/artifacts/workbench、dogfood seed bytes、unrelated skills、required settings except human-read verification、canonical R/D/P、release publication。

**Prerequisites and dependency**

I392-S70 new gate GREEN/required。Final PR head candidate can be fixed。

**RED evidence**

- qualification evaluator fails injected over-budget/CPU/flake/retry sample
- seeded fault inventory fails if any point not detected
- provider/dogfood root diff guard fails before sync
- dogfood seed digest guard fails on mutation
- fresh consumer validation fails before artifact install
- exact tree handoff fails if working tree/PR head changes after evidence

**Smallest implementation action**

1. Finalize `qualify`/`summarize` output schemas。
2. Run fault pack and ensure all fault IDs owned。
3. Update public docs/help。
4. Use final built wheel/service to update dogfood roots/slots/record。
5. Verify seed pre/post digests。
6. Run SpecDock sync/validate。
7. Create fresh consumer from same wheel and validate。
8. Run 20 sequential canonical qualification、evaluate first 5 budget/all 20 flake。
9. Freeze final PR head SHA、artifact hashes、tree status、required contexts and report handoff。
10. Remove all temporary generated files from tracked tree。

**Focused verification commands**

```bash
uv run pytest -q tests/unit/infra/test_provider_lifecycle_faults.py
uv run python scripts/provider_gate.py qualify \
  --manifest spec-dock/.workbench/provider-gate/candidate/manifest.json \
  --runs 20 \
  --budget-runs 5 \
  --wall-limit-seconds 600 \
  --cpu-wall-ratio-limit 1.1
uv run python scripts/provider_gate.py summarize \
  --manifest spec-dock/.workbench/provider-gate/candidate/manifest.json \
  --output spec-dock/.workbench/provider-gate/final-summary.json
make lint
uv run python scripts/provider_gate.py canonical \
  --manifest spec-dock/.workbench/provider-gate/candidate/manifest.json
# macOS:
uv run python scripts/provider_gate.py macos-delta \
  --manifest spec-dock/.workbench/provider-gate/candidate/manifest.json
python3 ./spec-dock/scripts/spec-dock sync
python3 ./spec-dock/scripts/spec-dock validate
git diff --check
test -z "$(git status --short)"
```

Fresh consumer smoke uses manifest-selected wheel:

```bash
tmp="$(mktemp -d)"
python3 -m venv "$tmp/venv"
"$tmp/venv/bin/python" -m pip install --no-deps "<verified-wheel>"
"$tmp/venv/bin/spec-dock" init "$tmp/consumer"
python3 "$tmp/consumer/spec-dock/scripts/spec-dock" validate
rm -rf "$tmp"
```

**Expected observable result**

- seeded fault detection 100%
- first 5 canonical runs each <=600s、CPU/wall <=1.1
- all 20 runs unexpected failure 0、flake 0、retry 0
- provider/dogfood roots and exact two slots match candidate
- dogfood record ready/version 0.2.4/digest matching
- seed digests unchanged
- fresh consumer valid
- final tree clean
- exact PR head SHA equals all evidence source SHA

**Evidence to record**

Qualification JSON、run-by-run wall/CPU/outcome、fault inventory/detection、provider/dogfood tree digests、seed before/after hashes、SpecDock commands、fresh consumer result、final manifest、required context state、PR URL/head SHA、reviewer/human merge instructions。

**Stop conditions and escalation owner**

Any budget/fault/flake failure、seed mutation、dogfood drift、validate failure、artifact/tree SHA mismatch、required gate weakening。Stop and forward-fix same Issue。Owner: Product owner; required setting issueはhuman repository admin。

**Cleanup**

Delete virtualenv、fresh consumer、old stages、canary、local artifacts not needed for review。Tracked treeにはproduction/tests/docs/reportだけを残す。

**Merge-point invariant**

Final PR head is releasable、all acceptance evidence is bound to same head/artifacts、new gate GREEN/required、human review required。Agentはmergeしない。

**Trace IDs**

I392-RQ-002〜003、I392-RQ-015、I392-RQ-019〜020、I392-D-016〜018。

## 4. Completion and human handoff

### PR-B internal checkpoints and main merge handoff

I392-S40とI392-S50の完了はbranch内evidence checkpointであり、merge-ready state、main merge point、human merge handoffを生成しない。PR-Bのhuman merge handoffはI392-S60のPR-B main merge gate invariantが成立した後だけ作成する。S40後またはS50後のSHAがmerge対象になった場合はhandoffを撤回し、同じbranch/PRでS60まで完了する。

### Implementation completion

I392-S00〜S80のexpected result、evidence、cleanup、merge invariantが全て成立し、final PR headが固定された時点。

### Human merge handoff

Reportに次を一つのtableで提示する。

- final PR URL
- exact head SHA
- wheel/sdist/candidate digests
- required contexts before/after
- all job run URLs/IDs
- human review status
- merge method restriction
- post-merge exact SHA comparison command
- forward-fix/revert note

### Post-merge

Human merge後:

```bash
git fetch origin main
git rev-parse origin/main
git diff --exit-code "<verified-pr-head>^{tree}" "origin/main^{tree}"
python3 ./spec-dock/scripts/spec-dock validate
```

Tree mismatch、merge commitにunexpected content、gate state変化があればIssue finishしない。

### Issue finish and Epic close

- merged tree equality確認
- #392 report complete
- #392をSpecDock lifecycleでfinish
- GitHub #392 close state確認
- Epic #384 acceptance再確認
- Epic close
- #388〜#390はsuperseded historicalのまま
