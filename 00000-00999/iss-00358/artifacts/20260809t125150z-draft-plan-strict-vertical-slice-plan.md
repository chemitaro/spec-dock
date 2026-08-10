---
authority: evidence_only
adoption_status: unreviewed
bundle_generation_not_promotion: true
document_status: candidate
document_role: "issue_plan_draft"
title: "iss-00358 Simplify Authoring Kit and Document Contracts — Vertical Slice Implementation Plan Draft"
target: "iss-00358"
source_repository: "chemitaro/spec-dock"
source_branch: "main"
source_sha: "2c75e0c02cb65a6e74040a72dc161d342d661091"
generated_on: "2026-08-09"
issue_id: "iss-00358"
github_issue_number: 358
depends_on:
---

> この文書は human review 用の evidence-only candidate であり、正本への採用、レビュー合格、実装着手可、PR準備完了、merge可能、Issue終了、Epic完了を表さない。

# Planning Level

- **Recommended level:** strict
- **Reason:** managed templates / docs、fresh consumer contract、historical preservation、cross-scope authoring semantics に影響する。
- **Documentation-only:** Runtime はこの選択を読まない。
- **Re-evaluate upward:** existing consumer content rewrite が必要と判明した場合。ただし原則として rewrite は scope 外。
- **Re-evaluate downward:** asset catalog がさらに限定された場合も、357 / 360 integration risk があるため原則維持。

# 1. Work sequence

## Step 1 — Complete asset inventory

Inventory:

- provider templates for Initiative / Epic / Issue
- profile templates
- Artifact templates
- Report templates
- docs README / guide / workflow / phase / authoring / rules / reference
- dogfood copies
- tests and link validators
- node scaffold expected paths
- managed installer inventory references
- skill references
- historical fixtures

Classify every item as retain、replace、historical-only、remove-from-provider、360-prune。

## Step 2 — Freeze semantic contracts

Write testable contracts for:

- R/D/P/Report responsibility
- scope layering
- one Issue Plan
- Planning Level docs-only
- six Current Artifact types
- durable decision location
- thin Report
- Current / Historical distinction

No template prose changes before contract review.

## Step 3 — Build thin templates

Order:

1. Report common shape
2. Requirement
3. Design
4. Plan
5. scope-specific minimal differences
6. Artifact six templates

Check headings, placeholder density, final-document cleanliness, Guide links.

## Step 4 — Build Authoring Guides

- overview
- requirement
- design
- plan
- report
- scope-layering
- artifacts
- current / historical navigation

Use examples sparingly and avoid duplicate policy.

## Step 5 — Build Completion Guides

- Base Plan Guide owns common rules.
- `light`, `standard`, `strict`, `critical` own only level-specific deltas.
- Add selection / escalation / N/A examples.
- Verify no Runtime / metadata language.
- Verify Initiative / Epic Guides do not require Issue Level.

## Step 6 — Simplify Current navigation

- make Storage Core + Authoring Kit the first-read path
- remove workflow / phase promotion / Assurance / ChatGPT pack from Current spine
- add Historical compatibility page where necessary
- update rules pages and template README
- avoid premature installed-skill claims until 359 / 360 contract is known

## Step 7 — Provider / dogfood projection

- update provider assets
- project exact relative tree to dogfood
- define exact-byte vs normalized comparisons
- run catalog / link / vocabulary / parity tests

## Step 8 — Existing consumer preservation

Use fixtures containing:

- hand-edited R/D/P
- heavy Report
- `.assurance.json`
- profile-derived docs
- draft / repair artifacts
- legacy discussions
- ADRs

Prove authoring asset work does not modify these files. Final update behavior is reverified by 360.

## Step 9 — IC-1 with 357

- generate fresh nodes using 357 mechanism and 358 content
- compare scope files
- verify Report empty-valid and non-gating
- verify one Plan
- verify six Current types
- verify Historical fixture
- resolve help / docs wording
- publish stable guide / asset paths

## Step 10 — Handoffs

To 359:

- authoring overview path
- R/D/P/Report Guide paths
- Planning Level paths
- scope layering path
- Artifact Current / Historical paths
- authority / reflection summary

To 360:

- fresh managed asset inventory
- obsolete provider asset inventory
- Current navigation removal list
- preservation list
- provider / dogfood parity expectations

# 2. Test obligations

- template catalog exact match
- heading / section contract
- Report section count and language
- one Plan template
- four Completion Guide links
- no common rule duplication beyond allowed summaries
- no `analysis`
- forbidden Current vocabulary
- Current / Historical classification
- provider-neutral language
- provider / dogfood parity
- link validity
- fresh scaffold with 357
- existing content hash preservation
- no Runtime Planning Level coupling
- no Issue Level requirement in Epic / Initiative Plan

# 3. Docs impact

Replace Current entry spine, but preserve historical references where needed. New member should be able to answer:

- Which document stores which decision?
- Which scope owns which concern?
- How deep should an Issue Plan be?
- What is an Artifact versus canonical specification?
- Why is Report optional-content?
- Where do old workflow files fit?
- Which CLI behavior is structural and which work method is external?

# 4. Migration

- No node-local content migration.
- No `.assurance.json` conversion.
- No draft / repair rename.
- Provider obsolete files are marked for 360 prune.
- Current links are rerouted in provider / dogfood.
- Existing consumer Current links are changed only by 360 managed update behavior; user-owned docs remain.

# 5. Rollback

- Separate commits for semantic contract、templates、guides、navigation、tests/projection。
- Revert provider asset changes without touching node-local documents.
- If IC-1 reveals a mechanism mismatch, adjust contract fixture / template path; do not add Runtime authoring policy.
- If a historical link must remain, place it in Historical navigation rather than restoring Current workflow route.

# 6. Completion evidence expected

Future evidence:

- classified asset inventory
- thin template snapshots
- Guide catalog
- link / vocabulary / parity results
- existing consumer preservation hashes
- IC-1 result
- 359 / 360 handoff manifests
- unresolved non-semantic mechanical items
