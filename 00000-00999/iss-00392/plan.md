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
repository_evidence:
  repository: "chemitaro/spec-dock"
  branch: "codex/epic-00384-provider-test-strategy-planning"
  sha: "ef183ae46febe52f0152431cb3a8b4846c9972fc"
---

# iss-00392 Provider Lifecycle And Regression Gate Hard Cutover — 実装計画

Normative artifacts: `artifacts/provider-lifecycle-wire-contract.md` and `artifacts/active-failure-disposition-register.md` (Issue documents use `../../artifacts/...`). Their exact wire/disposition data is not delegated to implementation.


## 1. Execution rules

1. 本書がentry point。BehaviorはIssue Requirement、components/state/filesystemはIssue Designを参照する。
2. Product source of truthは`src/spec_dock/`。Provider-firstで変更しdogfoodを後から同期する。
3. Behavior changeはtest-first。Existing failing nodeをRED authorityにする場合はexact node/reasonをtracked reportへ記録する。
4.各stepはimplementationとfocused verificationを含むvertical milestone。
5. S40/S50はPR-B internal checkpoint、S60だけPR-B main gate。
6. S70はPR-C internal checkpoint、S80だけPR-C main gate。
7. S60は`.github/workflows/provider-ci.yml`と`tests/unit/test_provider_test_lanes.py`をowned pathとし、deleted test pathsをexisting successorsへretargetし、S70-only toolingなしでcurrent PR/main-push gatesを別々にGREENにする。
8. S70はreplacement gate/environment/workflow/AGENTS/final testsを追加し、`tests/unit/test_provider_test_lanes.py`、`tests/unit/test_full_regression_baseline.py`を含むall remaining policy consumersをretire/replaceしてからproviders/old machineryを同じbranchで削除する。
9. Tracked reportはpre-merge factsのみ。Final source-bound/post-merge factsはexternal attestation。
10. Agentはmerge/required settings/Issue closeを実行しない。
11. Stop条件は同じ#392でforward-fix。New Issue、bridge、toggle、skip、ledger approval、old fallbackは禁止。

## 2. Common no-touch boundary

- `spec-dock/initiatives/**` user/Historical content（#392 tracked report/generated lifecycle metadataを除く）
- Issue #372 canonical/evidence
- consumer seeds `spec-dock/.gitignore`、root `.github/workflows/ci.yml`
- unrelated skills
- consumer `.workbench/**`
- human review/unrelated required settings
- release/tag/PyPI
- canonical R/D/P during implementation

## 3. Step and merge graph

```text
S00 admission
  -> PR-A: S10 internal -> S20 internal -> S30 only merge gate
  -> PR-B: S40 internal -> S50 internal -> S60 only merge gate
  -> PR-C: S70 internal -> S80 only merge gate
  -> human merge -> external closure attestations
```

## I392-S00 — Deterministic specification/#387 admission and baseline

**Objective and contract-visible outcome**

Specification lineageと#387 implementation driftを別々に証明し、implementation base、old `0.2.3` artifacts、current gate/failure inventoryを固定する。Stale repository evidence SHAからfuture mainへself-rejecting diffを行わない。

**Exact owned repository paths and symbols**

- Read-only repository/GitHub。
- Tracked write: #392 `report.md`のpre-merge admission summaryのみ。
- Ignored: `spec-dock/.workbench/iss-00392/admission/**`。
- No production symbol change。

**Explicit non-owned and no-touch paths**

All production/tests/workflows/settings。#387 diffを修正しない。

**Prerequisites and dependency**

- 本pack imported。
- Owner records replacement manifest hash/location and`SPEC_FREEZE_COMMIT`。
- #387 closed/human merged。
- Implementation base containsboth lineages。
- Clean worktree。

**RED evidence or justified no-new-test rule**

No product test。Temporary read-only checker mustrejectsynthetic wrong spec hash、wrong #387 path、protected drift。Checker isnotcommitted unlessgeneric code islaterowned byprovider gate。

**Smallest implementation action**

1. Verifymanifest exact payload hashes against`SPEC_FREEZE_COMMIT` blobs。
2. Verifycommit ancestry。
3. Obtain#387 PR base/head/merge andvalidateits own delta/content restrictions。
4. Verifyprotected paths fromspec freeze toimplementation base, accounting onlyvalidated #387 delta。
5. Capturecurrent lint/ordinary/full/dogfood gates。
6. Buildbaseline `0.2.3` wheel+sdist once andhash。
7. Generatelegacy root/slot digests andtest/failure inventory。

**Normative register admission**

Before anyS10 file iscreated, parse`../../artifacts/active-failure-disposition-register.md` betweenexact JSON markers andperformtwo comparisons:

1. `git show "$REPOSITORY_EVIDENCE_SHA:full-regression-ledger.json"` equalsall27 register node/signature pairs andsource blob identity。
2. post-#387 working tree ledger equalsregister `expected_post_387`: 15 rows、active14、resolved1、exact removals4〜15、nootherfield/signature/new row delta。

Expected #387 successor node IDs listed inthe register mustcollect。Any mismatch stopsIssue start/S10, requirescanonical register update byspec owner, andrequiresfresh Strict re-review。Luna doesnotselectan equivalent node。

**Focused verification commands**

```bash
test -z "$(git status --short)"
git merge-base --is-ancestor "$SPEC_FREEZE_COMMIT" "$IMPLEMENTATION_BASE_SHA"
git show "$SPEC_FREEZE_COMMIT:<canonical-path>" | sha256sum
git diff --name-status "$ISSUE_387_MERGE^1" "$ISSUE_387_MERGE"
python3 spec-dock/.workbench/iss-00392/admission/verify_failure_register.py \
  --register spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00384-provider-test-strategy-simplification-and-execution-cost-reduction/artifacts/active-failure-disposition-register.md \
  --source-ledger <(git show "$REPOSITORY_EVIDENCE_SHA:full-regression-ledger.json") \
  --post-387-ledger full-regression-ledger.json
make lint
uv run pytest -q
uv run python -m scripts.quality.verify_full_regression --shards 4
uv build --sdist --wheel --out-dir spec-dock/.workbench/iss-00392/admission/dist
python3 ./spec-dock/scripts/spec-dock validate
git diff --check
test -z "$(git status --short)"
```

**Expected observable result**

Spec hashes/ancestry/#387 delta/protected drift exact、current gates GREEN、exact one 0.2.3 wheel andsdist、legacy fixture inputs fixed。

**Evidence to record in Issue report.md**

