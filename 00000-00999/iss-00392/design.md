---
種別: 設計書（Issue）
ID: "iss-00392"
タイトル: "Provider Lifecycle And Regression Gate Hard Cutover"
関連GitHub: ["#392"]
状態: "draft"
最終更新: "2026-09-01"
依存: ["requirement.md", "../../design.md", "../../artifacts/20260831t152024z-adr-single-implementation-unit-and-provider-hard-cutover-policy.md"]
親: ["epic-00384", "init-local-00003"]
repository_evidence:
  repository: "chemitaro/spec-dock"
  branch: "codex/epic-00384-provider-test-strategy-planning"
  sha: "eaddf76806c338ee05463741f15fd3967bbceb57"
---

# iss-00392 Provider Lifecycle And Regression Gate Hard Cutover — 設計

Normative artifacts: `artifacts/provider-lifecycle-wire-contract.md` and `artifacts/active-failure-disposition-register.md` (Issue documents use `../../artifacts/...`). Their exact wire/disposition data is not delegated to implementation.


## 1. Exact production topology

```text
src/spec_dock/
  cli.py
  context_pack.py                                  (new)
  provider_lifecycle/                              (new)
    __init__.py
    model.py
    candidate.py
    filesystem.py
    legacy_023.py
    service.py
    public_result.py
  assets/legacy_0_2_3.json                         (new)

scripts/provider_gate.py                           (new, PR-C)
ci/linux-qualification.Dockerfile                  (new, PR-C)
ci/linux-qualification-environment.json            (new, PR-C)
tests/provider_test_ownership.json                 (new)
```

Final deletes old managed engine/manifest、ledger/timing/quality sharder、root policy hook、main-push Full Regression onlyatdefined PR boundaries。Non-lifecycle context rendering moves to`src/spec_dock/context_pack.py::render_context_pack()`。

## 2. Exact symbols

`model.py`: version/path constants、`SeedPolicy`、`ResumeIdentity`、states/operations/status、record/marker/candidate/observation/action/result/fault protocol、strict parsers。

`candidate.py`: packaged candidate build、materialize、candidate/tree digest、stage validate、seed source load。

`filesystem.py`: repository/parent/container bindings、staging owner、POSIX filesystem、container observe/bootstrap/cleanup、native rename、record/root/slot/seed publication/cleanup。

`legacy_023.py`: fixture/observation/recognizer/loader。

`service.py`: classify/install/update/uninstall/init/update dispatch/resume。

`public_result.py`: exit/text/JSON mappings。

## 3. Code-fixed paths

`SPEC_DOCK_CONTAINER=spec-dock`; roots docs/templates/system/scripts; slots exact two; seeds exact two; record `spec-dock/spec-dock.version`; slot marker `.spec-dock-provider-slot.json`。No arbitrary path arguments。

## 4. Strict data contracts

### I392-D-001 — Record

Seven exact keys。Max4096、regular/link1、UTF-8 duplicate-reject JSON。State/operation/policy relations perRequirement。Resume identity exact `(operation,candidate_digest,seed_policy)`。

### I392-D-002 — Candidate

Canonical `provider-candidate-v1` stream containsversion andsorted logical path/kind/mode/size/content hash entries。Unsafe kinds reject。Seeds/record/generated marker excluded。

### I392-D-003 — Slot marker

Exact schema/slot/version/candidate digest。Self excluded fromcandidate digest。

### I392-D-004 — Stage owner

Exact schema、root device/inode、operation、candidate digest、seed policy、created_spec_dock null ordevice/inode。Fsync beforebootstrap andafteridentity update。Mismatch blocks。

## 5. Descriptor-safe fresh bootstrap

### I392-D-005 — Classification order

Bind root -> probe record -> validate final state orlegacy -> ifabsent observecontainer absent/real/symlink -> requirefixed roots/slots absent -> stage collision -> result。Existing real container unknown child allowed。JSON-like invalid record neverlegacy fallback。

### I392-D-006 — Bootstrap algorithm

Stage/owner/preflight -> absence witness -> exclusive mkdirat -> no-follow open -> visible/held identity -> parent fsync -> stage owner identity fsync -> incomplete record。Pre-record exact empty cleanup yieldsblocked/mutation false/bootstrap_rolled_back true。Failure tocleanup retainsstage andpartial/mutation true。Existing container nevercleanup;uninstall neverdeletes。

## 6. Native filesystem protocol

Root fd nofollow/directory/cloexec + flock。Parents dirfd-relative。Visible/held revalidate。Linux renameat2 no-replace/exchange;macOS renameatx_np excl/swap。No fallback/EXDEV support。

