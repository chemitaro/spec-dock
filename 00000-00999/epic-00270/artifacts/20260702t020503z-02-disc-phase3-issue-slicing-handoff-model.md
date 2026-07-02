---
種別: disc
ID: "20260702t020503z-02-disc"
タイトル: "Phase 3 Issue Slicing Handoff Model"
状態: "proposed"
作成者: "iwasawayuuta"
最終更新: "2026-07-02"
親: ["epic-00270"]
関連:
  - "20260702t014409z-02-interview"
  - "20260702t015012z-interview"
authority: "proposed"
derived_from:
  - "V3 reference/epic-to-issue-slicing-and-handoff.md"
  - "V3 reference/issue-tdd-handoff-model.md"
  - "V3 reference/reviewer-anti-patterns.md"
reflected_to: []
---

# 20260702t020503z-02-disc Phase 3 Issue Slicing Handoff Model

## Baseline policy

- V3's 6 Issue set is the provisional baseline.
- Additional Issues / re-slicing are allowed, but not encouraged.
- Re-slicing requires a clear reason and must pass the user-approved medium gate:
  - existing 6 Issues would degrade independent reviewability, responsibility boundary, verifiability, or PR delivery; and
  - `plan.md` is updated; and
  - a fresh `spec-reviewer` gate is run.

## Good Issue slices

- one coherent actor/trigger or system trigger
- one observable result
- one primary model/context responsibility
- independently reviewable
- testable/verifiable
- clear handoff from Epic design

## Bad Issue slices

- decision-only containers
- "think about architecture"
- "implement the Epic"
- "edit all docs somehow"
- private helper refactor without observable result
- endpoint-only slice that hides domain/application/persistence implications

## Handoff package fields

Each downstream Issue should receive:

- parent Initiative/Epic IDs
- applicable parent requirement IDs
- applicable parent design IDs
- allowed local delta
- forbidden parent boundary changes
- acceptance criteria seed
- model/contract/lifecycle constraints
- expected evidence type
- suggested Issue grade
- dependencies
- escalation triggers
- relevant artifacts

## Suggested grade rule

| Signal | Suggested grade |
|---|---|
| docs-only or wording | lite |
| normal local behavior | standard |
| public/shared contract, compatibility, migration, workflow, metadata | strict |
| safety/security/privacy/destructive/GitHub mutation/rollback-hard | critical |

## Adoption target

- `plan.md`:
  - Adopt slicing policy, re-slicing gate, baseline Issue list, handoff package fields, grade guidance.
- `design.md`:
  - Adopt design slice catalog as bridge to plan.
- `report.md`:
  - Record any later re-slicing decision and reviewer evidence.