Repository evidence SHA、manifest hash/location、SPEC_FREEZE_COMMIT、path blob OIDs/content hashes、#387 base/head/merge/tree/delta、implementation base、commands、baseline artifacts、node/failure inventory。No final PR head/self hash。

**Stop conditions and escalation owner**

Missing identity/hash mismatch/#387 mismatch/protected drift/baseline failure。Owner: Product/repository owner。Do notwiden allowlist。

**Cleanup**

Detached worktree、venv、temporary checker。Keepignored baseline artifacts throughS50。

**Merge-point invariant**

No code diff。Not a merge point。

**Requirement and design trace IDs**

I392-RQ-001、I392-D-014。

## I392-S10 — Fixed model, strict record/seed policy, candidate, legacy fixture

**Objective and contract-visible outcome**

Dormant fixed paths、strict seven-key record、immutable seed policy、candidate digest、legacy fixture/classifierをdirect testsで完成する。

**Exact owned repository paths and symbols**

```text
src/spec_dock/provider_lifecycle/__init__.py
src/spec_dock/provider_lifecycle/model.py
src/spec_dock/provider_lifecycle/candidate.py
src/spec_dock/provider_lifecycle/legacy_023.py
src/spec_dock/assets/legacy_0_2_3.json
tests/unit/infra/test_provider_lifecycle_model.py
tests/unit/infra/test_provider_lifecycle_candidate.py
tests/unit/infra/test_provider_lifecycle_wire_contract.py
tests/unit/infra/test_provider_assets.py
```

Symbols: Issue Design model/candidate/legacy symbols、`SeedPolicy`、`ResumeIdentity`。

**Explicit non-owned and no-touch paths**

Public CLI、old engine/manifest、workflows、dogfood。

**Prerequisites and dependency**

S00 GREEN。

**RED evidence**

Exact constants/order、`provider-lifecycle-wire-contract.md` seven-key record andoperation/status/action/code enums、record relations/duplicate/size/type、seed policy matrix、resume tuple mismatch、candidate unsafe rejection/determinism、legacy exact/modified/recovery、invalid JSON nolegacy fallback。

**Smallest implementation action**

Pure dataclasses/enums/parsers/digest/legacy observation。No mutation function。

**Focused verification commands**

```bash
uv run pytest -q tests/unit/infra/test_provider_lifecycle_model.py \
  tests/unit/infra/test_provider_lifecycle_candidate.py \
  tests/unit/infra/test_provider_lifecycle_wire_contract.py \
  tests/unit/infra/test_provider_assets.py
uv run ruff check src/spec_dock/provider_lifecycle tests/unit/infra/test_provider_lifecycle_model.py
uv run mypy src/spec_dock/provider_lifecycle
```

**Expected observable result**

All direct tests GREEN、no public behavior change、fixture matchesS00 baseline。

**Evidence to record in Issue report.md**

RED/GREEN nodes、record samples each state/policy、candidate/legacy hashes。

**Stop conditions and escalation owner**

Need arbitrary path/history/progress field orambiguous policy。Owner: Product owner。

**Cleanup**

Generated fixture intermediates andtest temp。

**Merge-point invariant**

Internal PR-A checkpoint only。Old public product remains。No merge handoff。

**Requirement and design trace IDs**

I392-RQ-002〜007、I392-RQ-016、I392-D-001〜004。

## I392-S20 — Descriptor-bound filesystem, shared-container bootstrap, fresh install

**Objective and contract-visible outcome**

Fresh absent/existing shared containerでsafe bootstrap、stage、incomplete record、4 roots/2 slots/seeds/readyをdirect serviceで完成する。

**Exact owned repository paths and symbols**

```text
src/spec_dock/provider_lifecycle/filesystem.py
src/spec_dock/provider_lifecycle/service.py
tests/unit/infra/test_provider_lifecycle_filesystem.py
tests/unit/infra/test_provider_lifecycle_service.py
tests/unit/infra/test_provider_lifecycle_faults.py
```

Symbols: bindings、stage owner、`bootstrap_spec_dock_container`、cleanup、native rename、fresh install/fault hook。

**Explicit non-owned and no-touch paths**

Public CLI、old engine/workflow、dogfood tracked tree。

**Prerequisites and dependency**

S10 GREEN、native symbol probes available。

**RED evidence**

Absent container create/bind/order、existing real + unknown child preserve、symlink/non-dir block、absence race、failure aftermkdir/beforeowner/beforerecord、empty cleanup、cleanup-failure partial/resume、stage policy/identity strict、fresh create policy、preserve-only no seeds、all root/slot/seed/ready faults、no-follow/hard-link/native fail-closed。

**Smallest implementation action**

Root lock/binding、external stage owner、container bootstrap/cleanup、native rename、atomic record、fresh install service only。

**Focused verification commands**

```bash
uv run pytest -q tests/unit/infra/test_provider_lifecycle_filesystem.py \
  tests/unit/infra/test_provider_lifecycle_service.py \
  tests/unit/infra/test_provider_lifecycle_faults.py \
  -k 'fresh or container or bootstrap or seed_policy or binding or publish'
make lint
```

**Expected observable result**

Fresh service direct API GREEN。Unknown user children preserved。Seed policy/failure/resume exact。

**Evidence to record in Issue report.md**

Mutation timeline、container identity/cleanup table、policy/fault matrix、protected digests、native availability。

**Stop conditions and escalation owner**

Generic mkdir/rename fallback、recursive container delete、unrecorded policy inference。Owner: Product + filesystem safety reviewer。

**Cleanup**

Owned stages/temp workspaces。No consumer residue。

**Merge-point invariant**

Internal PR-A checkpoint only。No main merge handoff。

**Requirement and design trace IDs**

I392-RQ-002〜012、I392-D-005〜010。

## I392-S30 — Update/resume convergence and PR-A merge gate

**Objective and contract-visible outcome**

Ready/incomplete update、missing repair、same tuple convergence、cross tuple blockを完成し、dormant successor PR-Aをmerge-readyにする。

**Exact owned repository paths and symbols**

S10/S20 modules/tests。`update_tooling`、`resume_incomplete`、policy transition validation。

**Explicit non-owned and no-touch paths**

CLI、old engine/workflows/policy。

**Prerequisites and dependency**

S20 GREEN。

**RED evidence**

Whole-root replace、missing repair、marker mismatch、same operation/candidate/policy resume、policy tamper/mismatch、fresh ready thenupdate preserve-only、cleanup warning、race fail closed。

**Smallest implementation action**

Update/resume orchestration usingexisting primitives。No checkpoint list/rollback。

**Focused verification commands**

