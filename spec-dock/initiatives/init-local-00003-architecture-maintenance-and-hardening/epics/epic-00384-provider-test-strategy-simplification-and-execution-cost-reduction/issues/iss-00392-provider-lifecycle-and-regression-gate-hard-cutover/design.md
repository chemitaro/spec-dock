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
  sha: "f96d031ea86d3757374f3de14d588f1ba09a0864"
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

The terminal cleanup prelude never interprets a new request until old cleanup is safely complete.

### I392-D-003 — Wire integration

Tests parse the normative artifact and assert 37 codes, 123 rows, four record goldens, sixteen public review goldens, phase/reason/order inventories and exact JSON/text bytes. A typed result selects exactly one row; zero/multiple match is a programming defect.

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
9. Safe cleanup proceeds to any new requested operation; old tuple no longer gates dispatch.
10. Cleanup failure keeps exact recoverable evidence and returns `terminal-cleanup-failed`, using result family to select retry.
11. Namespace/repository sentinels remain; unknown siblings are never inspected or removed.

Tests kill/restart subprocesses after ACTIVE allocation, owner write, container mkdir, terminal record, ACTIVE terminal-cleanup write, stage removal and ACTIVE unlink.

## 4. Independent ephemeral workspaces and protected witness

### I392-D-007 — Workspace helper and exact variables

`create_external_workspace(repository,purpose,parent=None) -> ExternalWorkspace` returns a path and non-serializable handle holding parent/root FDs, device/inode/UID/mode, exact sentinel bytes, nonce and registered child set. `cleanup_external_workspace(handle)` accepts no path argument.

Exact purpose/env mapping:

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

Each path is independently created by `tempfile.mkdtemp(prefix="spec-dock-iss-00392-",dir=validated_parent)`. No aggregate root env variable or implicit subdirectory purpose exists. An orchestrator keeps multiple handles in memory and exports paths only to child commands.

`OWNER.json` exact keys: `schema_version,kind,issue_id,purpose,repository_realpath_sha256,owner_uid,nonce,root_device,root_inode,created_at`; mode0600/O_EXCL/O_NOFOLLOW/canonical LF. Cleanup reopens exact parent/root, verifies outside-repository relation, device/inode/UID/mode/sentinel, rejects unknown entries, deletes registered entries then root and fsyncs parent.

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

The retained workflow creates its own full-regression-s60 workspace below `${{ runner.temp }}` using the same helper, retains the handle in the job process, passes exact path to verifier, uploads exact path, and handle-cleans after upload. It does not use repository workbench or an aggregate workspace.

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

## 8. Exact evidence byte schemas

### I392-D-015 — Canonical JSON

All JSON is UTF-8, no NUL, declared key order, `ensure_ascii=False,separators=(",",":")`, no extras/duplicates, one final LF. Timestamps are UTC seconds. IDs positive integers. Sizes bytes. Hashes include child LF.

### I392-D-016 — Candidate manifest

Exact ordered keys: `schema_version,kind,repository,source_sha,source_tree,workflow_run_id,workflow_run_attempt,build_job_id,build_job_name,build_invocation_count,candidate_digest,wheel,sdist,files_order`. Kind/name/counts are fixed; wheel/sdist child keys are `filename,size_bytes,sha256`.

### I392-D-017 — Receipt

Exact keys: `schema_version,kind,role,repository,source_sha,source_tree,workflow_run_id,workflow_run_attempt,job_id,job_name,needs,status,build_invocation_count,candidate_artifact,candidate_manifest,wheel,sdist,evidence,started_at,completed_at`. Role enum producer/linux-canonical/sdist-smoke/macos-delta. Needs and build count are graph-fixed. Child objects and filenames are exact.

### I392-D-018 — Role evidence

Common exact keys: `schema_version,kind,role,repository,source_sha,source_tree,workflow_run_id,workflow_run_attempt,job_id,job_name,status,started_at,completed_at,build_invocation_count,candidate_manifest_sha256,wheel_sha256,sdist_sha256,details`. Role-specific details and stable Linux metrics are exactly represented by EVIDENCE-FIXTURE-V1 and table-driven schema tests.

### I392-D-019 — Provider aggregate

Exact keys: `schema_version,kind,repository,source_sha,source_tree,workflow_run_id,workflow_run_attempt,status,candidate_artifact,receipt_artifacts,roles,file_manifest,aggregate`. It hashes each of eight subordinate actual byte files, binds four receipt artifacts, role jobs, candidate, build counts and Linux qualification. Provider-attestation reopens/revalidates all nine output files before upload.

## 9. Download verifier and external attestations

### I392-D-020 — `verify-downloaded-artifact`

Exact interface used by provider-attestation, compatibility provider-tests and S80:

```bash
uv run python scripts/provider_gate.py verify-downloaded-artifact   --repository chemitaro/spec-dock   --candidate-dir "$ISS392_WS_ARTIFACT_DOWNLOAD/candidate"   --evidence-dir "$ISS392_WS_ARTIFACT_DOWNLOAD/evidence"   --run-json "$ISS392_WS_WORKFLOW_API/run.json"   --jobs-json "$ISS392_WS_WORKFLOW_API/jobs.json"   --artifacts-json "$ISS392_WS_WORKFLOW_API/artifacts.json"   --source-sha "$SOURCE_SHA"   --source-tree "$SOURCE_TREE"   --workflow-run-id "$RUN_ID"   --json
```

It reads actual candidate/evidence/API bytes, validates exact names/counts/schemas/source/run/job/needs/artifact identities, sizes/hashes/build counts/metrics and independent byte links. Success JSON keys `schema_version,status,code,repository,workflow_run_id,source_sha,source_tree,candidate_artifact,evidence_artifact,receipt_roles,evidence_files`; code `downloaded-artifact-verified`. Failure exits 2–12 retain the previously accepted exact typed mapping; no generic code.

### I392-D-021 — Attestation payload schemas

Pre-merge exact ordered keys:

```text
schema_version,kind,repository,issue_number,pull_request_number,
spec_freeze_commit,implementation_base_sha,
compatibility_head_sha,compatibility_head_tree,compatibility_workflow_run_id,
final_head_sha,final_head_tree,final_workflow_run_id,
compatibility_to_final_paths,tracked_report_blob_sha1,
candidate_artifact,evidence_artifact,provider_evidence_sha256,
environment_fingerprint_sha256,required_contexts_before,
required_contexts_both,canary_pull_request_number,canary_block_verified,
required_contexts_after_old_removed,required_contexts_final_head,
human_review_state,generated_at
```

Actual compatibility/final identities are distinct and external. Payload contains no future comment ID.

Post-merge exact keys:

```text
schema_version,kind,repository,issue_number,pre_merge_comment_id,
pre_merge_payload_sha256,final_head_sha,final_head_tree,merge_commit_sha,
merge_commit_tree,tree_equal,merge_actor,merged_at,spec_dock_finish_status,
spec_dock_finish_observed_at,github_issue_closed_event_id,
github_issue_closed_at,generated_at
```

This payload is constructed only after finish and #392 close event are measured. It contains no own future comment ID.

Epic exact keys:

```text
schema_version,kind,repository,epic_issue_number,implementation_issue_number,
post_merge_comment_id,post_merge_payload_sha256,
implementation_issue_closed_event_id,implementation_issue_closed_at,
epic_acceptance_status,github_epic_closed_event_id,github_epic_closed_at,
generated_at
```

It is constructed only after #384 close event is measured.

### I392-D-022 — `emit-attestation`, posting and comment receipt

Exact pure-local interface:

```bash
uv run python scripts/provider_gate.py emit-attestation   --kind "$KIND"   --input-json "$ISS392_WS_ATTESTATION_DRAFT/input.json"   --output-json "$ISS392_WS_ATTESTATION_DRAFT/payload.json"   --output-comment "$ISS392_WS_ATTESTATION_DRAFT/comment.md"   --json
```

It validates exact schema/relation, O_EXCL/no-follow writes, fsyncs/rereads, and emits canonical payload and four-line comment envelope. Accepted kinds are pre-merge-attestation-v1, post-merge-closure-v1, epic-closure-v1. Existing typed exits 2–6 remain exact.

Posting: pre/post are new comments on #392; Epic is a new comment on #384. Human issues:write posts; issues:read verifies. Payload never contains its own comment identity.

After POST/readback, create external `comment-receipt-v1` with exact keys:

```text
schema_version,kind,attestation_kind,repository,target_issue_number,
comment_id,comment_url,author_login,created_at,updated_at,payload_sha256,
body_sha256,body_size_bytes,verified_at
```

Require exact target, actor, body/marker/payload hash, positive ID, nondeleted visibility and `created_at==updated_at`. Receipt is not embedded in payload or tracked tree.

### I392-D-023 — Closure execution

1. Pre-merge payload/comment/receipt on #392.
2. Human merge.
3. Fetch merge commit; compare final-head tree to merge tree.
4. Run `python3 ./spec-dock/scripts/spec-dock issue finish`; verify result.
5. Run `python3 ./spec-dock/scripts/spec-dock close --id iss-00392`; read #392 close event.
6. Build/post/read back post-merge payload/comment/receipt on #392.
7. Re-evaluate Epic acceptance.
8. Run `python3 ./spec-dock/scripts/spec-dock close --id epic-00384`; read #384 close event.
9. Build/post/read back Epic payload/comment/receipt on #384.

### I392-D-024 — Stable environment and context heads

