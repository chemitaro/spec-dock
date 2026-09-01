---
種別: 実装計画書（Issue）
ID: "iss-00392"
タイトル: "Provider Lifecycle And Regression Gate Hard Cutover"
関連GitHub: ["#392"]
状態: "draft"
最終更新: "2026-09-01"
依存: ["requirement.md", "design.md", "../../plan.md", "../../artifacts/20260831t152024z-adr-single-implementation-unit-and-provider-hard-cutover-policy.md", "../../artifacts/provider-lifecycle-wire-contract.md", "../../artifacts/active-failure-disposition-register.md"]
親: ["epic-00384", "init-local-00003"]
Planning Level: "critical"
repository_evidence:
  repository: "chemitaro/spec-dock"
  branch: "codex/epic-00384-provider-test-strategy-planning"
  sha: "d145f0f0d6f35535eebc0da89b7b708824279f1f"
---

# iss-00392 Provider Lifecycle And Regression Gate Hard Cutover — 実装計画

## 1. Execution rules

1. This Plan is the entry point; Requirement and Design plus both normative Artifacts are binding.
2. Production source of truth is `src/spec_dock/`; provider-first precedes dogfood convergence.
3. Behavior changes are test-first. Existing RED may be reused only with exact node/evidence.
4. S40、S50、S70 are non-main checkpoints. Only S30、S60、S80 are main merge gates.
5. S40/S50 preserve checked-in legacy dogfood exactly; S60 performs the first complete migration; S70 performs the second complete update; S80 is read-only.
6. Repository `spec-dock/.workbench` is protected read-only. All temporary data uses the external workspace contract below.
7. S60 keeps current gates coherent and never invokes S70-only tooling. S70 replaces consumers before deleting providers.
8. Tracked report contains pre-freeze facts only. Final and post-merge facts remain external.
9. Agent does not merge、change required settings、start/finish/close #392、or create another Issue.
10. Any stop is forward-fixed in #392 without bridge、toggle、waiver、skip、old fallback or new Issue.

## 2. Common no-touch boundary

- Issue #387 canonical R/D/P and tracked report content.
- `spec-dock/initiatives/**` except #392 report and authorized generated lifecycle metadata.
- Complete `spec-dock/.workbench` tree.
- Consumer seeds `spec-dock/.gitignore` and root `.github/workflows/ci.yml`.
- Unrelated skills、unknown user data、Issue #372 evidence、human settings、release/tag/PyPI.
- Canonical Epic/Issue R/D/P during implementation.

## 3. External temporary workspace contract

All steps requiring temporary bytes create one purpose-bound directory outside repository. Allowed purposes are exactly those in I392-D-016. Portable shell/Python setup:

```bash
export REPOSITORY_REALPATH="$(python3 -c 'from pathlib import Path; print(Path(".").resolve(strict=True))')"
export ISS392_PURPOSE="s00-admission"
export ISS392_EXTERNAL_TMP="$(python3 - "$REPOSITORY_REALPATH" "$ISS392_PURPOSE" <<'PY_TMP'
from pathlib import Path
import hashlib, json, os, secrets, stat, sys, tempfile
repo=Path(sys.argv[1]); purpose=sys.argv[2]
allowed={
 's00-admission','s50-artifact-proof','s60-dogfood-witness','s70-pre-freeze',
 's70-dogfood-witness','s80-final-run','provider-build-artifacts',
 'provider-linux-canonical','provider-sdist-smoke','provider-macos-delta',
 'provider-attestation','post-merge-closure'
}
if purpose not in allowed: raise SystemExit('purpose-not-allowed')
base=Path(os.environ.get('SPEC_DOCK_EXTERNAL_TMPDIR', tempfile.gettempdir()))
st=os.lstat(base)
if stat.S_ISLNK(st.st_mode) or not stat.S_ISDIR(st.st_mode): raise SystemExit('unsafe-temp-base')
base=base.resolve(strict=True); repo=repo.resolve(strict=True)
if os.path.commonpath([str(base),str(repo)]) == str(repo): raise SystemExit('temp-inside-repository')
path=Path(tempfile.mkdtemp(prefix=f'spec-dock-iss-00392-{purpose}-',dir=base))
os.chmod(path,0o700)
fd=os.open(path,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC)
try:
 a=os.lstat(path); b=os.fstat(fd)
 if (a.st_dev,a.st_ino)!=(b.st_dev,b.st_ino) or a.st_uid!=os.geteuid() or stat.S_IMODE(a.st_mode)!=0o700:
  raise SystemExit('unsafe-temp-identity')
 sentinel={
  'schema_version':1,'kind':'spec-dock-iss-00392-external-workspace','purpose':purpose,
  'repository_realpath_sha256':hashlib.sha256(os.fsencode(repo)).hexdigest(),
  'repository_device':os.stat(repo).st_dev,'repository_inode':os.stat(repo).st_ino,
  'workspace_device':a.st_dev,'workspace_inode':a.st_ino,'effective_uid':os.geteuid(),
  'nonce':secrets.token_hex(32)
 }
 raw=(json.dumps(sentinel,separators=(',',':'))+'\n').encode()
 sfd=os.open('.spec-dock-iss-00392-owner.json',os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600,dir_fd=fd)
 try: os.write(sfd,raw); os.fsync(sfd)
 finally: os.close(sfd)
 os.fsync(fd)
 print(path)
finally: os.close(fd)
PY_TMP
)"
case "$ISS392_EXTERNAL_TMP" in "$REPOSITORY_REALPATH"|"$REPOSITORY_REALPATH"/*) exit 97;; esac
```

