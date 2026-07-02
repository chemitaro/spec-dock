---
種別: disc
ID: "20260702t020503z-disc"
タイトル: "Phase 3 Initiative Epic Template Model"
状態: "proposed"
作成者: "iwasawayuuta"
最終更新: "2026-07-02"
親: ["epic-00270"]
関連:
  - "20260702t014409z-research"
  - "20260702t020436z-01-disc"
authority: "proposed"
derived_from:
  - "V3 reference/initiative-design-playbook.md"
  - "V3 reference/epic-design-playbook.md"
  - "V3 issues/issue-01-redesign-initiative-templates.md"
  - "V3 issues/issue-02-redesign-epic-templates.md"
reflected_to: []
---

# 20260702t020503z-disc Phase 3 Initiative Epic Template Model

## Initiative template target

Initiative templates should support strategic planning, not implementation planning.

- Requirement:
  - strategic purpose, outcomes, success metrics
  - actors/stakeholders
  - capability candidates
  - scope/non-goals/unchanged
  - constraints and quality requirements
  - transition or rollout requirements
  - discovery artifacts and open questions
- Design:
  - strategic intent / domain vision
  - current and target capability landscape
  - subdomain or investment profile where useful
  - context map delta
  - decision/data ownership and source of truth
  - strategic invariants
  - context interaction strategy
  - quality strategy
  - transition architecture
  - Epic handoff
- Plan:
  - capability/design slice catalog
  - Epic portfolio and sequencing
  - transition tranches
  - dependency/blocker management
  - Epic readiness criteria
  - cross-Epic gates
  - Epic handoff package

## Epic template target

Epic templates should support shared model/capability envelopes for downstream Issues.

- Requirement:
  - capability outcome
  - parent Initiative linkage
  - actors/triggers/use cases
  - acceptance criteria
  - scope/non-goals/unchanged
  - cross-Issue constraints
  - quality/compatibility requirements
  - discovery artifacts and Issue slice candidates
- Design:
  - inherited Initiative constraints
  - target capability/model envelope
  - ubiquitous language delta
  - lifecycle/state model
  - shared invariants
  - command/query/event or operation portfolio
  - contract portfolio
  - consistency/failure/migration strategy
  - runtime scenarios
  - design slice catalog
  - Issue handoff
- Plan:
  - Issue slicing policy
  - design slice to Issue mapping
  - Issue list, suggested grade, dependency graph
  - Issue readiness criteria
  - cross-Issue integration gates
  - artifact adoption rules
  - Epic completion gate

## Anti-overreach

- Initiative templates must not ask for aggregate methods, endpoint schemas, file edit order, or TDD cycles.
- Epic templates must not force private class/method design or exact TDD cycles.
- PlantUML/C4 sections should be optional and explanatory.
- DDD/EDA support should be available but not make SpecDock a DDD-only tool.

## Current repo gap summary

- Current Initiative templates are still generic strategic scaffolds and lack explicit capability/context/source-of-truth/Epic handoff sections.
- Current Epic templates have useful technical sections but lack explicit target model envelope, design slice catalog, Issue handoff package, and suggested Issue grade.

## Adoption target

- `design.md`:
  - Adopt target template model and anti-overreach rules.
- `plan.md`:
  - Map Initiative template redesign to Issue 01 and Epic template redesign to Issue 02.
