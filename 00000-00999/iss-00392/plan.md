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
  sha: "eaddf76806c338ee05463741f15fd3967bbceb57"
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


## I392-S00 — Deterministic specification/#387/dogfood admission and baseline

**Objective and contract-visible outcome**

Verify specification lineage、#387 permitted three-way outcomes、source ledger all 27 identities、implementation base、exact legacy dogfood evidence andcurrent gates before anyproduction change。Materialize aformula-derived `post-387-admission.json`;do not assume15 rows。

**Exact owned repository paths and symbols**

- Read-only repository/GitHub and#387 R/D/P/report/merge tree。
- Tracked write: #392 `report.md` pre-merge admission summary only。
- Ignored: `spec-dock/.workbench/iss-00392/admission/**` includingadmission JSON、protected witness、baseline artifacts。
- No production symbol change。

**Explicit non-owned and no-touch paths**

Allproduction/tests/workflows/settings and#387 canonical R/D/P/report content。S00 parses #387 evidence butdoes notrepair it。

**Prerequisites and dependency**

- This pack imported and`SPEC_FREEZE_COMMIT` recorded。
- #387 human merge complete。
- Implementation base contains bothlineages andisclean。
- #387 report contains one exact disposition block betweenregister markers。

**RED evidence or justified no-new-test rule**

Temporary read-only admission checker mustreject: missing/duplicate report entry、invalid outcome、removed node stillpresent、retained node/signature drift、split mapping mismatch、multiple/no-declared failure lineage、unmapped new ledger row、outside-scope delta、wrongspec hash、non-exact dogfood record orunexpected slot marker。No production test isadded in S00。

**Smallest implementation action**

1. Verifyreplacement manifest hashes against`SPEC_FREEZE_COMMIT` blobs andancestry。
2. Obtain#387 base/head/merge/tree;validateits ownallowlist/content restrictions without changing#387 docs。
3. Parsecurrent register source block andverify all 27 original node/signature identities against theevidence ledger。
4. Parse#387 report block andcross-checkpost-merge tree、ledger、full collection using`ISS387-THREE-WAY-V1`。
5. Emitignored `post-387-admission.json` withformula-derived admitted rows;require allnew ledger rows mapped。
6. Capturecurrent lint/ordinary/current full workflows。
7. Buildbaseline0.2.3 wheel+sdist once forlegacy fixture only。
8. Provedogfood record bytes are exact `0.2.3\n` andbothfixed slots have no marker;capturefour-root/two-slot/protected/seed digests。

**Focused verification commands**

```bash
test -z "$(git status --short)"
git merge-base --is-ancestor "$SPEC_FREEZE_COMMIT" "$IMPLEMENTATION_BASE_SHA"
git show "$SPEC_FREEZE_COMMIT:<canonical-path>" | sha256sum
git diff --name-status "$ISSUE_387_MERGE^1" "$ISSUE_387_MERGE"
uv run python spec-dock/.workbench/iss-00392/admission/check_register.py   --register spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00384-provider-test-strategy-simplification-and-execution-cost-reduction/artifacts/active-failure-disposition-register.md   --issue-387-report spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00356-specdock-core-simplification-and-external-intelligence-boundary/issues/iss-00387-current-surface-workflow-residue-cleanup/report.md   --ledger full-regression-ledger.json   --output spec-dock/.workbench/iss-00392/admission/post-387-admission.json
python - <<'PY'
from pathlib import Path
assert Path('spec-dock/spec-dock.version').read_bytes() == b'0.2.3\n'
for p in (Path('.agents/skills/spec-dock/.spec-dock-provider-slot.json'), Path('.agents/skills/spec-dock-grill-with-docs/.spec-dock-provider-slot.json')):
    assert not p.exists() and not p.is_symlink()
PY
make lint
uv run pytest -q
uv run python -m scripts.quality.verify_full_regression --shards 4
uv build --sdist --wheel --out-dir spec-dock/.workbench/iss-00392/admission/dist
python3 ./spec-dock/scripts/spec-dock validate
git diff --check
test -z "$(git status --short)"
```

**Expected observable result**