Cleanup uses a committed helper implementing I392-D-017 or an exact audited equivalent. It never `rm -rf`s an unverified path. It reopens nofollow、checks realpath/device/inode/mode/uid/sentinel/nonce、rejects symlink/hardlink/special/foreign entries、removes all-or-nothing and verifies absence. If unsafe, leave the directory untouched and report stop.

## 4. Step graph

```text
S00 admission
 -> PR-A: S10 -> S20 -> S30 main gate
 -> PR-B: S40 internal -> S50 internal -> S60 main gate
 -> PR-C: S70 internal -> S80 main gate
 -> human merge -> external closure
```

## I392-S00 — Specification, #387, source ledger, protected data and legacy dogfood admission

**Stable ID**: `I392-S00`.

**Objective and contract-visible outcome**

Prove specification lineage and independently prove #387 human merge identity/tree, apply register v3, establish formula-derived admitted failures, baseline old artifacts, complete protected witness, and exact checked-in legacy dogfood before any production change.

**Exact owned repository paths and symbols**

Tracked: #392 `report.md` pre-merge admission summary only. Read-only: repository/GitHub. External purpose: `s00-admission`. No production symbol change.

**Explicit non-owned and no-touch paths**

All production/test/workflow/dogfood paths、all Issue #387 files、and repository `.workbench`.

**Prerequisites and dependency**

Pack imported and `SPEC_FREEZE_COMMIT` recorded; #387 human merge completed; implementation base contains both; clean tree; external workspace safely created.

**RED evidence or justified no-new-test rule**

Temporary external checker must reject wrong spec hash、pre-merge report with forbidden merge fields、PR/head/tree mismatch、nonhuman/unmerged PR、merge-tree inequality、invalid remove/retain/split、signature drift、unmapped row、ambiguous lineage、contract-external delta、nonexact legacy dogfood、or any attempted witness output under repository.

**Smallest implementation action**

1. Verify 11 payload hashes at `SPEC_FREEZE_COMMIT` and ancestry.
2. Parse #387 tracked report candidate/mapping without modifying it.
3. Fetch #387 PR/merge objects and independently verify head/tree/merge/tree equality/main ancestry.
4. Parse source ledger 27 identities and post-merge ledger/collection; apply `ISS387-THREE-WAY-V2`; emit external schema-v2 admission.
5. Build one baseline `0.2.3` wheel/sdist in external workspace for legacy fixture only.
6. Capture complete protected witness externally, including full `.workbench` tree.
7. Assert checked-in record bytes `0.2.3\n` and both fixed slots markerless.
8. Run current lint/ordinary/current full/validate gates.

**Focused verification commands**

```bash
test -z "$(git status --short)"
git merge-base --is-ancestor "$SPEC_FREEZE_COMMIT" "$IMPLEMENTATION_BASE_SHA"
# Fetch PR and merge JSON into "$ISS392_EXTERNAL_TMP/api" and verify register schema v3.
uv run python "$ISS392_EXTERNAL_TMP/check_admission.py" \
  --register "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00384-provider-test-strategy-simplification-and-execution-cost-reduction/artifacts/active-failure-disposition-register.md" \
  --issue-387-report "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00356-specdock-core-simplification-and-external-intelligence-boundary/issues/iss-00387-current-surface-workflow-residue-cleanup/report.md" \
  --pull-request-json "$ISS392_EXTERNAL_TMP/api/pull-request.json" \
  --merge-json "$ISS392_EXTERNAL_TMP/api/merge.json" \
  --ledger full-regression-ledger.json \
  --collection "$ISS392_EXTERNAL_TMP/full-collection.txt" \
  --output "$ISS392_EXTERNAL_TMP/post-387-admission.json"
python3 - <<'PY_DOGFOOD'
from pathlib import Path
assert Path('spec-dock/spec-dock.version').read_bytes() == b'0.2.3\n'
for p in [Path('.agents/skills/spec-dock/.spec-dock-provider-slot.json'),Path('.agents/skills/spec-dock-grill-with-docs/.spec-dock-provider-slot.json')]:
    assert not p.exists() and not p.is_symlink()
PY_DOGFOOD
uv build --sdist --wheel --out-dir "$ISS392_EXTERNAL_TMP/baseline-dist"
make lint
uv run pytest -q
uv run python -m scripts.quality.verify_full_regression --shards 4
python3 ./spec-dock/scripts/spec-dock validate
git diff --check
test -z "$(git status --short)"
```

**Expected observable result**

Exact spec/#387 identities and tree equality; no fixed row count; all rows mapped; current gates GREEN; baseline hashes fixed; complete protected witness external; exact legacy dogfood unchanged.

**Evidence to record in Issue report.md**

Manifest/SPEC_FREEZE、#387 candidate/PR/merge/tree/report/ledger/collection identities、admission formula/result、baseline artifact hashes、protected witness hash、dogfood record/slot/root identities、commands/exits. Do not record report own hash or future final head.

**Stop conditions and escalation owner**

Any identity/mapping/signature/tree/protected/legacy/gate mismatch stops before S10; canonical spec owner and independent Strict re-review. Luna does not choose a branch repair.

**Cleanup**

