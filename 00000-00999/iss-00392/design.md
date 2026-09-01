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
  sha: "3c24bae76e86651f958bde7c716c5453fff73e56"
---

# iss-00392 Provider Lifecycle And Regression Gate Hard Cutover — 設計

## 1. Production topology and exact symbols

```text
src/spec_dock/
  cli.py
  context_pack.py                                  new
  provider_lifecycle/                              new
    __init__.py
    model.py
    candidate.py
    filesystem.py
    external_workspace.py
    stage_namespace.py
    legacy_023.py
    service.py
    public_result.py
  assets/legacy_0_2_3.json                         new
scripts/provider_gate.py                           new at S70
ci/linux-qualification.Dockerfile                  new at S70
ci/linux-qualification-environment.json            new at S70
```

Final removes `managed_distribution.py`, `assets/managed_distribution.json`, old distribution tests, root lane hook, ledger/timing/sharder and old main-push workflow only at their specified steps.

Exact model exports include path constants; `LifecycleState`, `LifecycleOperation`, `LifecycleStatus`, `SeedPolicy`; `ResumeIdentity`; strict record/marker/result/action types; phase/reason/code enums generated from the wire artifact. Candidate module owns capture/digest/materialize. Filesystem owns bound descriptors/native rename/bootstrap. Stage namespace owns persistent discovery. External workspace owns ephemeral evidence directories. Service owns classification/dispatch/install/update/uninstall/resume. Public result owns only table-driven wire rendering.

## 2. Lifecycle, candidate and public wire

### I392-D-001 — Target/state model

Targets and state relations are fixed by Issue Requirement and the wire artifact. Record/marker parsing is strict and no unknown enum is representable. Candidate digest includes version and sorted path/kind/mode/content entries for four roots/two slots; source/stage digests match; seeds/record/generated markers are excluded.

### I392-D-002 — Operation protocols

Install/update and uninstall follow the exact wire phase sequences. The first target-state publication is incomplete record after any required container bootstrap. Terminal record is last. Same tuple resume derives remaining work from descriptor-bound target observations, not a stored progress list. Cross tuple blocks before mutation.

### I392-D-003 — Public wire integration

`provider-lifecycle-wire-contract.md` is parsed into generated constants during tests and mirrored by typed source constants. Tests assert 36 code values, 123 complete relation rows, 4 record goldens and 16 public JSON review goldens. Each service result must select exactly one row. Unknown or multiple row selection raises a programming defect; no generic code catches it.

## 3. Persistent lifecycle stage namespace

### I392-D-004 — Exact path and identity derivation

```text
namespace = repository_realpath.parent / ".spec-dock-provider-stages-v1"
repository_key = sha256(repo_realpath_utf8 + NUL + st_dev + NUL + st_ino)
tuple_key = sha256(operation + NUL + candidate_digest + NUL + seed_policy)
repo_dir = namespace / "repositories" / repository_key
active = repo_dir / "ACTIVE.json"
stage = repo_dir / "stages" / tuple_key
```

All hashes are lowercase hex; decimal device/inode contain no padding. Namespace and stage must be on repository `st_dev`. Directory modes are 0700; JSON modes 0600; current UID; no symlink component; regular JSON link count one.

### I392-D-005 — Sentinel schemas

`NAMESPACE.json` exact ordered keys:

```text
schema_version,kind,purpose,owner_uid,parent_device,parent_inode,created_at
```

Values: schema1, kind `spec-dock-stage-namespace`, purpose `provider-lifecycle-stage-v1`.

`REPOSITORY.json` exact keys:

```text
schema_version,kind,repository_key,repository_realpath_sha256,
repository_device,repository_inode,owner_uid
```

`ACTIVE.json` exact keys:

```text
schema_version,kind,state,repository_key,operation,candidate_digest,
seed_policy,tuple_key,stage_relative_path,created_at,updated_at
```

State enum is `allocating|ready|terminal-cleanup`. `stage_relative_path` is exact `stages/<tuple-key>`.

`STAGE-OWNER.json` exact keys:

```text
schema_version,kind,purpose,repository_key,repository_realpath_sha256,
repository_device,repository_inode,operation,candidate_digest,seed_policy,
tuple_key,stage_device,stage_inode,created_spec_dock,registered_entries
```

Purpose exact `provider-lifecycle-stage-v1`; `created_spec_dock` is null or `{device,inode}`; registered entries are unique UTF-8 bytewise relative paths.

### I392-D-006 — Allocation, discovery and cleanup

1. validate/create namespace and repository sentinels descriptor-safely;
2. read exact `ACTIVE.json`; no directory scan;
3. absent ACTIVE: atomically no-replace publish `state=allocating` for requested tuple;
4. create/open deterministic stage; absent/empty exact stage is initialized, unsafe/nonempty unowned stage blocks;
5. write/fsync stage owner, then atomically update ACTIVE to ready;
6. same tuple process restart reopens exact ACTIVE/stage/owner and resumes;
7. mismatched tuple returns `stage-owner-mismatch`;
8. bootstrap-before-record uses ACTIVE+owner created identity;
9. terminal cleanup updates ACTIVE to terminal-cleanup, removes only registered stage entries/stage, then exact content-bound ACTIVE; crash at any point is deterministic cleanup resume;
10. namespace/repository sentinels are retained. Unknown siblings/content are never scanned or removed.

Tests kill/restart subprocesses after ACTIVE allocation, stage creation, owner write, container mkdir and terminal-record publication on Linux and macOS.

## 4. Ephemeral external workspace and protected witness

### I392-D-007 — Workspace helper

`external_workspace.py` exposes `create_external_workspace(repository,purpose,parent=None)` and `cleanup_external_workspace(handle)`. Purpose enum is exactly:

```text
admission
baseline-build
protected-witness
full-regression-s00
full-regression-s30
full-regression-s60
tripwire
fresh-consumer
workflow-api
artifact-download
attestation-draft
```

