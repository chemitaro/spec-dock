---
種別: 設計書（Issue）
ID: "iss-00392"
タイトル: "Provider Lifecycle And Regression Gate Hard Cutover"
関連GitHub: ["#392"]
状態: "draft"
最終更新: "2026-09-02"
依存: ["requirement.md", "../../design.md", "../../artifacts/20260831t152024z-adr-single-implementation-unit-and-provider-hard-cutover-policy.md", "../../artifacts/provider-lifecycle-wire-contract.md", "../../artifacts/active-failure-disposition-register.md"]
親: ["epic-00384", "init-local-00003"]
repository_evidence:
  repository: "chemitaro/spec-dock"
  branch: "codex/epic-00384-provider-test-strategy-planning"
  sha: "95d7562ca1762e0b2a717912484eba5a5c2377f1"
---

# iss-00392 Provider Lifecycle And Regression Gate Hard Cutover — 設計

## 1. Production topology and exact symbols

```text
src/spec_dock/
  cli.py
  context_pack.py
  provider_lifecycle/
    __init__.py
    model.py
    candidate.py
    filesystem.py
    external_workspace.py
    stage_namespace.py
    legacy_023.py
    service.py
    public_result.py
  assets/legacy_0_2_3.json
scripts/provider_gate.py                    S70
ci/linux-qualification.Dockerfile           S70
ci/linux-qualification-environment.json     S70
```

Exact exported symbols include fixed path constants; lifecycle state/operation/status/seed-policy/result-family enums; `ResumeIdentity`; strict record/marker/result/action types; candidate capture/digest/materialize; descriptor/native filesystem; workspace handles; namespace/ACTIVE/stage owner types; classification/install/update/uninstall/resume/terminal-cleanup; and table-driven wire rendering.

## 2. Lifecycle, candidate and closed wire

### I392-D-001 — Model

The strict record and public result are defined only by `provider-lifecycle-wire-contract.md`. Candidate digest includes final version plus sorted logical path/kind/mode/content entries for four roots/two slots, excluding seeds/record/generated markers. Unknown enum/value cannot be represented.

Private `LifecycleResultFamily` is exact `install|legacy-migration|update|uninstall`. It is stored in ACTIVE/stage owner but not in the durable record, resume tuple or public result.

### I392-D-002 — Protocol order

Every invocation:

```text
repository lock/bind
-> recover_terminal_cleanup
-> classify/admit requested operation
-> candidate/stage/target preflight as applicable
-> incomplete record
-> fixed target publication/detach
-> verify
-> terminal record
-> attempt terminal stage cleanup
-> result
```

Parser validation first normalizes the actual invocation echo; parser errors and the removed-purge trap bypass cleanup. For every other lifecycle invocation, the terminal-cleanup prelude runs before target classification. If pending cleanup succeeds it returns cleanup-only `terminal-cleanup-completed`; it never continues into the requested operation in the same invocation.

### I392-D-003 — Wire integration

Tests parse the normative artifact and assert 38 codes, 136 rows, four record goldens, twenty-nine public review goldens, phase/reason/order inventories and exact JSON/text bytes. A typed result selects exactly one row; zero/multiple match is a programming defect.

## 3. Persistent lifecycle stage namespace

### I392-D-004 — Paths and identities

```text
namespace = repository_realpath.parent / ".spec-dock-provider-stages-v1"
repository_key = sha256(repo_realpath_utf8 + NUL + st_dev_decimal + NUL + st_ino_decimal)
tuple_key = sha256(operation + NUL + candidate_digest + NUL + seed_policy)
repo_dir = namespace / "repositories" / repository_key
active = repo_dir / "ACTIVE.json"
stage = repo_dir / "stages" / tuple_key
```

All directories are real/current-UID/mode0700/same filesystem; JSON files regular/link-count-one/mode0600. No scan or glob is used.

### I392-D-005 — Exact sentinels

`NAMESPACE.json` keys:

```text
schema_version,kind,purpose,owner_uid,parent_device,parent_inode,created_at
```

Kind `spec-dock-stage-namespace`, purpose `provider-lifecycle-stage-v1`.

`REPOSITORY.json` keys:

```text
schema_version,kind,repository_key,repository_realpath_sha256,
repository_device,repository_inode,owner_uid
```

`ACTIVE.json` keys:

```text
schema_version,kind,state,repository_key,operation,candidate_digest,
seed_policy,result_family,tuple_key,stage_relative_path,created_at,updated_at
```

State `allocating|ready|terminal-cleanup`; result family exact private enum; stage path exact `stages/<tuple-key>`.

`STAGE-OWNER.json` keys:

```text
schema_version,kind,purpose,repository_key,repository_realpath_sha256,
repository_device,repository_inode,operation,candidate_digest,seed_policy,
result_family,tuple_key,stage_device,stage_inode,created_spec_dock,
registered_entries
```

`created_spec_dock` is null or exact `{device,inode}`. Registered entries are unique UTF-8-bytewise relative paths.

### I392-D-006 — Allocation, lifecycle resume and terminal cleanup

1. Validate/create namespace/repository sentinels descriptor-safely.
2. Read exact ACTIVE only.
3. No ACTIVE: no-replace publish allocating for requested tuple/family, create exact stage, write owner, promote ready.
4. ACTIVE allocating/ready with nonterminal operation: same tuple/family resumes; mismatched request returns `stage-owner-mismatch`.
5. Terminal record + ACTIVE ready: atomically promote same bytes to terminal-cleanup and fsync.
6. Terminal-cleanup validates ACTIVE/owner/record identity, removes only registered entries and exact stage. Stage already absent is valid.
7. Remove ACTIVE only by expected-byte/content binding and fsync repo_dir. ACTIVE already absent causes repo_dir fsync and success.
8. Crash after ACTIVE unlink before fsync is recovered by step 7 next invocation.
9. ACTIVE absent at invocation start causes parent fsync and normal dispatch; no cleanup result exists because no old tuple can be exposed.
10. Cleanup success from present ACTIVE returns cleanup-only `terminal-cleanup-completed` with the actual invocation echo and old ACTIVE tuple, then exits 0. Caller re-runs the requested command.
11. Cleanup failure returns `terminal-cleanup-failed` with the actual invocation echo and old-family retry, then exits 1. It does not classify the new request.
12. Namespace/repository sentinels remain; unknown siblings are never inspected or removed.

Tests kill/restart subprocesses after ACTIVE allocation, owner write, container mkdir, terminal record, ACTIVE terminal-cleanup write, stage removal and ACTIVE unlink.

## 4. Independent ephemeral workspaces and protected witness

### I392-D-007 — Workspace helper, child registration and lifetime

`create_external_workspace(repository,purpose,parent=None) -> ExternalWorkspaceHandle` returns a non-serializable object holding parent/root FDs, exact root device/inode/UID/mode, sentinel bytes, nonce, reservations and lifecycle state. `workspace_path(handle)` may be exposed to a child, but `cleanup_external_workspace()` accepts only the live handle.

Exact purpose/env mapping remains:

| Purpose | Environment variable |
|---|---|
| admission | `ISS392_WS_ADMISSION` |
| baseline-build | `ISS392_WS_BASELINE_BUILD` |
| protected-witness | `ISS392_WS_PROTECTED_WITNESS` |
| full-regression-s00 | `ISS392_WS_FULL_REGRESSION_S00` |
| full-regression-s30 | `ISS392_WS_FULL_REGRESSION_S30` |
| full-regression-s60 | `ISS392_WS_FULL_REGRESSION_S60` |
| tripwire | `ISS392_WS_TRIPWIRE` |
| fresh-consumer | `ISS392_WS_FRESH_CONSUMER` |
| workflow-api | `ISS392_WS_WORKFLOW_API` |
| artifact-download | `ISS392_WS_ARTIFACT_DOWNLOAD` |
| attestation-draft | `ISS392_WS_ATTESTATION_DRAFT` |

Each path is independently created by `tempfile.mkdtemp(prefix="spec-dock-iss-00392-",dir=validated_parent)`. No aggregate root or implicit subpurpose exists. `OWNER.json` exact keys remain `schema_version,kind,issue_id,purpose,repository_realpath_sha256,owner_uid,nonce,root_device,root_inode,created_at` and are O_EXCL/O_NOFOLLOW mode0600 compact+LF.

The executable registration contract is I392-D-024: owner reserves one top-level tree before child launch; child writes descendants only; owner seals descriptor-walked inventory after exit; unknown/unregistered entries fail closed; a background owner retains FDs through Actions upload and cleans only after upload confirmation. A path, environment variable, nonce or sentinel alone never grants cleanup authority.

### I392-D-008 — Protected/exclusion manifests

`protected-manifest.json` lives only in `ISS392_WS_PROTECTED_WITNESS`. It includes every repository workbench and all protected paths, sorted by UTF-8 bytes. Entry keys: `path,kind,mode,uid,gid,size,sha256,link_target_hex,device_major,device_minor` with null for nonapplicable values.

Excluded only exact #392 report and meta. `authorized-exclusions.json` exact keys are `schema_version,repository,base_tree,current_tree,entries`; entries bind path/kind/modes/blobs/parents/step/role/semantic-diff hash. Report permits only pre-freeze method/step evidence and explicitly forbids actual compatibility/final identities. Meta permits only `updated_at`.

## 5. Issue #387 `ISS387-THREE-WAY-V2`

