---
authority: evidence_only
adoption_status: unreviewed
bundle_generation_not_promotion: true
document_status: candidate
document_role: "issue_plan_draft"
title: "iss-00357 Reduce Runtime to Storage Core — Vertical Slice Implementation Plan Draft"
target: "iss-00357"
source_repository: "chemitaro/spec-dock"
source_branch: "main"
source_sha: "2c75e0c02cb65a6e74040a72dc161d342d661091"
generated_on: "2026-08-09"
issue_id: "iss-00357"
github_issue_number: 357
depends_on:
---

> この文書は human review 用の evidence-only candidate であり、正本への採用、レビュー合格、実装着手可、PR準備完了、merge可能、Issue終了、Epic完了を表さない。

# Planning Level

- **Recommended level:** strict
- **Reason:** public CLI、lifecycle ordering、historical compatibility、filesystem safety、GitHub partial failure に影響する。
- **Documentation-only:** この選択は `plan.md` の説明であり、Runtime metadata / gate / routing ではない。
- **Re-evaluate upward:** managed data format の不可逆 migration、security boundary change、cross-platform publication primitive change が見つかった場合。
- **Re-evaluate downward:** しない。Scope を細分化する場合は Epic dependency と end-to-end value を再評価する。

# 1. Work sequence

## Step 1 — Exact inventory and characterization

- parser / registry command keys
- Runtime module import graph
- Active Manifest / Context Pack schemas
- Issue lifecycle gates and ports
- Artifact type constants、template routes、filename parsing
- specialized and generic import shared code
- node scaffold path
- provider / dogfood duplicate paths
- unit / CLI / integration tests
- docs / help references
- 360 prune handoff list

Produce retained / removed / shared inventory. No deletion in this step.

## Step 2 — Lock behavioral tests

Add or rewrite tests for adopted semantics before implementation:

- selection-only active
- start guard / dependency / force boundary
- finish order and partial failure
- Current / Historical Artifact split
- optional positional type
- generic import retained
- Report content invariance
- legacy active / Artifact / Report fixtures

Current workflow-gate tests are not copied as Target tests; they are replaced with explicit absence / invariance tests.

## Step 3 — Thin active state

- remove target-write fields for authority / grants / promotion
- tolerate legacy read fields
- simplify Context Pack
- remove lifecycle authority imports
- verify active mutation rollback

## Step 4 — Implement start / finish semantics

- isolate unfinished-active resolver
- isolate dependency-ready check
- enforce force boundary
- preserve checkout-before-active ordering
- simplify finish to close / clear / sync
- implement structured partial-success diagnostics
- remove Report / delegated / EAL access

## Step 5 — Artifact surface

- introduce Current creatable and Historical recognizable APIs
- change CLI argument to optional positional default blank
- remove `analysis` from any candidate path if present
- close `pr-repair-batch` / `draft-*` creation
- remove Assurance profile template resolution
- retain collision / safety behavior
- add historical fixtures

## Step 6 — Import surface

- remove provider-specific parser / registry / command / use case
- retain generic import and shared safety primitives
- update help / docs / tests
- prove no alias fallback

## Step 7 — Scaffold mechanism

- remove Assurance / profile composition
- generate R/D/P/Report deterministically
- use 358 contract fixture
- verify empty Report does not affect Core
- preserve existing node-local files on update path

## Step 8 — Disconnect and delete unreachable workflow modules

Only after retained tests pass:

- delete unreachable Assurance / authoring / guidance / workflow / delegated modules
- update bootstrap / ports / contracts
- remove obsolete unit tests
- preserve historical fixtures
- emit exact removal inventory for 360

## Step 9 — Runtime docs and projection

- CLI help
- lifecycle reference
- Artifact syntax / import reference
- provider / dogfood Runtime projection
- no Current links to removed workflow
- privacy-safe examples

## Step 10 — IC-1 handoff

With 358:

- run scaffold contract fixture
- compare six-type catalog
- verify Report path / headings / non-gating behavior
- resolve shared help / docs wording
- publish handoff inventory to 359 / 360

# 2. Test obligations

## Targeted suites

- domain artifacts / active / dependencies
- application issue lifecycle
- CLI parser / registry
- CLI new Artifact / import
- scaffold creation
- sync / validate / doctor regressions
- generic import platform tests
- provider / dogfood parity

## Required negative cases

- removed command names
- historical-only type creation
- unknown type
- `analysis`
- dependency bypass with `--force`
- active clear before close
- Report / EAL gate reappearance
- symlinked template / artifact path
- path traversal
- collision exhaustion
- privacy leakage from external import source

## Historical fixtures

- `.assurance.json`
- profile-derived `design.md` / `plan.md`
- `draft-*`
- `pr-repair-batch`
- legacy discussions
- heavy Report ledger
- generic imported Artifact
- existing dependency graph

# 3. Migration and compatibility work

- document legacy active state tolerance
- document removed commands and replacements
- document Current vs Historical artifact behavior
- document no automatic conversion
- document finish partial-recovery steps
- hand installer-owned prune paths to 360
- do not delete consumer files in this Issue

# 4. Rollback

- commit changes by coherent behavior boundary: active/lifecycle, Artifact/import, scaffold, module removal, docs/projection
- keep format migration absent or reversible
- if a retained command regresses, revert the corresponding boundary commit
- if physical module deletion exposes a hidden dependency, restore module temporarily and repair import graph; do not re-enable command registration
- verify previous active / Artifact bytes remain readable after rollback

# 5. Completion evidence expected

This list is future evidence, not a completion claim.

- retained / removed / shared inventory
- tests covering adopted lifecycle and Artifact semantics
- command help snapshot
- provider / dogfood parity result
- historical fixture preservation result
- IC-1 contract result
- 359 retained CLI handoff
- 360 prune inventory
- residual risks and follow-ups

# 6. Non-blocking discoveries

Mechanical file-count changes or additional obsolete modules may be absorbed if they follow the same retained / removed contract. A newly discovered Product semantic conflict is blocking and must be raised without reopening already adopted decisions.