Creation uses `tempfile.mkdtemp(prefix="spec-dock-iss-00392-",dir=validated_parent)`, mode0700. It resolves parent/workspace/repository, rejects repository/equal/descendant, symlink components, wrong UID, group/other write and identity drift. `OWNER.json` exact keys are schema_version,kind,issue_id,purpose,repository_realpath_sha256,owner_uid,nonce,root_device,root_inode,created_at; mode0600/O_EXCL/O_NOFOLLOW, canonical compact LF, fsynced.

Cleanup receives a non-serializable handle with captured parent/root fds/identity and exact sentinel bytes; it deletes only registered relative paths. Unknown entry, missing/replaced sentinel or containment change preserves all and returns hard failure.

### I392-D-008 — Protected and exclusion manifests

`protected-manifest.json` outside repository captures every protected entry. Sort is UTF-8 bytes. Row exact keys: path,kind,mode,uid,gid,size,sha256,link_target_hex,device_major,device_minor. Non-applicable scalar is null. Directory itself is included.

Exclude exactly:

```text
spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00384-provider-test-strategy-simplification-and-execution-cost-reduction/issues/iss-00392-provider-lifecycle-and-regression-gate-hard-cutover/report.md
spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00384-provider-test-strategy-simplification-and-execution-cost-reduction/issues/iss-00392-provider-lifecycle-and-regression-gate-hard-cutover/.meta.json
```

`authorized-exclusions.json` exact keys: schema_version,repository,base_tree,current_tree,entries. Entry keys: path,kind,mode_before,mode_after,blob_before,blob_after,parent_commits,authorized_step,allowed_role,semantic_diff_sha256. Report role allows only front matter plus Result Summary/Verification/Residual Risks/step evidence and forbids final-source/post-merge facts. Meta role allows only parsed `updated_at` difference. No missing/additional field, path or mode change.

## 5. Issue #387 `ISS387-THREE-WAY-V2`

### I392-D-009 — Report and tail

Report block schema is the register's schema3. It has candidate SHA/tree and entries, no PR number/merge facts. Candidate is last semantic #387 commit. Tail changed paths are required report and optional meta only. Report remains regular 100644 and contains evidence sections/block only; meta remains canonical schema with only updated_at changed.

### I392-D-010 — Unique PR discovery

S00 fetches:

```text
GET /repos/chemitaro/spec-dock/commits/<candidate>/pulls
GET /repos/chemitaro/spec-dock/issues/387/timeline
```

It intersects PR numbers, then filters exact repo, base main, merged, candidate ancestry, exact tail and final-head/merge tree equality. Exactly one result is required. It records final PR/head/tree/merge after merge externally; none are required in the pre-merge report. Then merged report/ledger/collection are evaluated by the register.

## 6. PR-B current gate and dogfood

### I392-D-011 — S40/S50/S60 ownership

S40 does not touch checked-in dogfood. S50 uses external consumers. S60 owns current `provider-ci.yml`, `provider-full-regression.yml`, ledger/timing/conftest/lane consumers, old engine/test removal, lifecycle docs/AGENTS lifecycle paragraphs, admitted behavior fixes and complete dogfood migration.

Retained Full Regression workflow adds step `Create external full-regression workspace`, using the external helper with parent `${{ runner.temp }}` and purpose `full-regression-s60`; step output `artifact_dir` is passed to verifier and upload-artifact path. Name, push/main+dispatch triggers, concurrency, job id and evaluator remain otherwise unchanged.

### I392-D-012 — Complete S60/S70 dogfood

S60 migrates exact legacy dogfood once after all PR-B candidate bytes settle. S70 updates once after all final candidate bytes settle. At each checkpoint record/markers/candidate digest/root/slot parity are complete, seeds/protected witnesses unchanged, no ACTIVE/stage residue remains, validate and fresh-consumer pass. S80 is read-only.

## 7. Final Provider CI topology

### I392-D-013 — Exact jobs and two workflow heads

Authoritative jobs:

```text
provider-build-artifacts: []
provider-linux-canonical: [provider-build-artifacts]
provider-sdist-smoke: [provider-build-artifacts]
provider-macos-delta: [provider-build-artifacts]
provider-attestation: [provider-build-artifacts,provider-linux-canonical,provider-sdist-smoke,provider-macos-delta]
provider-gate: [provider-attestation]
```

`PRC_COMPAT_HEAD` additionally has:

```text
provider-tests: [provider-attestation]
```

Compatibility job downloads `provider-evidence-SOURCE_SHA`, runs `verify-downloaded-artifact` against API metadata, and exits by that verifier. It ignores canary marker. `provider-gate` fails exact if `.github/provider-gate-canary-red` exists. Thus canary proves new required context while old remains GREEN. `PRC_FINAL_HEAD` removes only this job block; all other workflow bytes are identical.

### I392-D-014 — Artifact names and file sets

For `SOURCE_SHA`:

```text
provider-candidate-SOURCE_SHA
provider-receipt-producer-SOURCE_SHA
provider-receipt-linux-canonical-SOURCE_SHA
provider-receipt-sdist-smoke-SOURCE_SHA
provider-receipt-macos-delta-SOURCE_SHA
provider-evidence-SOURCE_SHA
```

Candidate artifact: exactly candidate-manifest.json, one wheel, one sdist. Each receipt artifact: exact receipt JSON plus exact role evidence JSON. Evidence artifact: exact nine files in this order:

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

## 8. Exact evidence byte schemas

### I392-D-015 — Canonical JSON convention

All evidence JSON is UTF-8, no NUL, `ensure_ascii=False`, separators comma/colon, declared key insertion order, no additional/duplicate keys and exactly one LF. Timestamp type is UTC RFC3339 seconds `YYYY-MM-DDTHH:MM:SSZ`. IDs are positive JSON integers. Sizes are integer bytes; times/ratios are finite nonnegative JSON numbers with units encoded in field names. SHA-256 is 64 lowercase hex; Git SHA/tree is 40 lowercase hex. Child hashes are SHA-256 of the complete canonical child file bytes including LF.

