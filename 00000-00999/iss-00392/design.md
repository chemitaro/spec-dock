---
種別: 設計書（Issue）
ID: "iss-00392"
タイトル: "Provider Lifecycle And Regression Gate Hard Cutover"
契約名: "Fixed Ownership Provider Lifecycle Hard Cutover"
関連GitHub: ["#392"]
状態: "draft"
最終更新: "2026-09-02"
依存:
  - "requirement.md"
  - "../../design.md"
  - "../../artifacts/provider-lifecycle-wire-contract.md"
  - "../../artifacts/active-failure-disposition-register.md"
親: ["epic-00384", "init-local-00003"]
実装開始許可: false
repository_evidence:
  repository: "chemitaro/spec-dock"
  branch: "codex/epic-00384-provider-test-strategy-planning"
  sha: "240e561e94b50250a4a6309452a7fd0fb511458a"
  tree: "181f7eb28da0edff3ca1352edf4cb2ae1f21d433"
---

# iss-00392 Provider Lifecycle And Regression Gate Hard Cutover — 設計

## 1. Design objective

Lifecycle state、mutation authority、public wire、filesystem recovery、migration and dogfoodを一つのProduct boundaryに置き、regression repairとprovider-gate policyを別writerへ分離する。

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

#392 owns state classification、candidate ownership、record/marker behavior、safe publication、migration、uninstall、public lifecycle output、lifecycle documentation and complete dogfood convergence。

#392 does not own the semantics represented by the 14 active baseline failures, their Product repair, test-policy architecture, final workflow/evidence/qualification or required-context transition。

## 4. Stable interfaces

- Parent lifecycle wire is input and cannot be edited semantically。
- The output lifecycle is consumed read-only by #395 and #396。
- The regression baseline is read-only input except the resolved row's behavior-preserving referential rebind if old lifecycle test identity disappears。
- Current gate remains the compatibility verifier at B1。
- Protected-data contract applies before、during and after candidate publication。

## 5. Dependency direction

```text
completed #387 + parent B0
  -> #392 lifecycle output B1
  -> #395 Product repair
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

At Issue start, current repository topology determines concrete modules、symbols、fixtures、commands and step ordering. Elaboration may decompose internals but may not add a bridge generation、change wire、terminalize active rows or introduce final-gate tooling as an acceptance dependency。

## 10. Risk controls

| Risk | Control |
|---|---|
| Scope grows back to single Issue | #395/#396 boundaries are explicit non-goals. |
| Lifecycle change masks active failures | Exact identities/signatures are compared before and after. |
| Partial dogfood | Candidate-changing output is atomic at Issue acceptance. |
| Current policy breaks after old test removal | Referential integrity is part of B1 GREEN. |
| Unsafe recovery | Wire and parent filesystem contracts are immutable. |

`owner_decisions_required=[]`.
