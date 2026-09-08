---
種別: 設計書（Issue）
ID: "iss-00395"
タイトル: "Regression Baseline Terminalization and Product Defect Repair"
関連GitHub: ["#395"]
状態: "draft"
最終更新: "2026-09-08"
依存:
  - "requirement.md"
  - "iss-00392"
  - "../../design.md"
  - "../../artifacts/active-failure-disposition-register.md"
  - "../../artifacts/provider-lifecycle-wire-contract.md"
親: ["epic-00384", "init-local-00003"]
実装開始許可: false
repository_evidence:
  role: "authoring-source-provenance"
  repository: "chemitaro/spec-dock"
  branch: "codex/epic-00384-provider-test-strategy-planning"
  sha: "240e561e94b50250a4a6309452a7fd0fb511458a"
  tree: "181f7eb28da0edff3ca1352edf4cb2ae1f21d433"
---

# iss-00395 Regression Baseline Terminalization and Product Defect Repair — 設計

## 1. Design objective

Regression debtを原因に対応して修復する。現行contractに追随しないtest harnessとProductの責務混線を区別し、test-policy例外に依存しないclean baselineをcurrent verifier上で先に成立させる。

## 2. Current / target

| Concern | B1 input | B2 target |
|---|---|---|
| Rows | 15 total, 14 active, 1 resolved | 15 total, 0 active, 15 resolved |
| Product | Accepted failure signatures remain | All accepted behaviors normal pass |
| Policy | Current approval/shard system present | Same system, approved count 0 |
| Lifecycle | Final #392 output | Read-only, unchanged |
| Final gate | Not present | Still not present; owned by #396 |

## 3. Responsibility model

The register provides identity、signature、behavior and terminalization mode. Issue #395 owns only production behavior and faithful test harness/observers needed for the 14 active rows as adjudicated in register §6.1 and the minimal current-policy data needed to represent their resolved state. It does not own policy architecture or lifecycle semantics。

## 4. Stable input/output interface

Input is accepted B1 tree plus exact register. Output is a clean current-policy baseline consumed by #396. Parent `E384-QUAL-001` remains a read-only future-gate contract and is not implemented or reinterpreted here. A row is resolved only when the canonical observation is normal pass and current evaluator agrees. Ledger text alone cannot create resolution truth。

### 今確定したProduct境界

- Credential-bearing originのread-only repo identity解析をpublication endpoint policyと分離する。publicationのuserinfo拒否、fetch/push整合、same-repo照合、secret非露出は弱めない。
- CLIからdomain catalogueへの直接依存をapplication contract経由へ戻す。catalogueの複製や旧typeの復活はしない。
- 12件のtest側は廃止active引数の除去と現行descriptor-bound scaffolderへの追随で観測を正常化する。期待するProduct behaviorと保護条件は変えない。

## 5. Repair isolation

Rolling-wave elaboration groups rows only when one diagnosed cause and one observable contract correction actually own them. Grouping by file、layer、developer or test location alone is invalid. Every group retains trace to individual register rows。

## 6. Compatibility

- Current CLI and lifecycle behavior remain compatible with B1。
- Current PR and full verifier remain the acceptance mechanism。
- Timing/sharding may be referentially updated for repaired nodes but not redesigned。
- #396 receives zero-approved-failure input and no unresolved Product choice; #396 alone later implements/evidences parent `E384-QUAL-001`。

## 7. Failure and recovery

- Signature or identity mismatch before repair blocks the Issue。
- A fix causing another registered behavior regression is not accepted。
- A row passing only through skip/xfail/policy exception remains unresolved。
- Branch rollback reverts complete #395 merge to B1。
- Cross-Issue contract change returns to parent。

## 8. Testability

Implementation-ready elaboration defines exact production observers、representative REDs、focused Product tests、register evaluator checks、ordinary/full integrated gates and protection evidence. This draft intentionally does not name concrete files、symbols or commands and does not select qualification values or mechanisms。

## 9. Risk controls

| Risk | Control |
|---|---|
| Treating stale 27 metadata as current | Current count derives only from exact 15-row payload. |
| Hiding a defect or regressing Product to obsolete tests | Use the adjudicated repair surface and prove the unchanged accepted behavior with a faithful observer. |
| Coupling to #396 | Current policy is sufficient and mandatory. |
| Broad refactor | Row ownership and non-goals constrain scope. |
| Hidden lifecycle drift | Wire/read-only conformance is rechecked. |

Issue固有の追加判断はない。親の `E384-DEC-001` / `E384-DEC-002` はユーザー採用済みで、`owner_decisions_required=[]` である。親G0の独立review・公開freeze/projectionと当該Issueの依存条件を満たして正式startし、詳細化・独立review後にだけProduct実装を許可する。#392の開始依頼は2026-09-08に受領済みである。

Wire §16のbootstrap bytes、runtime/lifecycle admissionとlease/handoff契約はread-onlyである。Candidate変更時も#392受入時のbootstrap identityを保持し、別の互換機構や運用例外を発明しない。