Qualification uses `specdock-linux-qualification-v1` and exact fingerprint for all runs. Tracked report has neither compatibility nor final identity. `PRC_COMPAT_HEAD`/tree and `PRC_FINAL_HEAD`/tree are external and distinct. Context sequence is compatibility both-green -> new added/both required -> canary new-red/old-green/blocked -> compatibility both-green -> old removed -> final distinct head/new-only GREEN with all evidence rerun.

## 10. Canonical evidence and attestation fixtures

### I392-D-025 — `EVIDENCE-FIXTURE-V1`

Fixture identity constants are exact and distinct:

```text
spec_freeze_commit = 8888888888888888888888888888888888888888
implementation_base_sha = 9999999999999999999999999999999999999999
compatibility_head_sha/tree = aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa / bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb
final_head_sha/tree = cccccccccccccccccccccccccccccccccccccccc / dddddddddddddddddddddddddddddddddddddddd
merge_commit_sha = eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee
tracked_report_blob_sha1 = ffffffffffffffffffffffffffffffffffffffff
```

Every table hash is SHA-256 of the complete displayed compact UTF-8 bytes including final LF. Comment hashes cover the four-line envelope. The three comment receipts are generated only after their comment fixtures and are not included in attestation payloads.

| File | Size bytes | SHA-256 |
|---|---:|---|
| `candidate-manifest.json` | 757 | `b9b35fceeeb498afd125a7afdf46cf22bbb1da6890749f262cc71f60d6c6b42e` |
| `producer-build-evidence.json` | 937 | `9792877d94a0276cb7d8ebf44220e317cbdc99d58e42537b9f8682507ab53e82` |
| `linux-canonical-evidence.json` | 1894 | `3c109642984e5ca0310398bf45a77600ebd1a7bb7c3147f19fed5904ff7bbf7e` |
| `sdist-smoke-evidence.json` | 977 | `a19970d40b87690b7815c45d6e18d81d034fed545e28fce5219ad2bc2e6a5d86` |
| `macos-delta-evidence.json` | 1102 | `67a9e3e52b41e7adae4ce4911fd0d896a93db60dc0e6d47d96b1357c700f6039` |
| `provider-receipt-producer.json` | 1227 | `316a81dffeaba2a4c6189c71deb7cb357c2afe43bf875cf96abad677151e64ea` |
| `provider-receipt-linux-canonical.json` | 1262 | `216a01f2144ad784da3b49e67b4dbb8f5af0e4f80fd570df30ae1e7441674552` |
| `provider-receipt-sdist-smoke.json` | 1249 | `c8ffcbf098b9bd36043801a9350c0c73d13dddf81bb97ce2f57728a0d8206e0f` |
| `provider-receipt-macos-delta.json` | 1250 | `151d0e8ec6185cd4a44ce4fc3938f0e664e0fe2004e539fd7f60218077cecec3` |
| `provider-evidence.json` | 4421 | `c286d143438ffcaf5c4877c809cba372f947495663507c8ab3f171edf11e00ab` |
| `pre-merge-attestation-v1.json` | 1706 | `a1f8cd2d0d5dcc21ddc83021c89d6bb754b57eafd8df846bdb9625e54f5f2ad4` |
| `post-merge-closure-v1.json` | 766 | `fd5f0731da069f2db9612006116c93cec674860cff618c8a8290fa26faf40a30` |
| `epic-closure-v1.json` | 519 | `d5fd9ce5208a5829f35abce7e073909351c2a23be97c2d3447aa5d5fc7696f88` |
| `comment-receipt-pre-merge.json` | 584 | `0b0c3303ce1fafeac7b5e9b80f8f766edc0e374288e5df3e9aebefcc0d501174` |
| `comment-receipt-post-merge.json` | 580 | `ad61bc75102377f21e327b4155e2bc7c07df64c6caf847cebca341dcf24c1a7b` |
| `comment-receipt-epic.json` | 574 | `22d9ddd17fab4961eb4ee8761aaa28fbbb988144c8777adb5c1bd0ba8631b6f0` |
| `pre-merge-attestation-v1.comment.md` | 1839 | `30d7421e38be3ef2f394d459e1ae9e3f540b705c29ba056692a3b12457651dc9` |
| `post-merge-closure-v1.comment.md` | 896 | `ce1568399ba026f8001c988c49e2cb01b1184bc4879f9d3ae3f39825d292b640` |
| `epic-closure-v1.comment.md` | 643 | `d7b251faeec80e0c06b47074abb80c6d6b4450aa7d3f7394753f6b6fb27b59c8` |

#### `candidate-manifest.json`

