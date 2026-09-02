---
種別: Issue-Start Handoff Contract
ID: "epic-00384-luna-max-rolling-wave-handoff-contract-v1"
タイトル: "Luna Max Issue-Start Implementation Handoff Contract"
状態: "accepted"
最終更新: "2026-09-02"
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

This file is not an implementation handoff. It is the required contract for creating a future handoff immediately before each Issue starts. The imported candidate `ce7e46cf2603e6fc52b4d4339faa7d3f7f3bac83` failed parent Strict review and is not a freeze identity. No Luna Max implementation may begin from the current parent or Issue draft documents. Issue #392 is specifically not started。

## 2. Authority order for future handoffs

A future Issue-specific handoff must state this order:

1. Current Issue implementation-ready Plan。
2. Current Issue Requirement and Design。
3. Parent Epic R/D/P and accepted multi-Issue ADR。
4. Epic Integration Branch Contract。
5. Rolling-Wave Issue Elaboration Contract。
6. Provider Lifecycle Wire Contract and Post-#387 Regression Baseline Register as applicable。
7. Root `AGENTS.md` at the exact implementation base。

Historical single-Issue ADR/HTML/guides and CLOSED #388〜#390 are not implementation authority。

## 3. Required identity block

Every generated handoff contains:

- repository、integration branch、Issue branch;
- exact current integration base SHA/tree;
- Issue ID、GitHub number and dependency metadata;
- predecessor merge/acceptance evidence;
- external `PARENT_FREEZE_SHA` receipt and post-pass GitHub Issue body projection receipt for #392 elaboration;
- current integration state B0/B1/B2;
- parent contract versions/hashes;
- independent Strict review identity and result;
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

These details are forbidden in the current contract-only Issue Plans and required in the future start-time handoff。

## 5. Issue-specific mandatory content

### For #392

Lifecycle wire conformance、safe filesystem/stage、migration/uninstall、public compatibility、complete dogfood、active-baseline preservation and transitional-gate GREEN。Parent `E384-QUAL-001` is preserved but read-only and non-owned. No #395/#396 implementation ownership。

### For #395

Exact 14-row Product repair map、cause grouping、normal-pass evidence、ledger transition、current-gate GREEN and lifecycle read-only proof。Parent `E384-QUAL-001` remains a future read-only contract. No policy deletion or final-gate dependency。

### For #396

Clean B2 admission、build/same-candidate role ownership、evidence schemas、complete mechanical conformance to parent `E384-QUAL-001`、consumer-first deletion、context transition、final docs/dogfood and B3 GREEN. The handoff may define measurement implementation but may not independently define or change qualification values/aggregation. No Product/lifecycle redesign。

## 6. Stop policy

The future handoff must set `implementation_allowed=false` and return to parent when dependency、branch tip、GREEN state、stable contract、baseline identity、scope、compatibility、rollback、`E384-QUAL-001` semantics/evidence or owner-decision evidence is unresolved. Luna Max does not infer an alternative architecture, qualification policy or another Issue。

## 7. Human boundaries

Luna Max may prepare commits/PR candidates and evidence according to the elaborated Plan. Human alone merges Issue PRs、reverts accepted integration merges、changes required contexts and merges the final Epic PR to main。

## 8. Replacement lifecycle

At each Issue start this file may be replaced by an Issue-specific implementation handoff bound to that Issue's exact base. After Issue acceptance, the next Issue receives a newly generated handoff; a prior Issue handoff is historical and not reusable。

`owner_decisions_required=[]`.
