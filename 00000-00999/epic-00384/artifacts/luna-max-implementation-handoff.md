---
種別: Implementation Handoff
対象: "GPT-5.6 Luna / reasoning Max"
Issue: "iss-00392"
最終更新: "2026-09-01"
repository_evidence:
  repository: "chemitaro/spec-dock"
  branch: "codex/epic-00384-provider-test-strategy-planning"
  sha: "d145f0f0d6f35535eebc0da89b7b708824279f1f"
---

# Luna Max Implementation Handoff

## 1. Authority order

1. Execute Issue `plan.md`.
2. Read Issue `requirement.md` for behavior.
3. Read Issue `design.md` for components, schemas and filesystem/CI dataflow.
4. Treat `provider-lifecycle-wire-contract.md` as the only public lifecycle wire authority.
5. Treat `active-failure-disposition-register.md` as the only failure admission/terminalization authority.
6. Use Epic R/D/P and accepted ADR for boundaries and merge governance.
7. Follow root `AGENTS.md` current policy until the exact S60/S70 owned-section transitions.
8. Do not make Product, Policy, Security, migration, CI-evidence or filesystem-safety choices. A mismatch selects a fixed stop, not an alternative design.
9. Never merge or change required contexts; prepare exact human handoff.

## 2. Dependency and PR graph

```text
#387 human merge
  -> S00 independent admission
  -> PR-A: S10 -> S20 -> S30 only merge gate
  -> PR-B: S40 internal -> S50 internal -> S60 only merge gate
  -> PR-C: S70 internal -> S80 only merge gate
  -> human merge -> external closure
```

S40, S50 and S70 are never offered as merge-ready. #392 is the only implementation Issue.

## 3. Repository path ownership

### S00

Repository reads only, except pre-merge summary in #392 tracked report. All temporary files are under an external owner-bound OS temp workspace. Never write repository `.workbench`.

### S10–S30

```text
src/spec_dock/provider_lifecycle/**
src/spec_dock/assets/legacy_0_2_3.json
tests/unit/infra/test_provider_lifecycle_model.py
tests/unit/infra/test_provider_lifecycle_candidate.py
tests/unit/infra/test_provider_lifecycle_wire_contract.py
tests/unit/infra/test_provider_lifecycle_filesystem.py
tests/unit/infra/test_provider_lifecycle_service.py
tests/unit/infra/test_provider_lifecycle_faults.py
tests/unit/infra/test_provider_assets.py
```

Public CLI, checked-in dogfood and old engine remain unchanged through S30.

### S40

Owned provider/public/doc paths:

```text
pyproject.toml
src/spec_dock/cli.py
src/spec_dock/provider_lifecycle/{model,service,public_result}.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/uninstall.py
README.md lifecycle sections
src/spec_dock/assets/spec_dock/docs/migration.md
src/spec_dock/assets/spec_dock/docs/README.md lifecycle sections
wire/public/CLI tests
```

S40 must not edit or sync any checked-in dogfood fixed root, either fixed skill slot, `spec-dock/spec-dock.version`, either slot marker, or root AGENTS. Dogfood stays exact legacy.

### S50

Only provider legacy/service and external synthetic migration/tripwire tests. It does not mutate checked-in dogfood.

### S60

```text
old engine/manifest/test deletion
src/spec_dock/context_pack.py
current .github/workflows/provider-ci.yml retarget
transitional tests/unit/test_provider_test_lanes.py
transitional ledger/timing/tests/conftest.py exact updates
failure-owner tests admitted by the register
README/provider lifecycle docs
root AGENTS.md lifecycle/uninstall sections only
all four checked-in dogfood roots
both fixed dogfood slots
seven-key dogfood record
both dogfood slot markers
#392 tracked report implementation summary
```

Retain current quality scripts, current main-push Full Regression workflow and current AGENTS test-policy sections until S70. S60 performs one complete dogfood migration, never partial sync.

### S70

```text
scripts/provider_gate.py
ci/linux-qualification.Dockerfile
ci/linux-qualification-environment.json
tests/unit/infra/test_provider_gate.py
tests/unit/infra/test_provider_workflow.py
tests/provider_test_ownership.json
Makefile
scripts/static_analysis/run.sh
final .github/workflows/provider-ci.yml
root AGENTS.md test-policy/provider-gate sections
README/provider docs test-policy sections
all old policy consumers, then providers/data/workflow deletion
all four dogfood roots, both slots, record and markers for second update
#392 tracked report pre-freeze completion
```

S70 local build is tool smoke only. S70 is not merge-ready.