```bash
uv run pytest -q tests/unit/infra/test_provider_lifecycle_*.py
make lint
uv run pytest -q
uv run python -m scripts.quality.verify_full_regression --shards 4
```

**Expected observable result**

Dormant install/update complete、all current gates GREEN、public CLI unchanged。

**Evidence to record in Issue report.md**

Fault/convergence table、policy transitions、current gate output。

**Stop conditions and escalation owner**

Need public toggle/old fallback/persistent progress。Owner: Product owner。

**Cleanup**

Temp stages/fault artifacts。

**Merge-point invariant**

Only PR-A main merge gate。Afterhuman merge, main exposesold public product + dormant successor andcurrent workflow remainsreleasable。

**Requirement and design trace IDs**

I392-RQ-010〜015、I392-D-007〜010。

## I392-S40 — Tooling-only uninstall, public wire, and lifecycle documentation cutover

**Objective and contract-visible outcome**

PR-B branchでuninstall/reinstall、version`0.2.4`、new CLI wiring、purge trap、normative wire、final lifecycle documentationを一体で接続する。S40 isinternal checkpoint; no main merge。

**Exact owned repository paths and symbols**

```text
pyproject.toml
src/spec_dock/cli.py
src/spec_dock/provider_lifecycle/model.py
src/spec_dock/provider_lifecycle/service.py
src/spec_dock/provider_lifecycle/public_result.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/uninstall.py
spec-dock/scripts/spec_dock_runtime/commands/uninstall.py
README.md                                              # lifecycle sections only
src/spec_dock/assets/spec_dock/docs/migration.md
spec-dock/docs/migration.md
src/spec_dock/assets/spec_dock/docs/README.md           # lifecycle sections only
spec-dock/docs/README.md                                # lifecycle sections only
tests/unit/infra/test_provider_lifecycle_wire_contract.py
tests/unit/infra/test_provider_lifecycle_public_result.py
tests/cli_runtime/test_provider_lifecycle.py
tests/cli_runtime/test_uninstall.py
tests/cli_runtime/test_update.py
```

Normative source: `../../artifacts/provider-lifecycle-wire-contract.md`。Provider docs source iseditedbeforedogfood projection。Root README anddocs README test-policy paragraphs remaincurrent andareownedlater byS70。

**Explicit non-owned and no-touch paths**

Old engine file retained untilS60、current pytest policy/workflows、root`AGENTS.md`、README test-policy paragraphs、user data/seeds、Historical docs。

**Prerequisites and dependency**

S30 GREEN。S40 startsPR-B samebranch/PR; S40/S50 cannot beoffered formerge。Wire artifact hash isverified throughSPEC_FREEZE_COMMIT。

**RED evidence**

- Wire tests fail againstmissing`migrate-0.2.3` operation、exactcode/action/nullability/golden mappings。
- Uninstall apply/default/aliases/trap tests fail againstold purge/journal behavior。
- One-time docs grep findslegacy journal/retry/purge/compatible-newer/empty-boundary text inroot/provider/dogfood docs。
- Provider/dogfood migration/docs README `cmp` fails untilprojection isupdated。

**Smallest implementation action**

1. Implementuninstall/result andexact wire enums/serializers。
2. WireCLI exclusively tosuccessor;version bump;remove purge public callsites。
3. Update runtime wrapper pair。
4. Rewrite root README lifecycle sections andprovider migration/docs README lifecycle sections tostrict record、same `(operation,candidate_digest,seed_policy)` resume、tooling-only uninstall、preserve-only update/reinstall/migration、`--remove-specs` mutation-zero/exit2。
5. Copy/sync provider docs toexact dogfood projections。
6. Do notchangeFull Regression/test-policy guidance untilS70。

**Focused verification commands**

```bash
uv run pytest -q \
  tests/unit/infra/test_provider_lifecycle_wire_contract.py \
  tests/unit/infra/test_provider_lifecycle_public_result.py
uv run pytest --run-full-regression --full-regression-shard -q \
  tests/cli_runtime/test_provider_lifecycle.py \
  tests/cli_runtime/test_uninstall.py \
  tests/cli_runtime/test_update.py
cmp src/spec_dock/assets/spec_dock/docs/migration.md spec-dock/docs/migration.md
cmp src/spec_dock/assets/spec_dock/docs/README.md spec-dock/docs/README.md
test -z "$(git grep -nE 'distribution-(journal|retry)|uninstall-retry|current explicit spec-history purge authority|--apply([^`]|`[^`]*`)*--remove-specs|compatible newer package|protocol 2 journal|空の `spec-dock/`|empty spec-dock boundary' -- README.md src/spec_dock/assets/spec_dock/docs spec-dock/docs || true)"
make lint
git diff --check
```

**Expected observable result**

Public final routes andwire goldens GREEN。Lifecycle docs describeonlyfinal`0.2.4` behavior andprovider/dogfood pairs arebyte-equal。Current test-policy text remainsintentionally present。

**Evidence to record in Issue report.md**

Wire test/golden IDs、CLI matrix、text/JSON/exit、docs changed paths、provider/projection hashes、retired lifecycle grep output、protected seed/data digests。

**Stop conditions and escalation owner**

Wire field/enum choice notdefined byartifact、bridge/toggle needed、purge mutation retained、docs requireaProduct decision、provider/dogfood mismatch、orS40 merge handoff。Owner: Product/spec owner + implementation owner。

**Cleanup**

Temporary snapshots; no generated docs beyondexact projection pair。

**Internal checkpoint invariant**

S40 isnot a main merge point。Same PR-B branch continuesS50/S60。No S40-only handoff。

**Requirement and design trace IDs**

I392-RQ-013〜019、I392-RQ-027〜028、I392-D-016〜017。

## I392-S50 — Legacy migration and old-package composite tripwire

**Objective and contract-visible outcome**

Exact `0.2.3` migration/uninstall、policy-preserving fault resume、old-package mutation-zeroをbuilt artifactsで証明する。PR-B internal checkpoint only。

**Exact owned repository paths and symbols**

```text
src/spec_dock/provider_lifecycle/legacy_023.py
src/spec_dock/provider_lifecycle/service.py
tests/integration/test_provider_lifecycle_artifacts.py
tests/integration/test_provider_lifecycle_tripwire.py
tests/platform/macos/test_provider_lifecycle_macos.py
tests/support/provider_lifecycle_tripwire/sitecustomize.py
tests/support/provider_lifecycle_tripwire/native_positive_control.py
```

**Explicit non-owned and no-touch paths**

Old engine deletion S60、current policy/workflows、baseline bytes、consumer data/seeds。

