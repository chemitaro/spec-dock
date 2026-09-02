---
種別: 実装計画書（Issue）
ID: "iss-00395"
タイトル: "Regression Baseline Terminalization and Product Defect Repair"
関連GitHub: ["#395"]
状態: "draft"
最終更新: "2026-09-02"
依存:
  - "requirement.md"
  - "design.md"
  - "iss-00392"
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

# iss-00395 Regression Baseline Terminalization and Product Defect Repair — 実装計画

## 1. Current planning state

This Plan fixes acceptance and sequencing relative to #392/#396. It does not specify repair files、symbols、test implementations、commands or step order. #395 must not start until B1 exists and an implementation-ready replacement passes Strict review。

## 2. Entry gate

Entry requires #392 human-merged、B1 GREEN、exact 15/14/1 register、current policy operational、lifecycle conformance unchanged、protected/dogfood evidence accepted and no concurrent writer。

## 3. Required Issue outcome

One Issue PR repairs all 14 active Product behaviors and proves zero active/approved failures under the current policy. Repairs may be internally staged, but partial row subsets are not mergeable or closable。

## 4. Evidence owned by this Issue

- exact baseline admission;
- individual row RED/GREEN and accepted Product behavior;
- no masking or new approved row;
- current evaluator and timing/collection coherence;
- ordinary and exact current full gate GREEN;
- lifecycle、dogfood and protected-data non-regression;
- B2 merged-tip GREEN readback。

## 5. Handoff and merge gate

Implementation-ready elaboration defines cause grouping、owned/no-touch surfaces、tests、commands and order. Merge readiness requires every active row resolved、no unexpected failure、independent Strict review、human PR review and whole-merge rollback record. Human merges to the Epic branch only。

## 6. Rollback / recovery

Before #396 starts, human whole-merge revert restores B1 and the 14-active known baseline. If #396 elaboration has started but not merged, discard it before revert. No row-by-row rollback that leaves policy state inconsistent is allowed。

## 7. Stop / return

Return to parent for any unknown row、semantic ambiguity requiring new Product decision、wire change、premature policy removal、scope outside register、non-GREEN B1 or non-empty owner decision. Do not create a new Issue or select alternate successor。

## 8. Issue-start elaboration gate

The replacement Plan must satisfy the rolling-wave contract and include exact current B1 tip、row-to-cause mapping、production ownership、tests/commands、integrated verification、ledger transition、cleanup and rollback. P0/P1 findings block start。

`owner_decisions_required=[]`.
