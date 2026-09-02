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
  sha: "0fafbf3e02d2fcd5b622d6a997323e0f98eb1c78"
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

### I392-D-002 — Protocol order, deferred intent and cleanup

Publication order remains candidate validation, persistent stage allocation, safe container bind/bootstrap, incomplete record, four roots, two slots, policy-authorized seeds, verify, terminal record, stage cleanup. `ACTIVE.json` is process-independent and includes immutable old operation/candidate/policy/result-family plus nullable `deferred_invocation`.

Every parser-valid lifecycle invocation is normalized before locking. Before normal dispatch, `recover_terminal_cleanup()` classifies role by syntax: token absent means desired; the exact hidden `--provider-cleanup-token` matching ACTIVE means cleanup-retry. A desired command atomically becomes the first `deferred_invocation` even when its base form equals the old retry; a tokenized retry preserves any existing deferred request. Cleanup failure returns the tokenized retry plus optional desired-after-cleanup command. Cleanup success is cleanup-only and returns only the preserved desired command, or no next action. No invocation both cleans an old stage and starts another lifecycle mutation. Public continuation is exactly the wire artifact's four-field object.

### I392-D-003 — Wire integration

Tests parse the normative artifact and assert 38 codes, 142 rows, four record goldens, thirty-three public review goldens, phase/reason/order inventories and exact JSON/text bytes. A typed result selects exactly one row; zero/multiple match is a programming defect.

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

`NAMESPACE.json`, `REPOSITORY.json`, `ACTIVE.json` and `STAGE-OWNER.json` are canonical compact UTF-8 plus LF, mode 0600, regular/link-count-one. Directory modes are 0700 and current UID.

`ACTIVE.json` exact ordered keys are `schema_version,kind,state,repository_key,repository_realpath_sha256,repository_device,repository_inode,operation,candidate_digest,seed_policy,result_family,tuple_key,cleanup_token,stage_relative_path,deferred_invocation,created_at,updated_at`.

- schema `1`, kind `provider-lifecycle-active`, state `allocating|ready|terminal-cleanup`.
- `result_family=install|legacy-migration|update|uninstall`.
- `cleanup_token` is exact lowercase 64-hex computed by the wire-defined SHA-256 input and is immutable for the ACTIVE lifetime. It marks retry role but grants no filesystem authority.
- `deferred_invocation` is null or an exact object with ordered keys `invocation_id,rendered_command`. `invocation_id` is the wire enum `init|init-force|update|uninstall-dry-run|uninstall-dry-run-keep|uninstall-apply|uninstall-apply-keep`; `rendered_command` is its exact no-token wire rendering. The first desired request is immutable until ACTIVE removal.
- `cleanup_retry_invocation` is not stored; it is the exact pure function of result family, seed policy and cleanup token fixed by the wire artifact. The private option is suppressed from public help.
- Any unknown key/value, tuple/path disagreement, invalid timestamp, identity change or noncanonical bytes blocks without scan or deletion.

`STAGE-OWNER.json` binds the same repository/tuple/result family and exact registered entries plus nullable created-container identity. It never stores a public desired command.

### I392-D-006 — Allocation, lifecycle resume and terminal cleanup

1. ACTIVE absent: no-replace create allocation identity, then deterministic stage and owner. A prior unlink crash is closed by directory fsync before dispatch.
2. Allocating: recreate only exact absent stage or complete exact empty owned stage initialization.
3. Ready plus incomplete record: exact tuple resume only.
4. Ready plus terminal record: atomically transition ACTIVE to terminal-cleanup.
5. Normalize the seven-value public invocation ID and private role. A no-token invocation is desired and is atomically stored when deferred is null, including no-token update/init-force whose base form equals the old retry. An exact tokenized retry never creates or changes deferred. A later desired command is not queued and cannot replace the first deferred request. Invalid/unmatched token maps to exact wire `invalid-request` before cleanup mutation.
6. Validate registered stage entries and remove only them. Stage already absent is success. Remove content-bound ACTIVE and fsync parent.
7. Failure while ACTIVE remains returns wire `terminal-cleanup-failed`, cleanup retry as `continuation.next_command`, and the immutable deferred request as `continuation.after_cleanup_command` when non-null. No normal dispatch.
8. Success from present ACTIVE returns wire `terminal-cleanup-completed`. It returns the immutable deferred request as `continuation.next_command`, or `none/null`; no normal dispatch.
9. A caller follows only `continuation`. Thus old install/update cleanup can never cause the caller to re-run old mutation instead of a pending uninstall. A cleanup retry with no deferred request completes cleanup and returns no next action.
10. Mismatched identity/sentinel/registered entry fails closed; no global or sibling scan.

Tests cover desired-uninstall/old-install, no-token desired update/init-force versus tokenized retry with the same base form, retry with and without deferred request, third-command preservation, stage absent, ACTIVE unlink crash, repeated cleanup failure and exact public goldens.

## 4. Independent ephemeral workspaces and protected witness

### I392-D-007 — Private owner root, exact reserved trees and live-handle lifetime

`create_external_workspace(repository,purpose)` creates one private mode-0700 `mkdtemp` owner root and returns an in-process `ExternalWorkspaceHandle` holding parent/root descriptors, identities and exact sentinel bytes. The owner root path is never exported, put in an environment variable, or accepted by a child command. The owner immediately calls `reserve_tree(handle,reserved_name)` and exports only that reserved tree path.

Exact one-to-one mapping:

| Purpose | Exported variable | Reserved top-level name | Exact child layout |
|---|---|---|---|
| admission | `ISS392_WS_ADMISSION` | `admission` | `inputs/`, `results/` |
| baseline-build | `ISS392_WS_BASELINE_BUILD` | `dist` | wheel, sdist, baseline manifest directly in tree |
| protected-witness | `ISS392_WS_PROTECTED_WITNESS` | `witness` | `protected-manifest.json`, `authorized-exclusions.json` |
| full-regression-s00 | `ISS392_WS_FULL_REGRESSION_S00` | `full-regression` | verifier-created timestamp run directories |
| full-regression-s30 | `ISS392_WS_FULL_REGRESSION_S30` | `full-regression` | verifier-created timestamp run directories |
| full-regression-s60 | `ISS392_WS_FULL_REGRESSION_S60` | `full-regression` | verifier-created timestamp run directories |
| tripwire | `ISS392_WS_TRIPWIRE` | `tripwire` | `venvs/`, `workspaces/`, `events/` |
| fresh-consumer | `ISS392_WS_FRESH_CONSUMER` | `consumer` | `venv/`, `repository/`, `evidence/` |
| workflow-api | `ISS392_WS_WORKFLOW_API` | `api` | standalone `run.json`, `jobs.json`, `artifacts.json` observation only; never an aggregate-verifier input tree |
| artifact-download | `ISS392_WS_ARTIFACT_DOWNLOAD` | `artifacts` | standalone archive transport inspection only; never an aggregate-verifier input tree |
| attestation-draft | `ISS392_WS_ATTESTATION_DRAFT` | `attestation` | `input.json`, `payload.json`, `comment.md`, `receipt.json` |
| provider-build | `ISS392_WS_PROVIDER_BUILD` | `output` | `candidate/`, `receipt/` |
| provider-linux | `ISS392_WS_PROVIDER_LINUX` | `role` | `raw/`, `extracted/`, `api/`, `output/` |
| provider-sdist | `ISS392_WS_PROVIDER_SDIST` | `role` | `raw/`, `extracted/`, `api/`, `output/` |
| provider-macos | `ISS392_WS_PROVIDER_MACOS` | `role` | `raw/`, `extracted/`, `api/`, `output/` |
| provider-attestation | `ISS392_WS_PROVIDER_ATTESTATION` | `aggregate` | `api/{run,jobs,artifacts}.json`, `raw/<artifact>.zip`, initially empty `extracted/<artifact>/`, `output/{role-set-verification,provider-evidence}.json` |
| provider-verification | `ISS392_WS_PROVIDER_VERIFICATION` | `verification` | `api/{run,jobs,artifacts}.json`, `raw/<artifact>.zip`, initially empty `extracted/<artifact>/`, `output/verify-downloaded-artifact.json` |
| provider-node-ownership | `ISS392_WS_PROVIDER_NODE_OWNERSHIP` | `verification` | `collection.json`, `result.json` |
| provider-workflow-structure | `ISS392_WS_PROVIDER_WORKFLOW_STRUCTURE` | `verification` | `result.json` |

A `verify-downloaded-artifact` step uses exactly one live handle and one exported reserved tree: `provider-attestation` for role-set verification or `provider-verification` for compatibility/canary/S80 aggregate verification. Its API snapshots, authenticated raw ZIPs, empty extraction destinations and stdout file all reside under that one tree. Combining `ISS392_WS_WORKFLOW_API`, `ISS392_WS_ARTIFACT_DOWNLOAD` and `ISS392_WS_PROVIDER_VERIFICATION` in one verifier invocation is forbidden. No extraction occurs before the verifier starts; the owner creates and registers each destination as an exact empty directory, and the verifier alone performs safe extraction.

Every command receives an exported reserved tree, never owner root. Before spawn, the live owner calls `register_output()` for every fixed file or subtree capability listed by the purpose row. A child cannot register, widen or clean its own outputs. The registration object is non-serializable and contains the reserved-tree descriptor identity, relative path, expected kind and one closed policy ID.

Exact registration policy IDs are `fixed-file-v1`, `fixed-directory-v1`, `baseline-dist-v1`, `full-regression-output-v1`, `tripwire-output-v1`, `fresh-consumer-output-v1`, `actions-api-snapshot-v1`, `actions-artifact-archive-v1`, `actions-artifact-extraction-v1`, `provider-role-output-v1`, `provider-verification-output-v1`, `attestation-output-v1`. `full-regression-output-v1` permits only UTC run directories matching `[0-9]{8}T[0-9]{6}\.[0-9]{6}Z` and the verifier's closed file inventory; the other policies validate the exact child layouts in the table. No generic recursive-write registration exists.