Safely clean external workspace only after required report summary; unsafe cleanup is a stop. No repository temp cleanup exists.

**Merge-point invariant**

No code diff; not a merge point.

**Requirement and design trace IDs**

RQ-001–006、017、D-013–018.

## I392-S10 — Fixed model, candidate, record, marker and closed wire

**Stable ID**: `I392-S10`.

**Objective and contract-visible outcome**

Create dormant pure model/candidate/legacy components and table-driven wire contract tests without public routing.

**Exact owned repository paths and symbols**

```text
src/spec_dock/provider_lifecycle/{__init__,model,candidate,legacy_023}.py
src/spec_dock/assets/legacy_0_2_3.json
tests/unit/infra/test_provider_lifecycle_{model,candidate,wire_contract}.py
tests/unit/infra/test_provider_assets.py
```

**Explicit non-owned and no-touch paths**

CLI、old engine、workflows、all dogfood targets/record/markers、`.workbench`.

**Prerequisites and dependency**

S00 GREEN and exact external baseline fixture hashes.

**RED evidence or justified no-new-test rule**

Tests fail for every unimplemented seven-key relation、unknown enum、all 116 wire rows、wrong phase pair、candidate unsafe kind、legacy mismatch、array order and compact golden.

**Smallest implementation action**

Implement frozen dataclasses/enums/parsers/digest/legacy reader and wire table constants. No mutation or public route.

**Focused verification commands**

```bash
uv run pytest -q tests/unit/infra/test_provider_lifecycle_model.py \
  tests/unit/infra/test_provider_lifecycle_candidate.py \
  tests/unit/infra/test_provider_lifecycle_wire_contract.py \
  tests/unit/infra/test_provider_assets.py
uv run ruff check src/spec_dock/provider_lifecycle tests/unit/infra/test_provider_lifecycle_wire_contract.py
uv run mypy src/spec_dock/provider_lifecycle
```

**Expected observable result**

Pure tests GREEN; all 36 codes/116 rows enumerable; public product and dogfood unchanged.

**Evidence to record in Issue report.md**

RED/GREEN nodes、enum/table counts、golden hashes、legacy fixture source hash.

**Stop conditions and escalation owner**

Need arbitrary path、new enum/reason、history catalog、progress field or unspecified wire relation: stop to spec/Product owner.

**Cleanup**

External test temp only; no generated marker in assets.

**Merge-point invariant**

Internal PR-A checkpoint; public old product remains.

**Requirement and design trace IDs**

RQ-007–010、020、D-001–004、D-012.

## I392-S20 — Descriptor-bound filesystem, external stage, fresh bootstrap and install

**Stable ID**: `I392-S20`.

**Objective and contract-visible outcome**

Complete direct-service fresh install with safe shared-container bootstrap and exact fault behavior.

**Exact owned repository paths and symbols**

```text
src/spec_dock/provider_lifecycle/{filesystem,service}.py
tests/unit/infra/test_provider_lifecycle_{filesystem,service,faults,external_workspace}.py
```

**Explicit non-owned and no-touch paths**

Public CLI、old engine/workflows、checked-in dogfood and all protected data.

**Prerequisites and dependency**

S10 GREEN; native primitives positively probed; external test temp outside repository.

**RED evidence or justified no-new-test rule**

Absent/existing container、unknown child、symlink/non-dir、absence race、failure before/after mkdir/owner/record、exact empty cleanup、cleanup failure resume、seed policy faults、root/slot/seed/ready boundaries、native/no-follow/hardlink failures. External workspace tests cover base collision、inside-repo、symlink、sentinel tamper、hardlink/special/foreign entry and conservative cleanup.

**Smallest implementation action**

Implement lock/bind、stage owner、container bootstrap/cleanup、native rename、atomic record/root/slot/seed publication and direct fresh install.

**Focused verification commands**

```bash
uv run pytest -q tests/unit/infra/test_provider_lifecycle_filesystem.py \
  tests/unit/infra/test_provider_lifecycle_service.py \
  tests/unit/infra/test_provider_lifecycle_faults.py \
  tests/unit/infra/test_provider_lifecycle_external_workspace.py
make lint
```

**Expected observable result**

Direct fresh install converges; exact wire result at every fault; no protected/repository temp mutation.

**Evidence to record in Issue report.md**

Mutation timeline、bootstrap identity/cleanup matrix、external workspace matrix、policy/fault table、native probes.

**Stop conditions and escalation owner**

Generic rename/mkdir fallback、recursive shared-container cleanup、repository temp requirement、or policy inference: Product/filesystem safety owner.

**Cleanup**

Only verified external/test directories by owner-bound cleanup.

**Merge-point invariant**

Internal PR-A checkpoint; public route unchanged.

**Requirement and design trace IDs**

RQ-004–016、D-004–011、D-016–018.

## I392-S30 — Update/resume convergence and PR-A main gate

**Stable ID**: `I392-S30`.

**Objective and contract-visible outcome**

Complete ready update、missing repair、same-tuple resume and cross-tuple block while keeping new code dormant.

**Exact owned repository paths and symbols**

S10/S20 modules/tests; `update_tooling`、`resume_incomplete` and state/policy transition table.

**Explicit non-owned and no-touch paths**

CLI、old engine、workflows、dogfood.

**Prerequisites and dependency**

S20 GREEN.

**RED evidence or justified no-new-test rule**

