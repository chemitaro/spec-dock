---
name: spec-dock
description: Inspect and explain the current SpecDock scope, documents, artifacts, dependencies, worktrees, and CLI without starting workflow automation.
---

# SpecDock

Use this skill as a thin, read-only guide to the repository's current SpecDock Storage Core and Authoring Kit. Treat local files and current CLI help as the authority. Do not infer workflow readiness, review status, or completion.

## Resolve one scope

1. Prefer one explicit Initiative, Epic, or Issue target supplied by the user.
2. When no target is supplied, run `./spec-dock/scripts/spec-dock active show` and select the deepest unambiguous active scope in its parent chain: Issue, then Epic, then Initiative.
3. Stop and ask for one explicit target when the requested scope cannot be resolved uniquely. Do not mutate active state to resolve ambiguity.
4. Resolve the canonical path under `spec-dock/initiatives/` and report the observed ID and path.

Only this read-only skill may use active scope as a target fallback.

## Read order

Read only what the request needs, in this order:

1. Scope identity, `.meta.json`, and parent chain.
2. `requirement.md`, `design.md`, `plan.md`, and `report.md` at the resolved scope.
3. The scope's direct-child `artifacts/`, its `rules.md`, and any Artifact the user identified.
4. Direct dependency metadata and `deps check --no-github` output when readiness facts are requested.
5. `worktree list` or `worktree show` when checkout placement matters.
6. `spec-dock/docs/authoring/overview.md`, `spec-dock/docs/authoring/artifacts.md`, relevant `spec-dock/docs/reference_*.md`, root CLI help, and the relevant leaf help.

Distinguish canonical documents from evidence Artifacts, generated projections, and CLI observations. Return exact paths and label missing or stale information instead of filling it in.

## CLI side-effect classes

Inspect current root and leaf `--help` before presenting a command. If observed behavior conflicts with this classification, stop and report the mismatch without executing the disputed operation.

### Execute-read-only

The skill may execute only these operations:

- root or leaf `--help`
- `active show`
- `deps check --no-github`
- `worktree list`
- `worktree show`
- `validate`
- bare `doctor`, with no GitHub target options

### Present-only

Explain the exact current command and its side effects, but leave execution to the operator:

- `new initiative`, `new epic`, and `new issue`
- `import initiative`, `import epic`, and `import issue`
- `active set` and `active clear`
- `deps add` and `deps remove`
- `deps check` when it can contact GitHub
- `issue start`
- `sync`
- `artifact import file`
- `worktree create` and `worktree remove`
- `workbench copy`
- `new artifact`
- external GitHub capability diagnostics using the current options:

  ```text
  ./spec-dock/scripts/spec-dock doctor \
    --github-repo <owner/repo> \
    --github-pr <pull-request-number> \
    --github-head-sha <head-sha> \
    [--github-extended]
  ```

The explicitly invoked `spec-dock-grill-with-docs` skill owns the sole skill-level exception for one `new artifact` operation under its own write boundary.

### Forbidden-from-skill

Do not execute or directly perform:

- `close`, `delete`, `issue finish`, `update`, or `uninstall`
- Git or GitHub mutation
- raw edits to `.meta.json`, active state, or dependency sources
- automatic edits to canonical Requirement, Design, Plan, Report, or ADR files
- mutating CLI operations outside the one Artifact exception named above
- removed commands, third-party workflow composition, or fallback automation

## Output

Answer with the smallest useful set of:

- resolved scope ID, kind, path, and parent chain
- canonical document and Artifact locations with their authority class
- observed dependencies and worktree placement
- relevant Current docs and CLI help pointers
- commands grouped by the side-effect classes above
- ambiguity, missing data, or a side-effect mismatch that requires operator action

This skill explains current structure and operations. It does not start planning, review, execution, installation, publication, migration, or rollback workflows.