### I392-D-016 — Candidate manifest schema

Exact ordered keys/types:

| Key | Type/value |
|---|---|
| schema_version | integer 1 |
| kind | `provider-candidate-manifest` |
| repository | `chemitaro/spec-dock` |
| source_sha | Git SHA |
| source_tree | Git tree |
| workflow_run_id | positive integer |
| workflow_run_attempt | positive integer |
| build_job_id | positive integer |
| build_job_name | `provider-build-artifacts` |
| build_invocation_count | integer 1 |
| candidate_digest | SHA-256 |
| wheel | object keys `filename,size_bytes,sha256` |
| sdist | object keys `filename,size_bytes,sha256` |
| files_order | exact `['wheel','sdist']` |

### I392-D-017 — Receipt schema

Every receipt has exact keys:

```text
schema_version,kind,role,repository,source_sha,source_tree,
workflow_run_id,workflow_run_attempt,job_id,job_name,needs,status,
build_invocation_count,candidate_artifact,candidate_manifest,wheel,sdist,
evidence,started_at,completed_at
```

- kind `provider-job-receipt`; role enum producer,linux-canonical,sdist-smoke,macos-delta; status `passed`.
- `needs` exact: producer `[]`; each consumer `['provider-build-artifacts']`.
- build count producer1, consumers0.
- candidate_artifact keys `id,name,digest`; name exact; digest API SHA-256 format.
- candidate_manifest/wheel/sdist/evidence keys `filename,size_bytes,sha256`.
- evidence filenames are role-fixed. Receipt parent artifact metadata is bound later by provider aggregate to avoid self-reference.

### I392-D-018 — Role evidence common envelope

Every role evidence exact keys:

```text
schema_version,kind,role,repository,source_sha,source_tree,
workflow_run_id,workflow_run_attempt,job_id,job_name,status,started_at,
completed_at,build_invocation_count,candidate_manifest_sha256,
wheel_sha256,sdist_sha256,details
```

Kind `provider-role-evidence`, status `passed`; identity equals its receipt. `details` schemas:

- producer ordered keys: `packaging_argv,packaging_exit_code,output_file_count,candidate_digest`; argv exact `['uv','build','--sdist','--wheel','--out-dir',<job external dir>]`, exit0, output2.
- linux-canonical ordered keys: `environment_id,environment_descriptor_sha256,environment_fingerprint_sha256,runner_image,container_image_id,kernel_release,cgroup_cpu_quota,cgroup_memory_limit_bytes,python_version,uv_version,lock_sha256,pytest_process_count,worker_count,run_count,budget_run_count,wall_seconds,process_tree_cpu_seconds,cpu_wall_ratios,unexpected_failure_count,flake_count,retry_count,seeded_fault_total,seeded_fault_detected,node_inventory_sha256`. Metric arrays are exact length20 in run order; process/worker1; run20; budget5; faults equal/detected; failure/flake/retry0.
- sdist-smoke ordered keys: `installed_from_filename,metadata_name,metadata_version,package_data_sha256,smoke_argv,smoke_exit_code`; filename equals manifest, metadata `spec-dock`/`0.2.4`, exit0.
- macos-delta ordered keys: `runner_image,macos_version,architecture,python_version,pytest_process_count,node_inventory_sha256,native_positive_control_total,native_positive_control_detected,platform_check_ids,failed_count`; process1, controls equal, failed0, check IDs exact sorted owner map.

### I392-D-019 — Provider aggregate schema

`provider-evidence.json` exact keys:

```text
schema_version,kind,repository,source_sha,source_tree,workflow_run_id,
workflow_run_attempt,status,candidate_artifact,receipt_artifacts,roles,
file_manifest,aggregate
```

Kind `provider-evidence`, status `passed`. Candidate artifact object keys `id,name,digest,manifest_sha256,wheel_sha256,sdist_sha256`. Receipt artifacts is four objects in role order with keys `role,id,name,digest`. Roles is four objects with `role,job_id,job_name,receipt_filename,receipt_sha256,evidence_filename,evidence_sha256`. `file_manifest` lists the eight subordinate files in exact evidence-file order, each `filename,size_bytes,sha256`. `aggregate` keys are `producer_build_invocation_count,consumer_build_invocation_count,role_count,file_count,environment_id,environment_fingerprint_sha256,qualification_run_count,budget_run_count,seeded_fault_total,seeded_fault_detected,status`; values 1,0,4,9,stable ID/fingerprint,20,5,equal/equal,passed.

Provider-attestation downloads actual candidate/receipts/evidence/API bytes, validates, copies the exact role bytes and writes aggregate. It reopens and rehashes all nine output files before upload.

## 9. Download verifier and attestations

### I392-D-020 — `verify-downloaded-artifact`

Exact invocation:

```bash
uv run python scripts/provider_gate.py verify-downloaded-artifact \
  --repository chemitaro/spec-dock \
  --candidate-dir "$EXTERNAL/candidate" \
  --evidence-dir "$EXTERNAL/evidence" \
  --run-json "$EXTERNAL/api/run.json" \
  --jobs-json "$EXTERNAL/api/jobs.json" \
  --artifacts-json "$EXTERNAL/api/artifacts.json" \
  --source-sha "$PRC_FINAL_HEAD" \
  --source-tree "$PRC_FINAL_TREE" \
  --workflow-run-id "$RUN_ID" \
  --json
```

Required directory/API inputs are real, owner-bound, no-follow paths. The verifier reads candidate manifest, wheel, sdist, all nine evidence files and all API JSON bytes; validates exact names/order/counts, schemas, source/run/job/needs/artifact identities, sizes/hashes, build counts and role metrics; and rejects stated hashes without matching bytes.

