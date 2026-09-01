---
種別: 設計書（Issue）
ID: "iss-00392"
タイトル: "Provider Lifecycle And Regression Gate Hard Cutover"
関連GitHub: ["#392"]
状態: "draft"
最終更新: "2026-09-01"
依存: ["requirement.md", "../../design.md", "../../artifacts/20260831t152024z-adr-single-implementation-unit-and-provider-hard-cutover-policy.md", "../../artifacts/provider-lifecycle-wire-contract.md", "../../artifacts/active-failure-disposition-register.md"]
親: ["epic-00384", "init-local-00003"]
repository_evidence:
  repository: "chemitaro/spec-dock"
  branch: "codex/epic-00384-provider-test-strategy-planning"
  sha: "d145f0f0d6f35535eebc0da89b7b708824279f1f"
---

# iss-00392 Provider Lifecycle And Regression Gate Hard Cutover — 設計

## 1. Production topology and exact symbols

Final production layout:

```text
src/spec_dock/
  cli.py
  context_pack.py
  provider_lifecycle/
    __init__.py
    model.py
    candidate.py
    filesystem.py
    legacy_023.py
    service.py
    public_result.py
  assets/legacy_0_2_3.json
scripts/provider_gate.py
ci/linux-qualification.Dockerfile
ci/linux-qualification-environment.json
tests/provider_test_ownership.json
```

Final tree removes `src/spec_dock/managed_distribution.py` and `src/spec_dock/assets/managed_distribution.json` after successor proof. Surviving non-lifecycle context rendering is extracted to `context_pack.py` without importing lifecycle journal/purge semantics.

`model.py` defines fixed paths、`LifecycleState`、`LifecycleOperation`、`LifecycleStatus`、`SeedPolicy`、`ResumeIdentity`、`InstallRecord`、`SlotMarker`、`Candidate`、`TargetObservation`、`LifecycleAction`、`LifecycleResult` and strict parsers/serializers. `candidate.py` owns packaged candidate capture/materialization/digest. `filesystem.py` owns root/parent/container binding、external stage、native rename、atomic publication and cleanup. `legacy_023.py` owns the exact one-generation recognizer. `service.py` owns classification/dispatch/install/update/uninstall/resume. `public_result.py` owns table-driven wire rendering only.

## 2. Lifecycle data and filesystem design

### I392-D-001 — Record and resume identity

The record is exact wire Artifact schema v3: seven ordered keys、max4096、regular nlink1、mode0644、compact UTF-8 one-LF JSON. Resume identity is exactly `(operation,candidate_digest,seed_policy)`. Any relation outside the Artifact is rejected before mutation.

### I392-D-002 — Candidate

Candidate targets are fixed in this order: docs、templates、system、scripts、spec-dock slot、grill slot. Digest stream includes schema marker、version、logical POSIX path、entry kind、mode、file size/content hash. It rejects symlink、special、hard link、absolute/traversal、case-fold/NFC collision. Seeds、record and generated slot marker are excluded.

### I392-D-003 — Slot marker

Each fixed slot contains `.spec-dock-provider-slot.json` with exact keys `schema_version,slot,version,candidate_digest`; compact UTF-8 one LF、mode0644、regular nlink1、max2048. Marker is excluded from candidate digest. New-record ownership requires exact marker; legacy ownership requires the single exact tree fixture.

### I392-D-004 — Stage owner

External candidate stage owner has exact compact fields:

```text
schema_version,kind,repository_device,repository_inode,operation,
candidate_digest,seed_policy,created_spec_dock_device,created_spec_dock_inode
```

Schema is 1、kind `provider-lifecycle-stage-owner`; created identity fields are both null or both positive integers. Owner is written/fsynced before fresh container creation and rewritten/fsynced after identity capture. Exact tuple mismatch blocks cleanup/resume.

### I392-D-005 — Classification order

