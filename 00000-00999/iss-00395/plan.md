---
種別: 実装計画書（Issue）
ID: "iss-00395"
タイトル: "Regression Baseline Terminalization and Product Defect Repair"
関連GitHub: ["#395"]
状態: "draft"
最終更新: "2026-09-14"
依存:
  - "requirement.md"
  - "design.md"
  - "../../artifacts/20260913t144152z-adr-issue-392-provisional-merge-and-deferred-b1.md"
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

# iss-00395 Regression Baseline Terminalization and Product Defect Repair — 実装計画

## 1. Current planning state

This Plan fixes acceptance and sequencing relative to #392/#396. It does not specify repair files、symbols、test implementations、commands or step order. #395 must start from the exact human-merged P392 tip, then wait for implementation-ready elaboration to pass independent review under Rolling-Wave Contract §5 before Product implementation。

## 2. Entry gate

Entry requires #392 human-merged as P392、the exact merged SHA、a P392 witness that all required checks and #392-owned acceptance checks are GREEN、a fresh full-verifier result limited to #395-owned active rows at that exact tip、exact 15/14/1 register、current policy operational、lifecycle conformance unchanged、protected/dogfood evidence accepted、parent `E384-QUAL-001` preserved as non-owned and no concurrent writer. The metadata `ready` indicator alone is not start authority. #392 issue closure and B1 are not entry requirements。

## 3. Required Issue outcome

One Issue PR restores all 14 accepted behavior contracts through their adjudicated Product/test repair surfaces and proves zero active/approved failures under the current policy. Repairs may be internally staged, but partial row subsets are not mergeable or closable。

## 4. Evidence owned by this Issue

- exact baseline admission;
- individual row RED/GREEN, faithful observer and accepted behavior;
- no masking or new approved row;
- current evaluator and timing/collection coherence;
- ordinary and exact current full gate GREEN;
- lifecycle、dogfood and protected-data non-regression;
- Same-tip post-merge B1 (current gates GREEN) and B2 (15/0/15) readback。

## 5. Handoff and merge gate

Implementation-ready elaboration defines cause grouping、owned/no-touch surfaces、tests、commands and order. Merge readiness requires every active row resolved、no unexpected failure、independent review under Rolling-Wave Contract §5、human PR review and whole-merge rollback record. Human merges to the Epic branch only。

## 6. Rollback / recovery

Before #396 starts, human whole-merge revert restores P392 and the 14-active known baseline. If #396 elaboration has started but not merged, stop and preserve it for a human disposition decision before revert. No row-by-row rollback that leaves policy state inconsistent is allowed。

## 7. Stop / return

Return to parent for any unknown row、semantic ambiguity requiring new Product decision、wire change、premature policy removal、`E384-QUAL-001` implementation/redefinition、scope outside register、P392 SHA mismatch or full-verifier failure outside the measured #395-owned row set、or non-empty owner decision. Do not create a new Issue or select alternate successor。

## 8. Issue-start elaboration gate

The replacement Plan must satisfy the rolling-wave contract and include exact P392 tip、row-to-cause mapping、Product/test ownership、tests/commands、integrated verification、ledger transition、cleanup and rollback. P0/P1 findings block Product implementation。

Issue固有の追加判断はない。親の `E384-DEC-001` / `E384-DEC-002` とP392 sequence ADRはユーザー採用済みで、`owner_decisions_required=[]` である。親G0の独立review・公開freeze/projection後、#392がhuman-merged P392になったexact SHAを入口として正式startする。#392 Issue closureを待たず、#395自身の詳細化・独立review後にだけProduct実装を許可する。
