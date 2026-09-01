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
  sha: "3c24bae76e86651f958bde7c716c5453fff73e56"
---

# ADR: Single Implementation Unit and Provider Hard Cutover Policy

Normative artifacts are `artifacts/provider-lifecycle-wire-contract.md` and `artifacts/active-failure-disposition-register.md`.

## Context

Epic #384 changes provider ownership, migration, uninstall, dogfood, public wire, failure disposition, operator guidance and CI evidence. Publishing any bridge generation or splitting decisions into research/test-only Issues would create multiple writers and unverifiable merge states. Strict review additionally established that Issue #387's semantic candidate precedes its report-only tail, lifecycle staging must survive process exit without scanning, retained Full Regression must not write repository workbench, protected-report exclusions must be exact, evidence schemas must be fixed now and required-context cutover needs an explicit compatibility and final head.

## Decisions

### ADR-D1 — Single Issue and dependency

GitHub #392 remains the sole implementation-and-verification Issue and starts only after #387 merge/admission. #387 canonical documents are not modified. Human alone merges and changes required contexts.

### ADR-D2 — Three safe main gates

S30, S60 and S80 are the only main gates. S40/S50/S70 are non-main. Main sees old public product after PR-A, complete `0.2.4` with coherent retained current gates after PR-B, and final build-once gate after PR-C. No bridge, runtime toggle, dual writer or automatic old fallback.

### ADR-D3 — Fixed lifecycle, immutable policy and closed wire

Four roots, two slots, one record, bounded fresh bootstrap/seeds. Record includes immutable seed policy and exact resume tuple. The wire artifact's 36 codes, 123 context rows, phase/action/path rules and valid goldens are the only public values.

### ADR-D4 — Persistent process-independent staging

Lifecycle staging lives in same-filesystem sibling namespace `.spec-dock-provider-stages-v1`, bound by namespace/repository sentinels and one `ACTIVE.json`. Tuple-key lookup is deterministic; no repository temp, temp-root scan or arbitrary-stage adoption. ACTIVE state covers allocation, ready stage, cleanup and bootstrap-before-record recovery.

### ADR-D5 — Ephemeral evidence outside repository

Evidence/build/download work uses owner-bound OS-temp directories. Repository `spec-dock/.workbench/**` is fully protected and never output/cleanup authority. S00/S30/S60 and retained main-push workflow pass explicit external `--artifact-dir`.

### ADR-D6 — Exact protected exclusions

Only #392 `report.md` and `.meta.json` are excluded from main protected equality. A separate external ledger limits report to pre-merge evidence content and meta to `updated_at`. All other initiatives/artifacts remain byte/type/mode/link-target protected.

### ADR-D7 — `ISS387-THREE-WAY-V2`

#387 report contains semantic candidate identity and mappings but no PR number or future merge facts. Candidate must be an ancestor of the final PR head. The only tail is report plus optional meta updated-at. S00 discovers exactly one merged PR from GitHub candidate/timeline evidence, verifies tail and final-head/merge tree equality, then applies the register. No fixed post-row count or implementer choice.

### ADR-D8 — Exact legacy, uninstall and dogfood

Only clean `0.2.3` migrates. Uninstall is tooling-only and durable. S40/S50 preserve checked-in legacy dogfood; S60 commits one complete migration; S70 commits one complete update; S80 is read-only. Partial projection is never mergeable.

### ADR-D9 — Current gate continuity

S60 repairs current Provider CI references and failure consumers, leaves final gate redesign to S70, and minimally changes retained Full Regression output to external runner temp. Current PR and main-push gates are independently GREEN.

### ADR-D10 — One frozen-head producer and exact byte graph

Only Linux `provider-build-artifacts` packages final head once. Three consumers build zero. Attestation downloads candidate, four receipts and four role evidence byte files, verifies exact schemas/metadata/hashes and uploads one nine-file evidence artifact. Filename-only assertions do not count.

### ADR-D11 — Stable environment and fixed attestation schemas

Qualification binds `specdock-linux-qualification-v1` and the full pinned fingerprint. Candidate, receipt, role, aggregate, pre-merge, post-merge and Epic closure schemas have exact ordered keys/types/units/canonical bytes and parent-child hashes. `EVIDENCE-FIXTURE-V1` fixes canonical fixture bytes, sizes and SHA-256 values. `emit-attestation` and append-only GitHub comment verification are fixed in Issue Design.

### ADR-D12 — Two-head required-context cutover

`PRC_COMPAT_HEAD` emits both old/new contexts. New is added as required while old remains. A canary makes only new RED and proves blocking. Old is then removed from required settings. `PRC_FINAL_HEAD` removes only compatibility job and reruns all authoritative evidence. Only the final head can merge.

### ADR-D13 — Documentation/evidence closure

S60 updates lifecycle docs and AGENTS lifecycle text; S70 updates final test policy. Tracked #392 report stops before final head evidence. Append-only external attestations hold final/pre/post closure facts. Merge equality is tree equality.

## Rejected alternatives

- Additional research, decision, test-only or verification-only Issues.
- Report PR-number input or candidate-equals-final-head requirement.
- Arbitrary external temp scan, random orphan adoption or repository `.workbench` staging.
- Retained Full Regression default artifact path.
- Broad initiative/artifact exclusion.
- Evidence schemas deferred to implementation or evidence without actual role bytes.
- Removing old required context before new required RED proof.
- Merging compatibility head without final-head evidence rerun.
- S40/S50/S70 merge, partial dogfood, multiple packagers, local final build, skip/ledger approval or old-engine fallback.

## Consequences

Implementation has more explicit filesystem/evidence code and a temporary PR-C compatibility head, but each main point is independently releasable and every recovery, wire, evidence and gate transition is reproducible. `owner_decisions_required=[]`.