## 7. Dispatch and operation protocol

### I392-D-007 — Pure seed policy derivation

Create onlyinit/init-force + never-installed absent。Allother install/update/migration/uninstall preserve。Resume usesrecorded exact,notderivation fromseed state。

### I392-D-008 — Install/update

Lock/classify/policy/candidate/stage/bootstrap/incomplete/roots/slots/policy seeds/postcondition/ready/cleanup。Ready fromfresh may retaincreate policy asprovenance;later update beginsnew preserve operation andneverrecreates seeds。

### I392-D-009 — Uninstall

Remove-specs trap beforetarget observation。Then dry-run orapply incomplete preserve -> detach roots/slots -> protect/container validation -> tooling-absent preserve -> cleanup。

### I392-D-010 — Resume

Exact request/stage/record tuple。Bootstrap-without-record additionally exactcreated identity。Matching target no-op。No persistent progress list。Cross tuple blocked。

## 8. Legacy and tripwire

Single `legacy_0_2_3.json` whole-tree fixture。Migration/uninstall preserve-only。Composite sitecustomize interceptsPython audit/native symbols beforecall。Positive controls mandatory。

## 9. Public result

Result fields: status/code/operation/candidate/policy/mutation/bootstrap rollback/phase/actions/failed/pending/retry/warnings/errors。Uninstall JSON schema1 retainsmain fields andadds code/policy/mutation/bootstrap fields。

## 10. Tests

Final test paths includemodel/candidate/filesystem/service/public/fault/assets/ownership/gate、CLI lifecycle/uninstall/update、artifact/tripwire、macOS delta、tripwire support、ownership JSON。

Required policy tests: fresh seed faults resume create; update/reinstall/migration faults nevercreate; tamper/missing/unknown policy block; later update does notreusefresh create;uninstall terminal preserve;stage mismatch block。

Required container tests: absent success、existing real + unknown child、symlink/non-dir、absence race、failure aftermkdir/beforeowner/beforerecord、empty cleanup、cleanup failure/foreign child partial、uninstall keepscontainer、no recursive cleanup。

## 11. PR-B transitional workflow and lane consumers


### I392-D-011 — S60 conditional register, current-gate repair, and dogfood migration

S60 exact owned surfaces include:

```text
.github/workflows/provider-ci.yml
tests/unit/test_provider_test_lanes.py
full-regression-ledger.json
full-regression-timing-weights.json
tests/conftest.py
old engine/test deletion paths
README lifecycle sections
src/spec_dock/assets/spec_dock/docs/migration.md
src/spec_dock/assets/spec_dock/docs/README.md
spec-dock/docs/migration.md
spec-dock/docs/README.md
spec-dock/{docs,templates,system,scripts}
.agents/skills/spec-dock
.agents/skills/spec-dock-grill-with-docs
spec-dock/spec-dock.version
two slot marker files
```

The current provider workflow retainsname/event/job IDs/matrix/setup andretargetsdeleted tests totheseexisting groups:

```text
unit: tests/unit/infra/test_provider_lifecycle_model.py
      tests/unit/infra/test_provider_lifecycle_candidate.py
      tests/unit/infra/test_provider_lifecycle_filesystem.py
      tests/unit/infra/test_provider_lifecycle_service.py
      tests/unit/infra/test_provider_lifecycle_public_result.py
CLI:  tests/cli_runtime/test_provider_lifecycle.py
      tests/cli_runtime/test_uninstall.py
      tests/cli_runtime/test_update.py
artifact: tests/integration/test_provider_lifecycle_artifacts.py
          tests/integration/test_provider_lifecycle_tripwire.py
macOS: tests/platform/macos/test_provider_lifecycle_macos.py
```

`test_provider_test_lanes.py` validates the#387 report-driven admission formula、allS60 ledger rows resolved、active0、exact successor existence andcurrent evaluator parity。The main-push verifier remainsoperational。

Afterdocs/code areprovider-first complete, the exact command`uvx --no-cache --from . spec-dock update .` migratesdogfood fromplain0.2.3/markerless slots。Aread-only parser verifiesseven record keys、state ready、operation null、version0.2.4、seed preserve-only、candidate digest andboth marker digests。Allprotected witnesses andseed hashes remainidentical。
## 12. PR-C consumer-first gate replacement


### I392-D-012 — Exact S70 consumer-first retirement set and dogfood update

S70 first createsfinal gate/environment/workflow/tests/AGENTS/docs。Itthen inventories andretires/replacesall remaining consumers beforedeleting providers。Mandatory consumer set includes:

```text
tests/unit/test_provider_test_lanes.py
tests/unit/test_full_regression_baseline.py
all tests importing tests.conftest.build_candidate_observation
all code/tests importing scripts.quality.full_regression_baseline
all code/tests importing scripts.quality.verify_full_regression
Makefile/static-analysis/workflows/docs/AGENTS old flags andpaths
```

Final tests ownonlynode ownership、artifact/receipt verification、workflow structure、budget/environment anddo notcopyfailure-approval semantics。Consumer0 isprovedbeforeprovider deletion。Afterallcandidate docs bytes settle, S70 runs`uvx --no-cache --from . spec-dock update .` andcommitscomplete dogfood state matchingthe newcandidate digest。S70 is not mergeable;S80 isread-only。

### I392-D-013 — Provider gate CLI, exact downloaded-artifact verifier, andenvironment

Final subcommands are:

```text
freeze-linux-environment
build
verify-artifact
verify-environment
verify-node-ownership
canonical
sdist-smoke
macos-delta
qualify
verify-downloaded-artifact
emit-attestation
```

`verify-downloaded-artifact` exact invocation:

```bash
uv run python scripts/provider_gate.py verify-downloaded-artifact   --repository chemitaro/spec-dock   --candidate-dir <existing-real-directory>   --evidence-dir <existing-real-directory>   --run-json <regular-file>   --artifacts-json <regular-file>   --source-sha <40-lowercase-hex>   --source-tree <40-lowercase-hex>   --workflow-run-id <positive-decimal>   [--json]
```

No optional expected job/artifact names areaccepted; names arecode-fixed byI392-D-019。Without `--json`, stdout is exactly `provider-gate: downloaded artifact verified sha=<sha> run=<id>\n`。With `--json`, stdout is one compact JSON object plus LF with exact keys `schema_version,status,code,repository,workflow_run_id,source_sha,source_tree,candidate_artifact,evidence_artifact,receipt_roles` and code `downloaded-artifact-verified`。Failure stdout is empty and stderr is exactly `provider-gate: <code>: <message>\n`。

Typed failure exits:

| Exit | Code | Condition |
|---:|---|---|
| 0 | `downloaded-artifact-verified` | allcontracts pass |
| 2 | `download-verify-invalid-arguments` | CLI/schema argument invalid |
| 3 | `download-verify-input-invalid` | input missing、non-regular、symlink、invalid JSON |
| 4 | `download-verify-run-identity-mismatch` | repository/run/head/tree mismatch |
| 5 | `download-verify-artifact-set-mismatch` | required artifact missing/duplicate/unexpected |
| 6 | `download-verify-artifact-metadata-mismatch` | Actions ID/name/digest/run mismatch |
| 7 | `download-verify-candidate-manifest-invalid` | manifest field/schema/build producer invalid |
| 8 | `download-verify-candidate-bytes-mismatch` | wheel/sdist/manifest hash orsize mismatch |
| 9 | `download-verify-receipt-invalid` | receipt schema/role/job/source/hash invalid |
| 10 | `download-verify-receipt-set-mismatch` | missing/duplicate/wrong role orneeds graph |
| 11 | `download-verify-build-count-mismatch` | producer not1 orconsumer not0 |
| 12 | `download-verify-evidence-mismatch` | evidence content/hash/upload identity mismatch |

No generic failure code。Unexpected exceptions aretest/CI defects andare not serialized asacontract code。

Environment remains`specdock-linux-qualification-v1` withpinned descriptor、2CPU、8GiB、x86_64、Python/uv/lock fingerprint; mismatch invalidatesallruns。
## 13. Required context

Old retained -> newGREEN -> add new required/keepold -> read-backboth -> dedicated non-merge canary RED/block -> closecanary/implementation GREEN -> remove old -> final read-back。No setting write ifunreadable。

## 14. Specification and evidence

### I392-D-014 — S00 identities

`REPOSITORY_EVIDENCE_SHA`、manifest payload hashes、`SPEC_FREEZE_COMMIT`、#387 base/head/merge tree、implementation base areseparate。No stale self-diff。

### I392-D-015 — Attestations

`pre-merge-attestation-v1` canonical JSON includesfinal head/tree、report blob observedexternally、artifact/environment/test/context evidence andJSON hash。Post-merge/epic attestations includeclosure events。Neverwritten totracked report。

Tree compare exact PR head tree OID vsmerge commit tree OID。

## 15. Root AGENTS