### I392-D-009 — Mapping-only report

Exact report block top-level keys are:

```text
schema_version,kind,issue_id,rule_id,entries
```

Schema4, kind `iss-00387-pre-merge-disposition`, issue `iss-00387`, rule `ISS387-THREE-WAY-V2`, entries12. Entry schema is the register. Identity/timestamp/hash fields are rejected.

### I392-D-010 — Unique merged PR discovery

S00 fetches Issue #387 timeline. For every same-repository PR reference, fetch PR object and `GET /repos/chemitaro/spec-dock/commits/<pr-head-sha>/pulls`; keep only exact association with same PR number, base main, merged, report present and merge reachable. Require one. Fetch head/merge commits and require tree equality. Read report/ledger/collection from merge tree and apply register. No report PR/candidate identity and no extra #387 commit boundary.

## 6. PR-B current gate and dogfood

### I392-D-011 — S40/S50/S60

S40/S50 preserve checked-in dogfood. S60 owns current provider-ci retarget, retained workflow external output, ledger/timing/conftest/lane consumers, old engine/test removal, lifecycle docs/AGENTS paragraphs, admitted fixes and complete dogfood migration.

The retained workflow starts the background workspace owner, reserves/seals the exact Full Regression output tree, retains owner FDs through `actions/upload-artifact`, marks upload-confirmed with actual artifact identity, and only then handle-cleans. Upload failure preserves the workspace and fails the job. It does not use repository workbench or an aggregate workspace.

### I392-D-012 — Complete dogfood checkpoints

S60 migrates once after all PR-B candidate bytes settle; S70 updates once after all final candidate bytes settle. Each has complete root/slot/record/marker parity, protected witness equality, seed equality, no ACTIVE/stage residue, validate and fresh-consumer proof. S80 is read-only.

## 7. Final Provider CI topology

### I392-D-013 — Compatibility and final jobs

Compatibility exact graph:

```text
provider-build-artifacts: []
provider-linux-canonical: [provider-build-artifacts]
provider-sdist-smoke: [provider-build-artifacts]
provider-macos-delta: [provider-build-artifacts]
provider-attestation: [provider-build-artifacts,provider-linux-canonical,provider-sdist-smoke,provider-macos-delta]
provider-gate: [provider-attestation]
provider-tests: [provider-build-artifacts,provider-attestation]
```

Compatibility `provider-tests`:

- permissions exact `actions:read`, `contents:read`, `pull-requests:read`;
- creates independent workflow-api and artifact-download workspaces/handles;
- downloads `provider-candidate-${SOURCE_SHA}` and `provider-evidence-${SOURCE_SHA}`;
- GETs and writes exact run, jobs and artifacts API response bytes;
- invokes I392-D-020 with candidate/evidence/API inputs and exact source/run identity;
- invokes no packaging and does not read the canary marker;
- cleans through its handles after verification.

Only `provider-gate` reads `.github/provider-gate-canary-red`. Final head removes only provider-tests and is distinct. All other workflow bytes stay equal; final run reruns all authority.

### I392-D-014 — Artifacts

Candidate artifact exact files: candidate manifest, one wheel, one sdist. Each receipt artifact has one receipt and one role evidence file. `provider-evidence-<sha>` has exactly nine files in this order:

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

## 8. Normative Provider Gate byte and CLI contract

### I392-D-015 — Authority and canonical scalars

This section is the sole normative wire authority for `scripts/provider_gate.py`, its role evidence, Actions receipts, aggregate evidence and external attestations. `EVIDENCE-FIXTURE-V2` is a serializer conformance vector containing synthetic but schema-valid literals; runtime values are not required to equal fixture IDs, paths or timestamps. Runtime values must satisfy the ranges and relations below. No field, enum, nullability, unit, ordering, exit mapping or semantic-digest input is implementation-defined.

All JSON bytes use UTF-8, no BOM/NUL, the displayed key order, `ensure_ascii=False`, separators `(",",":")`, no duplicate or additional keys, and exactly one final LF. Nested object/array order is normative.

| Scalar | Exact runtime contract |
|---|---|
| `GitOid` | 40 lowercase hexadecimal characters. |
| `Sha256` | 64 lowercase hexadecimal characters. |
| `ActionsDigest` | `sha256:` followed by `Sha256`. |
| `PositiveId` | JSON integer `1..9007199254740991`; boolean rejected. |
| `RunAttempt` | JSON integer `1..100`. |
| `ByteSize` | JSON integer `1..9223372036854775807`. |
| `Count` | JSON integer `0..1000000`, further fixed per field. |
| `UtcSecond` | exact `YYYY-MM-DDTHH:MM:SSZ`, Gregorian-valid UTC second. |
| `DurationMs` | JSON integer `0..3600000`. |
| `Repository` | exact `chemitaro/spec-dock`. |
| `Role` | exact order `producer,linux-canonical,sdist-smoke,macos-delta`. |
| `Passed` | exact string `passed`; failed jobs do not emit accepted role evidence/receipts. |

Time relations are inclusive: role `started_at <= completed_at`; pre payload `generated_at` follows the final run and context readback; post payload `merged_at <= issue_finish_started_at <= issue_finish_completed_at <= generated_at`; when `issue_finish_already_closed=false`, `issue_finish_started_at <= github_issue_closed_at <= issue_finish_completed_at`; when true, the unique selected close event is at or before `issue_finish_started_at`; Epic payload generation follows the observed Epic close event. Comment receipt requires `created_at=updated_at<=verified_at`.

### I392-D-016 — Digest-bearing fields and canonical inputs

| Field | Canonical input and relation |
|---|---|
| lifecycle `candidate_digest` | Wire artifact candidate stream over final version and the four roots/two slot payloads; record, seeds and generated markers excluded. |
| candidate/receipt/provider file `sha256` | SHA-256 of the complete referenced file bytes, including its one LF for JSON. |
| Actions artifact `digest` | SHA-256 of the downloaded Actions artifact archive bytes; must equal the exact digest in `artifacts.json`. |
| `environment_fingerprint_sha256` | SHA-256 of compact+LF JSON with exact ordered keys `environment_id,descriptor_sha256,base_image_digest,built_image_id,runner_image,architecture,cpu_quota_millis,memory_limit_bytes,python_version,uv_version,uv_lock_sha256,kernel_release,cgroup_version`. |
| `provider_evidence_sha256` | SHA-256 of complete `provider-evidence.json` bytes including LF. |
| attestation `payload_sha256` | SHA-256 of complete payload JSON bytes including LF. |
| comment `body_sha256` | SHA-256 of the exact four-line comment envelope bytes. |
| `tracked_report_blob_sha1` | Git blob OID of the report bytes in the frozen final head, obtained externally. |

The verifier recomputes every digest from actual bytes. A declared hash without the referenced bytes is invalid.

### I392-D-017 — Candidate manifest schema

Exact ordered keys and constraints:

| Key | Type | Exact relation |
|---|---|---|
| `schema_version` | integer | `1` |
| `kind` | string | `provider-candidate-manifest` |
| `repository` | string | `Repository` |
| `source_sha`,`source_tree` | string | `GitOid`; checked-out workflow head/tree |
| `workflow_run_id` | integer | `PositiveId`; current run |
| `workflow_run_attempt` | integer | `RunAttempt`; current run attempt |
| `build_job_id` | integer | `PositiveId`; API job named `provider-build-artifacts` |
| `build_job_name` | string | `provider-build-artifacts` |
| `build_invocation_count` | integer | exact `1` |
| `candidate_digest` | string | lifecycle candidate digest |
| `wheel` | object | keys `filename,size_bytes,sha256`; filename exact `spec_dock-0.2.4-py3-none-any.whl` |
| `sdist` | object | same keys; filename exact `spec_dock-0.2.4.tar.gz` |
| `files_order` | array | exact `["wheel","sdist"]` |

The candidate artifact contains exactly `candidate-manifest.json`, the named wheel and the named sdist. Producer invokes exactly one command identified as `uv-build-sdist-wheel-v1`; no other job invokes packaging.

### I392-D-018 — Role evidence schemas

All role evidence has exact ordered keys `schema_version,kind,role,repository,source_sha,source_tree,workflow_run_id,workflow_run_attempt,job_id,job_name,status,started_at,completed_at,build_invocation_count,candidate_manifest_sha256,wheel_sha256,sdist_sha256,details`.

Common relations: schema `1`, kind `provider-role-evidence`, source/run/candidate hashes equal manifest and API, status `passed`, and role/job/build-count mapping below.

| Role | Job name | Build count | Exact `details` keys and relations |
|---|---|---:|---|
| producer | `provider-build-artifacts` | 1 | `packaging_command_id=uv-build-sdist-wheel-v1`; `packaging_argv` exact six strings `uv,build,--sdist,--wheel,--out-dir,<absolute owner-bound output>`; exit `0`; output count `2`; candidate digest equals manifest. |
| linux-canonical | `provider-linux-canonical` | 0 | `environment_id,environment_descriptor_sha256,environment_fingerprint_input,environment_fingerprint_sha256,pytest_process_count,worker_count,node_inventory_sha256,qualification_runs,budget_run_count,seeded_fault_total,seeded_fault_detected`; exact environment ID, process/worker `1`, runs length `20`, budget count `5`, positive fault total equal detected. Each run keys `index,wall_milliseconds,cpu_milliseconds,exit_code,retry_count,flake_count`; indices `1..20`, exit/retry/flake `0`, wall positive, and for indices 1..5 `cpu_ms*1000 <= wall_ms*1100` and wall <=600000. All runs share the one fingerprint. |
| sdist-smoke | `provider-sdist-smoke` | 0 | `python_version,install_exit_code,metadata_smoke_exit_code,package_data_smoke_exit_code,installed_version`; exits `0`, installed version `0.2.4`. |
| macos-delta | `provider-macos-delta` | 0 | `runner_image,architecture,python_version,native_symbol,native_positive_control_events,nofollow_verified,executable_mode_verified,lifecycle_delta_exit_code`; architecture `x86_64|arm64`, symbol `renameatx_np`, control events `1`, booleans true, exit `0`. |

