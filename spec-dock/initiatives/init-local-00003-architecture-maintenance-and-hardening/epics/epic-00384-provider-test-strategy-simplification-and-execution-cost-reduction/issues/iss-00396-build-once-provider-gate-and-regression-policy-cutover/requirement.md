---
種別: 要件定義書（Issue）
ID: "iss-00396"
タイトル: "Build Once Provider Gate and Regression Policy Cutover"
関連GitHub: ["#396"]
状態: "draft"
最終更新: "2026-09-02"
依存:
  - "iss-00395"
  - "../../requirement.md"
  - "../../design.md"
  - "../../plan.md"
  - "../../artifacts/active-failure-disposition-register.md"
  - "../../artifacts/provider-lifecycle-wire-contract.md"
  - "../../artifacts/epic-integration-branch-contract.md"
  - "../../artifacts/rolling-wave-issue-elaboration-contract.md"
親: ["epic-00384", "init-local-00003"]
実装開始許可: false
repository_evidence:
  role: "authoring-source-provenance"
  repository: "chemitaro/spec-dock"
  branch: "codex/epic-00384-provider-test-strategy-planning"
  sha: "240e561e94b50250a4a6309452a7fd0fb511458a"
  tree: "181f7eb28da0edff3ca1352edf4cb2ae1f21d433"
---

# iss-00396 Build Once Provider Gate and Regression Policy Cutover — 要件定義

Parent: [Epic Requirement](../../requirement.md) / [E384-QUAL-001](../../requirement.md) / [Integration Contract](../../artifacts/epic-integration-branch-contract.md)

## 1. Observable outcome

Accepted B2 clean baseline上で、Provider CIがparent `E384-QUAL-001`へ適合するbuild-once gateへcutoverされる。Linux canonical、sdist smoke、macOS delta、qualification evidence、actual-byte evidence、new required contextが成立し、old ledger、243-node timing、sharder、policy skip machinery、policy hook、quality providers、main-push Full Regressionはconsumer-firstで撤去される。

## 2. Goal

- Duplicate packagingとduplicate contract executionを除去する。
- Final provider gateをactual source/tree/artifact bytesへ束縛する。
- Linux canonical execution、platform delta、`E384-QUAL-001`の実装・測定・証拠化をclosed ownershipへ収束する。
- Zero-failure baselineの後でold policyをatomicに除去する。
- Final operator guidance、dogfood and required contextsを一致させる。

## 3. Non-goals

- New lifecycle semantics、wire values、migration/uninstall behavior。
- B2に残る未知Product defectの修正またはapproved failure追加。
- Additional CI-only、evidence-only、verification-only Issue。
- MainへのIssue-level direct merge。
- Parent `E384-QUAL-001`の値、population、window、aggregation、platform scope、rejectionまたはescape prohibitionを変更・再定義すること。

## 4. Stable input

| Input | Required state |
|---|---|
| Dependency | #395 human-merged and B2 GREEN |
| Product | #392 lifecycle output and #395 repaired behavior, read-only |
| Regression | 15 rows all resolved; active/approved/unexpected 0 |
| Transitional policy | Present and coherent until replacement/consumer-zero |
| Timing | 243-node current file present until deletion gate |
| Dogfood/protection | B2 complete and accepted |
| Qualification policy | Parent `E384-QUAL-001` is immutable current authority; Issue elaboration may select implementation mechanisms only |

## 5. Stable output

| Output | Required state |
|---|---|
| Packaging | Build and consumption graph conforms to parent `E384-QUAL-001` |
| Test execution | Canonical owner and one authoritative execution per contract/role, with mechanical `E384-QUAL-001` conformance |
| Evidence | Same candidate, authenticated raw/extracted/API linkage and complete `E384-QUAL-001` raw evidence/result |
| Policy | Old consumers 0 before old provider/data/workflow deletion |
| Context | New required gate proven blocking, GREEN, and read back; old context removed without gap |
| Docs/dogfood | Final provider-gate guidance and complete candidate convergence |
| Integration | B3 GREEN and final Epic PR ready |

