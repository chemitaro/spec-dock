---
種別: Normative Artifact
ID: "epic-00384-rolling-wave-issue-elaboration-contract-v1"
タイトル: "Rolling-Wave Issue Elaboration Contract"
状態: "accepted"
最終更新: "2026-09-02"
対象: ["epic-00384", "iss-00392", "iss-00395", "iss-00396"]
repository_evidence:
  repository: "chemitaro/spec-dock"
  branch: "codex/epic-00384-provider-test-strategy-planning"
  sha: "240e561e94b50250a4a6309452a7fd0fb511458a"
  tree: "181f7eb28da0edff3ca1352edf4cb2ae1f21d433"
---

# Rolling-Wave Issue Elaboration Contract

## 1. Purpose

Current Issue R/D/P define stable acceptance contracts only. They intentionally omit implementation file lists、symbols、test code、exact commands and ordered implementation steps. Those details are generated once, immediately before each Issue starts, against the current accepted integration tip。

## 2. Immutable parent inputs

Elaboration may not change:

- Issue count、IDs、GitHub numbers、dependency direction;
- integration branch and human merge topology;
- stable cross-Issue contracts E384-C-001〜C-010;
- lifecycle wire values and #392 sole-writer/read-only rule;
- 15/14/1 baseline identities and Issue ownership;
- current-policy-through-#395 and consumer-first-#396 rule;
- protected data、compatibility、rollback、recovery and GREEN definitions;
- no-extra-Issue and human-only settings/merge rule。

A required change to any item is a parent stop, not an elaboration choice。

## 3. Start gate inputs

Before elaboration:

1. Resolve exact current integration branch tip and tree。
2. Verify predecessor Issue merged and accepted, or #387 completed for #392。
3. Verify current state B0/B1/B2 as applicable is GREEN。
4. Verify Issue metadata ID、GitHub number and `depends_on` relation。
5. Verify no other Issue writer is active。
6. Compare main drift and classify overlap。
7. Re-read root `AGENTS.md` and current parent contracts。
8. Verify current Issue remains open and not already started。

## 4. Required elaboration outputs

The issue-start specification pack must produce implementation-ready R/D/P and a Luna Max handoff containing:

- exact base SHA/tree and accepted predecessor evidence;
- observable goal and non-goals copied without semantic change;
- owned/shared/no-touch file inventory;
- component and symbol responsibilities;
- stable input/output schemas and compatibility points;
- first RED and representative failure evidence;
- complete test ownership and exact test cases;
- exact commands and expected results;
- ordered implementation and verification steps;
- migration/dogfood/update boundary where applicable;
- rollback、forward recovery、cleanup and stop/return procedures;
- Issue PR merge-ready acceptance checklist;
- requirement-to-design-to-plan traceability;
- `owner_decisions_required=[]` or an explicit parent stop。

## 5. Independent Strict review

Implementation-ready outputs require a new independent Strict review bound to the exact base SHA/tree. Review must cover architecture consistency、boundary ownership、unsafe intermediate state、testability、compatibility、rollback/recovery、evidence identity and human gates. P0/P1 findings block Issue start。

## 6. Allowed rolling-wave choices

The elaborator may choose exact implementation files、symbols、helper decomposition、test placement、command sequence and internal checkpoints only when every choice remains inside the Issue boundary and does not change parent behavior or outputs。

## 7. Stop and return

Return to the parent owner without starting the Issue when:

- dependency or branch-tip evidence differs;
- current branch is not GREEN;
- stable contract cannot be implemented without change;
- required behavior crosses another Issue boundary;
- an active baseline identity changed unexpectedly;
- old consumer removal is required before Issue #396;
- compatibility or rollback becomes ambiguous;
- main drift overlaps a stable contract;
- owner decision is non-empty。

The return payload identifies exact contract ID、expected/actual evidence、scope impact and whether the Issue draft or parent ADR needs revision。

## 8. Current status

No implementation-ready elaboration has been accepted for #392、#395 or #396 under this contract. Issue #392 must not start from the current draft documents。

`owner_decisions_required=[]`.
