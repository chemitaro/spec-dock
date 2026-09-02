---
種別: 設計書（Issue）
ID: "iss-00396"
タイトル: "Build Once Provider Gate and Regression Policy Cutover"
関連GitHub: ["#396"]
状態: "draft"
最終更新: "2026-09-02"
依存:
  - "requirement.md"
  - "iss-00395"
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

# iss-00396 Build Once Provider Gate and Regression Policy Cutover — 設計

## 1. Design objective

Clean Product baselineを入力に、packaging、test ownership、platform roles、qualification、evidence and required-context governanceを一つのfinal gateへ収束し、old policyをconsumer-firstで撤去する。

## 2. Current / target

| Concern | B2 input | B3 target |
|---|---|---|
| Failures | Active/approved/unexpected 0 | Same Product outcome preserved |
| Packaging | Multiple workflow executions possible | One Linux producer, downstream build 0 |
| Regression policy | Ledger/timing/sharder/skip/current hook present | Old machinery absent |
| Evidence | Transitional logs/artifacts | Actual-byte, source-bound, role-complete evidence |
| Context | Existing provider context | New final context required with no-gap transition |
| Docs/dogfood | Lifecycle final, test policy transitional | Both final and complete |

## 3. Responsibility boundary

#396 owns provider test execution architecture、packaging ownership、platform roles、qualification environment、artifact/evidence verification、old policy consumer/provider removal、required-context transition and final operator guidance。

#396 does not own Product defect repair or lifecycle semantics. A discovered Product failure stops admission rather than becoming a policy exception。

## 4. Stable interfaces

- Input B2 guarantees zero approved failure under current policy。
- Lifecycle wire and complete `0.2.4` candidate are read-only Product interfaces。
- Output B3 provides the final gate and evidence used by the Epic main merge。
- Human settings/merge are external actors with exact before/after observations。
- The baseline register remains historical parent authority after runtime files are removed。

## 5. Consumer-first transition

The transition has two logical sides within one Issue acceptance:

1. Replacement provider gate、owners、evidence and qualification become observable while old policy still exists。
2. Old consumers are replaced and verified zero; then old providers/data/workflow are removed; final gate is rerun on the resulting source。

Neither side is a separate Issue or mergeable state。

## 6. Compatibility and context

Compatibility is temporary CI coexistence, not Product dual behavior. Old and new required contexts overlap until intentional RED demonstrates the new gate blocks. Only after GREEN recovery may old context be removed. Final evidence belongs to the final source after compatibility-only surface removal。

## 7. Evidence model

Evidence must make source identity、candidate bytes、producer/consumer build counts、role results、environment fingerprint、artifact API state and final context independently inspectable. Filename or claimed hash without actual bytes is insufficient. Exact schemas are rolling-wave details constrained by these stable relations。

## 8. Failure and recovery

- Non-clean B2 blocks start。
- Consumer remaining blocks provider deletion。
- Evidence or environment mismatch invalidates the candidate。
- Context transition ambiguity restores captured settings and blocks merge。
- Whole Issue revert restores B2 current-policy state。
- Product/lifecycle defect returns to parent; #396 does not patch outside scope。

## 9. Testability

Implementation-ready elaboration defines concrete structural tests、role execution、artifact verification、environment qualification、consumer inventory、context readback and final integrated gates. This draft does not select workflow names、symbols、test files or exact commands beyond the stable observable contract。

## 10. Risk controls

| Risk | Control |
|---|---|
| Deleting policy too early | Replacement first, consumer zero, provider deletion last. |
| New gate masks Product failure | Clean B2 admission and no approved/skip escape. |
| Multiple packaging producers | Build count/source/artifact identity evidence. |
| Platform duplication | Explicit canonical vs delta ownership. |
| Context gap | Human no-gap sequence and before/after readback. |
| Irreversible cutover | Whole-merge rollback to B2 and settings restore. |

`owner_decisions_required=[]`.