Spec/#387 lineages exact、all 27 source identities accounted、eachconditional row hasonevalid report-driven branch、no unmapped row、formula-derived admitted ledger、current gatesGREEN、baselineartifact hashesfixed、dogfood exactlegacy/protected witness recorded。

**Evidence to record in Issue report.md**

Repository evidence/current SHA、manifest/SPEC_FREEZE、#387 base/head/merge/tree/report blob、register/ledger blob、27identity digest、conditional branch table、admitted row formula/result、baseline artifacts、dogfood record/marker/root/slot/protected/seed digests、commands/exits。

**Stop conditions and escalation owner**

Any missing report marker/entry、unmapped newnode、signature drift、#387 contract-external result、wrong dogfood legacy evidence、protected drift、baseline failure。Stop before S10;canonical spec owner updatesregister/spec andobtainsindependent Strict re-review。Luna must notchooseadisposition。Owner:spec/Product/repository owner。

**Cleanup**

Detached worktree/venv/temp checker afterevidence capture。Keepignored baseline/admission/protected witness through S60。

**Merge-point invariant**

No code diff。Not amerge point。

**Requirement and design trace IDs**

I392-RQ-001、I392-RQ-029、I392-RQ-031、I392-D-014、I392-D-018、I392-D-020。
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

S30 GREEN。S40 startsPR-B same branch/PR; S40/S50 cannot beoffered formerge。Wire artifact hash isverified throughSPEC_FREEZE_COMMIT。

**RED evidence**

- Wire tests fail until durable `operation=install` plus `legacy-migration-*` public codes, exact action/nullability relations, and all goldens match the normative wire artifact。
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

S40 is not a main merge point。Same PR-B branch continuesS50/S60。No S40-only handoff。

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

S50 is not a main merge point。Same branch continuesS60。No S50-only handoff。

**Requirement and design trace IDs**

I392-RQ-016〜017。


## I392-S60 — Terminalization, current workflow repair, complete dogfood migration, and PR-B gate

**Objective and contract-visible outcome**

Removeold lifecycle engine/tests aftersuccessor proof、mechanically terminalize the formula-derived post-#387 admitted failure set、keep bothcurrent workflows independentlyGREEN、convergeallPR-B docs andchecked-in dogfood tocomplete 0.2.4。This is the onlyPR-B main merge gate anddoes notintroducefinal S70 provider-gate design。

**Exact owned repository paths and symbols**

Deleteold product/tests:

```text
src/spec_dock/managed_distribution.py
src/spec_dock/assets/managed_distribution.json
tests/unit/infra/test_managed_distribution.py
tests/unit/infra/test_init_update.py
tests/cli_runtime/test_distribution_cutover.py
tests/integration/test_epic_00343_distribution.py
```

Create/update successor andtransitional gate:

```text
src/spec_dock/context_pack.py
src/spec_dock/cli.py
src/spec_dock/provider_lifecycle/**
.github/workflows/provider-ci.yml
tests/unit/test_provider_test_lanes.py
tests/unit/infra/test_provider_assets.py
tests/provider_test_ownership.json
full-regression-ledger.json
full-regression-timing-weights.json
tests/conftest.py
exact failure-owner tests from post-387-admission.json
README.md lifecycle sections
src/spec_dock/assets/spec_dock/docs/migration.md
src/spec_dock/assets/spec_dock/docs/README.md
spec-dock/docs/migration.md
spec-dock/docs/README.md
spec-dock/{docs,templates,system,scripts}
.agents/skills/spec-dock
.agents/skills/spec-dock-grill-with-docs
spec-dock/spec-dock.version
.agents/skills/spec-dock/.spec-dock-provider-slot.json
.agents/skills/spec-dock-grill-with-docs/.spec-dock-provider-slot.json
#392 report.md pre-merge implementation summary
```

Retainworking throughPR-C:

```text
scripts/quality/full_regression_baseline.py
scripts/quality/verify_full_regression.py
.github/workflows/provider-full-regression.yml
fast/full marker policy
```

**Explicit non-owned and no-touch paths**

#387 canonical docs/report、S70 provider gate/environment/finalAGENTS test-policy redesign、consumer seeds、initiatives/artifacts/workbench/unknown user data、release/settings。

**Prerequisites and dependency**