```json
{"schema_version":1,"kind":"provider-candidate-manifest","repository":"chemitaro/spec-dock","source_sha":"cccccccccccccccccccccccccccccccccccccccc","source_tree":"dddddddddddddddddddddddddddddddddddddddd","workflow_run_id":1101,"workflow_run_attempt":1,"build_job_id":2101,"build_job_name":"provider-build-artifacts","build_invocation_count":1,"candidate_digest":"1111111111111111111111111111111111111111111111111111111111111111","wheel":{"filename":"spec_dock-0.2.4-py3-none-any.whl","size_bytes":123456,"sha256":"2222222222222222222222222222222222222222222222222222222222222222"},"sdist":{"filename":"spec_dock-0.2.4.tar.gz","size_bytes":234567,"sha256":"3333333333333333333333333333333333333333333333333333333333333333"},"files_order":["wheel","sdist"]}
```

#### `producer-build-evidence.json`

```json
{"schema_version":1,"kind":"provider-role-evidence","role":"producer","repository":"chemitaro/spec-dock","source_sha":"cccccccccccccccccccccccccccccccccccccccc","source_tree":"dddddddddddddddddddddddddddddddddddddddd","workflow_run_id":1101,"workflow_run_attempt":1,"job_id":2101,"job_name":"provider-build-artifacts","status":"passed","started_at":"2026-09-02T00:00:00Z","completed_at":"2026-09-02T00:10:00Z","build_invocation_count":1,"candidate_manifest_sha256":"b9b35fceeeb498afd125a7afdf46cf22bbb1da6890749f262cc71f60d6c6b42e","wheel_sha256":"2222222222222222222222222222222222222222222222222222222222222222","sdist_sha256":"3333333333333333333333333333333333333333333333333333333333333333","details":{"packaging_argv":["uv","build","--sdist","--wheel","--out-dir","/runner/_temp/spec-dock-build"],"packaging_exit_code":0,"output_file_count":2,"candidate_digest":"1111111111111111111111111111111111111111111111111111111111111111"}}
```

#### `linux-canonical-evidence.json`

```json
{"schema_version":1,"kind":"provider-role-evidence","role":"linux-canonical","repository":"chemitaro/spec-dock","source_sha":"cccccccccccccccccccccccccccccccccccccccc","source_tree":"dddddddddddddddddddddddddddddddddddddddd","workflow_run_id":1101,"workflow_run_attempt":1,"job_id":2102,"job_name":"provider-linux-canonical","status":"passed","started_at":"2026-09-02T00:00:00Z","completed_at":"2026-09-02T00:10:00Z","build_invocation_count":0,"candidate_manifest_sha256":"b9b35fceeeb498afd125a7afdf46cf22bbb1da6890749f262cc71f60d6c6b42e","wheel_sha256":"2222222222222222222222222222222222222222222222222222222222222222","sdist_sha256":"3333333333333333333333333333333333333333333333333333333333333333","details":{"environment_id":"specdock-linux-qualification-v1","environment_descriptor_sha256":"4444444444444444444444444444444444444444444444444444444444444444","environment_fingerprint_sha256":"5555555555555555555555555555555555555555555555555555555555555555","runner_image":"ubuntu-24.04","container_image_id":"sha256:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb","kernel_release":"6.8.0","cgroup_cpu_quota":2.0,"cgroup_memory_limit_bytes":8589934592,"python_version":"3.11.9","uv_version":"0.8.14","lock_sha256":"6666666666666666666666666666666666666666666666666666666666666666","pytest_process_count":1,"worker_count":1,"run_count":20,"budget_run_count":5,"wall_seconds":[1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0],"process_tree_cpu_seconds":[0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5],"cpu_wall_ratios":[0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5],"unexpected_failure_count":0,"flake_count":0,"retry_count":0,"seeded_fault_total":27,"seeded_fault_detected":27,"node_inventory_sha256":"7777777777777777777777777777777777777777777777777777777777777777"}}
```

#### `sdist-smoke-evidence.json`

```json
{"schema_version":1,"kind":"provider-role-evidence","role":"sdist-smoke","repository":"chemitaro/spec-dock","source_sha":"cccccccccccccccccccccccccccccccccccccccc","source_tree":"dddddddddddddddddddddddddddddddddddddddd","workflow_run_id":1101,"workflow_run_attempt":1,"job_id":2103,"job_name":"provider-sdist-smoke","status":"passed","started_at":"2026-09-02T00:00:00Z","completed_at":"2026-09-02T00:10:00Z","build_invocation_count":0,"candidate_manifest_sha256":"b9b35fceeeb498afd125a7afdf46cf22bbb1da6890749f262cc71f60d6c6b42e","wheel_sha256":"2222222222222222222222222222222222222222222222222222222222222222","sdist_sha256":"3333333333333333333333333333333333333333333333333333333333333333","details":{"installed_from_filename":"spec_dock-0.2.4.tar.gz","metadata_name":"spec-dock","metadata_version":"0.2.4","package_data_sha256":"8888888888888888888888888888888888888888888888888888888888888888","smoke_argv":["python","-m","spec_dock.cli","--help"],"smoke_exit_code":0}}
```

#### `macos-delta-evidence.json`

