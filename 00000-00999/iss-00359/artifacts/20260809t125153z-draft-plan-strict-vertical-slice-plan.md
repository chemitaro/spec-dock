---
authority: evidence_only
adoption_status: unreviewed
bundle_generation_not_promotion: true
document_status: candidate
document_role: "issue_plan_draft"
title: "iss-00359 Replace Managed Workflow Skills with SpecDock Skills — Vertical Slice Implementation Plan Draft"
target: "iss-00359"
source_repository: "chemitaro/spec-dock"
source_branch: "main"
source_sha: "2c75e0c02cb65a6e74040a72dc161d342d661091"
generated_on: "2026-08-09"
issue_id: "iss-00359"
github_issue_number: 359
depends_on:
  - "iss-00357"
  - "iss-00358"
---

> この文書は human review 用の evidence-only candidate であり、正本への採用、レビュー合格、実装着手可、PR準備完了、merge可能、Issue終了、Epic完了を表さない。

# Planning Level

- **Recommended level:** standard
- **Reason:** managed skill contract と user entrypoint を変更するが、Runtime data format / irreversible migration は 360 が所有する。
- **Documentation-only:** Runtime はこの Level を知らない。
- **Escalate to strict:** native host shim、managed ownership collision、security-sensitive external invocation をこの Issue に取り込む必要が生じた場合。
- **Re-evaluation:** 360 へ渡せない installer-coupled behavior が見つかったとき。

# 1. Preconditions

- 357 retained CLI / Artifact contract available from IC-1
- 358 Guide / scope / authority contract available from IC-1
- exact Current managed skill inventory
- provider / dogfood skill asset paths
- 360 handoff schema agreed
- no assumption that old skill deletion already occurred

# 2. Work sequence

## Step 1 — Inventory current skill graph

Map:

- managed names in installer
- provider entry files
- dogfood copies
- native shims / adapters
- docs entrypoints
- skill-to-skill calls
- Runtime commands referenced
- tests / snapshots
- PR helper ownership
- external / third-party boundaries

Classify each current path as replaced by `spec-dock`、replaced by grill、external operator-owned、360 prune、historical evidence。

## Step 2 — Write executable skill contracts

Before prose expansion, create scenario fixtures for:

- explicit scope resolution
- active scope resolution
- canonical / evidence distinction
- dependency display
- deterministic CLI delegation
- no auto-apply
- missing external capability
- exactly-one Artifact
- no old skill fallback

## Step 3 — Implement `spec-dock`

- minimal entrypoint
- Core command discovery
- Kit Guide discovery
- scope / parent / dependency reading
- structural mutation rules
- direct Markdown authoring boundary
- removed workflow no-go rules
- concise compatibility reference

Avoid embedding full CLI or Guide content.

## Step 4 — Implement `spec-dock-grill-with-docs`

- explicit trigger
- bounded local read set
- optional external clarification boundary
- evidence synthesis shape
- Current Artifact type selection
- exactly-one output
- no canonical writer
- no-write failures

## Step 5 — Provider / dogfood projection

- add target assets
- update dogfood copies
- run link / static contract / parity tests
- keep obsolete source until agreed deletion point if 360 needs transactional handoff
- mark obsolete paths in handoff manifest

## Step 6 — Docs entrypoint

- explain the two skills
- link Storage Core / Authoring Kit
- explain external Intelligence boundary
- remove Current recommendation to use old workflow skills
- avoid claiming installer has cut over until 360

## Step 7 — Scenario integration

Run against 357 / 358 fixtures:

- inspect Issue
- create research / interview / disc / decision-candidate
- no `analysis`
- no specialized import
- no Report gate
- Planning Level is Guide text only
- dependency `ready` not equated with implementation handoff status

## Step 8 — 360 handoff

Deliver exact inventory:

- target managed skill paths
- obsolete managed paths
- modified-consumer collision policy candidates
- native shim / adapter paths
- docs to prune / reroute
- uninstall known legacy paths
- preservation exclusions
- installer tests needed

# 3. Tests

- skill front matter and discovery
- target catalog
- relative links
- forbidden old command / skill references
- no provider-owned AI endpoint / Oracle
- no canonical auto-write
- exactly-one Artifact
- no-write failures
- Current Artifact type selection
- provider / dogfood parity
- scenario fixtures
- legacy presence no-fallback
- 360 handoff manifest schema

# 4. Migration / compatibility

- Do not rename old skill directories in consumer.
- Do not delete user-owned external skill.
- Mark old SpecDock-managed skill files for 360 prune based on ownership.
- Historical docs may refer to old skill names.
- Current docs / new skills must not.
- Modified managed files require 360 collision behavior; this Issue records expected ownership but does not delete.

# 5. Rollback

- target skills can be reverted independently before 360 cutover
- no canonical document migration occurs
- no Runtime state migration occurs
- if an old dependency is discovered, add an explicit Core / Kit contract or 360 migration step; do not call old skill as fallback
- keep inventory and tests even if prose iteration is reverted

# 6. Completion evidence expected

Future evidence:

- current skill graph
- two target skill entries
- scenario / negative results
- provider / dogfood parity
- docs pointer update
- obsolete managed inventory
- 360 handoff
- residual external-capability assumptions
