---
種別: ADR
ID: "20260831t152024z-adr"
タイトル: "Single Implementation Unit and Provider Hard Cutover Policy"
状態: "accepted"
決定日: "2026-08-31"
最終更新: "2026-09-02"
対象: ["epic-00384", "iss-00392"]
repository_evidence:
  repository: "chemitaro/spec-dock"
  branch: "codex/epic-00384-provider-test-strategy-planning"
  sha: "0fafbf3e02d2fcd5b622d6a997323e0f98eb1c78"
---

# ADR: Single Implementation Unit and Provider Hard Cutover Policy

Normative artifacts are `artifacts/provider-lifecycle-wire-contract.md` and `artifacts/active-failure-disposition-register.md`.

## Context

Epic #384 changes provider ownership, migration, uninstall, dogfood, public wire, failure disposition, operator guidance and CI evidence. Multiple implementation Issues, an intermediate public generation or ambiguous recovery would create multiple writers and unsafe merge states. Strict review additionally fixed cleanup continuation, private-owner/reserved-tree workspace semantics, all nine Provider Gate inputs/raw archive/permissions, and issue-finish post-sync recovery, while retaining prior #387/evidence/two-head corrections.

## Decisions

### ADR-D1 — One Issue and dependency

GitHub #392 is the sole implementation-and-verification Issue and starts only after #387 merge/admission. #387 canonical documents are not changed. Human alone merges and changes required contexts.

### ADR-D2 — Three safe main gates

S30, S60 and S80 are the only main gates. S40/S50/S70 are non-main. Main sees old product after PR-A, complete `0.2.4` plus coherent current gates after PR-B, and final build-once gate after PR-C. No bridge, toggle, dual writer or automatic old fallback.

### ADR-D3 — Fixed lifecycle, immutable policy and deterministic continuation

Four roots, two slots, one record and bounded bootstrap/seeds remain fixed. ACTIVE stores old result family, exact cleanup token and nullable desired invocation. Every no-token public command is desired; only the generated hidden-token form is cleanup-only, so a desired update/init-force cannot be mistaken for an old retry. Public continuation separately represents tokenized cleanup retry and desired-after-cleanup command. Cleanup warnings and failures always use exact `active.cleanup_retry_command` with the matching hidden token; un-tokenized lifecycle retry tokens remain limited to lifecycle partial failures. Cleanup success is cleanup-only and returns desired command or none. Wire remains 38 codes, 142 rows, four records and thirty-three JSON goldens.

### ADR-D4 — Process-independent stage with cleanup-only recovery

Same-filesystem namespace and exact ACTIVE index survive process exit. Every no-token invocation is desired; only the exact hidden-token form is cleanup-retry. The first desired request becomes immutable deferred intent, and tokenized retry, repeat, or third desired command cannot overwrite it. Failure gives tokenized cleanup retry then optional first desired command. Success gives that desired command only. Stage/ACTIVE already-absent states are recovered; no invocation both cleans and mutates lifecycle.

### ADR-D5 — Private owner root and exported reserved tree per purpose

Each purpose receives a private `mkdtemp` owner root and live FD-backed handle. The root is not exported. Exactly one named reserved child is exported. Each downloaded-verification step places API snapshots, raw archives, empty extraction destinations and stdout under one provider-attestation or provider-verification tree; the verifier performs extraction. Owner reserves, spawns, seals, upload-confirms and cleans. Children cannot register or clean. Path/sentinel/nonce/PID is not authority; unknown or policy-invalid entries and owner death preserve and stop.

### ADR-D6 — Exact protected exclusions

Only #392 `report.md` and `.meta.json` are excluded from main equality and are constrained by a separate external exclusion ledger. All other initiatives/artifacts/workbench data remain protected.

### ADR-D7 — Mapping-only #387 report

#387 report carries only schema/rule and twelve mappings; no repository, PR, candidate/head/tree or merge fact. S00 discovers one merged PR from Issue timeline/cross-reference plus PR-head commit-association evidence, verifies head-tree/merge-tree equality and reads report/ledger/collection from the merge tree. No extra #387 commit boundary or report-to-merge identity/tail rule is required.

### ADR-D8 — Exact legacy, uninstall and dogfood

Only clean `0.2.3` migrates. Uninstall is tooling-only and durable. S40/S50 preserve legacy dogfood; S60 commits one complete migration; S70 one complete update; S80 is read-only. Partial projection is never mergeable.

### ADR-D9 — Current gate continuity

S60 repairs current Provider CI references and failure consumers and minimally sends retained Full Regression output to an independent runner-temp workspace. Current PR and main-push gates remain independently GREEN. Final redesign remains S70.

### ADR-D10 — One producer, raw-byte verifier and least privilege

Only Linux build packages once. Every consumer preserves authenticated raw Actions ZIP bytes and verifies them in one live-handle tree. Exact phases close in-progress role-set, compatibility green/canary, terminal canary readback and post-run final API/job/artifact states, including evidence-name nullability. All nine Provider Gate commands have exact argv and outputs. Workflow default permissions are empty and every job has an exact read-only override; structural tests reject any needs/permission/download/verifier drift.

### ADR-D11 — Distinct external two-head identities

Actual compatibility/final SHA/tree/run identities never appear in tracked #392 report. Compatibility and final heads are distinct. S70 creates both tracked heads, with final head removing only the compatibility job. S80 is strictly read-only and reruns all authoritative evidence. Serializer fixtures use distinct identity constants and recomputed child/hash chains.

### ADR-D12 — Stable environment and no-gap context cutover

Qualification binds `specdock-linux-qualification-v1`. Human requires new while old remains, proves new RED/old GREEN blocking, restores GREEN, removes old, then creates/finally validates the distinct final head.

### ADR-D13 — Measured append-only closure with bounded post-sync recovery

After tree equality, current issue finish closes #392 before clear/post-sync. A post-sync-only failure triggers exact active restoration and already-closed retry, maximum three finish attempts. Active restoration is proven by the current active-set exit/output and active-show readback; active-set has no post-sync value. The original close event remains unique; the accepted payload records every attempt/restore and the final successful interval. No redundant #392 close command. Post/Epic comments and receipts remain append-only and fact-after-observation.

### ADR-D14 — Documentation and human gates

S60 updates lifecycle docs and AGENTS lifecycle text; S70 updates final test policy. Tracked report ends before head freeze. Human-only merge/settings remain.

## Rejected alternatives

- Additional research, decision, test-only or verification-only Issues.
- Candidate/head/tree or PR identity in #387 report.
- Extra #387 commit boundary or report-to-merge identity/tail rule.
- Aggregate external temp root or cleanup from a serializable path.
- Old terminal tuple permanently blocking a later operation.
- Null retry for a cleanup warning or terminal cleanup failure.
- Compatibility job that verifies evidence names but not candidate/evidence/API bytes.
- Same fixture identity for compatibility and final heads.
- Post-merge payload created before finish/close facts exist.
- S40/S50/S70 merge, partial dogfood, multiple packagers, local final build, skip/ledger approval or old-engine fallback.

- Using old cleanup retry as an implicit desired command.
- Exporting owner root or deriving cleanup authority from a reserved path.
- Verifying extracted files without authenticated raw archive bytes or exact job permissions.
- Creating closure after a post-sync-failed finish without successful bounded recovery.
## Consequences

Implementation has explicit recovery/evidence code and a temporary compatibility head, but each main point is releasable and every continuation, reserved-tree workspace, raw archive/permission graph, #387 admission, context transition and recovered closure event is reproducible. `owner_decisions_required=[]`.