Environment fingerprint input uses the exact I392-D-016 key set; `cpu_quota_millis=2000`, `memory_limit_bytes=8589934592`, architecture `x86_64`, cgroup version `2`, nonempty pinned version strings and `sha256:` image identities.

### I392-D-019 — Receipt and provider aggregate schemas

Receipt exact keys: `schema_version,kind,role,repository,source_sha,source_tree,workflow_run_id,workflow_run_attempt,job_id,job_name,needs,status,build_invocation_count,candidate_artifact,candidate_manifest,wheel,sdist,evidence,started_at,completed_at`.

- Kind is `provider-job-receipt`.
- `needs=[]` for producer and exact `["provider-build-artifacts"]` for each consumer.
- `candidate_artifact` keys `id,name,digest`; name `provider-candidate-<source_sha>`.
- File references use exact keys `filename,size_bytes,sha256` and hash actual bytes.
- Role evidence filename mapping is exact: producer/build, linux/linux, sdist/sdist, macOS/macOS.
- Receipt artifacts are named `provider-receipt-<role>-<source_sha>` and each contains exactly its receipt JSON and role evidence JSON.

`provider-evidence.json` exact keys are `schema_version,kind,repository,source_sha,source_tree,workflow_run_id,workflow_run_attempt,status,candidate_artifact,receipt_artifacts,roles,file_manifest,aggregate`.

- Kind `provider-evidence`; status `passed`.
- `receipt_artifacts` and `roles` are exact role order.
- `file_manifest` has exactly eight rows in receipt/evidence pairs by role order; each row keys `filename,size_bytes,sha256` and hashes actual child bytes.
- Aggregate keys are `producer_build_invocation_count,consumer_build_invocation_count,role_count,file_count,environment_id,environment_fingerprint_sha256,qualification_run_count,budget_run_count,seeded_fault_total,seeded_fault_detected,status`, with exact values `1,0,4,9,specdock-linux-qualification-v1,<linux fingerprint>,20,5,<positive N>,<same N>,passed`.
- The uploaded `provider-evidence-<source_sha>` directory contains exactly `provider-evidence.json` plus the eight files in `file_manifest`; no archive-only assertion is sufficient.

### I392-D-020 — Exact Provider Gate CLI

Accepted subcommands are exactly:

```text
build-candidate
run-linux-canonical
run-sdist-smoke
run-macos-delta
assemble-provider-evidence
verify-downloaded-artifact
verify-node-ownership
verify-workflow-structure
emit-attestation
```

All workflow invocations pass `--json`. A successful command writes one compact+LF JSON object to stdout and nothing to stderr. A post-parse failure writes one compact+LF JSON object with exact ordered keys `schema_version,status,code,command,message,exit_code` to stdout and nothing to stderr. `status="error"`, `exit_code` equals the process exit and `command` is the accepted subcommand. Parser failure before a subcommand is known writes no stdout and exact stderr `provider-gate: error (provider-gate-arguments-invalid): The provider-gate command arguments are invalid.
`, exit 2.

#### Exact failure number/code/message/command matrix

| Exit | Code | Exact message | Exact allowed command set |
|---:|---|---|---|
| 2 | `provider-gate-arguments-invalid` | `The provider-gate command arguments are invalid.` | all nine commands |
| 3 | `provider-gate-input-missing` | `A required provider-gate input file is missing.` | `run-linux-canonical,run-sdist-smoke,run-macos-delta,assemble-provider-evidence,verify-downloaded-artifact,verify-node-ownership,verify-workflow-structure,emit-attestation` |
| 4 | `provider-gate-json-invalid` | `A provider-gate input is not valid canonical JSON.` | `run-linux-canonical,run-sdist-smoke,run-macos-delta,assemble-provider-evidence,verify-downloaded-artifact,verify-node-ownership,verify-workflow-structure,emit-attestation` |
| 5 | `provider-gate-schema-invalid` | `A provider-gate input does not match the exact schema.` | `run-linux-canonical,run-sdist-smoke,run-macos-delta,assemble-provider-evidence,verify-downloaded-artifact,verify-node-ownership,verify-workflow-structure,emit-attestation` |
| 6 | `provider-gate-identity-mismatch` | `Repository, source, tree, run, job, or artifact identity does not match.` | `run-linux-canonical,run-sdist-smoke,run-macos-delta,assemble-provider-evidence,verify-downloaded-artifact,emit-attestation` |
| 7 | `provider-gate-relation-mismatch` | `A provider-gate parent-child, timestamp, needs, or context relation does not match.` | `run-linux-canonical,run-sdist-smoke,run-macos-delta,assemble-provider-evidence,verify-downloaded-artifact,emit-attestation` |
| 8 | `provider-gate-byte-mismatch` | `A downloaded file size or SHA-256 does not match its declared bytes.` | `run-linux-canonical,run-sdist-smoke,run-macos-delta,assemble-provider-evidence,verify-downloaded-artifact,emit-attestation` |
| 9 | `provider-gate-inventory-mismatch` | `A required file, role, receipt, job, node, or artifact is missing, duplicated, or unexpected.` | `build-candidate,run-linux-canonical,run-sdist-smoke,run-macos-delta,assemble-provider-evidence,verify-downloaded-artifact,verify-node-ownership,verify-workflow-structure` |
| 10 | `provider-gate-build-count-mismatch` | `The packaging count is not exactly one producer invocation and zero consumer invocations.` | `build-candidate,run-linux-canonical,run-sdist-smoke,run-macos-delta,assemble-provider-evidence,verify-downloaded-artifact` |
| 11 | `provider-gate-qualification-mismatch` | `The stable Linux qualification environment or acceptance metrics do not match.` | `run-linux-canonical,assemble-provider-evidence,verify-downloaded-artifact` |
| 12 | `provider-gate-workflow-structure-mismatch` | `The Provider CI jobs, needs, permissions, artifact names, or packaging ownership do not match.` | `verify-workflow-structure` |
| 13 | `provider-gate-output-write-failed` | `Provider-gate output could not be created, fsynced, reread, and verified safely.` | `build-candidate,run-linux-canonical,run-sdist-smoke,run-macos-delta,assemble-provider-evidence,emit-attestation` |
| 14 | `provider-gate-comment-contract-mismatch` | `The attestation payload or append-only comment contract does not match.` | `emit-attestation` |

No command may remap a failure to another code. Unexpected Python exceptions are test/job defects and are not serialized as a generic Provider Gate result.

#### Exact success stdout schemas

All schemas reject extra/missing keys. Every file descriptor object has exact ordered keys `filename,size_bytes,sha256` and uses the scalar relations in D-015.

| Command | Code | Exact ordered stdout keys and fixed relations |
|---|---|---|
| `build-candidate` | `candidate-built` | `schema_version,status,code,command,repository,source_sha,source_tree,artifact_name,build_invocation_count,files`; status `completed`, artifact `provider-candidate-<source_sha>`, count `1`, files exact candidate manifest/wheel/sdist order. |
| `run-linux-canonical` | `linux-canonical-passed` | `schema_version,status,code,command,repository,source_sha,source_tree,workflow_run_id,receipt,evidence,build_invocation_count`; count `0`, descriptors point to exact linux receipt/evidence. |
| `run-sdist-smoke` | `sdist-smoke-passed` | same ordered keys as role success; exact sdist receipt/evidence, count `0`. |
| `run-macos-delta` | `macos-delta-passed` | same ordered keys as role success; exact macOS receipt/evidence, count `0`. |
| `assemble-provider-evidence` | `provider-evidence-assembled` | `schema_version,status,code,command,repository,source_sha,source_tree,workflow_run_id,artifact_name,file_count,files`; artifact `provider-evidence-<source_sha>`, count `9`, files exact D-014 order with actual byte descriptors. |
| `verify-downloaded-artifact` | `downloaded-artifact-verified` | exact D-021 ordered success object. |
| `verify-node-ownership` | `node-ownership-verified` | `schema_version,status,code,command,ownership_map_sha256,collected_node_count,owned_contract_count`; counts `0..1000000`, all collected contract nodes exactly owned once. |
| `verify-workflow-structure` | `workflow-structure-verified` | `schema_version,status,code,command,workflow_sha256,head_kind,job_count,jobs`; head kind `compatibility|final`, job count equals jobs length, jobs in exact workflow declaration order. |
| `emit-attestation` | `attestation-emitted` | exact D-023 ordered success object. |

The role-success schema is identical for the three role commands except code/command and exact receipt/evidence filenames. `build-candidate`, role runners, assembly and emitter register output files with the live workspace owner before creation and seal them before returning success.

### I392-D-021 — `verify-downloaded-artifact`

