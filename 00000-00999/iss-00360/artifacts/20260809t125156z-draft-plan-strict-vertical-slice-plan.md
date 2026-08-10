---
authority: evidence_only
adoption_status: unreviewed
bundle_generation_not_promotion: true
document_status: candidate
document_role: "issue_plan_draft"
title: "iss-00360 Cut Over Distribution and Retire Legacy Workflow Surfaces — Vertical Slice Implementation Plan Draft"
target: "iss-00360"
source_repository: "chemitaro/spec-dock"
source_branch: "main"
source_sha: "2c75e0c02cb65a6e74040a72dc161d342d661091"
generated_on: "2026-08-09"
issue_id: "iss-00360"
github_issue_number: 360
depends_on:
  - "iss-00357"
  - "iss-00358"
  - "iss-00359"
---

> この文書は human review 用の evidence-only candidate であり、正本への採用、レビュー合格、実装着手可、PR準備完了、merge可能、Issue終了、Epic完了を表さない。

# Planning Level

- **Recommended level:** strict
- **Reason:** destructive prune、existing consumer compatibility、cross-platform file operations、package distribution、uninstall に影響する。
- **Documentation-only:** Runtime はこの Level を読まない。
- **Escalate to critical:** security boundary、authentication material、irreversible user-data deletion risk、unrecoverable migration が見つかった場合。
- **Re-evaluation:** modified managed file policy または top-level preserve boundary が曖昧な場合は実装前に human review。

# 1. Preconditions

- 357 retained / removed Runtime inventory and tests
- 358 target / obsolete / preserve Authoring asset inventory
- 359 target / obsolete skill inventory
- existing installer init / update / uninstall behavior characterized
- exact consumer fixture set
- proposed final candidate accepted as downstream work item or at least preserved as planning dependency candidate

# 2. Work sequence

## Step 1 — Build unified inventory

Enumerate:

- target managed files / directories
- obsolete managed files / directories
- generated paths
- user-owned preserve roots
- executable wrappers
- native shims / adapters
- old skill paths
- docs / template paths
- version / retry markers
- projection exclusions

Cross-check source tree, package asset tree, dogfood tree, tests, docs.

## Step 2 — Characterize current installer safety

- replace / copy semantics
- prune behavior
- symlink handling
- modified managed file behavior
- uninstall boundary
- retry marker
- executable mode
- generated cache exclusion
- error / partial-success output

Lock tests before refactor.

## Step 3 — Introduce target / obsolete manifest

- one source for init / update / uninstall
- validate path safety and uniqueness
- disallow hidden unexpected destinations
- classify replace / prune policy
- expose inventory to tests
- avoid embedding node-local preserve paths as broad deletes

## Step 4 — Fresh init cutover

- copy Target Runtime / Kit / two skills
- remove old assets from Fresh source
- validate catalog / modes
- run fresh consumer smoke
- verify removed surface absence

## Step 5 — Existing update migration

- preflight full classification
- stage target
- refresh managed target
- prune exact obsolete managed
- preserve node-local / historical
- regenerate generated state
- implement partial-failure / retry
- test modified / ambiguous managed cases

## Step 6 — Uninstall

- consume same inventory
- remove current and known legacy managed
- preserve user-owned specs / evidence / external files
- handle mixed / partial install
- produce recovery marker / diagnostics
- verify repeated uninstall convergence

## Step 7 — Dogfood and package parity

- project provider Target into dogfood
- run provider / dogfood diff with exclusions
- build source distribution / wheel as applicable
- install into isolated fixture
- compare installed inventory / modes
- scan package for binary / hidden / interaction-log / sensitive-value / absolute-path hazards

## Step 8 — Integrated smoke

Run installed consumer flows from 357–359, including historical update fixture.

## Step 9 — Docs / migration / release impact

- actual command / asset changes
- Current entrypoints
- compatibility table
- no automatic conversion
- partial failure recovery
- uninstall preservation
- known limitations
- explicit external Intelligence boundary

## Step 10 — IC-3 and final handoff

Produce:

- exact integrated source identity
- consumer matrix results
- target / obsolete / preserve manifest
- parity results
- residual defects
- commands / logs references without verbatim interaction log
- handoff to proposed final candidate

# 3. Consumer matrix

| Scenario | Expected |
|---|---|
| fresh empty | exact Target inventory |
| fresh unrelated files | unrelated preserved |
| update unmodified legacy | obsolete managed pruned、Target refreshed、node data preserved |
| update modified managed | explicit conservative behavior |
| update historical evidence | bytes preserved |
| update unsafe symlink | fail before delete |
| interrupted update | retryable diagnostic |
| uninstall Target | owned assets removed、spec evidence preserved |
| uninstall legacy | known legacy owned assets removed |
| uninstall mixed | convergent partial cleanup |
| repeated operation | idempotent / convergent |

# 4. Test obligations

- unit manifest and ownership
- installer CLI
- file safety
- package build / install
- fresh / update / uninstall
- current / legacy / mixed
- modified managed
- provider / dogfood / installed parity
- executable mode
- integration smoke
- removed surface absence
- preservation hashes
- retry
- packaging prohibited-content scan

# 5. Rollback / recovery

- keep target manifest and migration changes in separable commits
- no node-local content migration, enabling package rollback
- before destructive prune, stage or record enough inventory for diagnosis
- if update fails pre-commit, previous managed state remains
- if failure occurs after partial prune / copy, retry converges; report exact phase
- if package rollback reinstalls old managed workflow, this is operational rollback only and must not rewrite preserved node data
- document when forward recovery is safer than reverting package version

# 6. Completion evidence expected

Future evidence:

- unified inventory
- fresh / update / uninstall matrix
- preservation hashes
- removed surface absence
- package build / install result
- provider / dogfood / installed parity
- integrated Core / Kit / skill smoke
- migration docs
- retry / recovery cases
- IC-3 handoff to final candidate

# 7. Scope control

Any defect discovered in 357–359 contract is reported back to owning Issue unless required for package integration and fixed with explicit ownership. New product feature is not added to 360 merely because it is convenient during cutover.