**Prerequisites and dependency**

S40 branch checkpoint GREEN。S00 baseline available。No main merge。

**RED evidence**

Exact/modified root/slot/recovery matrix、migration policy preserve-only、fault exact tuple resume、tripwire sentinel、Python/native controls、old command event0/tree unchanged。

**Smallest implementation action**

Complete legacy wiring andtripwire harness。Mutation attempt -> adjustfinal record/marker boundary;no bridge。

**Focused verification commands**

```bash
uv build --sdist --wheel --out-dir spec-dock/.workbench/iss-00392/final-artifacts
uv run pytest --run-full-regression --full-regression-shard -q \
  tests/integration/test_provider_lifecycle_artifacts.py \
  tests/integration/test_provider_lifecycle_tripwire.py
# macOS
uv run pytest --run-full-regression --full-regression-shard -q \
  tests/platform/macos/test_provider_lifecycle_macos.py
```

**Expected observable result**

Migration/uninstall GREEN、policy preserve-only、old events empty、controls captured、tree unchanged。

**Evidence to record in Issue report.md**

Artifact hashes、migration/fault policy matrix、tripwire/native logs。

**Stop conditions and escalation owner**

Old mutation/control failure/policy change/unsupported fallback/S50 merge handoff。Owner: Product + safety reviewer。

**Cleanup**

Venv/workspaces/probes。

**Internal checkpoint invariant**

S50 isnot a main merge point。Same branch continuesS60。No S50-only handoff。

**Requirement and design trace IDs**

I392-RQ-016〜017。

## I392-S60 — Old engine/test terminalization, docs convergence, transitional workflow repair, and PR-B main gate

**Objective and contract-visible outcome**

Removeold per-file/journal/purge engine andduplicate tests、applytheexact failure register、finishPR-B docs、andkeepbothcurrentprovider workflows independentlyGREEN。Transitional `provider-ci.yml` isretargetedtoexisting successors withoutadvancingS70 final redesign。NoS70-only tool isused。

**Exact owned repository paths and symbols**

Delete:

```text
src/spec_dock/managed_distribution.py
src/spec_dock/assets/managed_distribution.json
tests/unit/infra/test_managed_distribution.py
tests/unit/infra/test_init_update.py
tests/cli_runtime/test_distribution_cutover.py
tests/integration/test_epic_00343_distribution.py
```

Create/update:

```text
src/spec_dock/context_pack.py
src/spec_dock/cli.py
README.md                                              # final lifecycle, current test-policy retained
src/spec_dock/assets/spec_dock/docs/migration.md
spec-dock/docs/migration.md
src/spec_dock/assets/spec_dock/docs/README.md           # final lifecycle, current test-policy retained
spec-dock/docs/README.md
tests/unit/infra/test_provider_assets.py
tests/unit/infra/test_provider_lifecycle_wire_contract.py
tests/unit/infra/test_provider_test_ownership.py
tests/provider_test_ownership.json
tests/unit/test_provider_test_lanes.py
.github/workflows/provider-ci.yml
full-regression-ledger.json
full-regression-timing-weights.json
tests/conftest.py
tests/** exact fixed-in-place/successor nodes named in active-failure-disposition-register.md
pyproject.toml only deleted-file mypy references
```

Must remainpresent/functionally current throughPR-B:

```text
tests/unit/test_full_regression_baseline.py
tests/conftest.py
scripts/quality/full_regression_baseline.py
scripts/quality/verify_full_regression.py
scripts/quality/__init__.py
full-regression-ledger.json
full-regression-timing-weights.json
.github/workflows/provider-full-regression.yml
pytest fast/full options/markers
root AGENTS.md current test-policy text
```

**Transitional `.github/workflows/provider-ci.yml` exact repair**

Preserveworkflow name`Provider CI`、`pull_request` event、job IDs、Ubuntu/macOS matrix、checkout/head check、Python/uv install、static-analysis topology。Replaceonlydeleted test commands:

```text
old: tests/unit/infra/test_managed_distribution.py
new: tests/unit/infra/test_provider_lifecycle_model.py
     tests/unit/infra/test_provider_lifecycle_candidate.py
     tests/unit/infra/test_provider_lifecycle_filesystem.py
     tests/unit/infra/test_provider_lifecycle_service.py
     tests/unit/infra/test_provider_lifecycle_public_result.py
     tests/unit/infra/test_provider_lifecycle_wire_contract.py
     tests/unit/infra/test_provider_lifecycle_faults.py
     tests/unit/infra/test_provider_assets.py
     tests/unit/infra/test_provider_test_ownership.py

old: tests/cli_runtime/test_distribution_cutover.py
new: tests/cli_runtime/test_provider_lifecycle.py
     tests/cli_runtime/test_uninstall.py
     tests/cli_runtime/test_update.py

old: tests/integration/test_epic_00343_distribution.py
new: tests/integration/test_provider_lifecycle_artifacts.py
     tests/integration/test_provider_lifecycle_tripwire.py

macOS-only: tests/platform/macos/test_provider_lifecycle_macos.py
```

Currentpermission flags remainwherecurrently required。Do notbuildartifacts、addaggregate job、renamecontexts、remove matrix、orchangeevent; those belongS70。

**Failure register contract**

Normative source`../../artifacts/active-failure-disposition-register.md`。S60 ledger containsonlypost-#387 remaining15 rows。Row2 isresolved/superseded to`tests/unit/infra/test_provider_assets.py::test_fixed_skill_slots_match_provider_and_dogfood`。Rows1、3、16〜27 areresolved/fixed-in-place withsame node normalpass。Rows4〜15 stayabsent。Active0、resolved15、retired0。No disposition choice remains。

`tests/unit/test_provider_test_lanes.py` exact tests:

```text
test_s60_register_source_and_post_387_delta_are_exact
test_s60_full_regression_ledger_has_zero_active_rows_and_exact_resolved_relations
test_s60_terminal_successor_nodes_are_collected_and_normally_pass
test_s60_provider_ci_references_only_existing_successor_tests
test_s60_pytest_adapter_and_standalone_evaluator_are_equivalent
```

**Explicit non-owned and no-touch paths**

Final provider-gate redesign、Linux environment files、rootAGENTS/test-policy update、policy provider deletion、human settings、consumer data/seeds、release。

**Prerequisites and dependency**

S50 allproof GREEN。All exact successor nodescollectbeforeold deletion。S40 lifecycle docs/wire areGREEN。NoS40/S50 separate merge。

**RED evidence**

