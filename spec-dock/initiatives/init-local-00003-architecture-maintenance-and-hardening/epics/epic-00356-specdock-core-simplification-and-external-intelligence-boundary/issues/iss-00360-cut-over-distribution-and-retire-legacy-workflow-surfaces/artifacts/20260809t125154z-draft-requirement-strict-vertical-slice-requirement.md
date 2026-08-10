---
authority: evidence_only
adoption_status: unreviewed
bundle_generation_not_promotion: true
document_status: candidate
document_role: "issue_requirement_draft"
title: "iss-00360 Cut Over Distribution and Retire Legacy Workflow Surfaces — Vertical Slice Requirement Draft"
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

# 1. Slice outcome

Fresh install、existing repository update、uninstall の三つの consumer journey を通じて、Storage Core + Authoring Kit + two-skill Target distribution へ安全に cut over し、obsolete managed workflow surface を退役させる。

この Issue は installer layer だけを横断的に変更する作業ではない。利用者が package を導入・更新・削除した結果を確認できるところまで、managed inventory、provider assets、dogfood projection、compatibility、migration、rollback / recovery、docs、tests、357–359 integration smoke を同じ Issue で閉じる。

# 2. Current problem

exact source SHA では:

- installer managed skill list が多数の workflow / planning / execution / ChatGPT / adapter / PR helper を含む
- provider docs / templates / Runtime に obsolete surface がある
- dogfood projection が Current product を複製する
- update / uninstall は managed ownership と known legacy cleanup を扱うため、単純な directory replace では user-owned content を危険にさらす
- existing repositories には canonical R/D/P/Report、Artifact、Discussion、ADR、`.assurance.json`、profile-derived docs、modified managed assets が混在しうる
- 357–359 の target inventory を一つの transactional distribution contract に統合する必要がある

# 3. Observable value

Issue 後に利用者が確認できるべきこと:

## Fresh install

- Storage Core Runtime
- thin Authoring Kit
- six Current Artifact templates
- one Issue Plan + Base / four Completion Guides
- two repo-local skills
- Current docs
- required wrappers / generated state rules

だけが managed Target inventory として配置される。Removed workflow command / docs / template / skill / adapter / provider-specific import は Fresh consumer に存在しない。

## Existing update

- managed Target files are refreshed
- known obsolete SpecDock-managed assets are pruned
- node-local R/D/P/Report、Artifact、Discussion、ADR、`.assurance.json`、profile-derived docs、GitHub linkage、dependencies are preserved
- user-owned or modified ambiguous paths are not silently deleted
- generated state is safely regenerated or marked stale
- partial failure is diagnosable and retryable

## Uninstall

- current managed and known legacy managed assets are removed within explicit boundary
- user-owned specs / evidence remain
- partial cleanup leaves a recovery marker / clear diagnostics rather than false success

## Integrated product

- provider / dogfood / fresh installed / updated existing inventory is testable
- installed Runtime and skills use 357 / 358 / 359 semantics
- docs and migration guidance match actual behavior
- obsolete surface has no executable fallback

# 4. Managed ownership model

Each path is classified:

| Class | Meaning | Update | Uninstall |
|---|---|---|---|
| target managed | package owns exact/current content | create or refresh | remove |
| obsolete managed | package previously owned, no longer Current | prune after ownership / safety check | remove |
| user-owned spec | node-local R/D/P/Report/Artifact/Discussion/ADR/meta | preserve | preserve unless product uninstall contract explicitly and safely excludes; Target requirement is preserve |
| generated | indexes、active views、cache-like projections | regenerate / clear safely | remove |
| ambiguous modified managed | managed origin but local modification / ownership uncertain | fail or preserve with diagnostic; no silent overwrite/delete where policy requires protection | diagnostic / bounded handling |
| external | third-party skills / tools / arbitrary files | untouched | untouched |

Exact implementation classification must align with existing installer behavior and tests.

# 5. In scope