S50GREEN。`post-387-admission.json` isvalid andbinds#387 merge/report/ledger/collection。S60 branch includesS40/S50;no intermediate merge。

**RED evidence**

- Transitional provider CI failswhiledeleted old test paths remain。
- Lane test fails forfixed15 assumption、missing report mapping、active row、wrong terminal rule、unmapped successor orstale workflow path。
- Current main-push verifier failswhenledger/timing/conftest referencesdeleted nodes。
- Wire goldens fail foranyphase/reason/code/order mismatch。
- Dogfood verification failsbeforemigration、onpartial root/slot、marker absence、record mismatch、digest mismatch、seed/protected drift。
- Docs grep fails forlegacy journal、compatible-newer recovery、purge authority、empty-boundary guidance。

**Smallest implementation action**

1. Extractremainingnon-lifecycle context behavior andmoveasset assertions。
2. Applyregister branches from`post-387-admission.json`: outside rows perfixed rule; conditional retained/failure-lineage nodes fixed-in-place; removed/no-lineage identities remain terminal inregister;active0。
3. Updateledger/timing/conftest exact admitted rows andmake`tests/unit/test_provider_test_lanes.py` validateformula andcurrent evaluator parity。
4. Deleteold engine/manifest/duplicate tests。
5. Retargetcurrent`.github/workflows/provider-ci.yml` only:
   - unit -> existingprovider lifecycle model/candidate/filesystem/service/result tests;
   - CLI -> `test_provider_lifecycle.py`、`test_uninstall.py`、`test_update.py`;
   - artifact -> `test_provider_lifecycle_artifacts.py`、tripwire;
   - macOS matrix -> `test_provider_lifecycle_macos.py`。
   Preserveworkflow name/event/job IDs/matrix/setup/static topology;no build-once redesign。
6. Finishroot README lifecycle andprovider docs;sync exact dogfood docs projection。
7. Snapshotprotected dogfood paths/seeds fromS00 witness。
8. Run`uvx --no-cache --from . spec-dock update .` against repository root。This performs exact legacy migration withseed policy preserve-only。
9. Parsecandidate、record、markers;requirecompleteS60 digest identity andno incomplete/stage residue。
10. Verifyprotected witness/seed hashesbyte-identical、validate andfresh consumer。
11. Runcurrent PR workflow-equivalent suite andcurrent4-shard verifier independently。

**Focused verification commands**

```bash
uv run pytest -q tests/unit/test_provider_test_lanes.py   tests/unit/infra/test_provider_assets.py   tests/unit/infra/test_provider_lifecycle_model.py   tests/unit/infra/test_provider_lifecycle_public_result.py
uv run pytest --run-full-regression --full-regression-shard -q   tests/cli_runtime/test_provider_lifecycle.py   tests/cli_runtime/test_uninstall.py   tests/cli_runtime/test_update.py   tests/integration/test_provider_lifecycle_artifacts.py   tests/integration/test_provider_lifecycle_tripwire.py
python - <<'PY'
from pathlib import Path
import hashlib, json
protected = [Path('spec-dock/initiatives'), Path('spec-dock/.workbench'), Path('spec-dock/.gitignore'), Path('.github/workflows/ci.yml')]
def snap(path):
    if path.is_symlink(): return ['symlink', path.readlink().as_posix()]
    if path.is_file(): return ['file', hashlib.sha256(path.read_bytes()).hexdigest()]
    rows=[]
    if path.is_dir():
        for p in sorted(path.rglob('*'), key=lambda x:x.as_posix().encode()):
            rel=p.relative_to(path).as_posix()
            rows.append([rel, 'symlink', p.readlink().as_posix()] if p.is_symlink() else [rel, 'file', hashlib.sha256(p.read_bytes()).hexdigest()] if p.is_file() else [rel, 'dir', ''])
    return ['dir', rows] if path.is_dir() else ['absent', None]
Path('spec-dock/.workbench/iss-00392').mkdir(parents=True, exist_ok=True)
Path('spec-dock/.workbench/iss-00392/s60-protected-before.json').write_text(json.dumps({p.as_posix():snap(p) for p in protected}, sort_keys=True)+'\n')
PY
uvx --no-cache --from . spec-dock update .
uv run python - <<'PY'
from pathlib import Path
from spec_dock.provider_lifecycle.candidate import build_packaged_candidate
from spec_dock.provider_lifecycle.model import parse_install_record, parse_slot_marker
candidate = build_packaged_candidate(Path('src/spec_dock/assets'), '0.2.4')
record = parse_install_record(Path('spec-dock/spec-dock.version').read_bytes())
assert record.state.value == 'ready' and record.operation is None
assert record.version == '0.2.4' and record.seed_policy.value == 'preserve-only'
assert record.candidate_digest == candidate.digest
for slot in ('spec-dock','spec-dock-grill-with-docs'):
    marker=parse_slot_marker(Path('.agents/skills')/slot/'.spec-dock-provider-slot.json')
    assert marker.slot == slot and marker.version == '0.2.4' and marker.candidate_digest == candidate.digest
PY
cmp src/spec_dock/assets/spec_dock/docs/migration.md spec-dock/docs/migration.md
cmp src/spec_dock/assets/spec_dock/docs/README.md spec-dock/docs/README.md
! rg -n 'distribution-journal|compatible newer|current explicit spec-history purge authority|empty spec-dock.*reinitial' README.md src/spec_dock/assets/spec_dock/docs spec-dock/docs
make lint
uv run pytest -q
uv run python -m scripts.quality.verify_full_regression --shards 4
python3 ./spec-dock/scripts/spec-dock validate
uv run python spec-dock/.workbench/iss-00392/admission/compare_protected.py \
  --before spec-dock/.workbench/iss-00392/s60-protected-before.json \
  --root .
fresh="$(mktemp -d)"
uvx --no-cache --from . spec-dock init "$fresh"
python3 "$fresh/spec-dock/scripts/spec-dock" validate
rm -rf "$fresh"
git diff --check
```