- Old workflow commands fail afterold test paths aredeleted butbeforeretarget。
- Lane tests fail withactive rows、wrongregister delta、stale successors/workflow paths。
- Full verifier fails onanydeleted node reference。
- Lifecycle docs grep fails onanyold journal/retry/purge text。
- Fixed-in-place nodes failbeforetheirsource/test repair; superseded successors fail/absent beforecreation。

**Smallest implementation action**

1. Extractcontext behavior andmoveprovider asset assertions。
2. Implementallregister fixed-in-place repairs andexact successors;do notreclassify。
3. Deleteold engine/manifest/tests。
4. Updateledger/timing/conftest exact references andall remaining15 rows toterminal relations。
5. Update`test_provider_test_lanes.py` toregister/current-policy contract。
6. Retargettransitional `provider-ci.yml` exactly asabove。
7. Re-runprovider-first docs sync andlifecycle grep。
8. Runordinary, transitional PR workflow commands, andcurrent main-push verifier independently。

**Focused verification commands**

```bash
python3 spec-dock/.workbench/iss-00392/admission/verify_failure_register.py \
  --register spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00384-provider-test-strategy-simplification-and-execution-cost-reduction/artifacts/active-failure-disposition-register.md \
  --post-387-ledger full-regression-ledger.json \
  --expect-s60-terminal
uv run pytest -q \
  tests/unit/infra/test_provider_lifecycle_wire_contract.py \
  tests/unit/infra/test_provider_assets.py \
  tests/unit/infra/test_provider_test_ownership.py \
  tests/unit/test_provider_test_lanes.py \
  tests/unit/test_full_regression_baseline.py
# Run exact transitional Provider CI test commands locally.
uv run pytest -q tests/unit/infra/test_provider_lifecycle_model.py \
  tests/unit/infra/test_provider_lifecycle_candidate.py \
  tests/unit/infra/test_provider_lifecycle_filesystem.py \
  tests/unit/infra/test_provider_lifecycle_service.py \
  tests/unit/infra/test_provider_lifecycle_public_result.py \
  tests/unit/infra/test_provider_lifecycle_wire_contract.py \
  tests/unit/infra/test_provider_lifecycle_faults.py \
  tests/unit/infra/test_provider_assets.py \
  tests/unit/infra/test_provider_test_ownership.py
uv run pytest --run-full-regression --full-regression-shard -q \
  tests/cli_runtime/test_provider_lifecycle.py tests/cli_runtime/test_uninstall.py tests/cli_runtime/test_update.py \
  tests/integration/test_provider_lifecycle_artifacts.py tests/integration/test_provider_lifecycle_tripwire.py
uv run pytest -q
uv run python -m scripts.quality.verify_full_regression --shards 4
cmp src/spec_dock/assets/spec_dock/docs/migration.md spec-dock/docs/migration.md
cmp src/spec_dock/assets/spec_dock/docs/README.md spec-dock/docs/README.md
test -z "$(git grep -nE 'distribution-(journal|retry)|uninstall-retry|current explicit spec-history purge authority|--apply([^`]|`[^`]*`)*--remove-specs|compatible newer package|protocol 2 journal|空の `spec-dock/`|empty spec-dock boundary' -- README.md src/spec_dock/assets/spec_dock/docs spec-dock/docs || true)"
python3 - <<'PY_WORKFLOW_PATHS'
# Parse provider-ci.yml run commands and assert every tests/... argument exists.
# Assert old three paths are absent and final S70 job IDs are not introduced.
PY_WORKFLOW_PATHS
make lint
git diff --check
```

**Expected observable result**

Old engine/tests absent。Wire anddocs final。Register dispositions exact。Active approved failures0。TransitionalPRworkflow referencesonlyexisting successors andisGREEN。Currentmain-push verifier remainsGREEN withallproviders/consumers present。NoS70 tool orfinaljob topology appears。

**Evidence to record in Issue report.md**

Deletion table、27-row register validation、15-row terminal ledger、fixed/successor test outputs、transitionalworkflow diff/run identity、main-push verifier output、docs hashes/grep/cmp、wire goldens。Final head-bound values remainexternal。

**Stop conditions and escalation owner**

Unexpectedregister delta、missing successor、unresolved row、wire/docs mismatch、current workflow failure、deleted consumer、S70-only dependency、orS60 mergebeforeallproof。Owner: Product/spec/test/CI owners。No disposition substitution。

**Cleanup**

Obsoletefixtures/imports/mypy entries only。Keepallcurrent policy infrastructure intentionally forPR-B main。

**PR-B main merge invariant**

S60 is theonly PR-B main merge gate。S40+S50+S60 allGREEN。Afterhuman merge, main hascompletefinal`0.2.4` lifecycle、final lifecycle docs/wire、register-applied active0、noold engine fallback、workingtransitional Provider CI、andworkingcurrent main-push Full Regression。No bridge/toggle/final-gate redesign。

**Requirement and design trace IDs**

I392-RQ-018〜020、I392-RQ-027〜029、I392-D-011、I392-D-016〜018。

## I392-S70 — Consumer-first final provider gate, sole CI producer, test-policy docs, and atomic old policy removal

**Objective and contract-visible outcome**

PR-C branchでfinal Provider CI tooling/environment/workflow/test-policy documentationを先に成立させ、allcurrent policy consumersをretire/replaceした後にold providers/data/workflowを削除する。Local build ispre-freeze tooling smoke only。S70 isinternal; no main merge。

**Exact owned repository paths and symbols**

Create/update:

```text
scripts/provider_gate.py
ci/linux-qualification.Dockerfile
ci/linux-qualification-environment.json
tests/unit/infra/test_provider_gate.py
tests/unit/infra/test_provider_artifact_flow.py
tests/unit/infra/test_provider_test_ownership.py
tests/provider_test_ownership.json
scripts/static_analysis/run.sh
Makefile
.github/workflows/provider-ci.yml
AGENTS.md
README.md                                              # test-policy sections only
src/spec_dock/assets/spec_dock/docs/README.md           # test-policy sections only
spec-dock/docs/README.md                                # synced projection
pyproject.toml
```

Retire/replace before provider deletion:

```text
tests/unit/test_provider_test_lanes.py
tests/unit/test_full_regression_baseline.py
.github/workflows/provider-full-regression.yml          # consumer of old verifier; delete after replacement GREEN
```

Delete only afterconsumer inventory proveszero:

```text
tests/conftest.py
scripts/quality/full_regression_baseline.py
scripts/quality/verify_full_regression.py
scripts/quality/__init__.py if empty
full-regression-ledger.json
full-regression-timing-weights.json
pytest fast/full marker declarations/decorators/options
```

