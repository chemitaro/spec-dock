---
種別: 設計書（Epic）
ID: "epic-00384"
タイトル: "Provider Test Strategy Simplification and Execution Cost Reduction"
関連GitHub: ["#384"]
状態: "draft"
最終更新: "2026-09-01"
依存: ["requirement.md", "artifacts/20260831t152024z-adr-single-implementation-unit-and-provider-hard-cutover-policy.md"]
親: ["init-local-00003"]
正本検証:
  repository: "chemitaro/spec-dock"
  branch: "codex/epic-00384-provider-test-strategy-planning"
  sha: "b094771e089c1f31618116e84be32fcf78704409"
---

# epic-00384 Provider Test Strategy Simplification and Execution Cost Reduction — 設計

## 1. Design intent

Historical per-file reconciliation、journal/checkpoint recovery、purge、failure approval、sharded regressionを、fixed ownershipとexternal rerun convergenceを中心とするdeep contractへ置換する。設計はmutation authority、resume identity、fresh bootstrap、main merge continuity、artifact/test ownership、evidence identityを静的に限定する。

## 2. Architecture

```text
public CLI -> public result adapter -> provider lifecycle service
                                     |-> classifier
                                     |-> candidate builder
                                     |-> exact legacy-0.2.3 recognizer
                                     `-> descriptor-bound filesystem

shared spec-dock container
  |- fixed record
  |- fresh-only .gitignore seed
  |- four disposable roots
  `- protected consumer data

repository root
  |- two fixed .agents skill slots
  `- fresh-only consumer CI seed

PR-B main: complete final lifecycle + current provider gate intact
PR-C branch: replacement gate/environment/AGENTS + atomic old policy removal
PR-C main: final build-once provider gate
```

### E384-D-001 — Boundary decomposition

- `src/spec_dock/cli.py`: parser、command-to-service dispatch、error boundary。
- `src/spec_dock/provider_lifecycle/`: model、candidate、filesystem、legacy recognizer、service、public result。
- `src/spec_dock/assets/legacy_0_2_3.json`: single supported legacy generationのwhole-tree digests。
- `src/spec_dock/context_pack.py`: old moduleから抽出するnon-lifecycle behavior。
- `scripts/provider_gate.py`: artifact build/verify、node ownership、environment verification、qualification/attestation。
- `ci/linux-qualification.Dockerfile`、`ci/linux-qualification-environment.json`: stable Linux qualification contract。
- `tests/provider_test_ownership.json`: contract-to-owner mappingのみ。
- root `AGENTS.md`: final operator contract。PR-C/S70 ownership。

### E384-D-002 — Provider/dogfood direction

`src/spec_dock/`を先に変更し、dogfood `spec-dock/`へ4 roots、2 slots、recordを同期する。Dogfood `spec-dock/.gitignore`とroot `.github/workflows/ci.yml`はconsumer-owned seedでありupdate対象外。

## 3. Ownership and shared-container bootstrap

### E384-D-003 — Code-fixed authority

| Category | Exact path | Authority |
|---|---|---|
| Shared container bootstrap | `spec-dock` | fresh stateでabsentの場合のexclusive createだけ。replace/deleteなし。 |
| Disposable roots | `spec-dock/{docs,templates,system,scripts}` | valid new recordまたはexact legacy recognition |
| Disposable slots | `.agents/skills/spec-dock`、`.agents/skills/spec-dock-grill-with-docs` | matching new markerまたはexact legacy tree |
| Record | `spec-dock/spec-dock.version` | lifecycle service only |
| Seeds | `spec-dock/.gitignore`、`.github/workflows/ci.yml` | fresh `init` + absent only |

Existing shared containerのunknown non-target childはpreserve-and-ignore。Uninstallはcontainerを削除しない。

### E384-D-004 — Bootstrap protocol

Fresh classifierはcontainer absentまたはreal directoryを許可し、symlink/non-directoryをblockする。Absent caseは次の順序。

1. root fdとcontainer absence witnessをcapture。
2. candidate/stage/other parents/target collisionsを全validate。
3. stage ownerにroot identity、operation、candidate digest、seed policyをwrite/fsync。
4. `mkdirat(root_fd,"spec-dock",0755)`をexclusive実行。
5. `openat(...,O_NOFOLLOW|O_DIRECTORY)`でbindしvisible/held identityを一致確認。
6. root fsync後、created device/inodeをstage ownerへ追記/fsync。
7. incomplete recordをatomic publish。

Record前failureはcreated identityが同一かつemptyの場合だけdescriptor-bound `rmdir`でcleanup。Cleanup不能/foreign child/identity mismatchはstage ownerを保持した`partial_failure/bootstrap-incomplete`とし、same operation/candidate/seed policyだけresume。Existing containerはcleanupしない。

### E384-D-005 — External stage

```text
<target-parent>/.spec-dock-provider-txn-<root-id-hash>-<operation>-<candidate-digest>
```

Strict `STAGE-OWNER.json`はschema、root device/inode、operation、candidate digest、seed policy、created spec-dock identityを持つ。Exact matchのみresume/cleanup。Foreign/missing/invalid marker、symlink、tuple mismatchはblock。

## 4. State and record

### E384-D-006 — State machine

```text
absent
  -> incomplete(install,candidate,create-if-absent|preserve-only)
  -> ready(same seed policy)
  -> incomplete(update,candidate,preserve-only)
  -> ready
  -> incomplete(uninstall,candidate,preserve-only)
  -> tooling-absent-preserved-data(preserve-only)
  -> incomplete(install,new candidate,preserve-only)
  -> ready