Exact interface used by provider-attestation, compatibility provider-tests and S80:

```bash
uv run python scripts/provider_gate.py verify-downloaded-artifact \
  --repository chemitaro/spec-dock \
  --candidate-dir "$ISS392_WS_ARTIFACT_DOWNLOAD/candidate" \
  --evidence-dir "$ISS392_WS_ARTIFACT_DOWNLOAD/evidence" \
  --run-json "$ISS392_WS_WORKFLOW_API/run.json" \
  --jobs-json "$ISS392_WS_WORKFLOW_API/jobs.json" \
  --artifacts-json "$ISS392_WS_WORKFLOW_API/artifacts.json" \
  --source-sha "$SOURCE_SHA" \
  --source-tree "$SOURCE_TREE" \
  --workflow-run-id "$RUN_ID" \
  --json
```

It reads and hashes every actual candidate/evidence/API byte file, requires exact artifact and nine-file inventories, exact job names/needs/status/source/tree/run attempt, one producer build/zero consumers, all schema/timestamp/digest relations and stable qualification. Success stdout exact ordered keys are `schema_version,status,code,command,repository,workflow_run_id,source_sha,source_tree,candidate_artifact_name,evidence_artifact_name,receipt_roles,evidence_files`; receipt roles and evidence files use normative order. Any failure maps only through I392-D-020.

### I392-D-022 — Attestation payloads and measured closure

Pre-merge payload exact ordered keys are unchanged and exact: `schema_version,kind,repository,issue_number,pull_request_number,spec_freeze_commit,implementation_base_sha,compatibility_head_sha,compatibility_head_tree,compatibility_workflow_run_id,final_head_sha,final_head_tree,final_workflow_run_id,compatibility_to_final_paths,tracked_report_blob_sha1,candidate_artifact,evidence_artifact,provider_evidence_sha256,environment_fingerprint_sha256,required_contexts_before,required_contexts_both,canary_pull_request_number,canary_block_verified,required_contexts_after_old_removed,required_contexts_final_head,human_review_state,generated_at`.

Post-merge payload exact ordered keys are `schema_version,kind,repository,issue_number,pre_merge_comment_id,pre_merge_payload_sha256,final_head_sha,final_head_tree,merge_commit_sha,merge_commit_tree,tree_equal,merge_actor,merged_at,issue_finish_command,issue_finish_started_at,issue_finish_status,issue_finish_already_closed,github_issue_closed_event_id,github_issue_closed_at,issue_finish_active_cleared,issue_finish_post_sync_status,issue_finish_completed_at,generated_at`.

- `issue_finish_command` is exact `python3 ./spec-dock/scripts/spec-dock issue finish`.
- Current `issue_finish()` invokes `close_node()` before active clear/post-sync. There is no later `close --id iss-00392` command.
- The wrapper captures start/end; the returned `github_issue_number,already_closed,active_cleared,post_sync` values are matched to the immediate GitHub issue/timeline readback.
- If `already_closed=false`, the unique close event occurs within the command interval and is the #392 close evidence. If true, the selected preexisting close event is at or before command start and exact issue state readback is closed.
- Status is `finished`, active cleared true, post-sync `completed`; a failed/partial command produces no accepted post payload.

Epic payload exact keys are `schema_version,kind,repository,epic_issue_number,implementation_issue_number,post_merge_comment_id,post_merge_payload_sha256,implementation_issue_closed_event_id,implementation_issue_closed_at,epic_acceptance_status,github_epic_closed_event_id,github_epic_closed_at,generated_at`. It is created only after post comment receipt, Epic acceptance and measured #384 close event.

Comment receipt exact keys are `schema_version,kind,attestation_kind,repository,target_issue_number,comment_id,comment_url,author_login,created_at,updated_at,payload_sha256,body_sha256,body_size_bytes,verified_at`. Pre/post comments target #392; Epic targets #384. Payloads omit their own future comment identity.

### I392-D-023 — `emit-attestation` and append-only object

Exact interface:

```bash
uv run python scripts/provider_gate.py emit-attestation \
  --kind "$KIND" \
  --input-json "$ISS392_WS_ATTESTATION_DRAFT/input.json" \
  --output-json "$ISS392_WS_ATTESTATION_DRAFT/payload.json" \
  --output-comment "$ISS392_WS_ATTESTATION_DRAFT/comment.md" \
  --json
```

Accepted kinds are the three payload kinds. Inputs must already contain all measured facts and exact schema. Output files are O_EXCL/no-follow mode0600, fsynced and reread. Comment bytes are exactly marker line `<!-- spec-dock-attestation:<kind>:<payload-sha256> -->`, opening `json` fence, payload bytes without final LF, closing fence, one final LF. Success stdout exact keys are `schema_version,status,code,command,kind,payload_path,payload_size_bytes,payload_sha256,comment_path,comment_size_bytes,comment_sha256`, status completed/code attestation-emitted. Failure uses I392-D-020; stdout never contains payload/comment bytes.

Human posts the exact comment bytes as a new GitHub Issue comment. `issues:write` is required only for POST; `issues:read` for readback. The external receipt verifies exact target/ID/URL/actor/body/marker/hash, visibility and created=updated. Editing/deletion invalidates evidence.

### I392-D-024 — External workspace owner process and child registration

`create_external_workspace()` returns an in-process `ExternalWorkspaceHandle`; cleanup authority is never serialized. For child-producing operations, the owner process implements exact states `open -> child-running -> sealed -> upload-pending -> upload-confirmed -> cleaned`, or `preserved-on-failure`.

- Before launch, owner calls `reserve_tree(handle,name)` for one top-level ASCII name matching `[a-z0-9][a-z0-9-]{0,63}`; owner creates the directory descriptor-safely and records its device/inode in memory.
- The child receives only that reserved tree path plus inherited directory FD where supported. It may create descendants under that tree only. It cannot register another top-level name or invoke cleanup.
- After child exit, owner calls `seal_tree(handle,name,child_exit_code)`, walks only the reserved descriptor no-follow, rejects symlinks/special files/wrong owner/group-or-other-write, and freezes the complete relative inventory in memory. Any unreserved top-level entry or identity change yields `provider-gate-workspace-contract-failed` and preserves the workspace.
- Local orchestrators retain the handle until every consumer has read/sealed outputs, then cleanup.
- Exact Python API is `reserve_tree(handle,name) -> ReservedTree`, `spawn_registered_child(handle,reserved_tree,argv,env) -> ChildResult`, `seal_tree(handle,reserved_tree,child_result) -> SealedTree`, `begin_upload(handle,sealed_tree)`, `confirm_upload(handle,sealed_tree,artifact_id,artifact_name,artifact_digest)`, and `cleanup_external_workspace(handle)`. None accepts an arbitrary workspace root.
- GitHub Actions starts one background workspace-owner process for the job. A mode0600 Unix control socket under `$RUNNER_TEMP` accepts canonical one-line JSON messages with exact keys `schema_version,action,name,child_pid,child_exit_code,artifact_id,artifact_name,artifact_digest,nonce`; nonapplicable values are null. Action enum is `reserve-tree|child-started|seal-tree|upload-started|upload-confirmed|cleanup|preserve`. The owner replies with keys `schema_version,status,action,workspace_state,message`; status `ok|error`, workspace state the exact owner state enum. The nonce authenticates a message but cannot recreate FDs or cleanup another path.
- The owner creates each reserved directory itself, keeps its descriptor and PID alive while the child and `actions/upload-artifact` run, and never accepts a child-created top-level path. `child_pid` must be the launched process, `child_exit_code` is required only for seal, and artifact fields are required only for upload-confirmed.
- On upload success, the job sends exact artifact ID/name/digest, owner transitions upload-confirmed, revalidates the sealed inventory, then handle-cleans. On upload failure/cancellation, it sends `preserve`; owner closes FDs without deletion and reports preserved-on-failure. Job success requires owner exit 0 after confirmed cleanup.

Tests cover unregistered child creation, child escape/symlink/special/writable entry, forged path/nonce, owner death, upload-before-seal, cleanup-before-upload-confirm, upload failure preservation and successful after-upload cleanup.

### I392-D-025 — Compatibility/final heads and stable environment

Qualification uses `specdock-linux-qualification-v1` and exact fingerprint for all runs. Tracked report has neither compatibility nor final identity. S70 creates and commits both distinct heads: compatibility head emits both contexts, human performs the no-gap transition, then the final descendant removes only `provider-tests`. S80 owns no tracked path and only dispatches/reruns/downloads/verifies/reads back/comments on the already-existing final head.

## 9. Canonical evidence and attestation fixtures

### I392-D-026 — `EVIDENCE-FIXTURE-V2`

This fixture is a normative serializer oracle, not a runtime-identity allowlist. Every JSON block below is exact compact UTF-8 plus LF. Runtime validators accept any values satisfying I392-D-015–025; tests must not compare runtime IDs/timestamps/paths to fixture literals.

Fixture identities are synthetic and distinct: compatibility `a/b`, final `c/d`, merge `e`, report blob `f`, spec freeze `8`, implementation base `9`. The environment fingerprint is mechanically derived from its displayed input.

