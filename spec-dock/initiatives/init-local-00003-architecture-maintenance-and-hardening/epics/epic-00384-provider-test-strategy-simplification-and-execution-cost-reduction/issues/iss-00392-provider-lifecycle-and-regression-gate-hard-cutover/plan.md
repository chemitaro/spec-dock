---
種別: 実装計画書（Issue）
ID: "iss-00392"
タイトル: "Provider Lifecycle And Regression Gate Hard Cutover"
契約名: "Fixed Ownership Provider Lifecycle Hard Cutover"
関連GitHub: ["#392"]
状態: "draft"
最終更新: "2026-09-02"
依存:
  - "requirement.md"
  - "design.md"
  - "../../plan.md"
  - "../../artifacts/rolling-wave-issue-elaboration-contract.md"
親: ["epic-00384", "init-local-00003"]
Planning Level: "critical-contract-only"
実装開始許可: false
repository_evidence:
  role: "authoring-source-provenance"
  repository: "chemitaro/spec-dock"
  branch: "codex/epic-00384-provider-test-strategy-planning"
  sha: "240e561e94b50250a4a6309452a7fd0fb511458a"
  tree: "181f7eb28da0edff3ca1352edf4cb2ae1f21d433"
---

# iss-00392 Provider Lifecycle And Regression Gate Hard Cutover — 実装計画

## 1. Current planning state

This Plan is a rolling-wave contract, not an implementation procedure. It contains no exact file/symbol/test/command sequence. Issue #392 must not start until a current-tip implementation-ready replacement is generated and Strict-reviewed。

## 2. Entry gate

Entry requires parent G0 accepted、external `PARENT_FREEZE_SHA` and post-pass GitHub Issue projection receipts、integration state B0 GREEN、#387 completion verified、Issue #392 open/not-started、15/14/1 register exact、legacy candidate exact、current policy operational and no conflicting writer。

## 3. Required Issue outcome

One PR must deliver the complete lifecycle output in Requirement without terminalizing Product failures、replacing regression policy or implementing parent `E384-QUAL-001`. Final qualification remains a preserved read-only parent/#396 contract. Internal checkpoints are permitted during implementation but none is independently acceptable or mergeable。

## 4. Evidence owned by this Issue

- lifecycle and public-wire conformance;
- filesystem and fault recovery;
- exact legacy migration and uninstall;
- old-package mutation safety;
- complete dogfood and protected-data proof;
- 14-active-identity preservation;
- current transitional gate GREEN at the candidate and merged integration tip。

## 5. Handoff and merge gate

The implementation-ready Plan will define exact implementation order and commands. Merge readiness at this contract level requires all owned evidence、independent Strict review、human PR review、whole-Issue rollback record and no stop condition. Human merges to the Epic branch and revalidates B1 before Issue closure。

## 6. Rollback / recovery

Before #395 start, rollback is a human whole-merge revert to B0. During Issue work, recovery follows only the lifecycle contract or discards the unmerged branch. No partial old-writer restore、skip、approved failure or final-gate dependency is accepted。

## 7. Stop / return

Return to parent if current tree requires a stable wire change、baseline identity change、scope crossing into #395/#396、`E384-QUAL-001` implementation or reinterpretation、unsafe compatibility state、non-complete dogfood、or unresolved Product decision. Return evidence must identify exact contract ID and current tip。

## 8. Issue-start elaboration gate

The replacement implementation Plan must satisfy [Rolling-Wave Issue Elaboration Contract](../../artifacts/rolling-wave-issue-elaboration-contract.md), add exact owned/no-touch paths、symbols、tests、commands、RED/GREEN ordering and cleanup, and pass independent Strict review before `implementation_allowed` becomes true。

`owner_decisions_required=[]`.