The implementation adds an exact protected-after comparison against the S00/S60 snapshot anddeletesonlytheignored snapshot afterreport transcription。Thefresh consumer path iscaptured andremoved。

**Expected observable result**

Alladmitted failures normally pass;transitional ledgeractive0;current PR workflow successor paths exist/GREEN;current main-push verifierGREEN;old engine/testsabsent;docs final;dogfood four roots/two slots/record/markers allmatchS60 candidate;protected witness andseedsunchanged;validate/fresh consumerGREEN。

**Evidence to record in Issue report.md**

Conditional branch/admitted/final mapping、active/resolved counts、deleted/retargeted path table、bothcurrent workflow commands/results、wire golden results、docs grep/parity、dogfood pre/postrecord/marker/root/slot/candidate digests、protected/seed witness、validate/fresh consumer。

**Stop conditions and escalation owner**

Unmappedconditional node、signature drift、active row、workflow missing/deleted path、current verifier failure、S70-only tooling needed、wire mismatch、docs stale、dogfood modified legacy/partial/digest mismatch、protected/seed drift。No merge。Owner:Product/spec/test/CI/filesystem asapplicable。

**Cleanup**

Removeobsolete fixtures/imports/mypy entries andignoredtemp consumers/snapshots afterevidence transcription。Retaincurrent policy infrastructure intentionally。

**PR-B main merge invariant**

S60 is the onlyPR-B gate。S40/S50/S60 all proofGREEN。Main afterhuman merge hascomplete 0.2.4 lifecycle/docs/wire、complete checked-in dogfood candidate、no old engine、active0、working current PR workflow andworking current main-push verifier。No bridge/toggle/finalS70 gate redesign。

**Requirement and design trace IDs**

I392-RQ-018〜020、I392-RQ-027〜029、I392-RQ-031、I392-D-011、I392-D-017〜018、I392-D-020。

## I392-S70 — Consumer-first final gate, receipt graph, second dogfood update, and atomic policy removal

**Objective and contract-visible outcome**

Onone PR-C branch, add the final provider gate/environment/receipt verifier/workflow/AGENTS/docs, retireallold policy consumers, deletetheproviders, thenconvergedogfood tothe newcandidate。S70 isanon-main checkpoint;no authoritative final package isaccepted fromlocal validation。

**Exact owned repository paths and symbols**

Create/update:

```text
scripts/provider_gate.py
ci/linux-qualification.Dockerfile
ci/linux-qualification-environment.json
tests/unit/infra/test_provider_gate.py
tests/unit/infra/test_provider_workflow.py
tests/provider_test_ownership.json
scripts/static_analysis/run.sh
Makefile
.github/workflows/provider-ci.yml
AGENTS.md
README.md test-policy sections
src/spec_dock/assets/spec_dock/docs/README.md test-policy/provider-gate sections
spec-dock/docs/README.md
provider lifecycle code/tests needed bywire and receipts
spec-dock/{docs,templates,system,scripts}
.agents/skills/spec-dock
.agents/skills/spec-dock-grill-with-docs
spec-dock/spec-dock.version
two slot marker files
#392 report.md pre-freeze summary
```

Retire/delete afterconsumer-zero proof:

```text
tests/unit/test_provider_test_lanes.py
tests/unit/test_full_regression_baseline.py
allother imports of tests.conftest or scripts.quality full-regression modules
.github/workflows/provider-full-regression.yml
tests/conftest.py
full-regression-ledger.json
full-regression-timing-weights.json
scripts/quality/full_regression_baseline.py
scripts/quality/verify_full_regression.py
scripts/quality/__init__.py ifempty
fast/full marker declarations/decorators/options
```

**Explicit non-owned and no-touch paths**

Consumer seeds、initiatives/artifacts/workbench/user data、unrelatedskills、human settings、release/tag/PyPI、canonical R/D/P and#387 docs/report。

**Prerequisites and dependency**

PR-C isbased onexactS60 merged tree withworking current gates andcompleteS60 dogfood。No S70 commit isoffered formerge;branch continuestoS80。

**RED evidence**

- Workflow structural tests fail foradditional producer、downstream build、wrong/missing `needs`、receipt name/schema/role、source/job/run/hash/buildcount、zero/multiple evidence upload。
- `verify-downloaded-artifact` table tests cover exits2〜12、stdout/JSON/stderr andsymlink/path/hash/API mismatch。
- Consumer inventory test fails ifanyold policy import/reference remainsbeforeprovider deletion。
- Provider deletion withremaining`test_provider_test_lanes.py` or`test_full_regression_baseline.py` isRED。
- AGENTS/docs stale policy isRED。
- Candidate-wide dogfood update isRED before S70 andonpartial/digest/marker/protected drift。

**Smallest implementation action**

1. Implementprovider gate subcommands includingexactI392-D-013 verifier and receipts。
2. Freezeenvironment descriptor andaddDockerfile limits。
3. Rewritefinalworkflow withI392-D-019 jobs/needs/artifact names/receipt schemas。Only`provider-build-artifacts` packages。
4. Addworkflow structural tests andprovider gate tests;local `build` ispre-freeze tool validation only。
5. UpdateMakefile/static analysis/root AGENTS/root README test policy/provider docs test policy。
6. Replace/retireeveryremaining policy consumer, explicitly`test_provider_test_lanes.py` and`test_full_regression_baseline.py`;verifyconsumer0。
7. Deleteoldproviders/ledger/timing/sharder/workflow/markers inthesame branch;runfull collection/tests。
8. Afterallcandidate bytes settle, snapshotprotected witness andrun`uvx --no-cache --from . spec-dock update .`。
9. Verifyfour roots/two slots/seven-key record/two markers equalthe S70 candidate digest andprotected/seedsunchanged。
10. Complete tracked report pre-freeze summary andcommitall tracked content。Do notstartS80 untilclean。

**Focused verification commands**

