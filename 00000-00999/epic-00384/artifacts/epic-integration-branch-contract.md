---
種別: Normative Artifact
ID: "epic-00384-integration-branch-contract-v1"
タイトル: "Epic Integration Branch Contract"
状態: "draft"
最終更新: "2026-09-08"
対象: ["epic-00384", "iss-00392", "iss-00395", "iss-00396"]
repository_evidence:
  role: "authoring-source-provenance"
  repository: "chemitaro/spec-dock"
  branch: "codex/epic-00384-provider-test-strategy-planning"
  sha: "240e561e94b50250a4a6309452a7fd0fb511458a"
  tree: "181f7eb28da0edff3ca1352edf4cb2ae1f21d433"
---

# Epic Integration Branch Contract

## 1. Identity and authority

- Repository: `chemitaro/spec-dock`
- Integration branch: `codex/epic-00384-provider-test-strategy-planning`
- `PACK_AUTHORING_SOURCE_SHA`: `240e561e94b50250a4a6309452a7fd0fb511458a`
- `PACK_AUTHORING_SOURCE_TREE`: `181f7eb28da0edff3ca1352edf4cb2ae1f21d433`
- `FAILED_REVIEWED_CANDIDATE_SHA`: `ce7e46cf2603e6fc52b4d4339faa7d3f7f3bac83`
- `FAILED_REVIEWED_CANDIDATE_TREE`: `175408f56af05677fce2a42a169f735983a3a0af`
- Historical reviewer: `required-strict-github-connector-verificati-723`; failed candidate above was later corrected and execution `required-strict-github-connector-verificati-747` passed `1429c2f899c6d2086d5bd03c0dcea01f5b168435`
- `CURRENT_INTEGRATION_TIP`: dynamically resolved by comparing local HEAD, configured upstream and remote at every gate
- `PARENT_FREEZE_SHA`: exact accepted clean pushed parent tip recorded externally under Rolling-Wave Contract §5; the historical receipt at `1429c2f899c6d2086d5bd03c0dcea01f5b168435` does not certify later edits
- Human merge order: #392 -> #395 -> #396 -> Epic #384 to main

The authoring-source identity is provenance only. The failed reviewed candidate is remediation history only and is never a freeze identity. This artifact does not predict a future remediation SHA, start any Issue or authorize direct repository mutation。

## 2. Branch rules

1. Each Issue branch is created from the exact current integration tip after parent G0 and dependency acceptance. A new worktree or an existing worktree explicitly selected by the user may host it. Directory reuse does not permit Issue implementation on the integration branch. Formal `issue start` selects the branch/active Issue; implementation-ready elaboration and independent review must follow before Product implementation。
2. Each Issue PR base is the integration branch, never main or another Issue branch。
3. Only one implementation Issue may have an active writer at a time。
4. Human alone merges、reverts、changes required contexts or resolves branch protection。
5. Agent-created merge commits、partial cherry-picks、squashed fragments from several Issues、force-push rewrite of accepted history are forbidden。
6. Each Issue merge is atomic from the parent contract perspective。
7. All accepted commits remain ancestors of the final Epic PR head。

## 3. GREEN definition

GREEN is not only a checkmark. It requires:

- exact branch-tip SHA/tree recorded;
- dependency and owned-output contracts satisfied;
- mandatory Issue evidence complete;
- ordinary/current or final gate appropriate to the state passing;
- unexpected failure 0;
- protected data and dogfood invariants passing;
- no unresolved stop condition;
- rollback/recovery path recorded;
- human review acceptance.

## 4. State contracts

### B0 — Parent freeze

Three nodes、dependency metadata、parent R/D/P、ADRs、wire、baseline register、rolling-wave contract and `E384-QUAL-001` are coherent; E384-RQ-019 and `E384-DEC-001`/`E384-DEC-002` are fully resolved. The exact clean pushed tip has an independent review pass under Rolling-Wave Contract §5、external parent-freeze receipt and successful readback of the post-pass GitHub #384/#392/#395/#396 body projections. #392 is not started。

### B1 — After #392 merge

- Public fixed-ownership lifecycle complete。
- Exact 0.2.3 maintenance migration、seed policy、tooling-only uninstall、wire、filesystem recovery、pre-import coordination、both wrapper handoffs and writing-helper lifetime accepted。
- Runtime/lifecycle share repository-bound coordination outside replaced roots; legacy admission and crash/concurrency boundaries are verified。
- Old lifecycle writer removed。
- Complete candidate dogfood committed。
- 14 active baseline node/signature/lifecycle identities unchanged。
- Transitional current policy and gates GREEN。

### B2 — After #395 merge

- All 14 active rows normal pass and resolved/fixed-in-place unless a parent-predecided successor applies. Repairs follow register §6.1: faithful harness/observer repair where Product is already correct, and Product-boundary repair where required; no assertion weakening or obsolete API restoration。
- Fifteen rows total、active 0、approved 0、unexpected 0。
- Transitional current policy、timing、sharder、PR gate and full verifier internally coherent and GREEN。
- Lifecycle output from B1 unchanged except Product-fix interactions explicitly admitted by the Issue contract。

### B3 — After #396 merge

- Build-once packaging and same-candidate role graph are complete。
- `E384-QUAL-001` raw evidence and mechanical result are GREEN. One normal attempt executes one role graph; final qualification aggregates the fixed five-run population, fault campaign and latest-twenty history without nested repetition or selection。
- Required context and actual-byte evidence are GREEN。
- Old ledger、timing、sharder、policy skip、policy hook、quality providers and main-push workflow removed consumer-first。
- Final docs and complete dogfood coherent。
- B3 is final Epic PR source。

### B4 — After main merge

- Human merged B3 once to main。
- Final PR-head tree equals merge tree。
- Required contexts and final evidence read back on accepted source。
- Issue and Epic closure evidence complete。

## 5. Main drift

Between Issues only, compare current main and integration branch.

- Non-overlap with stable contracts/owned boundaries: human may integrate; re-run full current-state GREEN gate。
- Overlap or semantic ambiguity: do not start next Issue; return to parent specification and ADR review。
- Implementer may not silently rebase around conflict or change accepted input identities。

## 6. Rollback matrix

| State | Preferred action |
|---|---|
| Issue PR not merged | Abandon or revise Issue branch; integration branch unchanged. |
| Issue merged; successor not started | Human whole-merge revert, then revalidate prior state. |
| Successor started but unmerged | Stop and preserve successor work. Human decides its disposition and any prior-merge revert; regenerate elaboration against the accepted result. |
| Several Issue merges accepted | Revert accepted suffix in reverse dependency order or forward-fix within current owner boundary. |
| Required-context transition partly applied | Human restore captured before-state; integration merge blocked. |
| Final Epic PR not merged | Repair/re-run on integration branch; main unchanged. |
| Final Epic PR merged but closure fails | Main remains at accepted tree; perform measured closure recovery or explicit post-merge forward-fix. |

Partial lifecycle writer rollback、ledger-only rollback that violates gate consistency、automatic old engine fallback are forbidden。

## 7. Issue acceptance and closure

Parent B0 is not accepted until the independent review pass under Rolling-Wave Contract §5、external freeze receipt and Issue-body projection readback are complete. An Issue may be marked complete only after its PR is human-merged to the integration branch and the exact merged tip is GREEN. Issue closure does not assert deployment to main. Epic closure occurs only after B4。

Current parent candidate: `owner_decisions_required=[]`; both decisions are user-adopted. This document is not a B0 acceptance receipt. A separate explicit user request now authorizes parent commit/push and #392 formal start after B0; review completion alone never grants implementation permission.