| Fixture | Size bytes | SHA-256 |
|---|---:|---|
| `environment-fingerprint-input.json` | 624 | `cbf2ec163715a448bbb572db757b604a75ebeaec635129e36255614e9a6c228c` |
| `candidate-manifest.json` | 757 | `b9b35fceeeb498afd125a7afdf46cf22bbb1da6890749f262cc71f60d6c6b42e` |
| `producer-build-evidence.json` | 1005 | `254251772cc68d30784302c7606f28a8626c6690b2bf07e6fbeaf00c4d7c9b60` |
| `linux-canonical-evidence.json` | 4081 | `37846aa3069d3466b955219221064922f09574fc5c4f70e5fae618bd2e5c7045` |
| `sdist-smoke-evidence.json` | 847 | `1dad7052e5375b9033b12f3702a504aa160143e0411609bc9a4c796c8be9e1e2` |
| `macos-delta-evidence.json` | 937 | `b8447c94e0b1a3f8bd347bb024d1e0d6c8654bfb20932c0a368567f98820e87f` |
| `provider-receipt-producer.json` | 1228 | `5244312c62ffdc8cdb06d364fe2706cf047b5fb3f25ebf41e1b7ccfc764f3029` |
| `provider-receipt-linux-canonical.json` | 1262 | `5aced8b3e9b5955cda49332eb779e32cc4487ba5ee42106ce982726b8b3585e7` |
| `provider-receipt-sdist-smoke.json` | 1249 | `eca36bcfbaa60ba171bf3a488efc42c1bdfa82511c0315d1a3ffee0a1bdd752d` |
| `provider-receipt-macos-delta.json` | 1249 | `cd1da241faff23a475fad5fc72463f62456dc2ac10ae21a6819c4640f48dad2e` |
| `provider-evidence.json` | 4421 | `6b20606e234cbc0a43c6a89e98efdbc7fd59afe341293d4f6039bcfb166dbdfa` |
| `pre-merge-attestation-v1.json` | 1706 | `81a8cb8ffac801b7aacb8909380b644be1e58e77a474127205d2785ebd8a1ea4` |
| `post-merge-closure-v1.json` | 999 | `b1df7fd0b8be353d735163736de8416fa4cec5d98abd83ef7a9922c579eb3946` |
| `epic-closure-v1.json` | 519 | `f2d3870430a2095fee9dcc2c77ee2a273299dfa34d85841ca01247f61fd236ca` |
| `comment-receipt-pre-merge.json` | 584 | `aa100132e8a3d738c1a0959845a00d42cfd16a643ca19a936af1a063b969a1ae` |
| `comment-receipt-post-merge.json` | 581 | `9cd7292361ef6a5e4257b05c6c51cd48acc3ab047444a1863c1218784a113d04` |
| `comment-receipt-epic.json` | 574 | `0e5b95eb1148357302ee2de4b96b50201fae63ed5e89227cc84e50eada80b719` |
| `verify-downloaded-artifact.stdout.json` | 822 | `d71daa812b3bd06027b4a2f24e980206364da6a83c1dbc1fc4546a3078a3879f` |
| `emit-attestation.stdout.json` | 496 | `5f887f487e211fae92dd77ac3a5135b0fa9a6b112c9f7d6e75be35eecb2404e6` |
| `pre-merge-comment.md` | 1839 | `2138870e141753c991cfa33965f85dd99c0797064b8cbba65ad99688e514c06e` |
| `post-merge-comment.md` | 1129 | `511b735d2c443f38a955b603590de7ecb8c54033639f561a7a0995f23574509c` |
| `epic-closure-comment.md` | 643 | `a27d0c7ee31f505f6995b71a30502eff3e50259a765f59cbf4b94897d1db4cf8` |

#### `environment-fingerprint-input.json`

```json
{"environment_id":"specdock-linux-qualification-v1","descriptor_sha256":"4444444444444444444444444444444444444444444444444444444444444444","base_image_digest":"sha256:6666666666666666666666666666666666666666666666666666666666666666","built_image_id":"sha256:7777777777777777777777777777777777777777777777777777777777777777","runner_image":"ubuntu-24.04","architecture":"x86_64","cpu_quota_millis":2000,"memory_limit_bytes":8589934592,"python_version":"3.11.10","uv_version":"0.8.14","uv_lock_sha256":"8888888888888888888888888888888888888888888888888888888888888888","kernel_release":"6.11.0-1018-azure","cgroup_version":2}
```

#### `candidate-manifest.json`

```json
{"schema_version":1,"kind":"provider-candidate-manifest","repository":"chemitaro/spec-dock","source_sha":"cccccccccccccccccccccccccccccccccccccccc","source_tree":"dddddddddddddddddddddddddddddddddddddddd","workflow_run_id":1101,"workflow_run_attempt":1,"build_job_id":2101,"build_job_name":"provider-build-artifacts","build_invocation_count":1,"candidate_digest":"1111111111111111111111111111111111111111111111111111111111111111","wheel":{"filename":"spec_dock-0.2.4-py3-none-any.whl","size_bytes":123456,"sha256":"2222222222222222222222222222222222222222222222222222222222222222"},"sdist":{"filename":"spec_dock-0.2.4.tar.gz","size_bytes":234567,"sha256":"3333333333333333333333333333333333333333333333333333333333333333"},"files_order":["wheel","sdist"]}
```

#### `producer-build-evidence.json`

```json
{"schema_version":1,"kind":"provider-role-evidence","role":"producer","repository":"chemitaro/spec-dock","source_sha":"cccccccccccccccccccccccccccccccccccccccc","source_tree":"dddddddddddddddddddddddddddddddddddddddd","workflow_run_id":1101,"workflow_run_attempt":1,"job_id":2101,"job_name":"provider-build-artifacts","status":"passed","started_at":"2026-09-02T00:00:00Z","completed_at":"2026-09-02T00:10:00Z","build_invocation_count":1,"candidate_manifest_sha256":"b9b35fceeeb498afd125a7afdf46cf22bbb1da6890749f262cc71f60d6c6b42e","wheel_sha256":"2222222222222222222222222222222222222222222222222222222222222222","sdist_sha256":"3333333333333333333333333333333333333333333333333333333333333333","details":{"packaging_command_id":"uv-build-sdist-wheel-v1","packaging_argv":["uv","build","--sdist","--wheel","--out-dir","/runner/_temp/spec-dock-iss-00392-fixture/output"],"packaging_exit_code":0,"output_file_count":2,"candidate_digest":"1111111111111111111111111111111111111111111111111111111111111111"}}
```

#### `linux-canonical-evidence.json`

```json
{"schema_version":1,"kind":"provider-role-evidence","role":"linux-canonical","repository":"chemitaro/spec-dock","source_sha":"cccccccccccccccccccccccccccccccccccccccc","source_tree":"dddddddddddddddddddddddddddddddddddddddd","workflow_run_id":1101,"workflow_run_attempt":1,"job_id":2102,"job_name":"provider-linux-canonical","status":"passed","started_at":"2026-09-02T00:00:00Z","completed_at":"2026-09-02T00:10:00Z","build_invocation_count":0,"candidate_manifest_sha256":"b9b35fceeeb498afd125a7afdf46cf22bbb1da6890749f262cc71f60d6c6b42e","wheel_sha256":"2222222222222222222222222222222222222222222222222222222222222222","sdist_sha256":"3333333333333333333333333333333333333333333333333333333333333333","details":{"environment_id":"specdock-linux-qualification-v1","environment_descriptor_sha256":"4444444444444444444444444444444444444444444444444444444444444444","environment_fingerprint_input":{"environment_id":"specdock-linux-qualification-v1","descriptor_sha256":"4444444444444444444444444444444444444444444444444444444444444444","base_image_digest":"sha256:6666666666666666666666666666666666666666666666666666666666666666","built_image_id":"sha256:7777777777777777777777777777777777777777777777777777777777777777","runner_image":"ubuntu-24.04","architecture":"x86_64","cpu_quota_millis":2000,"memory_limit_bytes":8589934592,"python_version":"3.11.10","uv_version":"0.8.14","uv_lock_sha256":"8888888888888888888888888888888888888888888888888888888888888888","kernel_release":"6.11.0-1018-azure","cgroup_version":2},"environment_fingerprint_sha256":"cbf2ec163715a448bbb572db757b604a75ebeaec635129e36255614e9a6c228c","pytest_process_count":1,"worker_count":1,"node_inventory_sha256":"9999999999999999999999999999999999999999999999999999999999999999","qualification_runs":[{"index":1,"wall_milliseconds":301000,"cpu_milliseconds":250800,"exit_code":0,"retry_count":0,"flake_count":0},{"index":2,"wall_milliseconds":302000,"cpu_milliseconds":251600,"exit_code":0,"retry_count":0,"flake_count":0},{"index":3,"wall_milliseconds":303000,"cpu_milliseconds":252400,"exit_code":0,"retry_count":0,"flake_count":0},{"index":4,"wall_milliseconds":304000,"cpu_milliseconds":253200,"exit_code":0,"retry_count":0,"flake_count":0},{"index":5,"wall_milliseconds":305000,"cpu_milliseconds":254000,"exit_code":0,"retry_count":0,"flake_count":0},{"index":6,"wall_milliseconds":306000,"cpu_milliseconds":254800,"exit_code":0,"retry_count":0,"flake_count":0},{"index":7,"wall_milliseconds":307000,"cpu_milliseconds":255600,"exit_code":0,"retry_count":0,"flake_count":0},{"index":8,"wall_milliseconds":308000,"cpu_milliseconds":256400,"exit_code":0,"retry_count":0,"flake_count":0},{"index":9,"wall_milliseconds":309000,"cpu_milliseconds":257200,"exit_code":0,"retry_count":0,"flake_count":0},{"index":10,"wall_milliseconds":310000,"cpu_milliseconds":258000,"exit_code":0,"retry_count":0,"flake_count":0},{"index":11,"wall_milliseconds":311000,"cpu_milliseconds":258800,"exit_code":0,"retry_count":0,"flake_count":0},{"index":12,"wall_milliseconds":312000,"cpu_milliseconds":259600,"exit_code":0,"retry_count":0,"flake_count":0},{"index":13,"wall_milliseconds":313000,"cpu_milliseconds":260400,"exit_code":0,"retry_count":0,"flake_count":0},{"index":14,"wall_milliseconds":314000,"cpu_milliseconds":261200,"exit_code":0,"retry_count":0,"flake_count":0},{"index":15,"wall_milliseconds":315000,"cpu_milliseconds":262000,"exit_code":0,"retry_count":0,"flake_count":0},{"index":16,"wall_milliseconds":316000,"cpu_milliseconds":262800,"exit_code":0,"retry_count":0,"flake_count":0},{"index":17,"wall_milliseconds":317000,"cpu_milliseconds":263600,"exit_code":0,"retry_count":0,"flake_count":0},{"index":18,"wall_milliseconds":318000,"cpu_milliseconds":264400,"exit_code":0,"retry_count":0,"flake_count":0},{"index":19,"wall_milliseconds":319000,"cpu_milliseconds":265200,"exit_code":0,"retry_count":0,"flake_count":0},{"index":20,"wall_milliseconds":320000,"cpu_milliseconds":266000,"exit_code":0,"retry_count":0,"flake_count":0}],"budget_run_count":5,"seeded_fault_total":27,"seeded_fault_detected":27}}
```

