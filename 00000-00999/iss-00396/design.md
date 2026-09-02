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
  role: "authoring-source-provenance"
  repository: "chemitaro/spec-dock"
  branch: "codex/epic-00384-provider-test-strategy-planning"
  sha: "240e561e94b50250a4a6309452a7fd0fb511458a"
  tree: "181f7eb28da0edff3ca1352edf4cb2ae1f21d433"
---

# iss-00396 Build Once Provider Gate and Regression Policy Cutover — 設計

## 1. Design objective

Clean Product baselineを入力に、packaging、test ownership、platform roles、parent `E384-QUAL-001`の実装・測定・証拠化、actual-byte evidence and required-context governanceを一つのfinal gateへ収束し、old policyをconsumer-firstで撤去する。

## 2. Current / target

| Concern | B2 input | B3 target |
|---|---|---|
| Failures | Active/approved/unexpected 0 | Same Product outcome preserved |
| Packaging | Multiple workflow executions possible | `E384-QUAL-001`-conformant build and same-candidate consumption graph |
| Regression policy | Ledger/timing/sharder/skip/current hook present | Old machinery absent |
| Evidence | Transitional logs/artifacts | Actual-byte, source-bound, role-complete evidence |
| Context | Existing provider context | New final context required with no-gap transition |
| Docs/dogfood | Lifecycle final, test policy transitional | Both final and complete |

## 3. Responsibility boundary

#396 owns provider test execution architecture、packaging ownership、platform roles、`E384-QUAL-001` measurement/evaluation/evidence implementation、qualification environment、artifact/evidence verification、old policy consumer/provider removal、required-context transition and final operator guidance。

#396 does not own Product defect repair、lifecycle semantics or qualification policy values/aggregation. A discovered Product failure or an `E384-QUAL-001` semantic ambiguity stops admission rather than becoming a policy exception or local design choice。

## 4. Stable interfaces

- Input B2 guarantees zero approved failure under current policy。
- Lifecycle wire and complete `0.2.4` candidate are read-only Product interfaces。
- Parent `E384-QUAL-001` is the sole qualification policy source and a read-only input to #396。
- Output B3 provides the final gate and complete mechanical `E384-QUAL-001` conformance evidence used by the Epic main merge。
- Human settings/merge are external actors with exact before/after observations。
- The baseline register remains historical parent authority after runtime files are removed。

## 5. Consumer-first transition

The transition has two logical sides within one Issue acceptance:

1. Replacement provider gate、owners、evidence and a mechanical implementation of `E384-QUAL-001` become observable while old policy still exists。
2. Old consumers are replaced and verified zero; then old providers/data/workflow are removed; final gate is rerun on the resulting source。

Neither side is a separate Issue or mergeable state。

## 6. Compatibility and context

Compatibility is temporary CI coexistence, not Product dual behavior. Old and new required contexts overlap until intentional RED demonstrates the new gate blocks. Only after GREEN recovery may old context be removed. Final evidence belongs to the final source after compatibility-only surface removal。

## 7. Evidence model

Evidence must make source identity、candidate bytes、build graph、role results、environment fingerprint、every raw input required by `E384-QUAL-001`、its mechanical per-predicate result、artifact API state and final context independently inspectable. Filename or claimed hash without actual bytes is insufficient. Exact schemas and measurement collectors are rolling-wave details, but they may only encode the parent contract and may not become a second policy source。

## 8. Failure and recovery

- Non-clean B2 blocks start。
- Consumer remaining blocks provider deletion。
- Any `E384-QUAL-001` rejection, incomplete window/raw input, evidence mismatch or environment mismatch invalidates the candidate。
- Context transition ambiguity restores captured settings and blocks merge。
- Whole Issue revert restores B2 current-policy state。
- Product/lifecycle defect returns to parent; #396 does not patch outside scope。

## 9. Testability

Implementation-ready elaboration defines concrete structural tests、role execution、artifact verification、measurement collector、environment verification、`E384-QUAL-001` boundary tests、consumer inventory、context readback and final integrated gates. This draft does not select workflow names、symbols、schema field names、test files or exact commands, and elaboration may not alter parent qualification semantics。

## 10. Risk controls

| Risk | Control |
|---|---|
| Deleting policy too early | Replacement first, consumer zero, provider deletion last. |
| New gate masks Product failure | Clean B2 admission and no approved/skip escape. |
| Qualification policy drift or incomplete evidence | Resolve every decision from `E384-QUAL-001`; reject ambiguity, duplication or missing raw inputs. |
| Multiple packaging producers | Parent-contract conformance plus source/artifact identity evidence. |
| Platform duplication | Explicit canonical vs delta ownership. |
| Context gap | Human no-gap sequence and before/after readback. |
| Irreversible cutover | Whole-merge rollback to B2 and settings restore. |

`owner_decisions_required=[]`.
