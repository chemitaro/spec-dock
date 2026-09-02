---
種別: 要件定義書（Issue）
ID: "iss-00395"
タイトル: "Regression Baseline Terminalization and Product Defect Repair"
関連GitHub: ["#395"]
状態: "draft"
最終更新: "2026-09-02"
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

## 1. Observable outcome

Accepted #392 outputを含むEpic integration branch上で、post-#387 root ledgerの14 active rowsがすべてProduct実装修正によりnormal passとなる。Ledgerは15 total、0 active、15 resolved、approved failure 0となり、current PR gateとcurrent Full Regressionが独立してGREENになる。

## 2. Goal

- Exact 14 active rowsが示すProduct defectsを修正する。
- Row identity、signature、accepted behaviorをparent registerへ一致させる。
- Current regression systemを利用してclean baselineを成立させる。
- #396がpolicy cutoverできるstable zero-failure inputを提供する。

## 3. Non-goals

- Lifecycle wire、ownership、migration、uninstall semanticsの変更。
- Ledger、timing、sharder、policy skip machinery、current workflowsの最終削除。
- Build-once gate、evidence、parent `E384-QUAL-001` implementation、required-context transition。
- New Product feature、general dead-code cleanup、test-only terminalization。
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

**Shared/read-only:** E384-RQ-001〜003、006、007、009、016〜018 and parent `E384-QUAL-001`。E384-RQ-004〜005 and E384-RQ-012〜014 implementation are non-owned。

## 7. Requirements

### I395-RQ-001 — Exact baseline admission

Issue starts only when the register matches exact 15/14/1 and #392 B1 is GREEN. Stale 27-row top-level metadata is not admission authority。

### I395-RQ-002 — Product repair

Each active row is repaired through production behavior. The existing node becomes a normal pass unless parent register explicitly defines another stable successor. Current register defines all 14 active rows as fixed-in-place。

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

Concrete owner surfaces、repair hypotheses、RED/GREEN tests、commands and ordering are generated only against B1 current tip and independently Strict-reviewed before start. Elaboration does not implement or redefine `E384-QUAL-001`。

## 8. Verification evidence categories

Row-by-row RED/GREEN、Product behavior、current ledger evaluation、ordinary/full current gate、lifecycle non-regression、dogfood/protected data、merged-tip GREEN。

## 9. Rollback and recovery boundary

Whole #395 merge is the rollback unit. Revert returns to accepted B1 with the known 14-active baseline and current policy still operational. #396 cannot start until B2 is reaccepted。

## 10. Stop and return

Stop for unknown row/signature、already-changed active identity、required lifecycle redesign、need to remove current policy early、`E384-QUAL-001` implementation or reinterpretation、new Product scope、unresolvable behavior ambiguity、or non-GREEN B1。Return exact row and evidence to the parent; do not choose a new disposition。

`owner_decisions_required=[]`.