S70 updatesroot AGENTS。Final positive commands andprovider-first/human gate required;old flags/ledger/shard/main-push guidance forbidden。S80 validates。

## 16. PR-B documentation design

### I392-D-016 — Exact lifecycle documentation set

S40 changes lifecycle semantics onthePR-B branch; S60 ismerge-ready owner of:

```text
README.md                                      # lifecycle subsections
src/spec_dock/assets/spec_dock/docs/migration.md
legacy projection: spec-dock/docs/migration.md
src/spec_dock/assets/spec_dock/docs/README.md
legacy projection: spec-dock/docs/README.md
```

Despite the label `legacy projection` above, the two `spec-dock/docs/**` paths arecurrent dogfood projections, nothistorical evidence。Provider files areeditedfirst; `cmp` provespair equality。Exact forbidden active-lifecycle phrases at S60:

```text
spec-dock/.distribution-journal.json
spec-dock/.distribution-retry.json
spec-dock/.uninstall-retry.json
current explicit spec-history purge authority
--apply --remove-specs
compatible newer package
protocol 2 journal
empty spec-dock boundary / 空の spec-dock
```

Historical `spec-dock/initiatives/**` isexcluded。README/docs test-policy text remainsuntilS70; S70 replaces`--run-full-regression`/main-push guidance。S80 performsread-only drift verification only。

## 17. Normative wire implementation


### I392-D-017 — Wire source and tests

`provider-lifecycle-wire-contract.md` isimported asnormative test data。Production enums andserializers mustbeisomorphic toits closedtables。Tests enumerateeveryrecord relation、phase adjacency、action reason relation、code matrix row、path order andexact JSON/text golden。Unknown token/reason/code/path、duplicate array entry orwrong order isRED。No handwritten test-local alternative enum isauthoritative。
## 18. Failure register implementation


### I392-D-018 — Register admission and terminalization

S00 parser readsregister schema v2 andthe#387 report block markers, thenvalidatespost-#387 merge tree/ledger/collection。For eachrows4〜15 itappliesexactly one branch:

- removed: old absent, positive successors + absence evidence, nofailure lineage;
- retained unchanged: old present, same signature, retain reason;
- split/renamed: exact mapping, positive successors, zero/one failure-lineage node with same signature。

The admitted row count follows the register formula, neveraliteral15。S60 fixesalladmitted active rows andpreservesremoved/no-lineage original history onlyinregister。Anyunmapped node、missing report entry、signature drift、multiple lineage orout-of-contract tree returnsastop code before S10;Luna does notchoosearepair。
## 19. Frozen-head packaging dataflow


### I392-D-019 — Workflow jobs, immutable receipts, and attestation dataflow

Exact jobs and`needs`:

```text
provider-build-artifacts: []
provider-linux-canonical: [provider-build-artifacts]
provider-sdist-smoke: [provider-build-artifacts]
provider-macos-delta: [provider-build-artifacts]
provider-attestation:
  [provider-build-artifacts, provider-linux-canonical, provider-sdist-smoke, provider-macos-delta]
provider-gate: [provider-attestation]
```

Exact Actions artifacts:

```text
provider-candidate-<sha>
provider-receipt-producer-<sha>
provider-receipt-linux-canonical-<sha>
provider-receipt-sdist-smoke-<sha>
provider-receipt-macos-delta-<sha>
provider-evidence-<sha>
```

Candidate artifact contains only `candidate-manifest.json`、one wheel、one sdist。`candidate-manifest.json` is canonical compact JSON plus LF with exact keys/order:

```text
schema_version,kind,repository,source_sha,source_tree,
build_job_id,workflow_run_id,build_invocation_count,
wheel_filename,wheel_size,wheel_sha256,
sdist_filename,sdist_size,sdist_sha256,
candidate_artifact_name,candidate_content_sha256
```

Exact values: `schema_version=1`、`kind="provider-candidate-manifest"`、repository `chemitaro/spec-dock`、producer job `provider-build-artifacts`、build count `1`、candidate artifact `provider-candidate-<source_sha>`。`candidate_content_sha256` is SHA-256 of the canonical ordered tuple `(manifest-with-this-field-null, wheel bytes, sdist bytes)` and is repeated in Actions artifact metadata/receipts。Unknown or reordered fields are invalid。

Producer receipt and each consumer receipt use `provider-job-receipt-v1` exact keys:

```text
schema_version,kind,role,repository,source_sha,source_tree,
workflow_run_id,job_id,job_name,receipt_artifact_name,
candidate_artifact_id,candidate_artifact_name,candidate_artifact_digest,
manifest_sha256,wheel_filename,wheel_size,wheel_sha256,
sdist_filename,sdist_size,sdist_sha256,build_invocation_count,
status,evidence_filename,evidence_sha256
```

