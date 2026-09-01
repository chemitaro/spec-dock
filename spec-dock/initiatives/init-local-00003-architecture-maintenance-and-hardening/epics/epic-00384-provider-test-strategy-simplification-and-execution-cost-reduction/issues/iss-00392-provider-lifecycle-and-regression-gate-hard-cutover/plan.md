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
  sha: "e47c1356892857e61388c7aefb2539d2061d1b9c"
---

# iss-00392 Provider Lifecycle And Regression Gate Hard Cutover — 実装計画

## 1. Execution rules

1. 本書がentry point。BehaviorはIssue Requirement、components/state/filesystemはIssue Designを参照する。
2. Product source of truthは`src/spec_dock/`。Provider-firstで変更しdogfoodを後から同期する。
3. Behavior changeはtest-first。Existing failing nodeをRED authorityにする場合はexact node/reasonをtracked reportへ記録する。
4.各stepはimplementationとfocused verificationを含むvertical milestone。
5. S40/S50はPR-B internal checkpoint、S60だけPR-B main gate。
6. S70はPR-C internal checkpoint、S80だけPR-C main gate。
7. S60ではcurrent workflow/policy consumersを壊さずS70-only toolへ依存しない。
8. S70はreplacement gate/environment/workflow/AGENTSを追加してからold machineryを同じbranchで削除する。
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

**Focused verification commands**

```bash
test -z "$(git status --short)"
git merge-base --is-ancestor "$SPEC_FREEZE_COMMIT" "$IMPLEMENTATION_BASE_SHA"
git show "$SPEC_FREEZE_COMMIT:<canonical-path>" | sha256sum
git diff --name-status "$ISSUE_387_MERGE^1" "$ISSUE_387_MERGE"
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
tests/unit/infra/test_provider_assets.py
```

Symbols: Issue Design model/candidate/legacy symbols、`SeedPolicy`、`ResumeIdentity`。

**Explicit non-owned and no-touch paths**

Public CLI、old engine/manifest、workflows、dogfood。

**Prerequisites and dependency**

S00 GREEN。

**RED evidence**

Exact constants/order、record keys/relations/duplicate/size/type、seed policy matrix、resume tuple mismatch、candidate unsafe rejection/determinism、legacy exact/modified/recovery、invalid JSON nolegacy fallback。

**Smallest implementation action**

Pure dataclasses/enums/parsers/digest/legacy observation。No mutation function。

**Focused verification commands**

```bash
uv run pytest -q tests/unit/infra/test_provider_lifecycle_model.py \
  tests/unit/infra/test_provider_lifecycle_candidate.py \
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

## I392-S40 — Tooling-only uninstall, durable reinstall, public CLI cutover

**Objective and contract-visible outcome**

Uninstall/reinstall、version `0.2.4`、new CLI wiring、purge trapをcomplete final public routeへ接続する。PR-B internal checkpoint only。

**Exact owned repository paths and symbols**

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

**Explicit non-owned and no-touch paths**

Old engine file retained untilS60、current test policy/workflows retained throughS60、user data/seeds。

**Prerequisites and dependency**

S30 GREEN。S40 startsPR-B same branch/PR; no main handoff beforeS60。

**RED evidence**

Uninstall dry-run/apply/default/aliases/trap、durable preserve-only record、reinstall no seed、CLI state dispatch、JSON additive policy/bootstrap fields、wrapper forwarding、success/error/exit mapping。

**Smallest implementation action**

Implement uninstall/result、wire CLI exclusively tosuccessor、version bump、remove purge public callsites、update wrapper/docs。

**Focused verification commands**

```bash
uv run pytest -q tests/unit/infra/test_provider_lifecycle_public_result.py
uv run pytest --run-full-regression --full-regression-shard -q \
  tests/cli_runtime/test_provider_lifecycle.py \
  tests/cli_runtime/test_uninstall.py \
  tests/cli_runtime/test_update.py
