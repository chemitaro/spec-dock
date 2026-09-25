---
name: spec-dock
description: Operate and author SpecDock scopes, documents, Artifacts, dependencies, lifecycle state, worktrees, and managed installation through the current repository-local CLI. Use when Codex needs to inspect SpecDock or execute an in-scope SpecDock outcome instead of handing commands back to the user.
---

# SpecDock

Use this skill as the agent-first operating guide for the current SpecDock Storage Core and Authoring Kit. Treat local canonical files, current CLI help, and command results as the authority. Execute the SpecDock work covered by the user's request or approved plan; do not stop after merely presenting a command that can be run safely in the current environment.

## Resolve the scope

1. Prefer an explicit Initiative, Epic, Issue, repository, or worktree target from the request or approved plan.
2. When an existing scope is needed and no target is supplied, run `./spec-dock/scripts/spec-dock active show` and select the deepest unambiguous active scope in its parent chain: Issue, then Epic, then Initiative.
3. Stop before mutation when the target or parent is ambiguous. Do not mutate active state to manufacture certainty.
4. Resolve node targets to one canonical path under `spec-dock/initiatives/`. After creation or import, verify the reported ID and path from local files.

## Execute the outcome

1. Read root help and the relevant leaf help immediately before using a command. Current help owns syntax and available operations.
2. Inspect only the canonical docs, references, metadata, Artifact rules, dependency state, and worktree facts needed to validate the operation.
3. Execute every in-scope SpecDock command needed for the requested outcome. A user request or approved plan authorizes its ordinary documented local, Git, and GitHub side effects; do not ask for command-by-command confirmation.
4. Verify command output and post-state. Run `workspace validate`, `workspace sync`, `active show`, `dependency check`, or worktree inspection when the changed surface requires them.
5. Continue through the requested SpecDock outcome. Keep lifecycle admission, implementation evidence, PR delivery, merge, and lifecycle closure distinct rather than treating one command as proof of all of them.

Ordinary agent execution includes `scope create/import/show`, `active`, `work`, `branch`, `dependency`, `artifact`, `worktree`, `workbench`, `workspace`, and `installation` routes when the requested outcome needs them. This includes their documented GitHub issue and Git checkout effects. Use the fixed external distribution or its pinned repository shim; never fall back to checkout code after engine verification fails.

`work start TARGET` and `work finish TARGET` accept Initiative, Epic, and Issue. Start checks readiness, creates or checks out the corresponding branch, and selects the target. Supply `--base REF` when start must create a new branch; omit it when the target already has a canonical branch. Finish completes the target and clears its selected subtree. For selection alone use `active set` or `active clear`; for state alone use `scope close` or `scope reopen`; for branch alone use `branch create` or `branch switch`. Finish is not proof of commit, push, PR, merge, test, or review completion.

For a future or unfamiliar command, inspect its leaf help and Current reference docs. Execute it when its semantics are non-destructive and in scope. Stop and explain the unresolved effect when the documentation is insufficient to classify it safely.

## Destructive boundary

Require the user's request or an approved plan to name the exact target and destructive outcome before executing:

- `scope delete`, including recursive deletion
- `installation uninstall`
- `worktree remove`
- `worktree bootstrap` when its project-owned `make init` effects are not yet understood

Once that exact authorization exists, execute and verify the command rather than returning it for manual entry. Reconfirm only when the resolved target, deletion set, or effect is materially broader than authorized.

PR merge remains a human action in repositories whose `AGENTS.md` says so. Execute the preceding and following SpecDock commands under the authorization rules above.

## Documents and Artifacts

Read one resolved scope in this order when the task needs its contents:

1. `.meta.json` and parent chain
2. `requirement.md`, `design.md`, `plan.md`, and `report.md`
3. direct-child `artifacts/`, `rules.md`, and named Artifacts
4. direct dependencies and generated projections needed for observation
5. relevant files under `spec-dock/docs/authoring/` and `spec-dock/docs/reference_*.md`

Edit canonical Requirement, Design, Plan, Report, or ADR files when the user requests authoring or an approved plan assigns that work. Preserve their distinct roles and do not treat an Artifact, generated projection, external response, or Report as durable authority automatically.

Use `artifact create --scope TARGET --type TYPE --title TITLE` for supported Markdown Artifact types and populate the returned path. Use `artifact import file PATH --scope TARGET` for one explicit opaque evidence file. For another requested evidence format, such as HTML, create it in the resolved scope's direct-child `artifacts/` directory and apply the format-specific validation skill. Artifact creation and content authoring are one outcome; do not leave an empty scaffold for the operator to finish.

## Guardrails

- Use command-first mutation for metadata, active state, dependencies, generated projections, node lifecycle, and worktrees. Do not hand-edit their storage as a command fallback.
- Preserve user-owned content and follow Current fail-closed diagnostics. Do not bypass a failed command with raw filesystem, low-level Git, or direct GitHub mutation.
- Do not restore removed commands, retired bundled orchestration, provider-specific routes, or third-party composition as a fallback.
- Distinguish canonical documents, evidence Artifacts, generated projections, CLI observations, Git state, and GitHub state in the result.

## Report

Return the smallest useful evidence set:

- resolved target, parent chain, and canonical path
- commands executed and their material side effects
- created or changed IDs and paths
- validation and post-state results
- blockers, destructive scope mismatches, or remaining human gates

Command examples are supporting evidence, not a substitute for execution.
