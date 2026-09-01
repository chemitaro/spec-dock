---
種別: 設計書（Epic）
ID: "epic-00384"
タイトル: "Provider Test Strategy Simplification and Execution Cost Reduction"
関連GitHub: ["#384"]
状態: "draft"
最終更新: "2026-09-02"
依存: ["requirement.md", "artifacts/20260831t152024z-adr-single-implementation-unit-and-provider-hard-cutover-policy.md", "artifacts/provider-lifecycle-wire-contract.md", "artifacts/active-failure-disposition-register.md"]
親: ["init-local-00003"]
repository_evidence:
  repository: "chemitaro/spec-dock"
  branch: "codex/epic-00384-provider-test-strategy-planning"
  sha: "3c24bae76e86651f958bde7c716c5453fff73e56"
---

# epic-00384 Provider Test Strategy Simplification and Execution Cost Reduction — 設計

## 1. Architecture

```text
public CLI -> closed result adapter -> provider lifecycle service
                                  |-> classifier/candidate/legacy recognizer
                                  |-> descriptor-bound target filesystem
                                  `-> persistent external stage namespace

ephemeral evidence helper -> owner-bound OS-temp workspaces
protected witness -> all repository workbench + initiatives/artifacts
                     minus exact #392 report/meta exclusion ledger

PR-A/S30 -> dormant successor, old public product
PR-B/S60 -> complete lifecycle + retained current gates + dogfood migration
PR-C/compat head -> old and new required contexts emitted
PR-C/final head -> compatibility job removed, authoritative evidence rerun
PR-C/S80 -> human merge gate
```

Production source of truth is `src/spec_dock/`; checked-in `spec-dock/` is a consumer projection. The wire artifact owns every public lifecycle value. The register owns every Issue #387 conditional outcome.

## 2. Lifecycle ownership and state

### E384-D-001 — Code-fixed targets

Four roots, two slots, record, fresh-only seeds and shared-container create authority are constants. No manifest-supplied mutation path, wildcard or historical obsolete path is accepted. Slot markers bind slot/version/candidate digest; candidate digest excludes record, seeds and generated markers.

### E384-D-002 — Durable state and resume

Record keys are exactly `schema_version,state,operation,version,candidate_digest,seed_policy,skill_slots`. `seed_policy=create-if-absent` is admitted only for never-installed fresh init. Other intents use `preserve-only`. The exact resume tuple is stored in record and persistent stage ownership; mismatch blocks before new target mutation.

### E384-D-003 — Publication

Repository/parent descriptors are no-follow and identity-bound under an exclusive lock. Candidate is captured and validated before target mutation. Absent shared container is exclusively created and recorded in stage ownership. Fixed roots/slots publish in code-fixed order through native no-replace/exchange. Terminal record is last. Only post-terminal external cleanup failure may be a warning.

## 3. Persistent lifecycle stage namespace

### E384-D-004 — Namespace layout

```text
<repository-real-parent>/.spec-dock-provider-stages-v1/
  NAMESPACE.json
  repositories/<repository-key>/
    REPOSITORY.json
    ACTIVE.json
    stages/<tuple-key>/
      STAGE-OWNER.json
      candidate/
      tombstones/