1. bind repository root nofollow and lock;
2. observe record without following;
3. valid final record -> state-specific roots/slots/stage checks;
4. exact plain `0.2.3\n` -> legacy recovery probes and whole-tree fixture;
5. absent record -> shared container absent/real-dir check and fixed collision checks;
6. validate deterministic lifecycle stage ownership;
7. return exact observed state or one exact wire blocked code.

JSON-like invalid data never falls back to legacy. Existing real shared container may contain unknown protected children.

### I392-D-006 — Shared-container bootstrap

For absent container: candidate/stage/all other preflight first; capture root + absence witness; exclusive `mkdirat(root_fd,"spec-dock",0755)`; nofollow directory open; visible/held device/inode equality; fsync root; persist created identity to stage owner; then publish incomplete record. Failure before record removes only exact identity when empty. If identity changed、not empty、or removal/fsync fails, retain stage and return `bootstrap-cleanup-failed` under exact resume tuple. Existing container is never cleanup authority. Uninstall never removes it.

### I392-D-007 — Native publication

Repository root fd uses `O_RDONLY|O_DIRECTORY|O_NOFOLLOW|O_CLOEXEC` plus `flock(LOCK_EX)`. Parents open component-by-component relative to held fds. Linux uses `renameat2` with `RENAME_NOREPLACE`/`RENAME_EXCHANGE`; macOS uses `renameatx_np` with `RENAME_EXCL`/`RENAME_SWAP`. Missing symbol、EXDEV、unsupported OS、or unexpected identity has no generic fallback.

### I392-D-008 — Seed policy

Pure dispatch derives create only for init/init-force on never-installed absent. Every other lifecycle operation uses preserve. Resume validates recorded tuple and never re-derives from seed existence. Ready may retain prior create policy as provenance; the next update/uninstall first publishes preserve-only incomplete.

### I392-D-009 — Install/update protocol

```text
lock -> classify -> policy/candidate -> external stage/validate
-> bind/bootstrap container -> incomplete record
-> docs -> templates -> system -> scripts -> slot spec-dock -> slot grill
-> create absent seeds only for create-if-absent
-> verify target/protected witness -> terminal ready record -> cleanup
```

Each durable boundary invokes a private no-op production fault hook. Tests inject exact point IDs. Matching target is no-op on resume. Terminal record exists only after all target postconditions.

### I392-D-010 — Uninstall protocol

Removed purge trap is evaluated before target observation. Dry-run performs full safe classification and returns planned actions. Apply publishes preserve-only incomplete uninstall record、detaches six verified targets in fixed order、verifies target absence and protected preservation、publishes tooling-absent record、cleans stage. Shared container、seeds、user data remain.

### I392-D-011 — Resume

Record-present partial state requires exact tuple. Bootstrap-without-record additionally requires external stage owner and exact created container identity. No persistent action list or rollback image is stored. Current target observation determines completed/remaining actions. Cross tuple blocks without additional mutation.

### I392-D-012 — Closed public wire

`../../artifacts/provider-lifecycle-wire-contract.md` is loaded as normative test input. Production constructors are isomorphic to its exact tables. The generated 116-row relation table closes all 36 public codes, including every blocked phase pair and candidate/policy relation. Public arrays use `TARGET_PATH_ORDER`; failed/pending arrays exactly equal corresponding action statuses. No handwritten alternative enum、catch-all or fallback serializer exists.

## 3. #387 admission and failure terminalization

### I392-D-013 — #387 tracked pre-merge evidence

The tracked #387 report block schema is `iss-00387-pre-merge-disposition` v2. It records only repository、candidate head/tree and 12 conditional entries. It expressly excludes PR number/head、merge SHA/tree/time and close facts. Candidate head/tree refers to the immutable production/test/config candidate before final evidence-only report/plan commit; S00 verifies it against the actual PR head/tree rather than assuming tracked future values.

### I392-D-014 — S00 post-merge verification

