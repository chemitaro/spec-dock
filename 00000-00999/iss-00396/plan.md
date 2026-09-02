---
種別: 実装計画書（Issue）
ID: "iss-00396"
タイトル: "Build Once Provider Gate and Regression Policy Cutover"
関連GitHub: ["#396"]
状態: "draft"
最終更新: "2026-09-02"
依存:
  - "requirement.md"
  - "design.md"
  - "iss-00395"
  - "../../plan.md"
  - "../../artifacts/rolling-wave-issue-elaboration-contract.md"
親: ["epic-00384", "init-local-00003"]
Planning Level: "critical-contract-only"
実装開始許可: false
repository_evidence:
  repository: "chemitaro/spec-dock"
  branch: "codex/epic-00384-provider-test-strategy-planning"
  sha: "240e561e94b50250a4a6309452a7fd0fb511458a"
  tree: "181f7eb28da0edff3ca1352edf4cb2ae1f21d433"
---

# iss-00396 Build Once Provider Gate and Regression Policy Cutover — 実装計画

## 1. Current planning state

This Plan defines final-gate acceptance only. It intentionally omits exact workflow structure、files、symbols、schemas、tests、commands and implementation order. #396 cannot start before accepted B2 and a new implementation-ready Strict-reviewed pack。

## 2. Entry gate

Entry requires #395 human-merged、B2 GREEN、15 rows all resolved、active/approved/unexpected 0、current policy coherent、lifecycle conformance unchanged、complete dogfood/protected evidence and no concurrent writer。

## 3. Required Issue outcome

One Issue PR establishes the complete build-once gate and then removes the old policy consumer-first. Compatibility and final-source checkpoints may exist inside the Issue, but no partial state is independently mergeable or accepted。

## 4. Evidence owned by this Issue

- replacement gate structure and execution ownership;
- one producer and downstream build count 0;
- same-candidate role execution;
- qualification environment and metrics;
- authenticated actual-byte evidence;
- old consumer zero before old provider/data/workflow removal;
- required-context no-gap RED/GREEN/readback sequence;
- final docs、dogfood、protection and B3 merged-tip GREEN。

## 5. Handoff and merge gate

Implementation-ready elaboration specifies concrete topology and evidence schemas. Merge readiness requires final source rerun、all old policy machinery absent、new required context effective、independent Strict review、human PR review and whole-merge rollback/settings recovery record. Human merges to the Epic branch only。

## 6. Rollback / recovery

Before final Epic main merge, human whole-merge revert restores B2. Any partially changed branch settings are restored from captured before-state. Partial final workflow/old policy mixtures are never an accepted rollback target。

## 7. Stop / return

Return to parent for non-clean baseline、Product/lifecycle change、consumer-zero failure、evidence/qualification ambiguity、context gap、unrecoverable settings drift、partial dogfood or non-empty owner decision. Do not create a verification Issue or use skip/sharding/hardware as an escape。

## 8. Issue-start elaboration gate

The replacement Plan must satisfy the rolling-wave contract and contain exact B2 tip、workflow/jobs/permissions、artifacts/schemas、tests、commands、consumer-removal ordering、context operations、evidence readback、cleanup and rollback. P0/P1 findings block start。

`owner_decisions_required=[]`.
