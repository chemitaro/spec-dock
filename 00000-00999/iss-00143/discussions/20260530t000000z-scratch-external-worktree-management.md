# Intake: External Git Worktree Management

## Background

Codex Desktop can create Git worktrees internally, independently of `spec-dock worktree create`.

The current `spec-dock worktree` management surface is limited to worktrees created by spec-dock. That means `list`, `show`, and `remove` are centered on spec-dock-managed worktrees and do not cover worktrees created by other tools, including Codex Desktop.

## Requested Change

Remove the restriction that limits worktree listing, detail display, and removal to spec-dock-created worktrees.

`spec-dock` should be able to operate on any Git worktree belonging to the repository:

- list all repository worktrees, not only spec-dock-managed worktrees
- show details for any repository worktree
- remove any repository worktree

## Motivation

Users need one consistent command surface to inspect and clean up worktrees regardless of how they were created.

This is especially important because Codex Desktop may create worktrees for its own internal workflows. Those worktrees still belong to the same repository and should be visible, inspectable, and removable through the spec-dock worktree commands.

## Initial Scope Notes

This note is an intake memo only. It is not the issue requirement document.

The eventual requirement should clarify safety rules for removing unmanaged worktrees, including how to handle dirty worktrees, missing paths, branch preservation, and user confirmation or force semantics.
