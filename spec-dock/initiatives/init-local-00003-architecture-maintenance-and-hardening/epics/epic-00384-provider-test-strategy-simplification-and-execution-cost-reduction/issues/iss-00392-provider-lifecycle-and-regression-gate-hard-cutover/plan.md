---
種別: 実装計画書（Issue）
ID: "iss-00392"
タイトル: "Provider Lifecycle And Regression Gate Hard Cutover"
契約名: "Fixed Ownership Provider Lifecycle Hard Cutover"
関連GitHub: ["#392"]
状態: "draft-parent-return"
詳細化状態: "blocked-by-parent-wire"
親差し戻し: ["P392-001", "P392-002"]
最終更新: "2026-09-08"
依存:
  - "requirement.md"
  - "design.md"
  - "../../plan.md"
  - "../../artifacts/rolling-wave-issue-elaboration-contract.md"
親: ["epic-00384", "init-local-00003"]
Planning Level: "critical-contract-only"
実装開始許可: false
repository_evidence:
  role: "issue-elaboration-source-provenance"
  repository: "chemitaro/spec-dock"
  branch: "iss-00392-provider-lifecycle-and-regression-gate-hard-cutover"
  sha: "14a72044738ce698c3113a0ee70f052015e3be8a"
  tree: "af8e50ed3e20e5a03ef1e2a46332142befa1251f"
---

# iss-00392 Provider Lifecycle And Regression Gate Hard Cutover — 実装計画

## 1. Current planning state

本Planはまだcontract-levelであり、実行可能なProduct実装手順ではない。正式start後に詳細化を開始したが、親wireの通常I/O失敗・最初のincomplete record公開失敗が未被覆と判明した。Rolling-Wave Contract §2・§7に従い親へ差し戻す。コーダーの起動、Product変更、旧writer除去、dogfood更新は行わない。

## 2. Entry gate

Entry requires parent G0 accepted、external `PARENT_FREEZE_SHA` and post-pass GitHub Issue projection receipts、integration state B0 GREEN、#387 completion verified、Issue #392 open and formal selection authorized、15/14/1 register exact、legacy candidate exact、current policy operational and no conflicting writer。

## 3. Required Issue outcome

One PR must deliver the complete lifecycle output in Requirement without terminalizing registered behavior failures、replacing regression policy or implementing parent `E384-QUAL-001`. Final qualification remains a preserved read-only parent/#396 contract. Internal checkpoints are permitted during implementation but none is independently acceptable or mergeable。

## 4. Evidence owned by this Issue

- lifecycle and public-wire conformance;
- filesystem and fault recovery, including every Wire §16 shared/exclusive admission, pre-import, writing-helper/parent-death, both-wrapper handoff and ready/incomplete acceptance case;
- same-generation managed checkout, actual-target worktree coordination, entrypoint-last crash safety, reused-path preservation and nonlocking original-target consumer-hook handoff, including existing bootstrap-result compatibility;
- parent-approved legacy migration and resolved existing-branch checkout boundary;
- exact legacy migration and uninstall;
- old-package mutation safety;
- complete dogfood and protected-data proof;
- 14-active-identity preservation;
- current transitional gate GREEN at the candidate and merged integration tip。

## 5. Handoff and merge gate

The implementation-ready Plan will define exact implementation order and commands. Merge readiness at this contract level requires all owned evidence、independent review under Rolling-Wave Contract §5、human PR review、whole-Issue rollback record and no stop condition. Human merges to the Epic branch and revalidates B1 before Issue closure。

## 6. Rollback / recovery

Before #395 start, rollback is a human whole-merge revert to B0. During Issue work, recovery follows only the lifecycle contract; preserve unmerged branch/worktree content until a human decides its disposition. No partial old-writer restore、skip、approved failure or final-gate dependency is accepted。

## 7. Stop / return

Return to parent if current tree requires a stable wire change、baseline identity change、scope crossing into #395/#396、`E384-QUAL-001` implementation or reinterpretation、unsafe compatibility state、non-complete dogfood、or unresolved Product decision. Return evidence must identify exact contract ID and current tip。

## 8. Issue-start elaboration gate

The replacement implementation Plan must satisfy [Rolling-Wave Issue Elaboration Contract](../../artifacts/rolling-wave-issue-elaboration-contract.md), add exact owned/no-touch paths、symbols、tests、commands、RED/GREEN ordering and cleanup, and pass independent review under Rolling-Wave Contract §5 before `implementation_allowed` becomes true。

親の `E384-DEC-001` / `E384-DEC-002` は採用済みのまま維持する。2026-09-08に正式startし、このIssue branchで詳細化を開始した。その結果、通常のstage I/O失敗と最初のincomplete record公開失敗を親wireで表現できない `P392-001/002` を確認した。[調査証拠・親への差し戻し](artifacts/20260908t010201z-issue-392-elaboration-parent-return.md)を参照。

親契約を変更する承認は未取得であり、修正を仮採用しない。過去の `owner_decisions_required=[]` とEpic review passは、今回新しく見つかった不足の解消やIssue実装許可を意味しない。親の修正・独立review・freeze後に詳細化を再開し、完全なR/D/PとLuna Max handoffの独立reviewまで `実装開始許可: false` を維持する。

## 9. 詳細化を再開するためのチェックリスト

以下は仕様作成の残作業であり、実装ステップや別Issueではない。

- [x] 当該Issue branch・base SHA/tree・親固定契約を確認する。
- [x] 現行installer/runtime/testの接点と親契約の不足を調査し、fresh GPT-6 Max reviewerと照合する。
- [ ] 親修正の承認を得て、P392-001/002の状態・結果・retry/fault契約を親ADR/wireで閉じ、独立reviewとfreeze/projection手順を完了する。
- [ ] その固定点に対するexact owned/shared/no-touch file list、module/symbol、private schema、OS Adapter、旧test dispositionをDesignへ定義する。
- [ ] Requirementに受入条件とnegative/fault/concurrency/migration/baseline traceを揃える。
- [ ] 本Planを唯一のcritical-level実装計画へ置換する。各因果的stepに開始状態・編集対象・最初のRED・完了状態・exact command/expected exit・停止条件を定義する。途中単独mergeは不可。
- [ ] Luna Max handoffを生成し、同じIssue reviewerで完全な候補をreviewする。P0/P1=0とpassを確認するまで実装開始許可はfalse。

将来の実装担当は `coder`（GPT-5.6 Luna / Max）、レビュー担当は `gpt-6-astra` / Max。今回の調査結果だけを根拠に実装を委譲しない。
