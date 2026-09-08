---
種別: 設計書（Issue）
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
  - "../../design.md"
  - "../../artifacts/provider-lifecycle-wire-contract.md"
  - "../../artifacts/active-failure-disposition-register.md"
親: ["epic-00384", "init-local-00003"]
実装開始許可: false
repository_evidence:
  role: "issue-elaboration-source-provenance"
  repository: "chemitaro/spec-dock"
  branch: "iss-00392-provider-lifecycle-and-regression-gate-hard-cutover"
  sha: "14a72044738ce698c3113a0ee70f052015e3be8a"
  tree: "af8e50ed3e20e5a03ef1e2a46332142befa1251f"
---

# iss-00392 Provider Lifecycle And Regression Gate Hard Cutover — 設計

## 1. Design objective

Lifecycle state、mutation authority、public wire、filesystem recovery、migration and dogfoodを一つのProduct boundaryに置き、regression repairとprovider-gate policyを別writerへ分離する。

**詳細設計は未完了。** 現行sourceとの照合で親wireの不足が確定したため、closed result/schemaや復旧手順をコーダーの裁量で補わない。[調査証拠](artifacts/20260908t010201z-issue-392-elaboration-parent-return.md) §5〜§6に実在する編集接点と未採用のmodule/handoff案を保存した。これらは親修正後の詳細化入力であり、実装指示ではない。

## 2. Current / target

| Concern | Current B0 | Target B1 |
|---|---|---|
| Lifecycle writer | Historical per-file/managed distribution model | One fixed-ownership lifecycle writer |
| Record | Plain `0.2.3` legacy marker | Strict seven-key `0.2.4` state record |
| Resume | Historical journal/recovery | Exact operation/candidate/seed-policy identity |
| Uninstall | Historical purge-capable surface | Tooling-only durable absent state |
| Wire | Parent accepted finite contract | Production and public output exactly conformant |
| Dogfood | Exact legacy projection | Complete final lifecycle candidate |
| Regression system | 15-row transitional policy | Retained unchanged except lifecycle referential integrity |

## 3. Responsibility boundary

#392 additionally owns E384-RQ-019 and Wire §16: repository-root SH/EX admission, immutable pre-import bootstrap, update/uninstall release→exec handoff, parent-death-safe writing-helper lifetime, and external-only incomplete recovery. The replaceable create lock may remain only as inner create serialization. One-time legacy maintenance E384-DEC-001 is user-adopted; existing-branch checkout E384-DEC-002 is also user-adopted. Worktree creation/removal must coordinate the actual target root through managed publication/removal and cleanup; consumer-owned make hooks cross an explicit terminal external-handoff boundary.

#392 owns state classification、candidate ownership、record/marker behavior、safe publication、migration、uninstall、public lifecycle output、lifecycle documentation and complete dogfood convergence。

#392 does not own the semantics represented by the 14 active baseline failures, their Product/test repair, test-policy architecture, final workflow/evidence, parent `E384-QUAL-001` implementation or required-context transition。

## 4. Stable interfaces

- Parent lifecycle wire is input and cannot be edited semantically。
- The output lifecycle is consumed read-only by #395 and #396。
- The regression baseline is read-only input except the resolved row's behavior-preserving referential rebind if old lifecycle test identity disappears。
- Current gate remains the compatibility verifier at B1。
- Parent `E384-QUAL-001` is a preserved, read-only future-gate interface; #392 neither implements nor redefines it。
- Protected-data contract applies before、during and after candidate publication。

## 5. Dependency direction

```text
completed #387 + parent B0
  -> #392 lifecycle output B1
  -> #395 regression contract recovery
  -> #396 gate cutover
```

No import or runtime dependency on #395/#396 implementation is permitted。

## 6. Compatibility

Public compatibility is governed by the wire and accepted aliases/errors. Current regression-policy compatibility is preserved as an integration property, not a runtime toggle. Main does not consume B1 directly。

## 7. Failure and recovery

- Pre-mutation invalidity blocks with closed result。
- Durable partial state accepts only exact contract recovery。
- Unknown identity or protected-data drift preserves and stops。
- Post-merge regression outside known baseline blocks B1 acceptance。
- Branch rollback reverts the whole #392 merge before #395 start。

## 8. Testability

The implementation-ready elaboration must create observable tests for model/wire、filesystem/fault、CLI/public output、built artifact/migration、platform atomic behavior、dogfood/protection and current-gate non-regression。This draft does not choose test files or test code。

## 9. Elaboration boundary

At Issue start, current repository topology determines concrete modules、symbols、fixtures、commands and step ordering. Elaboration may decompose internals but may not add a bridge generation、change wire、terminalize active rows、implement/redefine `E384-QUAL-001` or introduce final-gate tooling as an acceptance dependency。

## 10. Risk controls

| Risk | Control |
|---|---|
| Scope grows back to single Issue | #395/#396 boundaries are explicit non-goals. |
| Lifecycle change masks active failures | Exact identities/signatures are compared before and after. |
| Partial dogfood | Candidate-changing output is atomic at Issue acceptance. |
| Current policy breaks after old test removal | Referential integrity is part of B1 GREEN. |
| Unsafe recovery | Wire and parent filesystem contracts are immutable. |

親の `E384-DEC-001` / `E384-DEC-002` は採用済みのまま維持する。2026-09-08に正式startし、このIssue branchで詳細化を開始した。その結果、通常のstage I/O失敗と最初のincomplete record公開失敗を親wireで表現できない `P392-001/002` を確認した。[調査証拠・親への差し戻し](artifacts/20260908t010201z-issue-392-elaboration-parent-return.md)を参照。

親契約を変更する承認は未取得であり、修正を仮採用しない。過去の `owner_decisions_required=[]` とEpic review passは、今回新しく見つかった不足の解消やIssue実装許可を意味しない。親の修正・独立review・freeze後に詳細化を再開し、完全なR/D/PとLuna Max handoffの独立reviewまで `実装開始許可: false` を維持する。