S00 retrieves GitHub PR and merge objects after human merge and checks exact relations in register v3. It then reads report blob at PR head、post-merge ledger and collection. The output `post-387-admission.json` is schema v2 and lives only in external purpose `s00-admission`. Formula-derived admitted rows carry exact source signatures. Any stop code prevents S10.

### I392-D-015 — S60 terminalization

Outside rows follow their fixed row rule. Conditional rows follow only the admitted branch: removed=no row/reinsert; retained=same node normal pass; split=positives pass and optional lineage node normal pass. Final transitional ledger has active0/approved0; no skip/xfail/signature waiver. `tests/unit/test_provider_test_lanes.py` verifies formulas、mappings、terminal status and current evaluator parity until S70.

## 4. External temporary workspace and protected witness

### I392-D-016 — Portable external workspace creation

Allowed purpose enum, exactly:

```text
s00-admission
s50-artifact-proof
s60-dogfood-witness
s70-pre-freeze
s70-dogfood-witness
s80-final-run
provider-build-artifacts
provider-linux-canonical
provider-sdist-smoke
provider-macos-delta
provider-attestation
post-merge-closure
```

Creation algorithm:

1. `REPOSITORY_REALPATH` is obtained from an already opened real repository directory and recorded device/inode.
2. Base is absolute `SPEC_DOCK_EXTERNAL_TMPDIR` when set, otherwise `tempfile.gettempdir()`; lstat must be a real directory, not symlink; realpath must be outside repository (`commonpath` unequal repository root).
3. Create using `tempfile.mkdtemp(prefix="spec-dock-iss-00392-${purpose}-", dir=base)`; immediately chmod0700.
4. Open nofollow directory fd; lstat/fstat identity equal; owner uid equals effective uid; mode exactly0700.
5. Generate cryptographic 32-byte nonce and exclusively create `.spec-dock-iss-00392-owner.json` mode0600 with `O_CREAT|O_EXCL|O_NOFOLLOW`.
6. Sentinel exact keys: `schema_version,kind,purpose,repository_realpath_sha256,repository_device,repository_inode,workspace_device,workspace_inode,effective_uid,nonce`; schema1、kind `spec-dock-iss-00392-external-workspace`.
7. Collision or unsafe base/workspace/sentinel is never reused or cleaned and returns a typed stop.

All commands receive the exact exported `ISS392_EXTERNAL_TMP` path. No relative fallback and no repository `.workbench` path are accepted.

### I392-D-017 — Cleanup authority

Cleanup reopens nofollow and revalidates path realpath、device/inode、0700、uid、sentinel mode0600/nlink1/content/purpose/repository identity/nonce. Recursive removal allows only real directories owned by effective uid and regular files owned by effective uid with nlink1. Any symlink、hard link、special file、foreign uid、identity drift、missing/tampered sentinel、or unexpected mount leaves the entire workspace and fails; no partial cleanup. After successful removal, verify absence and fsync base. Only the creator purpose owner may cleanup.

### I392-D-018 — Complete protected witness

Witness includes the protected root itself and every descendant sorted by raw UTF-8 POSIX relative path bytes. Each row stores path、kind、mode、uid、gid; regular stores size/SHA-256/nlink; directory stores device/inode; symlink stores target bytes encoded safely and SHA-256 without following. Special files cause stop. The complete `spec-dock/.workbench` tree is included. Witness files are written outside repository before mutation and after comparison; comparison is exact row equality. Tests cover hidden/nested/empty dirs、symlinks、mode/link target changes、root replacement、and attempted output inside witnessed tree.

## 5. PR-B dogfood, documents, and current gates

### I392-D-019 — S40/S50 preserve exact dogfood

At S00 current dogfood identity is exact plain record `0.2.3\n` and two markerless slots. S40 owns provider-side lifecycle sources、root README lifecycle、provider docs only; it must not edit any `spec-dock/{docs,templates,system,scripts}` path、fixed slot、record or marker. S50 works only on external synthetic consumers. Byte witnesses before/after both steps must match the full checked-in dogfood fixed set.