Whole-root replacement、missing repair、marker mismatch、all partial boundaries、same tuple convergence、policy/candidate/operation mismatch、ready fresh provenance then preserve update、cleanup warning and binding race.

**Smallest implementation action**

Add update/resume orchestration using the same observation/publication primitives; no rollback/progress list.

**Focused verification commands**

```bash
uv run pytest -q tests/unit/infra/test_provider_lifecycle_*.py
make lint
uv run pytest -q
uv run python -m scripts.quality.verify_full_regression --shards 4
```

**Expected observable result**

Dormant successor complete; current gates GREEN; public/dogfood unchanged.

**Evidence to record in Issue report.md**

Fault/convergence and policy transition tables、current gate results.

**Stop conditions and escalation owner**

Need public toggle、old fallback、checkpoint list or dogfood mutation: Product owner.

**Cleanup**

Verified external test temp only.

**Merge-point invariant**

Only PR-A main gate. Main remains old public product plus dormant successor and coherent current workflows.

**Requirement and design trace IDs**

RQ-013、016、D-008–012.

## I392-S40 — Public uninstall/wire/docs cutover while preserving exact legacy dogfood

**Stable ID**: `I392-S40`.

**Objective and contract-visible outcome**

On PR-B branch, connect final lifecycle CLI、tooling-only uninstall、purge trap、wire results and provider-side lifecycle documentation, while preserving checked-in dogfood byte-for-byte.

**Exact owned repository paths and symbols**

```text
pyproject.toml
src/spec_dock/cli.py
src/spec_dock/provider_lifecycle/{model,service,public_result}.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/uninstall.py
README.md lifecycle sections
src/spec_dock/assets/spec_dock/docs/migration.md
src/spec_dock/assets/spec_dock/docs/README.md lifecycle sections
tests/unit/infra/test_provider_lifecycle_{wire_contract,public_result}.py
tests/cli_runtime/test_{provider_lifecycle,uninstall,update}.py
```

**Explicit non-owned and no-touch paths**

Every checked-in dogfood root `spec-dock/{docs,templates,system,scripts}`、both root skill slots、`spec-dock/spec-dock.version`、both markers、root AGENTS、current test-policy text/workflows、all protected data. No provider-doc projection sync in S40.

**Prerequisites and dependency**

S30 GREEN; external complete witness of all dogfood owned/protected paths; S40 starts same PR-B that must continue through S60.

**RED evidence or justified no-new-test rule**

Old uninstall/purge tests RED; wire 116-row/goldens RED; provider docs grep finds old journal/retry/purge/empty-boundary semantics; dogfood before/after witness must reject any changed byte/type/mode/link target.

**Smallest implementation action**

Implement exact result adapter and public dispatch、version0.2.4、remove purge route、update shipped wrapper source、root README lifecycle and provider lifecycle docs. Do not copy/sync any dogfood target.

**Focused verification commands**

```bash
uv run pytest -q tests/unit/infra/test_provider_lifecycle_wire_contract.py \
  tests/unit/infra/test_provider_lifecycle_public_result.py
uv run pytest --run-full-regression --full-regression-shard -q \
  tests/cli_runtime/test_provider_lifecycle.py \
  tests/cli_runtime/test_uninstall.py tests/cli_runtime/test_update.py
# Compare exact external S40 before/after dogfood witness; no repository output.
make lint
git diff --check
```

**Expected observable result**

Final public route/wire/provider docs GREEN; exact legacy dogfood remains plain0.2.3 and markerless; no dogfood diff.

**Evidence to record in Issue report.md**

CLI/wire rows/goldens、provider docs hashes/grep、external dogfood witness equality.

**Stop conditions and escalation owner**

Any dogfood edit/sync、wire choice、bridge/toggle、purge mutation、or S40 merge handoff: block PR-B; Product/spec owner.

**Cleanup**

Safely clean external witness workspace after report summary.

**Internal checkpoint invariant**

Not a main merge point; same branch continues S50/S60. Checked-in dogfood stays exact legacy.

**Requirement and design trace IDs**

RQ-019–022、D-012、D-019、D-021.

## I392-S50 — Exact legacy/tripwire proof on external synthetic consumers

**Stable ID**: `I392-S50`.

**Objective and contract-visible outcome**

Prove exact migration/uninstall and old-package mutation-zero without touching checked-in dogfood.

**Exact owned repository paths and symbols**

```text
src/spec_dock/provider_lifecycle/{legacy_023,service}.py
tests/integration/test_provider_lifecycle_{artifacts,tripwire}.py
tests/platform/macos/test_provider_lifecycle_macos.py
tests/support/provider_lifecycle_tripwire/{sitecustomize,native_positive_control}.py
```

External purpose: `s50-artifact-proof`.

**Explicit non-owned and no-touch paths**

All checked-in dogfood roots/slots/record/markers、current gates、consumer data/seeds.

**Prerequisites and dependency**

S40 branch GREEN; S00 old artifact available or rebuilt from exact baseline identity in external temp; no main handoff.

**RED evidence or justified no-new-test rule**

Exact/modified root/slot/recovery matrix、preserve-only fault resume、tripwire startup、Python/native positive controls、old command event0 and checked-in dogfood external witness equality.

**Smallest implementation action**

Complete legacy adapter and tripwire harness using only external synthetic workspaces. If an old mutation occurs, repair record/marker admission; do not bridge.

**Focused verification commands**