### S80

Tracked paths: none. External temp/API/GitHub evidence only. No build, update, sync or tracked report edit.

## 4. Fixed lifecycle cheat sheet

```text
Shared container: spec-dock (fresh create only; never whole delete)
Roots: spec-dock/docs, templates, system, scripts
Slots: .agents/skills/spec-dock, .agents/skills/spec-dock-grill-with-docs
Record: spec-dock/spec-dock.version
Slot marker: <slot>/.spec-dock-provider-slot.json
Seeds: spec-dock/.gitignore, .github/workflows/ci.yml
```

Record exact keys:

```text
schema_version,state,operation,version,candidate_digest,seed_policy,skill_slots
```

`create-if-absent` applies only to never-installed fresh init. All other install/update/migration/uninstall intents use `preserve-only`. Resume tuple is exact operation/candidate/policy.

Publication order is stage -> bootstrap/bind -> incomplete record -> docs -> templates -> system -> scripts -> spec-dock slot -> grill slot -> authorized seeds -> verify -> terminal record -> cleanup.

## 5. Closed wire implementation

Do not infer or invent a wire value. Generate enums/tables/serializers and table-driven tests from `provider-lifecycle-wire-contract.md`. It contains:

- 36 public codes and 116 exact context rows;
- exact `phase`/`last_completed_phase`, operation, mode/apply, digest/policy nullability, mutation/rollback/retry/exit;
- closed action category/status/reason relations;
- fixed `TARGET_PATH_ORDER` for actions/failed/pending arrays;
- exact messages/guidance/warnings/errors and compact JSON/text goldens.

Unknown code, token, path, reason, field, duplicate or wrong ordering is a constructor/test defect, not a fallback result.

## 6. #387 admission

The #387 tracked report block is pre-merge only. It contains `candidate_head_sha` and `candidate_tree_sha` plus exact row mappings. It must not contain merge SHA/tree, post-merge ledger blob or merge time.

After merge S00 obtains GitHub PR data and requires:

```text
repository == chemitaro/spec-dock
PR number == report value
merged == true
PR head SHA/tree == report candidate head/tree
merge commit exists
merge commit tree == report candidate tree
candidate head is ancestor of merge commit
merged report blob contains the same mapping
```

Then cross-check merged tree ledger and full collection with `active-failure-disposition-register.md` rule `ISS387-THREE-WAY-V3`. For each conditional original row:

- removed: old absent, exact positive successor/absence evidence, no failure-lineage row;
- retained-unchanged: same node/signature plus nonempty retain reason;
- split-or-renamed: exact mapping and positive successors plus zero or one failure-lineage row with exact signature.

No fixed post row count. Missing/unmapped/drifted data stops before S10 for canonical spec amendment and Strict rereview.

## 7. External workspace contract

Create with Python `tempfile.mkdtemp` under an OS temp root, never under repository. Immediately:

1. resolve repository and temp real paths;
2. prove temp is not repository or descendant;
3. require real directory, UID=current UID and mode `0700`;
4. capture parent/root device and inode;
5. create `OWNER.json` with `O_CREAT|O_EXCL|O_NOFOLLOW`, mode `0600`;
6. fsync sentinel and directory;
7. register each child path before creating it.

Cleanup revalidates parent/root identity, UID/mode, outside-repository relation and exact sentinel bytes. Delete only registered children and then the exact root. Unknown child or mismatch preserves everything and stops. Never clean any repository `.workbench` path.

The protected witness for repository `spec-dock/.workbench` and other protected roots is stored in this external workspace. It records every entry's relative path, kind, mode, uid/gid, link target or regular bytes hash. Compare before/after exactly.

## 8. Dogfood contract

### S00, S40 and S50

Record bytes stay exact `0.2.3\n`; two slot markers remain absent; all four roots and two slots remain byte-identical. S40 provider docs may differ from checked-in legacy dogfood until the complete S60 migration. Do not run `spec-dock update .` or copy provider roots in S40/S50.

### S60

After provider code/docs are complete, run the new lifecycle service once against repository root. Commit all four roots, both slots, seven-key ready record and both markers for one S60 candidate digest. Verify provider/dogfood candidate parity, exact record/marker bytes, no stage/incomplete residue, protected witness and seed hashes unchanged, validate and fresh consumer. Update AGENTS lifecycle/uninstall sections only.

### S70

After final gate/test-policy candidate bytes settle, perform a second complete candidate-wide update and commit the new record/marker digest. Update AGENTS test-policy/provider-gate sections. S80 verifies only.