```json
{"schema_version":1,"kind":"provider-role-evidence","role":"macos-delta","repository":"chemitaro/spec-dock","source_sha":"cccccccccccccccccccccccccccccccccccccccc","source_tree":"dddddddddddddddddddddddddddddddddddddddd","workflow_run_id":1101,"workflow_run_attempt":1,"job_id":2104,"job_name":"provider-macos-delta","status":"passed","started_at":"2026-09-02T00:00:00Z","completed_at":"2026-09-02T00:10:00Z","build_invocation_count":0,"candidate_manifest_sha256":"b9b35fceeeb498afd125a7afdf46cf22bbb1da6890749f262cc71f60d6c6b42e","wheel_sha256":"2222222222222222222222222222222222222222222222222222222222222222","sdist_sha256":"3333333333333333333333333333333333333333333333333333333333333333","details":{"runner_image":"macos-15","macos_version":"15.0","architecture":"arm64","python_version":"3.11.9","pytest_process_count":1,"node_inventory_sha256":"9999999999999999999999999999999999999999999999999999999999999999","native_positive_control_total":2,"native_positive_control_detected":2,"platform_check_ids":["executable-mode","installed-entry-point","no-follow","renameatx-np"],"failed_count":0}}
```

#### `provider-receipt-producer.json`

```json
{"schema_version":1,"kind":"provider-job-receipt","role":"producer","repository":"chemitaro/spec-dock","source_sha":"cccccccccccccccccccccccccccccccccccccccc","source_tree":"dddddddddddddddddddddddddddddddddddddddd","workflow_run_id":1101,"workflow_run_attempt":1,"job_id":2101,"job_name":"provider-build-artifacts","needs":[],"status":"passed","build_invocation_count":1,"candidate_artifact":{"id":3100,"name":"provider-candidate-cccccccccccccccccccccccccccccccccccccccc","digest":"sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"},"candidate_manifest":{"filename":"candidate-manifest.json","size_bytes":757,"sha256":"b9b35fceeeb498afd125a7afdf46cf22bbb1da6890749f262cc71f60d6c6b42e"},"wheel":{"filename":"spec_dock-0.2.4-py3-none-any.whl","size_bytes":123456,"sha256":"2222222222222222222222222222222222222222222222222222222222222222"},"sdist":{"filename":"spec_dock-0.2.4.tar.gz","size_bytes":234567,"sha256":"3333333333333333333333333333333333333333333333333333333333333333"},"evidence":{"filename":"producer-build-evidence.json","size_bytes":937,"sha256":"9792877d94a0276cb7d8ebf44220e317cbdc99d58e42537b9f8682507ab53e82"},"started_at":"2026-09-02T00:00:00Z","completed_at":"2026-09-02T00:10:00Z"}
```

#### `provider-receipt-linux-canonical.json`

```json
{"schema_version":1,"kind":"provider-job-receipt","role":"linux-canonical","repository":"chemitaro/spec-dock","source_sha":"cccccccccccccccccccccccccccccccccccccccc","source_tree":"dddddddddddddddddddddddddddddddddddddddd","workflow_run_id":1101,"workflow_run_attempt":1,"job_id":2102,"job_name":"provider-linux-canonical","needs":["provider-build-artifacts"],"status":"passed","build_invocation_count":0,"candidate_artifact":{"id":3100,"name":"provider-candidate-cccccccccccccccccccccccccccccccccccccccc","digest":"sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"},"candidate_manifest":{"filename":"candidate-manifest.json","size_bytes":757,"sha256":"b9b35fceeeb498afd125a7afdf46cf22bbb1da6890749f262cc71f60d6c6b42e"},"wheel":{"filename":"spec_dock-0.2.4-py3-none-any.whl","size_bytes":123456,"sha256":"2222222222222222222222222222222222222222222222222222222222222222"},"sdist":{"filename":"spec_dock-0.2.4.tar.gz","size_bytes":234567,"sha256":"3333333333333333333333333333333333333333333333333333333333333333"},"evidence":{"filename":"linux-canonical-evidence.json","size_bytes":1894,"sha256":"3c109642984e5ca0310398bf45a77600ebd1a7bb7c3147f19fed5904ff7bbf7e"},"started_at":"2026-09-02T00:00:00Z","completed_at":"2026-09-02T00:10:00Z"}
```

#### `provider-receipt-sdist-smoke.json`

