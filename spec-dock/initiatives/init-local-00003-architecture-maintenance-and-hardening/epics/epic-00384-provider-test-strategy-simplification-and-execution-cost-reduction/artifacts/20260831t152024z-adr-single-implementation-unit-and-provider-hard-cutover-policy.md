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
  sha: "95d7562ca1762e0b2a717912484eba5a5c2377f1"
---

# ADR: Single Implementation Unit and Provider Hard Cutover Policy

Normative artifacts are `artifacts/provider-lifecycle-wire-contract.md` and `artifacts/active-failure-disposition-register.md`.

## Context

Epic #384 changes provider ownership, migration, uninstall, dogfood, public wire, failure disposition, operator guidance and CI evidence. Multiple implementation Issues, an intermediate public generation or ambiguous recovery would create multiple writers and unsafe merge states. Strict review additionally established six corrections: #387 report identity must be removed, ephemeral workspaces must be independent per purpose, terminal stage cleanup must precede later dispatch, compatibility/final identities must stay external and distinct, compatibility verification must consume the same actual bytes/API inputs as S80, and closure must use only measured events in order.

## Decisions

### ADR-D1 — One Issue and dependency

GitHub #392 is the sole implementation-and-verification Issue and starts only after #387 merge/admission. #387 canonical documents are not changed. Human alone merges and changes required contexts.

### ADR-D2 — Three safe main gates

S30, S60 and S80 are the only main gates. S40/S50/S70 are non-main. Main sees old product after PR-A, complete `0.2.4` plus coherent current gates after PR-B, and final build-once gate after PR-C. No bridge, toggle, dual writer or automatic old fallback.

### ADR-D3 — Fixed lifecycle, immutable policy and closed wire

Four roots, two slots, one record, bounded fresh bootstrap/seeds. Record includes immutable seed policy and exact resume tuple. The wire artifact's 38 codes, 136 context rows, phases/actions/order/retries and goldens are the only public values. Present ACTIVE cleanup returns cleanup-only success/failure with actual invocation echo; it never dispatches the new intent in the same invocation.

### ADR-D4 — Process-independent stage with mandatory terminal cleanup

Same-filesystem `.spec-dock-provider-stages-v1`, exact sentinels, repository/tuple keys and one ACTIVE index survive process exit. ACTIVE includes private result family. Before any normal dispatch, durable terminal cleanup is completed or returns `terminal-cleanup-failed` with the old operation retry. Stage/ACTIVE already-absent crash states are explicitly recovered. Successful cleanup releases the repository for any next intent.

### ADR-D5 — One owner-bound workspace per purpose

Each admission/build/witness/full-regression/tripwire/fresh-consumer/API/download/attestation purpose receives its own `mkdtemp` directory and live non-serializable cleanup handle. The owner reserves/seals child trees and stays alive through upload confirmation. No aggregate root, child self-registration, nonce-only or path-only cleanup authority exists. Repository `.workbench` is protected input, never output or cleanup target.

### ADR-D6 — Exact protected exclusions

Only #392 `report.md` and `.meta.json` are excluded from main equality and are constrained by a separate external exclusion ledger. All other initiatives/artifacts/workbench data remain protected.

### ADR-D7 — Mapping-only #387 report

#387 report carries only schema/rule and twelve mappings; no repository, PR, candidate/head/tree or merge fact. S00 discovers one merged PR from Issue timeline/cross-reference plus PR-head commit-association evidence, verifies head-tree/merge-tree equality and reads report/ledger/collection from the merge tree. No extra #387 commit boundary or report-to-merge identity/tail rule is required.

### ADR-D8 — Exact legacy, uninstall and dogfood

Only clean `0.2.3` migrates. Uninstall is tooling-only and durable. S40/S50 preserve legacy dogfood; S60 commits one complete migration; S70 one complete update; S80 is read-only. Partial projection is never mergeable.

### ADR-D9 — Current gate continuity

S60 repairs current Provider CI references and failure consumers and minimally sends retained Full Regression output to an independent runner-temp workspace. Current PR and main-push gates remain independently GREEN. Final redesign remains S70.

### ADR-D10 — One producer and same verifier

Only Linux build job packages each workflow head once. Three consumers build zero. Provider attestation verifies actual candidate/receipt/role/API bytes and uploads one nine-file evidence artifact. Compatibility `provider-tests` needs producer plus attestation, downloads candidate/evidence/API bytes and invokes the exact S80 verifier interface; no package build and no canary dependency.

### ADR-D11 — Distinct external two-head identities

Actual compatibility/final SHA/tree/run identities never appear in tracked #392 report. Compatibility and final heads are distinct. S70 creates both tracked heads, with final head removing only the compatibility job. S80 is strictly read-only and reruns all authoritative evidence. Serializer fixtures use distinct identity constants and recomputed child/hash chains.

### ADR-D12 — Stable environment and no-gap context cutover

Qualification binds `specdock-linux-qualification-v1`. Human requires new while old remains, proves new RED/old GREEN blocking, restores GREEN, removes old, then creates/finally validates the distinct final head.

### ADR-D13 — Measured append-only closure

Pre-merge comment is posted to #392 before merge. After merge, tree equality is measured, then current `issue finish` performs the #392 close before active clear/post-sync. Its returned close snapshot is bound to immediate timeline readback; no redundant `close --id iss-00392` is run. Only then is post-merge payload posted to #392. Epic acceptance is then measured, #384 is closed/read back, and Epic payload is posted to #384. Payloads omit their own future comment identity; external `comment-receipt-v1` objects bind each observed comment.

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

## Consequences

Implementation has explicit recovery/evidence code and a temporary compatibility head, but each main point is releasable and every wire, workspace, #387 admission, artifact byte, context transition and closure event is reproducible. `owner_decisions_required=[]`.