Success stdout is one compact LF JSON with exact keys `schema_version,status,code,repository,workflow_run_id,source_sha,source_tree,candidate_artifact,evidence_artifact,receipt_roles,evidence_files`; status is `verified`, code is `downloaded-artifact-verified`. Non-JSON success is exact `provider-gate: downloaded artifact verified sha=SOURCE_SHA run=RUN_ID\n`. Failure stdout is empty and stderr is `provider-gate: CODE: MESSAGE\n`. Exit/code mapping is: 2 `invalid-arguments`, 3 `input-invalid`, 4 `run-identity-mismatch`, 5 `artifact-set-mismatch`, 6 `artifact-metadata-mismatch`, 7 `candidate-manifest-invalid`, 8 `candidate-bytes-mismatch`, 9 `receipt-invalid`, 10 `receipt-set-or-needs-mismatch`, 11 `build-count-mismatch`, 12 `evidence-bytes-or-relation-mismatch`. No generic exit/code is valid.

### I392-D-021 — Attestation payload schemas

Pre-merge payload exact ordered keys:

```text
schema_version,kind,repository,issue_number,pull_request_number,
spec_freeze_commit,implementation_base_sha,compatibility_head_sha,
final_head_sha,final_head_tree,compatibility_to_final_paths,
tracked_report_blob_sha1,provider_workflow_run_id,candidate_artifact,
evidence_artifact,provider_evidence_sha256,environment_fingerprint_sha256,
required_contexts_before,required_contexts_both,canary_pull_request_number,
canary_block_verified,required_contexts_after_old_removed,
required_contexts_final_head,human_review_state,generated_at
```

Values: schema1, kind pre-merge-attestation-v1, issue392; compatibility-to-final exact `['.github/workflows/provider-ci.yml']`; context arrays unique UTF-8 sorted; booleans exact; human_review_state `approved`; artifact objects `id,name,digest`.

Post-merge payload keys:

```text
schema_version,kind,repository,issue_number,pre_merge_comment_id,
pre_merge_payload_sha256,final_head_sha,final_head_tree,merge_commit_sha,
merge_commit_tree,tree_equal,merge_actor,merged_at,spec_dock_finish_status,
github_issue_closed_event_id,github_issue_closed_at,generated_at
```

Kind post-merge-closure-v1, issue392, tree_equal true, finish status `finished`, IDs positive.

Epic closure payload keys:

```text
schema_version,kind,repository,epic_issue_number,implementation_issue_number,
post_merge_comment_id,post_merge_payload_sha256,
implementation_issue_closed_event_id,epic_acceptance_status,
github_epic_closed_event_id,github_epic_closed_at,generated_at
```

Kind epic-closure-v1, epic384, implementation392, acceptance `accepted`.

### I392-D-022 — `emit-attestation` and append-only GitHub Issue comment

Exact pure-local invocation:

```bash
uv run python scripts/provider_gate.py emit-attestation \
  --kind pre-merge-attestation-v1 \
  --input-json "$EXTERNAL/input.json" \
  --output-json "$EXTERNAL/pre-merge-attestation.json" \
  --output-comment "$EXTERNAL/pre-merge-attestation-comment.md" \
  --json
```

Kinds are exactly the three I392-D-021 schemas. Input is an exact-key JSON object for that kind; the command rejects unknown/missing/duplicate keys, noncanonical scalar types and relation violations. It writes with `O_CREAT|O_EXCL|O_NOFOLLOW`, mode 0600, refuses existing/symlink/output-outside-owner-workspace paths, fsyncs files/directories and rereads exact bytes. Output JSON is the canonical payload. Comment bytes are exactly:

````text
<!-- spec-dock-attestation:KIND:PAYLOAD_SHA256 -->
```json
CANONICAL_JSON_WITHOUT_FINAL_LF
```
````

The comment ends with exactly one LF. Success JSON keys are `schema_version,status,code,kind,payload_path,comment_path,payload_sha256,target_issue_number`; status `emitted`, code `attestation-emitted`, exit 0. Typed failures are exit 2 `attestation-invalid-arguments`, 3 `attestation-input-invalid`, 4 `attestation-relation-invalid`, 5 `attestation-output-unsafe`, 6 `attestation-serialization-mismatch`. Failure stdout is empty; stderr is exact `provider-gate: CODE: MESSAGE\n`; no generic code.

The immutable external object type is only a GitHub **Issue comment**. Pre/post comments target Issue #392; Epic closure targets Issue #384. Posting uses `POST /repos/chemitaro/spec-dock/issues/{issue_number}/comments` with a human operator credential having `issues:write`. Verification uses `GET /repos/chemitaro/spec-dock/issues/comments/{comment_id}` with `issues:read` and requires exact repository/issue, positive comment ID, expected operator login, exact body bytes and marker/payload hash, `created_at == updated_at`, and nondeleted visibility. PATCH/edit/delete, a different actor, changed timestamps/body/hash or ambiguous comment lookup invalidates dependent closure evidence.

### I392-D-023 — Stable environment

Descriptor and Linux evidence satisfy Requirement. All 20 metric arrays share one fingerprint and exact source/candidate. Cross-run fingerprint difference is schema/relation failure, not a warning.

## 10. Required-context two-head state machine

States are exact:

```text
compat-head-both-green
new-added-both-required
canary-new-red-old-green-blocked
implementation-both-green
old-removed-new-required
final-head-new-only-green
```

Transitions occur only in this order. Canary diff is exactly add `.github/provider-gate-canary-red`; never merged. Final implementation diff from compatibility head is exactly removal of `provider-tests` job in `provider-ci.yml`. Any other tracked change creates a new compatibility head and repeats transition/evidence.

## 11. Canonical evidence and attestation byte fixtures