```json
{"schema_version":1,"kind":"provider-job-receipt","role":"sdist-smoke","repository":"chemitaro/spec-dock","source_sha":"cccccccccccccccccccccccccccccccccccccccc","source_tree":"dddddddddddddddddddddddddddddddddddddddd","workflow_run_id":1101,"workflow_run_attempt":1,"job_id":2103,"job_name":"provider-sdist-smoke","needs":["provider-build-artifacts"],"status":"passed","build_invocation_count":0,"candidate_artifact":{"id":3100,"name":"provider-candidate-cccccccccccccccccccccccccccccccccccccccc","digest":"sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"},"candidate_manifest":{"filename":"candidate-manifest.json","size_bytes":757,"sha256":"b9b35fceeeb498afd125a7afdf46cf22bbb1da6890749f262cc71f60d6c6b42e"},"wheel":{"filename":"spec_dock-0.2.4-py3-none-any.whl","size_bytes":123456,"sha256":"2222222222222222222222222222222222222222222222222222222222222222"},"sdist":{"filename":"spec_dock-0.2.4.tar.gz","size_bytes":234567,"sha256":"3333333333333333333333333333333333333333333333333333333333333333"},"evidence":{"filename":"sdist-smoke-evidence.json","size_bytes":977,"sha256":"a19970d40b87690b7815c45d6e18d81d034fed545e28fce5219ad2bc2e6a5d86"},"started_at":"2026-09-02T00:00:00Z","completed_at":"2026-09-02T00:10:00Z"}
```

#### `provider-receipt-macos-delta.json`

```json
{"schema_version":1,"kind":"provider-job-receipt","role":"macos-delta","repository":"chemitaro/spec-dock","source_sha":"cccccccccccccccccccccccccccccccccccccccc","source_tree":"dddddddddddddddddddddddddddddddddddddddd","workflow_run_id":1101,"workflow_run_attempt":1,"job_id":2104,"job_name":"provider-macos-delta","needs":["provider-build-artifacts"],"status":"passed","build_invocation_count":0,"candidate_artifact":{"id":3100,"name":"provider-candidate-cccccccccccccccccccccccccccccccccccccccc","digest":"sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"},"candidate_manifest":{"filename":"candidate-manifest.json","size_bytes":757,"sha256":"b9b35fceeeb498afd125a7afdf46cf22bbb1da6890749f262cc71f60d6c6b42e"},"wheel":{"filename":"spec_dock-0.2.4-py3-none-any.whl","size_bytes":123456,"sha256":"2222222222222222222222222222222222222222222222222222222222222222"},"sdist":{"filename":"spec_dock-0.2.4.tar.gz","size_bytes":234567,"sha256":"3333333333333333333333333333333333333333333333333333333333333333"},"evidence":{"filename":"macos-delta-evidence.json","size_bytes":1102,"sha256":"67a9e3e52b41e7adae4ce4911fd0d896a93db60dc0e6d47d96b1357c700f6039"},"started_at":"2026-09-02T00:00:00Z","completed_at":"2026-09-02T00:10:00Z"}
```

#### `provider-evidence.json`

