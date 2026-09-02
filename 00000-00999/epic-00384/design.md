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
  sha: "ea168b745d3f443f11a24b975f32e3bb6fb17b1a"
---

# epic-00384 Provider Test Strategy Simplification and Execution Cost Reduction — 設計

## 1. Architecture

```text
public CLI -> closed wire adapter -> lifecycle service
                                   |-> classifier/candidate/legacy recognizer
                                   |-> descriptor-bound target filesystem
                                   `-> process-independent stage namespace

purpose workspace factory -> private owner root + exported reserved tree per purpose
protected witness         -> complete repository workbench/data observation

PR-A/S30 -> dormant successor, old public product
PR-B/S60 -> complete lifecycle + retained current gates + complete dogfood migration
PR-C compatibility head -> old/new contexts + compatibility byte verifier
PR-C final head         -> compatibility job removed + raw/archive/API evidence rerun
S80                     -> read-only PR-C merge gate
```

Production source of truth is `src/spec_dock/`; checked-in `spec-dock/` is a consumer projection. The wire artifact owns every public lifecycle value. The register owns every #387 conditional outcome.

## 2. Lifecycle ownership and state

### E384-D-001 — Code-fixed targets

Four roots, two slots, record, fresh-only seeds and shared-container create authority are constants. No manifest-supplied mutation path, wildcard or historical obsolete path is accepted. Slot markers bind slot/version/candidate digest; candidate digest excludes record, seeds and generated markers.

### E384-D-002 — Durable state, deferred intent and public continuation

The seven-key record keeps exact resume identity. Persistent `ACTIVE.json` stores old result family, an exact identity-bound `cleanup_token`, and a nullable deferred-invocation object. Invocation role is syntactic and machine-visible: every public command without the hidden token is desired, while the exact generated command carrying `--provider-cleanup-token <active token>` is cleanup-only. The first desired request is stored immutably even when its base form equals the old retry; tokenized retry, repeat, or third command cannot overwrite it. Cleanup failure returns tokenized retry now and optionally the first desired command after cleanup. Cleanup success is cleanup-only and returns that desired command or no action. The wire continuation object is the sole caller authority.

### E384-D-003 — Publication

Repository/parent descriptors are no-follow and identity-bound under exclusive lock. Candidate is captured/validated before target mutation. Absent shared container is exclusively created and recorded in stage ownership. Fixed roots/slots publish through native no-replace/exchange. Terminal record is last. A post-terminal cleanup warning leaves deterministic terminal-cleanup state and an exact retry command.

## 3. Persistent lifecycle stage namespace

### E384-D-004 — Layout and private schema

The same-filesystem layout remains namespace sentinel, per-repository sentinel, one `ACTIVE.json`, and deterministic tuple-key stage. Repository/tuple keys are SHA-256 over exact identities. ACTIVE exact keys include immutable `cleanup_token` and nullable `deferred_invocation`; its desired invocation enum is the seven wire forms. The cleanup token is a 64-hex SHA-256 of the wire-defined repository/tuple/result-family input and is identity binding, not authorization. Namespace/repository/stage directories are real, current-UID, 0700; JSON is canonical, regular/link-one, 0600. ACTIVE is the only locator; scans and orphan adoption are forbidden.

### E384-D-005 — Recovery state machine

Absent ACTIVE fsyncs parent then dispatches. Allocating/ready incomplete resumes exact tuple. Ready terminal atomically becomes cleanup. Before cleanup, a no-token invocation is persisted as the first desired request; an exact tokenized retry never changes it. Stage present/already absent and ACTIVE unlink crash are deterministic. Failure emits the exact tokenized cleanup retry plus the deferred desired request; success emits the desired request only, or none; both are cleanup-only. Wrong/missing token on a retry form and any identity/sentinel/entry mismatch fail closed.

## 4. Independent ephemeral workspaces and protection

### E384-D-006 — Private owner root and reserved-tree API

Each purpose creates a private mode-0700 owner root and live descriptor-backed handle. The root path is not exported. The owner reserves one exact top-level child, pre-registers every fixed output or closed subtree policy, and exports only the reserved child through the purpose-specific `ISS392_WS_*` variable. Exact mappings, policy IDs and layouts are Issue Design D-007. Children receive the reserved tree only and cannot create registration or cleanup authority. Owner seals output, remains alive through upload confirmation and cleans only via handle. Unknown or policy-invalid entries, root exposure, identity drift or premature owner death preserve and stop.

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

### E384-D-011 — Compatibility/final graph, raw bytes and permissions

Compatibility graph is producer -> three roles; producer+roles -> attestation -> gate, with compatibility provider-tests depending producer+attestation. Final removes only provider-tests. Workflow-level permissions are `{}`; exact job overrides are fixed in Issue Design. Every role/attestation/compatibility download preserves authenticated raw ZIP bytes, matches API/upload SHA-256, safe-extracts and passes raw+extracted+API data to the same verifier. Only gate reads the canary.

### E384-D-012 — Byte graph, exact Provider Gate CLI and qualification

Only producer packages once; consumers build zero. All nine provider-gate subcommands have exact argv, required flags, path types, repeated option order, stdout/stderr and number-code-message mapping in Issue Design. Provider evidence remains nine actual files and all raw archives/extracted files/API snapshots are independently verified. Linux evidence binds `specdock-linux-qualification-v1`, one fingerprint, twenty runs and fault metrics.

## 8. Attestation and closure

### E384-D-013 — Tracked/external identity split

Tracked #392 report records method and implementation summaries but no actual compatibility/final head or run identity. Actual compatibility/final SHA/tree and run IDs are fields of the external pre-merge attestation. Fixture identities are distinct, and all parent/child hashes are computed over actual canonical bytes.

### E384-D-014 — Append-only objects and comment receipts

`emit-attestation` creates payload/comment bytes only. Human posts pre-merge and post-merge comments to #392 and Epic closure to #384. Each payload omits its own future comment ID/body hash. After posting, an external `comment-receipt-v1` records target, ID, URL, actor, created/updated timestamps, payload hash, body hash/size and verification time. It is not embedded in payload or tracked tree.

### E384-D-015 — Closure state machine with post-sync recovery

```text
pre-merge #392 comment verified
-> human merge and tree equality
-> issue finish attempt 1
-> if post-sync failed after close/clear: bind unique original close event
-> active set iss-00392 and retry issue finish as already-closed (maximum attempts 3)
-> final successful interval selected
-> post-merge payload/comment/receipt on #392
-> Epic acceptance
-> close #384 and read event
-> Epic payload/comment/receipt on #384
```

No redundant #392 close command exists. Failed restore, ambiguous close event or three post-sync failures stops. Payload records all attempts/restores and the accepted final interval, while preserving the original close event.

## 9. r10 cross-contract invariants

- Wire continuation separates cleanup retry from desired request.
- Workspace variables are reserved trees, never owner roots.
- Provider Gate validates raw ZIP and extracted bytes under exact permissions.
- Closure accepts only a final successful issue-finish attempt after bounded recovery.

## 9. Traceability

| Requirement | Design |
|---|---|
| E384-RQ-001–005 | D-001–007 and wire artifact |
| E384-RQ-006–011 | D-001–010 and failure register |
| E384-RQ-012–014 | D-011–013 and Issue evidence schemas |
| E384-RQ-015–017 | D-013–015 |