The live owner creates the reserved directory before spawn, records device/inode in memory, pre-registers capabilities, starts the child with the reserved path plus inherited descriptor, and seals a no-follow inventory after exit. Any write outside a registered capability, any policy-invalid descendant, or any unknown top-level owner-root entry changes the state to `preserved-on-failure` and fails the step. Environment path, sentinel, nonce or PID cannot recreate registration or cleanup authority.

Exact APIs are `reserve_tree(handle,name)`, `register_output(handle,reserved_tree,relative_path,expected_kind,policy_id)`, `spawn_registered_child(handle,reserved_tree,registrations,argv,env,stdout_registration=None)`, `seal_tree(handle,reserved_tree,result)`, `begin_upload(handle,sealed_tree)`, `confirm_upload(handle,sealed_tree,artifact_id,name,digest)`, `cleanup_external_workspace(handle)`. Cleanup accepts the live handle only. In Actions, one background owner process with inherited FDs remains alive until every required upload is confirmed; upload failure or cancellation preserves the workspace and fails the job. Tests cover root exposure, env-to-root mismatch, cross-tree aggregate invocation, pre-extraction, nonempty destination, child attempted registration, unregistered entry, policy-invalid descendant, child escape, owner death, premature cleanup and after-upload success.

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

### I392-D-013 — Compatibility/final jobs and least-privilege permissions

Workflow-level default is exact YAML `permissions: {}`. Job declaration and `needs` order are normative.

Compatibility head graph:

```text
provider-build-artifacts: []
provider-linux-canonical: [provider-build-artifacts]
provider-sdist-smoke: [provider-build-artifacts]
provider-macos-delta: [provider-build-artifacts]
provider-attestation: [provider-build-artifacts,provider-linux-canonical,provider-sdist-smoke,provider-macos-delta]
provider-gate: [provider-attestation]
provider-tests: [provider-build-artifacts,provider-attestation]
```

Final head removes only `provider-tests`. Exact job permissions:

| Job | Exact override |
|---|---|
| `provider-build-artifacts` | `contents: read` |
| `provider-linux-canonical` | `actions: read`, `contents: read` |
| `provider-sdist-smoke` | `actions: read`, `contents: read` |
| `provider-macos-delta` | `actions: read`, `contents: read` |
| `provider-attestation` | `actions: read`, `contents: read` |
| `provider-gate` | `contents: read` |
| compatibility `provider-tests` | `actions: read`, `contents: read`, `pull-requests: read` |

No job has `issues:write`, `pull-requests:write`, `contents:write`, `actions:write`, `id-token:write`, `checks:write` or `security-events:write`. The canary uses the same workflow/job permissions; only `provider-gate` reads `.github/provider-gate-canary-red`. Append-only Issue comment POST is a separate human operation using `issues:write`; readback uses `issues:read`.

Compatibility `provider-tests` creates one `provider-verification` owner/step, stores API snapshots, raw candidate/evidence ZIPs, empty extraction destinations and verifier stdout under that single reserved tree, then calls the exact downloaded verifier. It invokes no package build and does not read the canary marker. It polls authenticated jobs API until `provider-gate` is terminal, selects `compatibility-aggregate-green` for success or `compatibility-aggregate-canary` for failure, and remains GREEN when actual-byte verification succeeds.

Exact job outputs are:

| Job | Exact outputs in declaration order |
|---|---|
| `provider-build-artifacts` | `candidate_artifact_id,candidate_artifact_digest,producer_receipt_artifact_id,producer_receipt_artifact_digest` |
| `provider-linux-canonical` | `receipt_artifact_id,receipt_artifact_digest` |
| `provider-sdist-smoke` | `receipt_artifact_id,receipt_artifact_digest` |
| `provider-macos-delta` | `receipt_artifact_id,receipt_artifact_digest` |
| `provider-attestation` | `evidence_artifact_id,evidence_artifact_digest` |
| `provider-gate` | none |
| compatibility `provider-tests` | none |

Each digest output is the bare lowercase 64-hex output of its one `actions/upload-artifact@v4` step. Each downstream job compares the output ID/name/digest with the authenticated REST artifact object and the complete raw ZIP bytes. An empty output, a duplicate artifact name, or a job output that names another run is a relation mismatch.

`verify-workflow-structure` parses the workflow as YAML and asserts top-level empty permissions, exact job set/order for `head_kind`, exact override maps, exact needs order, exact job output names/order, only one packaging command in producer package phase, zero packaging commands in producer finalize and every other job, exact artifact names, one-tree descriptor-bound raw-download/extraction/verifier invocation, provider-tests terminal-gate polling and phase selection, and complete provider-gate argv arrays. Missing, extra, inherited or write permission is `provider-gate-workflow-structure-mismatch`.

### I392-D-014 — Authenticated raw artifact download and safe extraction

For each selected artifact ID, the live workspace owner reserves the appropriate tree, opens the exact `raw/<artifact-name>.zip` descendant with descriptor-relative `O_WRONLY|O_CREAT|O_EXCL|O_NOFOLLOW`, mode 0600, and spawns the following exact argv with that already-open descriptor as child stdout:

```text
gh
api
--method
GET
-H
Accept: application/vnd.github+json
-H
X-GitHub-Api-Version: 2022-11-28
/repos/chemitaro/spec-dock/actions/artifacts/${ARTIFACT_ID}/zip
```

The child environment contains `GH_TOKEN=${{ github.token }}` and the inherited ordinary runner environment; the token is never placed in argv or output. There is no shell redirection and no child-selected output path. The owner fsyncs and rereads the raw file, seals its identity/size/hash, and keeps the raw archive until all verification plus required artifact upload/readback confirmation completes. HTTP/auth/redirect/short-write/nonzero exit, a missing content body, or any path/identity change stops the job and preserves the workspace.

The Actions upload output `artifact-digest` is exact bare lowercase 64-hex SHA-256. The REST artifact object `digest` is exact `sha256:` followed by the same lowercase 64 hex. Provider-gate hashes the complete authenticated ZIP response bytes and requires exact equality to the upload output when that job output is available and to the REST digest in every consumer. Missing, null, upper-case, another algorithm/prefix, or mismatch is `provider-gate-byte-mismatch`.

Safe extraction is performed only by provider-gate into the exact empty `extracted/<artifact-name>` descendant. It rejects invalid ZIP/CRC, encryption, duplicate normalized names, absolute names, backslashes, `.` or `..` components, NUL/non-UTF-8 names, symlink/special/device entries, unsupported compression, more than 1000 entries, any individual uncompressed file above 1073741824 bytes, total uncompressed bytes above 2147483648, existing destination content, or post-write identity/mode/hash mismatch. Only regular files and real directories are materialized descriptor-relatively without following links. Raw archive bytes and extracted file bytes are both mandatory verifier inputs.

## 8. Normative Provider Gate byte and CLI contract

### I392-D-015 — Authority, scalars and JSON

This section is the sole normative authority for `scripts/provider_gate.py`, raw Actions archive verification, role evidence, receipts, aggregate evidence and external attestations. JSON is UTF-8 compact with displayed key order, `ensure_ascii=False`, separators `(",",":")`, one final LF, no BOM/NUL/duplicate/extra keys. `GitOid` is 40 lowercase hex; `Sha256` 64 lowercase hex; `ActionsDigest` `sha256:` plus Sha256; IDs are integers 1..9007199254740991; run attempt 1..100; byte size 1..9223372036854775807; count 0..1000000; UTC timestamps `YYYY-MM-DDTHH:MM:SSZ`; duration milliseconds 0..3600000. Repository is exact `chemitaro/spec-dock`; role order is producer, linux-canonical, sdist-smoke, macos-delta.

### I392-D-016 — Digest, archive and phase-aware API relations

Every file SHA-256 covers complete actual bytes, including JSON LF. Actions artifact digest covers complete authenticated raw ZIP bytes and must match API prefixed and upload-output bare forms. Extracted file descriptors hash actual extracted bytes. Environment fingerprint hashes exact compact+LF ordered input. Provider aggregate hashes all eight subordinate actual files. Attestation payload and comment body hashes cover complete bytes. Declared hashes without bytes are invalid.

`RAW-ARCHIVE-DIGEST-V1` remains the independent transport oracle: exact 128 bytes, SHA-256 `f045719a6085e235f04e34bb12054b841ee0457dd4c424f7ecbd781c0f307368`, and the displayed hex bytes in D-026. Tests reconstruct exact bytes and require API digest `sha256:f045719a6085e235f04e34bb12054b841ee0457dd4c424f7ecbd781c0f307368` and upload output `f045719a6085e235f04e34bb12054b841ee0457dd4c424f7ecbd781c0f307368`.

`verify-downloaded-artifact --verification-phase` is the exact enum below. Scope and phase combinations outside this table are argument-invalid.

| Verification phase | Scope | Invocation location | Run `status/conclusion` | `provider-gate` | `provider-tests` | `evidence_artifact_name` |
|---|---|---|---|---|---|---|
| `role-set-compatibility` | `role-set` | in `provider-attestation` on compatibility head | `in_progress/null` | `queued/null` | `queued/null` | null |
| `role-set-final` | `role-set` | in `provider-attestation` on final head | `in_progress/null` | `queued/null` | absent | null |
| `compatibility-aggregate-green` | `aggregate` | in compatibility `provider-tests` after gate terminal polling | `in_progress/null` | `completed/success` | `in_progress/null` | exact `provider-evidence-${SOURCE_SHA}` |
| `compatibility-aggregate-canary` | `aggregate` | in canary `provider-tests` after gate terminal polling | `in_progress/null` | `completed/failure` | `in_progress/null` | exact `provider-evidence-${SOURCE_SHA}` |
| `compatibility-canary-post-run` | `aggregate` | external canary readback after run terminal | `completed/failure` | `completed/failure` | `completed/success` | exact `provider-evidence-${SOURCE_SHA}` |
| `post-run-final` | `aggregate` | S80 after final run terminal | `completed/success` | `completed/success` | absent | exact `provider-evidence-${SOURCE_SHA}` |

For both role-set phases, `provider-build-artifacts`, `provider-linux-canonical`, `provider-sdist-smoke` and `provider-macos-delta` are `completed/success`; `provider-attestation` is `in_progress/null`. For compatibility aggregate phases, those four roles and `provider-attestation` are `completed/success`. For `post-run-final`, every final-head job is `completed/success`. No `cancelled`, `skipped`, `neutral`, `timed_out` or missing required job is accepted.