```bash
uv run pytest -q tests/unit/infra/test_provider_gate.py tests/unit/infra/test_provider_workflow.py
uv run python scripts/provider_gate.py freeze-linux-environment   --descriptor ci/linux-qualification-environment.json   --dockerfile ci/linux-qualification.Dockerfile
# Pre-freeze tool validation only; output is notacceptance evidence.
uv run python scripts/provider_gate.py build   --source-sha "$(git rev-parse HEAD)"   --out spec-dock/.workbench/provider-gate/pre-freeze
uv run python scripts/provider_gate.py verify-environment   --descriptor ci/linux-qualification-environment.json
uv run python scripts/provider_gate.py verify-node-ownership   --map tests/provider_test_ownership.json
! rg -n 'tests\.conftest|scripts\.quality\.full_regression_baseline|scripts\.quality\.verify_full_regression|--run-full-regression|--full-regression-shard|POLICY_SKIP_REASON|full-regression-ledger|full-regression-timing'   --glob '!spec-dock/initiatives/**' .
test ! -e tests/unit/test_provider_test_lanes.py
test ! -e tests/unit/test_full_regression_baseline.py
test ! -e tests/conftest.py
test ! -e .github/workflows/provider-full-regression.yml
uv run pytest --collect-only -q
uv run pytest -q
make lint
uvx --no-cache --from . spec-dock update .
uv run python - <<'PY'
from pathlib import Path
from spec_dock.provider_lifecycle.candidate import build_packaged_candidate
from spec_dock.provider_lifecycle.model import parse_install_record, parse_slot_marker
candidate=build_packaged_candidate(Path('src/spec_dock/assets'),'0.2.4')
record=parse_install_record(Path('spec-dock/spec-dock.version').read_bytes())
assert record.state.value=='ready' and record.operation is None
assert record.candidate_digest==candidate.digest and record.seed_policy.value=='preserve-only'
for slot in ('spec-dock','spec-dock-grill-with-docs'):
    marker=parse_slot_marker(Path('.agents/skills')/slot/'.spec-dock-provider-slot.json')
    assert marker.candidate_digest==candidate.digest
PY
python3 ./spec-dock/scripts/spec-dock validate
uv run python spec-dock/.workbench/iss-00392/admission/compare_protected.py \
  --before spec-dock/.workbench/iss-00392/admission/protected-baseline.json \
  --root .
fresh="$(mktemp -d)"
uvx --no-cache --from . spec-dock init "$fresh"
python3 "$fresh/spec-dock/scripts/spec-dock" validate
rm -rf "$fresh"
grep -F 'make provider-test' AGENTS.md
grep -F 'make provider-qualify' AGENTS.md
git diff --check
```

Aseparate exact protected-before/after digest comparison andfresh consumer from current S70 source aremandatory andrecorded。Local pre-freeze artifacts aredeleted beforehead freeze。

**Expected observable result**

Final tooling/workflow structural testsGREEN、sole producer enforced、verifier exits/goldensGREEN、allold policy consumers/providersabsent、full suiteGREEN、AGENTS/docsfinal、S70dogfood complete/new digest/protectedunchanged、tracked tree clean aftercommit。No authoritative final package yet。

**Evidence to record in Issue report.md**

Consumer inventory/removal、workflow needs/artifact graph、verifier table results、environment descriptor、local tool-validation disclaimer、old machinery absence、AGENTS/docs grep、S60->S70 candidate/dogfood digest transition、protected/seed witness、validate/fresh consumer、finaltracked commit readiness。

**Stop conditions and escalation owner**

Anyremaining consumer、wrong workflow needs/receipt/upload、more thanonepackager、verifier catch-all、environment mismatch、old machinery reference、AGENTS/docsstale、dogfood partial/digest/marker/protected drift、tracked tree notclean。No merge;fixsame#392。Owner:CI/Product/spec/filesystem。

**Cleanup**

Removepre-freeze builds、temporary consumers/witnesses afterreport summary。Keeptracked descriptor/tests/docs/dogfood final state。NoS70-only handoff。

**Internal checkpoint invariant**

S70 is not amain merge point。PR-C branch itself hasworking replacement gate andcomplete dogfood butmustcontinue toS80 frozen-head workflow proof/context/attestation。Main remainsatworkingS60 state untilhuman PR-C merge。

**Requirement and design trace IDs**

I392-RQ-021〜023、I392-RQ-026、I392-RQ-028、I392-RQ-030〜031、I392-D-012〜013、I392-D-017、I392-D-019〜020。

## I392-S80 — Frozen-head Provider CI receipts, downloaded verification, context transition, and PR-C gate

**Objective and contract-visible outcome**

FreezeS70 tracked head/tree, dispatchtheauthoritative Provider CI run, consumeonlydownloaded candidate/evidence bytes, verifythe exactreceipt graph, completequalification/required-context transition/external attestation, andproducePR-C merge handoff。S80 ownsno tracked path andperformsnolocal build、dogfood update orsync。