Exact known policy module consumers atrepository evidence:

```text
tests/conftest.py -> scripts.quality.full_regression_baseline + ledger
tests/unit/test_provider_test_lanes.py -> tests.conftest + both quality modules + ledger/timing/workflows
tests/unit/test_full_regression_baseline.py -> scripts.quality.full_regression_baseline
scripts/quality/verify_full_regression.py -> baseline + ledger + timing + pytest legacy options
.github/workflows/provider-full-regression.yml -> scripts.quality.verify_full_regression
.github/workflows/provider-ci.yml -> legacy pytest permission flags
pyproject.toml -> marker declarations
AGENTS.md / README.md / docs README -> retired operator policy text
```

Ifpre-deletion grep findsany path outside thisexact list, stop forcanonical spec owner update + Strict review; Luna doesnotclassifyit。

**Final workflow exact topology**

```text
provider-build-artifacts          # Linux, sole final packaging producer
provider-linux-canonical          # download same artifact, build 0
provider-sdist-smoke              # download same artifact, build 0
provider-macos-delta              # download same artifact, build 0
provider-attestation              # download artifacts/receipts, build 0
provider-gate                     # aggregate only
```

`provider-build-artifacts` acceptsworkflow input`candidate_sha`、checksoutexactSHA、verifiesHEAD/tree、runsone`uv build --wheel --sdist` invocation、writesmanifest、uploads`provider-candidate-<candidate_sha>`。Downstream uses`actions/download-artifact@v4` fromsame run andverifieshashes。Nootherjob invokespackaging。

**Explicit non-owned and no-touch paths**

Lifecycle docs content alreadyfinal atS60 excepttest-policy paragraphs、consumer seed workflows、commit-identity workflow、human settings、release、canonical specs。

**Prerequisites and dependency**

PR-C basesexactlyonS60 main tree。Transitional PR/main workflows areGREEN beforechange。S70 continuesS80 withoutmerge。

**RED evidence**

- Provider gate tests rejectsecond producer、downstream build command、hash/source/tree/upload identity mismatch。
- Workflow tests fail untilallconsumer jobs download same artifact andrecordbuild0。
- `test_provider_test_lanes.py` and`test_full_regression_baseline.py` still importold providers before retirement。
- Pre-provider-deletion grep identifiesexact known consumers; anyunknown path ishardstop。
- Root AGENTS/README/docs README grep findsretired policy text。
- Environment fingerprint/budget evaluator negative cases failclosed。

**Smallest implementation action**

1. Implementprovider gate、artifact-flow tests、environment descriptor/Dockerfile。
2. Rewriteprovider-ci final topology withoneproducer/fourdownload consumers/aggregate。
3. UpdateMakefile/static analysis。
4. UpdateAGENTS andREADME/docs README test-policy sections;syncprojection。
5. Replacefinal behavior assertions from`test_provider_test_lanes.py` in`test_provider_gate.py`/`test_provider_test_ownership.py`/`test_provider_artifact_flow.py`;deleteold lane test。
6. Delete`test_full_regression_baseline.py`;do notportfailure approval evaluator。
7. Runconsumer grep;onlyscheduled providers/data/workflow mayremain。
8. Deleteold workflow/providers/ledger/timing/conftest/marker policy。
9. Runpost-deletion import/grep/collection/finalworkflow tests。
10. Runlocalpre-freeze tooling smoke with`--authority pre-freeze-tooling-smoke`;deleteoutput。Do notfreezehead oracceptthisartifact。

**Focused verification commands**

```bash
uv run pytest -q \
  tests/unit/infra/test_provider_gate.py \
  tests/unit/infra/test_provider_artifact_flow.py \
  tests/unit/infra/test_provider_test_ownership.py
uv run python scripts/provider_gate.py freeze-linux-environment \
  --descriptor ci/linux-qualification-environment.json \
  --dockerfile ci/linux-qualification.Dockerfile
# Non-authoritative tooling validation only.
uv run python scripts/provider_gate.py build \
  --authority pre-freeze-tooling-smoke \
  --source-sha "$(git rev-parse HEAD)" \
  --out spec-dock/.workbench/provider-gate/pre-freeze-smoke
rm -rf spec-dock/.workbench/provider-gate/pre-freeze-smoke
# Before provider deletion, only the exact scheduled set may match.
git grep -nE 'tests\.conftest|scripts\.quality\.full_regression_baseline|scripts\.quality\.verify_full_regression|--run-full-regression|--full-regression-shard|--full-regression-observation|POLICY_SKIP_REASON|full-regression-ledger\.json|full-regression-timing-weights\.json' -- \
  .github scripts tests AGENTS.md README.md src/spec_dock/assets/spec_dock/docs Makefile pyproject.toml
# Exact test consumers must be gone before providers.
test ! -e tests/unit/test_provider_test_lanes.py
test ! -e tests/unit/test_full_regression_baseline.py
# After deletion, no non-Historical match remains.
test -z "$(git grep -nE 'tests\.conftest|scripts\.quality\.full_regression_baseline|scripts\.quality\.verify_full_regression|--run-full-regression|--full-regression-shard|--full-regression-observation|POLICY_SKIP_REASON|provider-full-regression|full-regression-ledger\.json|full-regression-timing-weights\.json' -- . ':!spec-dock/initiatives/**' || true)"
uv run python -c 'import importlib.util; assert importlib.util.find_spec("scripts.quality.full_regression_baseline") is None; assert importlib.util.find_spec("scripts.quality.verify_full_regression") is None'
uv run pytest --collect-only -q
uv run pytest -q
make lint
cmp src/spec_dock/assets/spec_dock/docs/README.md spec-dock/docs/README.md
grep -F 'make provider-test' AGENTS.md
grep -F 'make provider-qualify' AGENTS.md
python3 - <<'PY_FINAL_WORKFLOW'
# Parse provider-ci.yml:
# - exact job IDs
# - only provider-build-artifacts contains a packaging command
# - all consumers need/download provider-candidate-${ inputs.candidate_sha }
# - each consumer emits build_invocation_count=0
# - provider-gate has no checkout/build/test
PY_FINAL_WORKFLOW
git diff --check
```

**Expected observable result**

Final workflow/tooling/env/docs arepresent。Knownconsumer tests retiredbeforeproviders。Noold policy imports/paths/options。Local smoke removed/non-authoritative。Workflow hasexactlyonepackaging producer anddownload-only consumers。Ordinarytests/collection/lintGREEN。AGENTS/test-policy docs final。

**Evidence to record in Issue report.md**

