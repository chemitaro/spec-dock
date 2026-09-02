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
  role: "authoring-source-provenance"
  repository: "chemitaro/spec-dock"
  branch: "codex/epic-00384-provider-test-strategy-planning"
  sha: "240e561e94b50250a4a6309452a7fd0fb511458a"
  tree: "181f7eb28da0edff3ca1352edf4cb2ae1f21d433"
---

# iss-00396 Build Once Provider Gate and Regression Policy Cutover — 実装計画

## 1. Current planning state

This Plan defines final-gate acceptance only. Parent `E384-QUAL-001` is an immutable input and the sole quantitative/aggregation authority. This Plan intentionally omits exact workflow structure、files、symbols、measurement collector、schemas、tests、commands and implementation order. #396 cannot start before accepted B2 and a new implementation-ready Strict-reviewed pack。

## 2. Entry gate

Entry requires #395 human-merged、B2 GREEN、15 rows all resolved、active/approved/unexpected 0、current policy coherent、lifecycle conformance unchanged、complete dogfood/protected evidence、an accepted external parent-freeze receipt、post-pass GitHub Issue projection readback and no concurrent writer。

## 3. Required Issue outcome

One Issue PR establishes the complete build-once gate and then removes the old policy consumer-first. Compatibility and final-source checkpoints may exist inside the Issue, but no partial state is independently mergeable or accepted。

## 4. Evidence owned by this Issue

- replacement gate structure and execution ownership;
- build and same-candidate role graph conformance to `E384-QUAL-001`;
- every raw qualification input and the mechanical per-predicate `E384-QUAL-001` result;
- qualification environment identity and fingerprint evidence;
- authenticated actual-byte evidence;
- old consumer zero before old provider/data/workflow removal;
- required-context no-gap RED/GREEN/readback sequence;
- final docs、dogfood、protection and B3 merged-tip GREEN。

## 5. Handoff and merge gate

Implementation-ready elaboration specifies concrete topology、measurement implementation and evidence schemas without changing `E384-QUAL-001`. Merge readiness requires complete parent-contract evidence on the final source、all old policy machinery absent、new required context effective、independent Strict review、human PR review and whole-merge rollback/settings recovery record. Human merges to the Epic branch only。

## 6. Rollback / recovery

Before final Epic main merge, human whole-merge revert restores B2. Any partially changed branch settings are restored from captured before-state. Partial final workflow/old policy mixtures are never an accepted rollback target。

## 7. Stop / return

Return to parent for non-clean baseline、Product/lifecycle change、consumer-zero failure、`E384-QUAL-001` ambiguity/duplication/non-conformance/incomplete evidence、context gap、unrecoverable settings drift、partial dogfood or non-empty owner decision. Do not create a verification Issue、invent a qualification policy or use a parent-prohibited escape。

## 8. Issue-start elaboration gate

The replacement Plan must satisfy the rolling-wave contract and contain exact B2 tip、workflow/jobs/permissions、measurement collector、artifacts/schemas、boundary tests、commands、consumer-removal ordering、context operations、`E384-QUAL-001` raw evidence/readback、cleanup and rollback. It must demonstrate that all policy values and aggregation are references to the parent contract rather than independently managed literals. P0/P1 findings block start。

`owner_decisions_required=[]`.