```

- `repository-key = sha256(repository_realpath_utf8 + NUL + st_dev_decimal + NUL + st_ino_decimal)`.
- `tuple-key = sha256(operation + NUL + candidate_digest + NUL + seed_policy)`.
- namespace/repository/stage directories are mode 0700; JSON files mode 0600; all are real directories/regular link-count-1 files owned by current UID.
- namespace and repository sentinels bind parent/repository device/inode and exact purpose `provider-lifecycle-stage-v1`.
- namespace device must equal repository device. Cross-device or symlinked namespace fails closed.

### E384-D-005 — Index and cross-process recovery

`ACTIVE.json` is the only discovery index and has state `allocating|ready|terminal-cleanup`, repository key/identity, operation, candidate digest, seed policy and tuple key. The operation atomically creates `ACTIVE.json` before allocating the deterministic stage directory. A process restart reads only that exact index/path; it never scans the temp root, namespace, repositories or stage siblings.

- no index: create exact index with no-replace, then deterministic stage and owner;
- same tuple: verify every identity/content field and resume;
- different tuple: public `stage-owner-mismatch`;
- `allocating` with missing stage: create exact deterministic stage and continue;
- `allocating` with empty exact stage: complete owner initialization;
- unsafe/nonempty/unowned stage: fail closed;
- bootstrap-without-record: `ACTIVE.json` plus `STAGE-OWNER.created_spec_dock` is the recovery authority;
- terminal cleanup removes registered stage entries and stage first, then removes exact content-bound `ACTIVE.json`; crash leaves a deterministic cleanup-resumable state.

No repository `.workbench`, global scan or best-effort orphan adoption exists.

## 4. Ephemeral evidence workspace and protection

### E384-D-006 — Ephemeral workspace

Purpose enum is exactly `admission`, `baseline-build`, `protected-witness`, `full-regression-s00`, `full-regression-s30`, `full-regression-s60`, `tripwire`, `fresh-consumer`, `workflow-api`, `artifact-download`, `attestation-draft`. `mkdtemp` creation, outside-repository realpath proof, UID/mode/device/inode capture, exclusive `OWNER.json`, registered-child cleanup and collision rules are shared by local commands and the S60 retained workflow.

### E384-D-007 — Protected witness and exclusion ledger

The witness records every entry under repository `spec-dock/.workbench/**` and all initiative/artifact paths by UTF-8-bytewise relative path, type, mode, uid/gid, link target, device identity and regular-file size/hash. It also covers seeds, unknown non-target paths and unrelated skills.

Only these paths are excluded from the main protected equality manifest:

```text
spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00384-provider-test-strategy-simplification-and-execution-cost-reduction/issues/iss-00392-provider-lifecycle-and-regression-gate-hard-cutover/report.md
spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00384-provider-test-strategy-simplification-and-execution-cost-reduction/issues/iss-00392-provider-lifecycle-and-regression-gate-hard-cutover/.meta.json
```

A separate `authorized-exclusions.json` outside the repository records exact before/after Git blob OID, filesystem mode/type, history parent, command/step and allowed semantic diff. Report changes are limited to the non-self-referential pre-merge sections defined by Issue Plan. Meta changes are limited to existing `updated_at`; every other parsed key/value is equal. Any other path or field change stops.

## 5. Issue #387 admission

### E384-D-008 — `ISS387-THREE-WAY-V2`

The #387 report block contains candidate SHA/tree and 12 mappings, not a PR number or merge identity. Candidate is the last semantic commit. Candidate-to-final-head tail is required report plus optional `.meta.json` updated-at only.

S00 calls candidate-associated PR and Issue #387 timeline APIs, intersects/filter results and requires exactly one merged PR. It then verifies candidate ancestry, exact evidence tail, final-head/merge tree equality, main reachability and merged report/ledger/collection. The register derives admitted rows and S60 actions. No fixed post-#387 row count or implementer-selected successor exists.

## 6. Dogfood, docs and current gate

### E384-D-009 — PR-B

S40 changes provider code/docs and root README lifecycle sections but preserves checked-in dogfood. S50 proves migration on external synthetic consumers. S60 applies the final service once to exact legacy dogfood, commits four roots/two slots/record/two markers, and compares provider/dogfood candidate digest. S60 also updates root AGENTS lifecycle/uninstall text, failure ledger/consumers, current Provider CI references and retained Full Regression workflow.

The retained workflow uses external purpose `full-regression-s60` below `${{ runner.temp }}`, passes `--artifact-dir` explicitly and uploads that path. No test-policy/provider-gate redesign occurs at S60.

### E384-D-010 — PR-C candidate

S70 adds final gate/environment/tests/docs, retires all old consumers before providers, removes old machinery and performs the second complete dogfood update. It first creates `PRC_COMPAT_HEAD`, where both old/new contexts emit. After context transition, `PRC_FINAL_HEAD` changes only `.github/workflows/provider-ci.yml` by removing exact job `provider-tests`; candidate bytes/dogfood do not change.

## 7. Final CI/evidence architecture

### E384-D-011 — Job graph

```text
provider-build-artifacts
  -> provider-linux-canonical
  -> provider-sdist-smoke
  -> provider-macos-delta
all four -> provider-attestation -> provider-gate
provider-attestation -> provider-tests (compatibility head only)
```

`provider-tests` independently verifies attestation success; it is not a no-op and remains GREEN when the new aggregate canary alone is forced RED. The final head removes only this job.

### E384-D-012 — Byte schemas and aggregate

Issue Design fixes exact ordered schemas for candidate manifest, receipts, role evidence, provider aggregate and attestations. Every file is compact UTF-8 plus one LF. `EVIDENCE-FIXTURE-V1` fixes canonical serializer bytes, sizes and SHA-256 values for all these objects and the three Issue-comment envelopes. Receipt hashes role evidence bytes; provider aggregate hashes all eight subordinate files; downloaded verification recomputes every size/hash and cross-checks Actions run/job/artifact metadata. No schema inference or additional key is allowed.

### E384-D-013 — Qualification

Linux role evidence binds `specdock-linux-qualification-v1`, descriptor/base image/resources/toolchain, exactly one pytest process/worker, 20 ordered runs and fault results. Different fingerprints cannot be combined.

## 8. Two-head context and closure

### E384-D-014 — Required-context sequence

1. push/test `PRC_COMPAT_HEAD`; both contexts GREEN;
2. human adds new required context while old remains and reads back both;
3. dedicated non-merge canary adds exact `.github/provider-gate-canary-red`; only `provider-gate` fails, `provider-tests` remains GREEN; prove block, close canary;
4. implementation PR compatibility head GREEN again;
5. human removes old required and reads back new-only required;
6. create `PRC_FINAL_HEAD` by deleting only compatibility job from `provider-ci.yml`;
7. freeze final head, rerun producer/all role/evidence jobs and final readback;
8. append-only pre-merge attestation; human merge; tree equality; post/Epic attestations.

### E384-D-015 — Attestation object

Attestations are canonical compact JSON files rendered by `emit-attestation`, then posted verbatim in a new GitHub Issue comment with marker `<!-- spec-dock-attestation:<kind>:<sha256> -->`. Pre/post comments use #392; Epic closure uses #384. Posting requires `issues:write`; verification uses `issues:read`, records comment ID/author/URL, requires marker/hash/bytes exact and `created_at == updated_at`. Any PATCH/edit/delete invalidates the object.

## 9. Traceability

| Requirement | Design |
|---|---|
| E384-RQ-001–005 | D-001–007 |
| E384-RQ-006–007 | D-001–005, D-009–010 and wire artifact |
| E384-RQ-008–011 | D-007–009 and failure register |
| E384-RQ-012–014 | D-010–014 and Issue evidence schemas |
| E384-RQ-015–017 | D-009–015 |