#### `sdist-smoke-evidence.json`

```json
{"schema_version":1,"kind":"provider-role-evidence","role":"sdist-smoke","repository":"chemitaro/spec-dock","source_sha":"cccccccccccccccccccccccccccccccccccccccc","source_tree":"dddddddddddddddddddddddddddddddddddddddd","workflow_run_id":1101,"workflow_run_attempt":1,"job_id":2103,"job_name":"provider-sdist-smoke","status":"passed","started_at":"2026-09-02T00:00:00Z","completed_at":"2026-09-02T00:10:00Z","build_invocation_count":0,"candidate_manifest_sha256":"b9b35fceeeb498afd125a7afdf46cf22bbb1da6890749f262cc71f60d6c6b42e","wheel_sha256":"2222222222222222222222222222222222222222222222222222222222222222","sdist_sha256":"3333333333333333333333333333333333333333333333333333333333333333","details":{"python_version":"3.11.10","install_exit_code":0,"metadata_smoke_exit_code":0,"package_data_smoke_exit_code":0,"installed_version":"0.2.4"}}
```

#### `macos-delta-evidence.json`

```json
{"schema_version":1,"kind":"provider-role-evidence","role":"macos-delta","repository":"chemitaro/spec-dock","source_sha":"cccccccccccccccccccccccccccccccccccccccc","source_tree":"dddddddddddddddddddddddddddddddddddddddd","workflow_run_id":1101,"workflow_run_attempt":1,"job_id":2104,"job_name":"provider-macos-delta","status":"passed","started_at":"2026-09-02T00:00:00Z","completed_at":"2026-09-02T00:10:00Z","build_invocation_count":0,"candidate_manifest_sha256":"b9b35fceeeb498afd125a7afdf46cf22bbb1da6890749f262cc71f60d6c6b42e","wheel_sha256":"2222222222222222222222222222222222222222222222222222222222222222","sdist_sha256":"3333333333333333333333333333333333333333333333333333333333333333","details":{"runner_image":"macos-15","architecture":"arm64","python_version":"3.11.10","native_symbol":"renameatx_np","native_positive_control_events":1,"nofollow_verified":true,"executable_mode_verified":true,"lifecycle_delta_exit_code":0}}
```

#### `provider-receipt-producer.json`

```json
{"schema_version":1,"kind":"provider-job-receipt","role":"producer","repository":"chemitaro/spec-dock","source_sha":"cccccccccccccccccccccccccccccccccccccccc","source_tree":"dddddddddddddddddddddddddddddddddddddddd","workflow_run_id":1101,"workflow_run_attempt":1,"job_id":2101,"job_name":"provider-build-artifacts","needs":[],"status":"passed","build_invocation_count":1,"candidate_artifact":{"id":3100,"name":"provider-candidate-cccccccccccccccccccccccccccccccccccccccc","digest":"sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"},"candidate_manifest":{"filename":"candidate-manifest.json","size_bytes":757,"sha256":"b9b35fceeeb498afd125a7afdf46cf22bbb1da6890749f262cc71f60d6c6b42e"},"wheel":{"filename":"spec_dock-0.2.4-py3-none-any.whl","size_bytes":123456,"sha256":"2222222222222222222222222222222222222222222222222222222222222222"},"sdist":{"filename":"spec_dock-0.2.4.tar.gz","size_bytes":234567,"sha256":"3333333333333333333333333333333333333333333333333333333333333333"},"evidence":{"filename":"producer-build-evidence.json","size_bytes":1005,"sha256":"254251772cc68d30784302c7606f28a8626c6690b2bf07e6fbeaf00c4d7c9b60"},"started_at":"2026-09-02T00:00:00Z","completed_at":"2026-09-02T00:10:00Z"}
```

#### `provider-receipt-linux-canonical.json`

```json
{"schema_version":1,"kind":"provider-job-receipt","role":"linux-canonical","repository":"chemitaro/spec-dock","source_sha":"cccccccccccccccccccccccccccccccccccccccc","source_tree":"dddddddddddddddddddddddddddddddddddddddd","workflow_run_id":1101,"workflow_run_attempt":1,"job_id":2102,"job_name":"provider-linux-canonical","needs":["provider-build-artifacts"],"status":"passed","build_invocation_count":0,"candidate_artifact":{"id":3100,"name":"provider-candidate-cccccccccccccccccccccccccccccccccccccccc","digest":"sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"},"candidate_manifest":{"filename":"candidate-manifest.json","size_bytes":757,"sha256":"b9b35fceeeb498afd125a7afdf46cf22bbb1da6890749f262cc71f60d6c6b42e"},"wheel":{"filename":"spec_dock-0.2.4-py3-none-any.whl","size_bytes":123456,"sha256":"2222222222222222222222222222222222222222222222222222222222222222"},"sdist":{"filename":"spec_dock-0.2.4.tar.gz","size_bytes":234567,"sha256":"3333333333333333333333333333333333333333333333333333333333333333"},"evidence":{"filename":"linux-canonical-evidence.json","size_bytes":4081,"sha256":"37846aa3069d3466b955219221064922f09574fc5c4f70e5fae618bd2e5c7045"},"started_at":"2026-09-02T00:00:00Z","completed_at":"2026-09-02T00:10:00Z"}
```

#### `provider-receipt-sdist-smoke.json`

```json
{"schema_version":1,"kind":"provider-job-receipt","role":"sdist-smoke","repository":"chemitaro/spec-dock","source_sha":"cccccccccccccccccccccccccccccccccccccccc","source_tree":"dddddddddddddddddddddddddddddddddddddddd","workflow_run_id":1101,"workflow_run_attempt":1,"job_id":2103,"job_name":"provider-sdist-smoke","needs":["provider-build-artifacts"],"status":"passed","build_invocation_count":0,"candidate_artifact":{"id":3100,"name":"provider-candidate-cccccccccccccccccccccccccccccccccccccccc","digest":"sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"},"candidate_manifest":{"filename":"candidate-manifest.json","size_bytes":757,"sha256":"b9b35fceeeb498afd125a7afdf46cf22bbb1da6890749f262cc71f60d6c6b42e"},"wheel":{"filename":"spec_dock-0.2.4-py3-none-any.whl","size_bytes":123456,"sha256":"2222222222222222222222222222222222222222222222222222222222222222"},"sdist":{"filename":"spec_dock-0.2.4.tar.gz","size_bytes":234567,"sha256":"3333333333333333333333333333333333333333333333333333333333333333"},"evidence":{"filename":"sdist-smoke-evidence.json","size_bytes":847,"sha256":"1dad7052e5375b9033b12f3702a504aa160143e0411609bc9a4c796c8be9e1e2"},"started_at":"2026-09-02T00:00:00Z","completed_at":"2026-09-02T00:10:00Z"}
```

#### `provider-receipt-macos-delta.json`

```json
{"schema_version":1,"kind":"provider-job-receipt","role":"macos-delta","repository":"chemitaro/spec-dock","source_sha":"cccccccccccccccccccccccccccccccccccccccc","source_tree":"dddddddddddddddddddddddddddddddddddddddd","workflow_run_id":1101,"workflow_run_attempt":1,"job_id":2104,"job_name":"provider-macos-delta","needs":["provider-build-artifacts"],"status":"passed","build_invocation_count":0,"candidate_artifact":{"id":3100,"name":"provider-candidate-cccccccccccccccccccccccccccccccccccccccc","digest":"sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"},"candidate_manifest":{"filename":"candidate-manifest.json","size_bytes":757,"sha256":"b9b35fceeeb498afd125a7afdf46cf22bbb1da6890749f262cc71f60d6c6b42e"},"wheel":{"filename":"spec_dock-0.2.4-py3-none-any.whl","size_bytes":123456,"sha256":"2222222222222222222222222222222222222222222222222222222222222222"},"sdist":{"filename":"spec_dock-0.2.4.tar.gz","size_bytes":234567,"sha256":"3333333333333333333333333333333333333333333333333333333333333333"},"evidence":{"filename":"macos-delta-evidence.json","size_bytes":937,"sha256":"b8447c94e0b1a3f8bd347bb024d1e0d6c8654bfb20932c0a368567f98820e87f"},"started_at":"2026-09-02T00:00:00Z","completed_at":"2026-09-02T00:10:00Z"}
```