### I392-D-024 — `EVIDENCE-FIXTURE-V1`

This fixture set is normative serializer test data, not runtime evidence. Runtime values vary only where the schemas above permit, but key order, types, enum/nullability, units, nested order and LF rule remain exact. Every hash below is SHA-256 over the complete displayed compact UTF-8 file bytes including the final LF.

| File | Size bytes | SHA-256 |
|---|---:|---|
| `candidate-manifest.json` | 757 | `122f30ab0179d47b01932b30ddb3eca77a7244e53191cdc2fc49f8839b73ae3b` |
| `producer-build-evidence.json` | 937 | `1733bd8d54b0f7b9ed65b636dbfec735139985fb4821decabdd01069fb238a8a` |
| `linux-canonical-evidence.json` | 1894 | `4b65c3c463c33c7a6407b2f351bfb007679fffadcdfee306f23049a3889c87c8` |
| `sdist-smoke-evidence.json` | 977 | `599c7d8b9efc4b2fcb2d51fdd574b0188d5882dbdfd5169f6cf8962904e3cf88` |
| `macos-delta-evidence.json` | 1102 | `88d9f20248ec33162ced7bd39282635137f9500db44ad8517e9d9f233b3f8f2e` |
| `provider-receipt-producer.json` | 1227 | `abad22d4051082e74a9eccf1140d0b09c6026bb8118ee4f4a3759c378042b9f0` |
| `provider-receipt-linux-canonical.json` | 1262 | `a5edd22f555f82c7e1f70200c059c12a8c4c774fc314bf175dd24efd8fc0dc5b` |
| `provider-receipt-sdist-smoke.json` | 1249 | `f4e04a3447eb4a2ba5b9c852ca7d8a6c578fa23482d7b4618a53512f62487cc7` |
| `provider-receipt-macos-delta.json` | 1250 | `b03cf780550b6b08c0b651fe21bc17614b880923d406f3c2d2e5b9bf2a261152` |
| `provider-evidence.json` | 4421 | `94272066af6b6abb1968f8128ca1cc1acf634f6846cd42824ef0bbc9bd920e42` |
| `pre-merge-attestation-v1.json` | 1603 | `4e9ed28d018491c401b632d413b53bd630d0e4403d30c064f89494c2d2722103` |
| `post-merge-closure-v1.json` | 712 | `e1c6154b5a09c17b7d1e3eb391473e7a8f821485a9bf4fe2f982561404a89d3b` |
| `epic-closure-v1.json` | 463 | `75af5796dd0efc8bc50ee51a592db8142d63263d66b89f56dd81f58190d2765b` |
| `pre-merge-attestation-v1.comment.md` | 1736 | `1b743daff62ce1892c7c683a608510ad5dbaf819e9a946a4560942954bb22035` |
| `post-merge-closure-v1.comment.md` | 842 | `aa99ecad273b0de5adf9819361bd2274b4928f269e14d3b28c2fb987462237a7` |
| `epic-closure-v1.comment.md` | 587 | `098761c85afada8ccb11ecc7f68e877b426950d7831ae209c3b852d5e4d49611` |

Type and unit closure: all IDs/counts/byte sizes are nonnegative integers except IDs, which are positive; `cgroup_cpu_quota`, wall/CPU seconds and ratios are finite JSON numbers; timestamp fields are UTC RFC3339 seconds; hash/commit/tree/image values use the scalar formats in I392-D-015; arrays have the exact lengths/order stated in I392-D-016–019 and I392-D-021. None of these fixture schemas contains a nullable field. A runtime nullable field is invalid unless explicitly declared elsewhere in the same schema.

#### `candidate-manifest.json`

```json
{"schema_version":1,"kind":"provider-candidate-manifest","repository":"chemitaro/spec-dock","source_sha":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","source_tree":"bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb","workflow_run_id":1001,"workflow_run_attempt":1,"build_job_id":2001,"build_job_name":"provider-build-artifacts","build_invocation_count":1,"candidate_digest":"cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc","wheel":{"filename":"spec_dock-0.2.4-py3-none-any.whl","size_bytes":123456,"sha256":"dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd"},"sdist":{"filename":"spec_dock-0.2.4.tar.gz","size_bytes":234567,"sha256":"eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"},"files_order":["wheel","sdist"]}
```

#### `producer-build-evidence.json`

```json
{"schema_version":1,"kind":"provider-role-evidence","role":"producer","repository":"chemitaro/spec-dock","source_sha":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","source_tree":"bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb","workflow_run_id":1001,"workflow_run_attempt":1,"job_id":2001,"job_name":"provider-build-artifacts","status":"passed","started_at":"2026-09-01T00:00:00Z","completed_at":"2026-09-01T00:10:00Z","build_invocation_count":1,"candidate_manifest_sha256":"122f30ab0179d47b01932b30ddb3eca77a7244e53191cdc2fc49f8839b73ae3b","wheel_sha256":"dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd","sdist_sha256":"eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee","details":{"packaging_argv":["uv","build","--sdist","--wheel","--out-dir","/runner/_temp/spec-dock-build"],"packaging_exit_code":0,"output_file_count":2,"candidate_digest":"cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"}}
```

#### `linux-canonical-evidence.json`