Job-step relations are exact. A completed/success job has every step `completed/success`; a queued job has an empty steps array. For an in-workflow snapshot, the current job has prior steps `completed/success`, exact step `capture-provider-api-snapshots` as `in_progress/null`, and every later step—including `verify-downloaded-artifact`, assembly and upload where present—as `queued/null`. The snapshot is fsynced after the API response completes, then the capture step completes and the verifier starts. A completed/failure canary gate has prior steps `completed/success` and exactly the canary enforcement step `completed/failure`. IDs are unique and `run_id` equals the selected run.

The three API files are authenticated raw UTF-8 JSON responses and are hashed before parsing. Duplicate keys or invalid UTF-8 are rejected. Unrelated GitHub fields remain in the raw hash but have no authority. Common required fields are: run ID/attempt/head/repository/workflow/event; unique job IDs/names/timestamps/steps; and unique artifact IDs/names/sizes/digests/expiry/run/URLs. Status, conclusion, exact job set and evidence-artifact presence are selected only by the phase table above.

Artifact inventory is phase-closed. Role-set phases require candidate plus four receipt artifacts and forbid `provider-evidence-*`. Aggregate phases require candidate plus exact provider evidence; other artifacts may be present in the API response but are not accepted as repeated verifier options. `candidate_artifact_name` is always exact and non-null. `evidence_artifact_name` is JSON null only for role-set phases and exact non-null for aggregate phases.

The verifier success object contains `verification_phase` and `api_snapshots` in exact order `run,jobs,artifacts`. Each snapshot row has ordered keys `kind,filename,size_bytes,sha256` and hashes complete raw bytes.

### I392-D-017 — Candidate manifest, role evidence and receipt schemas

Candidate manifest exact ordered keys and types:

| Key | Type | Exact relation |
|---|---|---|
| `schema_version` | integer | exact `1` |
| `kind` | string | `provider-candidate-manifest` |
| `repository` | string | exact `chemitaro/spec-dock` |
| `source_sha`,`source_tree` | GitOid | checked-out workflow head/tree |
| `workflow_run_id` | PositiveId | current run |
| `workflow_run_attempt` | RunAttempt | current run attempt |
| `build_job_id` | PositiveId | API job ID named `provider-build-artifacts` |
| `build_job_name` | string | exact `provider-build-artifacts` |
| `build_invocation_count` | integer | exact `1` |
| `candidate_digest` | Sha256 | lifecycle candidate stream |
| `wheel` | object | exact keys `filename,size_bytes,sha256`; filename `spec_dock-0.2.4-py3-none-any.whl` |
| `sdist` | object | same keys; filename `spec_dock-0.2.4.tar.gz` |
| `files_order` | array[string] | exact `wheel`, then `sdist` |

The candidate artifact contains exactly `candidate-manifest.json`, the named wheel and named sdist. Producer invokes exactly one packaging argv `uv build --sdist --wheel --out-dir <reserved-tree>/candidate`; no other job invokes `uv build`, `python -m build`, `pip wheel` or another packaging command.

Every role evidence object has exact ordered keys `schema_version,kind,role,repository,source_sha,source_tree,workflow_run_id,workflow_run_attempt,job_id,job_name,status,started_at,completed_at,build_invocation_count,candidate_manifest_sha256,wheel_sha256,sdist_sha256,details`. Common types are integer/string/GitOid/PositiveId/UtcSecond/Count/Sha256 as named; `kind=provider-role-evidence`, `status=passed`, and source/run/file hashes equal candidate/API facts. Role/job/build count are exact:

| Role | Job | Build count | Exact ordered `details` keys and relations |
|---|---|---:|---|
| producer | `provider-build-artifacts` | 1 | `packaging_command_id,packaging_argv,packaging_exit_code,output_file_count,candidate_digest`; ID `uv-build-sdist-wheel-v1`, argv exact six strings, exit 0, count 2 |
| linux-canonical | `provider-linux-canonical` | 0 | `environment_id,environment_descriptor_sha256,environment_fingerprint_input,environment_fingerprint_sha256,pytest_process_count,worker_count,node_inventory_sha256,qualification_runs,budget_run_count,seeded_fault_total,seeded_fault_detected`; environment exact, process/worker 1, twenty ordered runs, first five budget, positive fault total equals detected |
| sdist-smoke | `provider-sdist-smoke` | 0 | `python_version,install_exit_code,metadata_smoke_exit_code,package_data_smoke_exit_code,installed_version`; exits 0, version `0.2.4` |
| macos-delta | `provider-macos-delta` | 0 | `runner_image,architecture,python_version,native_symbol,native_positive_control_events,nofollow_verified,executable_mode_verified,lifecycle_delta_exit_code`; architecture `x86_64|arm64`, symbol `renameatx_np`, event 1, booleans true, exit 0 |

Each Linux qualification run has exact ordered keys `index,wall_milliseconds,cpu_milliseconds,exit_code,retry_count,flake_count`; indices 1 through 20, positive wall, nonnegative CPU, all three result counts 0. Runs 1 through 5 require wall <=600000 and `cpu_milliseconds*1000 <= wall_milliseconds*1100`. All runs use one exact environment fingerprint.

Receipt exact ordered keys are `schema_version,kind,role,repository,source_sha,source_tree,workflow_run_id,workflow_run_attempt,job_id,job_name,needs,status,build_invocation_count,candidate_artifact,candidate_manifest,wheel,sdist,evidence,started_at,completed_at`.

- `kind=provider-job-receipt`, `status=passed`.
- `needs=[]` for producer; each role consumer has exact `needs=["provider-build-artifacts"]`.
- `candidate_artifact` exact keys are `id,name,digest`; name `provider-candidate-<source_sha>`, digest `ActionsDigest` over raw ZIP.
- Candidate manifest/wheel/sdist/evidence descriptors have exact keys `filename,size_bytes,sha256` and hash actual bytes.
- Evidence filenames are `producer-build-evidence.json`, `linux-canonical-evidence.json`, `sdist-smoke-evidence.json`, `macos-delta-evidence.json`.
- Receipt artifact name is `provider-receipt-<role>-<source_sha>` and contains exactly receipt plus role evidence.

### I392-D-018 — Provider aggregate and raw archive descriptors

`provider-evidence.json` exact ordered keys are `schema_version,kind,repository,source_sha,source_tree,workflow_run_id,workflow_run_attempt,status,candidate_artifact,receipt_artifacts,roles,file_manifest,aggregate`.

- `kind=provider-evidence`, `status=passed`.
- `receipt_artifacts` and `roles` are exact role order producer, linux-canonical, sdist-smoke, macos-delta.
- `file_manifest` has exactly eight rows in receipt/evidence pairs by role order. Each row exact keys are `filename,size_bytes,sha256` and hashes the actual child bytes.
- `aggregate` exact keys are `producer_build_invocation_count,consumer_build_invocation_count,role_count,file_count,environment_id,environment_fingerprint_sha256,qualification_run_count,budget_run_count,seeded_fault_total,seeded_fault_detected,status`; values are `1,0,4,9,specdock-linux-qualification-v1,<computed fingerprint>,20,5,<positive N>,<same N>,passed`.
- The uploaded evidence artifact contains exactly `provider-evidence.json` plus those eight child files.

Verifier success includes `api_snapshots` as defined in D-016 and `artifact_archives`, ordered objects with exact keys `role,artifact_id,artifact_name,api_digest,archive_filename,archive_size_bytes,archive_sha256,extracted_directory`. Role-set order is candidate, producer, linux-canonical, sdist-smoke, macos-delta. Aggregate order is candidate, provider-evidence. `api_digest` is prefixed; `archive_sha256` is bare and equal after removing prefix. Paths are absolute under the supplied reserved artifact tree but do not confer cleanup authority.

### I392-D-019 — Exact nine subcommands, argv and path types

Accepted parser order is exactly `build-candidate`, `run-linux-canonical`, `run-sdist-smoke`, `run-macos-delta`, `assemble-provider-evidence`, `verify-downloaded-artifact`, `verify-node-ownership`, `verify-workflow-structure`, `emit-attestation`.

All path flags are absolute, normalized and no-follow. Writable paths must be descendants of the exact `--workspace` reserved tree. Read-only repository paths are descendants of `$REPOSITORY_ROOT`. Repeated `--artifact-archive` and `--artifact-dir` options are order-sensitive, unique and mandatory. Every invocation ends `--json`; no flag has an implicit path default.

Exact producer package argv:

```bash
uv run python scripts/provider_gate.py build-candidate \
  --phase package \
  --repository chemitaro/spec-dock \
  --repository-root "$REPOSITORY_ROOT" \
  --source-sha "$SOURCE_SHA" \
  --source-tree "$SOURCE_TREE" \
  --workflow-run-id "$RUN_ID" \
  --workflow-run-attempt "$RUN_ATTEMPT" \
  --job-id "$JOB_ID" \
  --workspace "$ISS392_WS_PROVIDER_BUILD" \
  --json
```

This form invokes packaging exactly once and writes the candidate directory plus `receipt/producer-build-evidence.json`. After `actions/upload-artifact@v4` uploads `provider-candidate-$SOURCE_SHA`, the same subcommand is invoked in receipt-finalization mode; it never packages:

```bash
uv run python scripts/provider_gate.py build-candidate \
  --phase finalize-receipt \
  --repository chemitaro/spec-dock \
  --repository-root "$REPOSITORY_ROOT" \
  --source-sha "$SOURCE_SHA" \
  --source-tree "$SOURCE_TREE" \
  --workflow-run-id "$RUN_ID" \
  --workflow-run-attempt "$RUN_ATTEMPT" \
  --job-id "$JOB_ID" \
  --candidate-artifact-id "$CANDIDATE_ARTIFACT_ID" \
  --candidate-artifact-name "provider-candidate-$SOURCE_SHA" \
  --candidate-artifact-digest "$CANDIDATE_ARTIFACT_DIGEST" \
  --workspace "$ISS392_WS_PROVIDER_BUILD" \
  --json
```