```bash
uv build --sdist --wheel --out-dir "$ISS392_EXTERNAL_TMP/final-artifacts"
uv run pytest --run-full-regression --full-regression-shard -q \
  tests/integration/test_provider_lifecycle_artifacts.py \
  tests/integration/test_provider_lifecycle_tripwire.py
# macOS runner executes tests/platform/macos/test_provider_lifecycle_macos.py.
```

**Expected observable result**

Exact legacy synthetic migration/uninstall GREEN; old event0/tree unchanged; controls intercepted; checked-in dogfood still exact legacy.

**Evidence to record in Issue report.md**

Old/final artifact hashes、migration/fault matrix、tripwire events/native controls、dogfood witness equality.

**Stop conditions and escalation owner**

Old mutation、control failure、checked-in dogfood drift、policy change、unsupported fallback or S50 merge handoff: Product/safety owner.

**Cleanup**

Owner-bound external cleanup only.

**Internal checkpoint invariant**

Not a main merge point; same PR-B continues S60; dogfood unchanged.

**Requirement and design trace IDs**

RQ-017–018、021、D-019.

## I392-S60 — Terminalization, transitional workflows, lifecycle docs/AGENTS, complete dogfood migration and PR-B gate

**Stable ID**: `I392-S60`.

**Objective and contract-visible outcome**