**Exact owned repository paths and symbols**

Tracked paths: none。

Ignored/external only:

```text
spec-dock/.workbench/provider-gate/final-run/**
GitHub Actions run/job/artifact API snapshots
provider-candidate-<sha> download
provider-evidence-<sha> download
pre-merge-attestation-v1 external object
required-context before/both/final snapshots
```

Anyrequired tracked correction returns toS70, createsanewhead andinvalidatesallS80 evidence。

**Explicit non-owned and no-touch paths**

Alltracked code/tests/docs/specs/report/dogfood after freeze、consumer seeds/user data、settings excepthuman-admin transition、release。

**Prerequisites and dependency**

S70 branchGREEN、tracked report finalized/committed、completeS70 dogfood digest verified、workingtreeclean、human adminavailable、dedicatedcanary allowed butnevermerged。

**RED evidence**

- Workflow tests rejectmissing/duplicateproducer、wrong `needs`、consumer build、receipt/upload/name/schema/hash/source/run/job/buildcount。
- `verify-downloaded-artifact` rejectsalltyped fail cases/exits2〜12 andnon-exactstdout/JSON。
- Qualification rejects environment/fingerprint/budget/CPU/fault/flake/retry mismatch。
- Context state machine rejectsold removal beforenew-required RED proof。
- Head/tree/tracked write、local build、`spec-dock update`、`spec-dock sync` invalidateS80。

**Smallest implementation action**