```json
{"schema_version":1,"kind":"provider-role-evidence","role":"linux-canonical","repository":"chemitaro/spec-dock","source_sha":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","source_tree":"bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb","workflow_run_id":1001,"workflow_run_attempt":1,"job_id":2002,"job_name":"provider-linux-canonical","status":"passed","started_at":"2026-09-01T00:00:00Z","completed_at":"2026-09-01T00:10:00Z","build_invocation_count":0,"candidate_manifest_sha256":"122f30ab0179d47b01932b30ddb3eca77a7244e53191cdc2fc49f8839b73ae3b","wheel_sha256":"dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd","sdist_sha256":"eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee","details":{"environment_id":"specdock-linux-qualification-v1","environment_descriptor_sha256":"ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff","environment_fingerprint_sha256":"1111111111111111111111111111111111111111111111111111111111111111","runner_image":"ubuntu-24.04","container_image_id":"sha256:2222222222222222222222222222222222222222222222222222222222222222","kernel_release":"6.8.0","cgroup_cpu_quota":2.0,"cgroup_memory_limit_bytes":8589934592,"python_version":"3.11.9","uv_version":"0.8.14","lock_sha256":"3333333333333333333333333333333333333333333333333333333333333333","pytest_process_count":1,"worker_count":1,"run_count":20,"budget_run_count":5,"wall_seconds":[1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0],"process_tree_cpu_seconds":[0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5],"cpu_wall_ratios":[0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5],"unexpected_failure_count":0,"flake_count":0,"retry_count":0,"seeded_fault_total":27,"seeded_fault_detected":27,"node_inventory_sha256":"4444444444444444444444444444444444444444444444444444444444444444"}}
```

#### `sdist-smoke-evidence.json`

```json
{"schema_version":1,"kind":"provider-role-evidence","role":"sdist-smoke","repository":"chemitaro/spec-dock","source_sha":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","source_tree":"bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb","workflow_run_id":1001,"workflow_run_attempt":1,"job_id":2003,"job_name":"provider-sdist-smoke","status":"passed","started_at":"2026-09-01T00:00:00Z","completed_at":"2026-09-01T00:10:00Z","build_invocation_count":0,"candidate_manifest_sha256":"122f30ab0179d47b01932b30ddb3eca77a7244e53191cdc2fc49f8839b73ae3b","wheel_sha256":"dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd","sdist_sha256":"eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee","details":{"installed_from_filename":"spec_dock-0.2.4.tar.gz","metadata_name":"spec-dock","metadata_version":"0.2.4","package_data_sha256":"5555555555555555555555555555555555555555555555555555555555555555","smoke_argv":["python","-m","spec_dock.cli","--help"],"smoke_exit_code":0}}
```

#### `macos-delta-evidence.json`

```json
{"schema_version":1,"kind":"provider-role-evidence","role":"macos-delta","repository":"chemitaro/spec-dock","source_sha":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","source_tree":"bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb","workflow_run_id":1001,"workflow_run_attempt":1,"job_id":2004,"job_name":"provider-macos-delta","status":"passed","started_at":"2026-09-01T00:00:00Z","completed_at":"2026-09-01T00:10:00Z","build_invocation_count":0,"candidate_manifest_sha256":"122f30ab0179d47b01932b30ddb3eca77a7244e53191cdc2fc49f8839b73ae3b","wheel_sha256":"dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd","sdist_sha256":"eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee","details":{"runner_image":"macos-15","macos_version":"15.0","architecture":"arm64","python_version":"3.11.9","pytest_process_count":1,"node_inventory_sha256":"6666666666666666666666666666666666666666666666666666666666666666","native_positive_control_total":2,"native_positive_control_detected":2,"platform_check_ids":["executable-mode","installed-entry-point","no-follow","renameatx-np"],"failed_count":0}}
```

#### `provider-receipt-producer.json`

```json
{"schema_version":1,"kind":"provider-job-receipt","role":"producer","repository":"chemitaro/spec-dock","source_sha":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","source_tree":"bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb","workflow_run_id":1001,"workflow_run_attempt":1,"job_id":2001,"job_name":"provider-build-artifacts","needs":[],"status":"passed","build_invocation_count":1,"candidate_artifact":{"id":3000,"name":"provider-candidate-aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","digest":"sha256:7777777777777777777777777777777777777777777777777777777777777777"},"candidate_manifest":{"filename":"candidate-manifest.json","size_bytes":757,"sha256":"122f30ab0179d47b01932b30ddb3eca77a7244e53191cdc2fc49f8839b73ae3b"},"wheel":{"filename":"spec_dock-0.2.4-py3-none-any.whl","size_bytes":123456,"sha256":"dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd"},"sdist":{"filename":"spec_dock-0.2.4.tar.gz","size_bytes":234567,"sha256":"eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"},"evidence":{"filename":"producer-build-evidence.json","size_bytes":937,"sha256":"1733bd8d54b0f7b9ed65b636dbfec735139985fb4821decabdd01069fb238a8a"},"started_at":"2026-09-01T00:00:00Z","completed_at":"2026-09-01T00:10:00Z"}
```

#### `provider-receipt-linux-canonical.json`

```json
{"schema_version":1,"kind":"provider-job-receipt","role":"linux-canonical","repository":"chemitaro/spec-dock","source_sha":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","source_tree":"bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb","workflow_run_id":1001,"workflow_run_attempt":1,"job_id":2002,"job_name":"provider-linux-canonical","needs":["provider-build-artifacts"],"status":"passed","build_invocation_count":0,"candidate_artifact":{"id":3000,"name":"provider-candidate-aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","digest":"sha256:7777777777777777777777777777777777777777777777777777777777777777"},"candidate_manifest":{"filename":"candidate-manifest.json","size_bytes":757,"sha256":"122f30ab0179d47b01932b30ddb3eca77a7244e53191cdc2fc49f8839b73ae3b"},"wheel":{"filename":"spec_dock-0.2.4-py3-none-any.whl","size_bytes":123456,"sha256":"dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd"},"sdist":{"filename":"spec_dock-0.2.4.tar.gz","size_bytes":234567,"sha256":"eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"},"evidence":{"filename":"linux-canonical-evidence.json","size_bytes":1894,"sha256":"4b65c3c463c33c7a6407b2f351bfb007679fffadcdfee306f23049a3889c87c8"},"started_at":"2026-09-01T00:00:00Z","completed_at":"2026-09-01T00:10:00Z"}
```

#### `provider-receipt-sdist-smoke.json`