Remove old lifecycle engine/tests after successor proof、mechanically terminalize admitted failures、keep current PR/main-push workflows independently GREEN、finish lifecycle docs and AGENTS lifecycle sections、and perform the one complete checked-in legacy dogfood migration. This is the only PR-B main gate.

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
src/spec_dock/provider_lifecycle/**
.github/workflows/provider-ci.yml
tests/unit/test_provider_test_lanes.py
tests/unit/infra/test_provider_assets.py
tests/provider_test_ownership.json
full-regression-ledger.json
full-regression-timing-weights.json
tests/conftest.py
exact failure-owner tests from external post-387-admission.json
README.md lifecycle sections
AGENTS.md lifecycle/uninstall sections only
src/spec_dock/assets/spec_dock/docs/{migration,README}.md
spec-dock/{docs,templates,system,scripts}/**
.agents/skills/spec-dock/**
.agents/skills/spec-dock-grill-with-docs/**
spec-dock/spec-dock.version
two .spec-dock-provider-slot.json files
#392 report.md pre-merge summary
```

Retain through S70: quality full-regression modules、main-push workflow、current markers/options and AGENTS test-policy/provider-gate sections.

**Explicit non-owned and no-touch paths**

#387 files、S70 final gate/environment/test-policy redesign、seeds、all initiatives/artifacts/complete `.workbench`/unknown user data、settings/release.

**Prerequisites and dependency**

S50 GREEN; valid external post-387 admission; exact checked-in dogfood still legacy/markerless; S40/S50 same branch; external purposes `s60-dogfood-witness` and fresh consumer safely created.

**RED evidence or justified no-new-test rule**

Transitional workflow RED while old deleted paths remain; lane test RED for wrong formula/active/stale mapping; current verifier RED for dangling rows; AGENTS lifecycle RED while removed purge is described as destructive; dogfood RED before complete migration or any partial/digest/marker/protected mismatch; wire/docs tests RED for stale semantics.

**Smallest implementation action**

1. Extract surviving context behavior and move asset assertions.
2. Apply external admission exactly; fix admitted active nodes or registered supersession; active0/approved0.
3. Update ledger/timing/conftest exact references and lane test.
4. Delete old engine/manifest/tests.
5. Retarget current `provider-ci.yml` only from deleted tests to existing model/candidate/filesystem/service/result、CLI、artifact/tripwire、and macOS successors; preserve workflow topology; no final gate tooling.
6. Finish root README/provider lifecycle docs; update AGENTS lifecycle/uninstall paragraphs only.
7. Capture external complete protected and complete dogfood witnesses.
8. Execute `uvx --no-cache --from . spec-dock update .` exactly once; this migrates exact legacy with preserve-only.
9. Verify four roots、two slots、seven-key ready record、two markers and candidate digest; provider/dogfood parity; no stage/incomplete residue.
10. Compare full protected witness including `.workbench`; verify seed hashes; validate and fresh consumer.
11. Run current PR-equivalent suite and current 4-shard verifier independently.

**Focused verification commands**

```bash
uv run pytest -q tests/unit/test_provider_test_lanes.py \
  tests/unit/infra/test_provider_assets.py \
  tests/unit/infra/test_provider_lifecycle_wire_contract.py
uv run pytest --run-full-regression --full-regression-shard -q \
  tests/cli_runtime/test_provider_lifecycle.py tests/cli_runtime/test_uninstall.py \
  tests/cli_runtime/test_update.py tests/integration/test_provider_lifecycle_artifacts.py \
  tests/integration/test_provider_lifecycle_tripwire.py
uvx --no-cache --from . spec-dock update .
uv run python - <<'PY_STATE'
from pathlib import Path
from spec_dock.provider_lifecycle.candidate import build_packaged_candidate
from spec_dock.provider_lifecycle.model import parse_install_record, parse_slot_marker
c=build_packaged_candidate(Path('src/spec_dock/assets'),'0.2.4')
r=parse_install_record(Path('spec-dock/spec-dock.version').read_bytes())
assert r.state.value=='ready' and r.operation is None and r.version=='0.2.4'
assert r.seed_policy.value=='preserve-only' and r.candidate_digest==c.digest
for slot in ('spec-dock','spec-dock-grill-with-docs'):
 m=parse_slot_marker((Path('.agents/skills')/slot/'.spec-dock-provider-slot.json').read_bytes())
 assert m.slot==slot and m.version=='0.2.4' and m.candidate_digest==c.digest
PY_STATE
cmp src/spec_dock/assets/spec_dock/docs/migration.md spec-dock/docs/migration.md
cmp src/spec_dock/assets/spec_dock/docs/README.md spec-dock/docs/README.md
make lint
uv run pytest -q
uv run python -m scripts.quality.verify_full_regression --shards 4
python3 ./spec-dock/scripts/spec-dock validate
# Compare external complete protected before/after witness and complete dogfood identity.
git diff --check
```

**Expected observable result**

All admitted failures normal/terminal; active0; old engine/tests absent; current workflows independently GREEN; lifecycle docs and AGENTS lifecycle match final product; checked-in dogfood is complete0.2.4 candidate; protected `.workbench`/seeds/user data identical.

**Evidence to record in Issue report.md**

Admission→final mapping、gate runs、workflow retarget table、wire/docs/AGENTS hashes/grep、dogfood record/marker/roots/slots/digest、protected witness hashes、validate/fresh consumer.

**Stop conditions and escalation owner**

Unmapped/drifted failure、active row、workflow dangling/failure/S70 dependency、stale operator docs、dogfood modified legacy/partial/digest mismatch、any protected/seed drift: no merge; relevant Product/spec/test/CI/filesystem owner.

**Cleanup**

Safely clean only external workspaces after report summary. Retain current policy infrastructure intentionally.

**PR-B main merge invariant**

S60 is the sole PR-B gate. Main has complete final0.2.4 lifecycle/wire/docs/AGENTS lifecycle、complete dogfood candidate、no old engine、active0、working current PR and main-push gates. No bridge/toggle/final S70 redesign.

**Requirement and design trace IDs**

RQ-022–023、032、D-015、D-020–022.

## I392-S70 — Consumer-first final gate, self-contained evidence tooling, second dogfood update and atomic old-policy removal

**Stable ID**: `I392-S70`.

**Objective and contract-visible outcome**

On one PR-C branch, add final provider gate/environment/verifier/workflow/tests/AGENTS policy, retire all old consumers before providers, remove old machinery, and commit a second complete dogfood candidate. S70 is non-main; local build is tool validation only.

**Exact owned repository paths and symbols**

Create/update:

```text
scripts/provider_gate.py
ci/linux-qualification.Dockerfile
ci/linux-qualification-environment.json
tests/unit/infra/test_provider_{gate,workflow}.py
tests/provider_test_ownership.json
scripts/static_analysis/run.sh
Makefile
.github/workflows/provider-ci.yml
AGENTS.md test-policy/provider-gate sections
README.md test-policy sections
src/spec_dock/assets/spec_dock/docs/README.md test-policy sections
provider lifecycle code/tests for external workspace, receipts and wire
spec-dock/{docs,templates,system,scripts}/**
.agents/skills/spec-dock/**
.agents/skills/spec-dock-grill-with-docs/**
spec-dock/spec-dock.version
two slot markers
#392 report.md pre-freeze summary
```

Retire/delete after consumer-zero proof:

```text
tests/unit/test_provider_test_lanes.py
tests/unit/test_full_regression_baseline.py
all other tests/code importing tests.conftest lane policy or scripts.quality full-regression modules
.github/workflows/provider-full-regression.yml
tests/conftest.py
full-regression-ledger.json
full-regression-timing-weights.json
scripts/quality/full_regression_baseline.py
scripts/quality/verify_full_regression.py
scripts/quality/__init__.py when empty
fast/full marker declarations/decorators/options
```

External purposes: `s70-pre-freeze` and `s70-dogfood-witness`.

**Explicit non-owned and no-touch paths**

Seeds、initiatives/artifacts/complete `.workbench`/unknown user data、#387 files、human settings/release、canonical R/D/P.

**Prerequisites and dependency**

PR-C based on exact S60 merged tree with current gates/dogfood GREEN. Branch continues through S80; no S70 handoff.

**RED evidence or justified no-new-test rule**

Workflow structural tests fail for extra packager、wrong needs/artifact/receipt/evidence set、consumer build、non-nine-file evidence、filename-only hashes、wrong verifier messages/exits. External workspace tests fail inside-repo/tamper/unsafe cleanup. Consumer inventory fails before provider removal. AGENTS policy and second dogfood update fail before final candidate.

**Smallest implementation action**

1. Implement exact provider gate subcommands, external workspace helper, receipt/evidence schemas and downloaded verifier.
2. Freeze stable Linux descriptor/Dockerfile.
3. Rewrite final workflow with sole producer and exact dataflow.
4. Add structural/verifier/golden tests; local build only in external pre-freeze workspace.
5. Update Makefile/static analysis and AGENTS/README/docs test-policy sections; retain S60 lifecycle text.
6. Retire all policy consumers and prove zero; then delete providers/data/old workflow/markers in same branch.
7. Run final collection/tests and stale-reference grep.
8. After all candidate bytes settle, capture external protected witness, run `uvx --no-cache --from . spec-dock update .`, verify second complete digest state and protected equality.
9. Complete tracked report pre-freeze summary; safely remove external local artifacts; commit and require clean tree.

**Focused verification commands**

```bash
uv run pytest -q tests/unit/infra/test_provider_gate.py tests/unit/infra/test_provider_workflow.py \
  tests/unit/infra/test_provider_lifecycle_external_workspace.py
uv run python scripts/provider_gate.py freeze-linux-environment \
  --descriptor ci/linux-qualification-environment.json \
  --dockerfile ci/linux-qualification.Dockerfile
# Non-authoritative pre-freeze tool validation, external only.
uv run python scripts/provider_gate.py build --source-sha "$(git rev-parse HEAD)" \
  --out "$ISS392_EXTERNAL_TMP/pre-freeze-candidate"
uv run python scripts/provider_gate.py verify-environment \
  --descriptor ci/linux-qualification-environment.json
uv run python scripts/provider_gate.py verify-node-ownership --map tests/provider_test_ownership.json
! rg -n 'tests\.conftest|scripts\.quality\.full_regression_baseline|scripts\.quality\.verify_full_regression|--run-full-regression|--full-regression-shard|POLICY_SKIP_REASON|full-regression-ledger|full-regression-timing' --glob '!spec-dock/initiatives/**' .
test ! -e tests/unit/test_provider_test_lanes.py
test ! -e tests/unit/test_full_regression_baseline.py
test ! -e tests/conftest.py
test ! -e .github/workflows/provider-full-regression.yml
uv run pytest --collect-only -q
uv run pytest -q
make lint
uvx --no-cache --from . spec-dock update .
python3 ./spec-dock/scripts/spec-dock validate
# Parse S70 record/markers and compare external protected witness exactly.
grep -F 'make provider-test' AGENTS.md
grep -F 'make provider-qualify' AGENTS.md
git diff --check
```

**Expected observable result**

Final tooling/workflow/verifier/environment tests GREEN; sole producer; actual-byte nine-file evidence contract; all old consumers/providers absent; final AGENTS; second complete dogfood digest; protected equality; tracked branch clean. No authoritative final package yet.

**Evidence to record in Issue report.md**

Consumer removal、workflow needs/artifacts/schemas、verifier exits/goldens、external workspace tests、environment descriptor、AGENTS split、S60→S70 candidate/dogfood digest、protected/seed equality、validate/fresh consumer. Mark local build non-authoritative.

**Stop conditions and escalation owner**

Remaining consumer、wrong graph/evidence bytes/verifier relation、extra packager、unsafe temp、stale AGENTS、old reference、dogfood/protected mismatch、dirty tree: no merge; fix same #392.

**Cleanup**

Owner-bound cleanup of pre-freeze/witness directories after report summary. No repository temp path.

**Internal checkpoint invariant**

Not a main gate. PR-C branch has coherent final candidate/gate/dogfood and must continue S80. Main remains S60 until human merge.

**Requirement and design trace IDs**

RQ-024–028、031–032、D-016–018、D-023–033.

## I392-S80 — Frozen-head Provider CI, downloaded actual-byte verification, context transition and PR-C gate

**Stable ID**: `I392-S80`.

**Objective and contract-visible outcome**

Freeze S70 head/tree, dispatch one authoritative workflow, download only candidate and nine-file evidence artifacts, verify actual bytes and all receipts/role evidence, complete qualification/context/attestation, and hand off human merge. S80 owns no tracked path and performs no local build/update/sync.

**Exact owned repository paths and symbols**

Tracked: none. External purpose `s80-final-run`; GitHub Actions/API/attestations only.

**Explicit non-owned and no-touch paths**

All tracked code/tests/docs/report/dogfood、seeds/protected data; settings except human-admin transition; release.

**Prerequisites and dependency**

S70 branch GREEN; tracked report finalized/committed; complete S70 dogfood; clean tree; external workspace safe; human admin available; dedicated canary never merged.

**RED evidence or justified no-new-test rule**

Committed tests already reject every graph/schema/byte/build/environment/context defect. Any tracked edit、local build、update、sync、zero/multiple run or artifact is a runtime stop.

**Smallest implementation action**

1. Freeze `VERIFIED_PR_HEAD`/tree/branch; no tracked edits.
2. Run read-only lint/collection/tests/docs/dogfood parse/validate.
3. Record prior dispatch run IDs externally; dispatch `provider-ci.yml` with exact candidate SHA and qualification true.
4. Select exactly one new matching run; wait success; fetch run/jobs/artifacts JSON externally.
5. Require exact six Actions artifacts and exact job graph; download candidate and provider evidence only.
6. Run exact I392-D-032 verifier. It rehashes three candidate files and nine evidence files, validates four receipts/evidence schemas and API linkage, producer1/consumer0.
7. Read qualification、sdist、macOS facts from actual role evidence bytes.
8. Execute required-context sequence: old retained -> new GREEN -> add new required -> read back both -> canary RED/block -> close canary -> implementation GREEN -> remove old -> final readback.
9. Emit content-addressed pre-merge attestation externally and post a new immutable GitHub object.
10. Reconfirm head/tree/status and dogfood digest unchanged.

**Focused verification commands**

```bash
test -z "$(git status --short)"
VERIFIED_PR_HEAD="$(git rev-parse --verify 'HEAD^{commit}')"
VERIFIED_PR_TREE="$(git rev-parse --verify 'HEAD^{tree}')"
PR_BRANCH="$(git branch --show-current)"
export VERIFIED_PR_HEAD VERIFIED_PR_TREE PR_BRANCH
make lint
uv run pytest --collect-only -q
uv run pytest -q
python3 ./spec-dock/scripts/spec-dock validate
# No uv build, provider_gate.py build, spec-dock update, or spec-dock sync.
gh run list --workflow provider-ci.yml --branch "$PR_BRANCH" --event workflow_dispatch --limit 100 --json databaseId > "$ISS392_EXTERNAL_TMP/before-runs.json"
gh workflow run provider-ci.yml --ref "$PR_BRANCH" -f candidate_sha="$VERIFIED_PR_HEAD" -f qualification=true
gh run watch "$RUN_ID" --exit-status
gh run view "$RUN_ID" --json databaseId,headSha,status,conclusion,jobs > "$ISS392_EXTERNAL_TMP/api/run.json"
gh api "repos/chemitaro/spec-dock/actions/runs/$RUN_ID/jobs" > "$ISS392_EXTERNAL_TMP/api/jobs.json"
gh api "repos/chemitaro/spec-dock/actions/runs/$RUN_ID/artifacts" > "$ISS392_EXTERNAL_TMP/api/artifacts.json"
gh run download "$RUN_ID" -n "provider-candidate-$VERIFIED_PR_HEAD" -D "$ISS392_EXTERNAL_TMP/candidate"
gh run download "$RUN_ID" -n "provider-evidence-$VERIFIED_PR_HEAD" -D "$ISS392_EXTERNAL_TMP/evidence"
uv run python scripts/provider_gate.py verify-downloaded-artifact \
  --repository chemitaro/spec-dock \
  --candidate-dir "$ISS392_EXTERNAL_TMP/candidate" \
  --evidence-dir "$ISS392_EXTERNAL_TMP/evidence" \
  --run-json "$ISS392_EXTERNAL_TMP/api/run.json" \
  --jobs-json "$ISS392_EXTERNAL_TMP/api/jobs.json" \
  --artifacts-json "$ISS392_EXTERNAL_TMP/api/artifacts.json" \
  --source-sha "$VERIFIED_PR_HEAD" \
  --source-tree "$VERIFIED_PR_TREE" \
  --workflow-run-id "$RUN_ID" --json > "$ISS392_EXTERNAL_TMP/download-verification.json"
jq -e '.status=="verified" and .code=="downloaded-artifact-verified" and (.evidence_files|length)==9' "$ISS392_EXTERNAL_TMP/download-verification.json"
uv run python scripts/provider_gate.py emit-attestation \
  --type pre-merge-attestation-v1 --source-sha "$VERIFIED_PR_HEAD" \
  --workflow-run-id "$RUN_ID" --input "$ISS392_EXTERNAL_TMP/evidence" \
  --output "$ISS392_EXTERNAL_TMP/pre-merge-attestation.json"
test "$(git rev-parse HEAD)" = "$VERIFIED_PR_HEAD"
test "$(git rev-parse 'HEAD^{tree}')" = "$VERIFIED_PR_TREE"
test -z "$(git status --short)"
```

**Expected observable result**

One frozen head、one Linux packaging invocation、same immutable wheel/sdist、consumer build0、four valid receipts and role evidence bytes、exact nine-file evidence、stable20-run metrics/fault100/macOS/sdist GREEN、dogfood digest match、new required before RED、canary blocks、implementation GREEN、old removed after proof、external attestation hash verified、tracked tree unchanged.

**Evidence to record**

Tracked report receives nothing after freeze. External attestation contains head/tree/report blob、run/jobs/needs/API artifact IDs/names/digests、candidate bytes、four receipt/evidence hashes and actual metrics、environment、context snapshots、dogfood digest and conclusions.

**Stop conditions and escalation owner**

Any tracked edit/local build/update/sync、unsafe temp、zero/multiple run、wrong head/tree/job/needs/artifact/file/receipt/evidence/build/hash/environment/metrics/dogfood/context/attestation: return S70, create a new head and rerun all final evidence. Settings owner is human admin.

**Cleanup**

Close canary without merge. After immutable external evidence is verified, safely clean local external workspace by owner sentinel. Never touch repository `.workbench`.

**PR-C main merge invariant**

S80 is sole PR-C gate. S70 candidate/consumer closure/dogfood and S80 authoritative CI/evidence/context/human review are GREEN. Main after human merge has complete final lifecycle/docs/wire/register/dogfood、final gate、no old machinery、final AGENTS. Agent does not merge.

**Requirement and design trace IDs**

RQ-025–033、D-025–033.

## 5. Human merge and external closure

Human performs merge. Exact verification:

```bash
MERGE_COMMIT="$(gh pr view "$PR_NUMBER" --json mergeCommit --jq '.mergeCommit.oid')"
test "$(git rev-parse "${VERIFIED_PR_HEAD}^{tree}")" = "$(git rev-parse "${MERGE_COMMIT}^{tree}")"
```

Do not compare a later `origin/main` tree. External `post-merge-closure-v1` records pre-attestation hash、merge SHA/tree、tree equality、actor/time、SpecDock finish and GitHub #392 close. External `epic-closure-v1` records #384 close after #392 finish. No tracked report writeback and no new Issue.

## 6. Definition of done

All I392-RQ-001–033 are verified; S30/S60/S80 are the only safe main gates; repository `.workbench` was never written/deleted; owner decision list remains empty.
