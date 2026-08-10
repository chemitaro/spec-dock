---
authority: evidence_only
adoption_status: unreviewed
bundle_generation_not_promotion: true
document_status: candidate
document_role: "issue_design_draft"
title: "iss-00357 Reduce Runtime to Storage Core — Vertical Slice Design Draft"
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

# 1. Design objective

Retained structural behavior と removed cognitive behavior を code boundary で分離し、Storage Core の command path が workflow modules を import しない構造にする。

# 2. Target component boundary

```text
CLI parser / registry
  -> thin command adapter
    -> application use case
      -> domain invariant
        -> filesystem / Git / GitHub ports
          -> deterministic result + privacy-safe presentation
```

Retained:

- `new`, `import` for nodes
- `active`, `issue start`, `issue finish`
- `deps`
- `artifact import file`
- `close`, `delete`
- `worktree`, `workbench`
- `sync`, `validate`, `doctor`
- repo-local update / uninstall wrapper where it remains a structural convenience

Removed from Runtime registration and reachable imports:

- assurance
- authoring
- guidance
- workflow
- delegated-authoring
- provider-specific ChatGPT import
- profile / grade classification
- reviewer / EAL / promotion gates
- draft routing
- PR repair creation surface

Exact retained list is fixed by implementation inventory before deletion; no removal may be inferred solely from filename.

# 3. Active state model

Target active entry:

```python
@dataclass(frozen=True)
class ActiveEntry:
    id: str
    path: str
```

Parent chain may be represented in the manifest only as selected structural entries, not authority. Derived Context Pack may include canonical paths、Artifact paths、dependency view、generated state pointers。It must not render grants、promotion record、Reviewer status、Report EAL summary。

Migration:

- loader tolerates legacy extra fields
- writer emits target minimal schema
- no in-place rewrite is required merely by reading
- next explicit active mutation may normalize generated active state
- user-owned node metadata is unaffected

# 4. Lifecycle use cases

## 4.1 `active set`

Use case inputs:

- target ref
- optional checkout flag if retained for low-level recovery
- ports for graph / active / Git

Rules:

- resolve valid scope
- no dependency check
- no unfinished Issue guard
- no authority / Report / quality check
- commit selected identity
- rollback active state on persistence failure

## 4.2 `issue start`

Pseudo-flow:

```python
target = resolve_issue(request.target)
current = load_active()
if current.issue != target and current.issue_is_unfinished and not request.force:
    raise UnfinishedActiveIssue
require_dependencies_ready(target)  # never bypassed
checkout(target.branch)
commit_active(target)
post_sync()
```

The unfinished check requires GitHub state only to decide whether the existing active Issue is unfinished. Unknown state must fail safe with actionable diagnostics rather than silently treating unfinished as finished.

## 4.3 `issue finish`

Pseudo-flow:

```python
active = require_active_issue()
close_result = close_linked_github_issue(active)  # already closed => success
try:
    clear_active()
except Exception as error:
    raise PartialSuccess(close_result, recovery=...)
try:
    post_sync()
except Exception as error:
    raise ProjectionStale(close_result, active_cleared=True, recovery=...)
return success
```

No transition grants or synthetic promotion record are persisted.

# 5. Artifact design

## 5.1 Separate sets

```python
CURRENT_CREATABLE_ARTIFACT_TYPES = (
    "blank",
    "research",
    "interview",
    "disc",
    "decision-candidate",
    "adr",
)

HISTORICAL_RECOGNIZABLE_ARTIFACT_TYPES = (
    # exact implementation inventory
)
```

APIs distinguish:

- `can_create(type)`
- `can_recognize_existing(type_or_filename)`
- `is_malformed_candidate(path)`

A historical-only type returns false for creation but true for recognition. Unknown malformed timestamp-intent filenames still fail validation.

## 5.2 CLI arguments

`new artifact` command spec:

- optional positional `artifact_type`
- default `blank`
- explicit choices limited to Current six
- no `--type` alternate
- scope selector exactly one of Initiative / Epic / Issue
- title required, slug optional

Parser help lists type choices and default without implying Historical types are accepted.

## 5.3 Template resolution

- Current type → `templates/artifacts/<type>.md`
- blank file identity omits `blank`
- no draft profile route
- no Assurance store / profile artifact store dependency
- historical recognition does not require a template file

## 5.4 Import

`artifact import file` stays independent of typed Markdown creation. It preserves opaque bytes and generic filename allocation. Remove parser、registry、command、application、specialized workbench constraints、docs、tests that are specific to `chatgpt-output`, while retaining shared safety primitives used by generic import.

# 6. Scaffold integration with 358

357 owns:

- selecting scope template directory
- creating R/D/P/Report paths
- atomic / rollback behavior
- no-Assurance operation
- provider / dogfood runtime mechanism
- tests against a minimal contract fixture

358 owns:

- template prose
- Guide links
- Report headings
- Artifact semantic wording

IC-1 fixture contract:

```json
{
  "scope_files": ["requirement.md", "design.md", "plan.md", "report.md"],
  "report_required_path": true,
  "report_content_gate": false,
  "issue_plan_count": 1,
  "artifact_current_types": [
    "blank", "research", "interview", "disc", "decision-candidate", "adr"
  ]
}
```

# 7. Removal strategy

1. Characterization tests capture retained behavior and current failure semantics.
2. Parser / registry registration is reduced first behind tests.
3. Application use cases stop importing authority / Assurance modules.
4. Domain models / infra contracts remove workflow fields from target writes while tolerating legacy reads.
5. Artifact creation stops profile / draft routing.
6. Specialized import is removed without touching generic import safety.
7. Unreachable workflow modules are deleted only after import graph / tests show no retained references.
8. Dogfood projection is updated from provider source.
9. Removed inventory is handed to 360 for installer prune.

This order prevents physical deletion before the retained graph is disconnected.

# 8. Error contract

| Error | User-visible result | State |
|---|---|---|
| invalid target | clear error | unchanged |
| dependency blocked at start | blocker list | unchanged |
| unfinished active Issue | recovery / `--force` explanation | unchanged |
| checkout fails | Git error summary | active unchanged |
| active persistence fails | rollback diagnostic | previous state restored |
| GitHub close fails | retry guidance | active retained |
| active clear fails after close | partial success | GitHub may be closed, active retained |
| post-sync fails | projection stale guidance | close succeeded, active cleared |
| unknown / historical-only type creation | allowed Current values | no file |
| collision / unsafe path | deterministic rejection | no partial artifact |
| generic import publication failure | committed vs not-committed distinction | explicit |

# 9. Tests

- unit: sets / filename parser / active model / dependency policy
- application: start / finish ordering and failures
- CLI: help and command absence
- filesystem: collision / lock / symlink / rollback
- import: platform-safe publication and privacy
- historical fixtures: heavy Report / Assurance / drafts / repair evidence
- projection: minimal Context Pack and provider-dogfood parity
- mutation invariance: Planning Level text or Report content changes do not affect deps / start / finish

# 10. Design trade-offs

- Legacy active fields are tolerated on read rather than rejected, reducing migration blast radius.
- Historical artifact inventory remains explicit rather than accepting every unknown filename, preserving structural validation.
- `issue finish` remains a convenience rather than removing it, because close / clear / sync ordering is valuable and deterministic.
- `active set` remains low-level selection, allowing blocked Issue research without conflating selection and execution.