`kind="provider-job-receipt"`。Role/job/receipt artifact/evidence filename are exact:

| Role | `job_name` | `receipt_artifact_name` | `evidence_filename` | Build count |
|---|---|---|---|---:|
| `producer` | `provider-build-artifacts` | `provider-receipt-producer-<sha>` | `producer-build-evidence.json` | 1 |
| `linux-canonical` | `provider-linux-canonical` | `provider-receipt-linux-canonical-<sha>` | `linux-canonical-evidence.json` | 0 |
| `sdist-smoke` | `provider-sdist-smoke` | `provider-receipt-sdist-smoke-<sha>` | `sdist-smoke-evidence.json` | 0 |
| `macos-delta` | `provider-macos-delta` | `provider-receipt-macos-delta-<sha>` | `macos-delta-evidence.json` | 0 |

Status is exact `passed`。`evidence_sha256` hashes the exact role-specific evidence file bytes。A receipt artifact contains exactly its one receipt JSON plus its one evidence JSON; their names are role-fixed。Own receipt SHA-256 is deliberately not embedded in the receipt to avoid self-reference; `provider-attestation` computes it after download and records it in `provider-evidence.json`。

`provider-attestation` downloads the candidate plus four receipt artifacts, fetches Actions run/artifact metadata, runs I392-D-013 verifier, and uploads exactly one `provider-evidence-<sha>`。That artifact contains exactly:

```text
provider-evidence.json
provider-receipt-producer.json
provider-receipt-linux-canonical.json
provider-receipt-sdist-smoke.json
provider-receipt-macos-delta.json
```

`provider-evidence.json` is canonical compact JSON plus LF with exact keys/order:

```text
schema_version,kind,repository,source_sha,source_tree,workflow_run_id,
candidate_artifact_id,candidate_artifact_name,candidate_content_sha256,
manifest_sha256,wheel_filename,wheel_size,wheel_sha256,
sdist_filename,sdist_size,sdist_sha256,producer_build_invocation_count,
consumer_build_invocation_count,receipt_artifacts,receipt_sha256_by_role,status
```

Exact values: schema `1`、kind `provider-evidence`、status `passed`、producer count `1`、consumer count `0`。`receipt_artifacts` is an array in exact role order `producer,linux-canonical,sdist-smoke,macos-delta`; each item has exact keys `role,artifact_id,artifact_name,receipt_filename,evidence_filename`。`receipt_sha256_by_role` is an object in the same role order and each value hashes the downloaded receipt JSON bytes。`provider-attestation` must not package or run platform tests。`provider-gate` depends only on attestation and checks its success。

Workflow structural tests areRED foranymissing/duplicate producer、consumer build command、wrong/missing `needs`、missing/duplicate receipt upload/download、wrong artifact name、more/less thanone evidence upload、source/hash/build-count mismatch。

### I392-D-020 — Dogfood state transition

S00 source state isexact plain`0.2.3\n` with two markerless fixed slots。S60 uses new code todirectly migrate repository root andcommitscomplete S60 candidate state。S70 uses new code toupdate thatready state aftercandidate changes andcommitscomplete S70 state。Atbothpoints:

- four roots andtwo slots digest tothepackaged candidate;
- record hasexactseven-keys、ready/null operation/version0.2.4/preserve-only/current digest;
- both markers matchversion/digest;
- provider/dogfood docs parity passes;
- initiatives/artifacts/workbench/seeds/user data witness isunchanged;
- validate andfresh consumer pass;
- no incomplete record、ownedstage、partial slot/root ormarkerless fixed slot remains。

S80 hasno tracked ownership andmust notrunupdate/sync。
## 20. Traceability

| Requirement | Design |
|---|---|
| RQ-001 | D-014 |
| RQ-002〜003、008〜012 | D-005〜010 |
| RQ-004〜005 | D-001、D-004、D-007〜010 |
| RQ-006〜007 | D-002〜003 |
| RQ-013〜019 | D-007〜010、public result |
| RQ-020 | D-011、D-018 |
| RQ-021〜023 | D-012〜013、D-019 |
| RQ-024 | required-context section |
| RQ-025〜026 | D-015、root AGENTS section |
| RQ-027 | D-016 |
| RQ-028 | D-017 and normative wire artifact |
| RQ-029 | D-014、D-018 and normative register |
| RQ-030 | D-013、D-019 |
| RQ-031 | D-011〜012、D-020 |