```json
{"schema_version":1,"kind":"provider-evidence","repository":"chemitaro/spec-dock","source_sha":"cccccccccccccccccccccccccccccccccccccccc","source_tree":"dddddddddddddddddddddddddddddddddddddddd","workflow_run_id":1101,"workflow_run_attempt":1,"status":"passed","candidate_artifact":{"id":3100,"name":"provider-candidate-cccccccccccccccccccccccccccccccccccccccc","digest":"sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","manifest_sha256":"b9b35fceeeb498afd125a7afdf46cf22bbb1da6890749f262cc71f60d6c6b42e","wheel_sha256":"2222222222222222222222222222222222222222222222222222222222222222","sdist_sha256":"3333333333333333333333333333333333333333333333333333333333333333"},"receipt_artifacts":[{"role":"producer","id":3101,"name":"provider-receipt-producer-cccccccccccccccccccccccccccccccccccccccc","digest":"sha256:cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"},{"role":"linux-canonical","id":3102,"name":"provider-receipt-linux-canonical-cccccccccccccccccccccccccccccccccccccccc","digest":"sha256:dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd"},{"role":"sdist-smoke","id":3103,"name":"provider-receipt-sdist-smoke-cccccccccccccccccccccccccccccccccccccccc","digest":"sha256:eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"},{"role":"macos-delta","id":3104,"name":"provider-receipt-macos-delta-cccccccccccccccccccccccccccccccccccccccc","digest":"sha256:ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff"}],"roles":[{"role":"producer","job_id":2101,"job_name":"provider-build-artifacts","receipt_filename":"provider-receipt-producer.json","receipt_sha256":"316a81dffeaba2a4c6189c71deb7cb357c2afe43bf875cf96abad677151e64ea","evidence_filename":"producer-build-evidence.json","evidence_sha256":"9792877d94a0276cb7d8ebf44220e317cbdc99d58e42537b9f8682507ab53e82"},{"role":"linux-canonical","job_id":2102,"job_name":"provider-linux-canonical","receipt_filename":"provider-receipt-linux-canonical.json","receipt_sha256":"216a01f2144ad784da3b49e67b4dbb8f5af0e4f80fd570df30ae1e7441674552","evidence_filename":"linux-canonical-evidence.json","evidence_sha256":"3c109642984e5ca0310398bf45a77600ebd1a7bb7c3147f19fed5904ff7bbf7e"},{"role":"sdist-smoke","job_id":2103,"job_name":"provider-sdist-smoke","receipt_filename":"provider-receipt-sdist-smoke.json","receipt_sha256":"c8ffcbf098b9bd36043801a9350c0c73d13dddf81bb97ce2f57728a0d8206e0f","evidence_filename":"sdist-smoke-evidence.json","evidence_sha256":"a19970d40b87690b7815c45d6e18d81d034fed545e28fce5219ad2bc2e6a5d86"},{"role":"macos-delta","job_id":2104,"job_name":"provider-macos-delta","receipt_filename":"provider-receipt-macos-delta.json","receipt_sha256":"151d0e8ec6185cd4a44ce4fc3938f0e664e0fe2004e539fd7f60218077cecec3","evidence_filename":"macos-delta-evidence.json","evidence_sha256":"67a9e3e52b41e7adae4ce4911fd0d896a93db60dc0e6d47d96b1357c700f6039"}],"file_manifest":[{"filename":"provider-receipt-producer.json","size_bytes":1227,"sha256":"316a81dffeaba2a4c6189c71deb7cb357c2afe43bf875cf96abad677151e64ea"},{"filename":"producer-build-evidence.json","size_bytes":937,"sha256":"9792877d94a0276cb7d8ebf44220e317cbdc99d58e42537b9f8682507ab53e82"},{"filename":"provider-receipt-linux-canonical.json","size_bytes":1262,"sha256":"216a01f2144ad784da3b49e67b4dbb8f5af0e4f80fd570df30ae1e7441674552"},{"filename":"linux-canonical-evidence.json","size_bytes":1894,"sha256":"3c109642984e5ca0310398bf45a77600ebd1a7bb7c3147f19fed5904ff7bbf7e"},{"filename":"provider-receipt-sdist-smoke.json","size_bytes":1249,"sha256":"c8ffcbf098b9bd36043801a9350c0c73d13dddf81bb97ce2f57728a0d8206e0f"},{"filename":"sdist-smoke-evidence.json","size_bytes":977,"sha256":"a19970d40b87690b7815c45d6e18d81d034fed545e28fce5219ad2bc2e6a5d86"},{"filename":"provider-receipt-macos-delta.json","size_bytes":1250,"sha256":"151d0e8ec6185cd4a44ce4fc3938f0e664e0fe2004e539fd7f60218077cecec3"},{"filename":"macos-delta-evidence.json","size_bytes":1102,"sha256":"67a9e3e52b41e7adae4ce4911fd0d896a93db60dc0e6d47d96b1357c700f6039"}],"aggregate":{"producer_build_invocation_count":1,"consumer_build_invocation_count":0,"role_count":4,"file_count":9,"environment_id":"specdock-linux-qualification-v1","environment_fingerprint_sha256":"5555555555555555555555555555555555555555555555555555555555555555","qualification_run_count":20,"budget_run_count":5,"seeded_fault_total":27,"seeded_fault_detected":27,"status":"passed"}}
```

#### `pre-merge-attestation-v1.json`

```json
{"schema_version":1,"kind":"pre-merge-attestation-v1","repository":"chemitaro/spec-dock","issue_number":392,"pull_request_number":500,"spec_freeze_commit":"8888888888888888888888888888888888888888","implementation_base_sha":"9999999999999999999999999999999999999999","compatibility_head_sha":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","compatibility_head_tree":"bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb","compatibility_workflow_run_id":1001,"final_head_sha":"cccccccccccccccccccccccccccccccccccccccc","final_head_tree":"dddddddddddddddddddddddddddddddddddddddd","final_workflow_run_id":1101,"compatibility_to_final_paths":[".github/workflows/provider-ci.yml"],"tracked_report_blob_sha1":"ffffffffffffffffffffffffffffffffffffffff","candidate_artifact":{"id":3100,"name":"provider-candidate-cccccccccccccccccccccccccccccccccccccccc","digest":"sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"},"evidence_artifact":{"id":3110,"name":"provider-evidence-cccccccccccccccccccccccccccccccccccccccc","digest":"sha256:0000000000000000000000000000000000000000000000000000000000000000"},"provider_evidence_sha256":"c286d143438ffcaf5c4877c809cba372f947495663507c8ab3f171edf11e00ab","environment_fingerprint_sha256":"5555555555555555555555555555555555555555555555555555555555555555","required_contexts_before":["Provider CI / provider-tests"],"required_contexts_both":["Provider CI / provider-gate","Provider CI / provider-tests"],"canary_pull_request_number":501,"canary_block_verified":true,"required_contexts_after_old_removed":["Provider CI / provider-gate"],"required_contexts_final_head":["Provider CI / provider-gate"],"human_review_state":"approved","generated_at":"2026-09-02T01:00:00Z"}
```

