---
種別: 要件定義書（Issue）
ID: "iss-00395"
タイトル: "Regression Baseline Terminalization and Product Defect Repair"
関連GitHub: ["#395"]
状態: "draft"
最終更新: "2026-09-08"
依存:
  - "iss-00392"
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

# iss-00395 Regression Baseline Terminalization and Product Defect Repair — 要件定義

Parent: [Epic Requirement](../../requirement.md) / [Baseline Register](../../artifacts/active-failure-disposition-register.md)

Formal `issue start` selects the Issue branch/active context after parent/dependency admission and an explicit user request. It does not authorize Product implementation. The workspace may be new or explicitly reused; implementation-ready R/D/P and handoff plus independent review are still required. The current Epic reassessment does not start this Issue.

## 1. Observable outcome

Accepted #392 outputを含むEpic integration branch上で、post-#387 root ledgerの14 active rowsが表す契約を原因に対応したProduct/test側修復でnormal passへ戻す。Ledgerは15 total、0 active、15 resolved、approved failure 0となり、current PR gateとcurrent Full Regressionが独立してGREENになる。

## 2. Goal

- Exact 14 active rowsのaccepted behaviorを回復する。親register §6.1に従い、12件のharness/observer不整合と2件のProduct責務境界を修復する。
- Row identity、signature、accepted behaviorをparent registerへ一致させる。
- Current regression systemを利用してclean baselineを成立させる。
- #396がpolicy cutoverできるstable zero-failure inputを提供する。

## 3. Non-goals

- Lifecycle wire、ownership、migration、uninstall semanticsの変更。
- Ledger、timing、sharder、policy skip machinery、current workflowsの最終削除。
- Build-once gate、evidence、parent `E384-QUAL-001` implementation、required-context transition。
- New Product feature、general dead-code cleanup、振る舞いを弱めるtest-only terminalization。
- Mainへの直接merge。

## 4. Stable input

| Input | Required state |
|---|---|
| Dependency | #392 human-merged and B1 GREEN |
| Lifecycle | Final wire-conformant `0.2.4`, read-only |
| Baseline | Exact 15 rows; 14 active and one resolved |
| Timing | 243 current weights until #396 |
| Current policy | Ledger evaluator, sharder, policy hook, PR/full workflow coherent |
| Protected data | B1 witness and complete dogfood accepted |

## 5. Stable output

| Output | Required state |
|---|---|
| Product behavior | All 14 accepted behaviors normal pass |
| Register state | 15 total, active 0, resolved 15, fixed-in-place 14, superseded 1 |
| Failure policy | Approved failure 0; no new skip/xfail/retirement |
| Current gates | Ordinary and current full verifier independently GREEN |
| Lifecycle | #392 wire and semantics unchanged |
| Integration | B2 GREEN, human-merged to Epic branch |

## 6. Owned and shared Epic acceptance

**Owned:** E384-RQ-010、011 and Product-repair portion of E384-RQ-015。

**Shared/read-only:** E384-RQ-001〜003、006、007、009、016〜019 and parent `E384-QUAL-001`。E384-RQ-004〜005 and E384-RQ-012〜014 implementation are non-owned。

## 7. Requirements

### I395-RQ-001 — Exact baseline admission

Issue starts only when the register matches exact 15/14/1 and #392 B1 is GREEN. Stale 27-row top-level metadata is not admission authority。

### I395-RQ-002 — Cause-appropriate contract repair

Repair the cause adjudicated in parent register §6.1: twelve test-harness/observer repairs and two Product boundary repairs. Keep the existing nodes and accepted behavior; all fourteen are fixed-in-place. A faithful fixture/observer correction is permitted; restoring retired CLI flags or replacing the production descriptor-bound API with its obsolete predecessor is forbidden. Production defects revealed behind a corrected harness remain owned only if they violate the same accepted row behavior。

### I395-RQ-003 — No masking

Skip、xfail、approved failure、signature rewriting、row deletion、mock-only expectation weakening、silent retirement and unrelated successor substitution are forbidden。

### I395-RQ-004 — Lifecycle read-only

Provider lifecycle wire、record、migration、uninstall、recovery and public compatibility are read-only inputs. Required semantic change is a parent stop。

### I395-RQ-005 — Transitional policy continuity

Current ledger、timing、sharder、policy hook、quality providers and workflows remain present、coherent and executable through Issue acceptance。

### I395-RQ-006 — Exact terminal state

After repairs, active 0、approved 0、unexpected 0 and all 15 rows resolved. Historical failure snapshot fields remain history; current pass truth comes from measured observation。

### I395-RQ-007 — Integration and protection

Candidate-changing Product repairs update dogfood completely when necessary and preserve protected data. Exact merged B2 tip is GREEN before closure。

### I395-RQ-008 — Issue-start gate

Concrete owner surfaces、repair hypotheses、RED/GREEN tests、commands and ordering are generated only against B1 current tip and independently reviewed under Rolling-Wave Contract §5 before Product implementation. Elaboration does not implement or redefine `E384-QUAL-001`。

## 8. Verification evidence categories

Row-by-row RED/GREEN、current behavior and faithful test observers、current ledger evaluation、ordinary/full current gate、lifecycle non-regression、dogfood/protected data、merged-tip GREEN。

## 9. Rollback and recovery boundary

Whole #395 merge is the rollback unit. Revert returns to accepted B1 with the known 14-active baseline and current policy still operational. #396 cannot start until B2 is reaccepted。

## 10. Stop and return

Stop for unknown row/signature、already-changed active identity、required lifecycle redesign、need to remove current policy early、`E384-QUAL-001` implementation or reinterpretation、new Product scope、unresolvable behavior ambiguity、or non-GREEN B1。Return exact row and evidence to the parent; do not choose a new disposition。

Issue固有の追加判断はない。親の `E384-DEC-001` / `E384-DEC-002` はユーザー採用済みで、`owner_decisions_required=[]` である。親G0の独立review・公開freeze/projectionと当該Issueの依存条件を満たして正式startし、詳細化・独立review後にだけProduct実装を許可する。#392の開始依頼は2026-09-08に受領済みである。
