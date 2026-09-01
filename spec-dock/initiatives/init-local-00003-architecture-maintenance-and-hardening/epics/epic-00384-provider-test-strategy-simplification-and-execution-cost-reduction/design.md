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
  sha: "95d7562ca1762e0b2a717912484eba5a5c2377f1"
---

# epic-00384 Provider Test Strategy Simplification and Execution Cost Reduction — 設計

## 1. Architecture

```text
public CLI -> closed wire adapter -> lifecycle service
                                   |-> classifier/candidate/legacy recognizer
                                   |-> descriptor-bound target filesystem
                                   `-> process-independent stage namespace

purpose workspace factory -> one mkdtemp + one cleanup handle per purpose
protected witness         -> complete repository workbench/data observation

PR-A/S30 -> dormant successor, old public product
PR-B/S60 -> complete lifecycle + retained current gates + complete dogfood migration
PR-C compatibility head -> old/new contexts + compatibility byte verifier
PR-C final head         -> compatibility job removed + full evidence rerun
S80                     -> read-only PR-C merge gate
```

Production source of truth is `src/spec_dock/`; checked-in `spec-dock/` is a consumer projection. The wire artifact owns every public lifecycle value. The register owns every #387 conditional outcome.

## 2. Lifecycle ownership and state

### E384-D-001 — Code-fixed targets

Four roots, two slots, record, fresh-only seeds and shared-container create authority are constants. No manifest-supplied mutation path, wildcard or historical obsolete path is accepted. Slot markers bind slot/version/candidate digest; candidate digest excludes record, seeds and generated markers.

### E384-D-002 — Durable state, resume and cleanup

Record keys are exactly `schema_version,state,operation,version,candidate_digest,seed_policy,skill_slots`. Resume identity is exact operation/candidate/policy. Persistent `ACTIVE.json` additionally stores private `result_family=install|legacy-migration|update|uninstall`, allowing a later process to render the correct cleanup retry without changing the resume tuple.

Normal dispatch is preceded by `recover_terminal_cleanup()`. It validates exact stage ownership and final record, promotes `ACTIVE.ready` to `terminal-cleanup`, removes registered stage entries, tolerates an already-absent stage, content-bound removes ACTIVE and fsyncs its parent. ACTIVE already absent causes a parent fsync then dispatch. Cleanup failure returns closed code `terminal-cleanup-failed` with actual invocation echo; cleanup success from present ACTIVE returns cleanup-only `terminal-cleanup-completed`. Neither result executes the new intent. ACTIVE-absent fsync recovery alone continues normal dispatch.

### E384-D-003 — Publication

Repository/parent descriptors are no-follow and identity-bound under exclusive lock. Candidate is captured/validated before target mutation. Absent shared container is exclusively created and recorded in stage ownership. Fixed roots/slots publish through native no-replace/exchange. Terminal record is last. A post-terminal cleanup warning leaves deterministic terminal-cleanup state and an exact retry command.

## 3. Persistent lifecycle stage namespace

### E384-D-004 — Layout and private schema

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

`repository-key = sha256(repository_realpath_utf8 + NUL + st_dev + NUL + st_ino)` and `tuple-key = sha256(operation + NUL + candidate_digest + NUL + seed_policy)`. Directories are real, current-UID, 0700 and same-device; JSON files are regular/link-count-one/0600. `ACTIVE.json` is the only locator; directory scans and unknown orphan adoption are forbidden.

`ACTIVE.json` and `STAGE-OWNER.json` include exact `result_family`. Allocation states are `allocating|ready|terminal-cleanup`. `result_family` is immutable for an ACTIVE lifetime and determines only retry rendering for terminal cleanup.

### E384-D-005 — Recovery state machine

- absent ACTIVE: no-replace allocate exact tuple index and deterministic stage;
- allocating: initialize/reopen only exact empty/owned stage;
- ready + incomplete record: same tuple lifecycle resume;
- ready + terminal record: atomically transition to terminal-cleanup before new dispatch;
- terminal-cleanup + stage present: validate registered entries, remove them/stage, then ACTIVE;
- terminal-cleanup + stage absent: remove ACTIVE and fsync parent;
- ACTIVE absent after prior unlink crash: fsync parent and continue;
- any identity/sentinel/registered-entry mismatch: fail closed without scanning/deleting unknown data.

## 4. Independent ephemeral workspaces and protection

### E384-D-006 — Purpose workspace API

`create_external_workspace(repository,purpose,parent=None)` returns `(path, ExternalWorkspaceHandle)`. No serializable token can recreate the handle. Exact environment variables map one-to-one to independently-created paths:

```text
ISS392_WS_ADMISSION
ISS392_WS_BASELINE_BUILD
ISS392_WS_PROTECTED_WITNESS
ISS392_WS_FULL_REGRESSION_S00
ISS392_WS_FULL_REGRESSION_S30
ISS392_WS_FULL_REGRESSION_S60
ISS392_WS_TRIPWIRE
ISS392_WS_FRESH_CONSUMER
ISS392_WS_WORKFLOW_API
ISS392_WS_ARTIFACT_DOWNLOAD
ISS392_WS_ATTESTATION_DRAFT
```

There is no aggregate external-root variable. An orchestrator may hold several handles simultaneously, but no workspace is a child of another. Each live owner reserves top-level child trees before launch, children write only beneath reserved descriptors, and the owner seals the complete descendant inventory. In Actions the background owner retains FDs through upload confirmation; unknown entries or premature cleanup fail closed.

### E384-D-007 — Protected witness and exclusions

The witness is in `ISS392_WS_PROTECTED_WITNESS` and captures all repository `spec-dock/.workbench/**`, initiatives/artifacts, seeds, unknown paths and unrelated skills by UTF-8 path order, kind, mode, UID/GID, link target, size/content hash and device identity. Only exact #392 `report.md` and `.meta.json` are excluded from equality; `authorized-exclusions.json` separately fixes their before/after blobs, mode, parents, step and allowed semantic diff. No other exclusion is valid.

## 5. Issue #387 admission

### E384-D-008 — Mapping-only report

The report block is schema 4 with exact top-level keys `schema_version,kind,issue_id,rule_id,entries`. It contains exactly twelve entries and no repository/PR/commit/tree/merge/timestamp/ledger/collection identity. Thus the current #387 plan remains satisfiable without an extra commit boundary or report self-reference.

### E384-D-009 — Unique PR and merge-tree evidence

S00 obtains Issue #387 timeline/cross-reference PR numbers, fetches each PR, and verifies each exact head SHA through the commit-association endpoint. It filters same repository, base `main`, merged state, report presence and main reachability, then requires exactly one. It compares PR-head tree to merge-commit tree and reads report, ledger and collection from that merge tree. `ISS387-THREE-WAY-V2` determines the admitted rows; no semantic-candidate/evidence-tail construct exists.

## 6. PR-B and dogfood

### E384-D-010 — S40/S50/S60

S40 changes provider lifecycle code/docs and root README lifecycle sections but preserves checked-in dogfood. S50 proves migration on independent external consumers. S60 applies the final service once to exact legacy dogfood, commits four roots/two slots/seven-key record/two markers, and proves candidate parity/protection. It updates AGENTS lifecycle/uninstall sections, current Provider CI test references and retained Full Regression workflow.

The retained workflow creates an independent `full-regression-s60` workspace below `${{ runner.temp }}` with a background owner, reserves/seals the output tree, passes it through `--artifact-dir`, keeps owner FDs alive through upload, and cleans only after actual upload confirmation. Name, triggers, concurrency, job ID and policy stay otherwise current.

## 7. Final CI/evidence architecture

### E384-D-011 — Compatibility and final job graphs

Compatibility head:

```text
provider-build-artifacts: []
provider-linux-canonical: [provider-build-artifacts]
provider-sdist-smoke: [provider-build-artifacts]
provider-macos-delta: [provider-build-artifacts]
provider-attestation: [provider-build-artifacts,provider-linux-canonical,provider-sdist-smoke,provider-macos-delta]
provider-gate: [provider-attestation]
provider-tests: [provider-build-artifacts,provider-attestation]
```

`provider-tests` has `actions:read`, `contents:read`, `pull-requests:read`; downloads exact candidate and nine-file evidence artifacts, saves run/jobs/artifacts API snapshots in its own workflow-api workspace and artifacts in its own artifact-download workspace, then calls the exact downloaded verifier. It invokes no package build and does not read the canary marker. Only `provider-gate` reads `.github/provider-gate-canary-red`.

Final head removes only `provider-tests`. Compatibility and final SHA/tree identities are external evidence only and must differ. Final head reruns all authoritative jobs.

### E384-D-012 — Byte graph and qualification

Only `provider-build-artifacts` packages once. Three role jobs build zero. `provider-attestation` verifies candidate bytes, four receipts, four role evidence files and API metadata, then uploads the exact nine-file `provider-evidence-<sha>`. S80 downloads candidate/evidence/API bytes and uses the same verifier interface. Linux evidence binds `specdock-linux-qualification-v1` and exact twenty-run fingerprint/metrics.

## 8. Attestation and closure

### E384-D-013 — Tracked/external identity split

Tracked #392 report records method and implementation summaries but no actual compatibility/final head or run identity. Actual compatibility/final SHA/tree and run IDs are fields of the external pre-merge attestation. Fixture identities are distinct, and all parent/child hashes are computed over actual canonical bytes.

### E384-D-014 — Append-only objects and comment receipts

`emit-attestation` creates payload/comment bytes only. Human posts pre-merge and post-merge comments to #392 and Epic closure to #384. Each payload omits its own future comment ID/body hash. After posting, an external `comment-receipt-v1` records target, ID, URL, actor, created/updated timestamps, payload hash, body hash/size and verification time. It is not embedded in payload or tracked tree.

### E384-D-015 — Closure state machine

```text
pre-merge #392 comment verified
-> human merge
-> final-head-tree == merge-tree
-> spec-dock issue finish starts
-> issue finish closes #392, clears active and post-syncs
-> returned close snapshot + #392 close event read
-> post-merge payload/comment/receipt on #392
-> Epic acceptance re-evaluated
-> spec-dock close epic-00384
-> #384 close event read
-> Epic payload/comment/receipt on #384
```

No payload requires a future event. Epic closure may reference the already-observed post-merge comment ID and payload hash.

## 9. Traceability

| Requirement | Design |
|---|---|
| E384-RQ-001–005 | D-001–007 and wire artifact |
| E384-RQ-006–011 | D-001–010 and failure register |
| E384-RQ-012–014 | D-011–013 and Issue evidence schemas |
| E384-RQ-015–017 | D-013–015 |