### I392-D-020 — S60 complete migration

After S40/S50 code/docs are final, S60 applies the new lifecycle service once to repository root and commits all four roots、two slots、record and two markers together. Record is ready、operation null、version0.2.4、seed preserve-only、candidate digest matching all targets/markers. Provider/dogfood parity、validate、fresh consumer and protected external witness pass. No incomplete/stage/partial/markerless fixed target remains.

### I392-D-021 — Root AGENTS ownership split

S60 changes only lifecycle/uninstall instructions: uninstall tooling-only/default dry-run/apply、`--remove-specs` removed mutation-zero exit2、exact retry command/tuple. It does not change current pytest/full-regression/provider gate instructions. S70 later replaces only test-policy/provider-gate sections with final commands and human-required-context procedure, retaining S60 lifecycle text and provider-first/human-only merge.

### I392-D-022 — Transitional current gates

S60 `provider-ci.yml` keeps workflow name、events、job IDs、matrix、setup/static topology and retargets only deleted old test paths to existing lifecycle successors. Current main-push verifier and all its remaining consumers remain until S70. PR workflow and main-push workflow are independently GREEN. No `scripts/provider_gate.py` dependency at S60.

## 6. PR-C consumer-first replacement and dogfood update

### I392-D-023 — Consumer-first removal

S70 first adds final provider gate/environment/workflow/tests/AGENTS policy. It inventories and retires/replaces all imports/references to `tests.conftest` lane policy and `scripts.quality` full-regression modules, explicitly including `tests/unit/test_provider_test_lanes.py` and `tests/unit/test_full_regression_baseline.py`. AST/import/grep/collection/workflow structural tests prove consumer0. Only then are old providers/data/workflow/markers removed in the same non-main branch.

### I392-D-024 — Second complete dogfood update

After every S70 candidate byte settles, run one candidate-wide update and commit the entire new digest state. Provider roots/slots and dogfood roots/slots match; record/markers match the new digest; external protected witness/seeds unchanged; validate/fresh consumer pass. S80 is read-only and cannot repair dogfood.

## 7. Final Provider CI and self-contained evidence

### I392-D-025 — Exact jobs and needs

```text
provider-build-artifacts: []
provider-linux-canonical: [provider-build-artifacts]
provider-sdist-smoke: [provider-build-artifacts]
provider-macos-delta: [provider-build-artifacts]
provider-attestation: [provider-build-artifacts, provider-linux-canonical, provider-sdist-smoke, provider-macos-delta]
provider-gate: [provider-attestation]
```

`provider-build-artifacts` is the only packaging command for frozen head. Consumer jobs download identical candidate bytes and have build count0. Attestation only aggregates and verifies; gate only depends on attestation.

### I392-D-026 — Exact Actions artifact names

For source SHA `${SOURCE_SHA}`:

```text
provider-candidate-${SOURCE_SHA}
provider-receipt-producer-${SOURCE_SHA}
provider-receipt-linux-canonical-${SOURCE_SHA}
provider-receipt-sdist-smoke-${SOURCE_SHA}
provider-receipt-macos-delta-${SOURCE_SHA}
provider-evidence-${SOURCE_SHA}
```

Exactly one of each exists in the run; no unexpected provider-prefixed artifact.

### I392-D-027 — Candidate manifest

Candidate artifact contains exactly `candidate-manifest.json`、one wheel、one sdist. Manifest compact key order:

```text
schema_version,kind,repository,source_sha,source_tree,build_job_id,
workflow_run_id,build_invocation_count,wheel_filename,wheel_size,wheel_sha256,
sdist_filename,sdist_size,sdist_sha256,candidate_artifact_name,candidate_content_sha256
```