Consumer inventory/retirement mapping、provider deletion order、workflow structural test、environment descriptor、pre-freeze smoke label/deletion、AGENTS/README/docs hashes andgrep、ordinary collection/tests。No final artifact hashes yet。

**Stop conditions and escalation owner**

Unknownconsumer、provider deletedbeforeconsumer0、more thanoneproducer、downstream build、workflow missing download/hash check、stale policy docs、resource limits unenforceable、orS70 merge handoff。Owner: CI/Product/spec/test owner。

**Cleanup**

Deletepre-freeze artifact/caches。Keeptracked final tooling/env/tests/docs only。

**Internal checkpoint invariant**

S70 isnot a main merge point。Main stillhasworkingS60 transitional gates。PR-C branch hasworkingfinal replacement andno danglingconsumer/provider;it mustcontinueS80 withouttracked content changes exceptreturningtoS70 onfailure。

**Requirement and design trace IDs**

I392-RQ-021〜024、I392-RQ-026、I392-RQ-030、I392-D-012〜013、I392-D-019。

## I392-S80 — Frozen-head Provider CI qualification, downloaded-byte evidence, required transition, and PR-C gate

**Objective and contract-visible outcome**

S70-finalized tracked treeをread-only freezeし、final Provider CIをexact candidate SHAでdispatchする。OnlyLinux`provider-build-artifacts` produceswheel/sdist/manifest。Linux qualification、sdist smoke、macOS delta、attestation consume thesame immutable downloaded bytes withbuild0。Then complete no-gap required-context transition andexternal pre-merge attestation。S80 doesnotedittracked content anddoesnotbuild locally。

**Exact owned repository paths and symbols**

Tracked paths: none。S80 isverification/freeze only。

Ignored/external evidence only:

```text
spec-dock/.workbench/provider-gate/final-run/**
GitHub Actions workflow run/jobs/artifacts/checks
new never-edited pre-merge-attestation-v1 GitHub comment/check artifact
required-context before/both/final snapshots
```

Anyrequired tracked correction returns toS70, createsanewhead, andinvalidatesallS80 evidence。

**Explicit non-owned and no-touch paths**

Alltracked source/tests/docs/specs/report afterfreeze、dogfood seeds/user data/unrelated skills、human settings excepthuman-admin transition、release。

**Prerequisites and dependency**

- S70 final branch GREEN andclean。
- Root/provider/dogfood docs andAGENTS alreadyfinal;`cmp`/grepGREEN。
- Tracked#392 report alreadycontainsnon-self-referential method/pre-freeze facts andiscommitted。
- PR branchhead willremainimmutable throughattestation。
- Human admin available;dedicated canary PR permitted butnevermerged。

**RED evidence**

- Workflow structural tests rejecttwo producers/downstream build/artifact name/hash/source mismatch。
- `verify-downloaded-artifact` rejectswrong run/head/tree/Actions artifact ID/digest/file hashes/build count。
- Environment、budget、CPU、flake、retry、fault mismatch cases failclosed。
- Context transition state machine rejectsold removal beforenew-required RED proof。
- Attestation hash/edit mismatch andtracked-head change failclosed。

**Smallest implementation action**

1. Confirmclean tree;set`VERIFIED_PR_HEAD`、`VERIFIED_PR_TREE`、`PR_BRANCH`。No furthertracked writes。
2. Runread-only local lint/collection/docs/dogfood validation;onfailure returnS70。
3. Dispatchfinal workflow on`PR_BRANCH` withinputs`candidate_sha=$VERIFIED_PR_HEAD` and`qualification=true`。
4. Selecttheunique run whosehead SHA/input/receipt equalsfrozenhead;waitwith`gh run watch --exit-status`。
5. Fetchrun/jobs andActions artifact metadata。Requireonejob`provider-build-artifacts` andoneartifact`provider-candidate-$VERIFIED_PR_HEAD`。
6. Downloadcandidate artifact andallconsumer receipts toignored evidence dir。
7. Verifycandidate manifest source SHA/tree、wheel/sdist hashes、build count1、Actions artifact ID/digest/name/run ID。VerifyLinux/macOS/sdist/attestation receipts referenceexact hashes andbuild count0。
8. VerifyLinux environment fingerprint samefor20 runs、first5 budget/CPU、all20flake/retry0、fault100%。Verify macOS samewheel andexclusive nodes。
9. Verifyfresh consumer、dogfood sync/validate evidence fromworkflow receipts;local read-only validate mayconfirmbutcannot replaceworkflow evidence。
10. Human capturesrequired before-state。New gate isalreadyGREEN whileold remainsrequired。
11. Human addsnewcontext required, keepsold, read-back both。
12. Dedicated non-merge canary setsnew gateRED;proveblocking;closewithoutmerge。
13. Re-run/confirmimplementation PR new gateGREEN onthefrozenhead;read-back。
14. Human removesold provider-only context;read-backfinal unrelated/review unchanged。
15. Generatecanonical`pre-merge-attestation-v1` fromdownloaded receipts/API snapshots;postnew never-edited object withJSON SHA-256。
16. ReconfirmHEAD/tree/working tree unchanged。

**Focused verification commands**