## 6. Owned and shared Epic acceptance

**Owned:** E384-RQ-012、013、014、parent `E384-QUAL-001`のimplementation/evidence responsibility and final test-policy/documentation portion of E384-RQ-015。The parent remains the sole policy/value authority。

**Shared/read-only:** E384-RQ-001〜003、006、007、011、016〜018。Lifecycle and Product repair contracts are non-owned。

## 7. Requirements

### I396-RQ-001 — Clean-baseline admission

Issue starts only when B2 proves 15 resolved、active/approved/unexpected 0. An unresolved Product defect is returned to #395/parent, not hidden in the new gate。

### I396-RQ-002 — Sole packaging producer

The packaging/consumer graph mechanically implements the build-invocation and same-candidate requirements of parent `E384-QUAL-001`. Its concrete job names and commands are rolling-wave implementation detail。

### I396-RQ-003 — Closed execution ownership

Every required invariant has one authoritative role and no duplicate execution. The canonical suite and platform-delta roles are separated without creating a second platform-body timing predicate; all qualification acceptance remains exclusively in parent `E384-QUAL-001`。

### I396-RQ-004 — Actual-byte evidence and qualification

Evidence binds source SHA/tree、candidate manifest/artifacts、role outputs、API metadata and content hashes. #396 must implement, measure and mechanically evaluate every predicate in parent `E384-QUAL-001`; missing or incomplete raw inputs, any rejected predicate, or any attempt to substitute a different value, population, window or aggregation rejects B3. #396 does not define an independent numeric policy or a separate Linux/macOS platform-body timing budget。

### I396-RQ-005 — Consumer-first policy removal

Replacement gate and tests exist before any old consumer is removed. All old consumers are retired/replaced and consumer 0 proven before deleting ledger、timing、sharder、policy skip machinery、policy hook、quality providers or old workflow。

### I396-RQ-006 — Lifecycle/register read-only

Provider lifecycle wire and Product behavior are read-only. Register is admission/history authority and is not reinterpreted. Runtime old policy files may be deleted only after clean-baseline and consumer-zero proof。

### I396-RQ-007 — Required-context transition

Human adds new required context while old remains, verifies both, proves intentional new RED blocks while compatibility remains GREEN, restores GREEN, then removes old and reads final state. No gap or unrelated setting drift。

### I396-RQ-008 — Final dogfood and guidance

Candidate-changing provider docs/policy assets are reflected as a complete dogfood candidate. Root/operator guidance describes final gate and no longer instructs ledger/shard/main-push policy。

### I396-RQ-009 — GREEN final integration

After human merge, B3 final gate、complete `E384-QUAL-001` conformance evidence、contexts、docs、dogfood and protected-data checks are GREEN. This is the sole source for the final Epic PR to main。

### I396-RQ-010 — Issue-start gate

Concrete workflow、modules、measurement collector、schemas、commands、tests、compatibility sequence and evidence implementation are authored only at B2 tip and independently Strict-reviewed before start. Elaboration may not change or duplicate `E384-QUAL-001` semantics。

## 8. Verification evidence categories

Workflow structure、same-candidate build graph、node/contract ownership、Linux/macOS/sdist role results、complete raw inputs and mechanical result for `E384-QUAL-001`、raw/extracted/API evidence、consumer-zero and deletions、contexts、final docs/dogfood/protection、B3 merged-tip GREEN。

## 9. Rollback and recovery boundary

Whole #396 merge is the rollback unit and returns to B2 clean current-policy state. Human settings are restored to captured before-state. Partial final-gate/old-policy restore is invalid unless it reconstructs the whole B2 contract and passes GREEN。

## 10. Stop and return

Stop for non-clean B2、required Product/lifecycle change、consumer remaining、`E384-QUAL-001` ambiguity/duplication/non-conformance/incomplete evidence、evidence identity gap、context gap、partial policy removal、partial dogfood、protected-data drift or non-empty owner decision. Return exact evidence; do not choose new qualification values or satisfy the contract through a prohibited escape。

`owner_decisions_required=[]`.