exact legacy-0.2.3 -> incomplete(migrate/install,preserve-only) -> ready
unsafe evidence -> blocked (derived, not serialized)
```

### E384-D-007 — Strict record and immutable resume identity

`spec-dock/spec-dock.version`はexact seven top-level keys。

```json
{
  "schema_version": 1,
  "state": "ready",
  "operation": null,
  "version": "0.2.4",
  "candidate_digest": "<64 lowercase hex>",
  "seed_policy": "create-if-absent",
  "skill_slots": {
    "spec-dock": "0.2.4",
    "spec-dock-grill-with-docs": "0.2.4"
  }
}
```

- seed policy: `create-if-absent|preserve-only`。
- create-if-absentはnever-installed absentへの`init`/`init --force`だけ。
- update-on-absent、reinstall、legacy migration、update、uninstallはpreserve-only。
-一operationではincompleteからterminal recordまでpolicy不変。
- Resume identityは`(operation,candidate_digest,seed_policy)`。Request/stage/record全一致必須。
- Seed fileの存在からpolicyを推測しない。
- Unknown/missing/duplicate key、invalid relation、oversize、invalid UTF-8/type/hard linkをblock。

### E384-D-008 — Slot marker

Each slotの`.spec-dock-provider-slot.json`はschema、slot、version、candidate digestを持つ。Markerはcandidate digest対象外。New record下のmarker mismatch/markerless slotはblock。Legacy recognizerだけexact markerless treeを扱う。

## 5. Candidate and atomic publication

### E384-D-009 — Candidate

Candidate sourceは4 roots/2 slotsへcode-fixed。Regular file/real directoryだけを許可し、symlink、special、hard link、path traversalをreject。Canonical path/kind/mode/content digest streamをversion込みでSHA-256。Seeds、record、generated markersはexcluded。Source captureとstaged digest一致必須。

### E384-D-010 — Publication

1. Root `flock`/descriptor binding。
2. Candidate stage/validate。
3. Shared container bootstrap/bind if needed。
4. Incomplete record publish with immutable policy。
5. `docs -> templates -> system -> scripts -> spec-dock slot -> grill slot`。
6. create-if-absent policyだけseedsを`O_EXCL|O_NOFOLLOW`作成。
7. Full postcondition後ready record with same policy。
8. Cleanup。Terminal record後のowned external cleanup failureだけwarning。

Absent publication/uninstall detachはnative no-replace、existing valid root/slot replaceはnative exchange。Linux `renameat2`、macOS `renameatx_np`。Fallbackなし。

## 6. Operation flows and results

### E384-D-011 — Dispatch

| Invocation/state | Operation | Seed policy |
|---|---|---|
| init/init-force + absent | install | create-if-absent |
| update + absent | install | preserve-only |
| any install + tooling-absent | install | preserve-only |
| init-force/update + legacy | migrate/install | preserve-only |
| init-force/update + ready | update | preserve-only |
| uninstall | uninstall | preserve-only |

Incomplete stateはexact tupleでのみresume。

### E384-D-012 — Uninstall

Dry-runはcomplete read-only plan。Applyはincomplete(uninstall,preserve-only) -> four roots/two owned slots detach -> protected/container validation -> tooling-absent(preserve-only) -> cleanup。User data、seeds、unknown paths、containerをtouchしない。

### E384-D-013 — Result model

| Status | Exit | Meaning |
|---|---:|---|
| planned | 0 | dry-run、mutation false |
| completed | 0 | desired durable state |
| completed_with_warnings | 0 | desired state、owned external cleanup only |
| blocked | 1 | pre-mutation rejectionまたは完全cleanup済みbootstrap |
| partial_failure | 1 | durable mutationまたはcleanup不能bootstrap |
| error | 2 | invalid/removed operation |

Resultはseed policy、mutation_started、bootstrap_rolled_backを公開する。

## 7. Legacy and downgrade safety

### E384-D-014 — Exact legacy recognizer

Fixtureはplain marker hash、4 root digests、2 slot digests、recovery pathsのみ。All roots exact、slots absent/exact。Active recovery markerはblock。Migration/uninstall policyはpreserve-only。

### E384-D-015 — Composite tripwire

Startup `sitecustomize`はtarget-scoped Python mutation auditと`ctypes.CDLL`の`renameat2`/`renameatx_np`をunderlying call前にinterceptする。Platform native positive controlはevent 1、old command matrixはevent 0 + tree digest unchanged。

## 8. Test and merge continuity

### E384-D-016 — Portfolio layers

Pure/model ownsstate/record/policy/result。Filesystem/service ownscontainer/no-follow/atomic/fault。CLI ownsparser/text/JSON/exit。Built artifact ownsmigration/lifecycle/tripwire/artifact identity。macOS ownsplatform delta only。

### E384-D-017 — PR-B transitional current-gate contract

S60 removes old product engine and duplicate tests、terminalizes all active failures、and owns the temporary current-gate repair paths `.github/workflows/provider-ci.yml` and `tests/unit/test_provider_test_lanes.py`。The workflow preserves its name、`pull_request` trigger、job IDs `provider-tests` / `provider-distribution-parity`、Ubuntu/macOS matrix、checkout/head verification、Python/uv setup、static analysis。Only deleted test references are retargeted:

| Deleted S60 reference | Required S60 successor command |
|---|---|
| `tests/unit/infra/test_managed_distribution.py` | `uv run pytest tests/unit/infra/test_provider_lifecycle_model.py tests/unit/infra/test_provider_lifecycle_candidate.py tests/unit/infra/test_provider_lifecycle_filesystem.py tests/unit/infra/test_provider_lifecycle_service.py tests/unit/infra/test_provider_lifecycle_public_result.py tests/unit/infra/test_provider_lifecycle_faults.py tests/unit/infra/test_provider_assets.py tests/unit/infra/test_provider_test_ownership.py` |
| `tests/cli_runtime/test_distribution_cutover.py` | `uv run pytest --run-full-regression --full-regression-shard tests/cli_runtime/test_provider_lifecycle.py tests/cli_runtime/test_uninstall.py tests/cli_runtime/test_update.py` |
| `tests/integration/test_epic_00343_distribution.py` | `uv run pytest --run-full-regression --full-regression-shard tests/integration/test_provider_lifecycle_artifacts.py tests/integration/test_provider_lifecycle_tripwire.py` |
| platform-specific parity formerly embedded in old files | macOS-only conditional `uv run pytest --run-full-regression --full-regression-shard tests/platform/macos/test_provider_lifecycle_macos.py` |

`tests/unit/test_provider_test_lanes.py` removes constants/assertions pointing to deleted files、removes deleted `test_init_update.py` IDs from its mirrored required-fast set、and adds exact tests `test_s60_full_regression_ledger_has_zero_active_rows`、`test_s60_terminal_rows_are_resolved_by_collected_current_or_successor_nodes`、`test_s60_provider_ci_references_only_existing_successor_tests`。Accepted retirement rows use unique absence-proof successor nodes in `tests/unit/infra/test_provider_test_ownership.py` with pytest IDs `retire-<sha256(old_nodeid)[:12]>`; the temporary ledger encodes them as resolved/superseded because current observations carry no retirement evidence。

S60 retains current `tests/conftest.py`、`tests/unit/test_full_regression_baseline.py`、ledger、timing、quality scripts、`provider-full-regression.yml`。Deleted node references are updated mechanically。Active approved failure 0。Both PR workflow-equivalent commands and current main-push verifier must pass。No `scripts/provider_gate.py` dependency。PR-B main remains releasable。

### E384-D-018 — PR-C consumer-first atomic replacement

S70 same branch first adds `provider_gate.py`、environment files、final workflow、Makefile/static analysis、root `AGENTS.md`、and final gate tests。Before deleting any policy provider, it then retires or replaces every remaining current-policy consumer, including the exact files `tests/unit/test_provider_test_lanes.py` and `tests/unit/test_full_regression_baseline.py`。The transitional `.github/workflows/provider-ci.yml` is rewritten to the final topology; it is not deleted。

The required order is:

1. Add final gate tooling、environment、workflow、and replacement tests; establish RED for forbidden old consumers/providers。
2. Delete `tests/unit/test_provider_test_lanes.py` after its final-policy absence/collection responsibilities are represented in `tests/unit/infra/test_provider_gate.py` and `tests/unit/infra/test_provider_test_ownership.py`。
3. Delete `tests/unit/test_full_regression_baseline.py` after the old baseline evaluator has no final Product authority and replacement gate tests cover final fail-closed artifact/node/result evaluation。
4. Rewrite all remaining callsites in `.github/workflows/provider-ci.yml`、`AGENTS.md`、`pyproject.toml`、Makefile/static-analysis/test helpers。
5. Run a pre-provider-deletion consumer inventory for `tests.conftest`、`scripts.quality.full_regression_baseline`、`scripts.quality.verify_full_regression`、legacy pytest options、ledger/timing paths; only the provider files scheduled for deletion may remain。
6. Delete `tests/conftest.py`、both quality modules、ledger、timing、old main-push workflow、and marker policy。
7. Prove post-deletion imports/references 0、ordinary collection GREEN、final workflow references only existing tools/tests、and final provider gate GREEN。

S70 is non-main。S80 is the only PR-C merge gate。PR-B current gates and PR-C final gate are independent GREEN invariants; main never observes a provider without all consumers or a workflow with missing commands。

## 9. Final provider gate and environment

### E384-D-019 — Gate topology

Linux job verifies PR head、builds wheel/sdist once、verifies manifest/environment、runs one canonical pytest process/worker1、sdist smoke。macOS downloads same wheel andrunsdelta only。Aggregate `Provider CI / provider-gate` runsno tests/rebuild。No main-push Full Regression afterPR-C。

### E384-D-020 — Stable Linux qualification

Tracked:

```text
ci/linux-qualification.Dockerfile
ci/linux-qualification-environment.json
```

Environment ID `specdock-linux-qualification-v1`。Descriptor pinsrunner label、x86_64、base ref/digest、2 CPU、8 GiB、Python series、exact uv、lock hash。Evidence addsdescriptor SHA-256、built image ID、runner metadata、kernel/cgroup、full versions。All20 runs one environment orfingerprint-equal instances。Any mismatch invalidateswhole series。

## 10. Required-context transition

### E384-D-021 — No-gap order

Capture -> new GREEN whileold required -> addnew required/keepold -> read backboth -> dedicated non-merge canary RED -> proveblocked -> closecanary/implementation GREEN -> removeold provider-only -> final readback。Unreadable state、RED notblocking、unrelated/review drift ishard stop。

## 11. Specification and evidence graph

### E384-D-022 — Specification lineage

Manifest hashes bindexact Epic/Issue R/D/P、ADR、handoff、notes。Owner records`SPEC_FREEZE_COMMIT` afterimport。S00 verifiesblobs/ancestry。Repository evidence SHA isprovenance only。#387 delta isverified fromits ownbase/head/merge tree。Protected drift isseparate。

### E384-D-023 — Non-cyclic evidence

```text
tracked report commit -> final PR head freeze -> build/qualification
-> pre-merge external attestation -> human merge
-> merge tree OID equality -> SpecDock/GitHub closure
-> post-merge external attestations
```

Tracked report hasnoown hash/final head/post-merge facts。External canonical JSON isnew/never-edited andcontent-hashed。Tree equality comparesverified PR head tree tohuman merge commit tree, notlater `origin/main`。

## 12. Root AGENTS contract

### E384-D-024 — Final operator guidance

PR-C updatesroot `AGENTS.md` toretainprovider-first/dogfood andhuman-only merge、document`make lint`/`make provider-test`/`make provider-qualify` anddirect gate commands、one-process Linux/same-wheel macOS delta、human-admin required transition。Removeold flags、policy skip、ledger、shard、main-push Full Regression instructions。

## 13. Traceability

| Requirement | Design |
|---|---|
| E384-RQ-001〜003、008〜009 | D-003〜010 |
| E384-RQ-004、013、016 | D-017〜018 |
| E384-RQ-005〜007、010〜011 | D-007、D-011〜015 |
| E384-RQ-012 | D-016〜017 |
| E384-RQ-014〜015 | D-019〜020 |
| E384-RQ-017 | D-021 |
| E384-RQ-018〜019 | D-022〜023 |
| E384-RQ-020 | D-024 |