```bash
test -z "$(git status --short)"
VERIFIED_PR_HEAD="$(git rev-parse --verify 'HEAD^{commit}')"
VERIFIED_PR_TREE="$(git rev-parse --verify 'HEAD^{tree}')"
PR_BRANCH="$(git branch --show-current)"
REPO="chemitaro/spec-dock"
export VERIFIED_PR_HEAD VERIFIED_PR_TREE PR_BRANCH REPO
mkdir -p spec-dock/.workbench/provider-gate/final-run
make lint
uv run pytest --collect-only -q
uv run pytest -q
cmp src/spec_dock/assets/spec_dock/docs/migration.md spec-dock/docs/migration.md
cmp src/spec_dock/assets/spec_dock/docs/README.md spec-dock/docs/README.md
python3 ./spec-dock/scripts/spec-dock validate
# Dispatch the authoritative build/qualification run. No local build command is permitted below.
gh run list --workflow provider-ci.yml --branch "$PR_BRANCH" --event workflow_dispatch --limit 100 \
  --json databaseId --jq '.[].databaseId' > spec-dock/.workbench/provider-gate/final-run/before-run-ids.txt
gh workflow run provider-ci.yml --ref "$PR_BRANCH" \
  -f candidate_sha="$VERIFIED_PR_HEAD" \
  -f qualification=true
for _ in $(seq 1 60); do
  gh run list --workflow provider-ci.yml --branch "$PR_BRANCH" --event workflow_dispatch --limit 100 \
    --json databaseId,headSha,status,conclusion,createdAt > spec-dock/.workbench/provider-gate/final-run/run-list.json
  RUN_ID="$(jq -r --slurpfile before <(jq -Rsc 'split("\n") | map(select(length>0)|tonumber)' spec-dock/.workbench/provider-gate/final-run/before-run-ids.txt) \
    --arg sha "$VERIFIED_PR_HEAD" \
    '[.[] | select(.headSha==$sha and ((.databaseId as $id | $before[0] | index($id))|not))] | if length==1 then .[0].databaseId else empty end' \
    spec-dock/.workbench/provider-gate/final-run/run-list.json)"
  test -n "$RUN_ID" && break
  sleep 5
done
test -n "$RUN_ID"
test "$(jq --arg sha "$VERIFIED_PR_HEAD" --slurpfile before <(jq -Rsc 'split("\n") | map(select(length>0)|tonumber)' spec-dock/.workbench/provider-gate/final-run/before-run-ids.txt) \
  '[.[] | select(.headSha==$sha and ((.databaseId as $id | $before[0] | index($id))|not))] | length' \
  spec-dock/.workbench/provider-gate/final-run/run-list.json)" = 1
gh run watch "$RUN_ID" --exit-status
gh run view "$RUN_ID" --json databaseId,headSha,status,conclusion,jobs > spec-dock/.workbench/provider-gate/final-run/run.json
test "$(jq -r .headSha spec-dock/.workbench/provider-gate/final-run/run.json)" = "$VERIFIED_PR_HEAD"
gh api "repos/$REPO/actions/runs/$RUN_ID/artifacts" > spec-dock/.workbench/provider-gate/final-run/artifacts.json
ARTIFACT_NAME="provider-candidate-$VERIFIED_PR_HEAD"
test "$(jq --arg n "$ARTIFACT_NAME" '[.artifacts[] | select(.name==$n)] | length' spec-dock/.workbench/provider-gate/final-run/artifacts.json)" = 1
gh run download "$RUN_ID" -n "$ARTIFACT_NAME" -D spec-dock/.workbench/provider-gate/final-run/candidate
gh run download "$RUN_ID" -n "provider-evidence-$VERIFIED_PR_HEAD" -D spec-dock/.workbench/provider-gate/final-run/evidence
uv run python scripts/provider_gate.py verify-downloaded-artifact \
  --candidate-dir spec-dock/.workbench/provider-gate/final-run/candidate \
  --evidence-dir spec-dock/.workbench/provider-gate/final-run/evidence \
  --run-json spec-dock/.workbench/provider-gate/final-run/run.json \
  --artifacts-json spec-dock/.workbench/provider-gate/final-run/artifacts.json \
  --source-sha "$VERIFIED_PR_HEAD" \
  --source-tree "$VERIFIED_PR_TREE" \
  --expected-producer-job provider-build-artifacts \
  --expected-consumer-build-count 0
uv run python scripts/provider_gate.py emit-attestation \
  --type pre-merge-attestation-v1 \
  --source-sha "$VERIFIED_PR_HEAD" \
  --workflow-run-id "$RUN_ID" \
  --input spec-dock/.workbench/provider-gate/final-run/evidence \
  --output spec-dock/.workbench/provider-gate/final-run/pre-merge-attestation.json
test "$(git rev-parse HEAD)" = "$VERIFIED_PR_HEAD"
test "$(git rev-parse 'HEAD^{tree}')" = "$VERIFIED_PR_TREE"
test -z "$(git status --short)"
```

`gh run list` selection mustalso becheckedagainstthe downloaded build receipt's`candidate_sha`; ifzero/multiplematching runs, stop。Workflow jobs themselves, notlocalcommands, ownfinalpackage/five-run/macOS/sdist evidence。

**Expected observable result**

One frozenhead、oneLinux packaging invocation、oneimmutable candidate artifact、samewheel/sdist bytes everywhere、allconsumer build counts0、stable environment20 runs、budget/CPU/fault/flake acceptance、new required beforeRED、canary blocked、implementationGREEN、old context removedafterproof、external attestation hashverified、tracked head/tree clean/unchanged。

**Evidence to record**

Tracked report receivesnothing afterfreeze。External pre-merge attestation containsfinalhead/tree、report blob observedexternally、workflow run/job IDs、Actions artifact ID/name/digest、candidate manifest/file hashes、producer count1、consumer build0 receipts、environment/runs/faults/macOS/sdist、required snapshots、commands/conclusions。

**Stop conditions and escalation owner**

Anytracked edit、local final build、zero/multiple run、wronghead/tree、producer countnot1、consumerbuildnot0、artifact reupload/hash mismatch、environment/budget/fault/flake/seed/docs/context/RED/attestation mismatch。Return toS70/newhead andrerunallsource-bound evidence。Owners: CI/Product/spec;settings:humanadmin。

**Cleanup**

Closecanary withoutmerge。KeepGitHub immutable evidence perretention;localignored downloads mayberemoved afterattestation verification。Do notmodifytrackedtree。

**PR-C main merge invariant**

S80 is theonly PR-C main merge gate。S70 replacement/consumer closure andS80 authoritativeworkflow proof/context/attestation/human review allGREEN。Main afterhuman merge hascompletefinal lifecycle/docs/wire/register closure、final build-once gate、noold machinery、final AGENTS。Agent doesnotmerge。

**Requirement and design trace IDs**

I392-RQ-021〜030、I392-D-012〜019。

## 4. Human merge and external closure protocol

### Pre-merge handoff

External pre-merge attestation providesPR URL、head SHA/tree OID、report blob OID、artifact/environment/test/context hashes。Tracked report doesnotself-reference。

### Human merge

Human performsmerge。Merge commit allowed。

### Tree equality

```bash
MERGE_COMMIT="<human observed merge commit>"
test "$(git rev-parse "${VERIFIED_PR_HEAD}^{tree}")" = \
     "$(git rev-parse "${MERGE_COMMIT}^{tree}")"
```

Do notcomparelater`origin/main`。

### Post-merge closure attestation

Generatecanonical `post-merge-closure-v1` externally withpre-attestation hash、merge SHA/tree、tree equality、actor/time、SpecDock issue finish result、GitHub #392 close event。Post asnew never-edited evidence。Do notwrite tracked report。

### Epic closure

After#392 finish, generate`epic-closure-v1` referencingpost-merge attestation andGitHub #384 close event。No newIssue。

## 5. Definition of done

All I392-RQ-001〜030 verified。S30/S60/S80 areonly main merge gates。Machine-readable owner decision list remains`[]`。
