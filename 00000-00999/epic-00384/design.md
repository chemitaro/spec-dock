---
種別: 設計書（Epic）
ID: "epic-00384"
タイトル: "Provider Test Strategy Simplification and Execution Cost Reduction"
関連GitHub: ["#384"]
状態: "draft"
最終更新: "2026-09-02"
依存:
  - "requirement.md"
  - "artifacts/20260902t070000z-adr-multi-issue-epic-integration-branch-and-rolling-wave-elaboration-policy.md"
  - "artifacts/epic-integration-branch-contract.md"
  - "artifacts/rolling-wave-issue-elaboration-contract.md"
  - "artifacts/provider-lifecycle-wire-contract.md"
  - "artifacts/active-failure-disposition-register.md"
親: ["init-local-00003"]
実装開始許可: false
repository_evidence:
  repository: "chemitaro/spec-dock"
  branch: "codex/epic-00384-provider-test-strategy-planning"
  sha: "240e561e94b50250a4a6309452a7fd0fb511458a"
  tree: "181f7eb28da0edff3ca1352edf4cb2ae1f21d433"
---

# epic-00384 Provider Test Strategy Simplification and Execution Cost Reduction — 設計

## 1. Delivery architecture

```text
post-#387 planning baseline
  -> parent contract freeze
  -> iss-00392 lifecycle PR -> human merge -> GREEN integration state B1
  -> iss-00395 defect PR    -> human merge -> GREEN integration state B2
  -> iss-00396 gate PR      -> human merge -> GREEN integration state B3
  -> final Epic PR          -> one human merge to main -> state B4
```

Issue branches are short-lived writers. The Epic branch is the only integration target. Main is not an Issue-level integration target.

## 2. Stable cross-Issue contracts

### E384-C-001 — Branch topology

The exact integration branch name is `codex/epic-00384-provider-test-strategy-planning`. Each Issue branch starts from its current tip, targets it by PR, and is merged sequentially by a human. The branch contract is detailed in [Epic Integration Branch Contract](artifacts/epic-integration-branch-contract.md).

### E384-C-002 — Dependency direction

Dependency direction is one-way:

```text
iss-00387 (completed predecessor)
  -> iss-00392
  -> iss-00395
  -> iss-00396
  -> Epic main merge
```

A later Issue may consume an earlier output but may not redefine it. An earlier Issue may not import a later Issue's implementation or verification tooling.

### E384-C-003 — Lifecycle wire ownership

[Provider Lifecycle Wire Contract](artifacts/provider-lifecycle-wire-contract.md) is frozen by the parent. Issue #392 is the sole production writer for lifecycle behavior and owns conformance. Issues #395 and #396 are read-only consumers and may neither extend nor reinterpret lifecycle fields, codes, ordering, retry, compatibility or filesystem semantics.

### E384-C-004 — Protected data and dogfood

The fixed provider target set, consumer preservation, private owner-bound workspaces and complete-candidate dogfood rule apply to every Issue. Candidate-changing Issues must converge provider and dogfood completely before merge. #395 may change dogfood only when its Product repair changes shipped candidate bytes.

### E384-C-005 — Regression baseline

