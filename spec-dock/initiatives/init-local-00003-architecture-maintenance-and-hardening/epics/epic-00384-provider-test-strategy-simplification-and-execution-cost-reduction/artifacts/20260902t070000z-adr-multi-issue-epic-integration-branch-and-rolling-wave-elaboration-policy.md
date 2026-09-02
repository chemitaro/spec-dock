---
種別: ADR
ID: "20260902t070000z-adr"
タイトル: "Multi-Issue Epic Integration Branch and Rolling-Wave Elaboration Policy"
状態: "accepted"
決定日: "2026-09-02"
最終更新: "2026-09-02"
対象: ["epic-00384", "iss-00392", "iss-00395", "iss-00396"]
supersedes: "20260831t152024z-adr-single-implementation-unit-and-provider-hard-cutover-policy.md"
repository_evidence:
  repository: "chemitaro/spec-dock"
  branch: "codex/epic-00384-provider-test-strategy-planning"
  sha: "240e561e94b50250a4a6309452a7fd0fb511458a"
  tree: "181f7eb28da0edff3ca1352edf4cb2ae1f21d433"
---

# ADR: Multi-Issue Epic Integration Branch and Rolling-Wave Elaboration Policy

## Context

Epic #384 combines three independently observable and independently recoverable changes: provider lifecycle replacement、current Product defect terminalization、provider test-policy/CI replacement。旧ADRはmainへ三回mergeする前提でsingle Issueを選んだが、Epic integration branchへdependency順に統合する構造では、mainのunsafe intermediate stateとparallel writersを回避できる。

Issue #387は既にCLOSEDかつmainへmerge済みである。Issues #392、#395、#396は実在し、依存方向もmetadataで固定済みである。Current regression baselineは27-row future modelではなく、15-row payload、14 active、1 resolved、243 timing nodesである。

## Decision

### ADR-MI-001 — Three implementation Issues

Epic implementation units are exactly:

1. `iss-00392` / #392 — fixed ownership provider lifecycle;
2. `iss-00395` / #395 — 14 active Product defect terminalization;
3. `iss-00396` / #396 — build-once provider gate and regression-policy cutover.

No research、decision、documentation、test-only、verification-only Issue is added。

### ADR-MI-002 — Epic integration branch

`codex/epic-00384-provider-test-strategy-planning` is the sole integration branch. Each Issue PR targets it, is merged by a human in dependency order, and must leave it GREEN. Main receives one final Epic merge only after all Issues are accepted。

### ADR-MI-003 — Single writer by domain

#392 is sole lifecycle writer. #395 is sole active-regression Product repair writer. #396 is sole provider-gate/test-policy writer. Later Issues consume earlier stable outputs read-only and cannot redefine them。

### ADR-MI-004 — Rolling-wave elaboration

Current Issue R/D/P are contract-level drafts. File、symbol、test code、exact command and execution steps are authored only immediately before Issue start against current integration tip. Independent Strict review is mandatory. A stable-contract change returns to parent adjudication rather than being chosen by Luna Max。

### ADR-MI-005 — Re-adopted lifecycle decisions

The following remain accepted: fixed roots/slots/record、immutable seed policy、safe shared-container bootstrap、same-filesystem stage、terminal cleanup continuation、exact clean 0.2.3 migration、tooling-only uninstall、closed public wire、protected consumer data、complete dogfood convergence。

### ADR-MI-006 — Exact regression baseline

Current authority is the 15-row `failure_paths` payload. The 27-count top-level data is frozen historical Issue #368 metadata. #392 preserves 14 active identities; #395 resolves them to normal pass; #396 admits only active/approved zero。

### ADR-MI-007 — Transitional and final gates

Current ledger/timing/sharder/policy machinery remains intact and GREEN through #392 and #395. #396 adds replacement before consumer-first removal, then deletes old machinery in the same Issue acceptance unit。

### ADR-MI-008 — Compatibility and evidence

Required-context changes and all merges are human-only. Dynamic head/run/artifact/merge facts are external evidence. Tracked specifications define schemas、ordering、acceptance and recovery only。

### ADR-MI-009 — Rollback and recovery

Issue merge is the integration rollback unit. Before the next Issue starts, a whole merge may be reverted. After dependency work starts, unmerged work is discarded and accepted suffixes are reverted in reverse order or repaired within the current owned boundary. Partial writer rollback and automatic old fallback are forbidden。

### ADR-MI-010 — Historical material

Old single-Issue ADR/HTML/guides and CLOSED #388〜#390 remain historical evidence and are not deleted. They do not authorize implementation or override this ADR。

## Consequences

- Main observes only the final B3 integration tree。
- Integration branch temporarily contains non-main intermediate states, but every state is GREEN and internally coherent。
- Each Issue has a smaller acceptance and rollback boundary。
- Planning is rolling-wave; start latency includes a mandatory rebaseline and Strict review。
- Parent contract maintenance is stricter because stable cross-Issue changes require ADR-level reassessment。

## Rejected alternatives

- Retaining one #392 implementation Issue。
- Main merge after each Issue。
- Parallel Issue implementation against the same branch tip。
- Splitting CI evidence、documentation or verification into additional Issues。
- Deleting transitional policy before #395 reaches active/approved zero。
- Letting #396 fix unknown Product defects or redefine lifecycle behavior。
- Reusing CLOSED #388〜#390。

See [Epic Integration Branch Contract](epic-integration-branch-contract.md) and [Rolling-Wave Issue Elaboration Contract](rolling-wave-issue-elaboration-contract.md). `owner_decisions_required=[]`.
