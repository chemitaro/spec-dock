---
種別: Issue-Start Handoff Contract
ID: "epic-00384-luna-max-rolling-wave-handoff-contract-v1"
タイトル: "Luna Max Issue-Start Implementation Handoff Contract"
状態: "draft"
最終更新: "2026-09-08"
対象: ["epic-00384", "iss-00392", "iss-00395", "iss-00396"]
active_issue: null
implementation_allowed: false
repository_evidence:
  role: "authoring-source-provenance"
  repository: "chemitaro/spec-dock"
  branch: "codex/epic-00384-provider-test-strategy-planning"
  sha: "240e561e94b50250a4a6309452a7fd0fb511458a"
  tree: "181f7eb28da0edff3ca1352edf4cb2ae1f21d433"
---

# Luna Max Issue-Start Implementation Handoff Contract

## 1. Current prohibition

This file is not an implementation handoff. It is the required contract for creating a future handoff after formal Issue selection and before Product implementation. The parent candidate `1429c2f899c6d2086d5bd03c0dcea01f5b168435` passed external review on 2026-09-02; this is parent planning evidence, not an Issue implementation-ready handoff. No Luna Max implementation may begin from the current parent or Issue draft documents. Issue #392 is specifically not started。

## 2. Authority order for future handoffs

A future Issue-specific handoff must state this order:

1. Current user instructions and applicable `AGENTS.md` at the exact implementation base。
2. Parent Epic Requirement、Design、Plan and accepted ADRs; stable parent acceptance/safety contracts cannot be weakened by a child plan。
3. Epic Integration Branch Contract、Rolling-Wave Issue Elaboration Contract、Provider Lifecycle Wire Contract and Post-#387 Regression Baseline Register as applicable。
4. Current Issue implementation-ready Requirement、Design and Plan within those parent boundaries。
5. The derived Issue-specific handoff。

A conflict is a stop/return condition, not an invitation to follow the more detailed child instruction.

Historical single-Issue ADR/HTML/guides and CLOSED #388〜#390 are not implementation authority。

## 3. Required identity block

Every generated handoff contains:

- repository、integration branch、Issue branch and the exact new or explicitly user-selected reused worktree;
- exact current integration base SHA/tree;
- Issue ID、GitHub number and dependency metadata;
- predecessor merge/acceptance evidence;
- external `PARENT_FREEZE_SHA` receipt and post-pass GitHub Issue body projection receipt for #392 elaboration;
- current integration state B0/B1/B2;
- parent contract versions/hashes;
- independent review identity, model/effort and result under Rolling-Wave Contract §5;
- `implementation_allowed=true` only after all gates pass。

## 4. Required implementation detail

The future handoff must be implementation-complete and include exact:

- owned/shared/no-touch paths;
- modules、classes、functions、schemas and responsibility boundaries;
- first RED and representative failure cases;
- tests and expected observations;
- commands、environment and artifact locations;
- ordered implementation、migration、dogfood and verification steps;
- cleanup and temporary workspace ownership;
- rollback、forward recovery and stop/return actions;
- PR acceptance and human merge handoff。

These details are intentionally not frozen in the current contract-only Issue Plans and are required in the future pre-implementation handoff. Formal `issue start` alone never sets `implementation_allowed=true`。

## 5. Issue-specific mandatory content

### For #392

Lifecycle wire conformance、safe filesystem/stage、migration/uninstall、Wire §16 root shared/exclusive coordination、immutable pre-import bootstrap、update/uninstall release→exec、writing-helper lease lifetime through parent death、resolved legacy/checkout admission、public compatibility、complete dogfood、active-baseline preservation and transitional-gate GREEN。Parent `E384-QUAL-001` is preserved but read-only and non-owned. No #395/#396 implementation ownership。

### For #395

Exact 14-row cause-appropriate repair map from register §6.1、faithful test harness/observer corrections、the two Product-boundary corrections、normal-pass evidence、ledger transition、current-gate GREEN and lifecycle read-only proof. Preserve descriptor-bound safety, strict publication validation, same-repository identity and no-secret output。Parent `E384-QUAL-001` remains a future read-only contract. No policy deletion or final-gate dependency。

### For #396

Clean B2 admission、build/same-candidate role ownership、evidence schemas、complete mechanical conformance to parent `E384-QUAL-001`、consumer-first deletion、context transition、final docs/dogfood and B3 GREEN. The handoff must realize one role graph per normal attempt, reuse observations across the five-run campaign/twenty-window, retain failed or missing attempts, and prove the reference environment capability limits. It may define measurement implementation but may not independently define or change qualification values/aggregation. No Product/lifecycle redesign。

## 6. Stop policy

The future handoff must set `implementation_allowed=false` and return to parent when dependency、branch tip、GREEN state、stable contract、baseline identity、scope、compatibility、rollback、`E384-QUAL-001` semantics/evidence or owner-decision evidence is unresolved. Luna Max does not infer an alternative architecture, qualification policy or another Issue。

## 7. Human boundaries

Luna Max may prepare commits/PR candidates and evidence according to the elaborated Plan. Human alone merges Issue PRs、reverts accepted integration merges、changes required contexts and merges the final Epic PR to main。

## 8. Replacement lifecycle

This parent file remains the common handoff contract. On the selected Issue branch/worktree, create the Issue-specific implementation handoff under that Issue's own canonical scope and bind it to that Issue's exact base. Do not overwrite this parent contract with a child handoff. After Issue acceptance, the next Issue receives a newly generated handoff; a prior Issue handoff is historical and not reusable。

Current parent candidate: `owner_decisions_required=[]`; both decisions are adopted; `implementation_allowed=false`. Parent publication and #392 formal start are user-requested; no coder is dispatched until the Issue-level detailed pack passes independent review.