1. Confirmclean;freeze`VERIFIED_PR_HEAD`/`VERIFIED_PR_TREE`/branch。No furthertracked writes。
2. Runread-only lint/collection/tests/docs/dogfood record/marker/digest/validate checks。Failure returnsS70。
3. Snapshotexisting workflow-dispatch run IDs。
4. Dispatch`provider-ci.yml` onfrozenbranch with`candidate_sha=<head>` and`qualification=true`。
5. Selectexactly one newrun matchinghead/input;waitterminal success;fetchrun/jobs/artifact metadata。
6. Requireexact job/needs graph fromI392-D-019 andexact oneofeachartifact name。
7. Download`provider-candidate-<sha>` and`provider-evidence-<sha>` only;theevidence artifact containsfour verified receipts。
8. RunexactI392-D-013 command ondownloaded files。Itmustreturnexit0/code`downloaded-artifact-verified` andproveproducer1/consumers0/same bytes。
9. VerifyLinux20-run environment/budget/CPU/fault/flake、sdist smoke、macOS delta fromreceipts。
10. Human keepsold required, addsnew required andread-backsboth;dedicatednon-mergecanary makesnew gateRED andprovesblock;closecanary;implementationheadGREEN;thenremove oldprovider-only/read-backfinal。
11. Emitcontent-addressed`pre-merge-attestation-v1` from downloaded evidence/API snapshots;postnewnever-editedobject。
12. Reconfirmhead/tree/status unchanged and dogfood record/markers stillmatchfrozen candidate receipt。

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
# No uv build, provider_gate.py build, spec-dock update, or spec-dock sync ispermitted in S80.
gh run list --workflow provider-ci.yml --branch "$PR_BRANCH" --event workflow_dispatch --limit 100   --json databaseId --jq '.[].databaseId' > spec-dock/.workbench/provider-gate/final-run/before-run-ids.txt
gh workflow run provider-ci.yml --ref "$PR_BRANCH"   -f candidate_sha="$VERIFIED_PR_HEAD"   -f qualification=true
# Poll API until exactly one newrun matchesfrozen head; zero/multiple ishard stop.
gh run watch "$RUN_ID" --exit-status
gh run view "$RUN_ID" --json databaseId,headSha,status,conclusion,jobs   > spec-dock/.workbench/provider-gate/final-run/run.json
gh api "repos/$REPO/actions/runs/$RUN_ID/artifacts"   > spec-dock/.workbench/provider-gate/final-run/artifacts.json
test "$(jq --arg n "provider-candidate-$VERIFIED_PR_HEAD" '[.artifacts[]|select(.name==$n)]|length' spec-dock/.workbench/provider-gate/final-run/artifacts.json)" = 1
test "$(jq --arg n "provider-evidence-$VERIFIED_PR_HEAD" '[.artifacts[]|select(.name==$n)]|length' spec-dock/.workbench/provider-gate/final-run/artifacts.json)" = 1
gh run download "$RUN_ID" -n "provider-candidate-$VERIFIED_PR_HEAD"   -D spec-dock/.workbench/provider-gate/final-run/candidate
gh run download "$RUN_ID" -n "provider-evidence-$VERIFIED_PR_HEAD"   -D spec-dock/.workbench/provider-gate/final-run/evidence
uv run python scripts/provider_gate.py verify-downloaded-artifact   --repository chemitaro/spec-dock   --candidate-dir spec-dock/.workbench/provider-gate/final-run/candidate   --evidence-dir spec-dock/.workbench/provider-gate/final-run/evidence   --run-json spec-dock/.workbench/provider-gate/final-run/run.json   --artifacts-json spec-dock/.workbench/provider-gate/final-run/artifacts.json   --source-sha "$VERIFIED_PR_HEAD"   --source-tree "$VERIFIED_PR_TREE"   --workflow-run-id "$RUN_ID"   --json > spec-dock/.workbench/provider-gate/final-run/download-verification.json
jq -e '.status=="verified" and .code=="downloaded-artifact-verified"'   spec-dock/.workbench/provider-gate/final-run/download-verification.json
uv run python scripts/provider_gate.py emit-attestation   --type pre-merge-attestation-v1   --source-sha "$VERIFIED_PR_HEAD"   --workflow-run-id "$RUN_ID"   --input spec-dock/.workbench/provider-gate/final-run/evidence   --output spec-dock/.workbench/provider-gate/final-run/pre-merge-attestation.json
test "$(git rev-parse HEAD)" = "$VERIFIED_PR_HEAD"
test "$(git rev-parse 'HEAD^{tree}')" = "$VERIFIED_PR_TREE"
test -z "$(git status --short)"
```

The run selector additionally verifiesdispatch input`candidate_sha` fromproducer receipt。Run/jobs exact names、IDs、needs andallreceipt fields arechecked bytheverifier, not manually assumed。

**Expected observable result**

Onefrozenhead、oneLinux packaging invocation、sameimmutablewheel/sdist inalljobs、consumer build0、fourvalidreceipts、exactoneprovider-evidence upload、stable20-runqualification、macOS/sdistGREEN、dogfood digest equalsreceipt candidate、new required beforeRED、canaryblocked、implementationGREEN、oldremovedafterproof、externalattestationhashverified、trackedhead/treeclean。

**Evidence to record**

Tracked report receivesnothing after freeze。External attestation containshead/tree/report blob、run/job/needs、Actions artifact IDs/names/digests、manifest/files、fourreceipts、producer1/consumer0、environment/runs/faults/macOS/sdist、dogfood record/markers/digest、required snapshots、commands/conclusions。

**Stop conditions and escalation owner**

Anytracked edit、localfinalbuild/update/sync、zero/multiplerun、wrong head/tree/needs/artifact/receipt、producer!=1、consumer!=0、hash mismatch、environment/budget/fault/flake/dogfood/context/attestation mismatch。ReturnS70/newhead andrerun all source-bound evidence。Owners:CI/Product/spec;settings:human admin。

**Cleanup**

Closecanarywithoutmerge。KeepimmutableGitHubevidence;localignoreddownloads mayberemoved afterattestation verification。Do notmodifytracked tree。

**PR-C main merge invariant**

S80 is the onlyPR-C gate。S70 replacement/consumer closure/dogfood andS80 authoritativeworkflow receipts/context/attestation/human review all GREEN。Main afterhuman merge hascompletefinal lifecycle/docs/wire/register/dogfood、final build-once gate、no oldmachinery、finalAGENTS。Agentdoes notmerge。

**Requirement and design trace IDs**

I392-RQ-021〜031、I392-D-012〜020。
## 4. Human merge and external closure protocol

### Pre-merge handoff

External pre-merge attestation providesPR URL、head SHA/tree OID、report blob OID、artifact/environment/test/context hashes。Tracked report does notself-reference。

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

All I392-RQ-001〜031 verified。S30/S60/S80 areonly main merge gates。Machine-readable owner decision list remains`[]`。