#### `provider-evidence.json`

```json
{"schema_version":1,"kind":"provider-evidence","repository":"chemitaro/spec-dock","source_sha":"cccccccccccccccccccccccccccccccccccccccc","source_tree":"dddddddddddddddddddddddddddddddddddddddd","workflow_run_id":1101,"workflow_run_attempt":1,"status":"passed","candidate_artifact":{"id":3100,"name":"provider-candidate-cccccccccccccccccccccccccccccccccccccccc","digest":"sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","manifest_sha256":"b9b35fceeeb498afd125a7afdf46cf22bbb1da6890749f262cc71f60d6c6b42e","wheel_sha256":"2222222222222222222222222222222222222222222222222222222222222222","sdist_sha256":"3333333333333333333333333333333333333333333333333333333333333333"},"receipt_artifacts":[{"role":"producer","id":3101,"name":"provider-receipt-producer-cccccccccccccccccccccccccccccccccccccccc","digest":"sha256:cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"},{"role":"linux-canonical","id":3102,"name":"provider-receipt-linux-canonical-cccccccccccccccccccccccccccccccccccccccc","digest":"sha256:dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd"},{"role":"sdist-smoke","id":3103,"name":"provider-receipt-sdist-smoke-cccccccccccccccccccccccccccccccccccccccc","digest":"sha256:eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"},{"role":"macos-delta","id":3104,"name":"provider-receipt-macos-delta-cccccccccccccccccccccccccccccccccccccccc","digest":"sha256:ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff"}],"roles":[{"role":"producer","job_id":2101,"job_name":"provider-build-artifacts","receipt_filename":"provider-receipt-producer.json","receipt_sha256":"5244312c62ffdc8cdb06d364fe2706cf047b5fb3f25ebf41e1b7ccfc764f3029","evidence_filename":"producer-build-evidence.json","evidence_sha256":"254251772cc68d30784302c7606f28a8626c6690b2bf07e6fbeaf00c4d7c9b60"},{"role":"linux-canonical","job_id":2102,"job_name":"provider-linux-canonical","receipt_filename":"provider-receipt-linux-canonical.json","receipt_sha256":"5aced8b3e9b5955cda49332eb779e32cc4487ba5ee42106ce982726b8b3585e7","evidence_filename":"linux-canonical-evidence.json","evidence_sha256":"37846aa3069d3466b955219221064922f09574fc5c4f70e5fae618bd2e5c7045"},{"role":"sdist-smoke","job_id":2103,"job_name":"provider-sdist-smoke","receipt_filename":"provider-receipt-sdist-smoke.json","receipt_sha256":"eca36bcfbaa60ba171bf3a488efc42c1bdfa82511c0315d1a3ffee0a1bdd752d","evidence_filename":"sdist-smoke-evidence.json","evidence_sha256":"1dad7052e5375b9033b12f3702a504aa160143e0411609bc9a4c796c8be9e1e2"},{"role":"macos-delta","job_id":2104,"job_name":"provider-macos-delta","receipt_filename":"provider-receipt-macos-delta.json","receipt_sha256":"cd1da241faff23a475fad5fc72463f62456dc2ac10ae21a6819c4640f48dad2e","evidence_filename":"macos-delta-evidence.json","evidence_sha256":"b8447c94e0b1a3f8bd347bb024d1e0d6c8654bfb20932c0a368567f98820e87f"}],"file_manifest":[{"filename":"provider-receipt-producer.json","size_bytes":1228,"sha256":"5244312c62ffdc8cdb06d364fe2706cf047b5fb3f25ebf41e1b7ccfc764f3029"},{"filename":"producer-build-evidence.json","size_bytes":1005,"sha256":"254251772cc68d30784302c7606f28a8626c6690b2bf07e6fbeaf00c4d7c9b60"},{"filename":"provider-receipt-linux-canonical.json","size_bytes":1262,"sha256":"5aced8b3e9b5955cda49332eb779e32cc4487ba5ee42106ce982726b8b3585e7"},{"filename":"linux-canonical-evidence.json","size_bytes":4081,"sha256":"37846aa3069d3466b955219221064922f09574fc5c4f70e5fae618bd2e5c7045"},{"filename":"provider-receipt-sdist-smoke.json","size_bytes":1249,"sha256":"eca36bcfbaa60ba171bf3a488efc42c1bdfa82511c0315d1a3ffee0a1bdd752d"},{"filename":"sdist-smoke-evidence.json","size_bytes":847,"sha256":"1dad7052e5375b9033b12f3702a504aa160143e0411609bc9a4c796c8be9e1e2"},{"filename":"provider-receipt-macos-delta.json","size_bytes":1249,"sha256":"cd1da241faff23a475fad5fc72463f62456dc2ac10ae21a6819c4640f48dad2e"},{"filename":"macos-delta-evidence.json","size_bytes":937,"sha256":"b8447c94e0b1a3f8bd347bb024d1e0d6c8654bfb20932c0a368567f98820e87f"}],"aggregate":{"producer_build_invocation_count":1,"consumer_build_invocation_count":0,"role_count":4,"file_count":9,"environment_id":"specdock-linux-qualification-v1","environment_fingerprint_sha256":"cbf2ec163715a448bbb572db757b604a75ebeaec635129e36255614e9a6c228c","qualification_run_count":20,"budget_run_count":5,"seeded_fault_total":27,"seeded_fault_detected":27,"status":"passed"}}
```

#### `pre-merge-attestation-v1.json`

```json
{"schema_version":1,"kind":"pre-merge-attestation-v1","repository":"chemitaro/spec-dock","issue_number":392,"pull_request_number":500,"spec_freeze_commit":"8888888888888888888888888888888888888888","implementation_base_sha":"9999999999999999999999999999999999999999","compatibility_head_sha":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","compatibility_head_tree":"bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb","compatibility_workflow_run_id":1001,"final_head_sha":"cccccccccccccccccccccccccccccccccccccccc","final_head_tree":"dddddddddddddddddddddddddddddddddddddddd","final_workflow_run_id":1101,"compatibility_to_final_paths":[".github/workflows/provider-ci.yml"],"tracked_report_blob_sha1":"ffffffffffffffffffffffffffffffffffffffff","candidate_artifact":{"id":3100,"name":"provider-candidate-cccccccccccccccccccccccccccccccccccccccc","digest":"sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"},"evidence_artifact":{"id":3110,"name":"provider-evidence-cccccccccccccccccccccccccccccccccccccccc","digest":"sha256:0000000000000000000000000000000000000000000000000000000000000000"},"provider_evidence_sha256":"6b20606e234cbc0a43c6a89e98efdbc7fd59afe341293d4f6039bcfb166dbdfa","environment_fingerprint_sha256":"cbf2ec163715a448bbb572db757b604a75ebeaec635129e36255614e9a6c228c","required_contexts_before":["Provider CI / provider-tests"],"required_contexts_both":["Provider CI / provider-gate","Provider CI / provider-tests"],"canary_pull_request_number":501,"canary_block_verified":true,"required_contexts_after_old_removed":["Provider CI / provider-gate"],"required_contexts_final_head":["Provider CI / provider-gate"],"human_review_state":"approved","generated_at":"2026-09-02T01:00:00Z"}
```

#### `post-merge-closure-v1.json`

```json
{"schema_version":1,"kind":"post-merge-closure-v1","repository":"chemitaro/spec-dock","issue_number":392,"pre_merge_comment_id":6001,"pre_merge_payload_sha256":"81a8cb8ffac801b7aacb8909380b644be1e58e77a474127205d2785ebd8a1ea4","final_head_sha":"cccccccccccccccccccccccccccccccccccccccc","final_head_tree":"dddddddddddddddddddddddddddddddddddddddd","merge_commit_sha":"eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee","merge_commit_tree":"dddddddddddddddddddddddddddddddddddddddd","tree_equal":true,"merge_actor":"chemitaro","merged_at":"2026-09-02T02:00:00Z","issue_finish_command":"python3 ./spec-dock/scripts/spec-dock issue finish","issue_finish_started_at":"2026-09-02T02:05:00Z","issue_finish_status":"finished","issue_finish_already_closed":false,"github_issue_closed_event_id":7001,"github_issue_closed_at":"2026-09-02T02:06:00Z","issue_finish_active_cleared":true,"issue_finish_post_sync_status":"completed","issue_finish_completed_at":"2026-09-02T02:07:00Z","generated_at":"2026-09-02T02:08:00Z"}
```

#### `epic-closure-v1.json`