## 9. Gate continuity

S60 keeps current gate topology. Retarget only deleted distribution test paths to concrete successor tests. Update lane/ledger/timing references mechanically and require active/approved failures zero. Run the current PR workflow-equivalent commands and current main-push verifier separately. Do not use `scripts/provider_gate.py` as S60 authority.

S70 first adds final gate modules/tests/workflow. Then retire/replace all old consumers, including `test_provider_test_lanes.py`, `test_full_regression_baseline.py`, imports of `tests.conftest` and quality modules and all command/doc references. Prove consumer zero before deleting providers, ledger, timing, sharder, conftest and old workflow.

## 10. Final CI and self-contained evidence

Exact needs:

```text
provider-build-artifacts -> linux canonical, sdist smoke, macOS delta
producer + linux + sdist + macOS -> provider-attestation
provider-attestation -> provider-gate
```

Only producer packages once. Consumer build counts are zero. Candidate artifact has manifest, one wheel and one sdist. Each role receipt artifact has one receipt and one role evidence file.

Final `provider-evidence-<sha>` contains exactly nine files in this order:

```text
provider-evidence.json
provider-receipt-producer.json
producer-build-evidence.json
provider-receipt-linux-canonical.json
linux-canonical-evidence.json
provider-receipt-sdist-smoke.json
sdist-smoke-evidence.json
provider-receipt-macos-delta.json
macos-delta-evidence.json
```

Provider evidence includes SHA-256/size for every eight subordinate files and all source/run/job/artifact/candidate/build/environment/metric bindings. The verifier reads every actual byte file and recomputes all hashes.

Exact verifier interface is the one in Issue Design I392-D-032 and Issue Plan S80. Do not make job or artifact names configurable and do not add a generic error code.

## 11. S80 sequence

1. Verify clean tracked S70 head, record/markers/digest and protected witness.
2. Freeze head/tree and create external S80 workspace.
3. Snapshot existing dispatch runs externally.
4. Dispatch final provider workflow with exact head and qualification input.
5. Select exactly one new matching run and wait success.
6. Save run/jobs/artifacts API JSON externally.
7. Download exact candidate and provider-evidence artifacts externally.
8. Run `verify-downloaded-artifact`; require exit 0 and exact JSON golden.
9. Verify environment/20-run/fault/macOS/sdist evidence from actual role files.
10. Human adds new required context while old remains, proves canary RED blocking, restores GREEN, then removes old provider-only context.
11. Emit immutable external pre-merge attestation.
12. Confirm head/tree/status and dogfood identity unchanged.

## 12. Root AGENTS split

S60 may change only lifecycle/uninstall text: `--remove-specs` is non-destructive removed trap, exit 2; uninstall is tooling-only; partial retry is exact same tuple. Current test/full-regression instructions stay.

S70 changes only final test-policy/provider-gate material plus any references necessarily made stale by removed policy. It documents `make lint`, `make provider-test`, `make provider-qualify`, sole Linux producer, same-wheel macOS delta, external evidence and human-only merge/settings. Old ledger/skip/shard/main-push instructions are absent.

## 13. Stop matrix

| Condition | Required action |
|---|---|
| #387 report predicts merge identity or postmerge data | stop before S10; spec owner correction and Strict rereview |
| GitHub PR/head/tree/merge mismatch | stop before S10 |
| Unknown register node/signature/mapping | stop before S10 |
| Repository workbench write/delete or external temp identity failure | destructive stop |
| Wire value/relation outside artifact | fail RED; do not invent |
| S40/S50 dogfood drift | restore exact legacy; no merge |
| S60 partial dogfood or protected drift | block PR-B |
| S60 current PR/main-push gate failure | block PR-B |
| S70 old consumer before provider deletion not zero | block PR-C |
| S70 partial second dogfood update | block PR-C |
| S80 tracked edit/build/update/sync | invalidate S80; return S70/new head |
| Extra packager or consumer build >0 | block PR-C |
| Evidence missing actual receipt/evidence bytes or hash mismatch | block PR-C |
| Environment/metric/fault/flake mismatch | invalidate qualification |
| New context not required before RED or RED does not block | stop and restore settings |
| Merge tree mismatch | do not finish Issue |

## 14. Definition of done

S30, S60 and S80 alone are merge gates. Every Requirement/Design trace and each step evidence is complete, all temporary data stayed outside repository, repository workbench is byte-identical, dogfood is complete at candidate-changing gates, final evidence is self-contained and byte-verified, human merge remains pending until external handoff, and `owner_decisions_required=[]`.