- package asset inventory
- provider source to dogfood projection
- installer `_MANAGED_*` inventory
- fresh init
- existing update
- uninstall
- known obsolete managed path prune
- native shim / adapter consequences
- docs / templates / Runtime / skill package inclusion
- preservation / collision / partial-failure behavior
- migration / compatibility guide
- release impact
- consumer test matrix
- 357–359 installed smoke
- no-fallback / absence tests
- handoff to proposed final candidate

# 6. Out of scope

- redesign of Runtime semantics owned by 357
- authoring semantics owned by 358
- skill semantics owned by 359
- external Intelligence installation
- automatic node-local content conversion
- promotion into repository authority of this bundle
- final independent full quality / PR assembly owned by proposed final candidate
- repository-wide unrelated cleanup

# 7. Preservation contract

Must preserve at minimum:

- Initiative / Epic / Issue directories and stable IDs
- `.meta.json` source metadata and direct dependency edges
- GitHub linkage
- node-local `requirement.md` / `design.md` / `plan.md` / `report.md`
- scope-local Artifact and legacy Discussion
- accepted / candidate ADR
- existing `.assurance.json`
- profile-derived / draft / repair / historical evidence
- Workbench user payload under existing ignore contract
- user-owned external skills / host configuration outside exact managed ownership
- unrecognized file in node scope unless explicitly managed

Preservation means no content rewrite, rename, type conversion, or deletion during normal update.

# 8. Prune contract

Prune only when all are true:

1. path is in known obsolete SpecDock-managed inventory
2. path is within allowed managed boundary
3. no path traversal / symlink escape
4. ownership / modification policy allows deletion
5. preflight completes before destructive step
6. partial failure can be diagnosed / retried

No name-pattern-only recursive deletion of arbitrary `.agents/skills/*` or docs.

# 9. Consumer matrices

## Fresh

- empty repository
- repository with unrelated files
- supported platform layouts
- repeated init behavior
- package version / source inventory

## Update

- unmodified previous managed installation
- modified managed file
- historical workflow-heavy consumer
- missing optional path
- partial previous update / retry marker
- user-owned extra skill / docs
- symlink / unsafe path
- interrupted copy / prune
- generated state stale
- node-local heavy Report / Assurance / drafts

## Uninstall

- current Target install
- legacy workflow-heavy install
- mixed / partially updated install
- modified managed file
- user-owned extras
- retry after partial failure

# 10. Compatibility / migration communication

Guide must state:

- Removed commands and no fallback
- retained commands
- new Artifact syntax and Current types
- generic file import only
- active / start / finish semantics
- Planning Level docs-only
- thin Report for Fresh nodes; existing Reports preserved
- two-skill entrypoints
- historical evidence policy
- update / uninstall recovery
- external Intelligence boundary

# 11. Acceptance criteria

Future verification criteria:

1. Fresh init inventory exactly matches Target managed inventory.
2. Removed Runtime / docs / template / skill / adapter / provider-specific import surface is absent.
3. Existing update prunes known obsolete managed paths without changing preservation fixtures.
4. Modified / ambiguous managed path behavior is explicit and tested.
5. Uninstall removes current and known legacy managed paths within boundary, preserving user-owned specs/evidence.
6. Provider / dogfood / fresh installed / updated existing target contracts are consistent.
7. 357 lifecycle / Artifact / import / scaffold tests pass in installed consumer smoke.
8. 358 templates / Guides / links / one Plan / thin Report pass in installed consumer.
9. 359 two skills are discoverable and no old skill fallback exists.
10. Interrupted update / prune and partial uninstall have retry / recovery evidence.
11. Migration docs match exact command / asset behavior.
12. No binary、secret、verbatim interaction log、local absolute path、unexpected hidden managed payload is packaged.
13. Exact consumer evidence and residual risks are handed to proposed final candidate.

# 12. Negative requirements

- Do not treat delete-all-and-reinstall as update if it risks user content.
- Do not migrate existing Report to thin Report.
- Do not delete `.assurance.json` or historical Artifact from node scope.
- Do not preserve obsolete executable fallback merely for compatibility.
- Do not package old skill as a wrapper around new skill.
- Do not claim final quality / change-set submission status inside this Issue.