```json
{"schema_version":1,"kind":"epic-closure-v1","repository":"chemitaro/spec-dock","epic_issue_number":384,"implementation_issue_number":392,"post_merge_comment_id":6002,"post_merge_payload_sha256":"b1df7fd0b8be353d735163736de8416fa4cec5d98abd83ef7a9922c579eb3946","implementation_issue_closed_event_id":7001,"implementation_issue_closed_at":"2026-09-02T02:06:00Z","epic_acceptance_status":"accepted","github_epic_closed_event_id":7002,"github_epic_closed_at":"2026-09-02T02:20:00Z","generated_at":"2026-09-02T02:21:00Z"}
```

#### `comment-receipt-pre-merge.json`

```json
{"schema_version":1,"kind":"comment-receipt-v1","attestation_kind":"pre-merge-attestation-v1","repository":"chemitaro/spec-dock","target_issue_number":392,"comment_id":6001,"comment_url":"https://api.github.com/repos/chemitaro/spec-dock/issues/comments/6001","author_login":"chemitaro","created_at":"2026-09-02T01:01:00Z","updated_at":"2026-09-02T01:01:00Z","payload_sha256":"81a8cb8ffac801b7aacb8909380b644be1e58e77a474127205d2785ebd8a1ea4","body_sha256":"2138870e141753c991cfa33965f85dd99c0797064b8cbba65ad99688e514c06e","body_size_bytes":1839,"verified_at":"2026-09-02T01:01:30Z"}
```

#### `comment-receipt-post-merge.json`

```json
{"schema_version":1,"kind":"comment-receipt-v1","attestation_kind":"post-merge-closure-v1","repository":"chemitaro/spec-dock","target_issue_number":392,"comment_id":6002,"comment_url":"https://api.github.com/repos/chemitaro/spec-dock/issues/comments/6002","author_login":"chemitaro","created_at":"2026-09-02T02:09:00Z","updated_at":"2026-09-02T02:09:00Z","payload_sha256":"b1df7fd0b8be353d735163736de8416fa4cec5d98abd83ef7a9922c579eb3946","body_sha256":"511b735d2c443f38a955b603590de7ecb8c54033639f561a7a0995f23574509c","body_size_bytes":1129,"verified_at":"2026-09-02T02:09:30Z"}
```

#### `comment-receipt-epic.json`

```json
{"schema_version":1,"kind":"comment-receipt-v1","attestation_kind":"epic-closure-v1","repository":"chemitaro/spec-dock","target_issue_number":384,"comment_id":6003,"comment_url":"https://api.github.com/repos/chemitaro/spec-dock/issues/comments/6003","author_login":"chemitaro","created_at":"2026-09-02T02:22:00Z","updated_at":"2026-09-02T02:22:00Z","payload_sha256":"f2d3870430a2095fee9dcc2c77ee2a273299dfa34d85841ca01247f61fd236ca","body_sha256":"a27d0c7ee31f505f6995b71a30502eff3e50259a765f59cbf4b94897d1db4cf8","body_size_bytes":643,"verified_at":"2026-09-02T02:22:30Z"}
```

#### `verify-downloaded-artifact.stdout.json`

```json
{"schema_version":1,"status":"completed","code":"downloaded-artifact-verified","command":"verify-downloaded-artifact","repository":"chemitaro/spec-dock","workflow_run_id":1101,"source_sha":"cccccccccccccccccccccccccccccccccccccccc","source_tree":"dddddddddddddddddddddddddddddddddddddddd","candidate_artifact_name":"provider-candidate-cccccccccccccccccccccccccccccccccccccccc","evidence_artifact_name":"provider-evidence-cccccccccccccccccccccccccccccccccccccccc","receipt_roles":["producer","linux-canonical","sdist-smoke","macos-delta"],"evidence_files":["provider-receipt-producer.json","producer-build-evidence.json","provider-receipt-linux-canonical.json","linux-canonical-evidence.json","provider-receipt-sdist-smoke.json","sdist-smoke-evidence.json","provider-receipt-macos-delta.json","macos-delta-evidence.json"]}
```

#### `emit-attestation.stdout.json`

```json
{"schema_version":1,"status":"completed","code":"attestation-emitted","command":"emit-attestation","kind":"pre-merge-attestation-v1","payload_path":"/runner/_temp/spec-dock-iss-00392-fixture/payload.json","payload_size_bytes":1706,"payload_sha256":"81a8cb8ffac801b7aacb8909380b644be1e58e77a474127205d2785ebd8a1ea4","comment_path":"/runner/_temp/spec-dock-iss-00392-fixture/comment.md","comment_size_bytes":1839,"comment_sha256":"2138870e141753c991cfa33965f85dd99c0797064b8cbba65ad99688e514c06e"}
```

#### `pre-merge-comment.md`

````text
<!-- spec-dock-attestation:pre-merge-attestation-v1:81a8cb8ffac801b7aacb8909380b644be1e58e77a474127205d2785ebd8a1ea4 -->
```json
{"schema_version":1,"kind":"pre-merge-attestation-v1","repository":"chemitaro/spec-dock","issue_number":392,"pull_request_number":500,"spec_freeze_commit":"8888888888888888888888888888888888888888","implementation_base_sha":"9999999999999999999999999999999999999999","compatibility_head_sha":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","compatibility_head_tree":"bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb","compatibility_workflow_run_id":1001,"final_head_sha":"cccccccccccccccccccccccccccccccccccccccc","final_head_tree":"dddddddddddddddddddddddddddddddddddddddd","final_workflow_run_id":1101,"compatibility_to_final_paths":[".github/workflows/provider-ci.yml"],"tracked_report_blob_sha1":"ffffffffffffffffffffffffffffffffffffffff","candidate_artifact":{"id":3100,"name":"provider-candidate-cccccccccccccccccccccccccccccccccccccccc","digest":"sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"},"evidence_artifact":{"id":3110,"name":"provider-evidence-cccccccccccccccccccccccccccccccccccccccc","digest":"sha256:0000000000000000000000000000000000000000000000000000000000000000"},"provider_evidence_sha256":"6b20606e234cbc0a43c6a89e98efdbc7fd59afe341293d4f6039bcfb166dbdfa","environment_fingerprint_sha256":"cbf2ec163715a448bbb572db757b604a75ebeaec635129e36255614e9a6c228c","required_contexts_before":["Provider CI / provider-tests"],"required_contexts_both":["Provider CI / provider-gate","Provider CI / provider-tests"],"canary_pull_request_number":501,"canary_block_verified":true,"required_contexts_after_old_removed":["Provider CI / provider-gate"],"required_contexts_final_head":["Provider CI / provider-gate"],"human_review_state":"approved","generated_at":"2026-09-02T01:00:00Z"}
```
````

#### `post-merge-comment.md`

````text
<!-- spec-dock-attestation:post-merge-closure-v1:b1df7fd0b8be353d735163736de8416fa4cec5d98abd83ef7a9922c579eb3946 -->
```json
{"schema_version":1,"kind":"post-merge-closure-v1","repository":"chemitaro/spec-dock","issue_number":392,"pre_merge_comment_id":6001,"pre_merge_payload_sha256":"81a8cb8ffac801b7aacb8909380b644be1e58e77a474127205d2785ebd8a1ea4","final_head_sha":"cccccccccccccccccccccccccccccccccccccccc","final_head_tree":"dddddddddddddddddddddddddddddddddddddddd","merge_commit_sha":"eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee","merge_commit_tree":"dddddddddddddddddddddddddddddddddddddddd","tree_equal":true,"merge_actor":"chemitaro","merged_at":"2026-09-02T02:00:00Z","issue_finish_command":"python3 ./spec-dock/scripts/spec-dock issue finish","issue_finish_started_at":"2026-09-02T02:05:00Z","issue_finish_status":"finished","issue_finish_already_closed":false,"github_issue_closed_event_id":7001,"github_issue_closed_at":"2026-09-02T02:06:00Z","issue_finish_active_cleared":true,"issue_finish_post_sync_status":"completed","issue_finish_completed_at":"2026-09-02T02:07:00Z","generated_at":"2026-09-02T02:08:00Z"}
```
````

#### `epic-closure-comment.md`

````text
<!-- spec-dock-attestation:epic-closure-v1:f2d3870430a2095fee9dcc2c77ee2a273299dfa34d85841ca01247f61fd236ca -->
```json
{"schema_version":1,"kind":"epic-closure-v1","repository":"chemitaro/spec-dock","epic_issue_number":384,"implementation_issue_number":392,"post_merge_comment_id":6002,"post_merge_payload_sha256":"b1df7fd0b8be353d735163736de8416fa4cec5d98abd83ef7a9922c579eb3946","implementation_issue_closed_event_id":7001,"implementation_issue_closed_at":"2026-09-02T02:06:00Z","epic_acceptance_status":"accepted","github_epic_closed_event_id":7002,"github_epic_closed_at":"2026-09-02T02:20:00Z","generated_at":"2026-09-02T02:21:00Z"}
```
````

Tests regenerate every fixture, recompute every size/hash, validate all parent-child/API/timestamp relations and verify both success stdout objects. Any byte, order, size, hash or relation drift is a specification/test defect.

## 10. Traceability

- D-001–006 implement RQ-008–017 including cleanup-only terminal recovery.
- D-007–010 implement RQ-001–007 and #387 admission.
- D-011–014 implement RQ-018–024 and transitional/final CI topology.
- D-015–026 are the complete Provider Gate/evidence/workspace/attestation wire and implement RQ-023–031.
- S70 creates both tracked PR-C heads; S80 is read-only evidence and comment work. `owner_decisions_required=[]`.