Schema1、kind `provider-candidate-manifest`、repository fixed、build job `provider-build-artifacts`、count1. Candidate content digest binds canonical manifest with its own content field null plus exact wheel/sdist bytes in fixed order.

### I392-D-028 — Receipt schema

Each receipt artifact contains exactly one role-fixed receipt JSON and one role-specific evidence JSON. Receipt exact key order:

```text
schema_version,kind,role,repository,source_sha,source_tree,workflow_run_id,
job_id,job_name,receipt_artifact_name,candidate_artifact_id,
candidate_artifact_name,candidate_artifact_digest,manifest_sha256,
wheel_filename,wheel_size,wheel_sha256,sdist_filename,sdist_size,sdist_sha256,
build_invocation_count,status,evidence_filename,evidence_size,evidence_sha256
```

Schema1、kind `provider-job-receipt`、status `passed`. Roles in fixed order: producer、linux-canonical、sdist-smoke、macos-delta. Job/artifact/evidence names are fixed: producer-build-evidence.json、linux-canonical-evidence.json、sdist-smoke-evidence.json、macos-delta-evidence.json. Producer count1; consumers0. Receipt does not embed its post-upload artifact ID/digest or own hash to avoid self-reference; aggregate binds those from Actions metadata.

### I392-D-029 — Role evidence schemas

- Producer evidence: schema/kind/role/repository/source SHA/tree/run/job、command argv、start/end、exit0、build invocation1、manifest/wheel/sdist names/sizes/hashes and candidate digest.
- Linux evidence: same identity、environment ID/descriptor/image/fingerprint、canonical node inventory hash、exact one pytest process/worker1、20 ordered run metrics、first-five budget booleans、fault inventory/detection100、flake/retry0、candidate hashes、build0.
- Sdist evidence: same identity、downloaded candidate hashes、installed metadata/package-data smoke commands/results、build0.
- macOS evidence: same identity、runner/macOS/Python、downloaded candidate hashes、exclusive node inventory、native rename/no-follow/mode/entry-point results、build0.

Every schema has exact ordered keys in `scripts/provider_gate.py` constants and table-driven golden tests. Unknown/additional keys or noncanonical bytes fail.

### I392-D-030 — Self-contained nine-file evidence artifact

Exact file order and set:

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

`provider-evidence.json` exact key order:

```text
schema_version,kind,repository,source_sha,source_tree,workflow_run_id,
evidence_artifact_name,candidate_artifact_id,candidate_artifact_name,
candidate_artifact_digest,candidate_content_sha256,manifest_sha256,
wheel_filename,wheel_size,wheel_sha256,sdist_filename,sdist_size,sdist_sha256,
producer_build_invocation_count,consumer_build_invocation_count,roles,file_manifest,status
```

Schema1、kind `provider-evidence`、status passed、producer1、consumer0. `roles` is fixed role order and each object has `role,job_id,job_name,receipt_artifact_id,receipt_artifact_name,receipt_filename,receipt_sha256,evidence_filename,evidence_size,evidence_sha256`. `file_manifest` lists the eight other files in exact order with filename、size、SHA-256; actual bytes are hashed. Aggregate does not include its own hash. After upload, verifier binds artifact ID/name/digest from API metadata externally.

### I392-D-031 — Attestation dataflow

Attestation downloads candidate and all four receipt artifacts plus run/jobs/artifacts API snapshots into external purpose `provider-attestation`; verifies exact bytes and schemas; normalizes receipt filenames; copies exact role evidence bytes; builds aggregate; reopens and rehashes all nine files; uploads exactly one evidence artifact. It runs no packaging/platform tests. Structural tests fail missing/duplicate/wrong needs、artifact、receipt/evidence file、upload、source/job/run/hash/build count.

### I392-D-032 — Exact downloaded verifier

Invocation:

```bash
uv run python scripts/provider_gate.py verify-downloaded-artifact \
  --repository chemitaro/spec-dock \
  --candidate-dir "$ISS392_EXTERNAL_TMP/candidate" \
  --evidence-dir "$ISS392_EXTERNAL_TMP/evidence" \
  --run-json "$ISS392_EXTERNAL_TMP/api/run.json" \
  --jobs-json "$ISS392_EXTERNAL_TMP/api/jobs.json" \
  --artifacts-json "$ISS392_EXTERNAL_TMP/api/artifacts.json" \
  --source-sha "$VERIFIED_PR_HEAD" \
  --source-tree "$VERIFIED_PR_TREE" \
  --workflow-run-id "$RUN_ID" \
  --json
```

Non-JSON success stdout: `provider-gate: downloaded artifact verified sha=${SOURCE_SHA} run=${RUN_ID}\n`. JSON success exact keys are `schema_version,status,code,repository,workflow_run_id,source_sha,source_tree,candidate_artifact,evidence_artifact,receipt_roles,evidence_files`; status `verified`、code `downloaded-artifact-verified`; candidate/evidence nested objects have `artifact_id,artifact_name,artifact_digest,file_count` with counts3/9; roles and evidence files use exact order. Failure stdout empty; stderr `provider-gate: ${CODE}: ${FIXED_MESSAGE}\n`.

| Exit | Code | Exact message |
|---:|---|---|
| 2 | `download-verify-invalid-arguments` | `Downloaded-artifact verification arguments are invalid.` |
| 3 | `download-verify-input-invalid` | `A downloaded verification input is missing, unsafe, malformed, or has an unexpected entry.` |
| 4 | `download-verify-run-identity-mismatch` | `The workflow run identity does not match the requested repository, source commit, and source tree.` |
| 5 | `download-verify-artifact-set-mismatch` | `The workflow artifact set is not the exact required candidate, receipt, and evidence set.` |
| 6 | `download-verify-artifact-metadata-mismatch` | `Downloaded artifact metadata does not match the workflow run metadata.` |
| 7 | `download-verify-candidate-manifest-invalid` | `The downloaded provider candidate manifest is invalid.` |
| 8 | `download-verify-candidate-bytes-mismatch` | `The downloaded candidate bytes do not match the candidate manifest.` |
| 9 | `download-verify-receipt-invalid` | `A downloaded provider job receipt is invalid.` |
| 10 | `download-verify-receipt-set-mismatch` | `The downloaded receipt set or workflow needs graph is invalid.` |
| 11 | `download-verify-build-count-mismatch` | `The provider build invocation counts violate the one-producer, zero-consumer-build contract.` |
| 12 | `download-verify-evidence-mismatch` | `The downloaded provider evidence bytes or their aggregate relations are invalid.` |

### I392-D-033 — Stable environment

`specdock-linux-qualification-v1` descriptor pins runner label、x86_64、container base ref/digest、2.0 CPU quota、8589934592 bytes memory、Python series/exact runtime、uv exact and lock hash. Linux evidence includes descriptor hash、image ID、runner image、kernel/cgroup and a canonical fingerprint. Every run matches; mismatch invalidates all metrics.

## 8. Human gate and evidence graph

Required-context order: capture old -> new GREEN while old required -> add new required keeping old -> read back both -> dedicated non-merge canary RED -> prove block -> close canary and restore implementation GREEN -> remove old provider-only -> final readback. Human alone changes settings and merges.

Tracked report contains no own hash/final head/final artifact/post-merge facts. Final external pre-merge attestation binds downloaded evidence and API snapshots after head freeze. Merge closure compares PR-head tree OID with merge-commit tree OID. Post-merge finish/Issue/Epic close facts remain external.

## 9. Traceability

I392-D-001–012 implement RQ-004–020. D-013–015 implement RQ-002–003/023. D-016–018 implement RQ-005–006. D-019–024 implement RQ-021–024/031–032. D-025–033 implement RQ-025–030. All are executed by S00–S80 in Issue Plan; no material choice remains.