```json
{"schema_version":1,"kind":"provider-job-receipt","role":"sdist-smoke","repository":"chemitaro/spec-dock","source_sha":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","source_tree":"bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb","workflow_run_id":1001,"workflow_run_attempt":1,"job_id":2003,"job_name":"provider-sdist-smoke","needs":["provider-build-artifacts"],"status":"passed","build_invocation_count":0,"candidate_artifact":{"id":3000,"name":"provider-candidate-aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","digest":"sha256:7777777777777777777777777777777777777777777777777777777777777777"},"candidate_manifest":{"filename":"candidate-manifest.json","size_bytes":757,"sha256":"122f30ab0179d47b01932b30ddb3eca77a7244e53191cdc2fc49f8839b73ae3b"},"wheel":{"filename":"spec_dock-0.2.4-py3-none-any.whl","size_bytes":123456,"sha256":"dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd"},"sdist":{"filename":"spec_dock-0.2.4.tar.gz","size_bytes":234567,"sha256":"eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"},"evidence":{"filename":"sdist-smoke-evidence.json","size_bytes":977,"sha256":"599c7d8b9efc4b2fcb2d51fdd574b0188d5882dbdfd5169f6cf8962904e3cf88"},"started_at":"2026-09-01T00:00:00Z","completed_at":"2026-09-01T00:10:00Z"}
```

#### `provider-receipt-macos-delta.json`

```json
{"schema_version":1,"kind":"provider-job-receipt","role":"macos-delta","repository":"chemitaro/spec-dock","source_sha":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","source_tree":"bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb","workflow_run_id":1001,"workflow_run_attempt":1,"job_id":2004,"job_name":"provider-macos-delta","needs":["provider-build-artifacts"],"status":"passed","build_invocation_count":0,"candidate_artifact":{"id":3000,"name":"provider-candidate-aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","digest":"sha256:7777777777777777777777777777777777777777777777777777777777777777"},"candidate_manifest":{"filename":"candidate-manifest.json","size_bytes":757,"sha256":"122f30ab0179d47b01932b30ddb3eca77a7244e53191cdc2fc49f8839b73ae3b"},"wheel":{"filename":"spec_dock-0.2.4-py3-none-any.whl","size_bytes":123456,"sha256":"dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd"},"sdist":{"filename":"spec_dock-0.2.4.tar.gz","size_bytes":234567,"sha256":"eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"},"evidence":{"filename":"macos-delta-evidence.json","size_bytes":1102,"sha256":"88d9f20248ec33162ced7bd39282635137f9500db44ad8517e9d9f233b3f8f2e"},"started_at":"2026-09-01T00:00:00Z","completed_at":"2026-09-01T00:10:00Z"}
```

#### `provider-evidence.json`

```json
{"schema_version":1,"kind":"provider-evidence","repository":"chemitaro/spec-dock","source_sha":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","source_tree":"bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb","workflow_run_id":1001,"workflow_run_attempt":1,"status":"passed","candidate_artifact":{"id":3000,"name":"provider-candidate-aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","digest":"sha256:7777777777777777777777777777777777777777777777777777777777777777","manifest_sha256":"122f30ab0179d47b01932b30ddb3eca77a7244e53191cdc2fc49f8839b73ae3b","wheel_sha256":"dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd","sdist_sha256":"eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"},"receipt_artifacts":[{"role":"producer","id":3001,"name":"provider-receipt-producer-aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","digest":"sha256:1111111111111111111111111111111111111111111111111111111111111111"},{"role":"linux-canonical","id":3002,"name":"provider-receipt-linux-canonical-aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","digest":"sha256:2222222222222222222222222222222222222222222222222222222222222222"},{"role":"sdist-smoke","id":3003,"name":"provider-receipt-sdist-smoke-aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","digest":"sha256:3333333333333333333333333333333333333333333333333333333333333333"},{"role":"macos-delta","id":3004,"name":"provider-receipt-macos-delta-aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","digest":"sha256:4444444444444444444444444444444444444444444444444444444444444444"}],"roles":[{"role":"producer","job_id":2001,"job_name":"provider-build-artifacts","receipt_filename":"provider-receipt-producer.json","receipt_sha256":"abad22d4051082e74a9eccf1140d0b09c6026bb8118ee4f4a3759c378042b9f0","evidence_filename":"producer-build-evidence.json","evidence_sha256":"1733bd8d54b0f7b9ed65b636dbfec735139985fb4821decabdd01069fb238a8a"},{"role":"linux-canonical","job_id":2002,"job_name":"provider-linux-canonical","receipt_filename":"provider-receipt-linux-canonical.json","receipt_sha256":"a5edd22f555f82c7e1f70200c059c12a8c4c774fc314bf175dd24efd8fc0dc5b","evidence_filename":"linux-canonical-evidence.json","evidence_sha256":"4b65c3c463c33c7a6407b2f351bfb007679fffadcdfee306f23049a3889c87c8"},{"role":"sdist-smoke","job_id":2003,"job_name":"provider-sdist-smoke","receipt_filename":"provider-receipt-sdist-smoke.json","receipt_sha256":"f4e04a3447eb4a2ba5b9c852ca7d8a6c578fa23482d7b4618a53512f62487cc7","evidence_filename":"sdist-smoke-evidence.json","evidence_sha256":"599c7d8b9efc4b2fcb2d51fdd574b0188d5882dbdfd5169f6cf8962904e3cf88"},{"role":"macos-delta","job_id":2004,"job_name":"provider-macos-delta","receipt_filename":"provider-receipt-macos-delta.json","receipt_sha256":"b03cf780550b6b08c0b651fe21bc17614b880923d406f3c2d2e5b9bf2a261152","evidence_filename":"macos-delta-evidence.json","evidence_sha256":"88d9f20248ec33162ced7bd39282635137f9500db44ad8517e9d9f233b3f8f2e"}],"file_manifest":[{"filename":"provider-receipt-producer.json","size_bytes":1227,"sha256":"abad22d4051082e74a9eccf1140d0b09c6026bb8118ee4f4a3759c378042b9f0"},{"filename":"producer-build-evidence.json","size_bytes":937,"sha256":"1733bd8d54b0f7b9ed65b636dbfec735139985fb4821decabdd01069fb238a8a"},{"filename":"provider-receipt-linux-canonical.json","size_bytes":1262,"sha256":"a5edd22f555f82c7e1f70200c059c12a8c4c774fc314bf175dd24efd8fc0dc5b"},{"filename":"linux-canonical-evidence.json","size_bytes":1894,"sha256":"4b65c3c463c33c7a6407b2f351bfb007679fffadcdfee306f23049a3889c87c8"},{"filename":"provider-receipt-sdist-smoke.json","size_bytes":1249,"sha256":"f4e04a3447eb4a2ba5b9c852ca7d8a6c578fa23482d7b4618a53512f62487cc7"},{"filename":"sdist-smoke-evidence.json","size_bytes":977,"sha256":"599c7d8b9efc4b2fcb2d51fdd574b0188d5882dbdfd5169f6cf8962904e3cf88"},{"filename":"provider-receipt-macos-delta.json","size_bytes":1250,"sha256":"b03cf780550b6b08c0b651fe21bc17614b880923d406f3c2d2e5b9bf2a261152"},{"filename":"macos-delta-evidence.json","size_bytes":1102,"sha256":"88d9f20248ec33162ced7bd39282635137f9500db44ad8517e9d9f233b3f8f2e"}],"aggregate":{"producer_build_invocation_count":1,"consumer_build_invocation_count":0,"role_count":4,"file_count":9,"environment_id":"specdock-linux-qualification-v1","environment_fingerprint_sha256":"1111111111111111111111111111111111111111111111111111111111111111","qualification_run_count":20,"budget_run_count":5,"seeded_fault_total":27,"seeded_fault_detected":27,"status":"passed"}}
```