`CANDIDATE_ARTIFACT_DIGEST` is the bare lowercase 64-hex `artifact-digest` output. Finalization rereads the packaged bytes/evidence, writes exactly `receipt/provider-receipt-producer.json`, and has build invocation count zero. The workflow then uploads the exact producer receipt tree as `provider-receipt-producer-$SOURCE_SHA`.

Exact Linux role argv:

```bash
uv run python scripts/provider_gate.py run-linux-canonical \
  --repository chemitaro/spec-dock \
  --repository-root "$REPOSITORY_ROOT" \
  --source-sha "$SOURCE_SHA" \
  --source-tree "$SOURCE_TREE" \
  --workflow-run-id "$RUN_ID" \
  --workflow-run-attempt "$RUN_ATTEMPT" \
  --job-id "$JOB_ID" \
  --candidate-archive "$ISS392_WS_PROVIDER_LINUX/raw/provider-candidate-$SOURCE_SHA.zip" \
  --candidate-dir "$ISS392_WS_PROVIDER_LINUX/extracted/provider-candidate-$SOURCE_SHA" \
  --run-json "$ISS392_WS_PROVIDER_LINUX/api/run.json" \
  --jobs-json "$ISS392_WS_PROVIDER_LINUX/api/jobs.json" \
  --artifacts-json "$ISS392_WS_PROVIDER_LINUX/api/artifacts.json" \
  --candidate-upload-digest "$CANDIDATE_ARTIFACT_DIGEST" \
  --environment-json "$REPOSITORY_ROOT/ci/linux-qualification-environment.json" \
  --workspace "$ISS392_WS_PROVIDER_LINUX" \
  --json
```

Exact sdist role argv:

```bash
uv run python scripts/provider_gate.py run-sdist-smoke \
  --repository chemitaro/spec-dock \
  --repository-root "$REPOSITORY_ROOT" \
  --source-sha "$SOURCE_SHA" \
  --source-tree "$SOURCE_TREE" \
  --workflow-run-id "$RUN_ID" \
  --workflow-run-attempt "$RUN_ATTEMPT" \
  --job-id "$JOB_ID" \
  --candidate-archive "$ISS392_WS_PROVIDER_SDIST/raw/provider-candidate-$SOURCE_SHA.zip" \
  --candidate-dir "$ISS392_WS_PROVIDER_SDIST/extracted/provider-candidate-$SOURCE_SHA" \
  --run-json "$ISS392_WS_PROVIDER_SDIST/api/run.json" \
  --jobs-json "$ISS392_WS_PROVIDER_SDIST/api/jobs.json" \
  --artifacts-json "$ISS392_WS_PROVIDER_SDIST/api/artifacts.json" \
  --candidate-upload-digest "$CANDIDATE_ARTIFACT_DIGEST" \
  --workspace "$ISS392_WS_PROVIDER_SDIST" \
  --json
```

Exact macOS role argv:

```bash
uv run python scripts/provider_gate.py run-macos-delta \
  --repository chemitaro/spec-dock \
  --repository-root "$REPOSITORY_ROOT" \
  --source-sha "$SOURCE_SHA" \
  --source-tree "$SOURCE_TREE" \
  --workflow-run-id "$RUN_ID" \
  --workflow-run-attempt "$RUN_ATTEMPT" \
  --job-id "$JOB_ID" \
  --candidate-archive "$ISS392_WS_PROVIDER_MACOS/raw/provider-candidate-$SOURCE_SHA.zip" \
  --candidate-dir "$ISS392_WS_PROVIDER_MACOS/extracted/provider-candidate-$SOURCE_SHA" \
  --run-json "$ISS392_WS_PROVIDER_MACOS/api/run.json" \
  --jobs-json "$ISS392_WS_PROVIDER_MACOS/api/jobs.json" \
  --artifacts-json "$ISS392_WS_PROVIDER_MACOS/api/artifacts.json" \
  --candidate-upload-digest "$CANDIDATE_ARTIFACT_DIGEST" \
  --workspace "$ISS392_WS_PROVIDER_MACOS" \
  --json
```

Exact role-set verifier argv used in `provider-attestation` before assembly:

```bash
uv run python scripts/provider_gate.py verify-downloaded-artifact \
  --scope role-set \
  --verification-phase "$ROLE_SET_VERIFICATION_PHASE" \
  --repository chemitaro/spec-dock \
  --repository-root "$REPOSITORY_ROOT" \
  --source-sha "$SOURCE_SHA" \
  --source-tree "$SOURCE_TREE" \
  --workflow-run-id "$RUN_ID" \
  --workflow-run-attempt "$RUN_ATTEMPT" \
  --run-json "$ISS392_WS_PROVIDER_ATTESTATION/api/run.json" \
  --jobs-json "$ISS392_WS_PROVIDER_ATTESTATION/api/jobs.json" \
  --artifacts-json "$ISS392_WS_PROVIDER_ATTESTATION/api/artifacts.json" \
  --expected-upload-digest "candidate=$CANDIDATE_ARTIFACT_DIGEST" \
  --expected-upload-digest "producer=$PRODUCER_RECEIPT_ARTIFACT_DIGEST" \
  --expected-upload-digest "linux-canonical=$LINUX_RECEIPT_ARTIFACT_DIGEST" \
  --expected-upload-digest "sdist-smoke=$SDIST_RECEIPT_ARTIFACT_DIGEST" \
  --expected-upload-digest "macos-delta=$MACOS_RECEIPT_ARTIFACT_DIGEST" \
  --artifact-archive "candidate=$ISS392_WS_PROVIDER_ATTESTATION/raw/provider-candidate-$SOURCE_SHA.zip" \
  --artifact-archive "producer=$ISS392_WS_PROVIDER_ATTESTATION/raw/provider-receipt-producer-$SOURCE_SHA.zip" \
  --artifact-archive "linux-canonical=$ISS392_WS_PROVIDER_ATTESTATION/raw/provider-receipt-linux-canonical-$SOURCE_SHA.zip" \
  --artifact-archive "sdist-smoke=$ISS392_WS_PROVIDER_ATTESTATION/raw/provider-receipt-sdist-smoke-$SOURCE_SHA.zip" \
  --artifact-archive "macos-delta=$ISS392_WS_PROVIDER_ATTESTATION/raw/provider-receipt-macos-delta-$SOURCE_SHA.zip" \
  --artifact-dir "candidate=$ISS392_WS_PROVIDER_ATTESTATION/extracted/provider-candidate-$SOURCE_SHA" \
  --artifact-dir "producer=$ISS392_WS_PROVIDER_ATTESTATION/extracted/provider-receipt-producer-$SOURCE_SHA" \
  --artifact-dir "linux-canonical=$ISS392_WS_PROVIDER_ATTESTATION/extracted/provider-receipt-linux-canonical-$SOURCE_SHA" \
  --artifact-dir "sdist-smoke=$ISS392_WS_PROVIDER_ATTESTATION/extracted/provider-receipt-sdist-smoke-$SOURCE_SHA" \
  --artifact-dir "macos-delta=$ISS392_WS_PROVIDER_ATTESTATION/extracted/provider-receipt-macos-delta-$SOURCE_SHA" \
  --workspace "$ISS392_WS_PROVIDER_ATTESTATION" \
  --json
```

The live owner binds stdout to the pre-reserved `output/role-set-verification.json` file. `ROLE_SET_VERIFICATION_PHASE` is exactly `role-set-compatibility` when `provider-tests` exists in the checked workflow and `role-set-final` otherwise; `verify-workflow-structure` proves that relation. Repeated `--expected-upload-digest`, `--artifact-archive`, and `--artifact-dir` options are each exact, unique, and ordered `candidate,producer,linux-canonical,sdist-smoke,macos-delta`. The five extraction destinations are owner-created, registered and empty before the verifier; no earlier extraction is permitted.

Exact role-set assembly argv:

```bash
uv run python scripts/provider_gate.py assemble-provider-evidence \
  --repository chemitaro/spec-dock \
  --repository-root "$REPOSITORY_ROOT" \
  --source-sha "$SOURCE_SHA" \
  --source-tree "$SOURCE_TREE" \
  --workflow-run-id "$RUN_ID" \
  --workflow-run-attempt "$RUN_ATTEMPT" \
  --run-json "$ISS392_WS_PROVIDER_ATTESTATION/api/run.json" \
  --jobs-json "$ISS392_WS_PROVIDER_ATTESTATION/api/jobs.json" \
  --artifacts-json "$ISS392_WS_PROVIDER_ATTESTATION/api/artifacts.json" \
  --verification-json "$ISS392_WS_PROVIDER_ATTESTATION/output/role-set-verification.json" \
  --artifact-archive "candidate=$ISS392_WS_PROVIDER_ATTESTATION/raw/provider-candidate-$SOURCE_SHA.zip" \
  --artifact-archive "producer=$ISS392_WS_PROVIDER_ATTESTATION/raw/provider-receipt-producer-$SOURCE_SHA.zip" \
  --artifact-archive "linux-canonical=$ISS392_WS_PROVIDER_ATTESTATION/raw/provider-receipt-linux-canonical-$SOURCE_SHA.zip" \
  --artifact-archive "sdist-smoke=$ISS392_WS_PROVIDER_ATTESTATION/raw/provider-receipt-sdist-smoke-$SOURCE_SHA.zip" \
  --artifact-archive "macos-delta=$ISS392_WS_PROVIDER_ATTESTATION/raw/provider-receipt-macos-delta-$SOURCE_SHA.zip" \
  --artifact-dir "candidate=$ISS392_WS_PROVIDER_ATTESTATION/extracted/provider-candidate-$SOURCE_SHA" \
  --artifact-dir "producer=$ISS392_WS_PROVIDER_ATTESTATION/extracted/provider-receipt-producer-$SOURCE_SHA" \
  --artifact-dir "linux-canonical=$ISS392_WS_PROVIDER_ATTESTATION/extracted/provider-receipt-linux-canonical-$SOURCE_SHA" \
  --artifact-dir "sdist-smoke=$ISS392_WS_PROVIDER_ATTESTATION/extracted/provider-receipt-sdist-smoke-$SOURCE_SHA" \
  --artifact-dir "macos-delta=$ISS392_WS_PROVIDER_ATTESTATION/extracted/provider-receipt-macos-delta-$SOURCE_SHA" \
  --workspace "$ISS392_WS_PROVIDER_ATTESTATION" \
  --json
```