make lint
```

**Expected observable result**

Public final routes workfornon-legacy proven states、purge unreachable、current policy operational、protected data/seeds unchanged。

**Evidence to record in Issue report.md**

CLI matrix、payloads/exits、policy、protected digests、old callsite grep。

**Stop conditions and escalation owner**

Bridge/toggle needed、purge mutation retained、schema breaking、S40 merge handoff attempted。Owner: Product + implementation owner。

**Cleanup**

Provider/dogfood wrapper parity、temp snapshots。

**Internal checkpoint invariant**

S40 isnot a main merge point。Same PR-B branch mustcontinue throughS50/S60。No S40-only handoff。

**Requirement and design trace IDs**

I392-RQ-013〜019。

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

## I392-S60 — Old engine/test terminalization and PR-B main merge gate

**Objective and contract-visible outcome**

Old per-file/journal/purge engineとduplicate testsを削除しall active failuresをterminalizeする。同時にcurrent main-push verifierの全consumerを保持・更新してGREENにする。S70-only provider gateへ依存しない。

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

Add/update:

```text
src/spec_dock/context_pack.py
src/spec_dock/cli.py
tests/unit/infra/test_provider_assets.py
tests/unit/infra/test_provider_test_ownership.py
tests/provider_test_ownership.json
tests/** exact active failure owners
full-regression-ledger.json                     # zero active; node updates
full-regression-timing-weights.json              # deleted node refs only
tests/conftest.py                                # deleted node refs only; policy retained
```

Must retain functional untilPR-C:

```text
scripts/quality/full_regression_baseline.py
scripts/quality/verify_full_regression.py
.github/workflows/provider-full-regression.yml
pytest fast/full policy and markers
```

**Explicit non-owned and no-touch paths**

Provider workflow redesign/removal、root AGENTS final policy、provider gate/environment、consumer data。

**Prerequisites and dependency**

S50 allproof GREEN、same PR-B branch、no old public callsite。

**RED evidence**

Old imports/files grep、ownership duplicate/missing tests、each active row focused RED/retirement authority、context/assets successor tests、current verifier fails ifstale node remains。

**Smallest implementation action**

Extract context behavior、move asset assertions、terminalizeeach row fix/successor/retirement、addstandalone ownership pytest、deleteold engine/tests、updatecurrent ledger/timing/conftest exact refs、runordinary/current verifier。Do notdeletecurrent policy consumers orcallprovider_gate。

**Focused verification commands**

```bash
test -z "$(git grep -nE 'execute_explicit_spec_history_purge_distribution|from spec_dock\.managed_distribution|import spec_dock\.managed_distribution' -- src tests || true)"
uv run pytest -q tests/unit/infra/test_provider_assets.py \
  tests/unit/infra/test_provider_test_ownership.py
uv run pytest -q
uv run python -m scripts.quality.verify_full_regression --shards 4
make lint
test -f .github/workflows/provider-full-regression.yml
test -f scripts/quality/verify_full_regression.py
test -f tests/conftest.py
```

**Expected observable result**

Old product engine absent、active approved failure0、current verifier/main-push workflow GREEN、no missing consumer、no provider_gate dependency。

**Evidence to record in Issue report.md**

Deletion table、failure terminalization table、ownership output、ledger active0、current verifier logs、retained consumer inventory。

**Stop conditions and escalation owner**

Unterminalized row/security gap/current verifier broken/S70-only command/workflow consumer deletion。Owner: Product/test/CI owner。No merge。

**Cleanup**

Obsolete fixtures/imports/mypy entries only。Keepcurrent policy infrastructure intentionally。

**PR-B main merge gate invariant**

S60 is the only PR-B main merge gate。S40+S50+S60 allproof GREEN。Human merge後のmain hascomplete final `0.2.4` lifecycle、no old fallback、active approved failure0、andstill-current main-push workflow withallconsumers intact/GREEN。No bridge/toggle。

**Requirement and design trace IDs**

I392-RQ-018〜021、I392-D-011〜013、PR continuity。

## I392-S70 — Replacement provider gate/environment/AGENTS and atomic old policy removal

**Objective and contract-visible outcome**

PR-C branchでreplacement gate、stable Linux environment、final workflow、root AGENTSを作成し、same branch/change setでold policy/workflow machineryを削除する。S70 internal only。

**Exact owned repository paths and symbols**

Create/update:

```text
scripts/provider_gate.py
ci/linux-qualification.Dockerfile
ci/linux-qualification-environment.json
tests/unit/infra/test_provider_gate.py
scripts/static_analysis/run.sh
Makefile
.github/workflows/provider-ci.yml
AGENTS.md
tests/provider_test_ownership.json
pyproject.toml
```

Delete:

```text
.github/workflows/provider-full-regression.yml
tests/conftest.py
full-regression-ledger.json
full-regression-timing-weights.json
scripts/quality/full_regression_baseline.py
scripts/quality/verify_full_regression.py
scripts/quality/__init__.py if empty
fast/full marker declarations/decorators/options
```

**Explicit non-owned and no-touch paths**

Consumer seed workflows、commit identity workflow、unrelated settings、human required configuration、release。

**Prerequisites and dependency**

S60 exact tree/PR-B merge result withcurrent gate GREEN。PR-C continues throughS80 beforemerge。

**RED evidence**

Provider gate command/hash/build-count/one-pytest、environment freeze/fingerprint mismatch、workflow same-wheel/macOS no build、atomic replacement ordering、AGENTS forbidden/required text、qualification evaluator failures、node intersection。

**Smallest implementation action**

Implement gate/tests、freeze descriptor/base digest/uv/lock、addDocker/resource limits、rewriteworkflow/Makefile/static analysis、updateAGENTS、verifyreplacement、deleteold machinery in same branch、run no-stale checks。Do notmerge。

**Focused verification commands**

```bash
uv run pytest -q tests/unit/infra/test_provider_gate.py
uv run python scripts/provider_gate.py freeze-linux-environment \
  --descriptor ci/linux-qualification-environment.json \
  --dockerfile ci/linux-qualification.Dockerfile
uv run python scripts/provider_gate.py build \
  --source-sha "$(git rev-parse HEAD)" \
  --out spec-dock/.workbench/provider-gate/candidate
uv run python scripts/provider_gate.py verify-artifact \
  --manifest spec-dock/.workbench/provider-gate/candidate/manifest.json \
  --source-sha "$(git rev-parse HEAD)"
uv run python scripts/provider_gate.py verify-environment \
  --descriptor ci/linux-qualification-environment.json
uv run python scripts/provider_gate.py verify-node-ownership \
  --map tests/provider_test_ownership.json
make lint
git grep -nE -- '--run-full-regression|--full-regression-shard|POLICY_SKIP_REASON|full-regression-ledger|verify_full_regression|full_regression' \
  -- . ':!spec-dock/initiatives/**' || true
grep -F 'make provider-test' AGENTS.md
grep -F 'make provider-qualify' AGENTS.md
```

**Expected observable result**

Replacement gate runnable、environment fixed、old machinery absent onPR-C branch、AGENTS final、no workflow missing files、new PR workflow GREEN。

**Evidence to record in Issue report.md**

Descriptor/hash/fingerprint schema、build manifest schema、workflow/deletion inventory、AGENTS policy diff。Final head-bound values external onlyafterfreeze。

**Stop conditions and escalation owner**

Replacement unavailable/resource limits unenforceable/old consumer broken/AGENTS stale/macOS rebuild/S70 merge handoff。Owner: CI/Product owner。

**Cleanup**

Build temp/caches、keeptracked descriptor/Dockerfile。

**Internal checkpoint invariant**

S70 isnot a main merge point。Main stillhasworking current gate untilPR-C merge。PR-C branch hasworking replacement/no dangling consumers andmustcontinueS80。

**Requirement and design trace IDs**

I392-RQ-021〜023、I392-RQ-026、I392-D-011〜013。

## I392-S80 — Final qualification, dogfood, required transition, external attestation, PR-C gate

**Objective and contract-visible outcome**

Tracked report/docs/dogfoodをfinalizeしhead freeze後にsame candidate/environmentでqualification、required transition、content-addressed external pre-merge attestationを完成する。PR-C only merge gate。

**Exact owned repository paths and symbols**

Beforehead freeze:

```text
scripts/provider_gate.py
tests/unit/infra/test_provider_gate.py
README.md
AGENTS.md
provider/dogfood docs/runtime pairs
dogfood 4 roots/2 slots/record
tests/provider_test_ownership.json
#392 report.md                    # pre-merge content only
```

Afterhead freeze: tracked pathsnone。Ignored/external evidence only。

**Explicit non-owned and no-touch paths**

Dogfood seeds、user history、unrelated skills、canonical R/D/P、settings excepthuman operation、release。

**Prerequisites and dependency**

S70 branch GREEN。Tracked report schema finalized。Human admin available。Dedicated canary PR allowed butnevermerged。

**RED evidence**

Environment mismatch、budget/CPU/flake/retry、missing fault、seed mutation、provider/dogfood drift、attestation hash mismatch、tracked report forbidden fields、context order state machine、tree OID comparison。

**Smallest implementation action**

Phase A tracked freeze:

1. Complete tracked report withmethod/step summaries/terminalization/external schema;omitown hash/final head/final source-bound hashes/post-merge facts。
2. UpdateREADME/AGENTS/provider/dogfood andverifyseed hashes。
3. Commitalltracked content andfreeze`VERIFIED_PR_HEAD`/`VERIFIED_PR_TREE`;no furthertracked edits。

Phase B source-bound evidence:

4. Buildexact head once。
5. Verifyenvironment descriptor/start exact environment。
6. Run20 sequential canonical;first5 budget/all20 stability。
7. Runfault pack andmacOS delta same wheel。
8. Runfresh consumer/dogfood validate。
9. New gate GREEN onimplementation PR。
10. Human capturesrequired before-state。
11. Human addsnew required whileold remains;read-back both。
12. Dedicated non-merge canary makesnew gateRED;proveblocked;closecanary。
13. Implementation PR GREEN/read-back。
14. Human removesold provider-only/read-back final。
15. Generate/postnew never-edited `pre-merge-attestation-v1` withcanonical JSON SHA-256。
16. Verifyhead unchanged/clean。

**Focused verification commands**

```bash
make lint
make provider-test
uv run python scripts/provider_gate.py qualify \
  --manifest spec-dock/.workbench/provider-gate/candidate/manifest.json \
  --environment ci/linux-qualification-environment.json \
  --environment-id specdock-linux-qualification-v1 \
  --runs 20 --budget-runs 5 \
  --wall-limit-seconds 600 --cpu-wall-ratio-limit 1.1
uv run python scripts/provider_gate.py macos-delta \
  --manifest spec-dock/.workbench/provider-gate/candidate/manifest.json
python3 ./spec-dock/scripts/spec-dock sync
python3 ./spec-dock/scripts/spec-dock validate
uv run python scripts/provider_gate.py emit-attestation \
  --type pre-merge-attestation-v1 \
  --output spec-dock/.workbench/provider-gate/pre-merge-attestation.json
test "$(git rev-parse HEAD)" = "$VERIFIED_PR_HEAD"
test -z "$(git status --short)"
```

**Expected observable result**

Same environment fingerprint all20、first5 wall/CPU pass、all20 failure/flake/retry0、fault100%、same wheel Linux/macOS、dogfood/fresh consumer valid、seed unchanged、new required alongsideold beforeRED、canary blocked、implementation GREEN、old removed afterproof、attestation hash verified、head clean/unchanged。

**Evidence to record in Issue report.md**

Tracked report receivespre-freeze method/non-self-referential summaries only。External attestation receivesfinal head/tree/report blob observedexternally、artifacts/environment/runs/faults/contexts/commands。

**Stop conditions and escalation owner**

Tracked edit afterfreeze、environment/budget/fault/flake/seed/context/RED/attestation mismatch。Same Issue forward-fix;new head requiresallsource-bound evidence rerun。Settings owner:human admin。

**Cleanup**

Canary closed withoutmerge、temporary environments/workspaces removed、external attestations retained。

**PR-C main merge invariant**

Only PR-C merge gate。S70+S80 allproof、new context required/GREEN、external pre-merge attestation、human review complete。Main afterhuman merge hasfinal provider gate、no old machinery、final AGENTS、complete lifecycle。Agent doesnotmerge。

**Requirement and design trace IDs**

I392-RQ-021〜026、I392-D-011〜015。

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

All I392-RQ-001〜026 verified。S30/S60/S80 areonly main merge gates。Machine-readable owner decision list remains`[]`。