#### `pre-merge-attestation-v1.json`

```json
{"schema_version":1,"kind":"pre-merge-attestation-v1","repository":"chemitaro/spec-dock","issue_number":392,"pull_request_number":500,"spec_freeze_commit":"8888888888888888888888888888888888888888","implementation_base_sha":"9999999999999999999999999999999999999999","compatibility_head_sha":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","final_head_sha":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","final_head_tree":"bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb","compatibility_to_final_paths":[".github/workflows/provider-ci.yml"],"tracked_report_blob_sha1":"cccccccccccccccccccccccccccccccccccccccc","provider_workflow_run_id":1001,"candidate_artifact":{"id":3000,"name":"provider-candidate-aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","digest":"sha256:7777777777777777777777777777777777777777777777777777777777777777"},"evidence_artifact":{"id":3010,"name":"provider-evidence-aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","digest":"sha256:8888888888888888888888888888888888888888888888888888888888888888"},"provider_evidence_sha256":"94272066af6b6abb1968f8128ca1cc1acf634f6846cd42824ef0bbc9bd920e42","environment_fingerprint_sha256":"1111111111111111111111111111111111111111111111111111111111111111","required_contexts_before":["Provider CI / provider-tests"],"required_contexts_both":["Provider CI / provider-gate","Provider CI / provider-tests"],"canary_pull_request_number":501,"canary_block_verified":true,"required_contexts_after_old_removed":["Provider CI / provider-gate"],"required_contexts_final_head":["Provider CI / provider-gate"],"human_review_state":"approved","generated_at":"2026-09-01T01:00:00Z"}
```

#### `post-merge-closure-v1.json`

```json
{"schema_version":1,"kind":"post-merge-closure-v1","repository":"chemitaro/spec-dock","issue_number":392,"pre_merge_comment_id":6001,"pre_merge_payload_sha256":"4e9ed28d018491c401b632d413b53bd630d0e4403d30c064f89494c2d2722103","final_head_sha":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","final_head_tree":"bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb","merge_commit_sha":"dddddddddddddddddddddddddddddddddddddddd","merge_commit_tree":"bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb","tree_equal":true,"merge_actor":"chemitaro","merged_at":"2026-09-01T02:00:00Z","spec_dock_finish_status":"finished","github_issue_closed_event_id":7001,"github_issue_closed_at":"2026-09-01T02:10:00Z","generated_at":"2026-09-01T02:11:00Z"}
```

#### `epic-closure-v1.json`

```json
{"schema_version":1,"kind":"epic-closure-v1","repository":"chemitaro/spec-dock","epic_issue_number":384,"implementation_issue_number":392,"post_merge_comment_id":6002,"post_merge_payload_sha256":"e1c6154b5a09c17b7d1e3eb391473e7a8f821485a9bf4fe2f982561404a89d3b","implementation_issue_closed_event_id":7001,"epic_acceptance_status":"accepted","github_epic_closed_event_id":7002,"github_epic_closed_at":"2026-09-01T02:20:00Z","generated_at":"2026-09-01T02:21:00Z"}
```

The three comment fixtures use this exact four-line envelope: marker line, opening `json` fence, the compact payload without its final LF, closing fence; the comment itself ends with one LF. Their byte hashes are in the table. No prose, blank line or alternate fence is permitted.

Fixture verification regenerates every object from typed constructors, compares exact bytes/size/hash, parses every JSON file, verifies all child hashes against actual bytes, and verifies each attestation comment marker/hash/body. A fixture drift requires canonical specification amendment; tests do not rewrite the expected hash table.


## 12. Traceability

- D-001–003 implement RQ-008–016.
- D-004–006 implement RQ-006–007/010–012.
- D-007–010 implement RQ-001–006 and #387 RQ-002–003.
- D-011–012 implement RQ-017–020.
- D-013–024 implement RQ-021–027.
