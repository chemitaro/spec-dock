---
authority: evidence_only
adoption_status: unreviewed
bundle_generation_not_promotion: true
document_status: candidate
document_role: "issue_design_draft"
title: "iss-00360 Cut Over Distribution and Retire Legacy Workflow Surfaces — Vertical Slice Design Draft"
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

# 1. Design objective

357–359 の target contracts を一つの managed distribution manifest に統合し、Fresh、Update、Uninstall を同じ ownership model で処理する。User data preservation と obsolete executable removal を両立する。

# 2. Distribution model

```text
Provider package source
  -> validated target asset manifest
    -> dogfood projection
    -> fresh init
    -> existing update
    -> uninstall ownership map
```

Manifest concepts:

```python
@dataclass(frozen=True)
class ManagedAsset:
    source: str
    destination: str
    kind: Literal["target", "generated"]
    replace_policy: str
    mode: str

@dataclass(frozen=True)
class ObsoleteManagedAsset:
    destination: str
    prior_owner: str
    prune_policy: str
```

Exact data structure may differ. The design requirement is one auditable source for target / obsolete / preserve boundaries rather than scattered hard-coded lists.

# 3. Target inventory composition

Target manifest consumes:

- 357 retained Runtime / wrappers / docs references
- 358 templates / Authoring Guides / Artifact templates
- 359 two skill assets
- required system / generated state contracts
- root documentation / package metadata required for use

It excludes:

- Assurance / profile / authoring pack / workflow / delegated Runtime
- Issue Planning runtime
- provider-specific import
- issue profile templates / draft routes
- repair batch Current templates
- old planning / execution / clarification / ChatGPT / adapter / PR workflow skills as SpecDock product surface
- current docs linking those routes

Some generic Git / GitHub helper skills may be independent products rather than SpecDock-managed Target. Exact disposition must follow ownership inventory, not broad name deletion.

# 4. Transaction phases

## 4.1 Preflight

- resolve target repository
- verify safe roots
- load existing installation metadata / inventory where available
- scan symlink / path type conflicts
- classify target、obsolete、preserve、ambiguous
- determine whether operation can proceed without destructive ambiguity
- stage target asset source

No deletion before complete preflight.

## 4.2 Stage / copy

- write target assets to staging or safe replace path
- verify bytes / expected catalog
- preserve user-owned node content
- update executable mode only for known wrappers
- avoid copying generated cache / binary

## 4.3 Prune

- process exact obsolete managed paths
- verify boundary and policy
- handle modified managed collision according to explicit strategy
- remove empty owned parents only when safe
- never recursively delete unknown sibling content

## 4.4 Commit / regenerate

- finalize target assets
- regenerate permitted generated views
- write version / inventory marker if existing installer contract uses one
- clean staging
- report committed / partial / not-committed state

## 4.5 Recovery

- retry marker or structured diagnostic includes operation phase and remaining owned paths
- re-running converges to Target without duplicate / data loss
- post-commit warning is distinguished from pre-commit failure

# 5. Fresh init

Fresh init can use a simpler path because no SpecDock node data exists, but it still:

- rejects unsafe destination collisions
- copies target managed inventory
- initializes ignore / generated state contracts
- creates no sample workflow authority
- installs only target skills
- ensures Runtime wrapper executable mode
- runs smoke / validate where appropriate
- outputs no secret / local absolute path

# 6. Existing update

Update treats `spec-dock/initiatives/**` and corresponding node-local scope as preserve surface. Managed templates / docs / scripts are refreshable; exact boundary follows repository layout.

Potential policy for modified managed files:

- content-hash known previous version → safe replace / prune
- content matches current target → no-op
- unknown modification → preserve and block / warn according to existing installer safety contract
- never silently delete ambiguous file merely because path is obsolete

If current implementation lacks prior hash manifest, use conservative path / ownership rules and explicit fixtures; do not fabricate certainty.

# 7. Uninstall

Uninstall inventory combines:

- current Target managed assets
- known legacy SpecDock-managed assets
- generated state
- native shims installed by SpecDock

Preserve:

- node-local specs / evidence
- external user skills
- arbitrary `.github` / `.codex` siblings
- user files inside allowed roots not identified as managed
- source repository itself

Uninstall may leave an intentionally preserved `spec-dock/initiatives` tree; exact top-level handling must be explicit in implementation docs and tests.

# 8. Parity definitions

- **Provider ↔ dogfood:** target managed asset content / catalog parity, with declared projection exclusions.
- **Provider ↔ fresh installed:** destination content / mode / catalog parity after installation.
- **Provider ↔ updated existing:** managed target files match; user-owned files are excluded and separately hash-preserved.
- **Uninstall:** owned target / legacy paths absent; preserve set unchanged.

Parity is not blanket directory equality.

# 9. Integration smoke

Installed consumer tests:

1. create or load sample graph
2. `active set` blocked Issue
3. `issue start` dependency behavior
4. create omitted-type blank and typed Artifact
5. generic file import
6. fresh thin Report present
7. read Base + selected Completion Guide
8. discover two skills
9. `issue finish` close / clear / sync with stub / controlled GitHub gateway
10. validate / sync
11. removed command / skill absence
12. historical fixture update preservation

# 10. Documentation integration

- package README
- installed docs README
- Current command reference
- Authoring overview
- migration guide
- update / uninstall recovery
- removed surfaces table
- two-skill entrypoints
- external boundary

Docs are generated / copied from provider source; no consumer-specific absolute paths.

# 11. Test design

- manifest unit tests
- safe path / symlink / collision
- fresh inventory
- update preserve / prune
- modified managed file
- partial failure / retry
- uninstall current / legacy / mixed
- executable mode
- provider / dogfood / installed parity
- installed Core / Kit / skill smoke
- removed fallback
- packaging scan for prohibited payload
- source distribution build

# 12. Trade-offs

- Conservative ambiguous-file handling may leave obsolete modified files, but avoids data loss; diagnostics make the exception visible.
- A single manifest adds maintenance but eliminates divergence among init / update / uninstall.
- Preserving historical evidence means old vocabulary remains in consumer data, while executable / Current navigation is removed.