#### `post-merge-closure-v1.json`

```json
{"schema_version":1,"kind":"post-merge-closure-v1","repository":"chemitaro/spec-dock","issue_number":392,"pre_merge_comment_id":6001,"pre_merge_payload_sha256":"a1f8cd2d0d5dcc21ddc83021c89d6bb754b57eafd8df846bdb9625e54f5f2ad4","final_head_sha":"cccccccccccccccccccccccccccccccccccccccc","final_head_tree":"dddddddddddddddddddddddddddddddddddddddd","merge_commit_sha":"eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee","merge_commit_tree":"dddddddddddddddddddddddddddddddddddddddd","tree_equal":true,"merge_actor":"chemitaro","merged_at":"2026-09-02T02:00:00Z","spec_dock_finish_status":"finished","spec_dock_finish_observed_at":"2026-09-02T02:05:00Z","github_issue_closed_event_id":7001,"github_issue_closed_at":"2026-09-02T02:10:00Z","generated_at":"2026-09-02T02:11:00Z"}
```

#### `epic-closure-v1.json`

```json
{"schema_version":1,"kind":"epic-closure-v1","repository":"chemitaro/spec-dock","epic_issue_number":384,"implementation_issue_number":392,"post_merge_comment_id":6002,"post_merge_payload_sha256":"fd5f0731da069f2db9612006116c93cec674860cff618c8a8290fa26faf40a30","implementation_issue_closed_event_id":7001,"implementation_issue_closed_at":"2026-09-02T02:10:00Z","epic_acceptance_status":"accepted","github_epic_closed_event_id":7002,"github_epic_closed_at":"2026-09-02T02:20:00Z","generated_at":"2026-09-02T02:21:00Z"}
```

#### `comment-receipt-pre-merge.json`

```json
{"schema_version":1,"kind":"comment-receipt-v1","attestation_kind":"pre-merge-attestation-v1","repository":"chemitaro/spec-dock","target_issue_number":392,"comment_id":6001,"comment_url":"https://api.github.com/repos/chemitaro/spec-dock/issues/comments/6001","author_login":"chemitaro","created_at":"2026-09-02T01:01:00Z","updated_at":"2026-09-02T01:01:00Z","payload_sha256":"a1f8cd2d0d5dcc21ddc83021c89d6bb754b57eafd8df846bdb9625e54f5f2ad4","body_sha256":"30d7421e38be3ef2f394d459e1ae9e3f540b705c29ba056692a3b12457651dc9","body_size_bytes":1839,"verified_at":"2026-09-02T01:01:00Z"}
```

#### `comment-receipt-post-merge.json`

```json
{"schema_version":1,"kind":"comment-receipt-v1","attestation_kind":"post-merge-closure-v1","repository":"chemitaro/spec-dock","target_issue_number":392,"comment_id":6002,"comment_url":"https://api.github.com/repos/chemitaro/spec-dock/issues/comments/6002","author_login":"chemitaro","created_at":"2026-09-02T02:12:00Z","updated_at":"2026-09-02T02:12:00Z","payload_sha256":"fd5f0731da069f2db9612006116c93cec674860cff618c8a8290fa26faf40a30","body_sha256":"ce1568399ba026f8001c988c49e2cb01b1184bc4879f9d3ae3f39825d292b640","body_size_bytes":896,"verified_at":"2026-09-02T02:12:00Z"}
```

#### `comment-receipt-epic.json`

```json
{"schema_version":1,"kind":"comment-receipt-v1","attestation_kind":"epic-closure-v1","repository":"chemitaro/spec-dock","target_issue_number":384,"comment_id":6003,"comment_url":"https://api.github.com/repos/chemitaro/spec-dock/issues/comments/6003","author_login":"chemitaro","created_at":"2026-09-02T02:22:00Z","updated_at":"2026-09-02T02:22:00Z","payload_sha256":"d5fd9ce5208a5829f35abce7e073909351c2a23be97c2d3447aa5d5fc7696f88","body_sha256":"d7b251faeec80e0c06b47074abb80c6d6b4450aa7d3f7394753f6b6fb27b59c8","body_size_bytes":643,"verified_at":"2026-09-02T02:22:00Z"}
```

Comment bodies use exactly marker line, opening `json` fence, compact payload without its LF, closing fence and one final LF. Tests regenerate every object and receipt, compare bytes/size/hash, parse every JSON and verify every parent-child/comment relation. They never rewrite fixture expectations.

## 11. Traceability

- D-001–006 implement RQ-008–017 including terminal cleanup.
- D-007–010 implement RQ-001–007 and #387 admission.
- D-011–014 implement RQ-018–024.
- D-015–025 implement RQ-023–031.
- S10–S80 implement the operational gates; `owner_decisions_required=[]`.
