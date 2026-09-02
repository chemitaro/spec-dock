---
種別: 設計書（Issue）
ID: "iss-00395"
タイトル: "Regression Baseline Terminalization and Product Defect Repair"
関連GitHub: ["#395"]
状態: "draft"
最終更新: "2026-09-02"
依存:
  - "requirement.md"
  - "iss-00392"
  - "../../design.md"
  - "../../artifacts/active-failure-disposition-register.md"
  - "../../artifacts/provider-lifecycle-wire-contract.md"
親: ["epic-00384", "init-local-00003"]
実装開始許可: false
repository_evidence:
  repository: "chemitaro/spec-dock"
  branch: "codex/epic-00384-provider-test-strategy-planning"
  sha: "240e561e94b50250a4a6309452a7fd0fb511458a"
  tree: "181f7eb28da0edff3ca1352edf4cb2ae1f21d433"
---

# iss-00395 Regression Baseline Terminalization and Product Defect Repair — 設計

## 1. Design objective

Regression debtをtest-policy cleanupではなくProduct behavior repairとして扱い、clean baselineをcurrent verifier上で先に成立させる。

## 2. Current / target

| Concern | B1 input | B2 target |
|---|---|---|
| Rows | 15 total, 14 active, 1 resolved | 15 total, 0 active, 15 resolved |
| Product | Accepted failure signatures remain | All accepted behaviors normal pass |
| Policy | Current approval/shard system present | Same system, approved count 0 |
| Lifecycle | Final #392 output | Read-only, unchanged |
| Final gate | Not present | Still not present; owned by #396 |

## 3. Responsibility model

The register provides identity、signature、behavior and terminalization mode. Issue #395 owns only production behavior needed for the 14 active rows and the minimal current-policy data needed to represent their resolved state. It does not own policy architecture or lifecycle semantics。

## 4. Stable input/output interface

Input is accepted B1 tree plus exact register. Output is a clean current-policy baseline consumed by #396. A row is resolved only when the canonical observation is normal pass and current evaluator agrees. Ledger text alone cannot create resolution truth。

## 5. Repair isolation

Rolling-wave elaboration groups rows only when one Product cause and one observable correction actually own them. Grouping by file、layer、developer or test location alone is invalid. Every group retains trace to individual register rows。

## 6. Compatibility

- Current CLI and lifecycle behavior remain compatible with B1。
- Current PR and full verifier remain the acceptance mechanism。
- Timing/sharding may be referentially updated for repaired nodes but not redesigned。
- #396 receives zero-approved-failure input and no unresolved Product choice。

## 7. Failure and recovery

- Signature or identity mismatch before repair blocks the Issue。
- A fix causing another registered behavior regression is not accepted。
- A row passing only through skip/xfail/policy exception remains unresolved。
- Branch rollback reverts complete #395 merge to B1。
- Cross-Issue contract change returns to parent。

## 8. Testability

Implementation-ready elaboration defines exact production observers、representative REDs、focused Product tests、register evaluator checks、ordinary/full integrated gates and protection evidence. This draft intentionally does not name concrete files、symbols or commands。

## 9. Risk controls

| Risk | Control |
|---|---|
| Treating stale 27 metadata as current | Current count derives only from exact 15-row payload. |
| Fixing tests rather than Product | Normal pass must be tied to accepted external behavior. |
| Coupling to #396 | Current policy is sufficient and mandatory. |
| Broad refactor | Row ownership and non-goals constrain scope. |
| Hidden lifecycle drift | Wire/read-only conformance is rechecked. |

`owner_decisions_required=[]`.
