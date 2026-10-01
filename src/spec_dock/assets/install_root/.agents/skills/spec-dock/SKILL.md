---
name: spec-dock
description: Operate and author SpecDock scopes, canonical documents, Artifacts, dependencies, work and native Git worktrees through the installed external CLI. Use for an in-scope SpecDock outcome and verify the command result and actual post-state.
---

# SpecDock

Use the installed external `spec-dock` console. Read current root and leaf help before commands; canonical documents and actual CLI/Git/GitHub evidence are authoritative. The repository shim only delegates through PATH. Do not execute checkout Python, the retired fixed bundle or shared control as a fallback.

## Resolve the context and target

1. Bind one repository/worktree, using its exact absolute root with `--project` when needed.
2. Prefer the explicit Initiative, Epic, Issue or path supplied by the request or approved plan. Resolve it to one canonical path under `spec-dock/initiatives/`.
3. If a Scope is needed without an explicit selector, inspect `spec-dock active show --json` and use the deepest unambiguous Scope in its valid chain. Empty, stale, corrupt or ambiguous observations do not supply a mutation target.
4. Read the target metadata, parent chain and relevant Requirement, Design, Plan and Report. Preserve their distinct authority; Artifact and external model output remain evidence until explicitly adopted.

## Execute the requested outcome

Read help, inspect the necessary preconditions, execute the in-scope command and verify its effects and post-state. A request or approved plan authorizes ordinary documented local, Git and GitHub effects; routine operations do not need command-by-command permission. Keep lifecycle admission, implementation, review, delivery and merge evidence separate.

- New Scope creation always uses `--backend github`; GitHub issues the number. Preserve existing IDs/ref/path and do not create offline/local Scopes or add UUID Scope identities.
- Start accepts Initiative, Epic and Issue. A new branch needs `--base REF`; existing branch reuse needs explicit `--branch NAME` and no base. Start checks live readiness outside the short exclusion, then rechecks same-clone reservations, checks out and publishes one direct target while excluded.
- One worktree has at most one direct target. Only Start acquires it. `active set TARGET` is an unchanged no-op only for the same valid direct target; an empty or different target requires Start. `active clear` releases the captured direct record without closing GitHub or changing branch.
- Finish completes the fixed GitHub Scope and confirms closed(completed) before clearing only the captured selection. It stays on the branch. Parent completion requires completed descendants. Finish is not handover or proof of delivery, test, review or merge completion.
- Branch leaves change/observe native Git refs without a branch registry. Dependency mutations use metadata through the CLI.
- Sync observes current same-clone main/linked worktrees and their direct targets; it writes no cache, generation or projection and does not infer running Codex processes. Use `--source github` for explicit live lifecycle observations.
- Installation changes only known static resources in one worktree. Init refuses existing destinations. Update/uninstall require verified external preservation for changes; unknown modified files require manual merge. Package updates are separate from static updates.

## Documents and Artifacts

Load only sources needed for the task: canonical metadata/docs, named direct-child Artifacts and rules, dependencies and applicable references under `spec-dock/docs/`. Use `workspace validate`, `workspace sync`, `active show` and relevant queries when verifying that changed surface.

Author canonical Requirement, Design, Plan, Report and accepted ADR when requested or assigned by the approved plan. Use `artifact create --scope TARGET --type TYPE --title TITLE --json` for a supported Markdown type, then populate the returned `data.result.artifact.path`. Use `artifact import file PATH --scope TARGET --json` for one complete opaque evidence file. Prepare other formats in an ignored Workbench and import the completed file; do not invent an Artifact ID or filename. Artifact creation and content authoring are one requested outcome.

## Destructive boundary

Require an exact target and destructive result in the request or approved plan for `scope delete`, `installation uninstall` and `worktree remove`. Understand project-owned `make init` effects before executing bootstrap. Once authorized, execute and verify rather than returning the command for manual entry. Reconfirm only if the actual scope materially exceeds the authorization. Keep any repository human PR merge gate.

## Failure and protected data

Use commands for metadata, lifecycle, dependencies, selection and native worktrees. Do not manufacture state by hand after a failed command. Ordinary file editing has no shared SpecDock lock or permission enforcement.

Preserve raw Git error details and the CLI's confirmed/unknown/not-attempted effects. Keep backups, uncertain records and candidates. Inspect actual local/remote state before a new explicit operation; do not automatically replay an unknown GitHub mutation, revert Git effects or resume a retired journal. Broken or multiple direct records are diagnostics, not an empty worktree.

## Report

Return the resolved target/path, material command effects, verification and remaining gates. A successful query, readiness result or document review does not by itself finish the Issue.