[Post-#387 Regression Baseline Register](artifacts/active-failure-disposition-register.md) freezes the current 15 rows. Its `failure_paths` identities are current authority; stale 27-row top-level metadata remains historical context only. #392 preserves the 14 active identities, #395 terminalizes them, and #396 consumes only the clean result.

### E384-C-006 — Transitional gate

The current ledger/timing/sharder/policy system remains a live compatibility provider through #392 and #395. It must be GREEN after both merges. #396 is the sole final-policy writer and removes it only after replacement and consumer-zero proof.

### E384-C-007 — Final provider gate

The final gate uses one Linux packaging producer and zero downstream builds. All roles consume the same candidate identity. Linux canonical, sdist, macOS delta, qualification and evidence are separate observable responsibilities but one Issue acceptance unit.

### E384-C-008 — Compatibility and evidence

Required-context transition has no gap. External dynamic identities are measured after source freeze; tracked documents contain schemas and methods, not future run/head/merge facts. Human is the only writer of branch settings and merge state.

### E384-C-009 — Rollback and recovery

Issue merge is the smallest integration rollback unit. Runtime lifecycle recovery uses the wire contract. Branch rollback uses whole-merge revert or reverse-order suffix revert. CI/settings recovery restores a captured human-readable before-state. No automatic old behavior fallback exists.

### E384-C-010 — Rolling-wave detail

The current Issue designs specify responsibility, inputs, outputs and acceptance boundaries. Implementation structures are intentionally absent. [Rolling-Wave Issue Elaboration Contract](artifacts/rolling-wave-issue-elaboration-contract.md) controls when those details may be introduced.

## 3. Integration states

| State | Source | Required invariant |
|---|---|---|
| B0 | Parent contract freeze on current branch | Three nodes and dependencies exist; #392 not started; baseline 15/14/1 and timing 243 fixed. |
| B1 | #392 merge | Complete final lifecycle and dogfood; old lifecycle writer absent; 14 active identities unchanged; transitional gates GREEN. |
| B2 | #395 merge | 15 resolved, active/approved 0; Product repairs accepted; transitional gates independently GREEN. |
| B3 | #396 merge | Final build-once gate GREEN; old ledger/timing/sharder/policy machinery absent; final docs/dogfood coherent. |
| B4 | Epic main merge | Main tree equals accepted B3 tree; final context and closure evidence read back. |

## 4. Issue responsibility boundaries

| Issue | Sole write authority | Explicit read-only input | Forbidden ownership |
|---|---|---|---|
| #392 | Provider lifecycle semantics, wire conformance, migration/uninstall/recovery, lifecycle docs and candidate | Post-#387 active identities and transitional gate | Product defect terminalization; final gate/policy removal |
| #395 | Product behavior represented by the 14 active rows and their terminal state | #392 lifecycle output, wire, current policy | Lifecycle redesign; final gate/policy removal |
| #396 | Provider test ownership, build-once CI, evidence, qualification, policy cutover and final guidance | Clean #395 baseline and #392 lifecycle | New Product behavior or lifecycle semantic change |

## 5. Compatibility design

- B1 is compatible with the current regression system even though Product lifecycle has changed.
- B2 is a clean baseline under the current regression system.
- B3 replaces that system atomically and preserves Product behavior.
- Compatibility is not a runtime feature toggle. It is an integration-state property.
- No Issue merge is required to be independently deployable to main; it must only be internally coherent and GREEN on the Epic branch.

## 6. Main drift design

Main is inspected only between Issues. Non-overlapping drift may be human-integrated into the Epic branch followed by complete GREEN revalidation. Drift touching a stable contract, owned boundary or acceptance identity blocks the next Issue and returns to parent adjudication. Issue implementers do not silently absorb it.

## 7. Evidence design

Each Issue records four evidence classes without deferring all proof to the final Issue:

1. contract conformance;
2. observable Product or CI outcome;
3. integration-branch GREEN state at exact tip;
4. rollback/recovery readiness.

Final Epic evidence additionally binds the B3 tree, human main merge tree equality and final required-context readback.

## 8. Historical material

Historical research, discussions, HTML guides and CLOSED #388–#390 remain in the repository. They may explain prior reasoning but cannot override current parent R/D/P, accepted multi-Issue ADR or normative contracts. The accepted disposable-root/fixed-slot ADR remains supporting technical authority where it does not conflict with the new ADR.

## 9. Traceability

| Requirement | Design contract |
|---|---|
| E384-RQ-001–003 | C-001, C-002, C-010 |
| E384-RQ-004–006 | C-003, C-004, C-009 |
| E384-RQ-007–011 | C-005, C-006 and B0–B2 |
| E384-RQ-012–014 | C-007, C-008 and B3 |
| E384-RQ-015–018 | C-004, C-008, C-009 and B4 |