Exact aggregate verifier argv used by compatibility, canary readback and S80:

```bash
uv run python scripts/provider_gate.py verify-downloaded-artifact \
  --scope aggregate \
  --verification-phase "$AGGREGATE_VERIFICATION_PHASE" \
  --repository chemitaro/spec-dock \
  --repository-root "$REPOSITORY_ROOT" \
  --source-sha "$SOURCE_SHA" \
  --source-tree "$SOURCE_TREE" \
  --workflow-run-id "$RUN_ID" \
  --workflow-run-attempt "$RUN_ATTEMPT" \
  --run-json "$ISS392_WS_PROVIDER_VERIFICATION/api/run.json" \
  --jobs-json "$ISS392_WS_PROVIDER_VERIFICATION/api/jobs.json" \
  --artifacts-json "$ISS392_WS_PROVIDER_VERIFICATION/api/artifacts.json" \
  --artifact-archive "candidate=$ISS392_WS_PROVIDER_VERIFICATION/raw/provider-candidate-$SOURCE_SHA.zip" \
  --artifact-archive "provider-evidence=$ISS392_WS_PROVIDER_VERIFICATION/raw/provider-evidence-$SOURCE_SHA.zip" \
  --artifact-dir "candidate=$ISS392_WS_PROVIDER_VERIFICATION/extracted/provider-candidate-$SOURCE_SHA" \
  --artifact-dir "provider-evidence=$ISS392_WS_PROVIDER_VERIFICATION/extracted/provider-evidence-$SOURCE_SHA" \
  --workspace "$ISS392_WS_PROVIDER_VERIFICATION" \
  --json
```

`AGGREGATE_VERIFICATION_PHASE` is exactly one of `compatibility-aggregate-green`, `compatibility-aggregate-canary`, `compatibility-canary-post-run`, or `post-run-final` at the locations fixed by D-016. One live `provider-verification` owner pre-registers API files, raw ZIPs, exact empty extraction directories and `output/verify-downloaded-artifact.json`, performs authenticated downloads, then spawns the verifier. The verifier performs extraction and writes its stdout to the registered output file. `ISS392_WS_WORKFLOW_API` and `ISS392_WS_ARTIFACT_DOWNLOAD` are never arguments to this invocation.

Exact ownership argv:

```bash
uv run python scripts/provider_gate.py verify-node-ownership \
  --repository-root "$REPOSITORY_ROOT" \
  --ownership-map "$REPOSITORY_ROOT/tests/provider_test_ownership.json" \
  --collection-json "$ISS392_WS_PROVIDER_NODE_OWNERSHIP/collection.json" \
  --workspace "$ISS392_WS_PROVIDER_NODE_OWNERSHIP" \
  --json
```

Exact workflow structure argv:

```bash
uv run python scripts/provider_gate.py verify-workflow-structure \
  --repository-root "$REPOSITORY_ROOT" \
  --workflow "$REPOSITORY_ROOT/.github/workflows/provider-ci.yml" \
  --head-kind "$HEAD_KIND" \
  --workspace "$ISS392_WS_PROVIDER_WORKFLOW_STRUCTURE" \
  --json
```

`HEAD_KIND` is exactly `compatibility` or `final` and is explicitly set by the caller.

Exact emitter argv:

```bash
uv run python scripts/provider_gate.py emit-attestation \
  --repository-root "$REPOSITORY_ROOT" \
  --kind "$ATTESTATION_KIND" \
  --input-json "$ISS392_WS_ATTESTATION_DRAFT/input.json" \
  --output-json "$ISS392_WS_ATTESTATION_DRAFT/payload.json" \
  --output-comment "$ISS392_WS_ATTESTATION_DRAFT/comment.md" \
  --workspace "$ISS392_WS_ATTESTATION_DRAFT" \
  --json
```

`ATTESTATION_KIND` is exactly `pre-merge-attestation-v1`, `post-merge-closure-v1` or `epic-closure-v1` and is explicitly set.

### I392-D-020 — Exact stdout, stderr and failure mapping

All flags displayed in D-019 are required for the displayed form, and no unlisted flag or positional argument is accepted. `build-candidate` accepts exactly the two `--phase` forms shown. `verify-downloaded-artifact` accepts exactly `--scope role-set` with a matching `role-set-*` verification phase and five ordered digest/archive/directory triples, or `--scope aggregate` with one matching aggregate verification phase and two ordered archive/directory pairs with no `--expected-upload-digest`. Scope/phase mismatch is arguments-invalid. `verify-workflow-structure --head-kind` accepts exactly `compatibility|final`. `emit-attestation --kind` accepts exactly the three displayed kinds.

Success writes one compact-plus-LF JSON object to stdout and nothing to stderr. Post-subcommand parse or typed execution failure writes one compact-plus-LF JSON object with exact ordered keys `schema_version,status,code,command,message,exit_code` to stdout and nothing to stderr. Before subcommand recognition, stdout is empty and stderr is exact `provider-gate: error (provider-gate-arguments-invalid): The provider-gate command arguments are invalid.` plus LF, exit 2.

| Exit | Code | Exact message | Exact commands that may emit it |
|---:|---|---|---|
| 2 | `provider-gate-arguments-invalid` | `The provider-gate command arguments are invalid.` | `build-candidate`, `run-linux-canonical`, `run-sdist-smoke`, `run-macos-delta`, `assemble-provider-evidence`, `verify-downloaded-artifact`, `verify-node-ownership`, `verify-workflow-structure`, `emit-attestation` |
| 3 | `provider-gate-input-missing` | `A required provider-gate input file is missing.` | `build-candidate`, `run-linux-canonical`, `run-sdist-smoke`, `run-macos-delta`, `assemble-provider-evidence`, `verify-downloaded-artifact`, `verify-node-ownership`, `verify-workflow-structure`, `emit-attestation` |
| 4 | `provider-gate-json-invalid` | `A provider-gate input is not valid canonical JSON.` | `build-candidate`, `run-linux-canonical`, `run-sdist-smoke`, `run-macos-delta`, `assemble-provider-evidence`, `verify-downloaded-artifact`, `verify-node-ownership`, `emit-attestation` |
| 5 | `provider-gate-schema-invalid` | `A provider-gate input does not match the exact schema.` | `build-candidate`, `run-linux-canonical`, `run-sdist-smoke`, `run-macos-delta`, `assemble-provider-evidence`, `verify-downloaded-artifact`, `verify-node-ownership`, `emit-attestation` |
| 6 | `provider-gate-identity-mismatch` | `Repository, source, tree, run, job, or artifact identity does not match.` | `build-candidate`, `run-linux-canonical`, `run-sdist-smoke`, `run-macos-delta`, `assemble-provider-evidence`, `verify-downloaded-artifact`, `emit-attestation` |
| 7 | `provider-gate-relation-mismatch` | `A provider-gate parent-child, timestamp, needs, permission, or context relation does not match.` | `run-linux-canonical`, `run-sdist-smoke`, `run-macos-delta`, `assemble-provider-evidence`, `verify-downloaded-artifact`, `verify-node-ownership`, `verify-workflow-structure`, `emit-attestation` |
| 8 | `provider-gate-byte-mismatch` | `A raw archive, extracted file, size, or SHA-256 does not match.` | `build-candidate`, `run-linux-canonical`, `run-sdist-smoke`, `run-macos-delta`, `assemble-provider-evidence`, `verify-downloaded-artifact`, `emit-attestation` |
| 9 | `provider-gate-inventory-mismatch` | `A required file, archive entry, role, receipt, job, node, or artifact is missing, duplicated, unsafe, or unexpected.` | `build-candidate`, `run-linux-canonical`, `run-sdist-smoke`, `run-macos-delta`, `assemble-provider-evidence`, `verify-downloaded-artifact`, `verify-node-ownership`, `verify-workflow-structure`, `emit-attestation` |
| 10 | `provider-gate-build-count-mismatch` | `The packaging count is not exactly one producer invocation and zero consumer invocations.` | `build-candidate`, `run-linux-canonical`, `run-sdist-smoke`, `run-macos-delta`, `assemble-provider-evidence`, `verify-downloaded-artifact` |
| 11 | `provider-gate-qualification-mismatch` | `The stable Linux qualification environment or acceptance metrics do not match.` | `run-linux-canonical`, `assemble-provider-evidence`, `verify-downloaded-artifact` |
| 12 | `provider-gate-workflow-structure-mismatch` | `The Provider CI jobs, needs, permissions, artifact names, raw downloads, verifier arguments, or packaging ownership do not match.` | `verify-workflow-structure` |
| 13 | `provider-gate-output-write-failed` | `Provider-gate output could not be created, fsynced, reread, sealed, and verified safely.` | `build-candidate`, `run-linux-canonical`, `run-sdist-smoke`, `run-macos-delta`, `assemble-provider-evidence`, `verify-downloaded-artifact`, `verify-node-ownership`, `verify-workflow-structure`, `emit-attestation` |
| 14 | `provider-gate-comment-contract-mismatch` | `The attestation payload or append-only comment contract does not match.` | `emit-attestation` |

No failure may be remapped. Unexpected Python exceptions are job defects and are not serialized as a generic result.

Success codes and exact ordered keys:

| Command form | Code | Ordered stdout keys |
|---|---|---|
| `build-candidate --phase package` | `candidate-built` | `schema_version,status,code,command,phase,repository,source_sha,source_tree,artifact_name,build_invocation_count,files` |
| `build-candidate --phase finalize-receipt` | `producer-receipt-finalized` | `schema_version,status,code,command,phase,repository,source_sha,source_tree,workflow_run_id,artifact_id,artifact_name,artifact_digest,receipt,evidence,build_invocation_count` |
| `run-linux-canonical` | `linux-canonical-passed` | `schema_version,status,code,command,repository,source_sha,source_tree,workflow_run_id,receipt,evidence,build_invocation_count` |
| `run-sdist-smoke` | `sdist-smoke-passed` | `schema_version,status,code,command,repository,source_sha,source_tree,workflow_run_id,receipt,evidence,build_invocation_count` |
| `run-macos-delta` | `macos-delta-passed` | `schema_version,status,code,command,repository,source_sha,source_tree,workflow_run_id,receipt,evidence,build_invocation_count` |
| `assemble-provider-evidence` | `provider-evidence-assembled` | `schema_version,status,code,command,repository,source_sha,source_tree,workflow_run_id,artifact_name,file_count,files` |
| `verify-downloaded-artifact --scope role-set` | `downloaded-artifact-verified` | `schema_version,status,code,command,scope,verification_phase,repository,workflow_run_id,source_sha,source_tree,candidate_artifact_name,evidence_artifact_name,api_snapshots,artifact_archives,receipt_roles,evidence_files` |
| `verify-downloaded-artifact --scope aggregate` | `downloaded-artifact-verified` | `schema_version,status,code,command,scope,verification_phase,repository,workflow_run_id,source_sha,source_tree,candidate_artifact_name,evidence_artifact_name,api_snapshots,artifact_archives,receipt_roles,evidence_files` |
| `verify-node-ownership` | `node-ownership-verified` | `schema_version,status,code,command,ownership_map_sha256,collected_node_count,owned_contract_count` |
| `verify-workflow-structure` | `workflow-structure-verified` | `schema_version,status,code,command,workflow_sha256,head_kind,job_count,jobs` |
| `emit-attestation` | `attestation-emitted` | `schema_version,status,code,command,kind,payload_path,payload_size_bytes,payload_sha256,comment_path,comment_size_bytes,comment_sha256` |

Success status is exact `completed`. File descriptors are exact ordered keys `filename,size_bytes,sha256`. `verification_phase` is mandatory for downloaded verification. `evidence_artifact_name` is null exactly for role-set phases and exact non-null for aggregate phases. Role build counts are zero. Producer package phase count is one and finalize phase count is zero. Assembly file count is nine. Workflow jobs are in declaration order. Extra or missing keys are `provider-gate-schema-invalid`.

### I392-D-021 — Single-owner actual-byte verifier and authenticated archive dataflow

The same verifier is used in provider-attestation (`scope=role-set`), compatibility provider-tests, external canary readback and S80 (`scope=aggregate`). Each invocation has exactly one live owner and one reserved tree. Before invocation, that owner creates API files and raw files no-follow/exclusive mode 0600, streams authenticated `gh api` responses to already-open descriptors, and creates each registered extraction destination as an exact empty directory. Raw ZIPs remain sealed until verification and any required upload/read confirmation.

For every raw archive the verifier, and no preceding step:

1. hashes complete raw bytes and compares API `sha256:<hex>` and any required upload output `<hex>`;
2. checks ZIP CRC and safe-extracts into its exact empty supplied directory;
3. rejects encrypted, duplicate, absolute, backslash, dot/dotdot, NUL/non-UTF-8, symlink, special, unsupported compression or size-limit entries;
4. hashes every extracted actual byte and verifies exact inventory;
5. validates the D-016 verification-phase run/job/artifact state, source/tree/run attempt/job IDs/names/needs/status/permissions;
6. validates candidate manifest, role evidence, receipts, provider aggregate, one producer/zero consumer builds and stable qualification;
7. emits the exact phase-aware success object to the registered stdout file.

Provider-attestation uses only `ISS392_WS_PROVIDER_ATTESTATION`. Compatibility/canary/S80 use only `ISS392_WS_PROVIDER_VERIFICATION`. Filename, stated hash, pre-extracted directory, separate API tree or API response alone is insufficient. Repeated option order is exact and duplicate options are arguments-invalid.

Compatibility `provider-tests` polls authenticated jobs API until provider-gate is terminal before it snapshots inputs. Gate success selects `compatibility-aggregate-green`; gate failure selects `compatibility-aggregate-canary`. The job never reads the canary file and its success depends only on actual-byte verification. After the canary run terminates, external readback runs `compatibility-canary-post-run` and proves run failure, gate failure and provider-tests success. S80 uses only `post-run-final`.

### I392-D-022 — Attestation payloads and observable post-sync recovery

Pre-merge and Epic payload key sets remain current. Post-merge payload exact ordered keys are:

`schema_version,kind,repository,issue_number,pre_merge_comment_id,pre_merge_payload_sha256,final_head_sha,final_head_tree,merge_commit_sha,merge_commit_tree,tree_equal,merge_actor,merged_at,issue_finish_command,max_finish_attempts,issue_finish_attempts,active_restore_attempts,accepted_issue_finish_attempt,github_issue_closed_event_id,github_issue_closed_at,generated_at`.

`max_finish_attempts` is exact 3. Each `issue_finish_attempts` row keys are `attempt,started_at,completed_at,exit_code,status,already_closed,active_cleared,post_sync_status`; status `finished|post-sync-failed`, post-sync `completed|failed`.

`active set` has no post-mutation sync contract and therefore restore rows contain no `post_sync_status`. Each restore row exact ordered keys are `before_attempt,command,started_at,completed_at,exit_code,stdout_sha256,stderr_sha256,readback_command,readback_started_at,readback_completed_at,readback_exit_code,readback_stdout_sha256,readback_stderr_sha256,active_issue_id_after`. The command is exact `python3 ./spec-dock/scripts/spec-dock active set --id iss-00392`; readback is exact `python3 ./spec-dock/scripts/spec-dock active show`.

For a successful restore, active-set exit is 0, stderr is empty SHA-256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`, and stdout bytes are exactly:

```text
spec-dock: ok (active set) target=iss-00392 initiative=init-local-00003 epic=epic-00384 issue=iss-00392
```

Their SHA-256 is `1967627d9f241b2dccef144b99af201ea0f196efe71941a59e1275d0f8bfc1cd`. Readback exit is 0, stderr is empty SHA-256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`, and stdout bytes are exactly:

```text
initiative: init-local-00003 (spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening)
epic: epic-00384 (spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00384-provider-test-strategy-simplification-and-execution-cost-reduction)
issue: iss-00392 (spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00384-provider-test-strategy-simplification-and-execution-cost-reduction/issues/iss-00392-provider-lifecycle-and-regression-gate-hard-cutover)
```

Their SHA-256 is `7b85ea56ea35d990a60006e46d08482aef029c0f3e5ace33955b0d5d1867004a` and parsed active issue is exact `iss-00392`. Raw stdout/stderr bytes are retained in the external attestation workspace and independently rehashed; hashes without bytes are invalid.

Closure algorithm:

1. Record attempt interval and run exact issue-finish command. The implementation closes #392 before clear/post-sync.
2. Exit 0 requires status finished, active cleared true and post-sync completed; this becomes `accepted_issue_finish_attempt`.
3. Exit 1 is recoverable only when measured result proves #392 closed, active cleared true and post-sync failed. Immediately read back the unique original close event. No post payload yet.
4. Before the next attempt, run exact active-set command, require its observable exit/stdout/stderr contract, run exact active-show readback and require its observable exit/stdout/stderr/active-ID contract. Do not infer or record active-set post-sync.
5. Rerun issue finish. Since #392 is already closed, require `already_closed=true`, no additional close event and active cleared true. If issue-finish post-sync fails, repeat restore+finish once more. After three failed finish attempts stop; no accepted payload.
6. The accepted payload records all attempt and restore observations and references the final successful finish interval. Earlier finish rows are post-sync-failed; attempts 2/3 have already-closed true. The original close event remains the only close evidence.
7. Ambiguous/multiple close events, reopen, active-set failure, active-show mismatch, stdout/stderr hash mismatch, third finish failure or fourth attempt is a hard stop. Never run `close --id iss-00392`.

### I392-D-023 — Attestation emitter and append-only comments

Exact emitter argv is D-019. Inputs contain only already measured facts. Output files are O_EXCL/no-follow 0600, fsynced/reread. Comment bytes are marker, JSON fence, payload without final LF, closing fence and one LF. Pre/post comments are new comments on #392; Epic comment on #384. Human POST uses issues:write; independent readback issues:read and verifies ID/URL/actor/body/hash/created=updated. Separate comment receipt is created after posting; no payload contains its own future comment identity.

### I392-D-024 — Workspace and workflow lifecycle

Local owner states are open, child-running, sealed, upload-pending, upload-confirmed, cleaned, preserved-on-failure. Actions background owner receives exact control messages but path/nonce alone confers no cleanup. It retains live descriptors through upload and confirms actual artifact ID/name/digest. For each verifier step, one owner controls API capture, raw download, empty extraction destinations, verifier stdout and any upload confirmation under one reserved tree. Raw archives are retained through aggregate/compatibility/canary/S80 verification and then cleaned only through the live handle. Every plan command uses the exact exported reserved-tree variable from D-007.

### I392-D-025 — Heads, environment and structural tests

S70 creates both compatibility and final tracked heads; final differs only by compatibility job removal. S80 is read-only. Qualification uses `specdock-linux-qualification-v1` and one exact fingerprint across 20 runs. Structural tests compare complete argv arrays, repeated option order, top-level/job permissions, needs, artifact names, one-tree authenticated raw download/extraction/verifier flow, phase-aware API/job-state tables, evidence-artifact nullability, provider-tests gate polling, one packager and zero consumer builds. Any drift blocks PR-C.

## 9. Canonical evidence and attestation fixtures

### I392-D-026 — `EVIDENCE-FIXTURE-V5`

