---
種別: 要件定義書（Issue）
ID: "iss-00392"
タイトル: "Provider Lifecycle And Regression Gate Hard Cutover"
契約名: "Fixed Ownership Provider Lifecycle Hard Cutover"
関連GitHub: ["#392"]
状態: "draft"
最終更新: "2026-09-02"
依存:
  - "../../requirement.md"
  - "../../design.md"
  - "../../plan.md"
  - "../../artifacts/provider-lifecycle-wire-contract.md"
  - "../../artifacts/active-failure-disposition-register.md"
  - "../../artifacts/epic-integration-branch-contract.md"
  - "../../artifacts/rolling-wave-issue-elaboration-contract.md"
完了済み前提: ["iss-00387"]
親: ["epic-00384", "init-local-00003"]
実装開始許可: false
repository_evidence:
  repository: "chemitaro/spec-dock"
  branch: "codex/epic-00384-provider-test-strategy-planning"
  sha: "240e561e94b50250a4a6309452a7fd0fb511458a"
  tree: "181f7eb28da0edff3ca1352edf4cb2ae1f21d433"
---

# iss-00392 Provider Lifecycle And Regression Gate Hard Cutover — 要件定義

本Issueは既存nodeを再利用するが、accepted scopeは**Fixed Ownership Provider Lifecycle Hard Cutover**に限定する。Regression baseline terminalizationとprovider-gate policy cutoverはそれぞれ#395、#396へ移管する。

Parent: [Epic Requirement](../../requirement.md) / [Integration Contract](../../artifacts/epic-integration-branch-contract.md) / [Rolling-Wave Contract](../../artifacts/rolling-wave-issue-elaboration-contract.md)

## 1. Observable outcome

Epic integration branch上で、SpecDockのpublic provider lifecycleがfixed ownership modelへhard cutoverされる。Fresh、exact legacy `0.2.3`、ready、incomplete、tooling-absent-preserved-dataの各stateに対し、install、update、tooling-only uninstall、reinstallがclosed wireとsafe recoveryへ一致する。Old lifecycle writerはなく、checked-in dogfoodは一つのcomplete `0.2.4` candidateになる。

## 2. Goal

- Four fixed roots、two fixed skill slots、strict record、fresh-only seeds、shared-container bootstrapを一つのlifecycle authorityへ収束する。
- Immutable seed policy、same-tuple resume、terminal cleanup continuationを成立させる。
- Exact clean `0.2.3` migrationとold-package mutation-zero boundaryを成立させる。
- Public compatibility、tooling-only uninstall、purge removalをwireどおり提供する。
- Provider-first implementationとcomplete dogfood convergenceを受け入れる。

## 3. Non-goals

- Registerの14 active Product failuresを修正またはterminalizeすること。
- Approved-failure policy、ledger、timing、sharder、policy skip machineryを削除すること。
- Build-once Provider Gate、stable qualification、required-context transitionを実装すること。
- 調査、文書、test、verificationだけの別Issueを作ること。
- Mainへ直接mergeすること。

## 4. Stable input

| Input | Required state |
|---|---|
| Predecessor | #387 CLOSED/completed and merged |
| Integration branch | Current B0 tip, GREEN, parent freeze accepted |
| Product baseline | Exact transitional `0.2.3` package/dogfood and old lifecycle writer |
| Regression baseline | 15 rows, 14 active, 1 resolved; active identities/signatures fixed |
| Test policy | Current ledger/timing/sharder/policy/current workflows operational |
| Normative wire | Parent `provider-lifecycle-wire-contract.md`, immutable |

## 5. Stable output

| Output | Observable state |
|---|---|
| Lifecycle | Complete fixed-ownership `0.2.4` public lifecycle |
| Compatibility | Accepted public grammar/result/text/JSON/exit preserved except approved lifecycle changes |
| Recovery | Exact resume/cleanup contract; no old fallback |
| Dogfood | Complete four-root/two-slot/record/marker candidate |
| Old implementation | Old lifecycle writer and obsolete lifecycle-only tests absent |
| Regression baseline | Same 14 active identities/signatures/lifecycle; no new active row |
| Current gates | Transitional PR/full-regression system remains coherent and GREEN |
| Merge target | Human merge to Epic integration branch only |

## 6. Owned and shared Epic acceptance

**Owned:** E384-RQ-004、005、006、008、009 and lifecycle portion of E384-RQ-015。

**Shared/read-only:** E384-RQ-001〜003、007、016〜018。#395/#396 contracts are non-owned。

## 7. Requirements

### I392-RQ-001 — Vertical acceptance unit

Implementation、migration、compatibility、dogfood and Issue-local verification form one acceptance unit. A dormant framework without public outcome or a documentation/test-only result is not accepted。

### I392-RQ-002 — Fixed authority

Persistent mutation authority is exactly four roots、two slots and the record, with bounded fresh container/seed creation only. Unknown paths and consumer data are not authority。

### I392-RQ-003 — Record and seed policy

Final record is the exact seven-key wire object. Seed policy is immutable across one operation and part of resume identity. Seed presence is not inference authority。

### I392-RQ-004 — Closed wire

The parent wire is implemented without added、missing or reinterpreted values. #392 is sole production writer; later Issues consume it read-only。

### I392-RQ-005 — Safe filesystem and recovery

Preflight、descriptor binding、same-filesystem stage、native atomic publication、bootstrap rollback、terminal cleanup and fault convergence preserve unknown data and fail closed on identity drift。

### I392-RQ-006 — Exact migration and uninstall

Only exact clean `0.2.3` migrates. Uninstall is tooling-only and leaves durable tooling-absent state. Removed purge flag is mutation-zero error. Old package cannot mutate final state。

### I392-RQ-007 — Provider-first complete dogfood

Provider source is the implementation authority. Candidate-changing output is projected as one complete dogfood candidate; seeds、initiatives、artifacts、workbench and unknown data remain unchanged。

### I392-RQ-008 — Active baseline immutability

The 14 active row identities、signatures and lifecycle remain unchanged. No new approved row、skip、xfail、retirement or terminalization occurs in this Issue。

### I392-RQ-009 — GREEN integration output

After human merge, B1 satisfies lifecycle acceptance and current transitional gates are independently GREEN with known baseline only。

### I392-RQ-010 — Issue-start gate

Current draft is not implementation-ready. Exact implementation R/D/P and Luna Max handoff must be generated against the accepted B0 tip and independently Strict-reviewed before start。

## 8. Verification evidence categories

Lifecycle behavior、public wire、filesystem/fault recovery、migration/uninstall、old-package safety、built candidate、dogfood/protected data、active-baseline preservation、current-gate non-regression。

## 9. Rollback and recovery boundary

Rollback unit is the complete #392 integration merge. Before #395 starts, human may revert it and return to B0. Runtime partial operations recover only through the closed lifecycle contract. Partial old-writer restoration or ledger manipulation is invalid。

## 10. Stop and return

Stop before implementation or merge if the wire must change、active identity/signature drifts、current gate cannot remain coherent、candidate cannot converge completely、protected data changes、#395/#396 responsibility is required、or owner decision becomes non-empty。Return exact contract/evidence mismatch to the parent。

`owner_decisions_required=[]`.