This is a normative serializer oracle, not a runtime identity allowlist. JSON is exact compact UTF-8 plus LF. Synthetic compatibility/final identities remain distinct. The verifier stdout fixture is the exact `post-run-final` aggregate profile. The post fixture deliberately demonstrates first-attempt issue-finish post-sync failure, observable active-set/active-show restoration, and second-attempt already-closed finish. The table contains exactly twenty-six vectors. All sizes and hashes below are mechanically computed from the displayed bytes.

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
| `post-merge-closure-v1.json` | 2020 | `9ae45c0e264aeddf17d1c50b02a8966513c7ca902615a60435401b36aad31891` |
| `epic-closure-v1.json` | 519 | `3eaf09de7b9096566d2b7960cd6f7e920228661b1fc9a594701def15a7d5a05e` |
| `comment-receipt-pre-merge.json` | 584 | `aa100132e8a3d738c1a0959845a00d42cfd16a643ca19a936af1a063b969a1ae` |
| `comment-receipt-post-merge.json` | 581 | `c194bd57126b0f57c8bcc9cd3b4b8e055e2696dc834e0f63934789cbe4e5f1d1` |
| `comment-receipt-epic.json` | 574 | `eaadf4eefa92918d71bb775fec947ab59136ffa25668523fc6aa807342e4032c` |
| `run-api.json` | 292 | `178e538f002baafbdbba399a117f5031c7ff07e1ae691abec0b12e2cef0160b9` |
| `jobs-api.json` | 1702 | `753f6326ffa4b1d1e910e01ec2e07a8d73da6355186ec001dfca350ab4251549` |
| `artifacts-api.json` | 2472 | `bb64c6c5ea9454c9855468663e4ad372d14e38692986ec0e366776dad439dec5` |
| `verify-downloaded-artifact.stdout.json` | 2427 | `7e5b5a6d89be059873a8a1b92e56c59a0897c618dd9718fb4448b0a10e31d1d0` |
| `emit-attestation.stdout.json` | 520 | `6f7e1fa7b579081cb7160389d45bb16825706b64655ad2bc521b73ce05b1a57b` |
| `pre-merge-comment.md` | 1839 | `2138870e141753c991cfa33965f85dd99c0797064b8cbba65ad99688e514c06e` |
| `post-merge-comment.md` | 2150 | `f1356b17832fd16da9408527eae338cf969291b941618a0e54d407262e830155` |
| `epic-closure-comment.md` | 643 | `d7594f6f9f02b837fae1007372165ea11b6bd8311dcbfe53c79589da3bc69c35` |
| `raw-artifact-archive.bin` | 128 | `f045719a6085e235f04e34bb12054b841ee0457dd4c424f7ecbd781c0f307368` |

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
{"schema_version":1,"kind":"post-merge-closure-v1","repository":"chemitaro/spec-dock","issue_number":392,"pre_merge_comment_id":6001,"pre_merge_payload_sha256":"81a8cb8ffac801b7aacb8909380b644be1e58e77a474127205d2785ebd8a1ea4","final_head_sha":"cccccccccccccccccccccccccccccccccccccccc","final_head_tree":"dddddddddddddddddddddddddddddddddddddddd","merge_commit_sha":"eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee","merge_commit_tree":"dddddddddddddddddddddddddddddddddddddddd","tree_equal":true,"merge_actor":"chemitaro","merged_at":"2026-09-02T02:00:00Z","issue_finish_command":"python3 ./spec-dock/scripts/spec-dock issue finish","max_finish_attempts":3,"issue_finish_attempts":[{"attempt":1,"started_at":"2026-09-02T02:05:00Z","completed_at":"2026-09-02T02:07:00Z","exit_code":1,"status":"post-sync-failed","already_closed":false,"active_cleared":true,"post_sync_status":"failed"},{"attempt":2,"started_at":"2026-09-02T02:10:00Z","completed_at":"2026-09-02T02:12:00Z","exit_code":0,"status":"finished","already_closed":true,"active_cleared":true,"post_sync_status":"completed"}],"active_restore_attempts":[{"before_attempt":2,"command":"python3 ./spec-dock/scripts/spec-dock active set --id iss-00392","started_at":"2026-09-02T02:08:00Z","completed_at":"2026-09-02T02:08:20Z","exit_code":0,"stdout_sha256":"1967627d9f241b2dccef144b99af201ea0f196efe71941a59e1275d0f8bfc1cd","stderr_sha256":"e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855","readback_command":"python3 ./spec-dock/scripts/spec-dock active show","readback_started_at":"2026-09-02T02:08:21Z","readback_completed_at":"2026-09-02T02:09:00Z","readback_exit_code":0,"readback_stdout_sha256":"7b85ea56ea35d990a60006e46d08482aef029c0f3e5ace33955b0d5d1867004a","readback_stderr_sha256":"e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855","active_issue_id_after":"iss-00392"}],"accepted_issue_finish_attempt":2,"github_issue_closed_event_id":7001,"github_issue_closed_at":"2026-09-02T02:06:00Z","generated_at":"2026-09-02T02:13:00Z"}
```

#### `epic-closure-v1.json`

```json
{"schema_version":1,"kind":"epic-closure-v1","repository":"chemitaro/spec-dock","epic_issue_number":384,"implementation_issue_number":392,"post_merge_comment_id":6002,"post_merge_payload_sha256":"9ae45c0e264aeddf17d1c50b02a8966513c7ca902615a60435401b36aad31891","implementation_issue_closed_event_id":7001,"implementation_issue_closed_at":"2026-09-02T02:06:00Z","epic_acceptance_status":"accepted","github_epic_closed_event_id":7002,"github_epic_closed_at":"2026-09-02T02:20:00Z","generated_at":"2026-09-02T02:21:00Z"}
```

#### `comment-receipt-pre-merge.json`

```json
{"schema_version":1,"kind":"comment-receipt-v1","attestation_kind":"pre-merge-attestation-v1","repository":"chemitaro/spec-dock","target_issue_number":392,"comment_id":6001,"comment_url":"https://api.github.com/repos/chemitaro/spec-dock/issues/comments/6001","author_login":"chemitaro","created_at":"2026-09-02T01:01:00Z","updated_at":"2026-09-02T01:01:00Z","payload_sha256":"81a8cb8ffac801b7aacb8909380b644be1e58e77a474127205d2785ebd8a1ea4","body_sha256":"2138870e141753c991cfa33965f85dd99c0797064b8cbba65ad99688e514c06e","body_size_bytes":1839,"verified_at":"2026-09-02T01:01:30Z"}
```

#### `comment-receipt-post-merge.json`

```json
{"schema_version":1,"kind":"comment-receipt-v1","attestation_kind":"post-merge-closure-v1","repository":"chemitaro/spec-dock","target_issue_number":392,"comment_id":6002,"comment_url":"https://api.github.com/repos/chemitaro/spec-dock/issues/comments/6002","author_login":"chemitaro","created_at":"2026-09-02T02:14:00Z","updated_at":"2026-09-02T02:14:00Z","payload_sha256":"9ae45c0e264aeddf17d1c50b02a8966513c7ca902615a60435401b36aad31891","body_sha256":"f1356b17832fd16da9408527eae338cf969291b941618a0e54d407262e830155","body_size_bytes":2150,"verified_at":"2026-09-02T02:14:30Z"}
```

#### `comment-receipt-epic.json`

```json
{"schema_version":1,"kind":"comment-receipt-v1","attestation_kind":"epic-closure-v1","repository":"chemitaro/spec-dock","target_issue_number":384,"comment_id":6003,"comment_url":"https://api.github.com/repos/chemitaro/spec-dock/issues/comments/6003","author_login":"chemitaro","created_at":"2026-09-02T02:22:00Z","updated_at":"2026-09-02T02:22:00Z","payload_sha256":"3eaf09de7b9096566d2b7960cd6f7e920228661b1fc9a594701def15a7d5a05e","body_sha256":"d7594f6f9f02b837fae1007372165ea11b6bd8311dcbfe53c79589da3bc69c35","body_size_bytes":643,"verified_at":"2026-09-02T02:22:30Z"}
```

#### `run-api.json`

```json
{"id":1101,"run_attempt":1,"head_sha":"cccccccccccccccccccccccccccccccccccccccc","event":"workflow_dispatch","status":"completed","conclusion":"success","repository":{"full_name":"chemitaro/spec-dock"},"workflow_id":9001,"html_url":"https://github.com/chemitaro/spec-dock/actions/runs/1101"}
```

#### `jobs-api.json`

```json
{"total_count":6,"jobs":[{"id":2101,"run_id":1101,"name":"provider-build-artifacts","status":"completed","conclusion":"success","started_at":"2026-09-02T00:00:00Z","completed_at":"2026-09-02T00:10:00Z","steps":[{"number":1,"name":"Run exact provider-gate role","status":"completed","conclusion":"success"}]},{"id":2102,"run_id":1101,"name":"provider-linux-canonical","status":"completed","conclusion":"success","started_at":"2026-09-02T00:00:00Z","completed_at":"2026-09-02T00:10:00Z","steps":[{"number":1,"name":"Run exact provider-gate role","status":"completed","conclusion":"success"}]},{"id":2103,"run_id":1101,"name":"provider-sdist-smoke","status":"completed","conclusion":"success","started_at":"2026-09-02T00:00:00Z","completed_at":"2026-09-02T00:10:00Z","steps":[{"number":1,"name":"Run exact provider-gate role","status":"completed","conclusion":"success"}]},{"id":2104,"run_id":1101,"name":"provider-macos-delta","status":"completed","conclusion":"success","started_at":"2026-09-02T00:00:00Z","completed_at":"2026-09-02T00:10:00Z","steps":[{"number":1,"name":"Run exact provider-gate role","status":"completed","conclusion":"success"}]},{"id":2105,"run_id":1101,"name":"provider-attestation","status":"completed","conclusion":"success","started_at":"2026-09-02T00:00:00Z","completed_at":"2026-09-02T00:10:00Z","steps":[{"number":1,"name":"Run exact provider-gate role","status":"completed","conclusion":"success"}]},{"id":2106,"run_id":1101,"name":"provider-gate","status":"completed","conclusion":"success","started_at":"2026-09-02T00:00:00Z","completed_at":"2026-09-02T00:10:00Z","steps":[{"number":1,"name":"Run exact provider-gate role","status":"completed","conclusion":"success"}]}]}
```

#### `artifacts-api.json`

```json
{"total_count":6,"artifacts":[{"id":3100,"name":"provider-candidate-cccccccccccccccccccccccccccccccccccccccc","size_in_bytes":128,"digest":"sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","expired":false,"workflow_run":{"id":1101},"created_at":"2026-09-02T00:10:00Z","expires_at":"2026-12-01T00:10:00Z","archive_download_url":"https://api.github.com/repos/chemitaro/spec-dock/actions/artifacts/3100/zip"},{"id":3101,"name":"provider-receipt-producer-cccccccccccccccccccccccccccccccccccccccc","size_in_bytes":256,"digest":"sha256:cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc","expired":false,"workflow_run":{"id":1101},"created_at":"2026-09-02T00:10:00Z","expires_at":"2026-12-01T00:10:00Z","archive_download_url":"https://api.github.com/repos/chemitaro/spec-dock/actions/artifacts/3101/zip"},{"id":3102,"name":"provider-receipt-linux-canonical-cccccccccccccccccccccccccccccccccccccccc","size_in_bytes":256,"digest":"sha256:dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd","expired":false,"workflow_run":{"id":1101},"created_at":"2026-09-02T00:10:00Z","expires_at":"2026-12-01T00:10:00Z","archive_download_url":"https://api.github.com/repos/chemitaro/spec-dock/actions/artifacts/3102/zip"},{"id":3103,"name":"provider-receipt-sdist-smoke-cccccccccccccccccccccccccccccccccccccccc","size_in_bytes":256,"digest":"sha256:eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee","expired":false,"workflow_run":{"id":1101},"created_at":"2026-09-02T00:10:00Z","expires_at":"2026-12-01T00:10:00Z","archive_download_url":"https://api.github.com/repos/chemitaro/spec-dock/actions/artifacts/3103/zip"},{"id":3104,"name":"provider-receipt-macos-delta-cccccccccccccccccccccccccccccccccccccccc","size_in_bytes":256,"digest":"sha256:ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff","expired":false,"workflow_run":{"id":1101},"created_at":"2026-09-02T00:10:00Z","expires_at":"2026-12-01T00:10:00Z","archive_download_url":"https://api.github.com/repos/chemitaro/spec-dock/actions/artifacts/3104/zip"},{"id":3110,"name":"provider-evidence-cccccccccccccccccccccccccccccccccccccccc","size_in_bytes":256,"digest":"sha256:0000000000000000000000000000000000000000000000000000000000000000","expired":false,"workflow_run":{"id":1101},"created_at":"2026-09-02T00:10:00Z","expires_at":"2026-12-01T00:10:00Z","archive_download_url":"https://api.github.com/repos/chemitaro/spec-dock/actions/artifacts/3110/zip"}]}
```

#### `verify-downloaded-artifact.stdout.json`

```json
{"schema_version":1,"status":"completed","code":"downloaded-artifact-verified","command":"verify-downloaded-artifact","scope":"aggregate","verification_phase":"post-run-final","repository":"chemitaro/spec-dock","workflow_run_id":1101,"source_sha":"cccccccccccccccccccccccccccccccccccccccc","source_tree":"dddddddddddddddddddddddddddddddddddddddd","candidate_artifact_name":"provider-candidate-cccccccccccccccccccccccccccccccccccccccc","evidence_artifact_name":"provider-evidence-cccccccccccccccccccccccccccccccccccccccc","api_snapshots":[{"kind":"run","filename":"run.json","size_bytes":292,"sha256":"178e538f002baafbdbba399a117f5031c7ff07e1ae691abec0b12e2cef0160b9"},{"kind":"jobs","filename":"jobs.json","size_bytes":1702,"sha256":"753f6326ffa4b1d1e910e01ec2e07a8d73da6355186ec001dfca350ab4251549"},{"kind":"artifacts","filename":"artifacts.json","size_bytes":2472,"sha256":"bb64c6c5ea9454c9855468663e4ad372d14e38692986ec0e366776dad439dec5"}],"artifact_archives":[{"role":"candidate","artifact_id":3100,"artifact_name":"provider-candidate-cccccccccccccccccccccccccccccccccccccccc","api_digest":"sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","archive_filename":"provider-candidate-cccccccccccccccccccccccccccccccccccccccc.zip","archive_size_bytes":128,"archive_sha256":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","extracted_directory":"/runner/_temp/spec-dock-iss-00392-fixture/verification/extracted/provider-candidate-cccccccccccccccccccccccccccccccccccccccc"},{"role":"provider-evidence","artifact_id":3110,"artifact_name":"provider-evidence-cccccccccccccccccccccccccccccccccccccccc","api_digest":"sha256:0000000000000000000000000000000000000000000000000000000000000000","archive_filename":"provider-evidence-cccccccccccccccccccccccccccccccccccccccc.zip","archive_size_bytes":256,"archive_sha256":"0000000000000000000000000000000000000000000000000000000000000000","extracted_directory":"/runner/_temp/spec-dock-iss-00392-fixture/verification/extracted/provider-evidence-cccccccccccccccccccccccccccccccccccccccc"}],"receipt_roles":["producer","linux-canonical","sdist-smoke","macos-delta"],"evidence_files":["provider-receipt-producer.json","producer-build-evidence.json","provider-receipt-linux-canonical.json","linux-canonical-evidence.json","provider-receipt-sdist-smoke.json","sdist-smoke-evidence.json","provider-receipt-macos-delta.json","macos-delta-evidence.json"]}
```

#### `emit-attestation.stdout.json`

```json
{"schema_version":1,"status":"completed","code":"attestation-emitted","command":"emit-attestation","kind":"pre-merge-attestation-v1","payload_path":"/runner/_temp/spec-dock-iss-00392-fixture/attestation/payload.json","payload_size_bytes":1706,"payload_sha256":"81a8cb8ffac801b7aacb8909380b644be1e58e77a474127205d2785ebd8a1ea4","comment_path":"/runner/_temp/spec-dock-iss-00392-fixture/attestation/comment.md","comment_size_bytes":1839,"comment_sha256":"2138870e141753c991cfa33965f85dd99c0797064b8cbba65ad99688e514c06e"}
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
<!-- spec-dock-attestation:post-merge-closure-v1:9ae45c0e264aeddf17d1c50b02a8966513c7ca902615a60435401b36aad31891 -->
```json
{"schema_version":1,"kind":"post-merge-closure-v1","repository":"chemitaro/spec-dock","issue_number":392,"pre_merge_comment_id":6001,"pre_merge_payload_sha256":"81a8cb8ffac801b7aacb8909380b644be1e58e77a474127205d2785ebd8a1ea4","final_head_sha":"cccccccccccccccccccccccccccccccccccccccc","final_head_tree":"dddddddddddddddddddddddddddddddddddddddd","merge_commit_sha":"eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee","merge_commit_tree":"dddddddddddddddddddddddddddddddddddddddd","tree_equal":true,"merge_actor":"chemitaro","merged_at":"2026-09-02T02:00:00Z","issue_finish_command":"python3 ./spec-dock/scripts/spec-dock issue finish","max_finish_attempts":3,"issue_finish_attempts":[{"attempt":1,"started_at":"2026-09-02T02:05:00Z","completed_at":"2026-09-02T02:07:00Z","exit_code":1,"status":"post-sync-failed","already_closed":false,"active_cleared":true,"post_sync_status":"failed"},{"attempt":2,"started_at":"2026-09-02T02:10:00Z","completed_at":"2026-09-02T02:12:00Z","exit_code":0,"status":"finished","already_closed":true,"active_cleared":true,"post_sync_status":"completed"}],"active_restore_attempts":[{"before_attempt":2,"command":"python3 ./spec-dock/scripts/spec-dock active set --id iss-00392","started_at":"2026-09-02T02:08:00Z","completed_at":"2026-09-02T02:08:20Z","exit_code":0,"stdout_sha256":"1967627d9f241b2dccef144b99af201ea0f196efe71941a59e1275d0f8bfc1cd","stderr_sha256":"e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855","readback_command":"python3 ./spec-dock/scripts/spec-dock active show","readback_started_at":"2026-09-02T02:08:21Z","readback_completed_at":"2026-09-02T02:09:00Z","readback_exit_code":0,"readback_stdout_sha256":"7b85ea56ea35d990a60006e46d08482aef029c0f3e5ace33955b0d5d1867004a","readback_stderr_sha256":"e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855","active_issue_id_after":"iss-00392"}],"accepted_issue_finish_attempt":2,"github_issue_closed_event_id":7001,"github_issue_closed_at":"2026-09-02T02:06:00Z","generated_at":"2026-09-02T02:13:00Z"}
```
````

#### `epic-closure-comment.md`

````text
<!-- spec-dock-attestation:epic-closure-v1:3eaf09de7b9096566d2b7960cd6f7e920228661b1fc9a594701def15a7d5a05e -->
```json
{"schema_version":1,"kind":"epic-closure-v1","repository":"chemitaro/spec-dock","epic_issue_number":384,"implementation_issue_number":392,"post_merge_comment_id":6002,"post_merge_payload_sha256":"9ae45c0e264aeddf17d1c50b02a8966513c7ca902615a60435401b36aad31891","implementation_issue_closed_event_id":7001,"implementation_issue_closed_at":"2026-09-02T02:06:00Z","epic_acceptance_status":"accepted","github_epic_closed_event_id":7002,"github_epic_closed_at":"2026-09-02T02:20:00Z","generated_at":"2026-09-02T02:21:00Z"}
```
````

#### `raw-artifact-archive.bin`

Hex bytes:

```text
504b030414000000000000002100ac2c607508000000080000000b0000007061796c6f61642e747874666978747572650a504b0102140314000000000000002100ac2c607508000000080000000b0000000000000000000000a481000000007061796c6f61642e747874504b0506000000000100010039000000310000000000
```

Tests regenerate every fixture, recompute every size/hash, validate parent-child/API/timestamp/recovery relations, verify raw archive digest semantics, and validate success stdout objects. Any drift is a specification defect.

## 10. Traceability

| Requirement | Design |
|---|---|
| I392-RQ-001–009 | D-007–010, failure register |
| I392-RQ-010–022 | D-001–006, wire artifact |
| I392-RQ-023–026 | D-011–012, D-024 |
| I392-RQ-027–029 | D-013–021, D-025–026 |
| I392-RQ-030–032 | D-022–023, D-025–026 |

The four r11 remediation contracts map to: the seven cleanup-warning rows plus WIR-CONT-001/WIR-TEXT-001; D-007/D-019/D-021/D-024 single-tree aggregate verification; D-013/D-016/D-020/D-021/D-025 phase-aware in-workflow and post-run evidence; and D-022/D-026 observable active restoration without an active-set post-sync field.
